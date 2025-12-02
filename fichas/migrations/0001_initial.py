from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("agenda", "0005_cita_recordatorios"),
        ("cuentas", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FichaClinica",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("fecha", models.DateField(default=django.utils.timezone.localdate)),
                ("motivo", models.CharField(max_length=200)),
                ("diagnostico", models.TextField(blank=True)),
                ("tratamiento", models.TextField(blank=True)),
                ("notas", models.TextField(blank=True)),
                ("proximo_control", models.DateField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "cliente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="fichas_clinicas",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "mascota",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="fichas_clinicas",
                        to="cuentas.mascotaperfil",
                    ),
                ),
                (
                    "profesional",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="fichas_clinicas",
                        to="agenda.profesional",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ficha clínica",
                "verbose_name_plural": "Fichas clínicas",
                "ordering": ["-fecha", "-created_at"],
            },
        ),
    ]
