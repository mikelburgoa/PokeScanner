🎴 PokeScanner
Aplicación Full-Stack para escanear, identificar y gestionar tu colección de cartas de Pokémon TCG utilizando Inteligencia Artificial (Google Gemini) y la API de TCGDex.

🛠️ Prerrequisitos
Antes de comenzar, asegúrate de tener instalado en tu sistema:

Node.js (versión 18 o superior)

Python (versión 3.8 o superior)

Una API Key gratuita de Google Gemini (consíguela gratis y sin tarjeta en Google AI Studio)

⚙️ Configuración Inicial (Primera vez)
1. Clonar el repositorio
git clone https://github.com/mikelburgoa/PokeScanner.git

cd PokeScanner

2. Configurar las variables de entorno (.env)
Copia la plantilla de configuración .env.example para crear tu archivo .env privado:

cp .env.example .env

Abre el archivo .env en tu editor de código y añade tu clave de Gemini:

GEMINI_API_KEY=tu_api_key_de_gemini_aqui

> Nota de seguridad: El archivo .env está protegido en .gitignore para garantizar que tu clave nunca se suba a GitHub.

3. Instalar dependencias
Backend (Python):

cd server

pip install -r requirements.txt

cd ..

Frontend (Vue 3):

npm install

🚀 Cómo Iniciar la Aplicación
Opción A: Inicio rápido en Windows con 1 Clic (Recomendado)
Haz doble clic sobre el archivo iniciar_pokescanner.bat en la raíz del proyecto.

Este script ejecutará automáticamente dos terminales en segundo plano:

El servidor de FastAPI (Backend) en el puerto 8000.

El servidor de Vite/Vue 3 (Frontend) en el puerto 3000.

Una vez ejecutado, abre tu navegador e ingresa a http://localhost:3000.

Opción B: Inicio manual por terminales
Si prefieres ver la consola en vivo de cada servicio, abre dos terminales separadas:

Terminal 1 - Backend (FastAPI):

cd server

python main.py

(El backend estará escuchando en http://localhost:8000)

Terminal 2 - Frontend (Vue 3 + Vite):

(Desde la raíz del proyecto PokeScanner/)

npm run dev

(Abre tu navegador en http://localhost:3000)

📖 Características Principales
📷 Escaneo en tiempo real: Visor con guía de encuadre vertical en proporción 3:4 para webcam o subida manual de imágenes.

🤖 Reconocimiento por IA: Lectura visual automática con Google Gemini y búsqueda cruzada en tiempo real con TCGdex.

📊 Gestión de colección: Registro del estado de conservación (NM, LP, MP, HP), control de stock y consulta de precios actualizados del mercado europeo (Cardmarket - EUR) y americano (TCGplayer - USD).

📑 Exportador a Excel: Generación de un informe clasificado por pestañas de expansiones guardado automáticamente en server/excel/coleccion_pokemon.xlsx.

📂 Estructura del Proyecto
PokeScanner/

├── server/                     # Backend FastAPI (Python)

│   ├── data/                   # Almacenamiento de colección (collection.json)

│   ├── excel/                  # Hojas de Excel exportadas

│   ├── services/               # Módulos de IA, TCGdex y exportador Excel

│   ├── main.py                 # Endpoints de la API REST

│   └── requirements.txt

├── src/                        # Frontend Vue 3 + Tailwind CSS

│   ├── components/             # Escáner de cámara, fichas e interfaz

│   ├── views/                  # Vistas principales (Escanear, Colección, Ajustes)

│   └── services/api.js         # Cliente HTTP

├── .env.example                # Plantilla de variables de entorno pública

├── .gitignore                  # Reglas para ocultar claves y archivos locales

├── iniciar_pokescanner.bat     # Lanzador automático para Windows

└── package.json