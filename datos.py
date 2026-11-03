# -*- coding: utf-8 -*-
"""Contenido del juego: dificultad por noche, cámaras y rutas.
Para ajustar el balance o los textos, este es el archivo a editar."""
import pygame

DIFICULTAD_NOCHES = {
  1: {"Barnaby": 3, "Silas": 2, "Penny": 1, "Rusty Bunny": 1},
  2: {"Barnaby": 6, "Silas": 5, "Penny": 3, "Rusty Bunny": 4},
  3: {"Barnaby": 9, "Silas": 8, "Penny": 6, "Rusty Bunny": 7},
  4: {"Barnaby": 12, "Silas": 11, "Penny": 9, "Rusty Bunny": 10},
  5: {"Barnaby": 15, "Silas": 14, "Penny": 13, "Rusty Bunny": 14},
  6: {"Barnaby": 14, "Silas": 13, "Penny": 13, "Rusty Bunny": 14},   # + la Unidad 0
}

# Ajuste de dificultad (menú de ajustes). No afecta a la Custom Night.
DIFICULTADES = {
    "historia":  {"nombre": "HISTORIA (FÁCIL)", "factor_ia": 0.6, "suma_ia": 0, "bateria": 0.75, "bonus_hora": False, "limite_unidad0": 16.0},
    "normal":    {"nombre": "NORMAL",           "factor_ia": 1.0, "suma_ia": 0, "bateria": 1.0,  "bonus_hora": True,  "limite_unidad0": 12.0},
    "pesadilla": {"nombre": "PESADILLA",        "factor_ia": 1.0, "suma_ia": 4, "bateria": 1.15, "bonus_hora": True,  "limite_unidad0": 9.0},
}

# Desafíos de la Custom Night. "mods" cambia reglas de la noche:
#   puerta_limitada: la compuerta se traba si queda cerrada más de 5 s
#   oxigeno_rapido: el oxígeno cae más rápido y se recupera más lento
#   fallas_frecuentes: las fallas de ventilación/cámaras aparecen el doble de seguido
#   bateria_inicial: batería con la que empieza la noche
#   sin_ir: no hay visión nocturna
DESAFIOS = [
    {"id": "marta", "nombre": "TURNO DE MARTA",
     "desc": "Solo Penny, al máximo. La compuerta se traba si queda cerrada más de 5 segundos.",
     "ia": {"Barnaby": 0, "Silas": 0, "Penny": 20, "Rusty Bunny": 0}, "mods": {"puerta_limitada": True}},
    {"id": "sin_aire", "nombre": "SIN AIRE",
     "desc": "Silas al máximo. El oxígeno cae más rápido y la ventilación falla seguido.",
     "ia": {"Barnaby": 5, "Silas": 20, "Penny": 0, "Rusty Bunny": 0}, "mods": {"oxigeno_rapido": True, "fallas_frecuentes": True}},
    {"id": "apagon", "nombre": "APAGÓN",
     "desc": "Los cuatro en 10, pero la noche empieza con 55% de batería.",
     "ia": {"Barnaby": 10, "Silas": 10, "Penny": 10, "Rusty Bunny": 10}, "mods": {"bateria_inicial": 55}},
    {"id": "a_ciegas", "nombre": "A CIEGAS",
     "desc": "Sin visión nocturna y con fallas de cámaras frecuentes.",
     "ia": {"Barnaby": 12, "Silas": 0, "Penny": 12, "Rusty Bunny": 12}, "mods": {"sin_ir": True, "fallas_frecuentes": True}},
    {"id": "banda", "nombre": "LA BANDA COMPLETA",
     "desc": "Los cuatro en 15. Sin trucos.",
     "ia": {"Barnaby": 15, "Silas": 15, "Penny": 15, "Rusty Bunny": 15}, "mods": {}},
]

# Los diálogos de las llamadas están en historia.py

CAMARAS_PLANTA = {
  "CAM_01": {"nombre": "Línea Ensamblaje 1",  "rect": pygame.Rect(950, 425, 60, 28)},
  "CAM_02": {"nombre": "Nave de Prensas",    "rect": pygame.Rect(950, 475, 60, 28)},
  "CAM_03": {"nombre": "Calderas (Sin Video)", "rect": pygame.Rect(870, 520, 60, 28)},
  "CAM_04": {"nombre": "Depósito Chatarra",   "rect": pygame.Rect(950, 525, 60, 28)},
  "CAM_05": {"nombre": "Bahía de Carga",    "rect": pygame.Rect(1030, 520, 60, 28)},
  "CAM_06": {"nombre": "Túnel Tuberías O.",   "rect": pygame.Rect(870, 575, 60, 28)},
  "CAM_07": {"nombre": "Corredor Cintas",    "rect": pygame.Rect(950, 575, 60, 28)},
  "CAM_08": {"nombre": "Generadores E.",    "rect": pygame.Rect(1030, 575, 60, 28)},
}

CAMARAS_VENT = {
  "VENT_01": {"nombre": "Toma Aire Principal", "rect": pygame.Rect(880, 430, 75, 32)},
  "VENT_02": {"nombre": "Bifurcación Norte",  "rect": pygame.Rect(1010, 430, 75, 32)},
  "VENT_03": {"nombre": "Ducto Extractor E.",  "rect": pygame.Rect(880, 520, 75, 32)},
  "VENT_04": {"nombre": "Ducto Techo Guardia", "rect": pygame.Rect(1010, 520, 75, 32)},
}

RUTA_SILAS_NORTE = ["CAM_02_MESAS", "VENT_01", "VENT_02", "VENT_04", "REJILLA_OFICINA", "OFICINA"]
RUTA_SILAS_OESTE = ["CAM_02_MESAS", "VENT_01", "VENT_03", "REJILLA_OFICINA", "OFICINA"]

JUMPSCARE_ARCHIVOS = {"Barnaby": "jumpscare_barnaby.png", "Silas": "jumpscare_silas.png",
                      "Penny": "jumpscare_penny.png", "Rusty Bunny": "jumpscare_bunny.png",
                      "Unidad 0": "jumpscare_unidad0.png"}

# Variantes de posición en cámara: (desplazamiento x, desplazamiento y, factor de escala).
# Cada vez que un animatrónico se mueve elige una al azar, así no aparece siempre en el mismo lugar.
POSES_CAMARA = [(0, 0, 1.0), (-175, 18, 0.88), (170, 8, 0.94)]
