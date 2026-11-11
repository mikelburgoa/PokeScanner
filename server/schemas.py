"""Esquemas de entrada de la API: aquí se valida todo lo que llega del navegador."""
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator

from core import config
from core.links import clean_cardmarket_url, clean_image_url, clean_tcgplayer_url
from core.pricing import CONDITIONS

# Una foto de MAX_IMAGE_BYTES ocupa ~4/3 de ese tamaño en base64
_MAX_B64_CHARS = config.MAX_IMAGE_BYTES * 4 // 3 + 1024


def _condition(v):
    v = (v or "NM").strip().upper()
    if v not in CONDITIONS:
        raise ValueError("el estado debe ser uno de: " + ", ".join(CONDITIONS))
    return v


class IdentifyRequest(BaseModel):
    image: str = Field(min_length=1, max_length=_MAX_B64_CHARS)  # foto en base64 (con o sin «data:image/...;base64,»)


class SaveCardRequest(BaseModel):
    id: str = Field("", max_length=64, pattern=r"^[\w.\-]*$")
    name: str = Field(min_length=1, max_length=150)
    number: str = Field("", max_length=30)
    rarity: str = Field("Común", max_length=80)
    set: str = Field("Sin Expansión", max_length=150)
    image: str = Field("", max_length=500)
    price_eur: float = Field(0.0, ge=0, le=1_000_000)
    price_usd: float = Field(0.0, ge=0, le=1_000_000)
    cardmarket_url: str = Field("", max_length=500)
    tcgplayer_url: str = Field("", max_length=500)
    condition: str = "NM"
    quantity: int = Field(1, ge=1, le=9999)
    prices_updated: str = Field("", max_length=32)

    @field_validator("name", "number", "rarity", "set", mode="before")
    @classmethod
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v

    @field_validator("price_eur", "price_usd", mode="before")
    @classmethod
    def _null_price(cls, v):
        return 0.0 if v is None else v

    @field_validator("image")
    @classmethod
    def _image(cls, v):
        return clean_image_url(v)

    @field_validator("cardmarket_url")
    @classmethod
    def _cardmarket(cls, v):
        return clean_cardmarket_url(v)

    @field_validator("tcgplayer_url")
    @classmethod
    def _tcgplayer(cls, v):
        return clean_tcgplayer_url(v)

    @field_validator("condition")
    @classmethod
    def _cond(cls, v):
        return _condition(v)


class UpdateCardRequest(BaseModel):
    quantity: Optional[int] = Field(None, ge=1, le=9999)
    condition: Optional[str] = None

    @field_validator("condition")
    @classmethod
    def _cond(cls, v):
        return None if v is None else _condition(v)


class SettingsPatch(BaseModel):
    provider: Optional[str] = None
    keys: Optional[Dict[str, Optional[str]]] = None  # null = borrar clave, "" = no cambiar
    models: Optional[Dict[str, str]] = None
    ollamaUrl: Optional[str] = Field(None, max_length=300)


class TestProviderRequest(BaseModel):
    """«Probar conexión»: lo escrito en pantalla (aunque aún no esté guardado)."""
    provider: str
    key: str = Field("", max_length=300)
    model: str = Field("", max_length=100)
    ollamaUrl: str = Field("", max_length=200)

    @field_validator("provider")
    @classmethod
    def _prov(cls, v):
        if v not in ("gemini", "anthropic", "openai", "ollama"):
            raise ValueError("Proveedor no válido.")
        return v

    @field_validator("key", "model", "ollamaUrl", mode="before")
    @classmethod
    def _strip(cls, v):
        return v.strip() if isinstance(v, str) else v
