from django.urls import path
from .views import lista, crear, editar, borrar

app_name = "productos"

urlpatterns = [
    path("", lista, name="lista"),
    path("nuevo/", crear, name="crear"),
    path("<int:pk>/editar/", editar, name="editar"),
    path("<int:pk>/borrar/", borrar, name="borrar"),
]
