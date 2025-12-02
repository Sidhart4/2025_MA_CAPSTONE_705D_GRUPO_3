# productos/models.py
from django.db import models
from django.utils.text import slugify

class Producto(models.Model):
    # Catálogos/choices opcionales
    ETIQUETAS = [
        ("", "—"),          # sin etiqueta
        ("nuevo", "Nuevo"),
        ("oferta", "Oferta"),
    ]
    TIPOS_MASCOTA = [
        ("Perro", "Perro"),
        ("Gato", "Gato"),
    ]

    nombre          = models.CharField(max_length=150)
    url_amigable    = models.SlugField(unique=True, blank=True)  # antes "slug"
    descripcion     = models.TextField(blank=True)
    categoria    = models.CharField(max_length=80, blank=True, default="")            # antes "category"
    tipo_mascota    = models.CharField(max_length=20, choices=TIPOS_MASCOTA, blank=True)  # antes "pet"
    marca        = models.CharField(max_length=80, blank=True, default="")

    precio          = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_anterior = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # antes "old_price"
    valoracion      = models.DecimalField(max_digits=3, decimal_places=1, default=0)               # antes "rating"
    stock           = models.PositiveIntegerField(default=0)

    etiqueta        = models.CharField(max_length=20, choices=ETIQUETAS, default="", blank=True)    # antes "badge"

    imagen          = models.ImageField(upload_to="productos", blank=True, null=True)

    activo          = models.BooleanField(default=True)
    creado          = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        # Autogenerar URL amigable si viene vacía
        if not self.url_amigable and self.nombre:
            base = slugify(self.nombre)
            slug = base
            i = 1
            # asegurar unicidad
            while Producto.objects.filter(url_amigable=slug).exclude(pk=self.pk).exists():
                i += 1
                slug = f"{base}-{i}"
            self.url_amigable = slug
        super().save(*args, **kwargs)
