from rest_framework import serializers
from .models import FichaClinica


class FichaClinicaSerializer(serializers.ModelSerializer):
    mascota_nombre = serializers.CharField(source="mascota.nombre", read_only=True)
    cliente_nombre = serializers.SerializerMethodField()
    profesional_nombre = serializers.CharField(source="profesional.nombre", read_only=True, default=None)

    class Meta:
        model = FichaClinica
        fields = [
            "id",
            "cliente",
            "cliente_nombre",
            "mascota",
            "mascota_nombre",
            "profesional",
            "profesional_nombre",
            "fecha",
            "motivo",
            "diagnostico",
            "tratamiento",
            "notas",
            "proximo_control",
            "created_at",
            "updated_at",
        ]

    def get_cliente_nombre(self, obj):
        return getattr(obj.cliente, "first_name", "") or getattr(obj.cliente, "username", "") or ""
