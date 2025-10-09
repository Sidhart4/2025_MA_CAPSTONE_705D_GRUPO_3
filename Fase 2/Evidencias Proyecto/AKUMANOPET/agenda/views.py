# agenda/views.py
from __future__ import annotations
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django import forms
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import HttpResponseBadRequest
from django.utils.dateparse import parse_date
from django.core.exceptions import PermissionDenied
from django.contrib.auth.decorators import user_passes_test

import datetime as dt
import math
from typing import Iterable, List, Dict, Optional

from .models import Cita, Profesional, Servicio, Disponibilidad


# ==========================
# Permisos
# ==========================
def es_staff_clinica(u):
    return u.is_authenticated and (
        u.is_staff
        or u.groups.filter(name__in=["Veterinarios", "Recepcion"]).exists()
    )

solo_staff = user_passes_test(es_staff_clinica, login_url="cuentas:login")


# ==========================
# Utilidades comunes agenda
# ==========================
def _parse_day(value):
    if not value:
        return timezone.localdate()
    try:
        return dt.date.fromisoformat(value)
    except Exception:
        return timezone.localdate()


def _hours_marks(start_h=9, end_h=18, step_min=30):
    """Genera marcas de la columna de horas (incluye end_h:00)."""
    base = dt.datetime(2000, 1, 1, start_h, 0)
    stop = dt.datetime(2000, 1, 1, end_h, 0)
    out = []
    cur = base
    while cur <= stop:
        out.append(cur.strftime("%H:%M"))
        cur += dt.timedelta(minutes=step_min)
    return out


# ==========================
# Helpers de disponibilidad
# ==========================
def _overlap(a_start: dt.datetime, a_dur_min: int,
             b_start: dt.datetime, b_dur_min: int) -> bool:
    a_end = a_start + dt.timedelta(minutes=a_dur_min)
    b_end = b_start + dt.timedelta(minutes=b_dur_min)
    return a_start < b_end and b_start < a_end


def _iter_times(start: dt.time, end: dt.time, step_min: int) -> Iterable[dt.time]:
    """[start, end) en pasos de `step_min` (end exclusivo)."""
    cur = dt.datetime.combine(dt.date.min, start)
    end_dt = dt.datetime.combine(dt.date.min, end)
    step = dt.timedelta(minutes=step_min)
    while cur + step <= end_dt:
        yield cur.time()
        cur += step


def _citas_tomadas_dict(the_date: dt.date):
    """Devuelve dict por profesional_id con tuplas (inicio_datetime, dur)."""
    d: Dict[int, List] = {}
    for c in Cita.objects.filter(fecha=the_date).select_related("profesional"):
        start_dt = dt.datetime.combine(the_date, c.hora)
        d.setdefault(c.profesional_id, []).append((start_dt, c.duracion_min))
    return d


def horas_disponibles_por_profesional(
    fecha: dt.date,
    profesional: Optional[Profesional],
    duracion_min: int,
) -> Dict[int, List[str]]:
    """
    Calcula horas libres reales (strings HH:MM) por cada profesional
    en `fecha`, usando Disponibilidad + Citas.
    Si `profesional` es None => evalúa todos.
    """
    wd = fecha.weekday()  # 0..6
    dispo_qs = Disponibilidad.objects.filter(dia_semana=wd)
    if profesional:
        dispo_qs = dispo_qs.filter(profesional=profesional)

    ocupadas = _citas_tomadas_dict(fecha)
    out: Dict[int, List[str]] = {}

    for d in dispo_qs.select_related("profesional"):
        step = d.slot_min or 30
        pro_id = d.profesional_id
        for hhmm in _iter_times(d.hora_inicio, d.hora_fin, step):
            start_dt = dt.datetime.combine(fecha, hhmm)
            taken = False
            for tk_start, tk_dur in ocupadas.get(pro_id, []):
                if _overlap(start_dt, duracion_min, tk_start, tk_dur):
                    taken = True
                    break
            if not taken:
                out.setdefault(pro_id, []).append(hhmm.strftime("%H:%M"))

    # Ordena horas
    for k in out.keys():
        out[k].sort()
    return out


