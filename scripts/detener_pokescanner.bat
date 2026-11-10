@echo off
setlocal
title Deteniendo PokeScanner...
set "PIDFILE=%~dp0..\logs\server.pid"

echo ===================================
echo   Deteniendo PokeScanner
echo ===================================
echo.

if not exist "%PIDFILE%" (
  echo PokeScanner no parece estar en marcha.
  echo ^(Si lo arrancaste con "npm run dev", cierralo con Ctrl+C en esa terminal.^)
  goto fin
)

set /p SPID=<"%PIDFILE%"

:: Solo se cierra ESE proceso, y solo si sigue siendo un python.exe
:: (no se tocan otros programas de Python ni de Node que tengas abiertos).
tasklist /FI "PID eq %SPID%" /FI "IMAGENAME eq python.exe" 2>nul | find "%SPID%" >nul
if errorlevel 1 (
  echo El servidor ya no estaba en marcha.
  del "%PIDFILE%" >nul 2>&1
  goto fin
)

taskkill /F /PID %SPID% /T >nul 2>&1
del "%PIDFILE%" >nul 2>&1
echo PokeScanner se ha detenido correctamente.

:fin
echo.
timeout /t 2 >nul
endlocal
exit
