import datetime as dt
from urllib.parse import urljoin

from django.conf import settings
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone

from agenda.models import Cita
from main.utils_email import enviar_correo_recordatorio
from main.utils_whatsapp import enviar_whatsapp_recordatorio


class Command(BaseCommand):
    help = "Envía recordatorios por WhatsApp o email 24 horas antes de la cita. Ejecuta este comando de forma horaria para asegurar la ventana completa."

    def add_arguments(self, parser):
        parser.add_argument(
            "--window-hours",
            type=int,
            default=25,
            help="Ventana de horas desde ahora para enviar recordatorios (default: 25h).",
        )

    def handle(self, *args, **options):
        now = timezone.now()
        start = now + dt.timedelta(hours=24)
        end = now + dt.timedelta(hours=options["window_hours"])
        qs = (
            Cita.objects.filter(fecha__gte=start.date(), fecha__lte=end.date())
            .select_related("profesional", "servicio")
            .order_by("fecha", "hora")
        )

        enviados = 0
        for cita in qs:
            cita_dt = cita.inicio_datetime()
            if not (start <= cita_dt <= end):
                continue

            path = reverse("agenda:reservar_exito", kwargs={"pk": cita.pk})
            base_url = getattr(settings, "BASE_URL", "").strip()
            enlace = urljoin(base_url.rstrip("/") + "/", path.lstrip("/")) if base_url else None

            if not enlace:
                enlace = path

            mascota_txt = cita.mascota or ""
            especie_txt = ""
            if "(" in mascota_txt and mascota_txt.endswith(")"):
                especie_txt = mascota_txt.rsplit("(", 1)[-1].rstrip(")")
                mascota_txt = mascota_txt.rsplit("(", 1)[0].strip()

            ctx = {
                "nombre_cliente": cita.nombre_cliente or "cliente",
                "nombre_mascota": cita.mascota,
                "especie": especie_txt,
                "servicio": getattr(cita.servicio, "nombre", ""),
                "profesional": getattr(cita.profesional, "nombre", ""),
                "fecha": cita.fecha.strftime("%d/%m/%Y"),
                "hora": cita.hora.strftime("%H:%M"),
                "enlace": enlace,
                "direccion_clinica": getattr(settings, "CLINIC_ADDRESS", "Monte Palomar 171, Maipú"),
                "year": timezone.now().year,
            }

            updated_fields = []

            if cita.recuerda_mail and cita.email_contacto and not cita.recordatorio_mail_enviado:
                try:
                    enviar_correo_recordatorio(cita.email_contacto, ctx)
                    cita.recordatorio_mail_enviado = now
                    updated_fields.append("recordatorio_mail_enviado")
                    enviados += 1
                except Exception as exc:
                    self.stderr.write(f"[Cita {cita.id}] Error email: {exc}")

            if cita.recuerda_wa and cita.whatsapp_contacto and not cita.recordatorio_wa_enviado:
                body = (
                    f"Hola {cita.nombre_cliente or ''}, recordatorio de tu cita mañana "
                    f"{ctx['fecha']} a las {ctx['hora']} - {ctx['servicio']}. "
                    f"Ubicación: {ctx['direccion_clinica']}."
                )
                if ctx["enlace"]:
                    body += f" Detalles: {ctx['enlace']}"
                ok, error = enviar_whatsapp_recordatorio(cita.whatsapp_contacto, body)
                if ok:
                    cita.recordatorio_wa_enviado = now
                    updated_fields.append("recordatorio_wa_enviado")
                    enviados += 1
                else:
                    self.stderr.write(f"[Cita {cita.id}] Error WhatsApp: {error}")

            if updated_fields:
                cita.save(update_fields=updated_fields)

        self.stdout.write(self.style.SUCCESS(f"Recordatorios enviados: {enviados}"))
