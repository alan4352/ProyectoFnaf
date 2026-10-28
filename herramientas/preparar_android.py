# -*- coding: utf-8 -*-
"""Prepara la carpeta build_android/ para armar el APK con buildozer.

Android ejecuta un archivo llamado main.py: es android/main.py, un lanzador que arranca el juego
(fnaf_fabrica.py copiado como juego.py) y muestra en pantalla cualquier error.

Uso (en Linux o WSL; en Windows no anda buildozer):
    pip install buildozer cython
    python herramientas/preparar_android.py
    cd build_android && buildozer android debug       # el APK queda en build_android/bin/
Lo más fácil es dejar que lo arme GitHub Actions (workflow "Version Android").
"""
import os
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "build_android")


def preparar():
    # Se conserva .buildozer (descargas del SDK/NDK) para no bajar todo de nuevo
    if os.path.isdir(DESTINO):
        for nombre in os.listdir(DESTINO):
            if nombre in (".buildozer", "bin"):
                continue
            ruta = os.path.join(DESTINO, nombre)
            shutil.rmtree(ruta) if os.path.isdir(ruta) else os.remove(ruta)
    else:
        os.makedirs(DESTINO)
    for nombre in os.listdir(RAIZ):
        if nombre.endswith(".py"):
            shutil.copy2(os.path.join(RAIZ, nombre), DESTINO)
    # El juego va como juego.py y main.py es un lanzador que muestra los errores en pantalla
    os.replace(os.path.join(DESTINO, "fnaf_fabrica.py"), os.path.join(DESTINO, "juego.py"))
    shutil.copy2(os.path.join(RAIZ, "android", "main.py"), os.path.join(DESTINO, "main.py"))
    shutil.copytree(os.path.join(RAIZ, "assets"), os.path.join(DESTINO, "assets"))
    shutil.copy2(os.path.join(RAIZ, "android", "buildozer.spec"), DESTINO)
    shutil.copytree(os.path.join(RAIZ, "android", "recipes"), os.path.join(DESTINO, "recipes"))
    print("Listo:", DESTINO)


if __name__ == "__main__":
    preparar()
