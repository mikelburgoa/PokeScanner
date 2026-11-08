# 🎴 PokeScanner

Aplicación Full-Stack para escanear, identificar y gestionar tu colección de cartas de Pokémon TCG utilizando Inteligencia Artificial (**Google Gemini, Claude, OpenAI o un modelo local con Ollama**, a tu elección) y la API de TCGdex.

## 🛠️ Prerrequisitos

Antes de comenzar, asegúrate de tener instalado en tu sistema:

- **Node.js** (versión 18 o superior)
- **Python** (versión 3.8 o superior)
- **Un proveedor de IA** para leer las fotos (basta con uno, ver [Proveedores de IA](#-proveedores-de-ia)). La opción más sencilla es una API Key gratuita de Google Gemini, sin tarjeta, en [Google AI Studio](https://aistudio.google.com/apikey).

## ⚙️ Configuración Inicial (Primera vez)

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/mikelburgoa/PokeScanner.git
   cd PokeScanner
   ```

2. **Instalar dependencias**

   Backend (Python):
   ```bash
   cd server
   pip install -r requirements.txt
   cd ..
   ```

   Frontend (Vue 3):
   ```bash
   npm install
   ```

3. **Configurar tu proveedor de IA** (elige una de las dos formas)

   **Opción 1 — Desde la aplicación (recomendada).** Arranca la app, ve a la pestaña **⚙️ Ajustes**, elige el proveedor, pega tu API key y pulsa **Guardar ajustes de IA**. No hace falta reiniciar nada.

   **Opción 2 — Con un archivo `.env`.** Copia la plantilla y añade tu clave:
   ```bash
   cp .env.example .env
   ```
   ```env
   GEMINI_API_KEY=tu_api_key_de_gemini_aqui
   # Opcionales, solo si usas esos proveedores:
   # ANTHROPIC_API_KEY=sk-ant-...
   # OPENAI_API_KEY=sk-...
   ```
   Si cambias el `.env`, **reinicia el servidor** para que lo lea.

> **Nota de seguridad:** tanto el `.env` como `server/data/settings.json` (donde se guardan las claves introducidas desde Ajustes) están protegidos en `.gitignore`, así que tus claves nunca se suben a GitHub. La aplicación nunca devuelve una clave al navegador: solo muestra si existe o no.

## 🚀 Cómo Iniciar la Aplicación

### Opción A: Inicio rápido en Windows con 1 clic (recomendado)

Haz doble clic sobre el archivo `iniciar_pokescanner.bat` en la raíz del proyecto.

Este script ejecutará automáticamente dos procesos en segundo plano:

- El servidor de FastAPI (Backend) en el puerto `8000`.
- El servidor de Vite/Vue 3 (Frontend) en el puerto `3001` (modificable en `vite.config.js`).

Una vez ejecutado, abre tu navegador en `http://localhost:3001`.

Para pararlo, usa `detener_pokescanner.bat`.

### Opción B: Inicio manual por terminales

Si prefieres ver la consola en vivo de cada servicio, abre dos terminales separadas:

**Terminal 1 — Backend (FastAPI):**
```bash
cd server
python main.py
```
El backend escucha en `http://127.0.0.1:8000`. Solo es accesible desde tu propio equipo, a propósito: guarda tus API keys y no tiene sistema de login.

**Terminal 2 — Frontend (Vue 3 + Vite)**, desde la raíz del proyecto `PokeScanner/`:
```bash
npm run dev
```
Abre tu navegador en `http://localhost:3001`.

## 🤖 Proveedores de IA

Se elige en **⚙️ Ajustes → Lectura de fotos (IA)**. Cada proveedor tiene su propia clave y modelo editable.

| Proveedor | Coste | Notas |
|---|---|---|
| **Google Gemini** | Gratis (con límites) | Sin tarjeta. Clave en [AI Studio](https://aistudio.google.com/apikey). |
| **Claude (Anthropic)** | De pago | Es la **API**, distinta de la suscripción de Claude.ai. Clave en [Anthropic Console](https://console.anthropic.com/settings/keys) y necesita saldo. |
| **OpenAI** | De pago | Es la **API**, distinta de ChatGPT Plus. Clave en [OpenAI Platform](https://platform.openai.com/api-keys). |
| **Ollama (local)** | Gratis | Corre en tu PC, sin clave. Requiere [Ollama](https://ollama.com/download) y un modelo con visión: `ollama pull qwen2.5vl`. Necesita una GPU decente. |

**Modo Automático** (por defecto): usa el primer proveedor que tenga clave, en este orden: Gemini → Claude → OpenAI. Si uno falla, prueba el siguiente. Ten en cuenta que si tienes la clave de Gemini en el `.env`, Automático siempre la usará primero; para forzar otro proveedor, elígelo explícitamente en Ajustes.

Para añadir otro proveedor, escribe una función `identify_xxx(img)` en `server/services/ai_scanner.py` y regístrala en `RUNNERS`.

## 📖 Características Principales

- 📷 **Escaneo en tiempo real:** visor con guía de encuadre vertical en proporción 3:4 para webcam o subida manual de imágenes.
- 🤖 **Reconocimiento por IA:** lectura visual automática con el proveedor que elijas (Gemini, Claude, OpenAI u Ollama) y búsqueda cruzada en tiempo real con TCGdex.
- 📊 **Gestión de colección:** registro del estado de conservación (NM, LP, MP, HP), control de stock y consulta de precios actualizados del mercado europeo (Cardmarket - EUR) y americano (TCGplayer - USD).
- 📑 **Exportador a Excel:** generación de un informe clasificado por pestañas de expansiones, guardado automáticamente en `server/excel/coleccion_pokemon.xlsx`.
- ⚙️ **Ajustes:** selector de proveedor de IA, gestión de claves y herramientas para borrar el Excel o vaciar la colección durante las pruebas.

## 📂 Estructura del Proyecto

```
PokeScanner/
├── server/                     # Backend FastAPI (Python)
│   ├── data/                   # Datos locales (collection.json y settings.json, ignorados por git)
│   ├── excel/                  # Hojas de Excel exportadas
│   ├── services/
│   │   ├── ai_scanner.py       # Lectura de fotos: Gemini, Claude, OpenAI y Ollama
│   │   ├── settings.py         # Proveedor, claves y modelos elegidos en Ajustes
│   │   ├── tcgdex.py           # Búsqueda de cartas y precios en TCGdex
│   │   └── excel_exporter.py   # Exportador a Excel
│   ├── main.py                 # Endpoints de la API REST
│   └── requirements.txt
├── src/                        # Frontend Vue 3 + Tailwind CSS
│   ├── components/             # Escáner de cámara, fichas e interfaz
│   ├── views/                  # Vistas principales (Escanear, Colección, Ajustes)
│   └── services/api.js         # Cliente HTTP
├── .env.example                # Plantilla de variables de entorno pública
├── .gitignore                  # Reglas para ocultar claves y archivos locales
├── iniciar_pokescanner.bat     # Lanzador automático para Windows
├── detener_pokescanner.bat     # Detiene frontend y backend
└── package.json
```

## 🔌 Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/identify` | Identifica una carta a partir de una foto (base64) y devuelve coincidencias de TCGdex |
| `GET` | `/api/search` | Busca cartas por nombre, número y set |
| `GET` | `/api/collection` | Lista la colección |
| `POST` | `/api/collection` | Añade una carta (si ya existe con el mismo estado, suma ejemplares) |
| `PUT` / `DELETE` | `/api/collection/{uid}` | Modifica o elimina una carta |
| `POST` | `/api/refresh` | Actualiza los precios de toda la colección |
| `GET` | `/api/export_excel` | Genera el Excel en `server/excel/` |
| `POST` | `/api/clear_excel` | Borra el archivo Excel |
| `POST` | `/api/clear_collection` | Vacía la colección |
| `GET` / `PUT` | `/api/settings` | Lee o guarda los ajustes de IA (nunca devuelve las claves) |

## 🩺 Solución de problemas

- **«Falta la API key de …»:** el proveedor elegido no tiene clave. Añádela en Ajustes o en el `.env`.
- **Uso Claude/OpenAI pero sigue respondiendo Gemini:** el proveedor está en *Automático* y tienes la clave de Gemini. Elige tu proveedor en Ajustes.
- **Cambié el `.env` y no hace efecto:** reinicia el servidor (`detener_pokescanner.bat` y vuelve a iniciar). Las claves guardadas desde Ajustes no lo necesitan.
- **Error con Claude u OpenAI:** comprueba que la key es de la API (no de la suscripción de chat) y que la cuenta tiene saldo.
- **Ollama no responde:** verifica que Ollama esté en marcha y que hayas descargado el modelo (`ollama pull qwen2.5vl`).
- **La cámara no se activa:** el navegador solo la permite en `localhost` o HTTPS. Revisa los permisos del navegador.