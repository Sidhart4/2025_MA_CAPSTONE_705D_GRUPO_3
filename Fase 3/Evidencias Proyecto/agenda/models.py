# agenda/models.py
from django.db import models
from django.conf import settings


class Profesional(models.Model):
    code = models.SlugField(unique=True, max_length=32)
    nombre = models.CharField(max_length=120)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Profesional"
        verbose_name_plural = "Profesionales"

    def __str__(self):
        return self.nombre


class Servicio(models.Model):
    code = models.SlugField(unique=True, max_length=32)
    nombre = models.CharField(max_length=120)

    # Opcionales (útiles para la reserva del cliente)
    descripcion = models.TextField(blank=True, default="")
    duracion_min_default = models.PositiveIntegerField(default=30)
    precio = models.PositiveIntegerField(default=0)
    icono = models.CharField(max_length=8, blank=True, default="🐾")

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Servicio"
        verbose_name_plural = "Servicios"

    def __str__(self):
        return self.nombre


class Disponibilidad(models.Model):
    """Tramos de atención semanales por profesional (para generar los slots)."""
    LUN = 0; MAR = 1; MIE = 2; JUE = 3; VIE = 4; SAB = 5; DOM = 6
    WEEKDAYS = [
        (LUN, "Lunes"),
        (MAR, "Martes"),
        (MIE, "Miércoles"),
        (JUE, "Jueves"),
        (VIE, "Viernes"),
        (SAB, "Sábado"),
        (DOM, "Domingo"),
    ]

    profesional = models.ForeignKey(
        Profesional, on_delete=models.CASCADE, related_name="disponibilidades"
    )
    dia_semana = models.IntegerField(choices=WEEKDAYS)
    hora_inicio = models.TimeField()  # p.ej. 09:00
    hora_fin = models.TimeField()     # p.ej. 13:00
    slot_min = models.PositiveIntegerField(default=30)

    class Meta:
        ordering = ["profesional", "dia_semana", "hora_inicio"]
        verbose_name = "Disponibilidad"
        verbose_name_plural = "Disponibilidades"
        constraints = [
            # Inicio siempre antes del fin
            models.CheckConstraint(
                check=models.Q(hora_inicio__lt=models.F("hora_fin")),
                name="dispo_inicio_menor_que_fin",
            ),
        ]

    def __str__(self):
        return f"{self.profesional} · {self.get_dia_semana_display()} {self.hora_inicio}-{self.hora_fin}"


class Cita(models.Model):
    fecha = models.DateField()
    hora = models.TimeField()
    duracion_min = models.PositiveIntegerField(default=30)

    profesional = models.ForeignKey(
        Profesional, on_delete=models.CASCADE, related_name="citas"
    )
    servicio = models.ForeignKey(
        Servicio, on_delete=models.PROTECT, related_name="citas"
    )

    mascota = models.CharField(max_length=120)  # ej: "Luna (Perro)"
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL
    )

    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["fecha", "hora"]
        indexes = [models.Index(fields=["fecha", "profesional"])]
        constraints = [
            models.UniqueConstraint(
                fields=["fecha", "hora", "profesional"],
                name="uniq_cita_por_profesional_fecha_hora",
            )
        ]
        verbose_name = "Cita"
        verbose_name_plural = "Citas"

    def __str__(self):
        return f"{self.fecha} {self.hora} · {self.mascota} · {self.profesional}"
# app "agenda" o "core" (donde prefieras) — models.py
from django.db import models

class Propietario(models.Model):
    nombre_completo = models.CharField(max_length=200)
    rut = models.CharField(max_length=20, blank=True, null=True, db_index=True)
    telefono1 = models.CharField(max_length=30, blank=True, null=True)
    telefono2 = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    direccion = models.CharField(max_length=250, blank=True, null=True)
    ciudad = models.CharField(max_length=120, blank=True, null=True)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre_completo


class Mascota(models.Model):
    MACHO = "M"; HEMBRA = "H"
    SEXO_CHOICES = [(MACHO, "Macho"), (HEMBRA, "Hembra")]

    propietario = models.ForeignKey(Propietario, on_delete=models.CASCADE, related_name="mascotas")
    nombre = models.CharField(max_length=120)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES, default=MACHO)
    especie = models.CharField(max_length=60)   # Canino / Felino / etc.
    raza = models.CharField(max_length=120, blank=True, null=True)
    color = models.CharField(max_length=120, blank=True, null=True)
    caracteristica = models.CharField(max_length=250, blank=True, null=True)
    fecha_nacimiento = models.DateField(blank=True, null=True)
    microchip = models.CharField(max_length=60, blank=True, null=True)
    esterilizado = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} ({self.especie})"
