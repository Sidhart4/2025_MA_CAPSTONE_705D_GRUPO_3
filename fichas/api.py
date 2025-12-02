from rest_framework import viewsets, permissions, filters

from .models import FichaClinica
from .serializers import FichaClinicaSerializer


class FichaClinicaViewSet(viewsets.ModelViewSet):
    queryset = (
        FichaClinica.objects.select_related("cliente", "mascota", "profesional")
        .order_by("-fecha", "-created_at")
    )
    serializer_class = FichaClinicaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = [
        "motivo",
        "mascota__nombre",
        "cliente__first_name",
        "cliente__username",
        "cliente__email",
    ]
    ordering = ["-fecha"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        cliente_id = self.request.query_params.get("cliente")
        mascota_id = self.request.query_params.get("mascota")
        if cliente_id:
            qs = qs.filter(cliente_id=cliente_id)
        if mascota_id:
            qs = qs.filter(mascota_id=mascota_id)
        if not user.is_staff:
            qs = qs.filter(cliente=user)
        return qs
