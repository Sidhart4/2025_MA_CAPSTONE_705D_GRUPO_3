from rest_framework import serializers
from clientes.models import Propietario, Mascota

class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = "__all__"

class PropietarioSerializer(serializers.ModelSerializer):
    mascotas = MascotaSerializer(many=True, read_only=True)

    class Meta:
        model = Propietario
        fields = "__all__"
