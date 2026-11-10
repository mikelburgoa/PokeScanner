"""Proveedor: OpenAI (API de pago; distinta de ChatGPT Plus)."""
from core import user_settings as settings
from core.errors import ApiError

from . import base


def identify(img):
    body = {
        "model": settings.get()["models"]["openai"],
        "max_tokens": 500,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": base.PROMPT},
            {"type": "image_url", "image_url": {"url": "data:%s;base64,%s" % (base.mime(img), base.b64(img))}},
        ]}],
    }
    r = base.http_json(
        "https://api.openai.com/v1/chat/completions", body,
        {"Authorization": "Bearer " + settings.api_key("openai")},
        timeout=60, service="OpenAI (leer la carta)",
    )
    try:
        return base.parse_ident(r["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError):
        raise ApiError(502, "OpenAI no devolvió respuesta. Prueba con otra foto.")