def horas_disponibles(
    fecha: dt.date,
    profesional: Optional[Profesional],
    servicio: Optional[Servicio],
) -> List[str]:
    """
    Si hay profesional => horas de ese profesional.
    Si no => unión de horas en las que al menos un profesional está libre.
    """
    dur = servicio.duracion_min_default if servicio else 30
    por_pro = horas_disponibles_por_profesional(fecha, profesional, dur)

    if profesional:
        return por_pro.get(profesional.id, [])

    # "Cualquier profesional": unión sin duplicados
    uniq = sorted({h for hs in por_pro.values() for h in hs})
    return uniq


def profesional_libre_para_hora(
    fecha: dt.date,
    hora_str: str,
    preferido: Optional[Profesional],
    servicio: Optional[Servicio],
) -> Optional[Profesional]:
    """Dado una hora (HH:MM), elige un profesional libre para esa hora."""
    dur = servicio.duracion_min_default if servicio else 30

    # si hay preferido y está libre => úsalo
    if preferido:
        hs = horas_disponibles_por_profesional(fecha, preferido, dur).get(preferido.id, [])
        if hora_str in hs:
            return preferido
        return None  # preferido no libre

    # buscar alguno libre
    por_pro = horas_disponibles_por_profesional(fecha, None, dur)
    for pro_id, horas in por_pro.items():
        if hora_str in horas:
            try:
                return Profesional.objects.get(pk=pro_id)
            except Profesional.DoesNotExist:
                pass
    return None


# ==========================
# Formulario CRUD interno
# ==========================
class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = ["fecha", "hora", "duracion_min", "profesional", "servicio", "mascota"]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "hora": forms.TimeInput(attrs={"type": "time"}),
        }


# ==========================
# Vistas de backoffice
# ==========================
def detalle(request, pk: int):
    """
    El detalle puede verlo:
    - staff/recepción/veterinario
    - el cliente dueño de la cita
    """
    cita = get_object_or_404(Cita, pk=pk)
    es_duenio = request.user.is_authenticated and cita.cliente_id == request.user.id
    if not (es_duenio or es_staff_clinica(request.user)):
        raise PermissionDenied("No tienes permiso para ver esta cita.")
    return render(request, "agenda/cita_detalle.html", {"cita": cita})


