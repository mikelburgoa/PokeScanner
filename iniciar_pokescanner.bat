@echo off
title Lanzador PokeScanner

echo =========================================
echo    Iniciando PokeScanner (Back + Front)
echo =========================================
echo.

:: 1. Iniciar el servidor Backend (FastAPI) en una nueva ventana de terminal
echo [1/2] Arrancando servidor Backend (FastAPI)...
start "PokeScanner - Backend (FastAPI)" cmd /k "cd /d %~dp0server && python main.py"

:: Esperar 3 segundos para asegurar que FastAPI haya iniciado
timeout /t 3 /nobreak > nul

:: 2. Iniciar el cliente Frontend (Vue 3 + Vite) en una nueva ventana de terminal
echo [2/2] Arrancando cliente Frontend (Vue 3)...
start "PokeScanner - Frontend (Vite)" cmd /k "cd /d %~dp0 && npm run dev"

echo.
echo =========================================
echo  PokeScanner iniciado correctamente.
echo  Pestañas abiertas en segundo plano.
echo =========================================