# cuentas/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

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
    """
    AuthenticationForm con placeholders, autofocus y mensajes limpios.
    """
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "tu@email.com",
                "autocomplete": "email",
                "autofocus": "autofocus",
                "class": "inpt"
            }
        )
    )
    password = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "********",
                "autocomplete": "current-password",
                "class": "inpt"
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