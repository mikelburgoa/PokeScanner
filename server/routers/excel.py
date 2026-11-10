"""Excel: generar el informe de la colección y borrarlo."""
from fastapi import APIRouter, HTTPException

from core import config
from core.errors import ApiError
from core.storage import LOCK, read_collection
from services.excel_exporter import export_excel_file

router = APIRouter(prefix="/api", tags=["excel"])


@router.get("/export_excel")
@router.post("/export_excel")
def export_excel():
    with LOCK:
        try:
            export_excel_file(read_collection(), str(config.EXCEL_FILE))
        except ApiError:
            raise
        except Exception:
            raise ApiError(500, "No se pudo generar el archivo Excel.")
    return {"success": True, "message": "Excel generado y actualizado correctamente en: %s" % config.EXCEL_FILE}


@router.post("/clear_excel")
def clear_excel():
    with LOCK:
        if config.EXCEL_FILE.exists():
            try:
                config.EXCEL_FILE.unlink()
            except OSError as e:
                raise HTTPException(status_code=500, detail="No se pudo borrar el archivo Excel: %s" % e)
    return {"success": True}