"""Identificación de cartas a partir de una foto.

Proveedores: Gemini, Claude, OpenAI y Ollama (local). Todos comparten PROMPT y parse_ident(),
así que devuelven el mismo dict (is_pokemon_card, name, number, total, set_name, ...).
Para añadir otro: escribe identify_xxx(img) y regístralo en RUNNERS.
El proveedor y las claves se eligen desde Ajustes (ver services/settings.py).
"""
import base64
import json
import os
import re
import socket
import urllib.error
import urllib.request

from services import settings

GEMINI_BASE = os.environ.get("CC_GEMINI_BASE", "https://generativelanguage.googleapis.com/v1beta")
ANTHROPIC_URL = os.environ.get("CC_ANTHROPIC_URL", "https://api.anthropic.com/v1/messages")

PROMPT = (
    "Analiza esta imagen de una carta coleccionable de Pokemon. Devuelve EXCLUSIVAMENTE un objeto JSON valido "
    "(sin markdown, sin comillas de bloque ```json) con los siguientes campos exactos: "
    '{"is_pokemon_card": true/false, "name": "...", "number": "...", "total": "...", "set_name": "...", '
    '"set_code": "...", "language": "...", "rarity": "...", "confidence": 0.0}. '
    "name es el nombre oficial de la carta tal y como aparece impreso en ella. number es el numero de coleccion "
    "sin el total; total es el numero tras la barra o null. confidence va de 0 a 1. "
    "Si no es una carta Pokemon, pon is_pokemon_card en false."
)


class ApiError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg


def _http_json(url, payload, headers=None, timeout=30, service="el servicio externo"):
    """POST con JSON; si payload es None, hace un GET."""
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    h = {"Content-Type": "application/json", "User-Agent": "CardCollector/1.0"}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h, method="POST" if data is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read().decode("utf-8", "replace")[:300]
        except Exception:
            pass
        raise ApiError(502, "%s respondió %s. %s" % (service, e.code, body))
    except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as e:
        raise ApiError(
            502,
            "No se pudo conectar con %s (%s). Suele ser algo temporal: vuelve a intentarlo en unos segundos."
            % (service, getattr(e, "reason", e)),
        )


def parse_ident(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        raise ApiError(502, "No se entendió la respuesta de la IA.")
    try:
        return json.loads(m.group(0))
    except ValueError:
        raise ApiError(502, "No se entendió la respuesta de la IA.")


def _mime(img):
    if img.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if img.startswith(b"RIFF") and b"WEBP" in img[:16]:
        return "image/webp"
    return "image/jpeg"


def _b64(img):
    return base64.b64encode(img).decode("ascii")


# ---------------------------------------------------------------- Gemini
_BAD_MODELS = set()  # modelos que Google ya no ofrece (404): no se reintentan hasta reiniciar el servidor
_GOOD = {}           # último modelo de Gemini que funcionó


def _gemini_discover(key):
    """Pregunta a Google qué modelos Flash tiene disponibles esta clave (los nombres cambian a menudo).
    Devuelve primero la versión más nueva y, dentro de cada versión, la variante lite (más barata)."""
    try:
        r = _http_json(GEMINI_BASE + "/models?pageSize=200", None, {"x-goog-api-key": key},
                       timeout=15, service="Gemini (lista de modelos)")
    except ApiError:
        return []
    found = []
    for m in r.get("models", []):
        name = (m.get("name") or "").replace("models/", "")
        mm = re.fullmatch(r"gemini-(\d+(?:\.\d+)?)-flash(-lite)?", name)
        if mm and "generateContent" in (m.get("supportedGenerationMethods") or []):
            found.append((-float(mm.group(1)), 0 if mm.group(2) else 1, name))
    return [n for _, _, n in sorted(found)]


def identify_gemini(img):
    key = settings.api_key("gemini")
    body = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": _mime(img), "data": _b64(img)}},
            {"text": PROMPT},
        ]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    tried, errors = [], []

    def run(models):
        for m in models:
            if not m or m in tried or m in _BAD_MODELS:
                continue
            tried.append(m)
            url = "%s/models/%s:generateContent" % (GEMINI_BASE, m)
            try:
                r = _http_json(url, body, {"x-goog-api-key": key}, timeout=35, service="Gemini (%s)" % m)
                parts = r["candidates"][0]["content"]["parts"]
                result = parse_ident("".join(p.get("text", "") for p in parts))
                _GOOD["gemini"] = m
                return result
            except ApiError as e:
                errors.append(e)
                if "404" in e.msg:  # el modelo ya no existe
                    _BAD_MODELS.add(m)
                # 404, cuota (429), caída temporal o timeout: se prueba con el siguiente modelo
                if any(s in e.msg for s in ("404", "429", "502", "503", "timed out", "temporal")):
                    continue
                raise  # clave inválida, imagen rechazada...: otro modelo no lo arreglaría
            except (KeyError, IndexError, TypeError):
                errors.append(ApiError(502, "Gemini no devolvió respuesta. Prueba con otra foto."))
        return None

    # 1) el modelo elegido en Ajustes, 2) el último que funcionó, 3) alias que Google mantiene al día
    result = run([settings.get()["models"]["gemini"], _GOOD.get("gemini"),
                  "gemini-flash-lite-latest", "gemini-flash-latest"])
    if result is None:  # 4) si todo da 404, se consulta qué modelos tiene disponibles esta clave
        result = run(_gemini_discover(key))
    if result is not None:
        return result

    real = [e for e in errors if "404" not in e.msg]  # un 429 o un fallo real es más útil que un 404
    if real:
        raise real[0]
    raise ApiError(
        502,
        "Ningún modelo de Gemini está disponible con tu clave (probados: %s). Google retira modelos con "
        "frecuencia: escribe uno vigente en Ajustes → Gemini → Modelo. Lista: "
        "https://ai.google.dev/gemini-api/docs/models" % ", ".join(tried),
    )


