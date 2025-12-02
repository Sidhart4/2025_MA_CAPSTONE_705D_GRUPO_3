from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("ventas", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="CajaSesion",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("caja_nombre", models.CharField(blank=True, default="", max_length=60)),
                ("estado", models.CharField(choices=[("ABIERTA", "Abierta"), ("CERRADA", "Cerrada")], default="ABIERTA", max_length=16)),
                ("saldo_inicial", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("saldo_final", models.DecimalField(decimal_places=2, default=0, max_digits=14)),
                ("abierto_en", models.DateTimeField(auto_now_add=True)),
                ("cerrado_en", models.DateTimeField(blank=True, null=True)),
                ("observacion", models.TextField(blank=True, default="")),
                ("encargado", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "db_table": "ventas_cajasesion",
                "ordering": ["-abierto_en"],
            },
        ),
        migrations.CreateModel(
            name="CajaMovimiento",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("INGRESO", "Ingreso"), ("EGRESO", "Egreso")], max_length=16)),
                ("origen", models.CharField(choices=[("MANUAL", "Manual"), ("VENTA", "Venta")], default="MANUAL", max_length=16)),
                ("monto", models.DecimalField(decimal_places=2, max_digits=14)),
                ("descripcion", models.CharField(blank=True, default="", max_length=240)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("sesion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="movimientos", to="ventas.cajasesion")),
                ("venta", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="ventas.venta")),
            ],
            options={
                "db_table": "ventas_cajamovimiento",
                "ordering": ["-creado_en"],
            },
        ),
    ]

