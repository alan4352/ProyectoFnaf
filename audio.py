# -*- coding: utf-8 -*-
"""Sonidos: generador sintético de respaldo y carga de audio real (assets/audio)."""
import io
import math
import random
import wave
import pygame
from recursos import cargar_sonido_opcional

def crear_sonido_procedural(duracion, frecuencia_base, tipo="seno", fade=True, mod=0.0):
    tasa = 44100
    n_muestras = int(tasa * duracion)
    muestras = bytearray()

    for i in range(n_muestras):
        t = i / tasa
        frec = frecuencia_base + (math.sin(2.0 * math.pi * mod * t) * (frecuencia_base * 0.2) if mod > 0 else 0)

        if tipo == "seno":
            val = math.sin(2.0 * math.pi * frec * t)
        elif tipo == "cuadrada":
            val = 1.0 if math.sin(2.0 * math.pi * frec * t) >= 0 else -1.0
        elif tipo == "ruido":
            val = random.uniform(-1.0, 1.0)
        elif tipo == "sierra":
            val = 2.0 * (t * frec - math.floor(0.5 + t * frec))
        else:
            val = 0.0

        if fade:
            factor_fade = 1.0 - (i / n_muestras)
            val *= factor_fade

        val_int = int(max(-32767, min(32767, val * 28000)))
        b = val_int.to_bytes(2, byteorder='little', signed=True)
        muestras.extend(b)
        muestras.extend(b)

    buffer_io = io.BytesIO()
    with wave.open(buffer_io, 'wb') as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(tasa)
        wf.writeframes(muestras)
    buffer_io.seek(0)
    return pygame.mixer.Sound(buffer_io)


SONIDOS_REALES = []

def sonido(nombre, *args, **kwargs):
    """Usa el archivo de audio real si existe; si no, genera el sonido sintético de respaldo."""
    real = cargar_sonido_opcional(nombre)
    if real:
        SONIDOS_REALES.append(nombre)
        return real
    return crear_sonido_procedural(*args, **kwargs)


# El juego reemplaza este diccionario por sus ajustes (volumen general y de efectos, de 0 a 100)
AJUSTES_AUDIO = {"vol_general": 100, "vol_efectos": 100}

def volumen_efectos():
    return AJUSTES_AUDIO.get("vol_general", 100) * AJUSTES_AUDIO.get("vol_efectos", 100) / 10000.0

def reproducir_sonido(sfx, vol_izq=1.0, vol_der=1.0):
    v = volumen_efectos()
    if v <= 0:
        return
    canal = sfx.play()
    if canal:
        canal.set_volume(vol_izq * v, vol_der * v)
