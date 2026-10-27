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
}

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
                      "Penny": "jumpscare_penny.png", "Rusty Bunny": "jumpscare_bunny.png"}

# Variantes de posición en cámara: (desplazamiento x, desplazamiento y, factor de escala).
# Cada vez que un animatrónico se mueve elige una al azar, así no aparece siempre en el mismo lugar.
POSES_CAMARA = [(0, 0, 1.0), (-175, 18, 0.88), (170, 8, 0.94)]
