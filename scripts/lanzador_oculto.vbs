' Arranca PokeScanner sin ventanas: compila la web (npm run build) y lanza el servidor, que abre el navegador.
' Todo se sirve desde un solo puerto (http://localhost:8000): no hace falta el servidor de Vite.
' Los registros quedan en la carpeta logs\ del proyecto.
Set fso = CreateObject("Scripting.FileSystemObject")
Set sh = CreateObject("WScript.Shell")

root = fso.GetParentFolderName(fso.GetParentFolderName(WScript.ScriptFullName))
sh.CurrentDirectory = root
If Not fso.FolderExists(root & "\logs") Then fso.CreateFolder(root & "\logs")

' 0 = ventana invisible, False = no espera a que termine.
' Se usa "&" (no "&&") para que el servidor arranque aunque la compilacion falle y ya exista una version anterior.
sh.Run "cmd /c ""npm run build > logs\build.log 2>&1 & python server\main.py --open > logs\server.log 2>&1""", 0, False
