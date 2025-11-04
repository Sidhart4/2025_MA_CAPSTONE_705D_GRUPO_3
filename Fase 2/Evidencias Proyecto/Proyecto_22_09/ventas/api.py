from datetime import datetime, timedelta, date
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import TruncDate
from django.db.models.functions import Coalesce as Co
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django.utils import timezone
from django.db.utils import OperationalError, ProgrammingError
from rest_framework import permissions

from .models import Venta, VentaItem, CajaSesion, CajaMovimiento
from .serializers import (
    VentaSerializer, VentaReadSerializer,
    CajaSesionSerializer, CajaMovimientoSerializer,
)

DEC = DecimalField(max_digits=12, decimal_places=2)


class VentaViewSet(viewsets.ModelViewSet):
    """
    CRUD de Ventas + endpoints para dashboard.
    - Acepta POST /api/ventas/ con 'metodo_pago' en español.
    """
    queryset = Venta.objects.all().order_by("-creado_en")

    def get_serializer_class(self):
        if self.action in ("retrieve",):
            return VentaReadSerializer
        return VentaSerializer

    # -------- helpers rango fechas --------
    def _parse_date(self, s: str | None):
        if not s:
            return None
        try:
            return datetime.strptime(s, "%Y-%m-%d").date()
        except Exception:
            return None

    def _rango_fechas(self, request):
        hoy = date.today()
        desde = self._parse_date(request.query_params.get("desde") or request.query_params.get("from"))
        hasta = self._parse_date(request.query_params.get("hasta") or request.query_params.get("to"))
        if not hasta:
            hasta = hoy
        if not desde:
            desde = hasta - timedelta(days=29)
        if desde > hasta:
            desde, hasta = hasta, desde
        return desde, hasta

    def _aplicar_fechas(self, qs, request):
        d, h = self._rango_fechas(request)
        return qs.filter(creado_en__date__gte=d, creado_en__date__lte=h)

    # -------- override create para devolver lectura --------
    def create(self, request, *args, **kwargs):
        ser = VentaSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        venta = ser.save()
        # Registrar en caja del usuario si hay sesión abierta
        try:
            sesion = CajaSesion.objects.filter(encargado=request.user, estado="ABIERTA").order_by("-abierto_en").first()
            if sesion:
                CajaMovimiento.objects.create(
                    sesion=sesion,
                    tipo="INGRESO",
                    origen="VENTA",
                    venta=venta,
                    monto=venta.total,
                    descripcion=f"Venta #{venta.id}",
                )
                sesion.recomputar_saldo()
                sesion.save(update_fields=["saldo_final"])
        except Exception:
            # No rompemos la creación de la venta si falla caja
            pass
        read = VentaReadSerializer(venta)
        return Response(read.data, status=status.HTTP_201_CREATED)

    # -------- endpoints dashboard --------
    @action(detail=False, methods=["get"], url_path="kpis", name="KPIs")
    def kpis(self, request):
        hoy = date.today()
        primer = hoy.replace(day=1)
        ventas_hoy_qs = Venta.objects.filter(creado_en__date=hoy)
        ventas_mes_qs = Venta.objects.filter(creado_en__date__gte=primer, creado_en__date__lte=hoy)

        ingresos_hoy = ventas_hoy_qs.aggregate(v=Co(Sum("total"), 0, output_field=DEC))["v"] or 0
        ventas_hoy = ventas_hoy_qs.count()
        ingresos_mes = ventas_mes_qs.aggregate(v=Co(Sum("total"), 0, output_field=DEC))["v"] or 0
        ventas_mes = ventas_mes_qs.count()
        ticket_prom = float(ingresos_mes) / ventas_mes if ventas_mes else 0.0

        return Response({
            "ingresos_hoy": float(ingresos_hoy),
            "ventas_hoy": ventas_hoy,
            "ingresos_mes": float(ingresos_mes),
            "ticket_promedio": ticket_prom,
        })

    @action(detail=False, methods=["get"], url_path="por-metodo", name="Por método")
    def por_metodo(self, request):
        qs = self._aplicar_fechas(Venta.objects.all(), request)
        rows = (
            qs.values("metodo_pago")
              .annotate(ingreso=Co(Sum("total"), 0, output_field=DEC))
              .order_by("-ingreso")
        )
        return Response([
            {"metodo": r["metodo_pago"] or "sin método", "ingreso": float(r["ingreso"] or 0)}
            for r in rows
        ])

    @action(detail=False, methods=["get"], url_path="por-categoria", name="Por categoría")
    def por_categoria(self, request):
        ventas_qs = self._aplicar_fechas(Venta.objects.all(), request)
        items_qs = VentaItem.objects.filter(venta__in=ventas_qs).select_related("producto")
        rows = (
            items_qs.values("producto__categoria")
                    .annotate(ingreso=Co(Sum(F("cantidad") * F("precio_unitario")), 0, output_field=DEC))
                    .order_by("-ingreso")
        )
        return Response([
            {"categoria": r["producto__categoria"] or "sin categoría", "ingreso": float(r["ingreso"] or 0)}
            for r in rows
        ])

    @action(detail=False, methods=["get"], url_path="top", name="Top productos")
    def top_productos(self, request):
        try:
            limit = int(request.query_params.get("limit", 8))
        except Exception:
            limit = 8
        ventas_qs = self._aplicar_fechas(Venta.objects.all(), request)
        items_qs = VentaItem.objects.filter(venta__in=ventas_qs).select_related("producto")
        rows = (
            items_qs.values("producto_id", "producto__nombre")
                    .annotate(
                        unidades=Co(Sum("cantidad"), 0),
                        ingreso=Co(Sum(F("cantidad") * F("precio_unitario")), 0, output_field=DEC),
                    )
                    .order_by("-ingreso")[:limit]
        )
        data = []
        for r in rows:
            data.append({
                "producto": r.get("producto__nombre") or f"Producto #{r['producto_id']}",
                "unidades": int(r["unidades"] or 0),
                "ingreso": float(r["ingreso"] or 0),
            })
        return Response(data)

    @action(detail=False, methods=["get"], url_path="serie-diaria", name="Serie diaria")
    def serie_diaria(self, request):
        desde, hasta = self._rango_fechas(request)
        qs = self._aplicar_fechas(Venta.objects.all(), request)
        rows = (
            qs.annotate(fecha=TruncDate("creado_en"))
              .values("fecha")
              .annotate(ingreso=Co(Sum("total"), 0, output_field=DEC))
              .order_by("fecha")
        )
        mapa = {r["fecha"]: float(r["ingreso"] or 0) for r in rows}
        serie, d = [], desde
        while d <= hasta:
            serie.append({"fecha": d.isoformat(), "ingreso": mapa.get(d, 0.0)})
            d += timedelta(days=1)
        return Response(serie)


