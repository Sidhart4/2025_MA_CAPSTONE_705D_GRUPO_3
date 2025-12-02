from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .api import VentaViewSet
from . import views

# Acepta con y sin barra final
class OptionalSlashRouter(DefaultRouter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # '/?' hace que la barra final sea opcional
        self.trailing_slash = r'/?'

router = OptionalSlashRouter()
router.register(r"ventas", VentaViewSet, basename="venta")

urlpatterns = [
    path("checkout/", views.checkout, name="checkout"),
    path("pago/retorno/", views.transbank_confirm, name="transbank_confirm"),
    path("pago/resultado/", views.checkout_result, name="checkout_result"),
    path("", include(router.urls)),
]
