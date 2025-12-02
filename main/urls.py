from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    path('', views.home, name='home'),     # /
    path('inicio/', views.home, name='inicio'),  # opcional /inicio
    path("contacto/", views.contacto, name="contacto"),
    path("equipo/", views.equipo, name="equipo"),
    path("precios/", views.precios, name="precios"),
]
