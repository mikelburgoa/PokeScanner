"""Rutas y configuración global del servidor.

Los DATOS DEL USUARIO (colección, Excel, ajustes con las API keys, copias de seguridad y, si lo usas,
el .env) viven FUERA de la carpeta del proyecto, en una carpeta personal. Así nunca acaban en un zip,
en git o en una carpeta compartida por accidente:

    Windows : %APPDATA%\\PokeScanner
    macOS   : ~/Library/Application Support/PokeScanner
    Linux   : ~/.local/share/pokescanner

Se puede cambiar con la variable de entorno POKESCANNER_DATA_DIR.
"""
import os
import shutil
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
except ImportError:  # python-dotenv viene con uvicorn[standard]; si faltara, se ignora el .env
    load_dotenv = None

APP_NAME = "PokeScanner"
SERVER_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = SERVER_DIR.parent
DIST_DIR = PROJECT_DIR / "dist"  # frontend compilado (npm run build)

HOST = "127.0.0.1"  # solo accesible desde tu equipo: no cambiar salvo que sepas lo que haces
PORT = int(os.environ.get("POKESCANNER_PORT", "8000"))


def _default_data_dir() -> Path:
    override = os.environ.get("POKESCANNER_DATA_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    if sys.platform.startswith("win"):
        return Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming") / APP_NAME
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / APP_NAME
    return Path(os.environ.get("XDG_DATA_HOME") or Path.home() / ".local" / "share") / "pokescanner"


DATA_DIR = _default_data_dir()
DATA_DIR.mkdir(parents=True, exist_ok=True)

DATA_FILE = DATA_DIR / "collection.json"
SETTINGS_FILE = DATA_DIR / "settings.json"
EXCEL_DIR = DATA_DIR / "excel"
EXCEL_DIR.mkdir(exist_ok=True)
EXCEL_FILE = EXCEL_DIR / "coleccion_pokemon.xlsx"
BACKUP_DIR = DATA_DIR / "backups"

MAX_IMAGE_BYTES = 15 * 1024 * 1024  # tamaño máximo de la foto a analizar

GEMINI_BASE = os.environ.get("CC_GEMINI_BASE", "https://generativelanguage.googleapis.com/v1beta")
ANTHROPIC_URL = os.environ.get("CC_ANTHROPIC_URL", "https://api.anthropic.com/v1/messages")


def load_env() -> None:
    """Carga variables desde un .env (opcional). Gana el primero que exista; no pisa el entorno real."""
    if not load_dotenv:
        return
    for p in (DATA_DIR / ".env", PROJECT_DIR / ".env", SERVER_DIR / ".env"):
        if p.exists():
            load_dotenv(p)


def migrate_legacy_data() -> list:
    """Copia los datos de versiones anteriores (server/data y server/excel) a la carpeta personal.

    Solo copia lo que todavía no existe en el destino y NO borra los originales: bórralos tú
    cuando hayas comprobado que todo está en su sitio. Devuelve los nombres copiados.
    """
    # La migración se hace UNA sola vez. Sin esta marca, al borrar el Excel (o vaciar la colección) desde la app,
    # el siguiente arranque volvería a copiar los datos antiguos de server/data y server/excel.
    marker = DATA_DIR / ".migrado"
    if marker.exists():
        return []
    moves = [
        (SERVER_DIR / "data" / "collection.json", DATA_FILE),
        (SERVER_DIR / "data" / "settings.json", SETTINGS_FILE),
        (SERVER_DIR / "excel" / "coleccion_pokemon.xlsx", EXCEL_FILE),
    ]
    copied = []
    for old, new in moves:
        if old.is_file() and not new.exists():
            try:
                shutil.copy2(old, new)
                copied.append(old.name)
            except OSError:
                pass
    try:
        marker.write_text("Datos de versiones anteriores ya migrados. Borra este archivo para volver a migrar.", encoding="utf8")
    except OSError:
        pass
    return copied


load_env()