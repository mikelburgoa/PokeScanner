"""Módulo de auditoría de seguridad integral para PokeScanner (inspirado en security-audit-skill)."""
import re
from pathlib import Path
from core import config


def run_security_audit() -> dict:
    findings = []

    # Determinar la raíz real del proyecto
    root_dir = Path(__file__).resolve().parent.parent.parent
    gitignore_path = root_dir / ".gitignore"
    env_file = root_dir / ".env"
    server_dir = root_dir / "server"

    # ==========================================
    # 1. PROTECCIÓN DE SECRETOS Y ARCHIVOS DE CONFIGURACIÓN
    # ==========================================
    if gitignore_path.exists():
        content = gitignore_path.read_text(encoding="utf-8", errors="ignore")
        lines = [line.strip() for line in content.splitlines() if line.strip() and not line.startswith("#")]

        if not any(k in content for k in ["settings.json", "*.json", "server/data"]):
            findings.append({
                "severity": "HIGH",
                "category": "Secrets Protection",
                "issue": "El archivo de configuración de claves (settings.json) no está protegido en .gitignore",
                "fix": "Añade 'server/data/*.json' o 'settings.json' a tu archivo .gitignore."
            })

        if env_file.exists():
            if ".env" not in lines and "*.env" not in lines:
                findings.append({
                    "severity": "HIGH",
                    "category": "Secrets Protection",
                    "issue": "El archivo .env existe y NO está protegido en .gitignore",
                    "fix": "Añade '.env' a tu archivo .gitignore para evitar subir variables de entorno a GitHub."
                })

    # ==========================================
    # 2. ESCÁNER DE CLAVES Y SECRETOS HARDCODEADOS (SAST)
    # ==========================================
    patterns = [
        (r'AIzaSy[A-Za-z0-9_-]{33}', 'API Key de Google Gemini'),
        (r'sk-proj-[A-Za-z0-9_-]{40,}', 'API Key de OpenAI'),
        (r'sk-ant-api[A-Za-z0-9_-]{40,}', 'API Key de Anthropic/Claude'),
        (r'eyJ[A-Za-z0-9-_=]+\.[A-Za-z0-9-_=]+\.?[A-Za-z0-9-_.+/=]*', 'Token JWT Hardcodeado')
    ]

    for py_file in server_dir.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            code = py_file.read_text(encoding="utf-8", errors="ignore")
            for pattern, key_type in patterns:
                if re.search(pattern, code):
                    findings.append({
                        "severity": "CRITICAL",
                        "category": "Hardcoded Secret",
                        "issue": f"Se ha detectado una {key_type} hardcodeada en {py_file.name}",
                        "fix": "Mueve la clave al archivo settings.json o .env y no la dejes escrita directamente en el código."
                    })
        except Exception:
            pass

    # ==========================================
    # 3. VERIFICACIÓN DE CONFIGURACIÓN CORS (REDES)
    # ==========================================
    main_py = server_dir / "main.py"
    if main_py.exists():
        main_code = main_py.read_text(encoding="utf-8", errors="ignore")
        if 'allow_origins=["*"]' in main_code and 'allow_credentials=True' in main_code:
            findings.append({
                "severity": "MEDIUM",
                "category": "CORS Security",
                "issue": "CORS permite todos los orígenes ('*') combinados con credenciales activadas",
                "fix": "Restringe 'allow_origins' en main.py a orígenes específicos como 'http://localhost:5173'."
            })

    # ==========================================
    # 4. SEGURIDAD DE CABECERAS Y NAVEGACIÓN (HTTP HEADERS)
    # ==========================================
    security_py = server_dir / "core" / "security.py"
    headers_protected = False

    if main_py.exists():
        main_code = main_py.read_text(encoding="utf-8", errors="ignore")
        if "X-Frame-Options" in main_code:
            headers_protected = True

    if security_py.exists():
        sec_code = security_py.read_text(encoding="utf-8", errors="ignore")
        if "X-Frame-Options" in sec_code or "LocalOnlyMiddleware" in sec_code:
            headers_protected = True

    if not headers_protected:
        findings.append({
            "severity": "LOW",
            "category": "HTTP Headers",
            "issue": "El servidor no incluye cabeceras de protección antihjacking (X-Frame-Options)",
            "fix": "Añade 'X-Frame-Options: DENY' en _SECURITY_HEADERS dentro de core/security.py."
        })

    # ==========================================
    # 5. MODO DEBUG Y RECARGA
    # ==========================================
    if main_py.exists():
        main_code = main_py.read_text(encoding="utf-8", errors="ignore")
        if "debug=True" in main_code:
            findings.append({
                "severity": "MEDIUM",
                "category": "Environment Security",
                "issue": "El servidor FastAPI tiene activado el modo debug=True",
                "fix": "Desactiva debug=True en entornos donde vayas a exponer la aplicación a la red local o internet."
            })

    # ==========================================
    # VERIFICACIÓN DE ALMACENAMIENTO DE DATOS
    # ==========================================
    data_dir = Path(config.DATA_DIR)
    if not data_dir.exists():
        findings.append({
            "severity": "LOW",
            "category": "Storage",
            "issue": "La carpeta de datos no existe todavía",
            "fix": "Se creará automáticamente al guardar configuraciones."
        })

    return {
        "passed": len(findings) == 0,
        "total_findings": len(findings),
        "findings": findings
    }