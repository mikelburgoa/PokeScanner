# 🎴 PokeScanner

Aplicación Full-Stack para escanear, identificar y gestionar tu colección de cartas de Pokémon TCG utilizando Inteligencia Artificial (**Google Gemini, Claude, OpenAI o un modelo local con Ollama**, a tu elección) y la API de TCGdex.

Está pensada para uso **personal y local**: cada persona la ejecuta en su equipo, con sus propias claves, y todos los datos se quedan en su ordenador. No hay base de datos global ni cuentas.

## 🛠️ Prerrequisitos

- **Node.js** (versión 18 o superior)
- **Python** (versión 3.9 o superior)
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
   pip install -U -r requirements.txt
   cd ..
   ```

   Frontend (Vue 3):
   ```bash
   npm install
   ```

3. **Configurar tu proveedor de IA** (elige una de las dos formas)

   **Opción 1 — Desde la aplicación (recomendada).** Arranca la app, ve a **⚙️ Ajustes**, elige el proveedor, pega tu API key y pulsa **Guardar ajustes de IA**. No hace falta reiniciar nada.

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

> **Nunca compartas ni subas tu `.env`** (ni lo incluyas en un zip del proyecto). Está en `.gitignore`, pero un zip o una carpeta compartida no lo respeta. Para pasar el proyecto a alguien usa `git archive -o PokeScanner.zip HEAD`, que solo incluye lo que está en git.

## 🚀 Cómo Iniciar la Aplicación

Hay un único servidor: FastAPI sirve la web compilada y la API en el mismo puerto (**http://localhost:8000**). No hace falta el servidor de Vite, ni proxy, ni CORS.

### Opción A: Inicio rápido en Windows con 1 clic (recomendado)

Haz doble clic en `scripts/iniciar_pokescanner.bat`. Compila la web, arranca el servidor sin ventanas visibles y abre el navegador. Los registros quedan en la carpeta `logs/` (`build.log` y `server.log`), por si algo falla.

Para pararlo, haz doble clic en `scripts/detener_pokescanner.bat`. Solo cierra el servidor de PokeScanner; **no toca** otros programas de Python o Node que tengas abiertos.

### Opción B: Inicio manual por terminal

Desde la raíz del proyecto:
```bash
npm run build     # compila la web (necesario la primera vez y tras cambiar el frontend)
npm start         # arranca el servidor y abre el navegador
```

### Opción C: Modo desarrollo

Si vas a modificar el código, un solo comando levanta el backend (con recarga automática) y el frontend (Vite):
```bash
npm run dev
```
Abre `http://localhost:3001`. También puedes arrancarlos por separado con `npm run dev:api` y `npm run dev:web`.

## 📁 Dónde se guardan tus datos

Tu colección, el Excel, las copias de seguridad y las claves guardadas desde Ajustes viven **fuera de la carpeta del proyecto**, para que nunca acaben por error en un zip, en git o en una carpeta compartida:

| Sistema | Carpeta |
|---|---|
| Windows | `%APPDATA%\PokeScanner` |
| macOS | `~/Library/Application Support/PokeScanner` |
| Linux | `~/.local/share/pokescanner` |

Puedes cambiarla con la variable de entorno `POKESCANNER_DATA_DIR`. La ruta exacta aparece en la pestaña **Ajustes** y al arrancar el servidor.

Contenido de esa carpeta:

- `collection.json` — tu colección.
- `excel/coleccion_pokemon.xlsx` — el informe exportado.
- `settings.json` — proveedor de IA elegido y claves (nunca se envían al navegador).
- `backups/` — copia fechada de la colección cada vez que la vacías (se conservan las 10 últimas).

**Si vienes de una versión anterior:** al arrancar, el servidor copia automáticamente `server/data/collection.json`, `server/data/settings.json` y `server/excel/coleccion_pokemon.xlsx` a la nueva carpeta (sin borrar los originales). Cuando compruebes que todo está en su sitio, puedes borrar `server/data/` y `server/excel/`.

## 🤖 Proveedores de IA

Se elige en **⚙️ Ajustes → Lectura de fotos (IA)**. Cada proveedor tiene su propia clave y modelo editable.

