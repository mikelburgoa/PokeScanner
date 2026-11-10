"""Protección de la API para uso local.

La app no tiene login porque solo debe usarla quien está sentado delante del equipo. El riesgo real
no es que alguien se conecte desde fuera (el servidor solo escucha en 127.0.0.1), sino que una web
cualquiera que visites mientras la app está abierta haga que TU navegador le mande órdenes
(por ejemplo POST /api/clear_collection). Este middleware lo corta:

  * Host   -> solo localhost / 127.0.0.1 / ::1   (frena el «DNS rebinding»)
  * Origin -> si el navegador manda uno, tiene que ser de localhost (frena el CSRF entre webs)

Además añade cabeceras de seguridad a todas las respuestas.
Variable opcional: POKESCANNER_ALLOWED_HOSTS="mi-pc.local,otro" para permitir más nombres de host.
"""
import os
from urllib.parse import urlparse

from starlette.datastructures import MutableHeaders
from starlette.responses import JSONResponse

_LOCAL = {"localhost", "127.0.0.1", "::1"}

# Solo se aplica a nuestra página (index.html), no a /docs. Imágenes: https cualquiera (TCGdex).
CSP = (
    "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; "
    "font-src 'self' https://fonts.gstatic.com; img-src 'self' https: data: blob:; connect-src 'self'; "
    "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
)

_SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
}


def allowed_hosts() -> set:
    extra = {h.strip().lower() for h in os.environ.get("POKESCANNER_ALLOWED_HOSTS", "").split(",") if h.strip()}
    return _LOCAL | extra


def host_of_header(value: str) -> str:
    """'localhost:8000' -> 'localhost'; '[::1]:8000' -> '::1'."""
    value = (value or "").strip().lower()
    if value.startswith("["):
        return value[1:].split("]", 1)[0]
    return value.split(":", 1)[0]


class LocalOnlyMiddleware:
    """Middleware ASGI puro (sin BaseHTTPMiddleware): rápido y estable entre versiones."""

    def __init__(self, app):
        self.app = app
        self.hosts = allowed_hosts()

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope["headers"]}

        if host_of_header(headers.get("host", "")) not in self.hosts:
            await self._deny("Host no permitido.", scope, receive, send)
            return

        origin = headers.get("origin")
        if origin is not None:
            try:
                origin_host = (urlparse(origin).hostname or "").lower()
            except ValueError:
                origin_host = ""
            if origin_host not in self.hosts:  # incluye Origin: null
                await self._deny("Origen no permitido.", scope, receive, send)
                return

        async def send_with_headers(message):
            if message["type"] == "http.response.start":
                h = MutableHeaders(scope=message)
                for k, v in _SECURITY_HEADERS.items():
                    h.setdefault(k, v)
                if scope["path"].startswith("/api/"):
                    h.setdefault("Cache-Control", "no-store")
            await send(message)

        await self.app(scope, receive, send_with_headers)

    @staticmethod
    async def _deny(msg, scope, receive, send):
        await JSONResponse({"detail": msg}, status_code=403)(scope, receive, send)


def install(app) -> None:
    app.add_middleware(LocalOnlyMiddleware)