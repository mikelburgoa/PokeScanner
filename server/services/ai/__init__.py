"""Lectura de cartas con IA.

Cada proveedor vive en su propio módulo y expone `identify(img) -> dict` con los mismos campos
(is_pokemon_card, name, number, total, set_name, ...). Para añadir otro: crea el módulo y regístralo
en RUNNERS (y en core/user_settings.py para que aparezca en Ajustes).
El proveedor y las claves se eligen desde Ajustes.
"""
from core import user_settings as settings
from core.errors import ApiError

from . import claude, gemini, ollama, openai

RUNNERS = {
    "gemini": gemini.identify,
    "anthropic": claude.identify,
    "openai": openai.identify,
    "ollama": ollama.identify,
}


def has_ai_key() -> bool:
    """¿Está la IA lista para usarse con la configuración actual?"""
    prov = settings.get()["provider"]
    if prov == "ollama":
        return True
    if prov == "auto":
        return any(settings.api_key(p) for p in settings.KEYED)
    return bool(settings.api_key(prov))


def identify(img):
    prov = settings.get()["provider"]

    if prov == "auto":  # el primero con clave (Gemini > Claude > OpenAI); si falla, prueba el siguiente
        order = [p for p in settings.KEYED if settings.api_key(p)]
        if not order:
            raise ApiError(503, "No hay ningún proveedor de IA configurado. Añade una API key (o usa Ollama) en Ajustes.")
        last = None
        for p in order:
            try:
                return RUNNERS[p](img)
            except ApiError as e:
                last = e
        raise last

    if prov in settings.KEYED and not settings.api_key(prov):
        raise ApiError(503, "Falta la API key de %s. Añádela en Ajustes." % settings.LABELS[prov])
    return RUNNERS[prov](img)
