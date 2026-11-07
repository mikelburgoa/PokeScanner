Set WshShell = CreateObject("WScript.Shell")
' Arranca FastAPI oculto (0 = ventana invisible)
WshShell.Run "cmd /c ""cd /d server && python main.py""", 0, False
' Arranca Vite oculto
WshShell.Run "cmd /c ""npm run dev""", 0, False
' Abre la web en el navegador predeterminado pasados 2 segundos
WScript.Sleep 2000
WshShell.Run "http://localhost:3001"