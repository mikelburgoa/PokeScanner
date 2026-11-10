"""Escaneo: identificar una carta a partir de una foto y buscar cartas en TCGdex."""
import base64
import binascii

from fastapi import APIRouter, HTTPException, Query

from core import config
from schemas import IdentifyRequest
from services import ai
from services.tcgdex import search_cards

router = APIRouter(prefix="/api", tags=["escaneo"])


@router.post("/identify")
def identify_card(req: IdentifyRequest):
    raw = req.image.split(",", 1)[1] if "," in req.image else req.image  # quita «data:image/jpeg;base64,»
    try:
        img = base64.b64decode(raw)
    except (binascii.Error, ValueError):
        raise HTTPException(status_code=400, detail="La imagen no es válida.")
    if not img:
        raise HTTPException(status_code=400, detail="Petición vacía.")
    if len(img) > config.MAX_IMAGE_BYTES:
        raise HTTPException(status_code=413, detail="La imagen es demasiado grande.")

    ident = ai.identify(img)  # los fallos de la IA salen como ApiError y se responden solos
    if not ident.get("is_pokemon_card") or not ident.get("name"):
        return {"success": False, "message": "No se detectó ninguna carta Pokémon válida en la imagen."}

    cands = search_cards(
        str(ident.get("name")),
        str(ident.get("number") or ""),
        str(ident.get("total") or ""),
        str(ident.get("set_name") or ""),
    )
    if not cands:
        return {
            "success": False,
            "identification": ident,
            "message": "Se identificó la carta (%s), pero no se encontraron coincidencias en TCGdex." % ident.get("name"),
        }
    return {"success": True, "identification": ident, "candidates": cands}


@router.get("/search")
def search(
    name: str = Query("", max_length=150),
    number: str = Query("", max_length=30),
    total: str = Query("", max_length=30),
    set: str = Query("", max_length=150),
):
    return {"success": True, "candidates": search_cards(name, number, total, set)}
