# -*- coding: utf-8 -*-
"""Efecto de monitor CRT: aberración de color, líneas de escaneo y viñeta."""
import pygame

# Brillo extra del CRT. El efecto viejo triplicaba el brillo sin querer; este valor
# compensa para que la imagen no se vea mucho más oscura que antes. 1.0 = colores reales.
BRILLO_CRT = 1.35
_capas_crt = {}

def _preparar_capas_crt(pantalla):
    """Se arman una sola vez: líneas de escaneo y viñeta (antes se recreaban en cada cuadro)."""
    ancho, alto = pantalla.get_size()
    scan = pygame.Surface((ancho, alto), pygame.SRCALPHA)
    for y in range(0, alto, 3):
        pygame.draw.line(scan, (0, 0, 0, 55), (0, y), (ancho, y), 1)
    # Viñeta redonda: se calcula chica y se agranda suave
    pw, ph = 120, 70
    chica = pygame.Surface((pw, ph), pygame.SRCALPHA)
    for y in range(ph):
        for x in range(pw):
            dx, dy = (x - pw / 2) / (pw / 2), (y - ph / 2) / (ph / 2)
            d = max(0.0, (dx * dx + dy * dy) ** 0.5 - 0.7)
            chica.set_at((x, y), (0, 0, 0, min(130, int(d * 220))))
    _capas_crt["scan"] = scan
    _capas_crt["vin"] = pygame.transform.smoothscale(chica, (ancho, alto))
    _capas_crt["rojo"] = pygame.Surface((ancho, alto))
    _capas_crt["azul"] = pygame.Surface((ancho, alto))

def aplicar_crt(pantalla, intensidad_aberracion=1):
    if not _capas_crt:
        _preparar_capas_crt(pantalla)

    # Aberración cromática real: el canal rojo se corre a la derecha y el azul a la izquierda
    if intensidad_aberracion > 0:
        shift = intensidad_aberracion
        rojo, azul = _capas_crt["rojo"], _capas_crt["azul"]
        rojo.blit(pantalla, (0, 0))
        rojo.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
        azul.blit(pantalla, (0, 0))
        azul.fill((0, 0, 255), special_flags=pygame.BLEND_RGB_MULT)
        pantalla.fill((0, 255, 0), special_flags=pygame.BLEND_RGB_MULT)
        pantalla.blit(rojo, (shift, 0), special_flags=pygame.BLEND_RGB_ADD)
        pantalla.blit(azul, (-shift, 0), special_flags=pygame.BLEND_RGB_ADD)

    if BRILLO_CRT > 1.0:
        extra = pantalla.copy()
        v = int(255 * (BRILLO_CRT - 1.0))
        extra.fill((v, v, v), special_flags=pygame.BLEND_RGB_MULT)
        pantalla.blit(extra, (0, 0), special_flags=pygame.BLEND_RGB_ADD)

    pantalla.blit(_capas_crt["scan"], (0, 0))
    pantalla.blit(_capas_crt["vin"], (0, 0))


# -------------------------------------------------------------
# Efectos animados generados por código (no necesitan imágenes)
# -------------------------------------------------------------
import random as _random


def cortes_glitch(sup, cantidad=8, amplitud=40, rect=None):
    """Corta franjas horizontales de la imagen y las corre de lugar (señal rota)."""
    zona = rect or sup.get_rect()
    for _ in range(cantidad):
        alto = _random.randint(3, 34)
        y = _random.randint(zona.top, max(zona.top, zona.bottom - alto))
        franja = sup.subsurface((zona.x, y, zona.w, alto)).copy()
        dx = _random.randint(-amplitud, amplitud)
        sup.blit(franja, (zona.x + dx, y))
        if _random.random() < 0.3:
            sup.fill(_random.choice([(40, 0, 0), (0, 30, 40), (30, 30, 30)]), (zona.x, y, zona.w, alto),
                     special_flags=pygame.BLEND_RGB_ADD)


def separar_rgb(sup, desplazamiento=8):
    """Separa los canales de color: el rojo se corre a un lado y el cian al otro."""
    rojo = sup.copy()
    rojo.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_MULT)
    sup.fill((0, 255, 255), special_flags=pygame.BLEND_RGB_MULT)
    sup.blit(rojo, (desplazamiento, _random.randint(-2, 2)), special_flags=pygame.BLEND_RGB_ADD)


def linea_tracking(sup, t, rect, velocidad=55.0):
    """Banda de 'tracking' de VHS que baja lentamente por la imagen."""
    alto_banda = 26
    recorrido = rect.h + alto_banda * 2
    y = rect.top - alto_banda + int((t * velocidad) % recorrido)
    for k in range(0, alto_banda, 2):
        fy = y + k
        if rect.top <= fy < rect.bottom - 2:
            dx = int(_random.randint(-6, 6) * (1 - abs(k - alto_banda / 2) / (alto_banda / 2)))
            franja = sup.subsurface((rect.x, fy, rect.w, 2)).copy()
            sup.blit(franja, (rect.x + dx, fy))
            if k % 6 == 0:
                sup.fill((22, 24, 22), (rect.x, fy, rect.w, 1), special_flags=pygame.BLEND_RGB_ADD)
