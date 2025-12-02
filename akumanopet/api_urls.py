from django.urls import path, include
from rest_framework.routers import DefaultRouter

# Productos (ya lo tienes; import actual)
from productos.api import ProductoViewSet

# Nuevos:
from clientes.api.api import ClienteViewSet
from agenda.api import CitaViewSet
from cuentas.api import UserViewSet, MeView
from cuentas.api import ClienteUserViewSet, MascotaPerfilViewSet
from fichas.api import FichaClinicaViewSet
from ventas.api import VentaViewSet, CajaViewSet
from clientes.api.api import PropietarioViewSet, MascotaViewSet

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
