@echo off
title Compilador FNAF Industrial Sector
cd /d "%~dp0"

echo =======================================================
echo  FNAF: INDUSTRIAL SECTOR - Compilar a .EXE
echo =======================================================
echo.

echo [1/4] Preparando entorno virtual (venv)...
if not exist venv (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: no se encontro Python. Instalalo desde python.org y marca "Add to PATH".
        pause
        exit /b 1
    )
)
call venv\Scripts\activate.bat

echo [2/4] Instalando dependencias (pygame y pyinstaller)...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: no se pudieron instalar las dependencias. Revisa tu conexion a internet.
    pause
    exit /b 1
)

echo [3/4] Limpiando compilaciones anteriores...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist
if exist FNAF_Industrial.spec del /q FNAF_Industrial.spec

echo [4/4] Compilando el juego a un .EXE unico (tarda 1-2 minutos)...
pyinstaller --clean --noconfirm --onefile --noconsole --name "FNAF_Industrial" --icon "icono.ico" --add-data "assets;assets" fnaf_fabrica.py
if errorlevel 1 (
    echo ERROR: fallo la compilacion. Revisa los mensajes de arriba.
    pause
    exit /b 1
)

echo.
echo =======================================================
echo  COMPILACION FINALIZADA CON EXITO
echo  Tu juego esta listo en: dist\FNAF_Industrial.exe
echo  (las partidas y ajustes se guardan junto al .exe)
echo =======================================================
pause
