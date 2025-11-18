# agenda/utils_slots.py
from __future__ import annotations
from datetime import datetime, date, time, timedelta
from typing import Iterable, List, Dict, Optional, Tuple

from django.db.models import Q

from .models import Disponibilidad, Cita, Profesional, Servicio


def _iter_times(start: time, end: time, step_min: int) -> Iterable[time]:
    """Genera HH:MM... desde start hasta end-step (end exclusivo)."""
    cur = datetime.combine(date.min, start)
    end_dt = datetime.combine(date.min, end)
    step = timedelta(minutes=step_min)
    while cur + step <= end_dt:
        yield cur.time()
        cur += step


def _overlap(a_start: datetime, a_dur_min: int,
             b_start: datetime, b_dur_min: int) -> bool:
    """¿Se solapan dos intervalos (en minutos)?"""
    a_end = a_start + timedelta(minutes=a_dur_min)
    b_end = b_start + timedelta(minutes=b_dur_min)
    return a_start < b_end and b_start < a_end


def day_slots(
    the_date: date,
    profesional: Optional[Profesional],
    servicio: Optional[Servicio],
    fallback_slot_min: int = 30,
) -> List[Dict]:
    """
    Construye los slots disponibles para un día.
    Si profesional es None => combina las disponibilidades de todos (modo 'cualquier profesional').
    Duración del servicio: servicio.duracion_min_default o fallback_slot_min.
    """
    dur = servicio.duracion_min_default if servicio else fallback_slot_min
    wd = the_date.weekday()  # 0..6

    # 1) Disponibilidades para ese día
    dispo_qs = Disponibilidad.objects.filter(dia_semana=wd)
    if profesional:
        dispo_qs = dispo_qs.filter(profesional=profesional)

    # 2) Citas ya tomadas (cualquier profesional o sólo uno)
    citas_qs = Cita.objects.filter(fecha=the_date)
    if profesional:
        citas_qs = citas_qs.filter(profesional=profesional)

    # Prepara lista de (inicio_datetime, dur_min, profesional_id)
    taken: List[Tuple[datetime, int, int]] = []
    for c in citas_qs.select_related("profesional"):
        start_dt = datetime.combine(the_date, c.hora)
        taken.append((start_dt, c.duracion_min, c.profesional_id))

    out: List[Dict] = []

    for d in dispo_qs.select_related("profesional"):
        step = d.slot_min or fallback_slot_min
        for hhmm in _iter_times(d.hora_inicio, d.hora_fin, step):
            start_dt = datetime.combine(the_date, hhmm)

            # ¿está libre? (no se solapa con ninguna cita del mismo profesional)
            clash = False
            for tk_start, tk_dur, tk_pro in taken:
                if profesional:  # filtrado por uno
                    if _overlap(start_dt, dur, tk_start, tk_dur):
                        clash = True
                        break
                else:
                    # modo "cualquier profesional": el slot está libre si al menos UN profesional
                    # tiene este horario sin solapes. Entonces se marca como libre por ese profesional.
                    if d.profesional_id == tk_pro and _overlap(start_dt, dur, tk_start, tk_dur):
                        clash = True
                        break

            if not clash:
                out.append({
                    "hora": hhmm.strftime("%H:%M"),
                    "datetime": start_dt,
                    "profesional_id": d.profesional_id,
                    "profesional": d.profesional,    # útil para “cualquier profesional”
                    "duracion": dur,
                    "disponible": True,
                    "value": f"{hhmm.strftime('%H:%M')}|{d.profesional_id}",
                })
            else:
                out.append({
                    "hora": hhmm.strftime("%H:%M"),
                    "datetime": start_dt,
                    "profesional_id": d.profesional_id,
                    "profesional": d.profesional,
                    "duracion": dur,
                    "disponible": False,
                    "value": "",
                })

    # Ordena por hora
    out.sort(key=lambda s: (s["hora"], s["profesional_id"]))
    return out


def week_slots(
    start_date: date,
    profesional: Optional[Profesional],
    servicio: Optional[Servicio],
    days: int = 7,
) -> List[Dict]:
    """Devuelve slots de 7 días (o 'days') a partir de start_date."""
    out: List[Dict] = []
    for i in range(days):
        d = start_date + timedelta(days=i)
        slots_dia = day_slots(d, profesional, servicio)
        for s in slots_dia:
            s["dia_corto"] = d.strftime("%a")  # Lun, Mar, ...
            s["fecha"] = d
        out.extend(slots_dia)
    return out
