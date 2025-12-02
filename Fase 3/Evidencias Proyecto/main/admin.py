
from django.contrib import admin
from .models import Producto

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display  = ("nombre", "precio", "precio_antes", "stock", "destacado", "updated_at")
    list_filter   = ("destacado",)
    search_fields = ("nombre", "slug")
    prepopulated_fields = {"slug": ("nombre",)}
