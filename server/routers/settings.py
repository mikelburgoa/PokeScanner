"""Ajustes: proveedor de IA, claves y modelos. Nunca se devuelve una clave."""
from fastapi import APIRouter, HTTPException

from core import config, user_settings
from core.security_audit import run_security_audit
from schemas import SettingsPatch
from services import ai

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