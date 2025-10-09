# agenda/forms.py
from django import forms
from .models import Cita
from django.utils import timezone
from .models import Servicio, Profesional, Cita
import datetime as dt

class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ["fecha", "hora", "duracion_min", "profesional", "servicio", "mascota"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora":  forms.TimeInput(attrs={"type": "time"}),
        }
SLOT_MIN = 30
START_H = 9
END_H = 18

class Paso1ServicioForm(forms.Form):
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.all().order_by("nombre"),
        label="Servicio",
        widget=forms.Select(attrs={"class": "input"})
    )

class Paso2HorarioForm(forms.Form):
    fecha = forms.DateField(
        label="Fecha",
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={"type": "date", "class": "input"})
    )
    profesional = forms.ModelChoiceField(
        queryset=Profesional.objects.all().order_by("nombre"),
        required=False, empty_label="Cualquier profesional",
        label="Profesional",
        widget=forms.Select(attrs={"class": "input"})
    )
    hora = forms.ChoiceField(
        label="Hora", choices=[],
        widget=forms.Select(attrs={"class": "input"})
    )

    def __init__(self, *args, **kwargs):
        # Para poder pasar horas disponibles desde la vista
        horas_disponibles = kwargs.pop("horas_disponibles", None)
        super().__init__(*args, **kwargs)
        if horas_disponibles:
            self.fields["hora"].choices = [(h, h) for h in horas_disponibles]
        else:
            self.fields["hora"].choices = [("", "— Selecciona fecha/profesional y pulsa Buscar —")]

class Paso3DatosForm(forms.Form):
    nombre = forms.CharField(label="Tu nombre", max_length=120, widget=forms.TextInput(attrs={"class": "input"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "input"}))
    whatsapp = forms.CharField(label="WhatsApp (opcional)", max_length=20, required=False, widget=forms.TextInput(attrs={"class": "input"}))
    mascota = forms.CharField(label="Nombre de la mascota", max_length=120, widget=forms.TextInput(attrs={"class": "input"}))
    especie = forms.ChoiceField(label="Especie", choices=[("Perro","Perro"),("Gato","Gato"),("Exótico","Exótico")], widget=forms.Select(attrs={"class": "input"}))

    recuerda_mail = forms.BooleanField(label="Recordatorio por email (24h antes)", initial=True, required=False)
    recuerda_wa = forms.BooleanField(label="Recordatorio por WhatsApp (24h antes)", initial=False, required=False)


# ------- util: cálculo de horarios disponibles -------
def _rango_horas(fecha: dt.date, slot_min=SLOT_MIN, start_h=START_H, end_h=END_H):
    base = dt.datetime.combine(fecha, dt.time(start_h, 0))
    stop = dt.datetime.combine(fecha, dt.time(end_h, 30))  # incluye 18:30 si SLOT_MIN=30
    cur = base
    out = []
    while cur <= stop:
        out.append(cur.strftime("%H:%M"))
        cur += dt.timedelta(minutes=slot_min)
    return out

def horas_disponibles(fecha: dt.date, profesional: Profesional | None, slot_min=SLOT_MIN):
    todas = _rango_horas(fecha, slot_min=slot_min)
    if profesional is None:
        # Sin profesional concreto, devolvemos todas (elige luego uno cualquiera al guardar).
        return todas
    ocupadas = set(
        c.hora.strftime("%H:%M") for c in
        Cita.objects.filter(fecha=fecha, profesional=profesional).only("hora")
    )
    return [h for h in todas if h not in ocupadas]