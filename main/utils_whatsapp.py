import re
import requests
from django.conf import settings


def _normalizar_numero(to_number: str) -> str:
    """
    Devuelve número solo dígitos en formato 56XXXXXXXXX.
    Acepta entrada con +56, espacios o guiones.
    """
    if not to_number:
        return ""
    digits = re.sub(r"\\D", "", to_number)
    # ya normalizado
    if digits.startswith("569") and len(digits) == 11:
        return digits
    if digits.startswith("56"):
        digits = digits[2:]
    if digits.startswith("9") and len(digits) == 9:
        return "569" + digits[1:]
    return ""


def enviar_whatsapp_recordatorio(to_number: str, body: str):
    """
    Envía un mensaje de texto simple usando WhatsApp Cloud API.
    Requiere en settings:
      WHATSAPP_TOKEN  (token de acceso)
      WHATSAPP_PHONE_ID (phone number ID)
    """
    token = getattr(settings, "WHATSAPP_TOKEN", "")
    phone_id = getattr(settings, "WHATSAPP_PHONE_ID", "")
    normalized = _normalizar_numero(to_number)

    if not normalized or not token or not phone_id:
        return False, "Faltan número o credenciales de WhatsApp"

    url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": normalized,
        "type": "text",
        "text": {"preview_url": False, "body": body},
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        if res.ok:
            return True, None
        return False, f"{res.status_code}: {res.text}"
    except Exception as exc:  # network/timeout
        return False, str(exc)
