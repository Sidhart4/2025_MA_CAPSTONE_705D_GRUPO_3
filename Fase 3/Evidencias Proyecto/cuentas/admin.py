from django.contrib import admin

from .models import MascotaPerfil


@admin.register(MascotaPerfil)
class MascotaPerfilAdmin(admin.ModelAdmin):
    list_display = ["nombre", "usuario", "especie", "creada"]
    search_fields = ["nombre", "usuario__username", "usuario__email"]
    list_filter = ["especie", "creada"]