| Proveedor | Coste | Notas |
|---|---|---|
| **Google Gemini** | Gratis (con límites) | Sin tarjeta. Clave en [AI Studio](https://aistudio.google.com/apikey). Si Google retira el modelo configurado, la app prueba otros automáticamente. |
| **Claude (Anthropic)** | De pago | Es la **API**, distinta de la suscripción de Claude.ai. Clave en [Anthropic Console](https://console.anthropic.com/settings/keys) y necesita saldo. |
| **OpenAI** | De pago | Es la **API**, distinta de ChatGPT Plus. Clave en [OpenAI Platform](https://platform.openai.com/api-keys). |
| **Ollama (local)** | Gratis | Corre en tu PC, sin clave. Requiere [Ollama](https://ollama.com/download) y un modelo con visión: `ollama pull qwen2.5vl`. Necesita una GPU decente. |

**Modo Automático** (por defecto): usa el primer proveedor que tenga clave, en este orden: Gemini → Claude → OpenAI. Si uno falla, prueba el siguiente. Si tienes la clave de Gemini guardada, Automático siempre la usará primero; para forzar otro proveedor, elígelo explícitamente en Ajustes.

Para añadir otro proveedor, crea un módulo en `server/services/ai/` con una función `identify(img)` y regístralo en `RUNNERS` (`server/services/ai/__init__.py`) y en `server/core/user_settings.py`.

## 🔒 Seguridad

PokeScanner no tiene login porque solo debe usarlo quien está delante del equipo. Para que eso sea seguro:

- **El servidor solo escucha en `127.0.0.1`**: no es accesible desde otros equipos de tu red ni desde internet.
- **Protección contra webs maliciosas.** Mientras la app está abierta, una página cualquiera podría intentar que tu navegador mande órdenes a `localhost` (por ejemplo, vaciar tu colección). El servidor rechaza cualquier petición cuyo `Host` u `Origin` no sea `localhost`.
- **Las claves nunca llegan al navegador**: la interfaz solo sabe si existe una clave, no su valor. Las llamadas a los proveedores salen siempre del servidor.
- **Todo lo que entra se valida** (tamaños, estados NM/LP/MP/HP, URLs solo de Cardmarket y TCGplayer, imagen máxima de 15 MB).
- **Excel seguro:** un nombre que empiece por `=` se guarda como texto, nunca como fórmula, y los hipervínculos solo apuntan a Cardmarket.
- **Ollama solo en tu equipo** por defecto (si lo tienes en otro PC de tu red: `POKESCANNER_ALLOW_REMOTE_OLLAMA=1`).
- **Copia de seguridad automática** antes de vaciar la colección.

No expongas el servidor: no uses túneles (ngrok…), no reenvíes puertos del router y no cambies el host a `0.0.0.0`.

### Variables de entorno opcionales

| Variable | Para qué sirve |
|---|---|
| `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` | Claves, como alternativa a Ajustes |
| `POKESCANNER_DATA_DIR` | Carpeta donde se guardan tus datos |
| `POKESCANNER_PORT` | Puerto del servidor (por defecto `8000`) |
| `POKESCANNER_ALLOWED_HOSTS` | Nombres de host extra permitidos (separados por comas) |
| `POKESCANNER_ALLOW_REMOTE_OLLAMA` | `1` para permitir un Ollama que no esté en este equipo |

## 📖 Características Principales

- 📷 **Escaneo en tiempo real:** visor con guía de encuadre vertical en proporción 3:4 para webcam o subida manual de imágenes.
- 🤖 **Reconocimiento por IA:** lectura visual automática con el proveedor que elijas (Gemini, Claude, OpenAI u Ollama) y búsqueda cruzada en tiempo real con TCGdex.
- 📊 **Gestión de colección:** registro del estado de conservación (NM, LP, MP, HP), control de stock y consulta de precios actualizados del mercado europeo (Cardmarket - EUR) y americano (TCGplayer - USD). El valor de cada carta lo calcula el servidor.
- 📑 **Exportador a Excel:** informe clasificado por pestañas de expansiones, guardado en `excel/coleccion_pokemon.xlsx` dentro de tu carpeta de datos.
- ⚙️ **Ajustes:** selector de proveedor de IA, gestión de claves y herramientas para borrar el Excel o vaciar la colección.

## 📂 Estructura del Proyecto

```
PokeScanner/
├── server/                       # Backend FastAPI (Python)
│   ├── main.py                   # Punto de entrada: ensambla la app y sirve la web compilada
│   ├── schemas.py                # Validación de todo lo que entra por la API
│   ├── core/
│   │   ├── config.py             # Rutas, carpeta de datos, migración desde versiones anteriores
│   │   ├── errors.py             # Un único ApiError para todos los servicios
│   │   ├── security.py           # Protección Host/Origin y cabeceras de seguridad
│   │   ├── storage.py            # Lectura/escritura de la colección y copias de seguridad
│   │   ├── pricing.py            # Única fuente de verdad del valor según el estado
│   │   ├── links.py              # Saneado de URLs (Cardmarket, TCGplayer, imágenes)
│   │   └── user_settings.py      # Proveedor, claves y modelos elegidos en Ajustes
│   ├── routers/                  # Endpoints agrupados por tema
│   │   ├── identify.py           # Identificar por foto y buscar
│   │   ├── collection.py         # CRUD de la colección y actualización de precios
│   │   ├── excel.py              # Exportar y borrar el Excel
│   │   └── settings.py           # Ajustes de IA
│   ├── services/
│   │   ├── ai/                   # Un módulo por proveedor
│   │   │   ├── __init__.py       # identify(): elige proveedor y reintenta
│   │   │   ├── base.py           # Prompt, cliente HTTP y parseo comunes
│   │   │   ├── gemini.py
│   │   │   ├── claude.py
│   │   │   ├── openai.py
│   │   │   └── ollama.py
│   │   ├── tcgdex.py             # Búsqueda de cartas y precios en TCGdex
│   │   └── excel_exporter.py     # Exportador a Excel
│   └── requirements.txt
├── src/                          # Frontend Vue 3 + Tailwind CSS
│   ├── components/               # Escáner de cámara, fichas e interfaz
│   ├── views/                    # Vistas principales (Escanear, Colección, Ajustes)
│   ├── utils/links.js            # Enlaces seguros a Cardmarket y TCGplayer
│   └── services/api.js           # Cliente HTTP
├── scripts/                      # Lanzadores para Windows
│   ├── iniciar_pokescanner.bat
│   ├── lanzador_oculto.vbs
│   └── detener_pokescanner.bat
├── .env.example                  # Plantilla pública de variables de entorno (opcional)
├── .gitignore
└── package.json
```

## 🔌 Endpoints de la API

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/identify` | Identifica una carta a partir de una foto (base64) y devuelve coincidencias de TCGdex |
| `GET` | `/api/search` | Busca cartas por nombre, número y set |
| `GET` | `/api/collection` | Lista la colección, con `unit_value_eur` y `value_eur` ya calculados |
| `POST` | `/api/collection` | Añade una carta (si ya existe con el mismo estado, suma ejemplares) |
| `PUT` / `DELETE` | `/api/collection/{uid}` | Modifica (cantidad, estado) o elimina una carta |
| `POST` | `/api/refresh` | Actualiza los precios de toda la colección |
| `POST` | `/api/clear_collection` | Vacía la colección (guarda antes una copia en `backups/`) |
| `GET` | `/api/export_excel` | Genera el Excel |
| `POST` | `/api/clear_excel` | Borra el archivo Excel |
| `GET` / `PUT` | `/api/settings` | Lee o guarda los ajustes de IA (nunca devuelve las claves) |
| `GET` | `/api/info` | Estado de la IA y carpeta de datos |

Con el servidor en marcha, la documentación interactiva está en `http://localhost:8000/docs`.

## 🩺 Solución de problemas

- **«La web no está compilada»:** ejecuta `npm run build` y reinicia el servidor.
- **«Falta la API key de …»:** el proveedor elegido no tiene clave. Añádela en Ajustes o en el `.env`.
- **Uso Claude/OpenAI pero sigue respondiendo Gemini:** el proveedor está en *Automático* y tienes la clave de Gemini. Elige tu proveedor en Ajustes.
- **Cambié el `.env` y no hace efecto:** reinicia el servidor. Las claves guardadas desde Ajustes no lo necesitan.
- **Error con Claude u OpenAI:** comprueba que la key es de la API (no de la suscripción de chat) y que la cuenta tiene saldo.
- **«Ningún modelo de Gemini está disponible»:** Google retira modelos con frecuencia. Escribe uno vigente en Ajustes → Gemini → Modelo ([lista](https://ai.google.dev/gemini-api/docs/models)).
- **Ollama no responde:** verifica que Ollama esté en marcha y que hayas descargado el modelo (`ollama pull qwen2.5vl`).
- **La cámara no se activa:** el navegador solo la permite en `localhost` o HTTPS. Revisa los permisos del navegador.
- **El puerto 8000 está ocupado:** cierra el otro programa o define `POKESCANNER_PORT` (en modo desarrollo, el proxy de `vite.config.js` apunta al 8000).
- **Perdí mi colección por vaciarla sin querer:** mira `backups/` en tu carpeta de datos; copia el último `collection-….json` como `collection.json`.
- **Algo no arranca con 1 clic:** revisa `logs/build.log` y `logs/server.log`.
