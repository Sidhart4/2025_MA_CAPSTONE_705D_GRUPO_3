from rest_framework import viewsets, permissions, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import (
    UserPublicSerializer,
    ClienteUserSerializer,
    MascotaPerfilSerializer,
)
from .models import MascotaPerfil

User = get_user_model()


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff
        return request.user and request.user.is_staff


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("id")
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAdminUser]


class ClienteUserViewSet(viewsets.ModelViewSet):
    """CRUD de usuarios clientes (no staff)."""

    queryset = User.objects.filter(is_staff=False).order_by("first_name", "username")
    serializer_class = ClienteUserSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["first_name", "last_name", "username", "email"]
    ordering = ["first_name"]


class MascotaPerfilViewSet(viewsets.ModelViewSet):
    queryset = MascotaPerfil.objects.select_related("usuario").order_by("nombre")
    serializer_class = MascotaPerfilSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["nombre", "usuario__first_name", "usuario__username", "usuario__email"]
    ordering = ["nombre"]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        usuario_id = self.request.query_params.get("usuario") or self.request.query_params.get("cliente")
        if usuario_id:
            qs = qs.filter(usuario_id=usuario_id)
        if not user.is_staff:
            qs = qs.filter(usuario=user)
        return qs


class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ser = UserPublicSerializer(request.user)
        return Response(ser.data)
