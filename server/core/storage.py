"""Lectura y escritura de la colección (collection.json) con copias de seguridad."""
import json
import os
import shutil
import threading
from datetime import datetime
from pathlib import Path

from core import config

LOCK = threading.RLock()  # reentrante: el exportador y los endpoints se llaman entre sí
KEEP_BACKUPS = 10


def read_collection() -> list:
    with LOCK:
        try:
            d = json.loads(config.DATA_FILE.read_text(encoding="utf-8"))
            return d if isinstance(d, list) else []
        except (OSError, ValueError):
            return []


def write_collection(items: list) -> None:
    """Escritura atómica: se escribe un archivo temporal y se reemplaza, así nunca queda a medias."""
    tmp = config.DATA_FILE.with_suffix(".tmp")
    with LOCK:
        tmp.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(str(tmp), str(config.DATA_FILE))


def snapshot(label: str = "manual"):
    """Guarda una copia fechada de la colección actual antes de una operación destructiva.

    Conserva las últimas KEEP_BACKUPS. Devuelve la ruta de la copia, o None si no había nada que guardar.
    """
    with LOCK:
        if not config.DATA_FILE.is_file() or not read_collection():
            return None
        config.BACKUP_DIR.mkdir(exist_ok=True)
        dest = config.BACKUP_DIR / ("collection-%s-%s.json" % (datetime.now().strftime("%Y%m%d-%H%M%S"), label))
        shutil.copy2(config.DATA_FILE, dest)
        for old in sorted(config.BACKUP_DIR.glob("collection-*.json"))[:-KEEP_BACKUPS]:
            try:
                old.unlink()
            except OSError:
                pass
        return dest


def list_backups() -> list:
    """Copias de seguridad de la colección, de la más reciente a la más antigua."""
    if not config.BACKUP_DIR.is_dir():
        return []
    out = []
    for f in sorted(config.BACKUP_DIR.glob("collection-*.json"), reverse=True):
        try:
            cards = json.loads(f.read_text(encoding="utf-8"))
            n = len(cards) if isinstance(cards, list) else 0
        except (OSError, ValueError):
            n = 0
        out.append({"name": f.name, "cards": n, "date": datetime.fromtimestamp(f.stat().st_mtime).isoformat(timespec="seconds")})
    return out


def restore_latest_backup():
    """Recupera la copia más reciente. Antes guarda el estado actual por si te arrepientes. Devuelve su info o None."""
    with LOCK:
        backups = list_backups()
        if not backups:
            return None
        latest = backups[0]
        items = json.loads((config.BACKUP_DIR / latest["name"]).read_text(encoding="utf-8"))
        snapshot("antes-de-restaurar")
        write_collection(items if isinstance(items, list) else [])
        return latest
