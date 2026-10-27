# -*- coding: utf-8 -*-
"""Rutas de archivos y carga de imágenes/sonidos desde la carpeta assets/."""
import os
import sys
import pygame

def carpeta_juego():
    """Carpeta real del juego: junto al .exe si está compilado, o junto a los .py del juego."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.abspath(__file__))

def ruta_recurso(ruta_relativa):
    """Obtiene la ruta absoluta para recursos de solo lectura (compatible con PyInstaller)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(carpeta_juego(), ruta_relativa)


# Índice de todos los archivos dentro de assets/ y sus subcarpetas (imágenes y audio).
# Se busca por nombre de archivo, así podés reorganizar las carpetas sin tocar el código.
INDICE_ASSETS = {}
_carpeta_assets = ruta_recurso("assets")
if os.path.isdir(_carpeta_assets):
    for _raiz, _dirs, _archivos in os.walk(_carpeta_assets):
        for _a in _archivos:
            INDICE_ASSETS.setdefault(_a.lower(), os.path.join(_raiz, _a))


def cargar_imagen_opcional(*nombres, opaca=False):
    """Carga la primera imagen que exista entre los nombres dados (o None)."""
    for nombre in nombres:
        base = os.path.splitext(nombre)[0]
        # Se acepta la misma imagen en .png o .jpg (los fondos en .jpg pesan mucho menos)
        p = next((INDICE_ASSETS[c] for c in (nombre.lower(), base.lower() + ".jpg", base.lower() + ".jpeg")
                  if c in INDICE_ASSETS), None)
        if p:
            try:
                img = pygame.image.load(p)
                return img.convert() if opaca else img.convert_alpha()
            except Exception as e:
                print(f"[ASSETS] No se pudo cargar {p}: {e}")
    return None

def escalar_cubriendo(img, ancho, alto, ancla_y=0.5):
    """Escala la imagen para cubrir ancho x alto sin deformarla y recorta lo que sobra.
    ancla_y: 0 = conserva la parte de arriba, 0.5 = centro, 1 = parte de abajo."""
    if img is None:
        return None
    escala = max(ancho / img.get_width(), alto / img.get_height())
    w, h = max(ancho, round(img.get_width() * escala)), max(alto, round(img.get_height() * escala))
    grande = pygame.transform.smoothscale(img, (w, h))
    x = (w - ancho) // 2
    y = int((h - alto) * ancla_y)
    return grande.subsurface((x, y, ancho, alto)).copy()


EXTENSIONES_AUDIO = (".ogg", ".wav", ".mp3")

def cargar_sonido_opcional(nombre):
    """Busca assets/.../<nombre>.ogg|.wav|.mp3. Devuelve None si no existe."""
    for ext in EXTENSIONES_AUDIO:
        p = INDICE_ASSETS.get((nombre + ext).lower())
        if p:
            try:
                return pygame.mixer.Sound(p)
            except Exception as e:
                print(f"[AUDIO] No se pudo cargar {p}: {e}")
    return None