@solo_staff
def lista(request):
    mode = request.GET.get("mode", "day")
    day = _parse_day(request.GET.get("day"))
    pro_id = request.GET.get("pro") or ""
    srv_id = request.GET.get("srv") or ""

    qs = Cita.objects.select_related("profesional", "servicio")
    if pro_id:
        qs = qs.filter(profesional_id=pro_id)
    if srv_id:
        qs = qs.filter(servicio_id=srv_id)

    # Parámetros de la grilla (30 min desde 09:00 a 18:00)
    SLOT_MIN = 30
    START_H = 9
    END_H = 18
    rows = ((END_H - START_H) * 60) // SLOT_MIN
    hours = _hours_marks(START_H, END_H, SLOT_MIN)

    citas = None
    days = None
    if mode == "day":
        citas = list(qs.filter(fecha=day).order_by("hora"))
        for c in citas:
            total_min = c.hora.hour * 60 + c.hora.minute
            offset = total_min - START_H * 60
            row = (offset // SLOT_MIN) + 1
            span = max(1, math.ceil(c.duracion_min / SLOT_MIN))
            c.row = int(max(1, min(row, rows)))
            c.span = int(max(1, min(span, rows - c.row + 1)))
    else:
        start = day - dt.timedelta(days=day.weekday())  # lunes
        end = start + dt.timedelta(days=7)              # siguiente lunes
        week_qs = qs.filter(fecha__gte=start, fecha__lt=end).order_by("fecha", "hora")
        by_day = {start + dt.timedelta(days=i): [] for i in range(7)}
        for c in week_qs:
            by_day[c.fecha].append(c)
        days = [{"date": d, "items": by_day[d]} for d in by_day.keys()]

    profesionales = Profesional.objects.all()
    servicios = Servicio.objects.all()

    ctx = {
        "mode": mode,
        "current_day": day,
        "pros": profesionales,
        "servicios": servicios,
        "pro_id": pro_id,
        "srv_id": srv_id,
        "citas": citas,
        "days": days,
        "hours": hours,
        "rows": rows,
        "prev_day": (day - dt.timedelta(days=1)).isoformat(),
        "next_day": (day + dt.timedelta(days=1)).isoformat(),
        "prev_week": (day - dt.timedelta(days=7)).isoformat(),
        "next_week": (day + dt.timedelta(days=7)).isoformat(),
    }
    return render(request, "agenda/agenda.html", ctx)


@solo_staff
def crear(request):
    if request.method == "POST":
        form = CitaForm(request.POST)
        if form.is_valid():
            c = form.save()
            return redirect(f"{reverse('agenda:lista')}?mode=day&day={c.fecha.isoformat()}")
    else:
        form = CitaForm(initial={"fecha": timezone.localdate(), "duracion_min": 30})

    return render(
        request,
        "agenda/cita_form.html",
        {"form": form, "titulo": "Nueva cita", "today": timezone.localdate().isoformat()},
    )


@solo_staff
def editar(request, pk: int):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita)
        if form.is_valid():
            c = form.save()
            return redirect(f"{reverse('agenda:lista')}?mode=day&day={c.fecha.isoformat()}")
    else:
        form = CitaForm(instance=cita)

    return render(
        request,
        "agenda/cita_form.html",
        {"form": form, "titulo": "Editar cita", "today": timezone.localdate().isoformat()},
    )


@solo_staff
def borrar(request, pk: int):
    cita = get_object_or_404(Cita, pk=pk)
    if request.method == "POST":
        day = cita.fecha.isoformat()
        cita.delete()
        messages.success(request, "Cita eliminada.")
        return redirect(f"{reverse('agenda:lista')}?mode=day&day={day}")
    return render(request, "agenda/cita_confirm_delete.html", {"cita": cita})


# =========================================================
# WIZARD PÚBLICO (sin JS): 3 pasos con sesión del usuario
# =========================================================
class Paso1ServicioForm(forms.Form):
    servicio = forms.ModelChoiceField(
        queryset=Servicio.objects.all().order_by("nombre"),
        label="Servicio",
        widget=forms.Select(attrs={"class": "input"})
    )


# agenda/views.py (o donde definiste Paso2HorarioForm)

class Paso2HorarioForm(forms.Form):
    fecha = forms.DateField(
        label="Fecha",
        initial=timezone.localdate,
        widget=forms.DateInput(attrs={"type": "date", "class": "input"})
    )
    profesional = forms.ModelChoiceField(
        queryset=Profesional.objects.none(),   # lo fijamos en __init__
        required=False,
        empty_label="Cualquier profesional disponible",
        label="Profesional",
        widget=forms.Select()                   # le pondremos clase en __init__
    )
    hora = forms.ChoiceField(
        label="Hora", choices=[],
        widget=forms.Select(attrs={"class": "input"})
    )

    def __init__(self, *args, **kwargs):
        horas = kwargs.pop("horas_disponibles", None)
        super().__init__(*args, **kwargs)

        # queryset ordenado y clase para el select
        self.fields["profesional"].queryset = Profesional.objects.order_by("nombre")
        self.fields["profesional"].widget.attrs.update({"class": "pro-select"})

        # horas disponibles
        if horas:
            self.fields["hora"].choices = [(h, h) for h in horas]
        else:
            self.fields["hora"].choices = [("", "— Pulsa Buscar horarios —")]



