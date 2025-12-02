from rest_framework import serializers
from .models import Producto

class ProductoSerializer(serializers.ModelSerializer):
    imagen_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Producto
        # 👉 Deja SOLO los campos reales de tu modelo
        fields = [
            "id",
            "nombre",
            "descripcion",
            "precio",
            "precio_anterior",
            "stock",
            "categoria",
            "activo",
            "valoracion",
            "etiqueta",
            "imagen",       # devuelve la ruta (relativa)
            "imagen_url",   # absoluta (útil para React/Electron)
        ]

    def get_imagen_url(self, obj):
        request = self.context.get("request")
        if obj.imagen and hasattr(obj.imagen, "url"):
            url = obj.imagen.url
            return request.build_absolute_uri(url) if request else url
        return None
