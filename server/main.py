"""PokeScanner API (FastAPI).

Arranque (desde la carpeta server/):
    python main.py
"""
import base64
import json
import os
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from services import settings
from services.ai_scanner import ApiError as AiApiError, has_ai_key, identify
from services.excel_exporter import ApiError as ExcelApiError, export_excel_file
from services.tcgdex import ApiError as TcgApiError, refresh_cards, search_cards

app = FastAPI(title="PokeScanner API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001", "http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

HERE = Path(__file__).resolve().parent
DATA_DIR = HERE / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "collection.json"
EXCEL_DIR = HERE / "excel"
EXCEL_DIR.mkdir(exist_ok=True)
EXCEL_FILE = EXCEL_DIR / "coleccion_pokemon.xlsx"

LOCK = threading.RLock()


# ------------------------------------------------------------------ almacenamiento
def read_collection():
    with LOCK:
        try:
            d = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return d if isinstance(d, list) else []
        except (OSError, ValueError):
            return []


def write_collection(items):
    tmp = DATA_FILE.with_suffix(".tmp")
    with LOCK:
        tmp.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(str(tmp), str(DATA_FILE))


# ------------------------------------------------------------------ modelos
class IdentifyRequest(BaseModel):
    image: str  # imagen en base64 (con o sin prefijo data:image/...;base64,)


class SaveCardRequest(BaseModel):
    id: str = ""
    name: str
    number: str = ""
    rarity: str = "Común"
    set: str = "Sin Expansión"
    image: str = ""
    price_eur: float = 0.0
    price_usd: float = 0.0
    cardmarket_url: str = ""
    tcgplayer_url: str = ""
    condition: str = "NM"
    quantity: int = 1


class SettingsPatch(BaseModel):
    provider: Optional[str] = None
    keys: Optional[Dict[str, Optional[str]]] = None  # null = borrar clave, "" = no cambiar
    models: Optional[Dict[str, str]] = None
    ollamaUrl: Optional[str] = None


# ------------------------------------------------------------------ IA + búsqueda
@app.post("/api/identify")
def api_identify(req: IdentifyRequest):
    raw = req.image.split(",", 1)[1] if "," in req.image else req.image
    try:
        img_data = base64.b64decode(raw)
    except Exception:
        raise HTTPException(status_code=400, detail="La imagen no es válida.")
    if not img_data:
        raise HTTPException(status_code=400, detail="Petición vacía.")

    try:
        ident = identify(img_data)
        if not ident.get("is_pokemon_card") or not ident.get("name"):
            return {"success": False, "message": "No se detectó ninguna carta Pokémon válida en la imagen."}
        cands = search_cards(
            ident.get("name"), ident.get("number") or "", ident.get("total") or "", ident.get("set_name") or ""
        )
    except (AiApiError, TcgApiError) as e:
        raise HTTPException(status_code=e.code, detail=e.msg)

    if not cands:
        return {
            "success": False,
            "identification": ident,
            "message": "Se identificó la carta (%s), pero no se encontraron coincidencias en TCGdex." % ident.get("name"),
        }
    return {"success": True, "identification": ident, "candidates": cands}


@app.get("/api/search")
def api_search(name: str = "", number: str = "", total: str = "", set: str = ""):
    try:
        return {"success": True, "candidates": search_cards(name, number, total, set)}
    except TcgApiError as e:
        raise HTTPException(status_code=e.code, detail=e.msg)


# ------------------------------------------------------------------ colección
@app.get("/api/collection")
def api_get_collection():
    return read_collection()


@app.post("/api/collection")
def api_save_card(card: SaveCardRequest):
    cond = (card.condition or "NM").upper()
    qty = max(1, int(card.quantity or 1))
    card_dict = card.model_dump()
    card_dict["condition"] = cond
    card_dict["quantity"] = qty
    card_dict["uid"] = "%s_%s" % (card.id, cond)

    with LOCK:
        collection = read_collection()
        found = next((c for c in collection if c.get("uid") == card_dict["uid"]), None)
        if found:  # misma carta y mismo estado: se suman ejemplares
            found["quantity"] = int(found.get("quantity") or 1) + qty
        else:
            collection.append(card_dict)
        write_collection(collection)
    return {"success": True, "uid": card_dict["uid"]}


@app.put("/api/collection/{uid}")
def api_update_card(uid: str, patch: Dict[str, Any]):
    with LOCK:
        collection = read_collection()
        for i, c in enumerate(collection):
            if c.get("uid") != uid:
                continue
            if "quantity" in patch:
                c["quantity"] = max(1, int(patch["quantity"] or 1))
            if "condition" in patch:
                c["condition"] = str(patch["condition"] or "NM").upper()
                c["uid"] = "%s_%s" % (c.get("id", ""), c["condition"])
            collection[i] = c
            write_collection(collection)
            return {"success": True, "card": c}
    raise HTTPException(status_code=404, detail="Carta no encontrada.")


@app.delete("/api/collection/{uid}")
def api_delete_card(uid: str):
    with LOCK:
        collection = read_collection()
        remaining = [c for c in collection if c.get("uid") != uid]
        if len(remaining) == len(collection):
            raise HTTPException(status_code=404, detail="Carta no encontrada.")
        write_collection(remaining)
    return {"success": True}


@app.post("/api/refresh")
def api_refresh():
    """Actualiza los precios de toda la colección desde TCGdex."""
    ids = sorted({c.get("id") for c in read_collection() if c.get("id")})
    if not ids:
        return {"success": True, "count": 0}
    try:
        fresh_map = refresh_cards(ids)
    except TcgApiError as e:
        raise HTTPException(status_code=e.code, detail=e.msg)

    count = 0
    with LOCK:
        collection = read_collection()  # se relee: pudo cambiar mientras se consultaba TCGdex
        for c in collection:
            f = fresh_map.get(c.get("id"))
            if not f:
                continue
            for k in ("price_eur", "price_usd", "cardmarket_url", "tcgplayer_url"):
                if f.get(k) is not None:
                    c[k] = f[k]
            count += 1
        write_collection(collection)
    return {"success": True, "count": count}


# ------------------------------------------------------------------ Excel
@app.get("/api/export_excel")
def api_export_excel():
    with LOCK:
        try:
            export_excel_file(read_collection(), str(EXCEL_FILE))
        except ExcelApiError as e:
            raise HTTPException(status_code=e.code, detail=e.msg)
        except Exception:
            raise HTTPException(status_code=500, detail="No se pudo generar el archivo Excel.")
    return {"success": True, "message": "Excel generado y actualizado correctamente en server/excel/%s" % EXCEL_FILE.name}


@app.post("/api/clear_excel")
def api_clear_excel():
    with LOCK:
        if EXCEL_FILE.exists():
            try:
                EXCEL_FILE.unlink()
            except OSError as e:
                raise HTTPException(status_code=500, detail="No se pudo borrar el archivo Excel: %s" % e)
    return {"success": True}


@app.post("/api/clear_collection")
def api_clear_collection():
    write_collection([])
    return {"success": True}


# ------------------------------------------------------------------ ajustes de IA
@app.get("/api/info")
def api_info():
    return {"hasKey": has_ai_key(), "excelExists": EXCEL_FILE.exists()}


@app.get("/api/settings")
def api_get_settings():
    """Proveedor activo y estado de cada uno. Nunca devuelve las claves."""
    return settings.public()


@app.put("/api/settings")
def api_put_settings(body: SettingsPatch):
    try:
        settings.update(body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return settings.public()


if __name__ == "__main__":
    import uvicorn

    # Solo escucha en tu equipo (127.0.0.1): el servidor guarda tus API keys y no tiene login.
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)