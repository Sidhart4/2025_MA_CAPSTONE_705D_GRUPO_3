# main/forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

# Validador de nombres (letras, espacios, tildes, apóstrofo y guion)
nombre_validator = RegexValidator(
    regex=r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' -]+$",
    message="Usa solo letras y espacios."
)

# Teléfono celular Chile: +56 9 ######## (permite con/sin espacios)
telefono_validator = RegexValidator(
    regex=r"^(?:\+?56)?\s*9\s*\d{8}$",
    message="Ingresa un celular chileno válido (+56 9 ########)."
)

class ContactoForm(forms.Form):
    nombre = forms.CharField(
        label="Nombre",
        max_length=100,
        min_length=2,
        validators=[nombre_validator],
        widget=forms.TextInput(attrs={"class": "i", "placeholder": "Tu nombre"})
    )

    correo = forms.EmailField(
        label="Correo",
        widget=forms.EmailInput(attrs={"class": "i", "placeholder": "tucorreo@dominio.com"})
    )

    telefono = forms.CharField(
        label="Teléfono (opcional)",
        required=False,
        validators=[telefono_validator],
        widget=forms.TextInput(attrs={"class": "i", "placeholder": "+56 9 1234 5678"})
    )

    asunto = forms.CharField(
        label="Asunto",
        min_length=4,
        max_length=120,
        widget=forms.TextInput(attrs={"class": "i", "placeholder": "Motivo del contacto"})
    )

    mensaje = forms.CharField(
        label="Mensaje",
        min_length=10,
        max_length=1500,
        widget=forms.Textarea(attrs={"class": "i", "rows": 6, "placeholder": "Cuéntanos tu consulta..."})
    )

    acepto = forms.BooleanField(
        label="Acepto la política de privacidad",
        error_messages={"required": "Debes aceptar la política de privacidad."}
    )

    # --- Normalizaciones / validaciones adicionales ---

    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        # Colapsar espacios internos múltiples
        nombre = " ".join(nombre.split())
        return nombre

    def clean_correo(self):
        # Normaliza a minúsculas
        return self.cleaned_data["correo"].strip().lower()

    def clean_telefono(self):
        tel = self.cleaned_data.get("telefono", "").strip()
        if not tel:
            return tel  # es opcional

        # quitar espacios para validación/formato
        plano = "".join(tel.split())

        # Ya pasó por RegexValidator, pero podemos normalizar el formato
        # Aceptamos: +569######## o 569######## o 9##########
        if plano.startswith("+56"):
            plano = plano[3:]
        elif plano.startswith("56"):
            plano = plano[2:]

        if not plano.startswith("9") or len(plano) != 9:
            # Esto es por si alguien pasó el regex por espacios “raros”
            raise ValidationError("Ingresa un celular chileno válido (+56 9 ########).")

        # Formato bonito: +56 9 1234 5678
        return f"+56 9 {plano[1:5]} {plano[5:]}"

    def clean_asunto(self):
        return " ".join(self.cleaned_data["asunto"].strip().split())

    def clean_mensaje(self):
        msg = self.cleaned_data["mensaje"].strip()
        # Evitar URLs en el mensaje (si no quieres links)
        if "http://" in msg or "https://" in msg:
            raise ValidationError("Por favor, no incluyas enlaces en el mensaje.")
        return msg

    def clean(self):
        """
        Validación cruzada si la necesitas.
        (Ejemplo: exigir teléfono si el asunto indica 'urgente')
        """
        cleaned = super().clean()
        asunto = cleaned.get("asunto", "").lower()
        tel = cleaned.get("telefono", "")

        if "urgente" in asunto and not tel:
            self.add_error("telefono", "Si el asunto es urgente, por favor deja un teléfono de contacto.")
        return cleaned
