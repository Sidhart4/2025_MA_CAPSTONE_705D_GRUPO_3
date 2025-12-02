from django.urls import path, include, re_path  # <--- Agregamos re_path
from django.conf import settings                # <--- Agregamos settings
from django.views.static import serve           # <--- Agregamos serve
from rest_framework.routers import DefaultRouter

# Productos (ya lo tienes; import actual)
from productos.api import ProductoViewSet

# Nuevos:
from clientes.api.api import ClienteViewSet, PropietarioViewSet, MascotaViewSet
from agenda.api import CitaViewSet
from cuentas.api import UserViewSet, MeView, ClienteUserViewSet, MascotaPerfilViewSet
from fichas.api import FichaClinicaViewSet
from ventas.api import VentaViewSet, CajaViewSet

router = DefaultRouter()
router.register(r"productos", ProductoViewSet, basename="producto")
router.register(r"clientes",  ClienteViewSet,  basename="cliente")
router.register(r"agenda",    CitaViewSet,    basename="cita")
router.register(r"usuarios",  UserViewSet,    basename="usuario")
router.register(r"usuarios-clientes", ClienteUserViewSet, basename="usuario-cliente")
router.register(r"ventas",    VentaViewSet,   basename="venta")
router.register(r"caja",      CajaViewSet,    basename="caja")
router.register(r"propietarios", PropietarioViewSet, basename="propietario")
router.register(r"mascotas", MascotaViewSet, basename="mascota")
router.register(r"mascotas-perfil", MascotaPerfilViewSet, basename="mascota-perfil")
router.register(r"fichas-clinicas", FichaClinicaViewSet, basename="ficha-clinica")

urlpatterns = [
    path("", include(router.urls)),
    path("me/", MeView.as_view(), name="me"),
]

# --- BLOQUE MAGICO PARA LAS FOTOS ---
# Esto fuerza a Django a servir los archivos de la carpeta media
# Nota: Solo funcionará para fotos que existan físicamente en el servidor
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]