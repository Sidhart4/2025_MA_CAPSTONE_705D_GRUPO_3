# clientes/api/api.py
from rest_framework import viewsets, filters
from ..models import Cliente, Propietario, Mascota
from ..serializers import (
    ClienteSerializer,
    PropietarioSerializer,
    MascotaSerializer,
)

class ClienteViewSet(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "email"]
    ordering = ["nombre"]

class PropietarioViewSet(viewsets.ModelViewSet):
    queryset = Propietario.objects.all().prefetch_related("mascotas")
    serializer_class = PropietarioSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "rut", "email", "telefono", "ciudad"]
    ordering = ["nombre"]

class MascotaViewSet(viewsets.ModelViewSet):
    queryset = Mascota.objects.select_related("propietario")
    serializer_class = MascotaSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "especie", "propietario__nombre", "propietario__rut"]
    ordering = ["nombre"]
