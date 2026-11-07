@echo off
title Deteniendo PokeScanner...
echo ===================================
echo   Deteniendo PokeScanner
echo ===================================
echo.

:: Forzar cierre de Node (Vite)
echo Deteniendo Frontend (Node/Vite)...
taskkill /F /IM node.exe /T 2>nul

:: Forzar cierre de Python (FastAPI)
echo Deteniendo Backend (FastAPI/Python)...
taskkill /F /IM python.exe /T 2>nul

echo.
echo ===================================
echo   PokeScanner se ha detenido correctamente.
echo ===================================
echo.
timeout /t 2 >nul
exit