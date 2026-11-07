import os
import json
import base64
import re
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env en la raíz del proyecto
HERE = Path(__file__).resolve().parent.parent.parent
env_path = HERE / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)
else:
    load_dotenv()

GEMINI_BASE = os.environ.get("CC_GEMINI_BASE", "https://generativelanguage.googleapis.com/v1beta")
GEMINI_MODEL = os.environ.get("CC_GEMINI_MODEL", "gemini-2.0-flash")
MODEL = os.environ.get("CC_MODEL", "claude-sonnet-5-5")

PROMPT = (
    "Analiza esta imagen de una carta coleccionable de Pokemon. "
    "Devuelve EXCLUSIVAMENTE un objeto JSON valido (sin markdown, sin comillas de bloque ```json) con los siguientes campos exactos: "
    '{"is_pokemon_card": true/false, "name": "...", "number": "...", "total": "...", '
    '"set_name": "...", "set_code": "...", "language": "...", "rarity": "...", "confidence": 0.0}. '
    "name es el nombre oficial de la carta tal y como aparece impreso en ella. "
    "number es el numero de coleccion sin el total; total es el numero tras la barra o null. "
    "confidence va de 0 a 1. Si no es una carta Pokemon, pon is_pokemon_card en false."
)

class ApiError(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg

def gemini_key():
    key = (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    return key

def parse_ident(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        raise ApiError(502, "No se entendió la respuesta de la IA.")
    try:
        return json.loads(m.group(0))
    except ValueError:
        raise ApiError(502, "No se entendió la respuesta de la IA.")

def identify_gemini(img, key):
    import urllib.request
    models = [GEMINI_MODEL, "gemini-2.0-flash", "gemini-1.5-flash"]
    seen = set()
    models = [m for m in models if not (m in seen or seen.add(m))]

    mime = "image/jpeg"
    if img.startswith(b"\x89PNG\r\n\x1a\n"):
        mime = "image/png"
    elif img.startswith(b"RIFF") and b"WEBP" in img[:16]:
        mime = "image/webp"

    body = {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": mime, "data": base64.b64encode(img).decode("ascii")}},
            {"text": PROMPT},
        ]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0},
    }
    last_exc = None
    for m in models:
        url = "%s/models/%s:generateContent" % (GEMINI_BASE, m)
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(body).encode("utf-8"),
                headers={"Content-Type": "application/json", "x-goog-api-key": key, "User-Agent": "CardCollector/1.0"}
            )
            with urllib.request.urlopen(req, timeout=35) as resp:
                r = json.loads(resp.read().decode("utf-8"))
                parts = r["candidates"][0]["content"]["parts"]
                return parse_ident("".join(p.get("text", "") for p in parts))
        except Exception as e:
            last_exc = e
            continue

    if last_exc:
        if isinstance(last_exc, ApiError):
            raise last_exc
        raise ApiError(502, "No se pudo conectar con Gemini: %s" % last_exc)
    raise ApiError(502, "Gemini no devolvió respuesta.")

def identify(img):
    gkey = gemini_key()
    akey = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not gkey and not akey:
        raise ApiError(503, "Falta la API key (GEMINI_API_KEY o ANTHROPIC_API_KEY) en el archivo .env. Puedes buscar la carta a mano.")
    if gkey:
        try:
            return identify_gemini(img, gkey)
        except ApiError:
            if not akey:
                raise
    raise ApiError(503, "Anthropic no configurada en este entorno.")