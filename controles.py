# -*- coding: utf-8 -*-
"""Teclas configurables de la oficina.

Cada acción tiene una tecla principal (se puede cambiar desde AJUSTES > CONTROLES) y, en
algunos casos, una tecla alternativa fija (por ejemplo, las flechas). Las teclas elegidas se
guardan en ajustes.json con su nombre ("space", "a", "up"...), así se pueden leer y editar.

Uso desde el juego:
    controles.es("puerta", evento.key)        # ¿Esta tecla es la de la puerta?
    controles.mantenida("linterna", teclas)   # ¿Se está manteniendo la tecla de la linterna?
    controles.etiquetas()                     # Nombres de las teclas para los textos de ayuda
"""
import pygame

import idioma

# (id, nombre en el menú, tecla por defecto, tecla alternativa fija o None)
ACCIONES = [
    ("monitor", "ABRIR / CERRAR CÁMARAS", pygame.K_SPACE, pygame.K_c),
    ("puerta", "COMPUERTA IZQUIERDA", pygame.K_a, None),
    ("linterna", "LINTERNA (MANTENER)", pygame.K_f, None),
    ("techo", "MIRAR AL TECHO", pygame.K_w, pygame.K_UP),
    ("bajar", "VOLVER A LA OFICINA", pygame.K_s, pygame.K_DOWN),
    ("sellar", "SELLAR LA REJILLA (EN EL TECHO)", pygame.K_SPACE, None),
    ("panel", "PANEL DE MANTENIMIENTO", pygame.K_m, None),
    ("vision", "VISIÓN NOCTURNA (EN CÁMARAS)", pygame.K_v, None),
    ("pausa", "PAUSA", pygame.K_p, pygame.K_ESCAPE),
]
POR_DEFECTO = {a[0]: a[2] for a in ACCIONES}
ALTERNATIVAS = {a[0]: a[3] for a in ACCIONES if a[3] is not None}
NOMBRES = {a[0]: a[1] for a in ACCIONES}
# Estas dos comparten tecla a propósito: una sirve en la oficina y la otra mirando al techo
PUEDEN_COMPARTIR = {frozenset(("monitor", "sellar"))}
# Teclas que no se pueden asignar (las usa el juego para otras cosas)
RESERVADAS = {pygame.K_ESCAPE, pygame.K_F1, pygame.K_F2, pygame.K_F3, pygame.K_F4, pygame.K_F5, pygame.K_F6,
              pygame.K_F7, pygame.K_F8, pygame.K_F9, pygame.K_F10, pygame.K_F11, pygame.K_F12}

TECLAS = dict(POR_DEFECTO)
_ajustes = {}

NOMBRES_ES = {"space": "ESPACIO", "up": "ARRIBA", "down": "ABAJO", "left": "IZQUIERDA", "right": "DERECHA",
              "escape": "ESC", "return": "ENTER", "left shift": "SHIFT IZQ.", "right shift": "SHIFT DER.",
              "left ctrl": "CTRL IZQ.", "right ctrl": "CTRL DER.", "left alt": "ALT IZQ.", "right alt": "ALT DER.",
              "tab": "TAB", "backspace": "BORRAR"}


def cargar(ajustes):
    """Lee las teclas guardadas en los ajustes (o deja las de siempre)."""
    global _ajustes
    _ajustes = ajustes
    guardadas = ajustes.get("teclas") or {}
    for accion in POR_DEFECTO:
        TECLAS[accion] = POR_DEFECTO[accion]
        nombre = guardadas.get(accion)
        if nombre:
            try:
                codigo = pygame.key.key_code(nombre)
            except (ValueError, pygame.error):
                continue
            if codigo not in RESERVADAS:
                TECLAS[accion] = codigo


def _guardar():
    _ajustes["teclas"] = {a: pygame.key.name(k) for a, k in TECLAS.items() if k != POR_DEFECTO[a]}


def asignar(accion, tecla):
    """Cambia la tecla de una acción. Si otra acción la usaba, intercambian las teclas.
    Devuelve False si la tecla no se puede usar."""
    if tecla in RESERVADAS or tecla in ALTERNATIVAS.values() and ALTERNATIVAS.get(accion) != tecla:
        return False
    anterior = TECLAS[accion]
    for otra, k in TECLAS.items():
        if otra != accion and k == tecla and frozenset((otra, accion)) not in PUEDEN_COMPARTIR:
            TECLAS[otra] = anterior
    TECLAS[accion] = tecla
    _guardar()
    return True


def restablecer():
    TECLAS.update(POR_DEFECTO)
    _guardar()


def es(accion, tecla):
    return tecla == TECLAS[accion] or tecla == ALTERNATIVAS.get(accion)


def mantenida(accion, teclas):
    alt = ALTERNATIVAS.get(accion)
    return bool(teclas[TECLAS[accion]] or (alt is not None and teclas[alt]))


def nombre_tecla(tecla):
    nombre = pygame.key.name(tecla)
    if idioma.ACTUAL.get("idioma") != "en" and nombre in NOMBRES_ES:
        return NOMBRES_ES[nombre]
    return nombre.upper()


def etiquetas():
    """Para los textos de ayuda: {"puerta": "A", "bajar_alt": "S / ABAJO", ...}"""
    salida = {}
    for accion, tecla in TECLAS.items():
        salida[accion] = nombre_tecla(tecla)
        alt = ALTERNATIVAS.get(accion)
        salida[accion + "_alt"] = salida[accion] + (" / " + nombre_tecla(alt) if alt is not None else "")
    return salida
