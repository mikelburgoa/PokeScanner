"""Proveedor: Claude (API de Anthropic, de pago; distinta de la suscripción a Claude.ai)."""
from core import config, user_settings as settings

from . import base


def identify(img):
    body = {
        "model": settings.get()["models"]["anthropic"],
        "max_tokens": 500,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": base.mime(img), "data": base.b64(img)}},
            {"type": "text", "text": base.PROMPT},
        ]}],
    }
    r = base.http_json(
        config.ANTHROPIC_URL, body,
        {"x-api-key": settings.api_key("anthropic"), "anthropic-version": "2023-06-01"},
        timeout=90, service="Claude (leer la carta)",
    )
    return base.parse_ident("".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text"))
