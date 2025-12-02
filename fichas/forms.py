from django import forms
from django.contrib.auth import get_user_model

from agenda.models import Profesional
from cuentas.models import MascotaPerfil
from .models import FichaClinica

User = get_user_model()


class FichaClinicaForm(forms.ModelForm):
    class Meta:
        model = FichaClinica
        fields = [
            "cliente",
            "mascota",
            "profesional",
            "fecha",
            "motivo",
            "diagnostico",
            "tratamiento",
            "notas",
            "proximo_control",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "inpt"}),
            "proximo_control": forms.DateInput(attrs={"type": "date", "class": "inpt"}),
            "motivo": forms.TextInput(attrs={"class": "inpt"}),
            "diagnostico": forms.Textarea(attrs={"rows": 3, "class": "inpt"}),
            "tratamiento": forms.Textarea(attrs={"rows": 3, "class": "inpt"}),
            "notas": forms.Textarea(attrs={"rows": 3, "class": "inpt"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["cliente"].queryset = User.objects.order_by("first_name", "username")
        self.fields["mascota"].queryset = MascotaPerfil.objects.select_related("usuario").order_by("nombre")
        self.fields["profesional"].queryset = Profesional.objects.order_by("nombre")

    def clean(self):
        cleaned = super().clean()
        cliente = cleaned.get("cliente")
        mascota = cleaned.get("mascota")
        if cliente and mascota and mascota.usuario_id != cliente.id:
            self.add_error("mascota", "La mascota seleccionada no pertenece a este cliente.")
        return cleaned


class MascotaPerfilStaffForm(forms.ModelForm):
    """Formulario para que staff/veterinario cree mascotas para un usuario."""

    usuario = forms.ModelChoiceField(
        queryset=User.objects.order_by("first_name", "username"),
        label="Cliente",
        help_text="Cliente dueño de la mascota.",
    )

    class Meta:
        model = MascotaPerfil
        fields = ["usuario", "nombre", "especie", "raza", "fecha_nacimiento", "foto", "notas"]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date", "class": "inpt"}),
            "notas": forms.Textarea(attrs={"rows": 3, "class": "inpt"}),
        }

    def clean(self):
        cleaned = super().clean()
        usuario = cleaned.get("usuario")
        nombre = cleaned.get("nombre")
        if usuario and nombre:
            exists = MascotaPerfil.objects.filter(usuario=usuario, nombre__iexact=nombre)
            if self.instance.pk:
                exists = exists.exclude(pk=self.instance.pk)
            if exists.exists():
                self.add_error("nombre", "Este cliente ya tiene una mascota con ese nombre.")
        return cleaned
