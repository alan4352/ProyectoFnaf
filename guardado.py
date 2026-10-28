# -*- coding: utf-8 -*-
"""Guardado y carga del progreso en save_data.json (junto al juego)."""
import json
import os
from recursos import carpeta_juego

def ruta_guardado():
    # El guardado NO va en _MEIPASS: esa carpeta es temporal y se borra al cerrar el .exe.
    return os.path.join(carpeta_juego(), "save_data.json")

def guardar_partida(datos):
    try:
        with open(ruta_guardado(), "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4)
    except:
        pass

def cargar_partida():
    try:
        if os.path.exists(ruta_guardado()):
            with open(ruta_guardado(), "r", encoding="utf-8") as f:
                return json.load(f)
    except:
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
    "crt": True,
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
        if os.path.exists(ruta_ajustes()):
            with open(ruta_ajustes(), "r", encoding="utf-8") as f:
                guardados = json.load(f)
            ajustes.update({k: v for k, v in guardados.items() if k in AJUSTES_POR_DEFECTO})
    except Exception:
        pass
    return ajustes

def guardar_ajustes(ajustes):
    try:
        with open(ruta_ajustes(), "w", encoding="utf-8") as f:
            json.dump(ajustes, f, indent=4)
    except Exception:
        pass
