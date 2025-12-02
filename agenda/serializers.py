from rest_framework import serializers
from .models import Cita, Propietario, Mascota # ajusta si tu modelo se llama distinto


class CitaSerializer(serializers.ModelSerializer):
    """Serializer base de Cita con campos legibles para el UI.

    Agrega:
    - servicio_nombre: nombre del Servicio
    - profesional_nombre: nombre del Profesional
    - cliente_nombre: display del usuario (full name/first_name/username/email)
    """

    servicio_nombre = serializers.SerializerMethodField(read_only=True)
    profesional_nombre = serializers.SerializerMethodField(read_only=True)
    cliente_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cita
        fields = (
            "id",
            "fecha",
            "hora",
            "duracion_min",
            "profesional",
            "servicio",
            "mascota",
            "cliente",
            "creado",
            "nombre_cliente",
            "email_contacto",
            "whatsapp_contacto",
            "recuerda_mail",
            "recuerda_wa",
            "recordatorio_mail_enviado",
            "recordatorio_wa_enviado",
            # Extras legibles
            "servicio_nombre",
            "profesional_nombre",
            "cliente_nombre",
        )
        read_only_fields = (
            "creado",
            "recordatorio_mail_enviado",
            "recordatorio_wa_enviado",
        )

    def get_servicio_nombre(self, obj):
        try:
            return getattr(obj.servicio, "nombre", None) or str(obj.servicio)
        except Exception:
            return None

    def get_profesional_nombre(self, obj):
        try:
            return getattr(obj.profesional, "nombre", None) or str(obj.profesional)
        except Exception:
            return None

    def get_cliente_nombre(self, obj):
        u = getattr(obj, "cliente", None)
        if not u:
            return None
        try:
            full = getattr(u, "get_full_name", lambda: "")() or ""
            return (
                full
                or getattr(u, "first_name", "")
                or getattr(u, "username", "")
                or getattr(u, "email", "")
                or None
            )
        except Exception:
            return None
class MascotaSerializer(serializers.ModelSerializer):
    propietario_nombre = serializers.CharField(source="propietario.nombre_completo", read_only=True)

    class Meta:
        model = Mascota
        fields = "__all__"


class PropietarioSerializer(serializers.ModelSerializer):
    mascotas = MascotaSerializer(many=True, read_only=True)

    class Meta:
        model = Propietario
        fields = "__all__"
