# Guía de Inicio - PokeScanner

Esta guía explica cómo poner en marcha la aplicación **PokeScanner** (Frontend en Vue 3 + Vite + Tailwind CSS y Backend en Python FastAPI).

---

## Prerrequisitos
- **Node.js** (versión 18 o superior)
- **Python** (versión 3.8 o superior)

---

## 1. Iniciar el Servidor Backend (FastAPI)
Abre una terminal, entra en la carpeta del servidor e instala las dependencias de Python:

```bash
cd server
pip install -r requirements.txt
python main.py
```
*El servidor FastAPI se iniciará en `http://localhost:8000` con recarga automática (`--reload`).*

---

## 2. Iniciar el Cliente Frontend (Vue 3 + Vite)
Abre una **segunda terminal** en la raíz del proyecto (`PokeScanner/`) e inicia el entorno de desarrollo de Vite:

```bash
npm run dev
```
*Vite abrirá automáticamente el frontend en `http://localhost:3000` con proxy configurado hacia `/api`.*

---

## 3. Uso de la Aplicación
1. Abre tu navegador en **`http://localhost:3000`**.
2. **Escanear:** Activa tu webcam (o sube una foto) para identificar cartas de Pokémon automáticamente mediante IA.
3. **Colección:** Visualiza tus cartas guardadas, filtra por expansión, actualiza precios desde TCGdex o exporta toda tu colección a un archivo Excel formateado profesionalmente (`openpyxl`).
4. **Ajustes:** Configura claves de API opcionales y gestiona el almacenamiento local.
