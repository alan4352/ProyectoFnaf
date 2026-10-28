# -*- coding: utf-8 -*-
"""Controles táctiles (celular, tablet o pantalla táctil).

El juego se maneja casi todo con toques (un toque es un clic). Para lo que necesita
teclado o clic derecho, se dibujan botones encima de la pantalla:
  - Oficina: LINTERNA (mantener), TECHO, PAUSA.  Arrastrar el dedo gira la vista.
  - Techo: BAJAR, SELLAR.
  - Cámaras: VISIÓN IR. Mantener el dedo apretado sobre un ducto = clic derecho (compuerta).
  - Cintas de 1982: una cruz para moverse.
  - El botón "atrás" de Android funciona como ESC.

El juego dice qué botones mostrar con `contexto` (una función que devuelve un conjunto de nombres).
Se activa solo en Android y en celulares (versión web), o a mano desde AJUSTES.
"""
import os
import sys

import pygame

import controles

ES_ANDROID = "ANDROID_ARGUMENT" in os.environ or hasattr(sys, "getandroidapilevel")

modo = "auto"            # "auto", "si" o "no" (ajuste CONTROLES TÁCTILES)
contexto = None          # Función del juego: devuelve los nombres de los botones visibles
_detectado = ES_ANDROID
_fuente = None

# nombre: (rectángulo, texto, tipo, acción). tipo "pulsar" manda la tecla una vez; "mantener" la deja apretada
BOTONES = {
    "pausa": (pygame.Rect(12, 520, 92, 50), "PAUSA", "pulsar", "pausa"),
    "techo": (pygame.Rect(1036, 318, 152, 84), "TECHO", "pulsar", "techo"),
    "linterna": (pygame.Rect(1036, 414, 152, 120), "LINTERNA", "mantener", "linterna"),
    "bajar": (pygame.Rect(1036, 318, 152, 84), "BAJAR", "pulsar", "bajar"),
    "sellar": (pygame.Rect(1036, 414, 152, 120), "SELLAR", "pulsar", "sellar"),
    "ir": (pygame.Rect(1012, 108, 176, 52), "VISIÓN IR", "pulsar", "vision"),
}
_CRUZ_CENTRO = (1080, 560)
_CRUZ_PASO = 72
CRUZ = {
    "arriba": (pygame.Rect(_CRUZ_CENTRO[0] - 32, _CRUZ_CENTRO[1] - 32 - _CRUZ_PASO, 64, 64), pygame.K_UP),
    "abajo": (pygame.Rect(_CRUZ_CENTRO[0] - 32, _CRUZ_CENTRO[1] - 32 + _CRUZ_PASO, 64, 64), pygame.K_DOWN),
    "izquierda": (pygame.Rect(_CRUZ_CENTRO[0] - 32 - _CRUZ_PASO, _CRUZ_CENTRO[1] - 32, 64, 64), pygame.K_LEFT),
    "derecha": (pygame.Rect(_CRUZ_CENTRO[0] - 32 + _CRUZ_PASO, _CRUZ_CENTRO[1] - 32, 64, 64), pygame.K_RIGHT),
}
SEGUNDOS_TOQUE_LARGO = 0.5

teclas_mantenidas = set()    # Teclas "apretadas" con botones táctiles (se suman a key.get_pressed)
dedo_en_boton = False        # El dedo está sobre un botón táctil: el juego no debe ver ese clic
_boton_apretado = None
_arrastre = 0.0
_largo = None                # [tiempo, posición] de un toque que puede volverse toque largo
_reloj = 0.0


def detectar_web():
    """En el navegador: ¿es un celular o tablet (pantalla táctil como puntero principal)?"""
    global _detectado
    if sys.platform == "emscripten":
        try:
            import platform
            _detectado = bool(platform.window.matchMedia("(pointer: coarse)").matches)
        except Exception:
            pass


def activo():
    return modo == "si" or (modo == "auto" and _detectado)


def _visibles():
    if not activo() or contexto is None:
        return set()
    try:
        return contexto()
    except Exception:
        return set()


def _tecla(accion_o_tecla, abajo=True):
    tecla = controles.TECLAS[accion_o_tecla] if isinstance(accion_o_tecla, str) else accion_o_tecla
    return pygame.event.Event(pygame.KEYDOWN if abajo else pygame.KEYUP, key=tecla, mod=0, unicode="",
                              scancode=0, tactil=True)


def _boton_en(pos, visibles):
    for nombre in visibles:
        if nombre in BOTONES and BOTONES[nombre][0].collidepoint(pos):
            return nombre
    if "cruz" in visibles:
        for nombre, (rect, _) in CRUZ.items():
            if rect.inflate(16, 16).collidepoint(pos):
                return "cruz_" + nombre
    return None


def _soltar(salida):
    global _boton_apretado, dedo_en_boton
    if _boton_apretado:
        if _boton_apretado.startswith("cruz_"):
            tecla = CRUZ[_boton_apretado[5:]][1]
            teclas_mantenidas.discard(tecla)
            salida.append(_tecla(tecla, False))
        elif BOTONES[_boton_apretado][2] == "mantener":
            tecla = controles.TECLAS[BOTONES[_boton_apretado][3]]
            teclas_mantenidas.discard(tecla)
            salida.append(_tecla(tecla, False))
    _boton_apretado = None
    dedo_en_boton = False


