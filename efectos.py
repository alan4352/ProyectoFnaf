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
