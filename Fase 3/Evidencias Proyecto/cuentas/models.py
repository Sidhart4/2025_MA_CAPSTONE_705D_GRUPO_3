from django.conf import settings
from django.db import models


class MascotaPerfil(models.Model):
    """Mascota registrada por un usuario para su perfil."""

    ESPECIES = [
        ("perro", "Perro"),
        ("gato", "Gato"),
        ("ave", "Ave"),
        ("otro", "Otro"),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="mascotas_perfil",
    )
    nombre = models.CharField(max_length=120)
    especie = models.CharField(max_length=12, choices=ESPECIES, default="perro")
    raza = models.CharField(max_length=120, blank=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    notas = models.TextField(blank=True)
    foto = models.ImageField(
        upload_to="perfil/mascotas/",
        blank=True,
        null=True,
    )
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Mascota de usuario"
        verbose_name_plural = "Mascotas de usuario"

    def __str__(self) -> str:
        return f"{self.nombre} ({self.get_especie_display()})"
