# carrito/urls.py
from django.urls import path
from . import views

app_name = "carrito"

urlpatterns = [
    path("", views.detalle, name="ver"),                 # /carrito/  -> carrito:ver
    path("mini/", views.mini, name="mini"),              # parcial del drawer
    path("add/<int:producto_id>/", views.add, name="add"),
    path("update/<int:producto_id>/", views.update, name="update"),
    path("remove/<int:producto_id>/", views.remove, name="remove"),
    path("clear/", views.clear, name="clear"),
]
