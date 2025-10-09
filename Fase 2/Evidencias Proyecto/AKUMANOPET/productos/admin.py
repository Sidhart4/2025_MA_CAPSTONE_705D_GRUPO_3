from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "categoria", "marca", "precio", "stock", "activo", "etiqueta", "creado")
    list_filter  = ("categoria", "marca", "etiqueta", "activo")
    search_fields = ("nombre", "descripcion", "marca", "categoria")
    ordering = ("-creado",)

    # <- antes decía 'slug'
    prepopulated_fields = {"url_amigable": ("nombre",)}
    readonly_fields = ("creado",)
