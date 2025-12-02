from django.contrib import admin
from .models import FichaClinica


@admin.register(FichaClinica)
class FichaClinicaAdmin(admin.ModelAdmin):
    list_display = ("id", "mascota", "cliente", "fecha", "profesional")
    list_filter = ("fecha", "profesional")
    search_fields = ("mascota__nombre", "cliente__first_name", "cliente__username", "cliente__email")
    autocomplete_fields = ("cliente", "mascota", "profesional")
