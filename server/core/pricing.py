"""Única fuente de verdad del valor de una carta según su estado de conservación.

El frontend ya no calcula nada: recibe `unit_value_eur` y `value_eur` en GET /api/collection,
y el exportador a Excel usa estas mismas funciones.
"""

COND_MULT = {"NM": 1.0, "LP": 0.85, "MP": 0.70, "HP": 0.50}
CONDITIONS = tuple(COND_MULT)


def _qty(item) -> int:
    try:
        return max(1, int(item.get("quantity") or 1))
    except (TypeError, ValueError):
        return 1


def _price(item) -> float:
    try:
        return float(item.get("price_eur") or item.get("price") or 0.0)
    except (TypeError, ValueError):
        return 0.0


def unit_value(item) -> float:
    """Valor de UN ejemplar en euros, ya ajustado por su estado."""
    cond = str(item.get("condition") or "NM").upper()
    return round(_price(item) * COND_MULT.get(cond, 1.0), 2)


def line_value(item) -> float:
    """Valor de todos los ejemplares de esa línea de la colección."""
    return round(unit_value(item) * _qty(item), 2)
