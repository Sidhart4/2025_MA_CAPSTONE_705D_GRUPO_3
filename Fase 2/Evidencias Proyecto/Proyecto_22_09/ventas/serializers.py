from decimal import Decimal
from typing import Optional

from django.db import transaction
from django.db.models import F, Q
from rest_framework import serializers

from .models import Venta, VentaItem, Producto, CajaSesion, CajaMovimiento


# -----------------------------
# Helpers
# -----------------------------
def _normaliza_metodo_pago(valor: str | None) -> str | None:
    """Normaliza método de pago (minúsculas + alias comunes)."""
    if not isinstance(valor, str):
        return valor
    v = valor.strip().lower()

    aliases = {
        "cash": "efectivo",
        "contado": "efectivo",
        "ef": "efectivo",

        "debito": "debito",
        "débito": "debito",
        "td": "debito",
        "tarjeta debito": "debito",
        "tarjeta de debito": "debito",

        "credito": "credito",
        "crédito": "credito",
        "tc": "credito",
        "tarjeta credito": "credito",
        "tarjeta de credito": "credito",

        "transf": "transferencia",
        "transfer": "transferencia",
        "transferencia bancaria": "transferencia",

        "otro": "otro",
    }
    return aliases.get(v, v)


def _valores_validos_metodo_pago_desde_modelo() -> set[str]:
    """Lee los choices reales del modelo Venta.metodo_pago (si existen)."""
    field = Venta._meta.get_field("metodo_pago")
    choices = getattr(field, "choices", None) or []
    return {str(value).strip().lower() for value, _ in choices} if choices else set()


# Determina el campo de stock del modelo Producto en tiempo de ejecución.
# Intentamos con nombres comunes; si no existe ninguno, devolvemos None.
_STOCK_CANDIDATES = ("stock", "existencia", "existencias", "inventario", "cantidad")


def _producto_stock_field_name(prod: Producto) -> Optional[str]:
    for name in _STOCK_CANDIDATES:
        if hasattr(prod, name):
            return name
    return None


# -----------------------------
# READ SERIALIZERS
# -----------------------------
class VentaItemReadSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    categoria = serializers.CharField(source="producto.categoria", read_only=True)
    subtotal = serializers.SerializerMethodField()

    class Meta:
        model = VentaItem
        fields = ("id", "producto", "producto_nombre", "categoria",
                  "cantidad", "precio_unitario", "subtotal")

    def get_subtotal(self, obj):
        try:
            return float((obj.cantidad or 0) * (obj.precio_unitario or 0))
        except Exception:
            return 0.0


class VentaReadSerializer(serializers.ModelSerializer):
    items = VentaItemReadSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = ("id", "creado_en", "metodo_pago", "total", "items")


# -----------------------------
# WRITE SERIALIZERS
# -----------------------------
class VentaItemWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = VentaItem
        fields = ("producto", "cantidad", "precio_unitario")

    def validate(self, attrs):
        if attrs.get("cantidad", 0) <= 0:
            raise serializers.ValidationError({"cantidad": "Debe ser mayor que 0."})
        try:
            pu = Decimal(attrs.get("precio_unitario", 0))
        except Exception:
            raise serializers.ValidationError({"precio_unitario": "Formato inválido."})
        if pu < 0:
            raise serializers.ValidationError({"precio_unitario": "No puede ser negativo."})
        return attrs


