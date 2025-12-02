from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MascotaPerfil

User = get_user_model()

class UserPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "is_staff"]
        read_only_fields = fields


class ClienteUserSerializer(serializers.ModelSerializer):
    """Serializer para crear/editar usuarios clientes (no staff)."""

    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "username", "password", "is_staff", "is_active"]
        read_only_fields = ["is_staff", "is_active"]

    def create(self, validated_data):
        password = validated_data.pop("password", None) or User.objects.make_random_password()
        email = validated_data.get("email") or ""
        validated_data.setdefault("username", email)
        user = User(**validated_data)
        user.set_password(password)
        user.is_staff = False
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.is_staff = False
        instance.save()
        return instance


class MascotaPerfilSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.SerializerMethodField()
    especie_display = serializers.CharField(source="get_especie_display", read_only=True)

    class Meta:
        model = MascotaPerfil
        fields = [
            "id",
            "usuario",
            "usuario_nombre",
            "nombre",
            "especie",
            "especie_display",
            "raza",
            "fecha_nacimiento",
            "notas",
            "foto",
            "creada",
            "actualizada",
        ]

    def get_usuario_nombre(self, obj):
        return getattr(obj.usuario, "first_name", "") or getattr(obj.usuario, "username", "") or ""
