"""Piezas comunes de todos los proveedores de IA: el prompt, el cliente HTTP y el parseo de la respuesta."""
import base64
import json
import re
import socket
import urllib.error
import urllib.request

from core.errors import ApiError

PROMPT = (
    "Analiza esta imagen de una carta coleccionable de Pokemon. Devuelve EXCLUSIVAMENTE un objeto JSON valido "
    "(sin markdown, sin comillas de bloque ```json) con los siguientes campos exactos: "
    '{"is_pokemon_card": true/false, "name": "...", "number": "...", "total": "...", "set_name": "...", '
    '"set_code": "...", "language": "...", "rarity": "...", "confidence": 0.0}. '
    "name es el nombre oficial de la carta tal y como aparece impreso en ella. number es el numero de coleccion "
    "sin el total; total es el numero tras la barra o null. confidence va de 0 a 1. "
    "Si no es una carta Pokemon, pon is_pokemon_card en false."
)


def http_json(url, payload, headers=None, timeout=30, service="el servicio externo"):
    """POST con JSON; si payload es None, hace un GET. Devuelve el JSON de la respuesta o lanza ApiError."""
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


def mime(img):
    if img.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if img.startswith(b"RIFF") and b"WEBP" in img[:16]:
        return "image/webp"
    return "image/jpeg"


def b64(img):
    return base64.b64encode(img).decode("ascii")
