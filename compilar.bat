@echo off
title Compilador FNAF Industrial
cd /d "%~dp0"

echo [1/3] Limpiando compilaciones anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [2/3] Activando entorno virtual venv...
call venv\Scripts\activate.bat

echo [3/3] Compilando juego a .EXE unico...
pyinstaller --clean --noconfirm --onefile --noconsole --name "FNAF_Industrial" --add-data "assets;assets" fnaf_fabrica.py

echo.
echo =======================================================
echo  COMPILACION FINALIZADA CON EXITO
echo  Tu juego esta listo en: dist\FNAF_Industrial.exe
echo =======================================================
pause