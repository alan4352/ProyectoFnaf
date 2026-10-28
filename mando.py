# -*- coding: utf-8 -*-
"""Soporte para mando (joystick / gamepad).

El mando se traduce a lo que el juego ya entiende, así no hay que tocar el resto del código:
  - Stick izquierdo: mueve un cursor por la pantalla (como el mouse). En las cintas mueve al
    personaje (cuenta como las flechas).
  - Cruceta: flechas (mirar al techo / volver, moverse por los menús).
  - Botones: se convierten en clics o en la tecla de cada acción (ver BOTONES).

Distribución (nombres de un mando de Xbox; en otros mandos cambian las letras):
  A = clic   B = clic derecho (linterna, visión IR)   X = puerta   Y = cámaras
  LB = mirar al techo   RB = panel de mantenimiento   BACK = visión nocturna   START = pausa
"""
import pygame

import controles

# Botón -> ("clic", número de botón del mouse) o ("accion", acción de controles.py)
BOTONES = {
    0: ("clic", 1),
    1: ("clic", 3),
    2: ("accion", "puerta"),
    3: ("accion", "monitor"),
    4: ("accion", "techo"),
    5: ("accion", "panel"),
    6: ("accion", "vision"),
    7: ("accion", "pausa"),
}
DESCRIPCION = [("A", "CLIC"), ("B", "CLIC DERECHO / LINTERNA"), ("X", "COMPUERTA"), ("Y", "CÁMARAS"),
               ("LB", "MIRAR AL TECHO"), ("RB", "PANEL DE MANTENIMIENTO"), ("BACK", "VISIÓN NOCTURNA"),
               ("START", "PAUSA"), ("STICK", "CURSOR / MOVERSE"), ("CRUCETA", "FLECHAS")]
ZONA_MUERTA = 0.25
VELOCIDAD_CURSOR = 950.0      # Píxeles por segundo con el stick a fondo

mandos = {}                   # instance_id -> Joystick
cursor = [600.0, 350.0]
cursor_activo = False         # True cuando el último movimiento fue con el mando
clics_mantenidos = set()      # Botones de mouse "apretados" con el mando
flechas = set()               # Flechas "apretadas" con el stick o la cruceta
_limites = (1200, 700)


def iniciar(ancho, alto):
    global _limites
    _limites = (ancho, alto)
    try:
        pygame.joystick.init()
        for i in range(pygame.joystick.get_count()):
            _agregar(i)
    except pygame.error:
        pass


def _agregar(indice):
    try:
        j = pygame.joystick.Joystick(indice)
        j.init()
        mandos[j.get_instance_id()] = j
    except pygame.error:
        pass


def nombre_mando():
    for j in mandos.values():
        try:
            return j.get_name()
        except pygame.error:
            pass
    return None


def _tecla(accion, abajo):
    tecla = controles.TECLAS[accion]
    tipo = pygame.KEYDOWN if abajo else pygame.KEYUP
    return pygame.event.Event(tipo, key=tecla, mod=0, unicode="", scancode=0, mando=True)


def _clic(boton, abajo):
    tipo = pygame.MOUSEBUTTONDOWN if abajo else pygame.MOUSEBUTTONUP
    return pygame.event.Event(tipo, button=boton, pos=(int(cursor[0]), int(cursor[1])), mando=True)


def traducir(eventos):
    """Recibe los eventos de pygame y devuelve la lista con los del mando convertidos."""
    global cursor_activo
    salida = []
    for ev in eventos:
        if ev.type == pygame.JOYDEVICEADDED:
            _agregar(ev.device_index)
        elif ev.type == pygame.JOYDEVICEREMOVED:
            mandos.pop(ev.instance_id, None)
            clics_mantenidos.clear()
            flechas.clear()
        elif ev.type in (pygame.JOYBUTTONDOWN, pygame.JOYBUTTONUP):
            abajo = ev.type == pygame.JOYBUTTONDOWN
            tipo, valor = BOTONES.get(ev.button, (None, None))
            if tipo == "clic":
                cursor_activo = True
                (clics_mantenidos.add if abajo else clics_mantenidos.discard)(valor)
                salida.append(_clic(valor, abajo))
            elif tipo == "accion":
                salida.append(_tecla(valor, abajo))
            continue
        elif ev.type == pygame.JOYHATMOTION:
            hx, hy = ev.value
            nuevas = set()
            if hx < 0: nuevas.add(pygame.K_LEFT)
            if hx > 0: nuevas.add(pygame.K_RIGHT)
            if hy > 0: nuevas.add(pygame.K_UP)
            if hy < 0: nuevas.add(pygame.K_DOWN)
            for k in nuevas - flechas:
                salida.append(pygame.event.Event(pygame.KEYDOWN, key=k, mod=0, unicode="", scancode=0, mando=True))
            for k in flechas - nuevas:
                salida.append(pygame.event.Event(pygame.KEYUP, key=k, mod=0, unicode="", scancode=0, mando=True))
            flechas.clear()
            flechas.update(nuevas)
            continue
        elif ev.type == pygame.MOUSEMOTION and not getattr(ev, "mando", False):
            cursor_activo = False
        salida.append(ev)
    return salida


def actualizar(dt):
    """Se llama una vez por cuadro: mueve el cursor con el stick."""
    global cursor_activo
    stick_x = stick_y = 0.0
    for j in mandos.values():
        try:
            if j.get_numaxes() >= 2:
                stick_x, stick_y = j.get_axis(0), j.get_axis(1)
                break
        except pygame.error:
            pass
    stick_x = 0.0 if abs(stick_x) < ZONA_MUERTA else stick_x
    stick_y = 0.0 if abs(stick_y) < ZONA_MUERTA else stick_y
    if stick_x or stick_y:
        cursor_activo = True
        cursor[0] = min(_limites[0] - 1, max(0, cursor[0] + stick_x * abs(stick_x) * VELOCIDAD_CURSOR * dt))
        cursor[1] = min(_limites[1] - 1, max(0, cursor[1] + stick_y * abs(stick_y) * VELOCIDAD_CURSOR * dt))
    # El stick también cuenta como flechas mantenidas (para moverse en las cintas)
    stick_flechas = set()
    if stick_x < -0.5: stick_flechas.add(pygame.K_LEFT)
    if stick_x > 0.5: stick_flechas.add(pygame.K_RIGHT)
    if stick_y < -0.5: stick_flechas.add(pygame.K_UP)
    if stick_y > 0.5: stick_flechas.add(pygame.K_DOWN)
    return stick_flechas


class TeclasConMando:
    """Envuelve el resultado de pygame.key.get_pressed() sumando lo que se aprieta con el mando."""
    def __init__(self, base, extra):
        self.base, self.extra = base, extra

    def __getitem__(self, tecla):
        return bool(self.base[tecla]) or tecla in self.extra

    def __len__(self):
        return len(self.base)


def dibujar_cursor(sup):
    if not cursor_activo:
        return
    x, y = int(cursor[0]), int(cursor[1])
    pygame.draw.circle(sup, (0, 0, 0), (x, y), 9, 3)
    pygame.draw.circle(sup, (255, 230, 120), (x, y), 8, 2)
    pygame.draw.line(sup, (255, 230, 120), (x - 13, y), (x - 5, y), 2)
    pygame.draw.line(sup, (255, 230, 120), (x + 5, y), (x + 13, y), 2)
    pygame.draw.line(sup, (255, 230, 120), (x, y - 13), (x, y - 5), 2)
    pygame.draw.line(sup, (255, 230, 120), (x, y + 5), (x, y + 13), 2)
