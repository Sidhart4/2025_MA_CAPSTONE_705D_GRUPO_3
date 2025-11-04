from django.contrib import admin
from .models import Cliente, Propietario, Mascota

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display  = ("id", "nombre", "email", "telefono", "created_at")
    search_fields = ("nombre", "email", "telefono")
    list_filter   = ("created_at",)
class MascotaInline(admin.TabularInline):
    model = Mascota
    extra = 0

@admin.register(Propietario)
class PropietarioAdmin(admin.ModelAdmin):
    list_display = ("id","nombre","rut","telefono","email","ciudad","created_at")
    search_fields = ("nombre","rut","email","telefono","ciudad")
    inlines = [MascotaInline]

@admin.register(Mascota)
class MascotaAdmin(admin.ModelAdmin):
    list_display = ("id","nombre","especie","propietario","sexo","nacimiento")
    list_filter = ("especie","sexo")
    search_fields = ("nombre","raza","color","propietario__nombre","propietario__rut")