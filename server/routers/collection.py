"""Colección: listar, añadir, modificar, borrar, actualizar precios y vaciar."""
from fastapi import APIRouter, HTTPException

from core.pricing import line_value, unit_value
from core.storage import LOCK, read_collection, snapshot, write_collection
from schemas import SaveCardRequest, UpdateCardRequest
from services.tcgdex import refresh_cards

router = APIRouter(prefix="/api", tags=["colección"])


def _uid(card_id, condition) -> str:
    return "%s_%s" % (card_id, condition)


def _with_values(card: dict) -> dict:
    """Añade el valor ya calculado: el frontend no necesita (ni debe) repetir la fórmula de precios."""
    out = dict(card)
    out["unit_value_eur"] = unit_value(card)
    out["value_eur"] = line_value(card)
    return out


@router.get("/collection")
def list_cards():
    return [_with_values(c) for c in read_collection()]


@router.post("/collection")
def save_card(card: SaveCardRequest):
    data = card.model_dump()
    data["uid"] = _uid(card.id, card.condition)
    with LOCK:
        collection = read_collection()
        found = next((c for c in collection if c.get("uid") == data["uid"]), None)
        if found:  # misma carta y mismo estado: se suman ejemplares
            found["quantity"] = int(found.get("quantity") or 1) + card.quantity
        else:
            collection.append(data)
        write_collection(collection)
    return {"success": True, "uid": data["uid"]}


@router.put("/collection/{uid}")
def update_card(uid: str, body: UpdateCardRequest):
    patch = body.model_dump(exclude_unset=True)
    with LOCK:
        collection = read_collection()
        idx = next((i for i, c in enumerate(collection) if c.get("uid") == uid), None)
        if idx is None:
            raise HTTPException(status_code=404, detail="Carta no encontrada.")
        card = collection[idx]

        if patch.get("quantity") is not None:
            card["quantity"] = patch["quantity"]
        if patch.get("condition") is not None:
            card["condition"] = patch["condition"]
            card["uid"] = _uid(card.get("id", ""), card["condition"])
            other = next((c for i, c in enumerate(collection) if i != idx and c.get("uid") == card["uid"]), None)
            if other:  # ya existía esa carta con ese estado: se fusionan en una sola línea
                other["quantity"] = int(other.get("quantity") or 1) + int(card.get("quantity") or 1)
                del collection[idx]
                card = other
        write_collection(collection)
    return {"success": True, "card": _with_values(card)}


@router.delete("/collection/{uid}")
def delete_card(uid: str):
    with LOCK:
        collection = read_collection()
        remaining = [c for c in collection if c.get("uid") != uid]
        if len(remaining) == len(collection):
            raise HTTPException(status_code=404, detail="Carta no encontrada.")
        write_collection(remaining)
    return {"success": True}


@router.post("/refresh")
def refresh_prices():
    """Actualiza los precios de toda la colección desde TCGdex."""
    ids = sorted({c.get("id") for c in read_collection() if c.get("id")})
    if not ids:
        return {"success": True, "count": 0}
    fresh_map = refresh_cards(ids)  # red: fuera del bloqueo

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


@router.post("/clear_collection")
def clear_collection():
    """Vacía la colección. Antes guarda una copia fechada en <carpeta de datos>/backups."""
    with LOCK:
        backup = snapshot("clear")
        write_collection([])
    return {"success": True, "backup": backup.name if backup else None}
