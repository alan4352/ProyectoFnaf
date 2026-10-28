# -*- coding: utf-8 -*-
"""Ventana del juego y escalado a cualquier pantalla.

El juego siempre se dibuja en una "pantalla virtual" de 1200x700. Al mostrar cada cuadro,
esa imagen se adapta al tamaño real de la ventana o del monitor:
  - "ajustar": la agranda sin deformarla (puede dejar bordes negros si el monitor
    tiene otra proporción, por ejemplo 5:4 o 16:10).
  - "estirar": llena toda la pantalla (sin bordes, pero la imagen se deforma un poco).
También aplica el brillo y muestra los FPS. Las posiciones del mouse se traducen solas,
así que el resto del código sigue trabajando en coordenadas de 1200x700.
"""
import sys

import pygame

import mando
import tactil

EN_NAVEGADOR = sys.platform == "emscripten"

virtual = None          # Superficie donde se dibuja el juego (1200x700)
AJUSTES = {}            # Mismo diccionario que los ajustes del juego
reloj = None            # Para mostrar los FPS
al_recibir_eventos = None   # Función opcional que ve todos los eventos (la usa el código secreto)
capa_extra = None           # Función opcional que dibuja encima de todo (panel del modo desarrollador)

_ventana = None
_destino = pygame.Rect(0, 0, 1, 1)
_flip_real = None
_get_pos_real = None
_event_get_real = None
_pressed_real = None
_teclas_real = None
_ultimo_tick = 0
_flechas_stick = set()
_fuente_fps = None


def iniciar(ancho, alto, ajustes):
    global virtual, AJUSTES, _flip_real, _get_pos_real, _event_get_real, _pressed_real, _teclas_real
    AJUSTES = ajustes
    aplicar_modo()
    virtual = pygame.Surface((ancho, alto))
    mando.iniciar(ancho, alto)
    # Se reemplazan estas funciones de pygame para que todo el juego funcione igual que antes
    # (y para que el mando se comporte como mouse y teclado)
    _flip_real = pygame.display.flip
    _get_pos_real = pygame.mouse.get_pos
    _event_get_real = pygame.event.get
    _pressed_real = pygame.mouse.get_pressed
    _teclas_real = pygame.key.get_pressed
    pygame.display.flip = presentar
    pygame.mouse.get_pos = posicion_mouse
    pygame.event.get = obtener_eventos
    pygame.mouse.get_pressed = botones_mouse
    pygame.key.get_pressed = teclas_apretadas
    return virtual


def aplicar_modo():
    """Crea la ventana según el ajuste de pantalla completa."""
    global _ventana
    ancho = virtual.get_width() if virtual else 1200
    alto = virtual.get_height() if virtual else 700
    try:
        if tactil.ES_ANDROID:
            # En Android: pantalla completa y la placa de video escala la imagen (más rápido)
            _ventana = pygame.display.set_mode((ancho, alto), pygame.FULLSCREEN | pygame.SCALED)
        elif EN_NAVEGADOR:
            # En la versión web la página se encarga del tamaño del lienzo
            _ventana = pygame.display.set_mode((ancho, alto))
        elif AJUSTES.get("pantalla_completa"):
            _ventana = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            _ventana = pygame.display.set_mode((ancho, alto), pygame.RESIZABLE)
    except pygame.error:
        _ventana = pygame.display.set_mode((ancho, alto))
    _calcular_destino()


