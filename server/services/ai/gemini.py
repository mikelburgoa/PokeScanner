"""Proveedor: Google Gemini (gratis con límites). Se autorrepara cuando Google retira un modelo."""
import re

from core import config, user_settings as settings
from core.errors import ApiError

from . import base

_BAD_MODELS = set()  # modelos que Google ya no ofrece (404): no se reintentan hasta reiniciar el servidor
_GOOD = {}           # último modelo de Gemini que funcionó


def discover(key):
    """Pregunta a Google qué modelos Flash tiene disponibles esta clave (los nombres cambian a menudo).
    Devuelve primero la versión más nueva y, dentro de cada versión, la variante lite (más barata)."""
    try:
        r = base.http_json(config.GEMINI_BASE + "/models?pageSize=200", None, {"x-goog-api-key": key},
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


def identify(img):
    key = settings.api_key("gemini")
    body = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": base.mime(img), "data": base.b64(img)}},
            {"text": base.PROMPT},
        ]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    tried, errors = [], []

    def run(models):
        for m in models:
            if not m or m in tried or m in _BAD_MODELS:
                continue
            tried.append(m)
            url = "%s/models/%s:generateContent" % (config.GEMINI_BASE, m)
            try:
                r = base.http_json(url, body, {"x-goog-api-key": key}, timeout=35, service="Gemini (%s)" % m)
                parts = r["candidates"][0]["content"]["parts"]
                result = base.parse_ident("".join(p.get("text", "") for p in parts))
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
        result = run(discover(key))
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
