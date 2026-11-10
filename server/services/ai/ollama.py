"""Proveedor: Ollama (modelo local con visión; sin clave y sin coste)."""
from core import user_settings as settings
from core.errors import ApiError

from . import base


def identify(img):
    s = settings.get()
    body = {
        "model": s["models"]["ollama"],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
        "messages": [{"role": "user", "content": base.PROMPT, "images": [base.b64(img)]}],
    }
    try:
        r = base.http_json(s["ollama_url"] + "/api/chat", body, timeout=180, service="Ollama")
    except ApiError as e:
        raise ApiError(
            e.code,
            e.msg + " Comprueba que Ollama esté en marcha y que hayas hecho «ollama pull %s»." % s["models"]["ollama"],
        )
    try:
        return base.parse_ident(r["message"]["content"])
    except (KeyError, TypeError):
        raise ApiError(502, "Ollama no devolvió respuesta. Prueba con otra foto o con otro modelo.")