def _calcular_destino():
    global _destino
    vw, vh = (virtual.get_size() if virtual else (1200, 700))
    ww, wh = pygame.display.get_surface().get_size()
    if AJUSTES.get("escalado") == "estirar":
        _destino = pygame.Rect(0, 0, ww, wh)
    else:
        k = min(ww / vw, wh / vh)
        w, h = int(vw * k), int(vh * k)
        _destino = pygame.Rect((ww - w) // 2, (wh - h) // 2, w, h)


def a_virtual(pos):
    """Convierte una posición de la ventana real a coordenadas del juego (1200x700)."""
    if not virtual or _destino.w == 0 or _destino.h == 0:
        return pos
    x = (pos[0] - _destino.x) * virtual.get_width() / _destino.w
    y = (pos[1] - _destino.y) * virtual.get_height() / _destino.h
    return (int(x), int(y))


def posicion_mouse():
    if mando.cursor_activo:
        return (int(mando.cursor[0]), int(mando.cursor[1]))
    return a_virtual(_get_pos_real())


def botones_mouse(*args, **kwargs):
    base = _pressed_real(*args, **kwargs)
    if tactil.dedo_en_boton:
        # El dedo está sobre un botón táctil: para el juego no hay clic izquierdo
        base = (False,) + tuple(base[1:])
    if not mando.clics_mantenidos:
        return base
    return tuple(bool(v) or (i + 1) in mando.clics_mantenidos for i, v in enumerate(base))


def teclas_apretadas():
    base = _teclas_real()
    extra = mando.flechas | _flechas_stick | tactil.teclas_mantenidas
    return mando.TeclasConMando(base, extra) if extra else base


def obtener_eventos(*args, **kwargs):
    global _ultimo_tick, _flechas_stick
    eventos = []
    for ev in _event_get_real(*args, **kwargs):
        if ev.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION) and hasattr(ev, "pos") \
                and not getattr(ev, "mando", False):
            datos = dict(ev.dict)
            datos["pos"] = a_virtual(ev.pos)
            ev = pygame.event.Event(ev.type, datos)
            if ev.type == pygame.MOUSEMOTION:
                mando.cursor[0], mando.cursor[1] = ev.pos   # El cursor del mando sigue desde donde está el mouse
        elif ev.type in (pygame.VIDEORESIZE, pygame.WINDOWSIZECHANGED):
            _calcular_destino()
        eventos.append(ev)
    ahora = pygame.time.get_ticks()
    dt = min(0.1, (ahora - _ultimo_tick) / 1000.0)
    _ultimo_tick = ahora
    if mando.mandos:
        eventos = mando.traducir(eventos)
        _flechas_stick = mando.actualizar(dt)
    elif any(ev.type == pygame.JOYDEVICEADDED for ev in eventos):
        eventos = mando.traducir(eventos)
    eventos = tactil.traducir(eventos, dt)
    if al_recibir_eventos:
        al_recibir_eventos(eventos)
    return eventos


def _aplicar_brillo(sup, brillo):
    if brillo > 1.0:
        extra = sup.copy()
        v = min(255, int(255 * (brillo - 1.0)))
        extra.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)
        sup.blit(extra, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
    elif brillo < 1.0:
        v = max(0, int(255 * brillo))
        sup.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)


def presentar():
    """Muestra la pantalla virtual en la ventana real (con brillo, escalado y FPS)."""
    global _fuente_fps
    ventana_real = pygame.display.get_surface()
    _calcular_destino()   # Barato: así responde enseguida si se agranda la ventana o cambia el modo

    imagen = virtual
    brillo = AJUSTES.get("brillo", 100) / 100.0
    mostrar_fps = AJUSTES.get("mostrar_fps") and reloj is not None
    botones_tactiles = tactil.hay_que_dibujar()
    if abs(brillo - 1.0) > 0.01 or mostrar_fps or capa_extra or mando.cursor_activo or botones_tactiles:
        # Con brillo normal se dibuja directo encima (el juego redibuja todo en cada cuadro);
        # copiar la pantalla entera en cada cuadro es caro en el celular
        imagen = virtual.copy() if abs(brillo - 1.0) > 0.01 else virtual
        if botones_tactiles:
            tactil.dibujar(imagen)
        if capa_extra:
            capa_extra(imagen)
        mando.dibujar_cursor(imagen)
        _aplicar_brillo(imagen, brillo)
        if mostrar_fps:
            if _fuente_fps is None:
                _fuente_fps = pygame.font.SysFont("consolas", 16, bold=True)
            txt = _fuente_fps.render(f"{reloj.get_fps():.0f} FPS", True, (120, 255, 140))
            imagen.blit(txt, (imagen.get_width() - txt.get_width() - 8, imagen.get_height() - 22))

    if _destino.size == imagen.get_size() and _destino.topleft == (0, 0):
        ventana_real.blit(imagen, (0, 0))
    else:
        ventana_real.fill((0, 0, 0))
        ventana_real.blit(pygame.transform.smoothscale(imagen, _destino.size), _destino.topleft)
    _flip_real()
