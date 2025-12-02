
from django.db import models

class Producto(models.Model):
    nombre       = models.CharField(max_length=160)
    slug         = models.SlugField(max_length=180, unique=True)
    descripcion  = models.TextField(blank=True)
    precio       = models.PositiveIntegerField()
    precio_antes = models.PositiveIntegerField(null=True, blank=True)
    stock        = models.PositiveIntegerField(default=0)
    rating       = models.DecimalField(max_digits=2, decimal_places=1, default=4.5)  # 0–5
    destacado    = models.BooleanField(default=False)
    imagen       = models.ImageField(upload_to="productos/", blank=True, null=True)

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return self.nombre

    @property
    def en_oferta(self):
        return bool(self.precio_antes and self.precio_antes > self.precio)