class Paso3DatosForm(forms.Form):
    nombre = forms.CharField(label="Tu nombre", max_length=120, widget=forms.TextInput(attrs={"class": "input"}))
    email = forms.EmailField(label="Email", widget=forms.EmailInput(attrs={"class": "input"}))
    whatsapp = forms.CharField(label="WhatsApp (opcional)", max_length=20, required=False, widget=forms.TextInput(attrs={"class": "input"}))
    mascota = forms.CharField(label="Nombre de la mascota", max_length=120, widget=forms.TextInput(attrs={"class": "input"}))
    especie = forms.ChoiceField(
        label="Especie",
        choices=[("Perro","Perro"),("Gato","Gato"),("Exótico","Exótico")],
        widget=forms.Select(attrs={"class": "input"})
    )
    recuerda_mail = forms.BooleanField(label="Recordatorio por email (24h antes)", initial=True, required=False)
    recuerda_wa = forms.BooleanField(label="Recordatorio por WhatsApp (24h antes)", initial=False, required=False)


WIZ_KEY = "reserva_wizard"


def _wiz_get(request):
    return request.session.get(WIZ_KEY, {})


def _wiz_set(request, data):
    request.session[WIZ_KEY] = data
    request.session.modified = True


def _wiz_clear(request):
    request.session.pop(WIZ_KEY, None)


