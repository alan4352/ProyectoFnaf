# -*- coding: utf-8 -*-
"""Guardado y carga del progreso en save_data.json (junto al juego).

En la versión web (navegador) no hay archivos que duren: ahí se guarda en el
almacenamiento del navegador (localStorage), con el mismo contenido en JSON.
"""
import json
import os
import sys
from recursos import carpeta_juego

EN_NAVEGADOR = sys.platform == "emscripten"


def _leer_texto(ruta, clave_web):
    if EN_NAVEGADOR:
        try:
            import platform
            return platform.window.localStorage.getItem(clave_web)
        except Exception:
            return None
    if os.path.exists(ruta):
        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()
    return None


def _escribir_texto(ruta, clave_web, texto):
    if EN_NAVEGADOR:
        try:
            import platform
            platform.window.localStorage.setItem(clave_web, texto)
        except Exception:
            pass
        return
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(texto)

def ruta_guardado():
    # El guardado NO va en _MEIPASS: esa carpeta es temporal y se borra al cerrar el .exe.
    return os.path.join(carpeta_juego(), "save_data.json")

def guardar_partida(datos):
    try:
        _escribir_texto(ruta_guardado(), "fnaf_industrial_partida", json.dumps(datos, indent=4))
    except Exception:
        pass

def cargar_partida():
    try:
        texto = _leer_texto(ruta_guardado(), "fnaf_industrial_partida")
        if texto:
            return json.loads(texto)
    except Exception:
        pass
    return {
      "noche_desbloqueada": 1,
      "juego_completado_5_noches": False,
      "ia_custom": {"Barnaby": 10, "Silas": 10, "Penny": 10, "Rusty Bunny": 10},
      "record_20_20_20_20": False
    }


# -------------------------------------------------------------
# Ajustes (volumen, brillo, pantalla...) en ajustes.json
# -------------------------------------------------------------
AJUSTES_POR_DEFECTO = {
    "vol_general": 100,
    "vol_efectos": 100,
    "vol_musica": 80,
    "vol_voces": 100,
    "brillo": 100,
    "crt": not EN_NAVEGADOR,    # En el navegador el efecto CRT baja mucho los FPS: arranca apagado
    "pantalla_completa": False,
    "escalado": "ajustar",      # "ajustar" (sin deformar, con bordes) o "estirar" (llena la pantalla)
    "vel_giro": 100,
    "mostrar_fps": False,
    "dificultad": "normal",     # "historia", "normal" o "pesadilla"
    "idioma": "es",             # "es" (español) o "en" (inglés)
    "subtitulos": False,        # Mostrar en pantalla los sonidos importantes
    "teclas": {},               # Teclas cambiadas en AJUSTES > CONTROLES ({"puerta": "q", ...})
}

def ruta_ajustes():
    return os.path.join(carpeta_juego(), "ajustes.json")

def cargar_ajustes():
    ajustes = dict(AJUSTES_POR_DEFECTO)
    try:
        texto = _leer_texto(ruta_ajustes(), "fnaf_industrial_ajustes")
        if texto:
            guardados = json.loads(texto)
            ajustes.update({k: v for k, v in guardados.items() if k in AJUSTES_POR_DEFECTO})
    except Exception:
        pass
    return ajustes

def guardar_ajustes(ajustes):
    try:
        _escribir_texto(ruta_ajustes(), "fnaf_industrial_ajustes", json.dumps(ajustes, indent=4))
    except Exception:
        pass
