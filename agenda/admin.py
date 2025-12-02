# agenda/admin.py
from django.contrib import admin
from .models import Cita, Profesional, Servicio, Disponibilidad

@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    list_display = ("fecha", "hora", "duracion_min", "profesional", "servicio", "mascota", "cliente")
    list_filter = ("fecha", "profesional", "servicio")
    search_fields = ("mascota", "profesional__nombre", "servicio__nombre", "cliente__username")
    date_hierarchy = "fecha"
    ordering = ("-fecha", "hora")

@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = ("nombre", "code")
    search_fields = ("nombre", "code")
    ordering = ("nombre",)

@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "code", "duracion_min_default", "precio")
    search_fields = ("nombre", "code")
    ordering = ("nombre",)

@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ("profesional", "dia_semana", "hora_inicio", "hora_fin", "slot_min")
    list_filter  = ("profesional", "dia_semana")
    ordering = ("profesional", "dia_semana", "hora_inicio")