# -----------------------------
# CAJA API
# -----------------------------

class CajaViewSet(viewsets.GenericViewSet):
    """Endpoints para gestionar la caja del usuario actual."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CajaSesionSerializer

    # Helper: obtener la sesión abierta del usuario
    def _sesion_abierta(self, request):
        u = request.user
        try:
            return (
                CajaSesion.objects
                .filter(encargado=u, estado="ABIERTA")
                .order_by("-abierto_en")
                .first()
            )
        except (OperationalError, ProgrammingError):
            # Si las migraciones de Caja no existen todavía, devuelve None sin romper la app
            return None

    @action(detail=False, methods=["get"], url_path="actual")
    def actual(self, request):
        sesion = self._sesion_abierta(request)
        if not sesion:
            return Response({"abierta": False})
        data = CajaSesionSerializer(sesion).data
        data["abierta"] = True
        return Response(data)

    @action(detail=False, methods=["post"], url_path="abrir")
    def abrir(self, request):
        if self._sesion_abierta(request):
            return Response({"detail": "Ya tienes una caja abierta."}, status=400)
        saldo_inicial = request.data.get("saldo_inicial", 0)
        obs = request.data.get("observacion", "")
        nombre = request.data.get("caja_nombre", "")
        sesion = CajaSesion.objects.create(
            encargado=request.user,
            caja_nombre=nombre,
            saldo_inicial=saldo_inicial or 0,
            saldo_final=saldo_inicial or 0,
            observacion=obs,
            estado="ABIERTA",
        )
        return Response(CajaSesionSerializer(sesion).data, status=201)

    @action(detail=False, methods=["post"], url_path="cerrar")
    def cerrar(self, request):
        sesion = self._sesion_abierta(request)
        if not sesion:
            return Response({"detail": "No tienes caja abierta."}, status=400)
        sesion.recomputar_saldo()
        sesion.estado = "CERRADA"
        sesion.cerrado_en = timezone.now()
        sesion.save(update_fields=["saldo_final", "estado", "cerrado_en"])
        return Response(CajaSesionSerializer(sesion).data)

    @action(detail=False, methods=["post"], url_path="movimiento")
    def movimiento(self, request):
        sesion = self._sesion_abierta(request)
        if not sesion:
            return Response({"detail": "Abre una caja primero."}, status=400)
        tipo = request.data.get("tipo")  # INGRESO/EGRESO
        monto = request.data.get("monto")
        descripcion = request.data.get("descripcion", "")
        if tipo not in ("INGRESO", "EGRESO"):
            return Response({"detail": "tipo debe ser INGRESO o EGRESO"}, status=400)
        mov = CajaMovimiento.objects.create(
            sesion=sesion, tipo=tipo, origen="MANUAL", monto=monto, descripcion=descripcion
        )
        sesion.recomputar_saldo()
        sesion.save(update_fields=["saldo_final"])
        return Response(CajaMovimientoSerializer(mov).data, status=201)

    @action(detail=False, methods=["get"], url_path="movimientos")
    def movimientos(self, request):
        sesion = self._sesion_abierta(request)
        if not sesion:
            return Response([])
        qs = sesion.movimientos.all().order_by("-creado_en")
        return Response(CajaMovimientoSerializer(qs, many=True).data)

    @action(detail=False, methods=["post"], url_path="registrar-venta")
    def registrar_venta(self, request):
        """Adjunta una venta como ingreso a la caja abierta del usuario."""
        sesion = self._sesion_abierta(request)
        if not sesion:
            return Response({"detail": "Abre una caja primero."}, status=400)
        venta_id = request.data.get("venta_id")
        try:
            venta = Venta.objects.get(pk=venta_id)
        except Venta.DoesNotExist:
            return Response({"detail": "Venta no encontrada."}, status=404)
        mov = CajaMovimiento.objects.create(
            sesion=sesion,
            tipo="INGRESO",
            origen="VENTA",
            venta=venta,
            monto=venta.total,
            descripcion=f"Venta #{venta.id}",
        )
        sesion.recomputar_saldo()
        sesion.save(update_fields=["saldo_final"])
        return Response(CajaMovimientoSerializer(mov).data, status=201)
