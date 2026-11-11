"""Ajustes: proveedor de IA, claves y modelos. Nunca se devuelve una clave."""
import os
import subprocess
import sys

from fastapi import APIRouter, HTTPException

from core import config, user_settings
from core.security_audit import run_security_audit
from schemas import SettingsPatch, TestProviderRequest
from services import ai
from services.ai import check

router = APIRouter(prefix="/api", tags=["ajustes"])


@router.get("/info")
def info():
    return {"hasKey": ai.has_ai_key(), "excelExists": config.EXCEL_FILE.exists(), "dataDir": str(config.DATA_DIR)}


@router.get("/settings")
def get_settings():
    return user_settings.public()


@router.put("/settings")
def put_settings(body: SettingsPatch):
    try:
        user_settings.update(body.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return user_settings.public()

@router.get("/security-audit")
def get_security_audit():
    return run_security_audit()


@router.post("/settings/test")
def test_provider(body: TestProviderRequest):
    """Comprueba clave y modelo sin gastar tokens. Siempre responde 200 con {ok, message}."""
    try:
        return check.run(body.provider, body.key, body.model, body.ollamaUrl)
    except ValueError as e:
        return {"ok": False, "message": str(e)}


@router.post("/open_data_dir")
def open_data_dir():
    """Abre la carpeta de datos en el explorador de archivos de este equipo (la ruta es fija, no viene del navegador)."""
    path = config.DATA_DIR
    try:
        path.mkdir(parents=True, exist_ok=True)
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # noqa: S606
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        raise HTTPException(status_code=500, detail="No se pudo abrir la carpeta. Ábrela a mano: %s" % path)
    return {"success": True}
