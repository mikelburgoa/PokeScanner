"""Saneado de URLs que acaban en el navegador (enlaces e imágenes) o en el Excel (hipervínculos).

Solo se aceptan enlaces https a Cardmarket / TCGplayer y a imágenes http(s). Cualquier otra cosa
(javascript:, file:, otros dominios...) se descarta y el frontend construye un enlace de búsqueda.
"""
from urllib.parse import urlparse

CARDMARKET_HOSTS = {"www.cardmarket.com", "cardmarket.com"}
TCGPLAYER_HOSTS = {"www.tcgplayer.com", "tcgplayer.com"}


def _clean(value, hosts, schemes):
    if not isinstance(value, str) or not value.strip():
        return ""
    value = value.strip()
    try:
        u = urlparse(value)
    except ValueError:
        return ""
    if u.scheme not in schemes or not u.hostname:
        return ""
    if hosts is not None and u.hostname.lower() not in hosts:
        return ""
    return value


def clean_cardmarket_url(value) -> str:
    return _clean(value, CARDMARKET_HOSTS, ("https",))


def clean_tcgplayer_url(value) -> str:
    return _clean(value, TCGPLAYER_HOSTS, ("https",))


def clean_image_url(value) -> str:
    return _clean(value, None, ("http", "https"))
