"""«Probar conexión»: comprueba la clave y el modelo SIN gastar tokens (solo consulta la lista/ficha del modelo)."""
import re
from urllib.parse import quote

from core import config, user_settings as settings
from core.errors import ApiError

from . import base, gemini


def _status(e: ApiError):
    m = re.search(r"respondió (\d{3})", e.msg or "")
    return int(m.group(1)) if m else None


def _fail(e: ApiError, what: str) -> dict:
    code = _status(e)
    if code in (400, 401, 403):
        return {"ok": False, "message": "La clave no es válida o no tiene permiso para usar %s." % what}
    if code == 429:
        return {"ok": False, "message": "Clave aceptada, pero has superado el límite de uso ahora mismo. Reintenta en un rato."}
    return {"ok": False, "message": e.msg}


def _gemini(key, model):
    try:
        base.http_json("%s/models/%s" % (config.GEMINI_BASE, quote(model, safe="-._")), None,
                       {"x-goog-api-key": key}, timeout=15, service="Gemini")
    except ApiError as e:
        if _status(e) == 404:
            ok = gemini.discover(key)
            if not ok:
                return {"ok": False, "message": "No se pudo consultar a Google con esta clave. Comprueba que sea correcta."}
            return {"ok": False, "message": "El modelo «%s» ya no existe. Prueba con: %s." % (model, ", ".join(ok[:3]))}
        return _fail(e, "Gemini")
    return {"ok": True, "message": "Clave válida y modelo «%s» disponible." % model}


def _anthropic(key, model):
    url = config.ANTHROPIC_URL.rsplit("/messages", 1)[0] + "/models/" + quote(model, safe="-._")
    try:
        base.http_json(url, None, {"x-api-key": key, "anthropic-version": "2023-06-01"}, timeout=15, service="Claude")
    except ApiError as e:
        if _status(e) == 404:
            return {"ok": False, "message": "Clave válida, pero el modelo «%s» no existe en tu cuenta." % model}
        return _fail(e, "Claude")
    return {"ok": True, "message": "Clave válida y modelo «%s» disponible." % model}


def _openai(key, model):
    try:
        base.http_json("https://api.openai.com/v1/models/" + quote(model, safe="-._:"), None,
                       {"Authorization": "Bearer " + key}, timeout=15, service="OpenAI")
    except ApiError as e:
        if _status(e) == 404:
            return {"ok": False, "message": "Clave válida, pero el modelo «%s» no existe o no tienes acceso." % model}
        return _fail(e, "OpenAI")
    return {"ok": True, "message": "Clave válida y modelo «%s» disponible." % model}


def _ollama(url, model):
    try:
        r = base.http_json(url + "/api/tags", None, timeout=8, service="Ollama")
    except ApiError:
        return {"ok": False, "message": "No se conecta con Ollama en %s. ¿Está en marcha?" % url}
    names = [m.get("name", "") for m in r.get("models", [])]
    if not any(n == model or n.split(":")[0] == model.split(":")[0] for n in names):
        have = ", ".join(names[:4]) or "ninguno"
        return {"ok": False, "message": "Ollama responde, pero no tiene «%s». Instálalo con «ollama pull %s». Tienes: %s." % (model, model, have)}
    return {"ok": True, "message": "Ollama responde y tiene el modelo «%s»." % model}


def run(provider: str, key: str = "", model: str = "", ollama_url: str = "") -> dict:
    """Usa lo que se haya escrito en pantalla (aunque no esté guardado) y, si falta, lo guardado."""
    s = settings.get()
    model = model or s["models"][provider]
    if provider == "ollama":
        url = (ollama_url or s["ollama_url"]).rstrip("/")
        settings._check_ollama_url(url)  # misma regla que al guardar: solo en este equipo
        return _ollama(url, model)
    key = key or settings.api_key(provider)
    if not key:
        return {"ok": False, "message": "Escribe o guarda primero una API key."}
    return {"gemini": _gemini, "anthropic": _anthropic, "openai": _openai}[provider](key, model)
