from rest_framework import serializers
from .models import Cliente, Propietario, Mascota

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = "__all__"

class MascotaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mascota
        fields = "__all__"

class PropietarioSerializer(serializers.ModelSerializer):
    # si tu modelo Mascota tiene FK a Propietario con related_name="mascotas"
    mascotas = MascotaSerializer(many=True, read_only=True)

    class Meta:
        model = Propietario
        fields = "__all__"