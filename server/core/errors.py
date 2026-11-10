"""Un único tipo de error de la API para todos los servicios (TCGdex, IA, Excel...).

Este módulo no importa FastAPI al cargarse: los servicios pueden usar ApiError sin depender del
framework web. Los manejadores HTTP se registran en install().
"""


class ApiError(Exception):
    """Error controlado: `code` es el estado HTTP y `msg` el texto que verá el usuario."""

    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code
        self.msg = msg


def install(app) -> None:
    """Registra cómo se responden los errores: siempre como {"detail": "texto"}."""
    from fastapi import Request
    from fastapi.exceptions import RequestValidationError
    from fastapi.responses import JSONResponse

    async def api_error_handler(_: Request, exc: ApiError):
        return JSONResponse({"detail": exc.msg}, status_code=exc.code)

    async def validation_handler(_: Request, exc: RequestValidationError):
        # El frontend espera un texto, no la lista de errores de pydantic
        parts = []
        for e in exc.errors():
            field = ".".join(str(p) for p in e.get("loc", ())[1:])
            msg = e.get("msg", "valor no válido")
            parts.append("%s: %s" % (field, msg) if field else msg)
        return JSONResponse({"detail": "Datos no válidos. " + "; ".join(parts)}, status_code=422)

    app.add_exception_handler(ApiError, api_error_handler)
    app.add_exception_handler(RequestValidationError, validation_handler)
