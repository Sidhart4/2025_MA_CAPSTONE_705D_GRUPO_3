from django.contrib import admin

from .models import PagoTransbank, Venta, VentaItem


class VentaItemInline(admin.TabularInline):
    model = VentaItem
    extra = 0
    readonly_fields = ["producto", "cantidad", "precio_unitario"]


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ["id", "nombre_cliente", "estado", "metodo_pago", "total", "creado_en"]
    list_filter = ["estado", "metodo_pago"]
    search_fields = ["nombre_cliente", "email_cliente"]
    inlines = [VentaItemInline]
    readonly_fields = ["creado_en"]


@admin.register(PagoTransbank)
class PagoTransbankAdmin(admin.ModelAdmin):
    list_display = ["venta", "status", "amount", "authorization_code", "created_at"]
    search_fields = ["token", "buy_order", "venta__id"]