def traducir(eventos, dt):
    """Convierte toques sobre los botones en teclas. Los demás eventos pasan igual."""
    global _boton_apretado, dedo_en_boton, _arrastre, _largo, _reloj
    _reloj = pygame.time.get_ticks() / 1000.0
    salida = []
    if not activo():
        for ev in eventos:
            if ev.type == pygame.KEYDOWN and ev.key == getattr(pygame, "K_AC_BACK", -1):
                ev = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode="", scancode=0)
            salida.append(ev)
        return salida
    visibles = _visibles()
    if _boton_apretado and not _boton_apretado.startswith("cruz_") and _boton_apretado not in visibles:
        _soltar(salida)
    if _boton_apretado and _boton_apretado.startswith("cruz_") and "cruz" not in visibles:
        _soltar(salida)
    for ev in eventos:
        if ev.type == pygame.KEYDOWN and ev.key == getattr(pygame, "K_AC_BACK", -1):
            salida.append(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE, mod=0, unicode="", scancode=0))
            continue
        if ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1 and not getattr(ev, "tactil", False):
            nombre = _boton_en(ev.pos, visibles)
            if nombre:
                _boton_apretado, dedo_en_boton = nombre, True
                if nombre.startswith("cruz_"):
                    tecla = CRUZ[nombre[5:]][1]
                    teclas_mantenidas.add(tecla)
                    salida.append(_tecla(tecla))
                else:
                    _, _, tipo, accion = BOTONES[nombre]
                    if tipo == "mantener":
                        teclas_mantenidas.add(controles.TECLAS[accion])
                    salida.append(_tecla(accion))
                continue
            _largo = [_reloj, ev.pos]
        elif ev.type == pygame.MOUSEBUTTONUP and ev.button == 1 and not getattr(ev, "tactil", False):
            _largo = None
            if _boton_apretado:
                _soltar(salida)
                continue
        elif ev.type == pygame.MOUSEMOTION and not getattr(ev, "tactil", False):
            if dedo_en_boton:
                continue
            if ev.buttons and ev.buttons[0]:
                _arrastre += ev.rel[0]
                if _largo and (abs(ev.pos[0] - _largo[1][0]) > 15 or abs(ev.pos[1] - _largo[1][1]) > 15):
                    _largo = None
        salida.append(ev)
    # Toque largo = clic derecho (por ejemplo, la compuerta de un ducto en el mapa de ventilación)
    if _largo and _reloj - _largo[0] >= SEGUNDOS_TOQUE_LARGO:
        if "clic_largo" in visibles:
            pos = _largo[1]
            salida.append(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=pos, tactil=True))
            salida.append(pygame.event.Event(pygame.MOUSEBUTTONUP, button=3, pos=pos, tactil=True))
        _largo = None
    return salida


def tomar_arrastre():
    """Cuántos píxeles se arrastró el dedo en horizontal desde la última vez (para girar la vista)."""
    global _arrastre
    valor, _arrastre = _arrastre, 0.0
    return valor


def hay_que_dibujar():
    return bool(_visibles() - {"clic_largo"})


def dibujar(sup):
    global _fuente
    visibles = _visibles()
    if not visibles:
        return
    if _fuente is None:
        _fuente = pygame.font.Font(None, 26)
    capa = pygame.Surface(sup.get_size(), pygame.SRCALPHA)
    for nombre in visibles:
        if nombre not in BOTONES:
            continue
        rect, texto, _, _ = BOTONES[nombre]
        apretado = _boton_apretado == nombre
        pygame.draw.rect(capa, (255, 230, 140, 120) if apretado else (20, 24, 28, 140), rect, border_radius=12)
        pygame.draw.rect(capa, (255, 230, 140, 200), rect, 2, border_radius=12)
        cx = rect.centerx
        if nombre in ("techo", "bajar"):
            cy = rect.centery - 12
            if nombre == "techo":
                punta = [(cx, cy - 12), (cx - 16, cy + 8), (cx + 16, cy + 8)]
            else:
                punta = [(cx, cy + 12), (cx - 16, cy - 8), (cx + 16, cy - 8)]
            pygame.draw.polygon(capa, (255, 240, 200, 220), punta)
            ty = rect.bottom - 30
        else:
            ty = rect.centery - 9
        s_ = _fuente.render(_traducir(texto), True, (255, 245, 220))
        capa.blit(s_, (cx - s_.get_width() // 2, ty))
    if "cruz" in visibles:
        for nombre, (rect, _) in CRUZ.items():
            apretado = _boton_apretado == "cruz_" + nombre
            pygame.draw.rect(capa, (255, 230, 140, 120) if apretado else (20, 24, 28, 110), rect, border_radius=10)
            pygame.draw.rect(capa, (255, 230, 140, 170), rect, 2, border_radius=10)
            cx, cy = rect.center
            puntas = {"arriba": [(cx, cy - 14), (cx - 14, cy + 10), (cx + 14, cy + 10)],
                      "abajo": [(cx, cy + 14), (cx - 14, cy - 10), (cx + 14, cy - 10)],
                      "izquierda": [(cx - 14, cy), (cx + 10, cy - 14), (cx + 10, cy + 14)],
                      "derecha": [(cx + 14, cy), (cx - 10, cy - 14), (cx - 10, cy + 14)]}[nombre]
            pygame.draw.polygon(capa, (255, 240, 200, 220), puntas)
    sup.blit(capa, (0, 0))


def _traducir(texto):
    try:
        import idioma
        return idioma.T(texto)
    except Exception:
        return texto
