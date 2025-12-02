from django.urls import path
from . import views

app_name = "reserva"

urlpatterns = [
    path("", views.lista, name="lista"),                     # /reserva/
    path("nueva/", views.crear, name="crear"),               # /reserva/nueva/
    path("<int:reserva_id>/", views.detalle, name="detalle"),# /reserva/12/
    path("<int:reserva_id>/editar/", views.editar, name="editar"),
    path("<int:reserva_id>/eliminar/", views.eliminar, name="eliminar"),
]
