"""PokeScanner: punto de entrada del servidor (solo ensambla la aplicación).

    python server/main.py            # uso normal: sirve la web compilada (dist/) y la API en un solo puerto
    python server/main.py --reload   # desarrollo: recarga al editar el código (junto a «npm run dev:web»)
    python server/main.py --open     # además abre el navegador

Organización:
    core/      configuración y rutas, errores, seguridad, almacenamiento, precios, ajustes
    routers/   los endpoints, agrupados por tema (escaneo, colección, excel, ajustes)
    services/  lógica externa: ai/ (un módulo por proveedor), tcgdex.py, excel_exporter.py
    schemas.py validación de todo lo que entra por la API
"""
import argparse
import atexit
import os
import threading
import webbrowser

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse

from core import config, errors, security
from routers import collection, excel, identify
from routers import settings as settings_router


def _mount_frontend(app: FastAPI) -> None:
    """Sirve la web compilada (dist/): un solo puerto, sin servidor de Vite, sin proxy y sin CORS."""
    index = config.DIST_DIR / "index.html"
    if not index.is_file():

        @app.get("/", include_in_schema=False)
        def no_frontend():
            return JSONResponse({
                "detail": "La web no está compilada. Ejecuta «npm run build» y reinicia, "
                          "o usa «npm run dev» para desarrollo."
            })

        return

    root = config.DIST_DIR.resolve()

    @app.get("/{full_path:path}", include_in_schema=False)
    def frontend(full_path: str):
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        try:
            target = (root / full_path).resolve()
            target.relative_to(root)  # impide salirse de dist/ (../../...)
        except (ValueError, OSError):
            raise HTTPException(status_code=404, detail="Not Found")
        if full_path and target.is_file():
            headers = {"Cache-Control": "public, max-age=31536000, immutable"} if full_path.startswith("assets/") else None
            return FileResponse(target, headers=headers)
        # Cualquier otra ruta es de vue-router (/collection, /settings...): se devuelve la página principal
        return FileResponse(index, headers={"Content-Security-Policy": security.CSP, "Cache-Control": "no-cache"})


def create_app() -> FastAPI:
    app = FastAPI(title="PokeScanner API", version="2.0.0")
    errors.install(app)
    security.install(app)
    for router in (identify.router, collection.router, excel.router, settings_router.router):
        app.include_router(router)
    _mount_frontend(app)
    return app


app = create_app()


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor de PokeScanner")
    parser.add_argument("--reload", action="store_true", help="recarga el servidor al editar el código (desarrollo)")
    parser.add_argument("--open", action="store_true", help="abre el navegador al arrancar")
    args = parser.parse_args()

    copied = config.migrate_legacy_data()
    url = "http://localhost:%d" % config.PORT
    print("PokeScanner  ->  %s" % url)
    print("Tus datos    ->  %s" % config.DATA_DIR)
    if copied:
        print("Datos de la versión anterior copiados: %s (los originales de server/data y server/excel siguen ahí; "
              "bórralos cuando compruebes que todo está bien)" % ", ".join(copied))
    if not (config.DIST_DIR / "index.html").is_file():
        print("Aviso: no hay web compilada (dist/). Ejecuta «npm run build», o usa «npm run dev» para desarrollo.")

    if args.open:
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()

    import uvicorn

    if args.reload:
        uvicorn.run("main:app", host=config.HOST, port=config.PORT, reload=True,
                    app_dir=str(config.SERVER_DIR), reload_dirs=[str(config.SERVER_DIR)])
        return

    # El archivo PID permite que detener_pokescanner.bat cierre solo ESTE proceso (y no todos los de Python)
    pid_file = config.PROJECT_DIR / "logs" / "server.pid"
    try:
        pid_file.parent.mkdir(exist_ok=True)
        pid_file.write_text(str(os.getpid()))
        atexit.register(lambda: pid_file.unlink(missing_ok=True))
    except OSError:
        pass
    uvicorn.run(app, host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()