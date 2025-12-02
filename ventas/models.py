from django.conf import settings
from django.db import models

try:
    # Si tienes app clientes, déjalo así; si no la tienes, pon cliente = CharField en su lugar
    from clientes.models import Cliente  # type: ignore
except Exception:
    Cliente = None  # para evitar import-time errors cuando la app no existe

from productos.models import Producto


class Venta(models.Model):
    METODOS = (
        ("EFECTIVO", "Efectivo"),
        ("TARJETA", "Tarjeta"),
        ("TRANSFERENCIA", "Transferencia"),
        ("WEBPAY", "Webpay (Transbank)"),
    )
    ESTADOS = (
        ("PAGADA", "Pagada"),
        ("ANULADA", "Anulada"),
        ("PENDIENTE", "Pendiente"),
    )

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Si tienes clientes.Cliente, este FK funcionará; si no, comenta estas 2 líneas y usa un CharField.
    cliente = models.ForeignKey(
        Cliente, on_delete=models.SET_NULL, null=True, blank=True
    ) if Cliente else None  # type: ignore

    metodo_pago = models.CharField(max_length=30, choices=METODOS, default="EFECTIVO")
    estado = models.CharField(max_length=30, choices=ESTADOS, default="PAGADA")

    total = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    nombre_cliente = models.CharField(max_length=150, blank=True, default="")
    rut_cliente = models.CharField(max_length=20, blank=True, default="")
    email_cliente = models.EmailField(blank=True, default="")
    telefono_cliente = models.CharField(max_length=30, blank=True, default="")
    direccion_entrega = models.CharField(max_length=255, blank=True, default="")
    notas_cliente = models.TextField(blank=True, default="")
    # NO hay campo 'fecha'; se usa creado_en para ordenar/filtrar
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ventas_venta"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"Venta #{self.pk} - {self.creado_en:%Y-%m-%d} - ${self.total:,.2f}"

    def recomputar_total(self):
        total = sum((i.cantidad or 0) * (i.precio_unitario or 0) for i in self.items.all())
        self.total = total
        return total

    def save(self, *args, **kwargs):
        # si ya existe y tiene items, recalcula total
        super().save(*args, **kwargs)
        if self.pk:
            self.recomputar_total()
            super().save(update_fields=["total"])


class VentaItem(models.Model):
    venta = models.ForeignKey(Venta, related_name="items", on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        db_table = "ventas_ventaitem"

    def __str__(self):
        return f"Item #{self.pk} - Venta {self.venta_id}"

    def save(self, *args, **kwargs):
        # Si no se pasó precio, toma el del producto
        if (self.precio_unitario or 0) == 0 and self.producto_id:
            self.precio_unitario = self.producto.precio or 0
        super().save(*args, **kwargs)


class PagoTransbank(models.Model):
    ESTADOS = (
        ("CREADA", "Creada"),
        ("AUTORIZADA", "Autorizada"),
        ("RECHAZADA", "Rechazada"),
        ("ANULADA", "Anulada"),
        ("ERROR", "Error"),
    )

    venta = models.OneToOneField(
        Venta,
        related_name="pago_transbank",
        on_delete=models.CASCADE,
    )
    token = models.CharField(max_length=128, unique=True)
    buy_order = models.CharField(max_length=26)
    session_id = models.CharField(max_length=60)
    amount = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=ESTADOS, default="CREADA")
    authorization_code = models.CharField(max_length=20, blank=True, default="")
    payment_type = models.CharField(max_length=12, blank=True, default="")
    installments = models.PositiveIntegerField(null=True, blank=True)
    accounting_date = models.CharField(max_length=10, blank=True, default="")
    transaction_date = models.DateTimeField(null=True, blank=True)
    response_payload = models.JSONField(default=dict, blank=True)
    email_enviado = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pago Webpay"
        verbose_name_plural = "Pagos Webpay"

    def __str__(self):
        return f"Pago Webpay #{self.venta_id} ({self.status})"


# -------------------- Caja (sesiones y movimientos) --------------------

class CajaSesion(models.Model):
    ESTADOS = (("ABIERTA", "Abierta"), ("CERRADA", "Cerrada"))

    encargado = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    caja_nombre = models.CharField(max_length=60, blank=True, default="")

    estado = models.CharField(max_length=16, choices=ESTADOS, default="ABIERTA")
    saldo_inicial = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    saldo_final = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    abierto_en = models.DateTimeField(auto_now_add=True)
    cerrado_en = models.DateTimeField(null=True, blank=True)
    observacion = models.TextField(blank=True, default="")

    class Meta:
        db_table = "ventas_cajasesion"
        ordering = ["-abierto_en"]

    def __str__(self):
        user = getattr(self.encargado, "username", "?")
        return f"Caja #{self.pk} · {user} · {self.estado}"

    @property
    def abierta(self):
        return self.estado == "ABIERTA"

    def recomputar_saldo(self):
        ingresos = sum((m.monto or 0) for m in self.movimientos.filter(tipo="INGRESO"))
        egresos = sum((m.monto or 0) for m in self.movimientos.filter(tipo="EGRESO"))
        self.saldo_final = (self.saldo_inicial or 0) + ingresos - egresos
        return self.saldo_final


class CajaMovimiento(models.Model):
    TIPOS = (("INGRESO", "Ingreso"), ("EGRESO", "Egreso"))
    ORIGENES = (("MANUAL", "Manual"), ("VENTA", "Venta"))

    sesion = models.ForeignKey(CajaSesion, related_name="movimientos", on_delete=models.CASCADE)
    tipo = models.CharField(max_length=16, choices=TIPOS)
    origen = models.CharField(max_length=16, choices=ORIGENES, default="MANUAL")
    venta = models.ForeignKey('Venta', null=True, blank=True, on_delete=models.SET_NULL)
    monto = models.DecimalField(max_digits=14, decimal_places=2)
    descripcion = models.CharField(max_length=240, blank=True, default="")
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "ventas_cajamovimiento"
        ordering = ["-creado_en"]

    def __str__(self):
        return f"{self.tipo} ${self.monto} · Sesion {self.sesion_id}"
