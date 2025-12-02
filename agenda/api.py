# agenda/api.py
from django.utils import timezone
from django.db.models import Q
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cita,Propietario, Mascota
from .serializers import CitaSerializer  # lo sigues usando para CRUD normal
from .serializers import PropietarioSerializer, MascotaSerializer

# (Opcional) sólo staff/recepción/vet para la lista de próximas
class IsClinicStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        u = request.user
        return u.is_authenticated and (
            u.is_staff or u.groups.filter(name__in=["Veterinarios", "Recepcion"]).exists()
        )


class CitaViewSet(viewsets.ModelViewSet):
    queryset = Cita.objects.all().order_by("-id")
    serializer_class = CitaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = []          # ej: ["cliente__first_name", "mascota"]
    ordering_fields = "__all__"

    @action(detail=False, methods=["get"], url_path="proximas",
            permission_classes=[IsClinicStaff])  # ← exige staff/recepción/vet
    def proximas(self, request):
        """
        Devuelve las próximas citas desde ahora (hoy y hora >= ahora + días futuros).
        ?limit=6 para limitar resultados.
        """
        # parámetros
        try:
            limit = int(request.query_params.get("limit", 6))
        except Exception:
            limit = 6

        now = timezone.localtime()
        hoy = now.date()
        hhmm = now.time()

        qs = (
            self.get_queryset()
            .select_related("profesional", "servicio", "cliente")
            .filter(Q(fecha=hoy, hora__gte=hhmm) | Q(fecha__gt=hoy))
            .order_by("fecha", "hora")[:limit]
        )

        # formateo liviano para la tarjeta “Próximos clientes”
        def _cliente_display(u):
            if not u:
                return "—"
            full = getattr(u, "get_full_name", lambda: "")() or ""
            return full or getattr(u, "first_name", "") or getattr(u, "username", "") or getattr(u, "email", "") or "—"

        data = []
        for c in qs:
            data.append({
                "id": c.id,
                "fecha": c.fecha.isoformat(),
                "hora": c.hora.strftime("%H:%M") if c.hora else None,
                "paciente": c.mascota or "—",  # en tu flujo guardas "Firulais (Gato)" como texto
                "propietario": _cliente_display(getattr(c, "cliente", None)),
                "motivo": getattr(c.servicio, "nombre", None) or "—",
                "doctor": getattr(c.profesional, "nombre", None) or "—",
            })
        return Response(data)
class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all().order_by("-creado_en")
    serializer_class = PropietarioSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre_completo", "rut", "email", "ciudad"]
    ordering_fields = "__all__"


class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.select_related("propietario").all().order_by("-creado_en")
    serializer_class = MascotaSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "especie", "raza", "propietario__nombre_completo", "propietario__rut"]
    ordering_fields = "__all__"