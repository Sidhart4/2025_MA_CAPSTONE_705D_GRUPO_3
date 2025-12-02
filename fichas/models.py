from django.db import models
from django.conf import settings
from django.utils import timezone


class FichaClinica(models.Model):
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fichas_clinicas",
    )
    mascota = models.ForeignKey(
        "cuentas.MascotaPerfil",
        on_delete=models.PROTECT,
        related_name="fichas_clinicas",
    )
    profesional = models.ForeignKey(
        "agenda.Profesional",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="fichas_clinicas",
    )
    fecha = models.DateField(default=timezone.localdate)
    motivo = models.CharField(max_length=200)
    diagnostico = models.TextField(blank=True)
    tratamiento = models.TextField(blank=True)
    notas = models.TextField(blank=True)
    proximo_control = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-fecha", "-created_at"]
        verbose_name = "Ficha clínica"
        verbose_name_plural = "Fichas clínicas"

    def __str__(self):
        return f"{self.mascota} ({self.fecha})"

# Create your models here.
