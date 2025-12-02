from django.db import models

class Cliente(models.Model):
    nombre     = models.CharField(max_length=120)
    email      = models.EmailField(unique=True)
    telefono   = models.CharField(max_length=30, blank=True)
    direccion  = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-id']

    def __str__(self):
        return f"{self.nombre} <{self.email}>"
class Propietario(models.Model):
    nombre   = models.CharField(max_length=120)
    rut      = models.CharField(max_length=20, blank=True, db_index=True)
    email    = models.EmailField(blank=True)
    telefono = models.CharField(max_length=30, blank=True)
    ciudad   = models.CharField(max_length=80, blank=True)
    direccion = models.CharField(max_length=200, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.rut})" if self.rut else self.nombre


class Mascota(models.Model):
    ESPECIE = [("Perro","Perro"),("Gato","Gato"),("Otro","Otro")]
    SEXO = [("M","Macho"),("H","Hembra"),("U","Desconocido")]

    propietario = models.ForeignKey(
        Propietario, on_delete=models.CASCADE, related_name="mascotas"
    )
    nombre   = models.CharField(max_length=120)
    especie  = models.CharField(max_length=10, choices=ESPECIE)
    raza     = models.CharField(max_length=80, blank=True)
    sexo     = models.CharField(max_length=1, choices=SEXO, default="U")
    color    = models.CharField(max_length=80, blank=True)
    nacimiento = models.DateField(null=True, blank=True)
    microchip   = models.CharField(max_length=40, blank=True)
    esterilizado = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} · {self.propietario.nombre}"