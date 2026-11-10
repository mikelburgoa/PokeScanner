@echo off
:: Arranque con 1 clic: compila la web y lanza el servidor sin ventanas visibles.
:: Si algo falla, revisa la carpeta logs\ del proyecto (build.log y server.log).
start "" wscript.exe "%~dp0lanzador_oculto.vbs"
exit
