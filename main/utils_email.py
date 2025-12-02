# main/utils_email.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from email.mime.image import MIMEImage
from pathlib import Path

def enviar_correo_reserva(to_email: str, ctx: dict):
    """
    Envía el correo de confirmación de reserva.
    - Plantilla: main/templates/main/email/reserva_confirmacion.html
      (se carga como "main/email/reserva_confirmacion.html")
    - Adjunta logo inline (CID) desde main/static/images/logo.png
    """
    subject = "✅ Tu reserva en Akuma no Pet fue confirmada"

    # Render HTML del correo (usa {{ enlace }}, {{ year }}, etc.)
    # OJO: Ruta namespaced por app "main/"
    html = render_to_string("main/email/reserva_confirmacion.html", ctx)

    # Texto plano fallback (por si el cliente no soporta HTML)
    txt = (
        f"Hola {ctx.get('nombre_cliente','')}, tu reserva fue confirmada.\n"
        f"Servicio: {ctx.get('servicio','')} | Fecha: {ctx.get('fecha','')} {ctx.get('hora','')}\n"
        f"Mascota: {ctx.get('nombre_mascota','')} ({ctx.get('especie','')})\n"
        f"Ver / Reprogramar: {ctx.get('enlace','')}\n"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html, "text/html")

    # Adjuntar LOGO inline (CID)
    # Ruta esperada según tu estructura: main/static/images/logo.png
    candidates = [
        Path(settings.BASE_DIR) / "main" / "static" / "images" / "logo.png",
        Path(settings.BASE_DIR) / "static" / "images" / "logo.png",
    ]
    logo_path = next((p for p in candidates if p.exists()), None)

    if logo_path and logo_path.exists():
        with open(logo_path, "rb") as f:
            img = MIMEImage(f.read())
        img.add_header("Content-ID", "<logo-akuma>")  # importante: con <>
        img.add_header("Content-Disposition", "inline", filename="logo.png")
        msg.attach(img)

    msg.send(fail_silently=False)


def enviar_correo_recordatorio(to_email: str, ctx: dict):
    """
    Envía un recordatorio 24h antes.
    Plantilla: main/email/reserva_recordatorio.html
    """
    subject = "Recordatorio: tu cita es mañana"
    html = render_to_string("main/email/reserva_recordatorio.html", ctx)
    txt = (
        f"Hola {ctx.get('nombre_cliente','')}, te recordamos tu cita.\n"
        f"Fecha: {ctx.get('fecha','')} {ctx.get('hora','')}\n"
        f"Servicio: {ctx.get('servicio','')} con {ctx.get('profesional','')}\n"
        f"Ubicación: {ctx.get('direccion_clinica','')}\n"
        f"Ver detalles: {ctx.get('enlace','')}\n"
    )

    msg = EmailMultiAlternatives(
        subject=subject,
        body=txt,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[to_email],
    )
    msg.attach_alternative(html, "text/html")

    # Reutilizamos el logo inline si existe
    candidates = [
        Path(settings.BASE_DIR) / "main" / "static" / "images" / "logo.png",
        Path(settings.BASE_DIR) / "static" / "images" / "logo.png",
    ]
    logo_path = next((p for p in candidates if p.exists()), None)

    if logo_path and logo_path.exists():
        with open(logo_path, "rb") as f:
            img = MIMEImage(f.read())
        img.add_header("Content-ID", "<logo-akuma>")
        img.add_header("Content-Disposition", "inline", filename="logo.png")
        msg.attach(img)

    msg.send(fail_silently=False)
