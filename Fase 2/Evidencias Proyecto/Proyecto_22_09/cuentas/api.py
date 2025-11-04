from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserPublicSerializer

User = get_user_model()

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Solo staff puede listar/crear/editar usuarios
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_staff
        return request.user and request.user.is_staff

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """
    /api/usuarios/  -> lista sólo para staff
    /api/usuarios/{id}/ -> detalle sólo para staff
    """
    queryset = User.objects.all().order_by("id")
    serializer_class = UserPublicSerializer
    permission_classes = [permissions.IsAdminUser]

class MeView(APIView):
    """
    /api/me/ -> datos del usuario autenticado
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        ser = UserPublicSerializer(request.user)
        return Response(ser.data)