@ensure_csrf_cookie
def reservar_wizard(request):
    """
    Paso 1: servicio
    Paso 2: fecha/profesional + hora (buscar horarios / navegar día -> continuar)
    Paso 3: datos cliente/mascota -> crea Cita
    """
    step = int(request.GET.get("step", "1"))
    wiz = _wiz_get(request)

    # ------ PASO 1 ------
    if step == 1:
        if request.method == "POST":
            f = Paso1ServicioForm(request.POST)
            if f.is_valid():
                srv = f.cleaned_data["servicio"]
                wiz.update({"servicio_id": srv.id})
                _wiz_set(request, wiz)
                return redirect(f"{reverse('agenda:reservar')}?step=2")
        else:
            initial = {}
            if wiz.get("servicio_id"):
                initial["servicio"] = wiz["servicio_id"]
            f = Paso1ServicioForm(initial=initial)

        servicios = Servicio.objects.order_by("nombre")
        return render(
            request,
            "agenda/reservar_paso1.html",
            {"form": f, "step": 1, "step_total": 3, "servicios": servicios},
        )

    # ------ PASO 2 ------
    if step == 2:
        # Debe existir un servicio elegido
        if not wiz.get("servicio_id"):
            return redirect(f"{reverse('agenda:reservar')}?step=1")

        # Servicio (para calcular duración)
        srv = get_object_or_404(Servicio, pk=wiz["servicio_id"])

        if request.method == "POST":
            action = request.POST.get("action")          # "buscar" o "continuar"
            shift = request.POST.get("shift_day")        # "-1" o "1" (flechitas)
            fecha_str = request.POST.get("fecha")
            pro_id = request.POST.get("profesional") or None

            # fecha base
            fecha = parse_date(fecha_str) if fecha_str else timezone.localdate()

            # navegación de día
            if shift in ("-1", "1"):
                delta = -1 if shift == "-1" else 1
                fecha = fecha + dt.timedelta(days=delta)

            # profesional (opcional)
            profesional = None
            if pro_id:
                profesional = Profesional.objects.filter(pk=pro_id).first()

            # a) Buscar horarios / navegación
            if action == "buscar" or shift in ("-1", "1"):
                horas = horas_disponibles(fecha, profesional, srv)
                initial = {"fecha": fecha.isoformat()}
                if profesional:
                    initial["profesional"] = profesional.pk

                f = Paso2HorarioForm(
                    request.POST if action == "buscar" else None,
                    initial=initial,
                    horas_disponibles=horas,
                )
                return render(
                    request, "agenda/reservar_paso2.html",
                    {"form": f, "step": 2, "step_total": 3}
                )

            # b) Continuar → valida hora elegida
            horas = horas_disponibles(fecha, profesional, srv)
            f = Paso2HorarioForm(request.POST, horas_disponibles=horas)
            if f.is_valid():
                wiz.update({
                    "fecha": fecha.isoformat(),
                    "profesional_id": profesional.id if profesional else None,
                    "hora": f.cleaned_data["hora"],
                })
                _wiz_set(request, wiz)
                return redirect(f"{reverse('agenda:reservar')}?step=3")

            # si no válido, re-render con errores
            return render(
                request, "agenda/reservar_paso2.html",
                {"form": f, "step": 2, "step_total": 3}
            )

        # GET inicial: precarga con sesión o con hoy
        fecha_init = parse_date(wiz.get("fecha")) if wiz.get("fecha") else timezone.localdate()
        pro_obj = Profesional.objects.filter(pk=wiz.get("profesional_id")).first() if wiz.get("profesional_id") else None

        horas = horas_disponibles(fecha_init, pro_obj, srv)
        initial = {"fecha": fecha_init.isoformat()}
        if pro_obj:
            initial["profesional"] = pro_obj.pk

        f = Paso2HorarioForm(initial=initial, horas_disponibles=horas)
        return render(
            request, "agenda/reservar_paso2.html",
            {"form": f, "step": 2, "step_total": 3}
        )

    # ------ PASO 3 ------
    if step == 3:
        if not all(k in wiz for k in ("servicio_id", "fecha", "hora")):
            return redirect(f"{reverse('agenda:reservar')}?step=1")

        if request.method == "POST":
            f = Paso3DatosForm(request.POST)
            if f.is_valid():
                srv = get_object_or_404(Servicio, pk=wiz["servicio_id"])
                fecha = parse_date(wiz["fecha"])
                hh, mm = wiz["hora"].split(":")
                hora = dt.time(int(hh), int(mm))

                preferido = None
                if wiz.get("profesional_id"):
                    preferido = get_object_or_404(Profesional, pk=wiz["profesional_id"])

                # Elegir profesional libre para esa hora (puede ser el preferido)
                pro_final = profesional_libre_para_hora(fecha, wiz["hora"], preferido, srv)
                if not pro_final:
                    messages.error(request, "Ese horario ya fue tomado. Elige otro por favor.")
                    return redirect(f"{reverse('agenda:reservar')}?step=2")

                dur = getattr(srv, "duracion_min_default", None) or 30

                # doble verificación por carrera
                if Cita.objects.filter(fecha=fecha, hora=hora, profesional=pro_final).exists():
                    messages.error(request, "Ese horario ya fue tomado. Elige otro por favor.")
                    return redirect(f"{reverse('agenda:reservar')}?step=2")

                cita = Cita.objects.create(
                    fecha=fecha,
                    hora=hora,
                    duracion_min=dur,
                    profesional=pro_final,
                    servicio=srv,
                    mascota=f"{f.cleaned_data['mascota']} ({f.cleaned_data['especie']})",
                    cliente=request.user if request.user.is_authenticated else None,
                )
                _wiz_clear(request)
                return redirect("agenda:reservar_exito", pk=cita.pk)
        else:
            f = Paso3DatosForm()

        srv = get_object_or_404(Servicio, pk=wiz["servicio_id"])
        pro = get_object_or_404(Profesional, pk=wiz["profesional_id"]) if wiz.get("profesional_id") else None

        resumen = {"servicio": srv, "fecha": wiz["fecha"], "hora": wiz["hora"], "profesional": pro}
        return render(
            request, "agenda/reservar_paso3.html",
            {"form": f, "step": 3, "step_total": 3, "resumen": resumen}
        )

    return HttpResponseBadRequest("Paso inválido")

def reservar_exito(request, pk: int):
    cita = get_object_or_404(Cita, pk=pk)
    return render(request, "agenda/reservar_exito.html", {"cita": cita})


def reservar_paso1(request):
    step = 1
    total_steps = 3
    percent = int(round(step * 100 / total_steps))
    return render(request, "agenda/reservar_paso1.html", {
        "step": step,
        "total_steps": total_steps,
        "percent": percent,
    })