class VentaSerializer(serializers.ModelSerializer):
    """
    Serializer de escritura con items anidados.
    - Acepta metodo_pago con mayúsculas/minúsculas/acentos/alias.
    - Valida contra los 'choices' del modelo (si existen).
    - DESCUENTA STOCK de Producto al crear la venta (operación atómica).
    """
    items = VentaItemWriteSerializer(many=True, write_only=True)
    metodo_pago = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Venta
        fields = ("id", "creado_en", "metodo_pago", "total", "items")
        read_only_fields = ("total",)

    # --- método de pago ---
    def validate_metodo_pago(self, value):
        norm = _normaliza_metodo_pago(value)
        permitidos = _valores_validos_metodo_pago_desde_modelo()
        if permitidos:
            if norm in (None, "",):
                return ""
            if norm not in permitidos:
                listado = ", ".join(sorted(permitidos))
                raise serializers.ValidationError(
                    f"'{value}' no es válido. Opciones: {listado}."
                )
        return norm or ""

    # --- create con descuento de stock ---
    def create(self, validated_data):
        items_data = validated_data.pop("items", [])

        # Si método viene vacío, usa default razonable (si tienes enum en el modelo, ajústalo allí)
        metodo = validated_data.pop("metodo_pago", None) or "efectivo"

        # Operación atómica: si algo falla, se revierte todo
        with transaction.atomic():
            # asigna usuario logueado si viene en el contexto
            req = getattr(self, 'context', {}).get('request') if hasattr(self, 'context') else None
            user = getattr(req, 'user', None)
            venta = Venta.objects.create(
                metodo_pago=metodo,
                usuario=user if getattr(user, 'is_authenticated', False) else None,
                **validated_data,
            )

            total = Decimal("0")

            # Para evitar ventas con stock negativo, procesamos cada item:
            # - Bloqueamos/aseguramos fila del producto (cuando el motor lo soporte).
            # - Validamos stock suficiente.
            # - Descontamos stock con actualización condicional.
            for it in items_data:
                prod_id = it["producto"].id if isinstance(it["producto"], Producto) else it["producto"]
                cantidad = int(it["cantidad"])

                # Obtenemos el producto (select_for_update si DB lo soporta; en SQLite no hace lock pero mantiene atomicidad)
                prod = Producto.objects.select_for_update(nowait=False).get(pk=prod_id)

                stock_field = _producto_stock_field_name(prod)
                if not stock_field:
                    raise serializers.ValidationError(
                        {"items": f"El producto #{prod_id} no tiene un campo de stock ('stock', 'existencia', 'inventario', 'cantidad')."}
                    )

                # Validación previa de stock en memoria
                stock_actual = getattr(prod, stock_field)
                if stock_actual is None:
                    raise serializers.ValidationError({"items": f"Stock inválido para producto #{prod_id}."})
                if cantidad > stock_actual:
                    raise serializers.ValidationError({"items": f"Stock insuficiente para '{getattr(prod, 'nombre', prod_id)}'. Disponible: {stock_actual}, solicitado: {cantidad}."})

                # Descuento condicional en DB para evitar condiciones de carrera (si otro proceso vende al mismo tiempo)
                updated = (
                    Producto.objects
                    .filter(Q(pk=prod_id) & Q(**{f"{stock_field}__gte": cantidad}))
                    .update(**{stock_field: F(stock_field) - cantidad})
                )
                if updated != 1:
                    # Alguien consumió el stock entre la lectura y la actualización
                    raise serializers.ValidationError({"items": f"Stock insuficiente para '{getattr(prod, 'nombre', prod_id)}' (concurrencia)."})

                # Creamos el item
                item = VentaItem.objects.create(venta=venta, **it)
                total += Decimal(item.cantidad) * Decimal(item.precio_unitario)

            # Actualizamos el total de la venta
            venta.total = total
            venta.save(update_fields=["total"])

            return venta

    def update(self, instance, validated_data):
        # Nota: NO modificamos el stock en update; suele manejarse con lógica específica.
        metodo = validated_data.get("metodo_pago", None)
        if metodo is not None and metodo != "":
            instance.metodo_pago = metodo
        instance.save()
        return instance


# -----------------------------
# CAJA SERIALIZERS
# -----------------------------

class CajaMovimientoSerializer(serializers.ModelSerializer):
    venta_total = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CajaMovimiento
        fields = (
            "id", "sesion", "tipo", "origen", "venta", "venta_total",
            "monto", "descripcion", "creado_en",
        )
        read_only_fields = ("sesion", "creado_en", "venta_total")

    def get_venta_total(self, obj):
        try:
            return float(obj.venta.total) if obj.venta_id else None
        except Exception:
            return None


class CajaSesionSerializer(serializers.ModelSerializer):
    encargado_nombre = serializers.SerializerMethodField(read_only=True)
    ingresos = serializers.SerializerMethodField(read_only=True)
    egresos = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CajaSesion
        fields = (
            "id", "encargado", "encargado_nombre", "caja_nombre",
            "estado", "saldo_inicial", "saldo_final",
            "abierto_en", "cerrado_en", "observacion",
            "ingresos", "egresos",
        )
        read_only_fields = ("encargado", "abierto_en", "cerrado_en", "saldo_final")

    def get_encargado_nombre(self, obj):
        u = getattr(obj, "encargado", None)
        if not u:
            return None
        full = getattr(u, "get_full_name", lambda: "")() or ""
        return full or getattr(u, "first_name", "") or getattr(u, "username", "") or getattr(u, "email", "")

    def _sum(self, obj, tipo):
        qs = obj.movimientos.filter(tipo=tipo).values_list("monto", flat=True)
        return float(sum(qs) or 0)

    def get_ingresos(self, obj):
        return self._sum(obj, "INGRESO")

    def get_egresos(self, obj):
        return self._sum(obj, "EGRESO")
