import os
import json
import base64
import threading
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from services.ai_scanner import identify, ApiError as AiApiError
from services.tcgdex import search_cards, refresh_cards, fetch_card, simplify, ApiError as TcgApiError
from services.excel_exporter import export_excel_file, ApiError as ExcelApiError

app = FastAPI(title="Card Collector API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

HERE = Path(__file__).resolve().parent

# Configuración de carpetas de almacenamiento local
DATA_DIR = HERE / "data"
DATA_FILE = DATA_DIR / "collection.json"

EXCEL_DIR = HERE / "excel"
EXCEL_DIR.mkdir(parents=True, exist_ok=True)
EXCEL_FILE = EXCEL_DIR / "coleccion_pokemon.xlsx"

LOCK = threading.Lock()

def read_collection():
    with LOCK:
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            if not DATA_FILE.exists():
                DATA_FILE.write_text("[]", encoding="utf-8")
            d = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            return d if isinstance(d, list) else []
        except (OSError, ValueError):
            return []

def write_collection(items):
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DATA_FILE.with_suffix(".tmp")
    with LOCK:
        tmp.write_text(json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
        os.replace(str(tmp), str(DATA_FILE))

class IdentifyRequest(BaseModel):
    image: str

class SaveCardRequest(BaseModel):
    id: str
    name: str
    number: Optional[str] = ""
    rarity: Optional[str] = "Común"
    set: Optional[str] = "Sin Expansión"
    image: Optional[str] = ""
    price_eur: Optional[float] = 0.0
    price_usd: Optional[float] = 0.0
    cardmarket_url: Optional[str] = ""
    tcgplayer_url: Optional[str] = ""
    condition: Optional[str] = "NM"
    quantity: Optional[int] = 1

@app.post("/api/identify")
def api_identify(req: IdentifyRequest):
    try:
        img_data = req.image
        if "," in img_data:
            img_data = img_data.split(",")[1]
        raw_bytes = base64.b64decode(img_data)
        
        ident = identify(raw_bytes)
        if not ident.get("is_pokemon_card") or not ident.get("name"):
            return {
                "success": False, 
                "message": "No se detectó ninguna carta Pokémon válida en la imagen.", 
                "candidates": []
            }
            
        cands = search_cards(
            name=ident.get("name", ""),
            number=ident.get("number", ""),
            total=ident.get("total", ""),
            set_name=ident.get("set_name", "")
        )

        if not cands:
            return {
                "success": False, 
                "message": f"Se identificó la carta ({ident.get('name')}), pero no se encontraron coincidencias en TCGdex.", 
                "candidates": []
            }

        return {
            "success": True,
            "identification": ident,
            "candidates": cands
        }
    except (AiApiError, TcgApiError) as e:
        raise HTTPException(status_code=e.code, detail=e.msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
def api_search(q: str, number: Optional[str] = "", set_name: Optional[str] = ""):
    try:
        cands = search_cards(name=q, number=number, set_name=set_name)
        return {"candidates": cands}
    except TcgApiError as e:
        raise HTTPException(status_code=e.code, detail=e.msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/collection")
def api_get_collection():
    return read_collection()

@app.post("/api/collection")
def api_save_card(card: SaveCardRequest):
    items = read_collection()
    card_dict = card.model_dump()
    uid = f"{card_dict['id']}_{card_dict['condition'].upper()}"
    card_dict["uid"] = uid
    
    found = False
    for it in items:
        if it.get("uid") == uid:
            it["quantity"] = int(it.get("quantity", 1)) + int(card_dict.get("quantity", 1))
            found = True
            break
    if not found:
        items.append(card_dict)
    write_collection(items)
    return {"success": True, "collection": items}

@app.put("/api/collection/{uid}")
def api_update_card(uid: str, card: SaveCardRequest):
    items = read_collection()
    card_dict = card.model_dump()
    card_dict["uid"] = uid
    updated = False
    for i, it in enumerate(items):
        if it.get("uid") == uid:
            items[i] = card_dict
            updated = True
            break
    if not updated:
        items.append(card_dict)
    write_collection(items)
    return {"success": True, "collection": items}

@app.delete("/api/collection/{uid}")
def api_delete_card(uid: str):
    items = read_collection()
    items = [it for it in items if it.get("uid") != uid]
    write_collection(items)
    return {"success": True, "collection": items}

@app.post("/api/refresh")
def api_refresh():
    items = read_collection()
    ids = list(set(it.get("id") for it in items if it.get("id")))
    if not ids:
        return {"success": True, "updated": 0}
    fresh_map = refresh_cards(ids)
    count = 0
    for it in items:
        cid = it.get("id")
        if cid in fresh_map:
            f = fresh_map[cid]
            it["price_eur"] = f.get("price_eur", it.get("price_eur", 0))
            it["price_usd"] = f.get("price_usd", it.get("price_usd", 0))
            it["cardmarket_url"] = f.get("cardmarket_url", it.get("cardmarket_url", ""))
            it["tcgplayer_url"] = f.get("tcgplayer_url", it.get("tcgplayer_url", ""))
            count += 1
    write_collection(items)
    return {"success": True, "updated": count, "collection": items}

@app.get("/api/export_excel")
def api_export_excel():
    items = read_collection()
    try:
        # Exporta directamente dentro de server/excel/coleccion_pokemon.xlsx
        export_excel_file(items, str(EXCEL_FILE))
        if EXCEL_FILE.exists():
            return FileResponse(
                path=str(EXCEL_FILE),
                filename="coleccion_pokemon.xlsx",
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        raise HTTPException(status_code=500, detail="No se pudo generar el archivo Excel.")
    except ExcelApiError as e:
        raise HTTPException(status_code=e.code, detail=e.msg)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear_excel")
def api_clear_excel():
    if EXCEL_FILE.exists():
        try:
            EXCEL_FILE.unlink()
        except Exception:
            pass
    return {"success": True}

@app.post("/api/clear_collection")
def api_clear_collection():
    write_collection([])
    return {"success": True, "collection": []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)