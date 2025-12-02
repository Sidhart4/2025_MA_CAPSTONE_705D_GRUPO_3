import logging
from typing import Any, Dict, Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TransbankError(Exception):
    """Errores al comunicarse con Transbank."""


class TransbankClient:
    """
    Cliente liviano para Webpay Plus REST (v1.2).
    Usa las credenciales configuradas en settings.
    """

    BASE_PATH = "/rswebpaytransaction/api/webpay/v1.2"

    def __init__(self):
        env = getattr(settings, "TRANSBANK_ENV", "integration").lower()

        # URL oficial de integración (sandbox)
        default_base = (
            "https://webpay3gint.transbank.cl"
            if env != "production"
            else "https://webpay3g.transbank.cl"
        )

        custom_base = getattr(settings, "TRANSBANK_BASE_URL", "").strip()
        self.base_url = (custom_base or default_base).rstrip("/")

        # Credenciales desde settings
        self.api_key_id = str(getattr(settings, "TRANSBANK_API_KEY_ID", ""))
        self.api_key_secret = str(getattr(settings, "TRANSBANK_API_KEY_SECRET", ""))
        self.timeout = getattr(settings, "TRANSBANK_TIMEOUT", 15)

        # 🔥 DEBUG
        print("\n===== DEBUG TRANSBANK CLIENT =====")
        print("ENV:", env)
        print("BASE_URL:", self.base_url)
        print("API_KEY_ID:", self.api_key_id)
        print("API_KEY_SECRET:", self.api_key_secret)
        print("=================================\n")

        if not self.api_key_id or not self.api_key_secret:
            raise TransbankError("Faltan credenciales de Transbank en settings.")

    def _headers(self) -> Dict[str, str]:
        """
        Headers correctos para Webpay Plus REST (integration)
        """

        headers = {
            "Tbk-Api-Key-Id": self.api_key_id,          # commerce code
            "Tbk-Api-Key-Secret": self.api_key_secret,  # api key
            "Content-Type": "application/json",
        }

        print("\n===== DEBUG HEADERS =====")
        for k, v in headers.items():
            print(f"{k}: {v}")
        print("==========================\n")

        return headers

    def _request(
        self,
        method: str,
        path: str,
        json_payload: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{self.BASE_PATH}{path}"

        print("\n===== DEBUG REQUEST =====")
        print("METHOD:", method)
        print("URL:", url)
        print("PAYLOAD:", json_payload)
        print("==========================\n")

        try:
            resp = requests.request(
                method=method,
                url=url,
                headers=self._headers(),
                json=json_payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            logger.exception("Error de red con Transbank: %s", exc)
            raise TransbankError("No fue posible contactar a Transbank.") from exc

        print("\n===== DEBUG RESPONSE =====")
        print("HTTP STATUS:", resp.status_code)
        print("BODY:", resp.text)
        print("===========================\n")

        if resp.status_code >= 400:
            if resp.status_code == 401:
                raise TransbankError("Credenciales rechazadas por Transbank (401).")
            raise TransbankError(
                f"Transbank devolvió un error ({resp.status_code})."
            )

        try:
            return resp.json()
        except ValueError:
            logger.error("Respuesta no válida de Transbank (no es JSON): %s", resp.text)
            raise TransbankError("Respuesta inválida desde Transbank.")

    def create_transaction(
        self,
        *,
        amount: int,
        buy_order: str,
        session_id: str,
        return_url: str,
    ) -> Dict[str, Any]:

        print("\n===== CREANDO TRANSACCIÓN =====")
        print("MONTO:", amount)
        print("BUY_ORDER:", buy_order)
        print("SESSION_ID:", session_id)
        print("RETURN_URL:", return_url)
        print("================================\n")

        payload = {
            "buy_order": buy_order[:26],
            "session_id": session_id[:60],
            "amount": amount,
            "return_url": return_url,
        }

        return self._request("POST", "/transactions", payload)

    def commit_transaction(self, token: str) -> Dict[str, Any]:
        return self._request("PUT", f"/transactions/{token}")

    def get_status(self, token: str) -> Dict[str, Any]:
        return self._request("GET", f"/transactions/{token}")
