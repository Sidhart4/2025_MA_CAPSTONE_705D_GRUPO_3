from django.urls import path

from . import views

app_name = "fichas"

urlpatterns = [
    path("", views.fichas_lista, name="lista"),
    path("nueva/", views.ficha_crear, name="crear"),
    path("<int:pk>/editar/", views.ficha_editar, name="editar"),
    path("mascota/nueva/", views.mascota_crear, name="mascota_crear"),
]
