"""Ajustes de IA del usuario (proveedor, claves y modelos) en server/data/settings.json.

Pensado para uso local: el archivo queda ignorado por git (server/data/*.json) y el servidor
nunca devuelve una clave al navegador, solo si existe o no. El .env sigue funcionando
como alternativa: si no hay clave guardada en Ajustes, se usa la de las variables de entorno.
"""
import json
import os
import threading
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # uvicorn[standard] ya lo instala; si faltara, simplemente se ignora el .env
    load_dotenv = None

SERVER_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = SERVER_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
SETTINGS_FILE = DATA_DIR / "settings.json"

if load_dotenv:
    for _p in (SERVER_DIR.parent / ".env", SERVER_DIR / ".env"):
        if _p.exists():
            load_dotenv(_p)

KEYED = ("gemini", "anthropic", "openai")  # proveedores que necesitan API key
PROVIDERS = KEYED + ("ollama",)
LABELS = {"gemini": "Google Gemini", "anthropic": "Claude (Anthropic)", "openai": "OpenAI", "ollama": "Ollama (local)"}
DEFAULT_MODELS = {
    "gemini": os.environ.get("CC_GEMINI_MODEL", "gemini-flash-lite-latest"),
    "anthropic": os.environ.get("CC_MODEL", "claude-sonnet-5-5"),
    "openai": "gpt-4o-mini",
    "ollama": "qwen2.5vl",
}
DEFAULT_OLLAMA_URL = "http://localhost:11434"

_LOCK = threading.RLock()


def _env_key(provider: str) -> str:
    if provider == "gemini":
        return (os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY") or "").strip()
    if provider == "anthropic":
        return os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if provider == "openai":
        return os.environ.get("OPENAI_API_KEY", "").strip()
    return ""


def _read() -> dict:
    try:
        d = json.loads(SETTINGS_FILE.read_text(encoding="utf-8"))
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def get() -> dict:
    d = _read()
    models = dict(DEFAULT_MODELS)
    models.update({k: v for k, v in (d.get("models") or {}).items() if k in PROVIDERS and v})
    return {
        "provider": d.get("provider") if d.get("provider") in PROVIDERS + ("auto",) else "auto",
        "keys": {k: v for k, v in (d.get("keys") or {}).items() if k in KEYED and v},
        "models": models,
        "ollama_url": d.get("ollama_url") or DEFAULT_OLLAMA_URL,
    }


def api_key(provider: str) -> str:
    """Clave guardada en Ajustes o, si no hay, la del .env / variable de entorno."""
    return get()["keys"].get(provider, "") or _env_key(provider)


def public() -> dict:
    """Vista segura para el frontend: nunca incluye las claves."""
    s = get()
    return {
        "provider": s["provider"],
        "ollamaUrl": s["ollama_url"],
        "providers": {
            p: {
                "label": LABELS[p],
                "needsKey": p in KEYED,
                "hasKey": bool(api_key(p)) if p in KEYED else True,
                "model": s["models"][p],
            }
            for p in PROVIDERS
        },
    }


def update(patch: dict) -> None:
    """Aplica cambios parciales. Lanza ValueError con un mensaje legible si algo no es válido."""
    with _LOCK:
        d = _read()
        d.setdefault("keys", {})
        d.setdefault("models", {})

        prov = patch.get("provider")
        if prov is not None:
            if prov not in PROVIDERS + ("auto",):
                raise ValueError("Proveedor no válido.")
            d["provider"] = prov

        for name, val in (patch.get("keys") or {}).items():
            if name not in KEYED:
                raise ValueError("Proveedor no válido: %s." % name)
            if val is None:  # null = borrar la clave guardada
                d["keys"].pop(name, None)
                continue
            val = val.strip()
            if not val:  # vacío = no cambiar
                continue
            if len(val) > 300 or any(c.isspace() for c in val):
                raise ValueError("La API key de %s no parece válida." % LABELS[name])
            d["keys"][name] = val

        for name, val in (patch.get("models") or {}).items():
            if name in PROVIDERS and isinstance(val, str) and val.strip():
                d["models"][name] = val.strip()[:100]

        url = patch.get("ollamaUrl")
        if url is not None:
            url = url.strip().rstrip("/")
            if url and not url.startswith(("http://", "https://")):
                raise ValueError("La URL de Ollama debe empezar por http:// o https://")
            d["ollama_url"] = url or DEFAULT_OLLAMA_URL

        tmp = SETTINGS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        try:
            os.chmod(tmp, 0o600)  # solo el usuario (en Windows se ignora)
        except OSError:
            pass
        os.replace(str(tmp), str(SETTINGS_FILE))