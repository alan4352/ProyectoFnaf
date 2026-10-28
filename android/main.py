# -*- coding: utf-8 -*-
"""Lanzador del juego en Android.

Android ejecuta este main.py. Arranca el juego (juego.py, que es una copia de fnaf_fabrica.py)
y, si algo falla, muestra el error en la pantalla del celular en vez de cerrarse sin avisar.
Si el juego se cerró de golpe la vez anterior (un error de bajo nivel), lo muestra al abrirlo de nuevo.
"""
import os
import sys
import traceback

# En Android, SDL muestra el acelerómetro como si fuera un mando: se desactiva (movería el cursor solo)
os.environ.setdefault("SDL_ACCELEROMETER_AS_JOYSTICK", "0")

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)
RUTA_REGISTRO = os.path.join(BASE, "registro_error.txt")
ultimas_lineas = []


class _Copia:
    """Guarda las últimas líneas que el juego escribe (para mostrarlas si falla)."""
    def __init__(self, original):
        self.original = original

    def write(self, texto):
        try:
            if self.original:
                self.original.write(texto)
        except Exception:
            pass
        for linea in texto.splitlines():
            if linea.strip():
                ultimas_lineas.append(linea)
        del ultimas_lineas[:-25]

    def flush(self):
        try:
            if self.original:
                self.original.flush()
        except Exception:
            pass


def _leer_anterior():
    try:
        with open(RUTA_REGISTRO, encoding="utf-8", errors="replace") as f:
            return f.read().strip()
    except OSError:
        return ""


_originales = {}


def _guardar_originales():
    """El juego reemplaza algunas funciones de pygame (ver ventana.py): se guardan las de verdad."""
    import pygame
    _originales.update(flip=pygame.display.flip, get=pygame.event.get)


def mostrar_en_pantalla(titulo, texto):
    """Pantalla negra con el error. Se cierra tocando la pantalla."""
    import pygame
    if _originales:
        pygame.display.flip = _originales["flip"]
        pygame.event.get = _originales["get"]
    pygame.init()
    pantalla = pygame.display.get_surface()
    if pantalla is None:
        try:
            pantalla = pygame.display.set_mode((1200, 700), pygame.FULLSCREEN | pygame.SCALED)
        except Exception:
            pantalla = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    ancho, alto = pantalla.get_size()
    fuente = pygame.font.Font(None, max(16, alto // 34))
    lineas = []
    for linea in texto.splitlines():
        while len(linea) > 110:
            lineas.append(linea[:110])
            linea = "    " + linea[110:]
        lineas.append(linea)
    reloj = pygame.time.Clock()
    inicio = pygame.time.get_ticks()
    desde = max(0, len(lineas) - (alto - 90) // fuente.get_linesize())
    while True:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                return
            if (ev.type in (pygame.MOUSEBUTTONDOWN, pygame.KEYDOWN, pygame.FINGERDOWN)
                    and pygame.time.get_ticks() - inicio > 1500):
                return
        pantalla.fill((20, 6, 6))
        pantalla.blit(fuente.render(titulo, True, (255, 120, 100)), (16, 12))
        pantalla.blit(fuente.render("Sacale una captura a esta pantalla y mandala. Tocá para cerrar.", True,
                                    (220, 200, 150)), (16, 12 + fuente.get_linesize()))
        y = 24 + fuente.get_linesize() * 3
        for linea in lineas[desde:]:
            pantalla.blit(fuente.render(linea, True, (235, 235, 235)), (16, y))
            y += fuente.get_linesize()
        pygame.display.flip()
        reloj.tick(20)


anterior = _leer_anterior()
registro = None
try:
    import faulthandler
    registro = open(RUTA_REGISTRO, "w", encoding="utf-8")
    faulthandler.enable(registro)   # Si el juego se cae de golpe, deja acá dónde fue
except Exception:
    pass
sys.stdout = _Copia(sys.stdout)
sys.stderr = _Copia(sys.stderr)

if anterior:
    try:
        mostrar_en_pantalla("EL JUEGO SE CERRÓ DE GOLPE LA VEZ ANTERIOR", anterior)
    except Exception:
        pass

try:
    _guardar_originales()
    import juego  # noqa: F401  (el juego arranca al importarlo)
except SystemExit:
    pass
except BaseException:
    error = traceback.format_exc()
    texto = "\n".join(["Últimos mensajes:"] + ultimas_lineas[-10:] + ["", error])
    try:
        if registro:
            registro.write(texto)
            registro.flush()
    except Exception:
        pass
    try:
        mostrar_en_pantalla("ERROR AL ABRIR EL JUEGO", texto)
    except Exception:
        pass
    # Ya se mostró: que no vuelva a aparecer la próxima vez
    try:
        if registro:
            registro.seek(0)
            registro.truncate()
    except Exception:
        pass