# ---------------------------------------------------------------- Claude
def identify_anthropic(img):
    body = {
        "model": settings.get()["models"]["anthropic"],
        "max_tokens": 500,
        "messages": [{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": _mime(img), "data": _b64(img)}},
            {"type": "text", "text": PROMPT},
        ]}],
    }
    r = _http_json(
        ANTHROPIC_URL, body,
        {"x-api-key": settings.api_key("anthropic"), "anthropic-version": "2023-06-01"},
        timeout=90, service="Claude (leer la carta)",
    )
    return parse_ident("".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text"))


# ---------------------------------------------------------------- OpenAI
def identify_openai(img):
    body = {
        "model": settings.get()["models"]["openai"],
        "max_tokens": 500,
        "response_format": {"type": "json_object"},
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": PROMPT},
            {"type": "image_url", "image_url": {"url": "data:%s;base64,%s" % (_mime(img), _b64(img))}},
        ]}],
    }
    r = _http_json(
        "https://api.openai.com/v1/chat/completions", body,
        {"Authorization": "Bearer " + settings.api_key("openai")},
        timeout=60, service="OpenAI (leer la carta)",
    )
    try:
        return parse_ident(r["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError):
        raise ApiError(502, "OpenAI no devolvió respuesta. Prueba con otra foto.")


# ---------------------------------------------------------------- Ollama (local)
def identify_ollama(img):
    s = settings.get()
    body = {
        "model": s["models"]["ollama"],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
        "messages": [{"role": "user", "content": PROMPT, "images": [_b64(img)]}],
    }
    try:
        r = _http_json(s["ollama_url"] + "/api/chat", body, timeout=180, service="Ollama")
    except ApiError as e:
        raise ApiError(
            e.code,
            e.msg + " Comprueba que Ollama esté en marcha y que hayas hecho «ollama pull %s»." % s["models"]["ollama"],
        )
    try:
        return parse_ident(r["message"]["content"])
    except (KeyError, TypeError):
        raise ApiError(502, "Ollama no devolvió respuesta. Prueba con otra foto o con otro modelo.")


RUNNERS = {
    "gemini": identify_gemini,
    "anthropic": identify_anthropic,
    "openai": identify_openai,
    "ollama": identify_ollama,
}


def has_ai_key():
    """¿Está la IA lista para usarse con la configuración actual?"""
    prov = settings.get()["provider"]
    if prov == "ollama":
        return True
    if prov == "auto":
        return any(settings.api_key(p) for p in settings.KEYED)
    return bool(settings.api_key(prov))


def identify(img):
    prov = settings.get()["provider"]

    if prov == "auto":  # el primero con clave (Gemini > Claude > OpenAI); si falla, prueba el siguiente
        order = [p for p in settings.KEYED if settings.api_key(p)]
        if not order:
            raise ApiError(
                503,
                "No hay ningún proveedor de IA configurado. Añade una API key (o usa Ollama) en Ajustes.",
            )
        last = None
        for p in order:
            try:
                return RUNNERS[p](img)
            except ApiError as e:
                last = e
        raise last

    if prov in settings.KEYED and not settings.api_key(prov):
        raise ApiError(503, "Falta la API key de %s. Añádela en Ajustes." % settings.LABELS[prov])
    return RUNNERS[prov](img)