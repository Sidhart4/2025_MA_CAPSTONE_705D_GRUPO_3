# cuentas/forms.py
import datetime as dt

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import MascotaPerfil


class RegistroForm(UserCreationForm):
    first_name = forms.CharField(label="Nombre", max_length=150, required=False)
    email = forms.EmailField(label="Email", required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data.get("first_name", "")
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class PrettyAuthForm(AuthenticationForm):
    """AuthenticationForm con placeholders, autofocus y mensajes limpios."""

    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "tu@email.com",
                "autocomplete": "email",
                "autofocus": "autofocus",
                "class": "inpt",
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "********",
                "autocomplete": "current-password",
                "class": "inpt",
            }
        ),
    )

    def get_invalid_login_error(self):
        # Mensaje genérico por defecto (lo refinamos en la vista)
        return forms.ValidationError(
            "Email o contraseña incorrectos.",
            code="invalid_login",
        )

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                "Tu cuenta está desactivada. Contáctanos si crees que es un error.",
                code="inactive",
            )


class MascotaPerfilForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.usuario = kwargs.pop("usuario", None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = MascotaPerfil
        fields = ["nombre", "especie", "raza", "fecha_nacimiento", "foto", "notas"]
        widgets = {
            "nombre": forms.TextInput(attrs={"placeholder": "Firulais", "class": "inpt"}),
            "especie": forms.Select(attrs={"class": "inpt"}),
            "raza": forms.TextInput(attrs={"placeholder": "Raza / mezcla", "class": "inpt"}),
            "fecha_nacimiento": forms.DateInput(
                attrs={"type": "date", "class": "inpt"}, format="%Y-%m-%d"
            ),
            "notas": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Notas o necesidades especiales",
                    "class": "inpt",
                }
            ),
        }

    def clean_nombre(self):
        nombre = (self.cleaned_data.get("nombre") or "").strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        if not any(char.isalpha() for char in nombre):
            raise forms.ValidationError("El nombre debe incluir letras.")
        return nombre

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get("fecha_nacimiento")
        if not fecha:
            return fecha
        hoy = dt.date.today()
        if fecha > hoy:
            raise forms.ValidationError("La fecha de nacimiento no puede ser futura.")
        limite = hoy - dt.timedelta(days=365 * 40)
        if fecha < limite:
            raise forms.ValidationError("Revisa la fecha, parece muy antigua para una mascota.")
        return fecha

    def clean(self):
        cleaned = super().clean()
        nombre = cleaned.get("nombre")
        if self.usuario and nombre:
            qs = MascotaPerfil.objects.filter(usuario=self.usuario, nombre__iexact=nombre)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            existe = qs.exists()
            if existe:
                self.add_error(
                    "nombre", "Ya tienes una mascota registrada con ese nombre."
                )
        return cleaned
