from django import forms
from .models import Producto

class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "marca",
            "tipo_mascota",
            "categoria",
            "precio",
            "precio_anterior",  # si existe en tu modelo
            "stock",
            "descripcion",
            "imagen",           # si es ImageField y es obligatorio
            "activo",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "input"}),
            "marca": forms.TextInput(attrs={"class": "input"}),                # o Select si corresponde
            "tipo_mascota": forms.Select(attrs={"class": "input"}),           # Perro/Gato, etc.
            "categoria": forms.Select(attrs={"class": "input"}),
            "precio": forms.NumberInput(attrs={"step": "0.01", "class": "input"}),
            "precio_anterior": forms.NumberInput(attrs={"step": "0.01", "class": "input"}),
            "stock": forms.NumberInput(attrs={"min": 0, "class": "input"}),
            "descripcion": forms.Textarea(attrs={"rows": 3, "class": "input"}),
            "activo": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }
