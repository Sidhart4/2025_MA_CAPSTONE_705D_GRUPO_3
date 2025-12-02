# agenda/urls.py
from django.urls import path
from . import views

app_name = "agenda"

urlpatterns = [
    # Wizard público
    path("reservar/", views.reservar_wizard, name="reservar"),
    path("reservar/exito/<int:pk>/", views.reservar_exito, name="reservar_exito"),

    # Agenda interna (solo staff por decorador)
    path("", views.lista, name="lista"),
    path("nueva/", views.crear, name="crear"),
    path("<int:pk>/", views.detalle, name="detalle"),          # detalle: dueño o staff
    path("<int:pk>/editar/", views.editar, name="editar"),     # solo staff
    path("<int:pk>/eliminar/", views.borrar, name="borrar"),   # solo staff
]
