import sys
import os
import time
import math
import random
import json
import pygame

from recursos import *      # rutas y carga de imágenes/sonidos
from audio import *         # sonidos sintéticos y reales
from guardado import *      # save_data.json
from datos import *         # dificultad, diálogos, cámaras, rutas
from efectos import aplicar_crt, cortes_glitch, separar_rgb, linea_tracking
from historia import *      # textos de la historia: llamadas, cintas, finales
from minijuegos import crear_minijuego, Relato
from progreso import Progreso, LOGROS, NOMBRES_LOGROS, formato_tiempo
from unidad0 import Unidad0, POSICIONES as POS_UNIDAD0, SEGUNDOS_PARA_RECHAZAR
import idioma
import controles as mapa_teclas
import mando
from idioma import T, FuenteTraducible
import historia as historia_es
import historia_en
import minijuegos as modulo_minijuegos

# -------------------------------------------------------------
# Reloj propio del juego: solo avanza mientras el juego no está en pausa,
# y nunca salta más de 0.1 s por cuadro (al arrastrar la ventana o si el juego se traba).
# -------------------------------------------------------------
reloj_juego = 0.0
pausado = False

def tiempo_juego():
    return reloj_juego

# -------------------------------------------------------------
# 0. Configuración de Directorios y Carga Segura de Assets
# -------------------------------------------------------------
# Modo desarrollador: se activa y desactiva escribiendo CODIGO_DESARROLLO en el teclado
# (en cualquier pantalla; conviene hacerlo en el menú). Los atajos están en el panel que aparece.
# Si ponés MODO_DESARROLLO = True, el juego arranca con el modo ya activado.
MODO_DESARROLLO = False
CODIGO_DESARROLLO = "dunmore"
VERSION = "1.1"
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
pygame.mixer.set_num_channels(24)
pygame.mixer.set_reserved(3)
CANAL_AMBIENTE = pygame.mixer.Channel(0)   # Zumbido de fábrica en bucle durante la noche
CANAL_MUSICA = pygame.mixer.Channel(1)     # Música del menú
CANAL_VOZ = pygame.mixer.Channel(2)        # Voz de las llamadas

ANCHO_VENTANA = 1200
ALTO_VENTANA = 700
ANCHO_OFICINA = 1800
ALTO_OFICINA = 700

# Ajustes del jugador (ajustes.json) y ventana con escalado propio (ver ventana.py)
AJUSTES = cargar_ajustes()
mapa_teclas.cargar(AJUSTES)
import audio as modulo_audio
modulo_audio.AJUSTES_AUDIO = AJUSTES
import ventana
pantalla = ventana.iniciar(ANCHO_VENTANA, ALTO_VENTANA, AJUSTES)

def alternar_pantalla_completa():
    AJUSTES["pantalla_completa"] = not AJUSTES["pantalla_completa"]
    ventana.aplicar_modo()
    guardar_ajustes(AJUSTES)
pygame.display.set_caption("FNAF: Industrial Sector (1982)")
_icono = cargar_imagen_opcional("icono.png")
if _icono:
    pygame.display.set_icon(pygame.transform.smoothscale(_icono, (64, 64)))
reloj = pygame.time.Clock()
ventana.reloj = reloj

superficie_crt = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
pantalla_camaras = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))

# -------------------------------------------------------------
# 1. Fuentes Tipográficas
# -------------------------------------------------------------
def cargar_fuente(tamaño, negrita=False):
    for f in ["consolas", "lucidaconsole", "couriernew", "arial"]:
        font_match = pygame.font.match_font(f)
        if font_match:
            try:
                fn = FuenteTraducible(font_match, tamaño)
                fn.set_bold(negrita)
                return fn
            except:
                pass
    fn = FuenteTraducible(None, tamaño)
    fn.set_bold(negrita)
    return fn

fuente_cam = cargar_fuente(13, True)
fuente_pequeña = cargar_fuente(15, True)
fuente_media = cargar_fuente(20, True)
fuente_grande = cargar_fuente(34, True)
fuente_titulo = cargar_fuente(46, True)
fuente_reloj_6am = cargar_fuente(72, True)
fuente_panel = cargar_fuente(18, True)
fuente_llamada = cargar_fuente(16, True)
fuente_8bit = cargar_fuente(14, True)

# Idioma: la interfaz se traduce sola (idioma.py) y la historia sale de historia.py o historia_en.py
CLAVES_HISTORIA = ["INTRO_JUEGO", "TITULOS_NOCHE", "DIALOGOS_NOCHES", "CINTAS", "FINAL_NORMAL", "FINAL_VERDADERO",
                   "FRASES_ALUCINACION", "FINAL_NOCHE6", "LLAMADA_EQUIVOCADA", "CINTA_SECRETA", "CREDITOS"]

def aplicar_idioma():
    idioma.ACTUAL["idioma"] = AJUSTES.get("idioma", "es")
    modulo = historia_en if idioma.ACTUAL["idioma"] == "en" else historia_es
    for clave in CLAVES_HISTORIA:
        globals()[clave] = getattr(modulo, clave)
    modulo_minijuegos.CINTAS = modulo.CINTAS

aplicar_idioma()

# -------------------------------------------------------------
# Pantalla de carga (se ve mientras se generan los sonidos y se cargan las imágenes)
# -------------------------------------------------------------
PASOS_CARGA = 30
_pasos_carga = [0]

def pantalla_de_carga(texto=""):
    _pasos_carga[0] += 1
    frac = min(1.0, _pasos_carga[0] / PASOS_CARGA)
    pantalla.fill((4, 5, 6))
    for txt, fuente, y, color in [("ENSAMBLADORA DUNMORE S.A. PRESENTA", fuente_pequeña, 220, (110, 130, 120)),
                                  ("FNAF: INDUSTRIAL SECTOR", fuente_titulo, 260, (225, 230, 235)),
                                  ("(1982)", fuente_media, 320, (200, 60, 60))]:
        sup = fuente.render(txt, True, color)
        pantalla.blit(sup, (ANCHO_VENTANA // 2 - sup.get_width() // 2, y))
    barra = pygame.Rect(ANCHO_VENTANA // 2 - 220, 410, 440, 10)
    pygame.draw.rect(pantalla, (25, 30, 30), barra)
    pygame.draw.rect(pantalla, (60, 200, 130), (barra.x, barra.y, int(barra.w * frac), barra.h))
    sup = fuente_cam.render(texto.upper(), True, (90, 110, 100))
    pantalla.blit(sup, (ANCHO_VENTANA // 2 - sup.get_width() // 2, 430))
    pygame.event.pump()
    pygame.display.flip()

pantalla_de_carga("INICIANDO")
modulo_audio.al_progreso = lambda nombre: pantalla_de_carga("PREPARANDO SONIDO: " + nombre.replace("_", " "))

# -------------------------------------------------------------
# 2. Generador de Audio Procedural Sintético (WAV en memoria)
# -------------------------------------------------------------
sfx_puerta = sonido("puerta", 0.35, 110, "cuadrada")
sfx_linterna = sonido("linterna", 0.08, 1200, "cuadrada")
sfx_persiana = sonido("persiana", 0.45, 95, "sierra")
sfx_monitor_movimiento = sonido("monitor_movimiento", 0.22, 280, "seno")
sfx_estatica_cctv = sonido("estatica_cctv", 0.18, 0, "ruido", fade=False)
sfx_alarma_error = sonido("alarma_error", 0.4, 880, "cuadrada", mod=8.0)
sfx_reboot_click = sonido("reboot_click", 0.05, 1800, "seno")
sfx_apagon_down = sonido("apagon_down", 1.2, 160, "sierra")
sfx_jumpscare = sonido("jumpscare", 2.2, 180, "ruido", fade=False)
sfx_bobina_cuerda = sonido("bobina_cuerda", 0.12, 600, "sierra")
sfx_lure_audio = sonido("lure_audio", 0.5, 440, "seno", mod=4.0)
sfx_ir_hum = sonido("ir_hum", 0.35, 65, "seno", fade=False)
sfx_ir_lock = sonido("ir_lock", 0.18, 1450, "cuadrada")
sfx_paso_metal = sonido("paso_metal", 0.18, 140, "cuadrada")
sfx_conducto_metal = sonido("conducto_metal", 0.25, 90, "sierra")
sfx_timbre = sonido("timbre", 0.4, 750, "seno", mod=12.0)
sfx_campana_1 = sonido("campana_1", 0.8, 523, "seno")
sfx_campana_2 = sonido("campana_2", 0.8, 659, "seno")
sfx_campana_3 = sonido("campana_3", 1.2, 784, "seno")
sfx_paso_8bit = sonido("paso_8bit", 0.06, 220, "cuadrada")
sfx_respiracion = sonido("respiracion", 0.9, 0, "ruido")          # Penny junto a la puerta
sfx_golpe_techo = sonido("golpe_techo", 0.14, 70, "cuadrada")     # Silas en la rejilla
sfx_golpe_vidrio = sonido("golpe_vidrio", 0.06, 1700, "seno")      # Rusty tocando el vidrio
sfx_respiracion.set_volume(0.35)
sfx_glitch_8bit = sonido("glitch_8bit", 0.3, 0, "ruido")

NOTAS_CAJA_MUSICA = [
  crear_sonido_procedural(0.4, f, "seno") for f in [523, 587, 659, 698, 784, 880]
]

# Gritos de jumpscare (uno por animatrónico) y ambiente
GRITOS = {n: cargar_sonido_opcional(f"grito_{a}") for n, a in
          [("Barnaby", "barnaby"), ("Silas", "silas"), ("Penny", "penny"), ("Rusty Bunny", "bunny")]}
sfx_ambiente = sonido("ambiente", 3.0, 55, "seno", fade=False)
if "ambiente" not in SONIDOS_REALES:
    sfx_ambiente.set_volume(0.12)
musica_menu = cargar_sonido_opcional("musica_menu")
caja_musica = cargar_sonido_opcional("caja_musica")   # Melodía del apagón (si no está, se usan notas sintéticas)
modulo_audio.al_progreso = None
VOCES_LLAMADA = {n: cargar_sonido_opcional(f"llamada_noche_{n}") for n in range(1, 6)}
print(f"[AUDIO] Archivos reales: {', '.join(SONIDOS_REALES) or 'ninguno'}"
      f" | gritos: {sum(1 for g in GRITOS.values() if g)}/4"
      f" | voces: {sum(1 for v in VOCES_LLAMADA.values() if v)}/5"
      f" | música menú: {'sí' if musica_menu else 'no'} | caja de música: {'sí' if caja_musica else 'no'}")

def actualizar_audio_continuo():
    """Arranca o corta el ambiente y la música según lo que esté pasando."""
    g = AJUSTES["vol_general"] / 100.0
    CANAL_AMBIENTE.set_volume(g * AJUSTES["vol_musica"] / 100.0)
    CANAL_MUSICA.set_volume(g * AJUSTES["vol_musica"] / 100.0)
    CANAL_VOZ.set_volume(g * AJUSTES["vol_voces"] / 100.0)
    if estado_actual == ESTADO_AJUSTES:
        return   # En ajustes se deja todo como estaba (música del menú o la noche en pausa)
    en_noche = estado_actual == ESTADO_JUEGO and not juego_terminado and not en_jumpscare and not en_apagon
    if en_noche and not CANAL_AMBIENTE.get_busy():
        CANAL_AMBIENTE.play(sfx_ambiente, loops=-1)
    elif not en_noche and CANAL_AMBIENTE.get_busy():
        CANAL_AMBIENTE.fadeout(400)
    en_menu = estado_actual in (ESTADO_MENU, ESTADO_CUSTOM, ESTADO_ARCHIVO, ESTADO_EXTRAS, ESTADO_LOGROS, ESTADO_RESUMEN)
    if musica_menu and en_menu and not CANAL_MUSICA.get_busy():
        CANAL_MUSICA.play(musica_menu, loops=-1, fade_ms=800)
    elif not en_menu and CANAL_MUSICA.get_busy():
        CANAL_MUSICA.fadeout(600)
    if estado_actual != ESTADO_JUEGO and CANAL_VOZ.get_busy():
        CANAL_VOZ.stop()

# -------------------------------------------------------------
# 3. Guardado y Carga de Progreso (save_data.json)
# -------------------------------------------------------------
datos_guardados = cargar_partida()
noche_desbloqueada = datos_guardados.get("noche_desbloqueada", 1)
juego_completado_5_noches = datos_guardados.get("juego_completado_5_noches", False)
ia_custom = datos_guardados.get("ia_custom", {"Barnaby": 10, "Silas": 10, "Penny": 10, "Rusty Bunny": 10})
record_20_20_20_20 = datos_guardados.get("record_20_20_20_20", False)
evidencias = set(datos_guardados.get("evidencias", []))   # Pruebas encontradas en las cintas (1 a 4)
noche6_desbloqueada = datos_guardados.get("noche6_desbloqueada", False)
noche6_superada = datos_guardados.get("noche6_superada", False)
final_verdadero_visto = datos_guardados.get("final_verdadero_visto", False)
progreso = Progreso(datos_guardados)       # Estadísticas y logros (progreso.py)

def guardar_progreso():
    guardar_partida({
        "noche_desbloqueada": noche_desbloqueada,
        "juego_completado_5_noches": juego_completado_5_noches,
        "ia_custom": ia_custom,
        "record_20_20_20_20": record_20_20_20_20,
        "evidencias": sorted(evidencias),
        "noche6_desbloqueada": noche6_desbloqueada,
        "noche6_superada": noche6_superada,
        "final_verdadero_visto": final_verdadero_visto,
        **progreso.a_dict(),
    })

# -------------------------------------------------------------
# 4. Carga Segura de Sprites y Texturas
# -------------------------------------------------------------
ASSETS = {}
pantalla_de_carga("CARGANDO IMÁGENES")

# Índice de todas las imágenes dentro de assets/ y sus subcarpetas
# (camaras/, jumpscares/, oficina/, sprites/...). Se busca por nombre de archivo,
# así podés reorganizar las carpetas sin tocar el código.

# Fondos: se escalan UNA sola vez al cargar (escalar 2400x1792 en cada cuadro es muy lento).
# La oficina se escala a 1800 de ancho y se recorta en alto; ancla_y elige qué franja se ve.
ANCLA_Y_OFICINA = 0.55
ASSETS["oficina_base"] = escalar_cubriendo(cargar_imagen_opcional("oficina.png", "oficina_base.png", opaca=True), ANCHO_OFICINA, ALTO_OFICINA, ANCLA_Y_OFICINA)
ASSETS["oficina_puerta_abierta"] = escalar_cubriendo(cargar_imagen_opcional("oficina_puerta_abierta.png", opaca=True), ANCHO_OFICINA, ALTO_OFICINA, ANCLA_Y_OFICINA)
ASSETS["techo_rejilla"] = escalar_cubriendo(cargar_imagen_opcional("techo.png", "techo_rejilla.png", opaca=True), ANCHO_VENTANA, ALTO_VENTANA)
ASSETS["periodico_verdadero"] = escalar_cubriendo(cargar_imagen_opcional("periodico_verdadero.png", opaca=True), ANCHO_VENTANA, ALTO_VENTANA)
ASSETS["periodico"] = escalar_cubriendo(cargar_imagen_opcional("periodico.png", opaca=True), ANCHO_VENTANA, ALTO_VENTANA)

for i in range(1, 9):
    ASSETS[f"cam_0{i}"] = escalar_cubriendo(cargar_imagen_opcional(f"cam_0{i}.png", opaca=True), 720, 480)
ASSETS["vent_tunel"] = escalar_cubriendo(cargar_imagen_opcional("vent_tunel.png", opaca=True), 720, 480)
# Opcional: una imagen distinta por ducto (vent_01.png ... vent_04.png). Si falta, se usa vent_tunel.png
for i in range(1, 5):
    ASSETS[f"vent_0{i}"] = escalar_cubriendo(cargar_imagen_opcional(f"vent_0{i}.png", opaca=True), 720, 480)
ASSETS["vent_bloqueada"] = escalar_cubriendo(cargar_imagen_opcional("vent_bloqueada.png", opaca=True), 720, 480)

# Jumpscares a pantalla completa (un poco más grandes para poder hacer zoom y temblor)
for _nombre, _archivo in JUMPSCARE_ARCHIVOS.items():
    ASSETS[f"jumpscare_{_nombre}"] = escalar_cubriendo(cargar_imagen_opcional(_archivo, opaca=True), int(ANCHO_VENTANA * 1.15), int(ALTO_VENTANA * 1.15))

# Sprites con transparencia
for _clave in ["barnaby_oficina", "barnaby_cam", "silas_techo", "silas_vent",
               "penny_puerta", "penny_cam", "bunny_ventana", "bunny_cam"]:
    ASSETS[_clave] = cargar_imagen_opcional(f"{_clave}.png")

# Animaciones por cuadros: si existen <nombre>_00.png, <nombre>_01.png, ... se reproducen en bucle.
# Sirve para cualquier sprite (barnaby_cam_00.png...) y para los jumpscares (jumpscare_penny_00.png...).
ANIMS = {}

def cargar_cuadros(clave, escalar=None):
    cuadros = []
    while True:
        img = cargar_imagen_opcional(f"{clave}_{len(cuadros):02d}.png", opaca=escalar is not None)
        if img is None:
            break
        cuadros.append(escalar(img) if escalar else img)
    return cuadros

for _clave in ["barnaby_oficina", "barnaby_cam", "silas_techo", "silas_vent",
               "penny_puerta", "penny_cam", "bunny_ventana", "bunny_cam"]:
    _cuadros = cargar_cuadros(_clave)
    if _cuadros:
        ANIMS[_clave] = _cuadros
        ASSETS[_clave] = ASSETS.get(_clave) or _cuadros[0]
for _nombre, _archivo in JUMPSCARE_ARCHIVOS.items():
    _cuadros = cargar_cuadros(_archivo[:-4], lambda im: escalar_cubriendo(im, int(ANCHO_VENTANA * 1.15), int(ALTO_VENTANA * 1.15)))
    if _cuadros:
        ANIMS[f"jumpscare_{_nombre}"] = _cuadros
        ASSETS[f"jumpscare_{_nombre}"] = ASSETS.get(f"jumpscare_{_nombre}") or _cuadros[0]
if ANIMS:
    print("[ASSETS] Animaciones: " + ", ".join(f"{k} ({len(v)} cuadros)" for k, v in ANIMS.items()))

OPCIONALES = {"oficina_puerta_abierta", "periodico_verdadero", "cam_03", "vent_01", "vent_02", "vent_03", "vent_04"}

def sprite(clave, fps=8):
    """Cuadro actual de una animación, o la imagen fija si no tiene cuadros."""
    cuadros = ANIMS.get(clave)
    if cuadros:
        return cuadros[int(tiempo_juego() * fps) % len(cuadros)]
    return ASSETS.get(clave)

def _silueta(img):
    if img is None:
        return None
    s_ = img.copy()
    s_.fill((14, 14, 18, 255), special_flags=pygame.BLEND_RGBA_MULT)
    w, h = s_.get_size()
    for ex in (0.43, 0.57):
        pygame.draw.circle(s_, (230, 240, 255, 255), (int(w * ex), int(h * 0.16)), max(3, w // 60))
    return s_

ASSETS["unidad0"] = _silueta(ASSETS.get("barnaby_cam"))
if ASSETS.get("jumpscare_Barnaby"):
    _js = ASSETS["jumpscare_Barnaby"].copy()
    _js.fill((55, 40, 45), special_flags=pygame.BLEND_RGB_MULT)
    _js.fill((40, 0, 0), special_flags=pygame.BLEND_RGB_ADD)
    ASSETS["jumpscare_Unidad 0"] = _js
OPCIONALES.add("jumpscare_Unidad 0")

_faltan = [k for k, v in ASSETS.items() if v is None and k not in OPCIONALES]
print(f"[ASSETS] Cargados {len(ASSETS) - len(_faltan)}/{len(ASSETS)}. Faltan: {', '.join(_faltan) or 'ninguno'}")

# -------------------------------------------------------------
# 5. Efectos CRT y Post-Procesado
# -------------------------------------------------------------
crt_activo = AJUSTES["crt"]

def aplicar_postprocesado_crt(dt, intensidad_aberracion=1):
    if crt_activo:
        aplicar_crt(pantalla, intensidad_aberracion)

# -------------------------------------------------------------
# 6. Renderizado Auxiliar de Sprites
# -------------------------------------------------------------
def dibujar_sprite_centrado(superficie, img, cx, cy, escala=1.0, brillo=255, vivo=False):
    """vivo=True: leve "respiración" y tirones de señal ocasionales (para cámaras)."""
    if img and vivo:
        t = tiempo_juego()
        escala *= 1.0 + 0.012 * math.sin(t * 2.3 + cx * 0.05)
        if random.random() < 0.035:
            cx += random.randint(-7, 7)
            cy += random.randint(-3, 3)
    if img:
        w = int(img.get_width() * escala)
        h = int(img.get_height() * escala)
        escalada = pygame.transform.scale(img, (w, h))
        if brillo < 255:
            escalada.set_alpha(brillo)
        superficie.blit(escalada, (cx - w // 2, cy - h // 2))
    else:
        radio = int(45 * escala)
        color = (min(255, brillo), min(120, brillo // 2), 40)
        pygame.draw.circle(superficie, color, (cx, cy), radio)
        pygame.draw.circle(superficie, (255, 255, 255), (cx - 12, cy - 10), int(8 * escala))
        pygame.draw.circle(superficie, (255, 255, 255), (cx + 12, cy - 10), int(8 * escala))

# -------------------------------------------------------------
# 7. Variables de Timers y Sonidos Continuos
# -------------------------------------------------------------
tiempo_ultimo_hum_ir = 0.0
anomalia_detectada_previa = False
tiempo_ultimo_hum_amb = 0.0

# -------------------------------------------------------------
# 8. Componentes Visuales Detallados y Texturas Industriales
# -------------------------------------------------------------
def dibujar_boton_industrial(superficie, x, y, ancho, alto, activo, color_luz, etiqueta=""):
    sombra = pygame.Surface((ancho + 8, alto + 8), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, 150), (0, 0, ancho + 8, alto + 8), border_radius=5)
    superficie.blit(sombra, (x - 2, y - 2))

    rect_caja = pygame.Rect(x, y, ancho, alto)
    pygame.draw.rect(superficie, (26, 29, 32), rect_caja, border_radius=4)
    pygame.draw.rect(superficie, (48, 52, 56), (x + 2, y + 2, ancho - 4, alto - 4), border_radius=3)
    pygame.draw.rect(superficie, (18, 20, 22), rect_caja, 2, border_radius=4)

    for cx, cy in [(x + 4, y + 4), (x + ancho - 5, y + 4), (x + 4, y + alto - 5), (x + ancho - 5, y + alto - 5)]:
        pygame.draw.circle(superficie, (50, 42, 35), (cx, cy), 2)
        pygame.draw.circle(superficie, (12, 14, 15), (cx, cy), 1)

    r_btn = pygame.Rect(x + 7, y + 7, ancho - 14, alto - 14)
    if activo:
        pygame.draw.rect(superficie, (15, 17, 20), r_btn, border_radius=3)
        pygame.draw.rect(superficie, color_luz, (r_btn.x + 2, r_btn.y + 2, r_btn.width - 4, r_btn.height - 4), border_radius=2)
        glow = pygame.Surface((ancho + 16, alto + 16), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*color_luz, 50), (ancho // 2 + 8, alto // 2 + 8), ancho // 2 + 6)
        superficie.blit(glow, (x - 8, y - 8))
    else:
        pygame.draw.rect(superficie, (14, 16, 18), r_btn, border_radius=3)
        dim_color = (max(8, color_luz[0] // 6), max(8, color_luz[1] // 6), max(8, color_luz[2] // 6))
        pygame.draw.rect(superficie, dim_color, (r_btn.x + 2, r_btn.y + 2, r_btn.width - 4, r_btn.height - 4), border_radius=2)
        pygame.draw.line(superficie, (75, 80, 85), (r_btn.left + 2, r_btn.top + 2), (r_btn.right - 4, r_btn.top + 2), 1)

    if etiqueta:
        txt = fuente_cam.render(etiqueta, True, (160, 175, 180))
        superficie.blit(txt, (x + ancho // 2 - txt.get_width() // 2, y + alto + 4))

def dibujar_puerta_blindada(superficie, rect):
    sombra = pygame.Surface((rect.width + 20, rect.height + 20), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, 215), (0, 0, rect.width + 20, rect.height + 20), border_radius=6)
    superficie.blit(sombra, (rect.x - 10, rect.y - 10))

    pygame.draw.rect(superficie, (26, 28, 30), rect)
    pygame.draw.rect(superficie, (45, 48, 52), (rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8))
    pygame.draw.rect(superficie, (14, 15, 17), rect, 3)

    for y_div in range(rect.top + 40, rect.bottom - 60, 75):
        pygame.draw.rect(superficie, (32, 35, 38), (rect.left + 8, y_div, rect.width - 16, 26))
        pygame.draw.line(superficie, (65, 70, 76), (rect.left + 8, y_div), (rect.right - 8, y_div), 1)
        pygame.draw.line(superficie, (12, 13, 15), (rect.left + 8, y_div + 26), (rect.right - 8, y_div + 26), 2)

        for rx in [rect.left + 18, rect.left + 48, rect.right - 50, rect.right - 20]:
            pygame.draw.circle(superficie, (60, 65, 70), (rx, y_div + 13), 4)
            pygame.draw.circle(superficie, (15, 17, 18), (rx, y_div + 13), 2)

    alto_franja = 48
    y_franja = rect.bottom - alto_franja - 8
    r_franja = pygame.Rect(rect.left + 8, y_franja, rect.width - 16, alto_franja)
    pygame.draw.rect(superficie, (170, 135, 25), r_franja)
    for fx in range(r_franja.left - 40, r_franja.right + 40, 28):
        pts = [
          (fx, r_franja.bottom),
          (fx + 14, r_franja.bottom),
          (fx + 28, r_franja.top),
          (fx + 14, r_franja.top)
        ]
        pygame.draw.polygon(superficie, (24, 25, 26), pts)
    pygame.draw.rect(superficie, (14, 15, 16), r_franja, 2)

    r_tag = pygame.Rect(rect.centerx - 110, rect.top + 160, 220, 36)
    pygame.draw.rect(superficie, (16, 17, 19), r_tag, border_radius=3)
    col_alerta = (200, 50, 50) if int(tiempo_juego() * 3) % 2 == 0 else (110, 25, 25)
    pygame.draw.rect(superficie, col_alerta, r_tag, 2, border_radius=3)
    txt_lock = fuente_pequeña.render("SECTOR 01 // COMPUERTA SELLADA", True, (230, 200, 200))
    superficie.blit(txt_lock, (r_tag.centerx - txt_lock.get_width() // 2, r_tag.centery - txt_lock.get_height() // 2))

def dibujar_ventilacion_techo_cerrada(superficie, rect):
    sombra_t = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
    pygame.draw.rect(sombra_t, (0, 0, 0, 220), (0, 0, rect.width + 40, rect.height + 40), border_radius=12)
    superficie.blit(sombra_t, (rect.x - 20, rect.y - 20))

    pygame.draw.rect(superficie, (24, 27, 30), rect, border_radius=8)
    pygame.draw.rect(superficie, (42, 47, 52), (rect.x + 8, rect.y + 8, rect.width - 16, rect.height - 16), border_radius=6)
    pygame.draw.rect(superficie, (12, 14, 15), rect, 5, border_radius=8)

    for y_lama in range(rect.top + 24, rect.bottom - 30, 28):
        r_lama = pygame.Rect(rect.left + 20, y_lama, rect.width - 40, 20)
        pygame.draw.rect(superficie, (34, 38, 42), r_lama)
        pygame.draw.line(superficie, (68, 75, 82), (r_lama.left, r_lama.top), (r_lama.right, r_lama.top), 2)
        pygame.draw.line(superficie, (12, 14, 15), (r_lama.left, r_lama.bottom), (r_lama.right, r_lama.bottom), 2)
        pygame.draw.circle(superficie, (75, 80, 85), (r_lama.left + 10, r_lama.centery), 3)
        pygame.draw.circle(superficie, (12, 14, 16), (r_lama.left + 10, r_lama.centery), 1)
        pygame.draw.circle(superficie, (75, 80, 85), (r_lama.right - 10, r_lama.centery), 3)
        pygame.draw.circle(superficie, (12, 14, 16), (r_lama.right - 10, r_lama.centery), 1)

    for step_x in range(rect.left + 30, rect.right - 15, 45):
        pygame.draw.circle(superficie, (70, 75, 80), (step_x, rect.top + 14), 3)
        pygame.draw.circle(superficie, (12, 14, 15), (step_x, rect.top + 14), 1)
        pygame.draw.circle(superficie, (70, 75, 80), (step_x, rect.bottom - 14), 3)
        pygame.draw.circle(superficie, (12, 14, 15), (step_x, rect.bottom - 14), 1)

    caja_centro = pygame.Rect(rect.centerx - 140, rect.centery - 35, 280, 70)
    pygame.draw.rect(superficie, (16, 18, 20), caja_centro, border_radius=5)
    col_alerta_techo = (235, 50, 50) if int(tiempo_juego() * 4) % 2 == 0 else (90, 18, 18)
    pygame.draw.rect(superficie, col_alerta_techo, caja_centro, 2, border_radius=5)

    pygame.draw.circle(superficie, col_alerta_techo, (caja_centro.left + 28, caja_centro.centery), 12)
    pygame.draw.circle(superficie, (255, 220, 220), (caja_centro.left + 28, caja_centro.centery), 4)

    txt_s1 = fuente_pequeña.render("SELLADO NEUMÁTICO ACTIVO", True, (255, 140, 140))
    txt_s2 = fuente_cam.render("DRENAJE DE OXÍGENO EN CURSO", True, (200, 210, 220))
    superficie.blit(txt_s1, (caja_centro.left + 50, caja_centro.top + 15))
    superficie.blit(txt_s2, (caja_centro.left + 50, caja_centro.top + 38))

def dibujar_persiana_metalica_industrial(superficie, rect, progreso=1.0):
    if progreso <= 0.0:
        return

    alto_visible = int(rect.height * max(0.0, min(1.0, progreso)))
    rect_visible = pygame.Rect(rect.x, rect.y, rect.width, alto_visible)

    sombra_marco = pygame.Surface((rect_visible.width, rect_visible.height), pygame.SRCALPHA)
    pygame.draw.rect(sombra_marco, (0, 0, 0, 215), (0, 0, rect_visible.width, rect_visible.height))
    superficie.blit(sombra_marco, (rect_visible.x, rect_visible.y))

    pygame.draw.rect(superficie, (32, 35, 38), rect_visible)

    ancho_guia = 18
    pygame.draw.rect(superficie, (20, 22, 24), (rect.left, rect.top, ancho_guia, alto_visible))
    pygame.draw.rect(superficie, (20, 22, 24), (rect.right - ancho_guia, rect.top, ancho_guia, alto_visible))
    pygame.draw.rect(superficie, (10, 12, 14), (rect.left, rect.top, ancho_guia, alto_visible), 2)
    pygame.draw.rect(superficie, (10, 12, 14), (rect.right - ancho_guia, rect.top, ancho_guia, alto_visible), 2)

    paso_lama = 20
    for y_lama in range(rect.top + 2, rect_visible.bottom - 12, paso_lama):
        r_lama = pygame.Rect(rect.left + ancho_guia, y_lama, rect.width - (ancho_guia * 2), paso_lama - 2)
        pygame.draw.rect(superficie, (46, 50, 54), r_lama)
        pygame.draw.line(superficie, (74, 80, 86), (r_lama.left, r_lama.top), (r_lama.right, r_lama.top), 1)
        pygame.draw.line(superficie, (14, 16, 18), (r_lama.left, r_lama.bottom), (r_lama.right, r_lama.bottom), 2)

        if (y_lama // paso_lama) % 4 == 0:
            pygame.draw.line(superficie, (65, 45, 30), (r_lama.left + 40, r_lama.top + 4), (r_lama.left + 95, r_lama.top + 4), 2)
        elif (y_lama // paso_lama) % 7 == 0:
            pygame.draw.line(superficie, (70, 42, 25), (r_lama.right - 120, r_lama.top + 5), (r_lama.right - 50, r_lama.top + 5), 2)

    if alto_visible >= 32:
        viga_inf = pygame.Rect(rect.left + ancho_guia - 4, rect_visible.bottom - 32, rect.width - (ancho_guia * 2) + 8, 30)
        pygame.draw.rect(superficie, (24, 26, 28), viga_inf)
        pygame.draw.rect(superficie, (10, 12, 14), viga_inf, 2)
        pygame.draw.rect(superficie, (48, 52, 56), (viga_inf.centerx - 35, viga_inf.top + 8, 70, 14), border_radius=3)
        pygame.draw.rect(superficie, (14, 16, 18), (viga_inf.centerx - 30, viga_inf.top + 10, 60, 10), border_radius=2)

    if progreso >= 0.85:
        txt_stencil = fuente_pequeña.render("[PERSIANA CERRADA // RESISTENCIA MECÁNICA]", True, (180, 150, 60))
        superficie.blit(txt_stencil, (rect.centerx - txt_stencil.get_width() // 2, rect.top + rect.height // 2 - 10))

def dibujar_compuerta_ducto_remota(superficie, rect):
    sombra = pygame.Surface((rect.width + 16, rect.height + 16), pygame.SRCALPHA)
    pygame.draw.rect(sombra, (0, 0, 0, 195), (0, 0, rect.width + 16, rect.height + 16), border_radius=6)
    superficie.blit(sombra, (rect.x - 8, rect.y - 8))

    pygame.draw.rect(superficie, (26, 29, 32), rect, border_radius=3)
    pygame.draw.rect(superficie, (12, 14, 16), rect, 3, border_radius=3)

    paso = 22
    for y in range(rect.top + 8, rect.bottom - 35, paso):
        r_l = pygame.Rect(rect.left + 14, y, rect.width - 28, paso - 3)
        pygame.draw.rect(superficie, (40, 44, 48), r_l)
        pygame.draw.line(superficie, (68, 74, 80), (r_l.left, r_l.top), (r_l.right, r_l.top), 1)
        pygame.draw.line(superficie, (14, 16, 18), (r_l.left, r_l.bottom), (r_l.right, r_l.bottom), 2)

    r_hz = pygame.Rect(rect.left + 14, rect.bottom - 30, rect.width - 28, 22)
    pygame.draw.rect(superficie, (175, 140, 25), r_hz)
    for hx in range(r_hz.left - 20, r_hz.right + 20, 22):
        pts = [
          (hx, r_hz.bottom),
          (hx + 10, r_hz.bottom),
          (hx + 18, r_hz.top),
          (hx + 8, r_hz.top)
        ]
        pygame.draw.polygon(superficie, (22, 23, 25), pts)
    pygame.draw.rect(superficie, (14, 15, 16), r_hz, 2)

    caja_aviso = pygame.Rect(rect.centerx - 120, rect.centery - 22, 240, 44)
    pygame.draw.rect(superficie, (14, 16, 18), caja_aviso, border_radius=3)
    col_borde = (220, 50, 50) if int(tiempo_juego() * 3) % 2 == 0 else (100, 20, 20)
    pygame.draw.rect(superficie, col_borde, caja_aviso, 2, border_radius=3)
    txt_1 = fuente_cam.render("COMPUERTA CERRADA REMOTAMENTE", True, (255, 110, 110))
    txt_2 = fuente_cam.render("[FLUIDO BLOQUEADO]", True, (200, 210, 220))
    superficie.blit(txt_1, (caja_aviso.centerx - txt_1.get_width() // 2, caja_aviso.top + 7))
    superficie.blit(txt_2, (caja_aviso.centerx - txt_2.get_width() // 2, caja_aviso.top + 23))

def dibujar_plano_minimapa(superficie, rect_mapa, es_ventilacion):
    for gx in range(rect_mapa.left + 15, rect_mapa.right, 25):
        pygame.draw.line(superficie, (16, 24, 20), (gx, rect_mapa.top + 4), (gx, rect_mapa.bottom - 4), 1)
    for gy in range(rect_mapa.top + 15, rect_mapa.bottom, 25):
        pygame.draw.line(superficie, (16, 24, 20), (rect_mapa.left + 4, gy), (rect_mapa.right - 4, gy), 1)

    rect_oficina = pygame.Rect(940, 622, 80, 32)
    pygame.draw.rect(superficie, (20, 35, 28), rect_oficina)
    pygame.draw.rect(superficie, (80, 160, 120), rect_oficina, 2)
    txt_you = fuente_cam.render("OFICINA [TÚ]", True, (130, 240, 180))
    superficie.blit(txt_you, (rect_oficina.centerx - txt_you.get_width() // 2, rect_oficina.centery - 5))

    if not es_ventilacion:
        color_sala = (18, 28, 24)
        color_muro = (45, 85, 68)
        color_pasillo = (35, 65, 52)

        conexiones = [
          ((980, 445), (980, 495)),
          ((980, 495), (900, 535)),
          ((980, 495), (980, 545)),
          ((980, 545), (1060, 535)),
          ((900, 535), (900, 595)),
          ((980, 545), (980, 595)),
          ((1060, 535), (1060, 595)),
          ((900, 595), (945, 635)),
          ((980, 595), (980, 622)),
          ((1060, 595), (1015, 635)),
        ]
        for p1, p2 in conexiones:
            pygame.draw.line(superficie, color_pasillo, p1, p2, 6)
            pygame.draw.line(superficie, color_muro, p1, p2, 2)

        for cam_id, data in CAMARAS_PLANTA.items():
            r = data["rect"]
            sala_rect = r.inflate(14, 10)
            pygame.draw.rect(superficie, color_sala, sala_rect)
            pygame.draw.rect(superficie, color_muro, sala_rect, 1)
    else:
        color_tubo = (110, 65, 25)
        color_borde_t = (190, 115, 45)
        nodos_v = [
          ((917, 446), (1047, 446)),
          ((917, 446), (917, 536)),
          ((1047, 446), (1047, 536)),
          ((917, 536), (965, 622)),
          ((1047, 536), (995, 622)),
        ]
        for p1, p2 in nodos_v:
            pygame.draw.line(superficie, color_tubo, p1, p2, 8)
            pygame.draw.line(superficie, color_borde_t, p1, p2, 2)

    txt_plano = fuente_cam.render("PLANO SECTOR B // NIVEL 1", True, (80, 120, 100))
    superficie.blit(txt_plano, (rect_mapa.left + 10, rect_mapa.top + 8))

# -------------------------------------------------------------
# 9. Estados y Variables de Partida
# -------------------------------------------------------------
ESTADO_MENU = "MENU_PRINCIPAL"
ESTADO_CUSTOM = "CUSTOM_NIGHT_MENU"
ESTADO_JUEGO = "JUGANDO"
ESTADO_VICTORIA = "VICTORIA_6AM"
ESTADO_MINIJUEGO = "MINIJUEGO_8BIT"
ESTADO_PERIODICO = "PANTALLA_PERIODICO"
ESTADO_AJUSTES = "MENU_AJUSTES"
ESTADO_RELATO = "RELATO"
ESTADO_TITULO_NOCHE = "TITULO_NOCHE"
ESTADO_ARCHIVO = "ARCHIVO_1982"
ESTADO_EXTRAS = "EXTRAS"
ESTADO_LOGROS = "LOGROS"
ESTADO_RESUMEN = "RESUMEN_ESTADISTICAS"
ESTADO_CREDITOS = "CREDITOS"
ESTADO_CONTROLES = "CONTROLES"
resumen_volver_a = ESTADO_EXTRAS   # A dónde se va después de la pantalla de estadísticas
creditos_volver_a = ESTADO_EXTRAS
t_creditos = 0.0
ajustes_volver_a = "MENU"     # "MENU" o "PAUSA": a dónde vuelve el menú de ajustes
ajustes_seleccion = 0

tiempo_inicio_periodico = 0.0
final_actual = None            # FINAL_NORMAL o FINAL_VERDADERO (historia.py)
estado_actual = ESTADO_MENU
noche_actual = 1

cam_x = 300
mirando_techo = False
monitor_abierto = False
modo_ventilacion = False
panel_mantenimiento_abierto = False

progreso_monitor = 0.0
DURACION_TRANSICION_MONITOR = 0.18

progreso_persiana = 0.0
VEL_TRANSICION_PERSIANA = 4.0

lure_cooldown = 0.0

bobina_generador = 100.0
bobina_cargando = False
apagon_bobina_activo = False
tiempo_inicio_apagon_bobina = 0.0

camara_seleccionada = "CAM_01"
trampa_ducto = None          # Ducto con la compuerta cerrada (None = ninguna)
trampa_cooldown = 0.0        # Segundos hasta poder volver a cerrar una compuerta
COOLDOWN_TRAMPA = 15.0

# Botones de la pared derecha (coordenadas dentro de la oficina de 1800 px).
# Se usan tanto para dibujarlos como para detectar el clic, así nunca se desalinean.
RECT_BTN_PERSIANA = pygame.Rect(1720, 255, 50, 50)
RECT_BTN_LUZ_DER = pygame.Rect(1720, 330, 50, 50)
RECT_BTN_BOBINA = pygame.Rect(565, 200, 240, 34)  # Botón de la bobina dentro de CAM_08
# Botones de la pared izquierda (más arriba para que no los tape el texto de batería)
RECT_BTN_PUERTA_IZQ = pygame.Rect(40, 300, 50, 50)
RECT_BTN_LUZ_IZQ = pygame.Rect(40, 375, 50, 50)

bateria = 100.0
oxigeno = 100.0
hora = 12
tiempo_inicio = 0.0
DURACION_HORA_SEGUNDOS = 45

puerta_izq_cerrada = False
luz_izq = False
linterna_pasillo = False
persiana_der_sostenida = False
tiempo_inicio_persiana = 0.0
luz_der = False
ventilacion_sellada = False

vision_nocturna_cam = False
carga_ir = 100.0             # La visión nocturna se descarga mientras está prendida
ir_agotado = False           # Si se vacía, hay que esperar a que recupere el 40%
DESCARGA_IR = 16.0           # % por segundo (unos 6 s de uso seguido)
RECARGA_IR = 10.0
ultimo_aviso_sonoro = {}     # Pistas de sonido: último momento en que sonó cada una
glitch_cam_timer = 0.0
progreso_cegado_barnaby = 0.0
calor_linterna = 0.0
linterna_sobrecalentada = False

en_apagon = False
tiempo_inicio_apagon = 0.0
tiempo_ultima_nota_apagon = 0.0
indice_nota_apagon = 0

juego_terminado = False
mensaje_muerte = ""

en_jumpscare = False
animatronico_atacante = ""
tiempo_inicio_jumpscare = 0.0
DURACION_JUMPSCARE = 2.4
intensidad_shake = 0.0

tiempo_inicio_6am = 0.0
campanas_tocadas = [False, False, False]

error_ventilacion = False
error_camaras = False
tiempo_siguiente_fallo = 0.0
reboot_activo = None
reboot_tiempo_inicio = 0.0
DURACION_REBOOT = 3.5


llamada_activa = False
llamada_lista = []            # Líneas de la llamada de esta noche (normalmente DIALOGOS_NOCHES)
llamada_equivocada = False
desafio_elegido = None        # Desafío de Custom Night seleccionado (o None)
modificadores = {}            # Reglas especiales de la noche (desafíos)
puerta_t_cerrada = 0.0
puerta_trabada_hasta = 0.0
fantasma_cam, fantasma_hasta = None, 0.0
unidad0 = Unidad0()
ultimo_aviso_unidad0 = 0.0
llamada_muteada = False
indice_dialogo = 0
tiempo_ultimo_texto = 0.0
tiempo_repique = 0.0

class Animatronico:
    def __init__(self, nombre, ruta, nivel_ia, tiempo_tick, rutas_alternativas=None):
        self.nombre = nombre
        # Si hay rutas alternativas, cada vez que vuelve al inicio elige una al azar
        self.rutas = rutas_alternativas or [ruta]
        self.ruta = ruta
        self.nodo_actual = 0
        self.nivel_ia = nivel_ia
        self.bonus_hora = 0          # Agresividad extra que se gana con las horas (2, 3 y 4 AM)
        self.tiempo_tick = tiempo_tick
        self.ultimo_tick = tiempo_juego()
        self.tiempo_en_ataque = 0.0
        self.pose = 0                # Variante de posición en cámara (cambia en cada movimiento)

    def sala(self):
        return self.ruta[self.nodo_actual]

    def volver_al_inicio(self):
        self.ruta = random.choice(self.rutas)
        self.nodo_actual = 0
        self.tiempo_en_ataque = 0.0
        self.pose = random.randint(0, 2)

    def reiniciar(self, nivel_ia):
        self.volver_al_inicio()
        self.nivel_ia = nivel_ia
        self.bonus_hora = 0
        self.ultimo_tick = tiempo_juego()

    def actualizar(self):
        if self.nivel_ia <= 0 or dev_congelados:
            return

        sala_actual = str(self.ruta[self.nodo_actual])
        if monitor_abierto and progreso_monitor >= 0.95 and vision_nocturna_cam and not error_camaras and (camara_seleccionada in sala_actual):
            self.ultimo_tick = tiempo_juego()
            return

        ahora = tiempo_juego()
        tick_efectivo = self.tiempo_tick
        if self.nombre == "Rusty Bunny" and apagon_bobina_activo:
            tick_efectivo *= 0.5

        if ahora - self.ultimo_tick >= tick_efectivo:
            self.ultimo_tick = ahora
            if random.randint(1, 20) <= min(20, self.nivel_ia + self.bonus_hora):
                self.avanzar()

    def avanzar(self):
        global glitch_cam_timer
        if self.nodo_actual < len(self.ruta) - 1:
            nodo_anterior = self.ruta[self.nodo_actual]
            self.nodo_actual += 1
            self.pose = random.randint(0, 2)
            nodo_nuevo = self.ruta[self.nodo_actual]

            if monitor_abierto and (camara_seleccionada in str(nodo_anterior) or camara_seleccionada in str(nodo_nuevo)):
                glitch_cam_timer = 0.45
                reproducir_sonido(sfx_estatica_cctv, 0.9, 0.9)

            if self.nombre == "Penny":
                reproducir_sonido(sfx_paso_metal, 0.9, 0.1)
                subtitulo("PASOS METÁLICOS", -1)
            elif self.nombre == "Rusty Bunny":
                reproducir_sonido(sfx_paso_metal, 0.1, 0.9)
                subtitulo("PASOS METÁLICOS", 1)
            elif self.nombre == "Silas":
                reproducir_sonido(sfx_conducto_metal, 0.6, 0.6)
                subtitulo("RUIDO EN LOS DUCTOS", 0)
            elif self.nombre == "Barnaby":
                reproducir_sonido(sfx_paso_metal, 0.5, 0.5)
                subtitulo("PASOS PESADOS EN EL PASILLO", 0)

barnaby = Animatronico("Barnaby", ["CAM_01", "CAM_02", "CAM_07_LEJOS", "CAM_07_CERCA", "OFICINA"], 10, 7.5)
silas = Animatronico("Silas", RUTA_SILAS_NORTE, 9, 8.0, [RUTA_SILAS_NORTE, RUTA_SILAS_OESTE])
penny = Animatronico("Penny", ["CAM_01", "CAM_03", "CAM_06", "PUERTA_IZQ", "OFICINA"], 8, 8.5)
bunny = Animatronico("Rusty Bunny", ["CAM_01", "CAM_04", "CAM_05", "CAM_08", "VENTANA_DER", "OFICINA"], 9, 7.8)

def intervalo_fallas(base=(22.0, 40.0)):
    if modificadores.get("fallas_frecuentes"):
        return (base[0] / 2.2, base[1] / 2.2)
    return base

def alternar_puerta():
    """Abre o cierra la compuerta izquierda (con estadísticas y la regla de 'puerta trabada')."""
    global puerta_izq_cerrada, uso_puerta_noche, puerta_t_cerrada
    if not puerta_izq_cerrada and tiempo_juego() < puerta_trabada_hasta:
        reproducir_sonido(sfx_alarma_error, 0.6, 0.1)
        return
    reproducir_sonido(sfx_puerta, 0.9, 0.2)
    puerta_izq_cerrada = not puerta_izq_cerrada
    if puerta_izq_cerrada:
        progreso.sumar("puertas_cerradas")
        uso_puerta_noche = True
        puerta_t_cerrada = 0.0

# -------------------------------------------------------------
# Modo infinito: sin 6 AM. Cada hora suben todos y se recarga parte de la batería.
# -------------------------------------------------------------
INFINITO_IA_INICIAL = 3
INFINITO_SUBE_POR_HORA = 2
INFINITO_RECARGA_POR_HORA = 25
INFINITO_HORA_UNIDAD0 = 4          # Desde esta hora se suma la Unidad 0
infinito_horas = 0
infinito_registrado = False
infinito_record_nuevo = False
infinito_ultimo = 0.0

def TK(plantilla):
    """Traduce un texto de ayuda y le pone las teclas que eligió el jugador ({puerta}, {bajar_alt}...)."""
    return T(plantilla).format(**mapa_teclas.etiquetas())

def es_infinito():
    return noche_actual == "INFINITO"

def nombre_noche():
    return "MODO INFINITO" if es_infinito() else f"NOCHE {noche_actual}"

def avanzar_hora_infinito():
    """Se llama al pasar cada hora en el modo infinito."""
    global infinito_horas, bateria, oxigeno
    infinito_horas += 1
    for a in (barnaby, silas, penny, bunny):
        a.nivel_ia = min(20, a.nivel_ia + INFINITO_SUBE_POR_HORA)
    if not en_apagon:
        bateria = min(100.0, bateria + INFINITO_RECARGA_POR_HORA)
    oxigeno = min(100.0, oxigeno + 30)
    reproducir_sonido(sfx_campana_1, 0.5, 0.5)
    subtitulo("CAMPANADA: UNA HORA MÁS", 0, 3.0)
    dif = DIFICULTADES.get(AJUSTES.get("dificultad"), DIFICULTADES["normal"])
    if infinito_horas == INFINITO_HORA_UNIDAD0:
        unidad0.reiniciar(True, dif["limite_unidad0"] * 1.2)
        reproducir_sonido(sfx_estatica_cctv, 0.8, 0.8)
        subtitulo("ALGO NUEVO SE ENCENDIÓ EN LA PLANTA", 0, 4.0)
    elif infinito_horas > INFINITO_HORA_UNIDAD0 and unidad0.activa:
        unidad0.limite = max(5.0, unidad0.limite * 0.92)
    if infinito_horas >= 10:
        progreso.desbloquear("maraton")

def registrar_infinito():
    """Guarda el tiempo resistido en el modo infinito (una vez por intento)."""
    global infinito_registrado, infinito_record_nuevo, infinito_ultimo
    if not es_infinito() or infinito_registrado:
        return
    infinito_registrado = True
    infinito_ultimo = tiempo_juego() - tiempo_inicio
    records = progreso.stats["records_infinito"]
    infinito_record_nuevo = not MODO_DESARROLLO and (not records or infinito_ultimo > max(records))
    if not MODO_DESARROLLO:
        records.append(round(infinito_ultimo, 1))
        records.sort(reverse=True)
        del records[5:]

def texto_tiempo_infinito(segundos):
    horas = int(segundos // DURACION_HORA_SEGUNDOS)
    return f"{horas} H  ({formato_tiempo(segundos)})"

# Parpadeo de la luz de la oficina: más seguido a medida que avanza la noche y baja la batería
parpadeo_luz_hasta = 0.0
parpadeo_luz_proximo = 0.0

def dibujar_parpadeo_luz():
    global parpadeo_luz_hasta, parpadeo_luz_proximo
    ahora_p = tiempo_juego()
    if ahora_p >= parpadeo_luz_proximo:
        horas_noche = (ahora_p - tiempo_inicio) / DURACION_HORA_SEGUNDOS
        espera = max(4.0, 22.0 - horas_noche * 2.5 - (100 - bateria) * 0.08)
        parpadeo_luz_proximo = ahora_p + random.uniform(espera * 0.6, espera * 1.4)
        parpadeo_luz_hasta = ahora_p + random.uniform(0.15, 0.45)
    if ahora_p < parpadeo_luz_hasta and int(ahora_p * 28) % 3 != 0:
        nivel = random.choice([70, 110, 150])
        pantalla.fill((nivel, nivel, nivel), special_flags=pygame.BLEND_RGB_MULT)

# Subtítulos de sonidos (accesibilidad): texto, lado (-1 izquierda, 0 centro, 1 derecha), hasta cuándo
subtitulos_activos = []

def subtitulo(texto, lado=0, segundos=2.5):
    if not AJUSTES.get("subtitulos"):
        return
    fin = tiempo_juego() + segundos
    for item in subtitulos_activos:
        if item[0] == texto:
            item[1], item[2] = lado, fin
            return
    subtitulos_activos.append([texto, lado, fin])

def dibujar_subtitulos():
    ahora_s = tiempo_juego()
    subtitulos_activos[:] = [s_ for s_ in subtitulos_activos if s_[2] > ahora_s][-4:]
    pisos = {-1: 0, 0: 0, 1: 0}
    for texto, lado, fin in reversed(subtitulos_activos):
        i = pisos[lado]
        pisos[lado] += 1
        cuerpo = T(texto)
        etiqueta = ("<<  " + cuerpo) if lado < 0 else ((cuerpo + "  >>") if lado > 0 else cuerpo)
        sup = fuente_pequeña.render(etiqueta, True, (255, 255, 255))
        caja = pygame.Rect(0, 0, sup.get_width() + 24, sup.get_height() + 10)
        caja.centerx = ANCHO_VENTANA // 2 + lado * 260
        caja.bottom = ALTO_VENTANA - 62 - i * (caja.height + 4)
        fondo = pygame.Surface(caja.size, pygame.SRCALPHA)
        fondo.fill((0, 0, 0, 175))
        pantalla.blit(fondo, caja.topleft)
        if fin - ahora_s < 0.4:
            sup.set_alpha(int(255 * (fin - ahora_s) / 0.4))
        pantalla.blit(sup, (caja.x + 12, caja.y + 5))

def comenzar_noche(noche):
    global cam_x, mirando_techo, monitor_abierto, modo_ventilacion, panel_mantenimiento_abierto
    global camara_seleccionada, trampa_ducto, bateria, oxigeno, hora
    global tiempo_inicio, puerta_izq_cerrada, luz_izq, linterna_pasillo
    global persiana_der_sostenida, progreso_persiana, luz_der, ventilacion_sellada
    global juego_terminado, mensaje_muerte, en_jumpscare, animatronico_atacante
    global llamada_activa, llamada_muteada, indice_dialogo, tiempo_ultimo_texto, tiempo_repique
    global estado_actual, noche_actual
    global error_ventilacion, error_camaras, tiempo_siguiente_fallo, reboot_activo
    global en_apagon, tiempo_inicio_apagon, indice_nota_apagon
    global vision_nocturna_cam, glitch_cam_timer, progreso_cegado_barnaby, calor_linterna, linterna_sobrecalentada
    global progreso_monitor, lure_cooldown, bobina_generador, bobina_cargando, apagon_bobina_activo
    global trampa_cooldown, carga_ir, ir_agotado, pausado
    global llamada_lista, llamada_equivocada, modificadores, uso_puerta_noche, puerta_t_cerrada, puerta_trabada_hasta
    global infinito_horas, infinito_registrado, infinito_record_nuevo

    noche_actual = noche
    infinito_horas, infinito_registrado, infinito_record_nuevo = 0, False, False
    subtitulos_activos.clear()
    cam_x = 300
    mirando_techo = False
    monitor_abierto = False
    progreso_monitor = 0.0
    progreso_persiana = 0.0
    modo_ventilacion = False
    panel_mantenimiento_abierto = False
    camara_seleccionada = "CAM_01"
    trampa_ducto = None
    trampa_cooldown = 0.0
    carga_ir = 100.0
    ir_agotado = False
    pausado = False
    ultimo_aviso_sonoro.clear()
    bateria = 100.0
    oxigeno = 100.0
    hora = 12
    tiempo_inicio = tiempo_juego()
    puerta_izq_cerrada = False
    luz_izq = False
    linterna_pasillo = False
    persiana_der_sostenida = False
    luz_der = False
    ventilacion_sellada = False
    en_apagon = False
    tiempo_inicio_apagon = 0.0
    indice_nota_apagon = 0
    juego_terminado = False
    mensaje_muerte = ""
    en_jumpscare = False
    animatronico_atacante = ""

    vision_nocturna_cam = False
    glitch_cam_timer = 0.0
    progreso_cegado_barnaby = 0.0
    calor_linterna = 0.0
    linterna_sobrecalentada = False

    lure_cooldown = 0.0
    bobina_generador = 100.0
    bobina_cargando = False
    apagon_bobina_activo = False

    error_ventilacion = False
    error_camaras = False
    reboot_activo = None
    modificadores = dict(desafio_elegido["mods"]) if (noche == "CUSTOM" and desafio_elegido) else {}
    bateria = float(modificadores.get("bateria_inicial", 100))
    tiempo_siguiente_fallo = tiempo_juego() + random.uniform(*intervalo_fallas())
    uso_puerta_noche = False
    puerta_t_cerrada, puerta_trabada_hasta = 0.0, 0.0

    dif = DIFICULTADES.get(AJUSTES.get("dificultad"), DIFICULTADES["normal"])
    if noche == "CUSTOM":
        difs = desafio_elegido["ia"] if desafio_elegido else ia_custom
    elif noche == "INFINITO":
        difs = {k: INFINITO_IA_INICIAL for k in ("Barnaby", "Silas", "Penny", "Rusty Bunny")}
    else:
        base = DIFICULTAD_NOCHES.get(noche, DIFICULTAD_NOCHES[1])
        difs = {k: (0 if v == 0 else max(1, min(20, round(v * dif["factor_ia"]) + dif["suma_ia"]))) for k, v in base.items()}
    unidad0.reiniciar(noche == 6, dif["limite_unidad0"])

    barnaby.reiniciar(difs["Barnaby"])
    silas.reiniciar(difs["Silas"])
    penny.reiniciar(difs["Penny"])
    bunny.reiniciar(difs["Rusty Bunny"])

    CANAL_VOZ.stop()
    # Secreto: muy rara vez entra una llamada equivocada (noches 2 a 5)
    llamada_equivocada = isinstance(noche, int) and 2 <= noche <= 5 and random.random() < 1 / 12
    llamada_lista = LLAMADA_EQUIVOCADA if llamada_equivocada else DIALOGOS_NOCHES.get(noche, [])
    if llamada_equivocada:
        progreso.desbloquear("numero_equivocado")
    if isinstance(noche, int) and noche in DIALOGOS_NOCHES:
        if VOCES_LLAMADA.get(noche) and not llamada_equivocada:
            CANAL_VOZ.play(VOCES_LLAMADA[noche])
        llamada_activa = True
        llamada_muteada = False
        indice_dialogo = 0
        tiempo_ultimo_texto = tiempo_juego()
        tiempo_repique = tiempo_juego()
    else:
        llamada_activa = False

    estado_actual = ESTADO_JUEGO

def iniciar_jumpscare(nombre, causa):
    global en_jumpscare, animatronico_atacante, tiempo_inicio_jumpscare
    global mensaje_muerte, monitor_abierto, mirando_techo, panel_mantenimiento_abierto, intensidad_shake
    global progreso_monitor
    en_jumpscare = True
    animatronico_atacante = nombre
    tiempo_inicio_jumpscare = tiempo_juego()
    mensaje_muerte = causa
    monitor_abierto = False
    progreso_monitor = 0.0
    mirando_techo = False
    panel_mantenimiento_abierto = False
    intensidad_shake = 30.0
    reproducir_sonido(GRITOS.get(nombre) or sfx_jumpscare)
    CANAL_VOZ.stop()
    if not causa.startswith("PRUEBA DE JUMPSCARE"):
        progreso.muerte("Apagón" if causa.startswith("SIN ENERGÍA") else nombre)
        registrar_infinito()
        guardar_progreso()

# -------------------------------------------------------------
# 10. Cintas de 1982 (minijuegos), relatos y títulos de noche
# -------------------------------------------------------------
CTX_MINIJUEGOS = {
    "fuentes": {"cam": fuente_cam, "8bit": fuente_8bit, "pequeña": fuente_pequeña, "media": fuente_media,
                "grande": fuente_grande, "titulo": fuente_titulo},
    "sonar": lambda clave, vol=0.8: reproducir_sonido({
        "paso": sfx_paso_8bit, "glitch": sfx_glitch_8bit, "ok": sfx_reboot_click, "error": sfx_alarma_error,
        "explosion": sfx_apagon_down, "prueba": sfx_campana_2}.get(clave, sfx_reboot_click), vol, vol),
}
minijuego_actual = None
minijuego_numero = 1
minijuego_origen = "NOCHE"        # "NOCHE" (después de ganar una noche) o "ARCHIVO" (repetición desde el menú)
relato_actual = None
relato_despues = None             # Función que se llama cuando termina el relato
noche_a_presentar = 1
t_titulo_noche = 0.0

def iniciar_minijuego(numero, origen="NOCHE"):
    global estado_actual, minijuego_actual, minijuego_numero, minijuego_origen
    minijuego_numero, minijuego_origen = numero, origen
    minijuego_actual = crear_minijuego(numero, CTX_MINIJUEGOS)
    estado_actual = ESTADO_MINIJUEGO

def fondo_relato_oficina():
    """La oficina, muy oscura, para que el texto de la introducción se lea encima."""
    img = ASSETS.get("oficina_base")
    if not img:
        return None
    fondo = img.copy()
    fondo.fill((34, 36, 38), special_flags=pygame.BLEND_RGB_MULT)
    return fondo

def mostrar_relato(titulo, lineas, despues, color=(90, 220, 140), fondo=None):
    global estado_actual, relato_actual, relato_despues
    relato_actual = Relato(CTX_MINIJUEGOS, titulo, lineas, color, fondo)
    relato_despues = despues
    estado_actual = ESTADO_RELATO

def ir_al_menu():
    global estado_actual
    estado_actual = ESTADO_MENU

def presentar_noche(noche):
    """Pantalla 'NOCHE X' antes de empezar (como en FNAF)."""
    global estado_actual, noche_a_presentar, t_titulo_noche
    noche_a_presentar, t_titulo_noche = noche, tiempo_juego()
    estado_actual = ESTADO_TITULO_NOCHE

def dibujar_titulo_noche():
    pantalla.fill((0, 0, 0))
    t = tiempo_juego() - t_titulo_noche
    alfa = max(0, min(255, int(255 * min(t / 0.6, (3.4 - t) / 0.6))))
    capa = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
    for texto, fuente, y, color in [("12:00 AM", fuente_reloj_6am, 250, (240, 240, 240)),
                                    (f"NOCHE {noche_a_presentar}", fuente_grande, 345, (220, 60, 60)),
                                    (TITULOS_NOCHE.get(noche_a_presentar, ""), fuente_pequeña, 395, (150, 160, 165))]:
        sup = fuente.render(texto, True, color)
        capa.blit(sup, (ANCHO_VENTANA // 2 - sup.get_width() // 2, y))
    capa.set_alpha(alfa)
    pantalla.blit(capa, (0, 0))

def cinta_disponible(n):
    if n == 0:
        return "cinta_cero" in progreso.logros
    return noche_desbloqueada > n or juego_completado_5_noches

def numeros_archivo():
    """Las 4 cintas y, si ya la encontraste, la cinta 0 al final."""
    return (1, 2, 3, 4, 0) if cinta_disponible(0) else (1, 2, 3, 4)

def tiene_prueba_cinta(n):
    return progreso.stats["cinta0_prueba"] if n == 0 else n in evidencias

def botones_archivo():
    numeros = numeros_archivo()
    if len(numeros) == 4:
        return [pygame.Rect(150 + i * 230, 200, 210, 300) for i in range(4)]
    return [pygame.Rect(75 + i * 212, 200, 200, 300) for i in range(len(numeros))]

RECT_ARCHIVO_VOLVER = pygame.Rect(ANCHO_VENTANA // 2 - 140, 590, 280, 50)

def dibujar_archivo():
    pantalla.fill((8, 10, 12))
    txt = fuente_titulo.render("ARCHIVO 1982", True, (220, 230, 235))
    pantalla.blit(txt, (ANCHO_VENTANA // 2 - txt.get_width() // 2, 50))
    sub = fuente_pequeña.render(f"CINTAS RECUPERADAS DEL SISTEMA DE SEGURIDAD  //  PRUEBAS: {len(evidencias)}/4", True, (130, 160, 150))
    pantalla.blit(sub, (ANCHO_VENTANA // 2 - sub.get_width() // 2, 115))
    pos = pygame.mouse.get_pos()
    for n, rect in zip(numeros_archivo(), botones_archivo()):
        abierta = cinta_disponible(n)
        hover = abierta and rect.collidepoint(pos)
        secreta = n == 0
        pygame.draw.rect(pantalla, (28, 34, 32) if hover else ((24, 12, 12) if secreta else (16, 20, 20)), rect, border_radius=8)
        pygame.draw.rect(pantalla, (200, 50, 50) if secreta else ((60, 160, 110) if abierta else (50, 55, 58)), rect, 2, border_radius=8)
        # Cassette
        c = pygame.Rect(rect.x + 30, rect.y + 25, rect.w - 60, 90)
        pygame.draw.rect(pantalla, (40, 40, 44) if abierta else (24, 26, 28), c, border_radius=6)
        pygame.draw.rect(pantalla, ((200, 70, 60) if secreta else (210, 200, 170)) if abierta else (60, 60, 60), (c.x + 12, c.y + 10, c.w - 24, 30))
        for cx in (c.x + 45, c.right - 45):
            pygame.draw.circle(pantalla, (15, 15, 15), (cx, c.y + 65), 13)
            pygame.draw.circle(pantalla, (90, 90, 90), (cx, c.y + 65), 5)
        etiqueta = fuente_cam.render(f"CINTA {n}", True, (40, 30, 20) if abierta else (90, 90, 90))
        pantalla.blit(etiqueta, (c.centerx - etiqueta.get_width() // 2, c.y + 18))
        datos_c = CINTAS[n]
        if abierta:
            nombre = datos_c["personaje"].split(",")[0]
            for k, linea in enumerate([nombre, datos_c["titulo"].split("//")[-1].strip()]):
                s_ = fuente_cam.render(linea, True, (220, 225, 220))
                pantalla.blit(s_, (rect.centerx - s_.get_width() // 2, rect.y + 135 + k * 20))
            if tiene_prueba_cinta(n):
                partes = partir_texto(T(datos_c["prueba"]), fuente_cam, rect.w - 20)
                for k, linea in enumerate(["PRUEBA:"] + partes):
                    s_ = fuente_cam.render(linea, True, (255, 210, 90))
                    pantalla.blit(s_, (rect.centerx - s_.get_width() // 2, rect.y + 195 + k * 18))
            else:
                s_ = fuente_cam.render("PRUEBA: ???", True, (120, 120, 120))
                pantalla.blit(s_, (rect.centerx - s_.get_width() // 2, rect.y + 195))
            s_ = fuente_pequeña.render("[ REPRODUCIR ]", True, (90, 230, 150) if hover else (110, 160, 140))
            pantalla.blit(s_, (rect.centerx - s_.get_width() // 2, rect.bottom - 35))
        else:
            for k, linea in enumerate(["BLOQUEADA", f"Supera la noche {n}"]):
                s_ = fuente_cam.render(linea, True, (110, 110, 110))
                pantalla.blit(s_, (rect.centerx - s_.get_width() // 2, rect.y + 150 + k * 22))
    if len(evidencias) == 4:
        s_ = fuente_pequeña.render("TIENES TODAS LAS PRUEBAS. SOBREVIVE A LA NOCHE 5 PARA USARLAS.", True, (255, 210, 90))
        pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, 530))
    dibujar_boton_menu(RECT_ARCHIVO_VOLVER, "[ESC] VOLVER", (40, 160, 110))

# -------------------------------------------------------------
# 11. Renderizado de Oficina (Normal y En Apagón)
# -------------------------------------------------------------
superficie_oficina = pygame.Surface((ANCHO_OFICINA, ALTO_OFICINA))

def dibujar_oficina():
    luz_izq_efectiva = luz_izq and not apagon_bobina_activo
    luz_der_efectiva = luz_der and not apagon_bobina_activo

    # 1. Base del entorno
    if ASSETS.get("oficina_base"):
        superficie_oficina.blit(ASSETS["oficina_base"], (0, 0))
    else:
        superficie_oficina.fill((18, 20, 22))
        pygame.draw.rect(superficie_oficina, (28, 30, 32), (0, 0, ANCHO_OFICINA, 120))
        pygame.draw.line(superficie_oficina, (45, 35, 25), (0, 120), (ANCHO_OFICINA, 120), 4)

        # Puerta Izquierda Blindada
        rect_puerta = pygame.Rect(95, 235, 275, 450)
        color_fondo = (45, 45, 15) if luz_izq_efectiva else (8, 10, 12)
        pygame.draw.rect(superficie_oficina, color_fondo, rect_puerta)
        pygame.draw.rect(superficie_oficina, (75, 80, 85), rect_puerta, 6)

        # Pasillo Frontal
        rect_pasillo = pygame.Rect(650, 180, 500, 400)
        pygame.draw.rect(superficie_oficina, (5, 6, 8), rect_pasillo)
        pygame.draw.rect(superficie_oficina, (40, 42, 45), rect_pasillo, 4)

        # Escritorio de madera (X: 550 a 1250, superficie en Y: 520)
        pygame.draw.rect(superficie_oficina, (30, 24, 20), (550, 520, 700, 180))
        pygame.draw.line(superficie_oficina, (58, 46, 38), (550, 520), (1250, 520), 4)

        # Pared industrial sólida debajo del ventanal (X: 1200 a 1700, Y: 460 a 700)
        pygame.draw.rect(superficie_oficina, (22, 24, 26), (1190, 460, 520, 240))
        for y_rem in [490, 570, 650]:
            pygame.draw.line(superficie_oficina, (35, 38, 42), (1190, y_rem), (1710, y_rem), 2)
            for x_rem in range(1210, 1700, 70):
                pygame.draw.circle(superficie_oficina, (48, 52, 56), (x_rem, y_rem), 3)

    if ASSETS.get("oficina_base"):
        dibujar_oficina_con_imagen(luz_izq_efectiva, luz_der_efectiva)
        return

    # --- 2. VENTANA INDUSTRIAL HORIZONTAL CON VIDRIO (X: 1220, Y: 220, 480x240 px) ---
    rect_ventana = pygame.Rect(1220, 220, 480, 240)

    # Fondo de la nave contigua visto a través del cristal
    col_fondo_ext = (32, 44, 38) if luz_der_efectiva else (8, 12, 11)
    pygame.draw.rect(superficie_oficina, col_fondo_ext, rect_ventana)

    # Objetos en penumbra detrás del vidrio (estanterías, cajas, maquinaria y vapor)
    alpha_siluetas = 160 if luz_der_efectiva else 50
    s_fondo_ven = pygame.Surface((rect_ventana.width, rect_ventana.height), pygame.SRCALPHA)

    # Estantería metálica con cajas apiladas
    pygame.draw.rect(s_fondo_ven, (14, 20, 18, alpha_siluetas), (30, 45, 110, 175))
    for y_est in range(75, 205, 32):
        pygame.draw.line(s_fondo_ven, (38, 50, 44, alpha_siluetas + 30), (30, y_est), (140, y_est), 2)
        pygame.draw.rect(s_fondo_ven, (26, 36, 32, alpha_siluetas + 15), (45, y_est - 18, 26, 18))
        pygame.draw.rect(s_fondo_ven, (26, 36, 32, alpha_siluetas + 15), (85, y_est - 22, 32, 22))

    # Silueta de engranaje y prensa industrial
    pygame.draw.rect(s_fondo_ven, (16, 24, 20, alpha_siluetas), (210, 75, 150, 145))
    pygame.draw.circle(s_fondo_ven, (28, 40, 34, alpha_siluetas + 20), (285, 105), 32)
    pygame.draw.circle(s_fondo_ven, (10, 14, 12, alpha_siluetas + 40), (285, 105), 14)

    # Ducto superior exterior
    pygame.draw.rect(s_fondo_ven, (22, 30, 26, alpha_siluetas), (0, 18, 480, 14))

    # Tinte verdoso de vidrio de seguridad templado
    tinte_cristal = (60, 125, 95, 35 if not luz_der_efectiva else 70)
    s_fondo_ven.fill(tinte_cristal, special_flags=pygame.BLEND_RGBA_ADD)

    # Reflejos diagonales de cristal translúcido
    pygame.draw.polygon(s_fondo_ven, (255, 255, 255, 24 if not luz_der_efectiva else 52), [
        (70, 0), (130, 0), (30, 240), (0, 240)
    ])
    pygame.draw.polygon(s_fondo_ven, (255, 255, 255, 15 if not luz_der_efectiva else 38), [
        (150, 0), (185, 0), (85, 240), (50, 240)
    ])
    superficie_oficina.blit(s_fondo_ven, (rect_ventana.x, rect_ventana.y))

    # Rusty Bunny asomándose tras el vidrio en la ventana horizontal
    if bunny.nodo_actual == 4 and progreso_persiana < 0.6:
        sp_bunny = sprite("bunny_ventana") or sprite("bunny_cam")
        brillo_b = 255 if luz_der_efectiva else 40
        dibujar_sprite_centrado(superficie_oficina, sp_bunny, 1450, 345, 0.72, brillo_b)

    # Persiana metálica horizontal bajando sobre el ventanal
    if progreso_persiana > 0.0:
        dibujar_persiana_metalica_industrial(superficie_oficina, rect_ventana, progreso_persiana)

    # Parteluces en cruz dividiendo el ventanal en 4 paneles de cristal
    pygame.draw.line(superficie_oficina, (42, 47, 52), (rect_ventana.centerx, rect_ventana.top), (rect_ventana.centerx, rect_ventana.bottom), 8)
    pygame.draw.line(superficie_oficina, (68, 75, 82), (rect_ventana.centerx - 2, rect_ventana.top), (rect_ventana.centerx - 2, rect_ventana.bottom), 2)
    pygame.draw.line(superficie_oficina, (42, 47, 52), (rect_ventana.left, rect_ventana.centery), (rect_ventana.right, rect_ventana.centery), 8)
    pygame.draw.line(superficie_oficina, (68, 75, 82), (rect_ventana.left, rect_ventana.centery - 2), (rect_ventana.right, rect_ventana.centery - 2), 2)

    # Marco exterior perimetral de acero
    pygame.draw.rect(superficie_oficina, (54, 60, 66), rect_ventana, 8)
    pygame.draw.rect(superficie_oficina, (12, 14, 16), rect_ventana, 2)

    # Repisa de hormigón/metal debajo del ventanal
    rect_repisa = pygame.Rect(rect_ventana.left - 10, rect_ventana.bottom - 2, rect_ventana.width + 20, 18)
    pygame.draw.rect(superficie_oficina, (36, 40, 44), rect_repisa)
    pygame.draw.line(superficie_oficina, (74, 80, 86), (rect_repisa.left, rect_repisa.top), (rect_repisa.right, rect_repisa.top), 2)

    # Botones industriales a la derecha del marco horizontal
    dibujar_boton_industrial(superficie_oficina, *RECT_BTN_PERSIANA, persiana_der_sostenida, (240, 160, 30), "PERSIANA")
    dibujar_boton_industrial(superficie_oficina, *RECT_BTN_LUZ_DER, luz_der_efectiva, (255, 240, 80), "LUZ")

    # --- 3. ELEMENTOS DE MANTENIMIENTO Y PUERTA IZQUIERDA ---
    if en_apagon:
        capa_oscura = pygame.Surface((ANCHO_OFICINA, ALTO_OFICINA), pygame.SRCALPHA)
        capa_oscura.fill((0, 0, 0, 225))
        superficie_oficina.blit(capa_oscura, (0, 0))

        t_ap = tiempo_juego() - tiempo_inicio_apagon
        if 2.5 < t_ap < 12.0:
            if random.random() < 0.75:
                sp_b = sprite("barnaby_oficina") or sprite("barnaby_cam")
                dibujar_sprite_centrado(superficie_oficina, sp_b, 900, 360, 0.95, 45)
                pygame.draw.circle(superficie_oficina, (160, 235, 255), (882, 305), 7)
                pygame.draw.circle(superficie_oficina, (160, 235, 255), (918, 305), 7)
                pygame.draw.circle(superficie_oficina, (255, 255, 255), (882, 305), 3)
                pygame.draw.circle(superficie_oficina, (255, 255, 255), (918, 305), 3)
        return

    if apagon_bobina_activo:
        parpadeo_falla = pygame.Surface((ANCHO_OFICINA, ALTO_OFICINA), pygame.SRCALPHA)
        alpha_falla = random.choice([160, 210, 140])
        parpadeo_falla.fill((0, 0, 0, alpha_falla))
        superficie_oficina.blit(parpadeo_falla, (0, 0))

    # Terminal de mantenimiento en pared izquierda
    rect_terminal_pared = pygame.Rect(480, 360, 65, 85)
    s_term = pygame.Surface((rect_terminal_pared.width + 10, rect_terminal_pared.height + 10), pygame.SRCALPHA)
    pygame.draw.rect(s_term, (0, 0, 0, 150), (0, 0, rect_terminal_pared.width + 10, rect_terminal_pared.height + 10), border_radius=4)
    superficie_oficina.blit(s_term, (rect_terminal_pared.x - 3, rect_terminal_pared.y - 3))

    pygame.draw.rect(superficie_oficina, (28, 32, 36), rect_terminal_pared, border_radius=4)
    pygame.draw.rect(superficie_oficina, (48, 55, 62), (rect_terminal_pared.x + 3, rect_terminal_pared.y + 3, rect_terminal_pared.width - 6, rect_terminal_pared.height - 6), border_radius=3)
    pygame.draw.rect(superficie_oficina, (12, 14, 16), rect_terminal_pared, 2, border_radius=4)

    color_luz_term = (240, 50, 50) if (error_ventilacion or error_camaras or apagon_bobina_activo) else (40, 220, 80)
    pygame.draw.circle(superficie_oficina, (15, 18, 20), (512, 385), 10)
    pygame.draw.circle(superficie_oficina, color_luz_term, (512, 385), 7)
    pygame.draw.circle(superficie_oficina, (255, 255, 255), (510, 383), 2)
    txt_lbl_t = fuente_cam.render("MANT.", True, (180, 195, 205))
    superficie_oficina.blit(txt_lbl_t, (494, 408))

    # Puerta Izquierda y Penny
    rect_puerta = pygame.Rect(95, 235, 275, 450)
    if puerta_izq_cerrada:
        dibujar_puerta_blindada(superficie_oficina, rect_puerta)
    else:
        if penny.nodo_actual == 3:
            sp_penny = sprite("penny_puerta") or sprite("penny_cam")
            brillo_p = 255 if luz_izq_efectiva else 35
            dibujar_sprite_centrado(superficie_oficina, sp_penny, 230, 420, 1.0, brillo_p)

    dibujar_boton_industrial(superficie_oficina, *RECT_BTN_PUERTA_IZQ, puerta_izq_cerrada, (240, 40, 40), "PUERTA")
    dibujar_boton_industrial(superficie_oficina, *RECT_BTN_LUZ_IZQ, luz_izq_efectiva, (255, 240, 80), "LUZ")

    # Pasillo Frontal y Barnaby
    if linterna_pasillo:
        if not ASSETS.get("oficina_base"):
            pygame.draw.polygon(superficie_oficina, (85, 80, 60), [(650, 180), (1150, 180), (1050, 500), (750, 500)])
            pygame.draw.rect(superficie_oficina, (38, 38, 32), (750, 240, 300, 260))
        else:
            haz = pygame.Surface((500, 400), pygame.SRCALPHA)
            pygame.draw.ellipse(haz, (255, 245, 190, 65), (30, 20, 440, 360))
            superficie_oficina.blit(haz, (650, 180))

        sp_barnaby = sprite("barnaby_oficina") or sprite("barnaby_cam")
        if barnaby.nodo_actual == 2:
            dibujar_sprite_centrado(superficie_oficina, sp_barnaby, 900, 360, 0.58, 180)
        elif barnaby.nodo_actual == 3:
            dibujar_sprite_centrado(superficie_oficina, sp_barnaby, 900, 370, 1.05, 255)

        if barnaby.nodo_actual in [2, 3]:
            ancho_b = int((progreso_cegado_barnaby / 1.4) * 140)
            pygame.draw.rect(superficie_oficina, (20, 25, 30), (830, 210, 140, 10))
            pygame.draw.rect(superficie_oficina, (255, 220, 60), (830, 210, ancho_b, 10))
            pygame.draw.rect(superficie_oficina, (200, 200, 200), (830, 210, 140, 10), 1)

    # --- 4. TROFEOS APOYADOS EN LA MESA ---
    dibujar_trofeos(520, 0)

def dibujar_trofeos(y_mesa, dx):
    """Trofeos sobre el escritorio. y_mesa = altura de la superficie, dx = corrimiento horizontal."""

    if juego_completado_5_noches or noche_desbloqueada >= 5:
        # Sombra proyectada directamente sobre el tablero
        s_base1 = pygame.Surface((52, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(s_base1, (0, 0, 0, 190), (0, 0, 52, 14))
        superficie_oficina.blit(s_base1, (dx + 718, y_mesa - 5))

        # Base de madera oscura
        pygame.draw.rect(superficie_oficina, (28, 20, 14), (dx + 722, y_mesa - 16, 44, 16), border_radius=2)
        pygame.draw.rect(superficie_oficina, (52, 38, 28), (dx + 724, y_mesa - 14, 40, 12), border_radius=1)
        pygame.draw.rect(superficie_oficina, (190, 195, 205), (dx + 734, y_mesa - 10, 20, 6))

        # Copa de plata
        pygame.draw.rect(superficie_oficina, (120, 128, 136), (dx + 740, y_mesa - 34, 8, 20))
        pygame.draw.line(superficie_oficina, (220, 230, 240), (dx + 742, y_mesa - 34), (dx + 742, y_mesa - 15), 2)
        pygame.draw.polygon(superficie_oficina, (140, 150, 160), [(dx + 732, y_mesa - 56), (dx + 756, y_mesa - 56), (dx + 750, y_mesa - 34), (dx + 738, y_mesa - 34)])
        pygame.draw.polygon(superficie_oficina, (225, 235, 245), [(dx + 737, y_mesa - 56), (dx + 744, y_mesa - 56), (dx + 741, y_mesa - 34)])
        pygame.draw.circle(superficie_oficina, (170, 180, 192), (dx + 744, y_mesa - 58), 13)
        pygame.draw.circle(superficie_oficina, (230, 240, 250), (dx + 744, y_mesa - 58), 8)
        pygame.draw.circle(superficie_oficina, (255, 255, 255), (dx + 742, y_mesa - 60), 2)

    if record_20_20_20_20:
        # Sombra proyectada directamente sobre el tablero
        s_base2 = pygame.Surface((56, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(s_base2, (0, 0, 0, 190), (0, 0, 56, 14))
        superficie_oficina.blit(s_base2, (dx + 790, y_mesa - 5))

        # Base de caoba con placa dorada
        pygame.draw.rect(superficie_oficina, (32, 16, 12), (dx + 794, y_mesa - 18, 48, 18), border_radius=2)
        pygame.draw.rect(superficie_oficina, (58, 30, 22), (dx + 796, y_mesa - 16, 44, 14), border_radius=1)
        pygame.draw.rect(superficie_oficina, (220, 180, 50), (dx + 806, y_mesa - 12, 24, 7))

        # Busto dorado de Barnaby
        cx, cy = dx + 818, y_mesa - 44
        pygame.draw.circle(superficie_oficina, (140, 105, 15), (cx - 15, cy - 14), 7)
        pygame.draw.circle(superficie_oficina, (230, 185, 45), (cx - 15, cy - 14), 4)
        pygame.draw.circle(superficie_oficina, (140, 105, 15), (cx + 15, cy - 14), 7)
        pygame.draw.circle(superficie_oficina, (230, 185, 45), (cx + 15, cy - 14), 4)

        pygame.draw.circle(superficie_oficina, (155, 115, 20), (cx, cy), 18)
        pygame.draw.circle(superficie_oficina, (235, 190, 50), (cx - 3, cy - 3), 14)

        # Sombrero
        pygame.draw.rect(superficie_oficina, (18, 18, 20), (cx - 10, cy - 24, 20, 4))
        pygame.draw.rect(superficie_oficina, (25, 25, 28), (cx - 7, cy - 35, 14, 12))

        # Rostro
        pygame.draw.ellipse(superficie_oficina, (245, 210, 80), (cx - 9, cy + 1, 18, 12))
        pygame.draw.circle(superficie_oficina, (20, 15, 10), (cx, cy + 4), 3)
        pygame.draw.circle(superficie_oficina, (20, 20, 20), (cx - 6, cy - 3), 3)
        pygame.draw.circle(superficie_oficina, (20, 20, 20), (cx + 6, cy - 3), 3)
        pygame.draw.circle(superficie_oficina, (255, 255, 255), (cx - 7, cy - 4), 1)
        pygame.draw.circle(superficie_oficina, (255, 255, 255), (cx + 5, cy - 4), 1)

# --- Zonas de la imagen de oficina (coordenadas ya escaladas a 1800x700) ---
# Si cambiás la imagen o ANCLA_Y_OFICINA, ajustá estos rectángulos.
RECT_PUERTA_IMG = pygame.Rect(172, 25, 285, 660)     # Hueco de la puerta blindada izquierda
CENTRO_PASILLO_IMG = (900, 330)                      # Fondo del pasillo (Barnaby)
Y_MESA_IMG = 628                                     # Superficie del escritorio
DX_TROFEOS_IMG = 175                                 # Trofeos sobre los papeles, lejos del teléfono

# --- Ventana derecha en perspectiva (medida sobre oficina_base.png escalada a 1800x700) ---
# Los bordes izquierdo y derecho son verticales; las líneas de arriba/abajo están inclinadas.
# Cada línea se da como (y en el borde izquierdo, y en el borde derecho).
VENT_X0, VENT_X1 = 1298, 1714
LINEA_TECHO_PERSIANA = (127, 23)    # Donde la persiana sale de la caja
LINEA_BARRA_PERSIANA = (250, 158)   # Borde inferior de la persiana enrollada (lo que ya se ve en la imagen)
LINEA_BASE_VIDRIO = (470, 565)      # Hasta donde baja la persiana al cerrarse
_ALTO_RECT = 130                    # Alto de la textura "enderezada" de las láminas
_FILAS_BARRA = 32                   # Filas de la barra inferior (con la manija)
_ALTO_TEXTURA = 620

def y_en_linea(linea, x):
    t = (x - VENT_X0) / (VENT_X1 - VENT_X0)
    return linea[0] + (linea[1] - linea[0]) * t

def poligono_vidrio():
    return [(VENT_X0, LINEA_BARRA_PERSIANA[0]), (VENT_X1, LINEA_BARRA_PERSIANA[1]),
            (VENT_X1, LINEA_BASE_VIDRIO[1]), (VENT_X0, LINEA_BASE_VIDRIO[0])]

_PERIODO_LAMINA = 14                # Alto de cada lámina en la textura enderezada

def _crear_textura_persiana(fondo):
    """Arma una persiana larga con los colores y el óxido de la persiana enrollada de la imagen.
    Las láminas se dibujan limpias (las de la foto no son paralelas y al estirarlas se ondulan)."""
    ancho = VENT_X1 - VENT_X0
    recta = pygame.Surface((ancho, _ALTO_RECT))
    for i in range(ancho):
        x = VENT_X0 + i
        yt = int(y_en_linea(LINEA_TECHO_PERSIANA, x))
        yb = int(y_en_linea(LINEA_BARRA_PERSIANA, x))
        col = fondo.subsurface((x, yt, 1, yb - yt))
        recta.blit(pygame.transform.smoothscale(col, (1, _ALTO_RECT)), (i, 0))

    # Color de fondo: la foto muy suavizada (solo manchas de óxido y luz, sin las rayas)
    cuerpo = recta.subsurface((0, 30, ancho, _ALTO_RECT - _FILAS_BARRA - 30))
    manchas = pygame.transform.smoothscale(pygame.transform.smoothscale(cuerpo, (max(1, ancho // 12), 3)), (ancho, 96))
    manchas.fill((25, 25, 25), special_flags=pygame.BLEND_RGB_ADD)   # un poco más clara

    alta = pygame.Surface((ancho, _ALTO_TEXTURA))
    y = _ALTO_TEXTURA - _FILAS_BARRA
    while y > 0:
        y -= manchas.get_height()
        alta.blit(manchas, (0, y))

    # Relieve de cada lámina: brillo arriba, sombra en la ranura de abajo
    perfil = [255, 235, 215, 205, 200, 195, 190, 185, 178, 170, 160, 140, 95, 70]
    for fila in range(_ALTO_TEXTURA - _FILAS_BARRA):
        v = perfil[fila % _PERIODO_LAMINA]
        alta.fill((v, v, v), (0, fila, ancho, 1), special_flags=pygame.BLEND_RGB_MULT)
        if fila % _PERIODO_LAMINA == 0:
            alta.fill((28, 28, 26), (0, fila, ancho, 1), special_flags=pygame.BLEND_RGB_ADD)

    # La barra inferior (con la manija) sale tal cual de la foto
    alta.blit(recta.subsurface((0, _ALTO_RECT - _FILAS_BARRA, ancho, _FILAS_BARRA)), (0, _ALTO_TEXTURA - _FILAS_BARRA))
    return alta

def _crear_capa_cadena(fondo, rect=pygame.Rect(1664, 0, 26, 470)):
    """Recorta la cadena que cuelga delante de la ventana para dibujarla por encima de la persiana.
    Se ignoran las filas oscuras que ocupan casi todo el ancho (son ranuras de las láminas, no cadena)."""
    capa = pygame.Surface(rect.size, pygame.SRCALPHA)
    for y in range(rect.h):
        fila = []
        for x in range(rect.w):
            r, g, b, *_ = fondo.get_at((rect.x + x, rect.y + y))
            fila.append((x, r, g, b, 0.3 * r + 0.59 * g + 0.11 * b))
        oscuros = [f for f in fila if f[4] < 45]
        if len(oscuros) > rect.w * 0.6:
            continue
        for x, r, g, b, lum in oscuros:
            capa.set_at((x, y), (r, g, b, 255 if lum < 30 else 150))
    return capa, rect.topleft

TEXTURA_PERSIANA = _crear_textura_persiana(ASSETS["oficina_base"]) if ASSETS.get("oficina_base") else None
CAPA_CADENA = _crear_capa_cadena(ASSETS["oficina_base"]) if ASSETS.get("oficina_base") else None
_cache_persiana = {}

def superficie_persiana(progreso):
    """Persiana bajando en perspectiva. Se cachea en 40 pasos para no recalcular cada cuadro."""
    paso = max(1, min(40, round(progreso * 40)))
    if paso in _cache_persiana:
        return _cache_persiana[paso]
    p = paso / 40
    ancho = VENT_X1 - VENT_X0
    y_min = int(min(LINEA_TECHO_PERSIANA))
    y_max = int(max(LINEA_BASE_VIDRIO))
    sup = pygame.Surface((ancho, y_max - y_min), pygame.SRCALPHA)
    for i in range(ancho):
        x = VENT_X0 + i
        yt = y_en_linea(LINEA_TECHO_PERSIANA, x)
        h_base = y_en_linea(LINEA_BARRA_PERSIANA, x) - yt
        h_full = y_en_linea(LINEA_BASE_VIDRIO, x) - yt
        h = int(h_base + p * (h_full - h_base))
        filas = min(_ALTO_TEXTURA, max(1, int(h * _ALTO_RECT / h_base)))
        col = TEXTURA_PERSIANA.subsurface((i, _ALTO_TEXTURA - filas, 1, filas))
        sup.blit(pygame.transform.smoothscale(col.convert(), (1, h)), (i, int(yt) - y_min))
    _cache_persiana[paso] = (sup, y_min)
    return _cache_persiana[paso]

def dibujar_ventana_con_imagen(luz_der_efectiva):
    poli = poligono_vidrio()
    xs = [p[0] for p in poli]; ys = [p[1] for p in poli]
    bbox = pygame.Rect(min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys))
    poli_local = [(x - bbox.x, y - bbox.y) for x, y in poli]

    # Oscuridad / luz del otro lado del vidrio
    capa = pygame.Surface(bbox.size, pygame.SRCALPHA)
    pygame.draw.polygon(capa, (0, 0, 0, 45) if luz_der_efectiva else (0, 0, 0, 185), poli_local)
    superficie_oficina.blit(capa, bbox.topleft)
    if luz_der_efectiva:
        brillo = pygame.Surface(bbox.size, pygame.SRCALPHA)
        pygame.draw.polygon(brillo, (45, 42, 22, 0), poli_local)
        superficie_oficina.blit(brillo, bbox.topleft, special_flags=pygame.BLEND_RGB_ADD)

    # Rusty Bunny detrás del vidrio (recortado con la forma de la ventana)
    if bunny.nodo_actual == 4 and progreso_persiana < 0.6:
        sp_bunny = sprite("bunny_ventana") or sprite("bunny_cam")
        tmp = pygame.Surface(bbox.size, pygame.SRCALPHA)
        dibujar_sprite_centrado(tmp, sp_bunny, bbox.w // 2 - 10, bbox.h // 2 + 40, 0.68, 255 if luz_der_efectiva else 45)
        mascara = pygame.Surface(bbox.size, pygame.SRCALPHA)
        pygame.draw.polygon(mascara, (255, 255, 255, 255), poli_local)
        tmp.blit(mascara, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        superficie_oficina.blit(tmp, bbox.topleft)

    # Persiana bajando
    if progreso_persiana > 0.0 and TEXTURA_PERSIANA:
        sup, y_min = superficie_persiana(progreso_persiana)
        superficie_oficina.blit(sup, (VENT_X0, y_min))
        if CAPA_CADENA:
            superficie_oficina.blit(*CAPA_CADENA)

def dibujar_oficina_con_imagen(luz_izq_efectiva, luz_der_efectiva):
    # Fondo alternativo opcional: si existe oficina_puerta_abierta.png se usa con la puerta abierta
    if not puerta_izq_cerrada and ASSETS.get("oficina_puerta_abierta"):
        superficie_oficina.blit(ASSETS["oficina_puerta_abierta"], (0, 0))

    # --- VENTANA DERECHA ---
    dibujar_ventana_con_imagen(luz_der_efectiva)

    dibujar_boton_industrial(superficie_oficina, *RECT_BTN_PERSIANA, persiana_der_sostenida, (240, 160, 30), "PERSIANA")
    dibujar_boton_industrial(superficie_oficina, *RECT_BTN_LUZ_DER, luz_der_efectiva, (255, 240, 80), "LUZ")

    # --- APAGÓN TOTAL ---
    if en_apagon:
        capa_oscura = pygame.Surface((ANCHO_OFICINA, ALTO_OFICINA), pygame.SRCALPHA)
        capa_oscura.fill((0, 0, 0, 225))
        superficie_oficina.blit(capa_oscura, (0, 0))
        t_ap = tiempo_juego() - tiempo_inicio_apagon
        if 2.5 < t_ap < 12.0 and random.random() < 0.75:
            sp_b = sprite("barnaby_oficina") or sprite("barnaby_cam")
            dibujar_sprite_centrado(superficie_oficina, sp_b, RECT_PUERTA_IMG.centerx, 400, 1.15, 45)
        return

    if apagon_bobina_activo:
        parpadeo_falla = pygame.Surface((ANCHO_OFICINA, ALTO_OFICINA), pygame.SRCALPHA)
        parpadeo_falla.fill((0, 0, 0, random.choice([160, 210, 140])))
        superficie_oficina.blit(parpadeo_falla, (0, 0))

    # --- TERMINAL DE MANTENIMIENTO (misma zona de clic que antes: 480-545 x 360-445) ---
    rect_terminal_pared = pygame.Rect(480, 360, 65, 85)
    pygame.draw.rect(superficie_oficina, (28, 32, 36), rect_terminal_pared, border_radius=4)
    pygame.draw.rect(superficie_oficina, (48, 55, 62), rect_terminal_pared.inflate(-6, -6), border_radius=3)
    pygame.draw.rect(superficie_oficina, (12, 14, 16), rect_terminal_pared, 2, border_radius=4)
    color_luz_term = (240, 50, 50) if (error_ventilacion or error_camaras or apagon_bobina_activo) else (40, 220, 80)
    pygame.draw.circle(superficie_oficina, (15, 18, 20), (512, 385), 10)
    pygame.draw.circle(superficie_oficina, color_luz_term, (512, 385), 7)
    superficie_oficina.blit(fuente_cam.render("MANT.", True, (180, 195, 205)), (494, 408))
    # Nota pegada en la pared (pista del código secreto)
    nota = pygame.Rect(556, 372, 38, 30)
    pygame.draw.rect(superficie_oficina, (190, 175, 90), nota)
    pygame.draw.rect(superficie_oficina, (120, 105, 50), nota, 1)
    superficie_oficina.blit(fuente_cam.render("0303", True, (60, 40, 30)), (nota.x + 4, nota.y + 8))

    # --- PUERTA IZQUIERDA ---
    # La imagen ya muestra la puerta blindada cerrada. Con la puerta abierta se dibuja el hueco oscuro.
    rp = RECT_PUERTA_IMG
    if not puerta_izq_cerrada and not ASSETS.get("oficina_puerta_abierta"):
        hueco = pygame.Surface(rp.size)
        base = (34, 32, 20) if luz_izq_efectiva else (5, 6, 7)
        hueco.fill(base)
        for i in range(0, rp.height, 4):   # degradé: más oscuro arriba y al fondo
            k = 0.55 + 0.45 * (i / rp.height)
            pygame.draw.line(hueco, tuple(int(c * k) for c in base), (0, i), (rp.width, i), 4)
        superficie_oficina.blit(hueco, rp.topleft)
        pygame.draw.rect(superficie_oficina, (40, 38, 34), rp, 10)
        pygame.draw.rect(superficie_oficina, (12, 12, 12), rp, 3)
    if not puerta_izq_cerrada and penny.nodo_actual == 3:
        sp_penny = sprite("penny_puerta") or sprite("penny_cam")
        superficie_oficina.set_clip(rp)
        dibujar_sprite_centrado(superficie_oficina, sp_penny, rp.centerx + 70, rp.centery + 40, 1.2, 255 if luz_izq_efectiva else 35)
        superficie_oficina.set_clip(None)
    if puerta_izq_cerrada:
        # Luz roja de "sellada" sobre el marco
        col = (230, 40, 40) if int(tiempo_juego() * 3) % 2 == 0 else (110, 20, 20)
        pygame.draw.circle(superficie_oficina, (15, 15, 15), (rp.centerx, rp.top + 18), 11)
        pygame.draw.circle(superficie_oficina, col, (rp.centerx, rp.top + 18), 7)

    dibujar_boton_industrial(superficie_oficina, *RECT_BTN_PUERTA_IZQ, puerta_izq_cerrada, (240, 40, 40), "PUERTA")
    dibujar_boton_industrial(superficie_oficina, *RECT_BTN_LUZ_IZQ, luz_izq_efectiva, (255, 240, 80), "LUZ")

    # --- PASILLO FRONTAL: linterna y Barnaby ---
    px, py = CENTRO_PASILLO_IMG
    if linterna_pasillo:
        haz = pygame.Surface((500, 420), pygame.SRCALPHA)
        pygame.draw.ellipse(haz, (255, 245, 190, 55), (30, 20, 440, 380))
        pygame.draw.ellipse(haz, (255, 245, 190, 35), (110, 80, 280, 260))
        superficie_oficina.blit(haz, (px - 250, py - 200))

        sp_barnaby = sprite("barnaby_oficina") or sprite("barnaby_cam")
        if barnaby.nodo_actual == 2:
            dibujar_sprite_centrado(superficie_oficina, sp_barnaby, px, py + 10, 0.45, 190)
        elif barnaby.nodo_actual == 3:
            dibujar_sprite_centrado(superficie_oficina, sp_barnaby, px, py + 60, 0.95, 255)

        if barnaby.nodo_actual in [2, 3]:
            ancho_b = int((progreso_cegado_barnaby / 1.4) * 140)
            pygame.draw.rect(superficie_oficina, (20, 25, 30), (px - 70, 70, 140, 10))
            pygame.draw.rect(superficie_oficina, (255, 220, 60), (px - 70, 70, ancho_b, 10))
            pygame.draw.rect(superficie_oficina, (200, 200, 200), (px - 70, 70, 140, 10), 1)

    dibujar_trofeos(Y_MESA_IMG, DX_TROFEOS_IMG)


# -------------------------------------------------------------
# 12. Vista Cenital
# -------------------------------------------------------------
def dibujar_vista_techo():
    if ASSETS.get("techo_rejilla"):
        pantalla.blit(ASSETS["techo_rejilla"], (0, 0))
    else:
        pantalla.fill((12, 14, 16))

    rect_escotilla = pygame.Rect(ANCHO_VENTANA//2 - 200, ALTO_VENTANA//2 - 200, 400, 400)
    if ventilacion_sellada:
        dibujar_ventilacion_techo_cerrada(pantalla, rect_escotilla)
    else:
        if not ASSETS.get("techo_rejilla"):
            pygame.draw.rect(pantalla, (4, 5, 7), rect_escotilla)
            for x in range(rect_escotilla.left + 30, rect_escotilla.right, 40):
                pygame.draw.line(pantalla, (65, 70, 75), (x, rect_escotilla.top), (x, rect_escotilla.bottom), 5)

        if silas.sala() == "REJILLA_OFICINA":
            sp_silas_t = sprite("silas_techo") or sprite("silas_vent")
            dibujar_sprite_centrado(pantalla, sp_silas_t, ANCHO_VENTANA//2, ALTO_VENTANA//2 - 20, 1.0, 220)
            txt_aviso = fuente_pequeña.render("¡SILAS EN LA REJILLA DEL TECHO!", True, (255, 90, 90))
            pantalla.blit(txt_aviso, (ANCHO_VENTANA//2 - 130, ALTO_VENTANA//2 + 130))

    txt_info = fuente_media.render(TK("[{sellar}] Sellar Compuerta - [{bajar_alt}] Bajar a la Oficina"), True, (200, 200, 200))
    pantalla.blit(txt_info, (ANCHO_VENTANA//2 - 320, ALTO_VENTANA - 60))

# -------------------------------------------------------------
# 13. Panel de Mantenimiento
# -------------------------------------------------------------
def dibujar_panel_mantenimiento():
    pantalla.fill((10, 14, 18))
    pygame.draw.rect(pantalla, (20, 26, 32), (150, 80, 900, 540), border_radius=10)
    pygame.draw.rect(pantalla, (50, 80, 100), (150, 80, 900, 540), 3)

    txt_t = fuente_grande.render("PANEL DE CONTROL Y MANTENIMIENTO", True, (220, 240, 255))
    txt_sub = fuente_pequeña.render("SUBSISTEMAS INDUSTRIALES // TERMINAL REBOOT", True, (120, 160, 180))
    pantalla.blit(txt_t, (ANCHO_VENTANA//2 - txt_t.get_width()//2, 110))
    pantalla.blit(txt_sub, (ANCHO_VENTANA//2 - txt_sub.get_width()//2, 155))

    rect_box_v = pygame.Rect(220, 210, 760, 80)
    pygame.draw.rect(pantalla, (14, 18, 22), rect_box_v, border_radius=6)
    st_v = "ERROR CRÍTICO // PRESIÓN CERO" if error_ventilacion else "OPERACIONAL (100%)"
    col_v = (240, 50, 50) if error_ventilacion else (40, 220, 80)
    txt_v_lbl = fuente_panel.render("TURBINA DE VENTILACIÓN:", True, (200, 220, 230))
    txt_v_val = fuente_panel.render(st_v, True, col_v)
    pantalla.blit(txt_v_lbl, (240, 238))
    pantalla.blit(txt_v_val, (480, 238))

    btn_reboot_v = pygame.Rect(780, 225, 180, 50)
    pygame.draw.rect(pantalla, (35, 55, 75), btn_reboot_v, border_radius=4)
    txt_b_v = fuente_cam.render("REINICIAR VENT.", True, (255, 255, 255))
    pantalla.blit(txt_b_v, (btn_reboot_v.x + 35, btn_reboot_v.y + 18))

    rect_box_c = pygame.Rect(220, 310, 760, 80)
    pygame.draw.rect(pantalla, (14, 18, 22), rect_box_c, border_radius=6)
    st_c = "SEÑAL PERDIDA // SIN VIDEO" if error_camaras else "OPERACIONAL (100%)"
    col_c = (240, 50, 50) if error_camaras else (40, 220, 80)
    txt_c_lbl = fuente_panel.render("MATRIZ DE CÁMARAS CCTV:", True, (200, 220, 230))
    txt_c_val = fuente_panel.render(st_c, True, col_c)
    pantalla.blit(txt_c_lbl, (240, 338))
    pantalla.blit(txt_c_val, (480, 338))

    btn_reboot_c = pygame.Rect(780, 325, 180, 50)
    pygame.draw.rect(pantalla, (35, 55, 75), btn_reboot_c, border_radius=4)
    txt_b_c = fuente_cam.render("REINICIAR CCTV", True, (255, 255, 255))
    pantalla.blit(txt_b_c, (btn_reboot_c.x + 40, btn_reboot_c.y + 18))

    btn_reboot_all = pygame.Rect(ANCHO_VENTANA//2 - 160, 420, 320, 55)
    pygame.draw.rect(pantalla, (70, 35, 25), btn_reboot_all, border_radius=6)
    pygame.draw.rect(pantalla, (220, 100, 50), btn_reboot_all, 2)
    txt_all = fuente_panel.render("[REINICIAR TODO]", True, (255, 220, 200))
    pantalla.blit(txt_all, (btn_reboot_all.x + 75, btn_reboot_all.y + 16))

    if reboot_activo:
        prog = min(1.0, (tiempo_juego() - reboot_tiempo_inicio) / DURACION_REBOOT)
        rect_barra_bg = pygame.Rect(300, 510, 600, 24)
        pygame.draw.rect(pantalla, (20, 25, 30), rect_barra_bg)
        pygame.draw.rect(pantalla, (40, 180, 240), (300, 510, int(600 * prog), 24))
        pygame.draw.rect(pantalla, (100, 140, 180), rect_barra_bg, 2)
        txt_prog = fuente_cam.render(f"RESTABLECIENDO SISTEMA... {int(prog * 100)}%", True, (220, 240, 255))
        pantalla.blit(txt_prog, (ANCHO_VENTANA//2 - txt_prog.get_width()//2, 540))

    rect_cerrar_panel = pygame.Rect(ANCHO_VENTANA//2 - 110, 575, 220, 35)
    pygame.draw.rect(pantalla, (40, 45, 50), rect_cerrar_panel, border_radius=4)
    txt_ret = fuente_pequeña.render("[M / CLIC] VOLVER A OFICINA", True, (200, 210, 220))
    pantalla.blit(txt_ret, (rect_cerrar_panel.x + 15, rect_cerrar_panel.y + 10))

    return btn_reboot_v, btn_reboot_c, btn_reboot_all, rect_cerrar_panel

# -------------------------------------------------------------
# 14. Renderizado de Cámaras CCTV y Ventilación
# -------------------------------------------------------------
def con_pose(a, x, y, escala):
    dx, dy, f = POSES_CAMARA[a.pose % len(POSES_CAMARA)]
    return x + dx, y + dy, escala * f

def dibujar_feed_ventilacion():
    if trampa_ducto == camara_seleccionada and ASSETS.get("vent_bloqueada"):
        pantalla_camaras.blit(ASSETS["vent_bloqueada"], (100, 80))
    elif ASSETS.get(camara_seleccionada.lower()) or ASSETS.get("vent_tunel"):
        pantalla_camaras.blit(ASSETS.get(camara_seleccionada.lower()) or ASSETS["vent_tunel"], (100, 80))
    else:
        pygame.draw.rect(pantalla_camaras, (22, 25, 27), (100, 80, 720, 480))
        pygame.draw.rect(pantalla_camaras, (8, 10, 11), (300, 200, 320, 240))

    if trampa_ducto == camara_seleccionada and not ASSETS.get("vent_bloqueada"):
        rect_compuerta = pygame.Rect(280, 185, 360, 265)
        dibujar_compuerta_ducto_remota(pantalla_camaras, rect_compuerta)

    silas_en_cam = (
      camara_seleccionada == silas.sala()
    )

    if silas_en_cam and trampa_ducto != camara_seleccionada:
        pos_x, pos_y, esc_s = con_pose(silas, 460, 335, 0.70)
        dibujar_sprite_centrado(pantalla_camaras, sprite("silas_vent"), pos_x, pos_y, esc_s, 225, vivo=True)

def dibujar_sistema_camaras():
    pantalla_camaras.fill((8, 12, 10))

    # --- 1. RECORTE ESTRICTO DENTRO DE LA PANTALLA CCTV (720x480) ---
    rect_pantalla_cctv = pygame.Rect(100, 80, 720, 480)
    pantalla_camaras.set_clip(rect_pantalla_cctv)

    if error_camaras:
        pygame.draw.rect(pantalla_camaras, (12, 8, 8), rect_pantalla_cctv)
        txt_err_cam = fuente_grande.render("[CCTV OFFLINE - SYSTEM ERROR]", True, (240, 50, 50))
        txt_sub_err = fuente_pequeña.render(TK("Fallo en tarjeta de video analógica. Reiniciar desde Panel [{panel}]."), True, (200, 120, 120))
        pantalla_camaras.blit(txt_err_cam, (ANCHO_VENTANA//2 - txt_err_cam.get_width()//2 - 140, 270))
        pantalla_camaras.blit(txt_sub_err, (ANCHO_VENTANA//2 - txt_sub_err.get_width()//2 - 140, 320))
    elif modo_ventilacion:
        dibujar_feed_ventilacion()
    else:
        # Fondo de la cámara escalado con precisión a 720x480
        img_id = camara_seleccionada.lower()
        if ASSETS.get(img_id):
            feed_img = ASSETS[img_id]
            pantalla_camaras.blit(feed_img, (100, 80))
        else:
            pygame.draw.rect(pantalla_camaras, (18, 22, 20), rect_pantalla_cctv)
            if camara_seleccionada == "CAM_03":
                txt_alerta = fuente_grande.render("[SEÑAL PERDIDA - FALLO EN SENSOR CCTV]", True, (160, 60, 60))
                pantalla_camaras.blit(txt_alerta, (140, 260))

        brillo_boost = 35 if vision_nocturna_cam else 0

        # Unidad 0 (noche 6)
        if unidad0.activa and camara_seleccionada == unidad0.sala():
            ux, uy, ue = POS_UNIDAD0[camara_seleccionada]
            dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("unidad0"), ux, uy, ue, 235, vivo=True)
            if unidad0.en_pasillo():
                prog_r = unidad0.mirada / SEGUNDOS_PARA_RECHAZAR
                pygame.draw.rect(pantalla_camaras, (20, 20, 24), (360, 130, 200, 10))
                pygame.draw.rect(pantalla_camaras, (230, 230, 255), (360, 130, int(200 * prog_r), 10))
                lbl_u = fuente_cam.render("NO LE QUITES LOS OJOS DE ENCIMA", True, (230, 230, 255))
                pantalla_camaras.blit(lbl_u, (460 - lbl_u.get_width() // 2, 145))
        # Secreto: una silueta pasa frente a la cámara
        if fantasma_cam == camara_seleccionada and tiempo_juego() < fantasma_hasta:
            sombra = pygame.Surface((90, 230), pygame.SRCALPHA)
            pygame.draw.ellipse(sombra, (0, 0, 0, 170), (25, 0, 40, 46))
            pygame.draw.rect(sombra, (0, 0, 0, 170), (15, 44, 60, 120), border_radius=10)
            pygame.draw.rect(sombra, (0, 0, 0, 170), (22, 160, 18, 70))
            pygame.draw.rect(sombra, (0, 0, 0, 170), (50, 160, 18, 70))
            pantalla_camaras.blit(sombra, (560 + int((fantasma_hasta - tiempo_juego()) * 80), 230))
            if int(tiempo_juego() * 10) % 2 == 0:
                lbl_f = fuente_grande.render("SALIDA", True, (200, 30, 30))
                pantalla_camaras.blit(lbl_f, (460 - lbl_f.get_width() // 2, 470))

        # Posicionamiento calibrado de animatrónicos en el feed
        if camara_seleccionada == "CAM_01":
            if barnaby.nodo_actual == 0:
                dibujar_sprite_centrado(pantalla_camaras, sprite("barnaby_cam"), 460, 340, 0.62, min(255, 230 + brillo_boost), vivo=True)
            if penny.nodo_actual == 0:
                dibujar_sprite_centrado(pantalla_camaras, sprite("penny_cam"), 280, 350, 0.55, min(255, 220 + brillo_boost), vivo=True)
            if bunny.nodo_actual == 0:
                dibujar_sprite_centrado(pantalla_camaras, sprite("bunny_cam"), 640, 340, 0.58, min(255, 225 + brillo_boost), vivo=True)

        elif camara_seleccionada == "CAM_02":
            if barnaby.nodo_actual == 1:
                dibujar_sprite_centrado(pantalla_camaras, sprite("barnaby_cam"), *con_pose(barnaby, 460, 330, 0.65), min(255, 220 + brillo_boost), vivo=True)

        elif camara_seleccionada == "CAM_03":
            if penny.nodo_actual == 1:
                txt_audio = fuente_media.render("[AUDIO: PISADAS METÁLICAS EN CALDERA]", True, (240, 180, 80))
                pantalla_camaras.blit(txt_audio, (170, 360))

        elif camara_seleccionada == "CAM_04":
            if bunny.nodo_actual == 1:
                dibujar_sprite_centrado(pantalla_camaras, sprite("bunny_cam"), *con_pose(bunny, 460, 335, 0.62), min(255, 215 + brillo_boost), vivo=True)

        elif camara_seleccionada == "CAM_05":
            if bunny.nodo_actual == 2:
                dibujar_sprite_centrado(pantalla_camaras, sprite("bunny_cam"), *con_pose(bunny, 460, 335, 0.68), min(255, 220 + brillo_boost), vivo=True)

        elif camara_seleccionada == "CAM_06":
            if penny.nodo_actual == 2:
                dibujar_sprite_centrado(pantalla_camaras, sprite("penny_cam"), *con_pose(penny, 460, 335, 0.68), min(255, 220 + brillo_boost), vivo=True)

        elif camara_seleccionada == "CAM_07":
            if barnaby.nodo_actual in [2, 3]:
                pos_y = 310 if barnaby.nodo_actual == 2 else 345
                escala_b = 0.50 if barnaby.nodo_actual == 2 else 0.75
                brillo_b = 180 if barnaby.nodo_actual == 2 else 245
                dibujar_sprite_centrado(pantalla_camaras, sprite("barnaby_cam"), 460, pos_y, escala_b, min(255, brillo_b + brillo_boost), vivo=True)

        elif camara_seleccionada == "CAM_08":
            if bunny.nodo_actual == 3:
                dibujar_sprite_centrado(pantalla_camaras, sprite("bunny_cam"), *con_pose(bunny, 460, 335, 0.72), min(255, 235 + brillo_boost), vivo=True)

            rect_bobina_box = pygame.Rect(565, 115, 240, 75)
            pygame.draw.rect(pantalla_camaras, (20, 24, 28), rect_bobina_box, border_radius=6)
            pygame.draw.rect(pantalla_camaras, (50, 70, 85), rect_bobina_box, 2)

            col_bob = (50, 220, 90) if bobina_generador > 45 else ((240, 180, 40) if bobina_generador > 20 else (240, 50, 50))
            txt_b_tag = fuente_cam.render("BOBINA GENERADOR AUXILIAR", True, (210, 225, 235))
            pantalla_camaras.blit(txt_b_tag, (575, 123))

            pygame.draw.rect(pantalla_camaras, (10, 12, 14), (575, 145, 220, 18), border_radius=3)
            pygame.draw.rect(pantalla_camaras, col_bob, (575, 145, int(220 * (bobina_generador / 100.0)), 18), border_radius=3)

            rect_btn_bobina = RECT_BTN_BOBINA
            col_btn_bob = (40, 160, 220) if bobina_cargando else (30, 45, 55)
            pygame.draw.rect(pantalla_camaras, col_btn_bob, rect_btn_bobina, border_radius=4)
            txt_btn_c = "[MANTENER: CARGAR BOBINA]" if not bobina_cargando else "[CARGANDO ENERGÍA...]"
            lbl_btn_c = fuente_cam.render(txt_btn_c, True, (255, 255, 255))
            pantalla_camaras.blit(lbl_btn_c, (rect_btn_bobina.centerx - lbl_btn_c.get_width() // 2, rect_btn_bobina.centery - 6))

    # Efecto Visión Nocturna IR dentro del recuadro
    if not error_camaras:
        if vision_nocturna_cam:
            overlay_nv = pygame.Surface((720, 480), pygame.SRCALPHA)
            overlay_nv.fill((45, 210, 95, 45))
            pygame.draw.circle(overlay_nv, (170, 255, 190, 50), (360, 240), 210)
            pantalla_camaras.blit(overlay_nv, (100, 80), special_flags=pygame.BLEND_RGBA_ADD)
            for y_nv in range(80, 560, 6):
                pygame.draw.line(pantalla_camaras, (20, 90, 40), (100, y_nv), (820, y_nv), 1)

            anomalia_detectada = any(camara_seleccionada in str(a.ruta[a.nodo_actual]) for a in [barnaby, silas, penny, bunny])
            global anomalia_detectada_previa
            if anomalia_detectada:
                if not anomalia_detectada_previa:
                    reproducir_sonido(sfx_ir_lock, 0.7, 0.7)
                    anomalia_detectada_previa = True
                txt_nv = fuente_cam.render(f"[IR LOCK // ANOMALÍA PARALIZADA - {int(carga_ir)}%]", True, (255, 75, 75))
                pygame.draw.rect(pantalla_camaras, (255, 60, 60), (310, 190, 300, 280), 2)
            else:
                anomalia_detectada_previa = False
                txt_nv = fuente_cam.render(f"[VISIÓN NOCTURNA IR: {int(carga_ir)}% - CLIC DER / V]", True, (100, 255, 140))
            pantalla_camaras.blit(txt_nv, (805 - txt_nv.get_width(), 92))
        else:
            if ir_agotado:
                txt_nv = fuente_cam.render(f"[IR RECARGANDO... {int(carga_ir)}%]", True, (220, 120, 80))
            else:
                txt_nv = fuente_cam.render(f"[CLIC DER / V] VISIÓN NOCTURNA IR ({int(carga_ir)}%)", True, (120, 150, 135))
            pantalla_camaras.blit(txt_nv, (805 - txt_nv.get_width(), 92))

        if glitch_cam_timer > 0:
            pantalla_camaras.fill((12, 16, 14), rect_pantalla_cctv)
            for _ in range(18):
                gy = random.randint(80, 540)
                gh = random.randint(4, 22)
                c_bar = random.choice([(200, 240, 220), (40, 180, 120), (180, 50, 50)])
                pygame.draw.rect(pantalla_camaras, c_bar, (100, gy, 720, gh))
            txt_mov = fuente_grande.render("[INTERFERENCIA DE MOVIMIENTO]", True, (255, 90, 90))
            pantalla_camaras.blit(txt_mov, (460 - txt_mov.get_width() // 2, 295))

    # Banda de tracking de VHS que recorre la imagen
    if not error_camaras and camara_seleccionada != "CAM_03":
        linea_tracking(pantalla_camaras, tiempo_juego(), rect_pantalla_cctv)

    # Ruido estático analógico dentro del marco
    densidad = 1800 if error_camaras or camara_seleccionada == "CAM_03" else 450
    for _ in range(densidad):
        rx = random.randint(100, 820)
        ry = random.randint(80, 560)
        g = random.randint(25, 160)
        pantalla_camaras.set_at((rx, ry), (g, g, g))

    # --- 2. LIBERAR RECORTE PARA DIBUJAR MARCO, MAPA Y BOTONES EXTERIORES ---
    pantalla_camaras.set_clip(None)

    pygame.draw.rect(pantalla_camaras, (50, 60, 55), (96, 76, 728, 488), 6)

    dict_actual = CAMARAS_VENT if modo_ventilacion else CAMARAS_PLANTA
    nombre_cam = dict_actual.get(camara_seleccionada, {}).get("nombre", "DESCONOCIDO")
    txt_cam_tag = fuente_media.render(f"[{camara_seleccionada}] - {nombre_cam.upper()}", True, (210, 230, 220))
    pantalla_camaras.blit(txt_cam_tag, (110, 520))

    str_tiempo = time.strftime("%Y-%m-%d  %H:%M:%S")
    txt_time = fuente_pequeña.render(f"FEED SURVEILLANCE // {str_tiempo}", True, (150, 170, 160))
    pantalla_camaras.blit(txt_time, (110, 542))

    btn_modo_rect = pygame.Rect(840, 345, 330, 36)
    color_btn_m = (170, 80, 30) if modo_ventilacion else (25, 75, 110)
    pygame.draw.rect(pantalla_camaras, color_btn_m, btn_modo_rect, border_radius=4)
    txt_btn_m = "[VER DUCTOS DE AIRE]" if not modo_ventilacion else "[VER PLANTA DE FÁBRICA]"
    lbl_btn_m = fuente_cam.render(txt_btn_m, True, (255, 255, 255))
    pantalla_camaras.blit(lbl_btn_m, (btn_modo_rect.x + 80, btn_modo_rect.y + 11))

    if modo_ventilacion:
        btn_lure = pygame.Rect(840, 305, 330, 32)
        puede_usar_lure = (lure_cooldown <= 0.0)
        col_lure = (35, 120, 160) if puede_usar_lure else (40, 45, 50)
        pygame.draw.rect(pantalla_camaras, col_lure, btn_lure, border_radius=4)
        txt_lure = "[EMITIR SEÑUELO DE AUDIO]" if puede_usar_lure else f"SEÑUELO RECARGANDO ({int(lure_cooldown)}s)"
        lbl_lure = fuente_cam.render(txt_lure, True, (255, 255, 255) if puede_usar_lure else (160, 160, 160))
        pantalla_camaras.blit(lbl_lure, (btn_lure.centerx - lbl_lure.get_width() // 2, btn_lure.centery - 6))

        if trampa_ducto:
            txt_trampa, col_trampa = f"COMPUERTA CERRADA EN {trampa_ducto.replace('_', ' ')}", (255, 120, 120)
        elif trampa_cooldown > 0.0:
            txt_trampa, col_trampa = f"COMPUERTA REARMANDO ({int(trampa_cooldown) + 1}s)", (160, 160, 160)
        else:
            txt_trampa, col_trampa = "COMPUERTA LISTA: CLIC DER EN UN DUCTO", (120, 230, 160)
        lbl_trampa = fuente_cam.render(txt_trampa, True, col_trampa)
        pantalla_camaras.blit(lbl_trampa, (btn_lure.centerx - lbl_trampa.get_width() // 2, btn_lure.top - 20))

    rect_minimapa = pygame.Rect(840, 390, 330, 275)
    pygame.draw.rect(pantalla_camaras, (10, 15, 12), rect_minimapa)
    dibujar_plano_minimapa(pantalla_camaras, rect_minimapa, modo_ventilacion)
    pygame.draw.rect(pantalla_camaras, (55, 85, 70), rect_minimapa, 3)

    if modo_ventilacion:
        for cam_id, data in CAMARAS_VENT.items():
            btn_r = data["rect"]
            es_activa = (cam_id == camara_seleccionada)
            es_trampa = (cam_id == trampa_ducto)
            color_btn = (180, 40, 40) if es_trampa else ((16, 185, 129) if es_activa else (25, 35, 42))
            pygame.draw.rect(pantalla_camaras, color_btn, btn_r)
            pygame.draw.rect(pantalla_camaras, (255, 255, 255) if es_activa else (70, 90, 100), btn_r, 2)
            lbl = fuente_cam.render(cam_id.replace("_", " "), True, (255, 255, 255) if (es_activa or es_trampa) else (190, 210, 200))
            pantalla_camaras.blit(lbl, (btn_r.x + 8, btn_r.y + 10))
    else:
        for cam_id, data in CAMARAS_PLANTA.items():
            btn_r = data["rect"]
            es_activa = (cam_id == camara_seleccionada)
            color_btn = (16, 185, 129) if es_activa else (20, 28, 24)
            color_borde = (255, 255, 255) if es_activa else (75, 105, 90)
            color_texto = (0, 0, 0) if es_activa else (195, 220, 205)
            pygame.draw.rect(pantalla_camaras, color_btn, btn_r)
            pygame.draw.rect(pantalla_camaras, color_borde, btn_r, 2)
            lbl = fuente_cam.render(cam_id.replace("_", " "), True, color_texto)
            pantalla_camaras.blit(lbl, (btn_r.x + 7, btn_r.y + 8))

# -------------------------------------------------------------
# 15. Jumpscares
# -------------------------------------------------------------
def dibujar_jumpscare(progreso):
    color_fondo = (20, 22, 25) if (int(progreso * 30) % 2 == 0) else (4, 4, 6)
    pantalla.fill(color_fondo)

    cx = ANCHO_VENTANA // 2
    cy = ALTO_VENTANA // 2

    img_js = sprite(f"jumpscare_{animatronico_atacante}", fps=14)
    if img_js:
                # Embestida: arranca un poco lejos y se abalanza contra la cámara en el primer 15%
        t = min(1.0, progreso / 0.15)
        factor = 0.72 + 0.28 * (1 - (1 - t) ** 3)
        w, h = int(img_js.get_width() * factor), int(img_js.get_height() * factor)
        frame = pygame.transform.scale(img_js, (w, h))
        # Parpadeo de señal: algunos cuadros salen oscurecidos
        if random.random() < 0.12:
            frame.fill((90, 90, 90), special_flags=pygame.BLEND_RGB_MULT)
        pantalla.blit(frame, (cx - w // 2, cy - h // 2))
        # Señal rota: franjas corridas y colores separados (más fuerte al principio)
        if random.random() < (0.55 if progreso < 0.35 else 0.2):
            cortes_glitch(pantalla, random.randint(4, 10), int(60 * (1.2 - progreso)))
        if random.random() < (0.45 if progreso < 0.35 else 0.15):
            separar_rgb(pantalla, random.choice([-1, 1]) * random.randint(6, 16))
        # Fundido a negro al final
        if progreso > 0.8:
            negro = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
            negro.set_alpha(int(255 * (progreso - 0.8) / 0.2))
            pantalla.blit(negro, (0, 0))
        return
    escala = 1.0 + (progreso * 1.8)
    pygame.draw.circle(pantalla, (220, 40, 40), (cx, cy), int(100 * escala))
    if random.random() < 0.4:
        cortes_glitch(pantalla, 6, 50)

    for _ in range(450):
        rx = random.randint(0, ANCHO_VENTANA)
        ry = random.randint(0, ALTO_VENTANA)
        pantalla.set_at((rx, ry), (220, 220, 220))

# -------------------------------------------------------------
# 16. Subtítulos, Menús y Periódico de Victoria
# -------------------------------------------------------------
def partir_texto(texto, fuente, ancho_max):
    """Divide un texto en líneas que entren en ancho_max píxeles."""
    lineas, actual = [], ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        if fuente.size(prueba)[0] <= ancho_max or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas

def dibujar_panel_llamada():
    lista_actual = llamada_lista
    if llamada_activa and not llamada_muteada and not en_apagon and indice_dialogo < len(lista_actual):
        rect_caja = pygame.Rect(40, 20, 720, 82)
        s_caja = pygame.Surface((rect_caja.width, rect_caja.height), pygame.SRCALPHA)
        s_caja.fill((12, 16, 20, 230))
        pantalla.blit(s_caja, (rect_caja.x, rect_caja.y))
        pygame.draw.rect(pantalla, (50, 90, 80), rect_caja, 2)

        if int(tiempo_juego() * 3) % 2 == 0:
            pygame.draw.circle(pantalla, (40, 240, 120), (rect_caja.x + 20, rect_caja.y + 22), 6)
        txt_tag = fuente_cam.render(f"LÍNEA ACTIVA // SUPERVISIÓN TURNO {noche_actual}", True, (40, 240, 120))
        pantalla.blit(txt_tag, (rect_caja.x + 35, rect_caja.y + 15))

        for n_linea, linea in enumerate(partir_texto(lista_actual[indice_dialogo], fuente_llamada, rect_caja.width - 40)[:2]):
            txt_dialogo = fuente_llamada.render(linea, True, (240, 245, 240))
            pantalla.blit(txt_dialogo, (rect_caja.x + 20, rect_caja.y + 34 + n_linea * 21))

        rect_mute = pygame.Rect(rect_caja.right + 15, 20, 140, 82)
        pygame.draw.rect(pantalla, (120, 30, 30), rect_mute, border_radius=4)
        pygame.draw.rect(pantalla, (220, 60, 60), rect_mute, 2)
        txt_m1 = fuente_pequeña.render("[MUTE CALL]", True, (255, 255, 255))
        pantalla.blit(txt_m1, (rect_mute.centerx - txt_m1.get_width() // 2, rect_mute.centery - txt_m1.get_height() // 2))

# Fondo del menú: las cámaras de la planta van pasando, oscurecidas, con estática entre una y otra
_fondos_menu = []

def dibujar_fondo_menu():
    if not _fondos_menu:
        for i in range(1, 9):
            img = ASSETS.get(f"cam_0{i}")
            if img:
                fondo = escalar_cubriendo(img, ANCHO_VENTANA, ALTO_VENTANA).copy()
                fondo.fill((64, 70, 68), special_flags=pygame.BLEND_RGB_MULT)
                _fondos_menu.append((f"CAM_0{i}", fondo))
        if not _fondos_menu:
            _fondos_menu.append(("", None))
    t = tiempo_juego()
    duracion = 7.0
    indice = int(t // duracion) % len(_fondos_menu)
    etiqueta, fondo = _fondos_menu[indice]
    if fondo is None:
        pantalla.fill((8, 10, 12))
        return
    # Paneo lento, como una cámara que gira
    fase = (t % duracion) / duracion
    pantalla.blit(fondo, (int(-12 + 24 * fase), 0))
    linea_tracking(pantalla, t, pantalla.get_rect(), velocidad=40.0)
    if t % duracion < 0.35 or t % duracion > duracion - 0.1:
        pantalla.fill((10, 12, 12))
        for _ in range(2500):
            g = random.randint(30, 150)
            pantalla.set_at((random.randrange(ANCHO_VENTANA), random.randrange(ALTO_VENTANA)), (g, g, g))
    else:
        txt = fuente_cam.render(etiqueta, True, (150, 170, 160))
        pantalla.blit(txt, (ANCHO_VENTANA - txt.get_width() - 20, 18))
        if int(t * 2) % 2 == 0:
            pygame.draw.circle(pantalla, (200, 40, 40), (ANCHO_VENTANA - txt.get_width() - 34, 25), 5)

def dibujar_menu_principal():
    dibujar_fondo_menu()

    sp_menu = sprite("barnaby_oficina") or sprite("barnaby_cam")
    if sp_menu:
        twitch_x = random.randint(-14, 14) if random.random() < 0.10 else 0
        twitch_y = random.randint(-8, 8) if random.random() < 0.10 else 0
        brillo_m = random.choice([30, 45, 150, 25]) if random.random() < 0.08 else 40
        dibujar_sprite_centrado(pantalla, sp_menu, 230 + twitch_x, 380 + twitch_y, 1.35, brillo_m)

    txt_t1 = fuente_titulo.render("FNAF: INDUSTRIAL SECTOR", True, (220, 230, 235))
    pantalla.blit(txt_t1, (400, 90))

    txt_crt_info = fuente_cam.render(f"[F1] POST-PROCESADO CRT: {'ACTIVO' if crt_activo else 'OFF'}", True, (100, 180, 140))
    pantalla.blit(txt_crt_info, (400, 145))

    estrellas = sum([juego_completado_5_noches, final_verdadero_visto, noche6_superada, record_20_20_20_20])
    for i in range(estrellas):
        sx = 400 + i * 50
        sy = 175
        pygame.draw.circle(pantalla, (245, 200, 40), (sx + 15, sy + 12), 14)
        pygame.draw.circle(pantalla, (255, 240, 150), (sx + 15, sy + 12), 8)
    if record_20_20_20_20:
        txt_rec = fuente_cam.render("★ RÉCORD 20/20/20/20 COMPLETADO ★", True, (255, 215, 50))
        pantalla.blit(txt_rec, (400 + estrellas * 55, 180))

    if evidencias:
        txt_ev = fuente_cam.render(f"PRUEBAS: {len(evidencias)}/4   LOGROS: {len(progreso.logros)}/{len(LOGROS)}", True, (255, 210, 90))
        pantalla.blit(txt_ev, (760, 180))
    desbloq_cust = (noche_desbloqueada >= 5 or juego_completado_5_noches)
    items = [("NUEVO", "NUEVO JUEGO", (40, 160, 110), True),
             ("CONTINUAR", f"CONTINUAR (N.{min(noche_desbloqueada, 5)})", (40, 160, 220), noche_desbloqueada > 1)]
    if noche6_desbloqueada:
        items.append(("NOCHE6", "NOCHE 6", (220, 50, 50), True))
    items += [("CUSTOM", "CUSTOM NIGHT", (220, 100, 40), desbloq_cust),
              ("EXTRAS", "EXTRAS", (200, 170, 70), True),
              ("AJUSTES", "AJUSTES", (110, 130, 150), True),
              ("SALIR", "SALIR", (160, 40, 40), True)]
    opciones = boton_lista(items, 400, 212, 62 if len(items) > 6 else 68)

    txt_ver = fuente_cam.render(f"v{VERSION}", True, (70, 80, 85))
    pantalla.blit(txt_ver, (ANCHO_VENTANA - txt_ver.get_width() - 12, ALTO_VENTANA - 22))

    for _ in range(400):
        rx = random.randint(0, ANCHO_VENTANA)
        ry = random.randint(0, ALTO_VENTANA)
        pantalla.set_at((rx, ry), (random.randint(25, 100), random.randint(25, 100), random.randint(25, 100)))

    return opciones

def dibujar_menu_custom():
    pantalla.fill((12, 14, 16))
    txt_t = fuente_titulo.render("CUSTOM NIGHT", True, (240, 140, 40))
    pantalla.blit(txt_t, (ANCHO_VENTANA//2 - txt_t.get_width()//2, 40))
    if desafio_elegido:
        sub = f"{T('DESAFÍO')}: {T(desafio_elegido['nombre'])}  //  {T(desafio_elegido['desc'])}"
        color_sub = (240, 200, 90)
    else:
        sub = T("Configura la IA de cada uno (0 a 20) o elige un desafío abajo.")
        color_sub = (150, 160, 165)
    for k, linea in enumerate(partir_texto(sub, fuente_pequeña, 1000)[:2]):
        s_ = fuente_pequeña.render(linea, True, color_sub)
        pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, 105 + k * 20))

    animatronicos = ["Barnaby", "Silas", "Penny", "Rusty Bunny"]
    controles = []

    for i, nombre in enumerate(animatronicos):
        x = 140 + i * 250
        y = 180
        rect_card = pygame.Rect(x, y, 200, 250)
        pygame.draw.rect(pantalla, (20, 24, 28), rect_card, border_radius=8)
        pygame.draw.rect(pantalla, (50, 70, 85), rect_card, 2)

        txt_n = fuente_pequeña.render(nombre, True, (220, 230, 240))
        pantalla.blit(txt_n, (x + 100 - txt_n.get_width()//2, y + 20))

        val = (desafio_elegido["ia"] if desafio_elegido else ia_custom)[nombre]
        txt_val = fuente_grande.render(str(val), True, (255, 255, 255))
        pantalla.blit(txt_val, (x + 100 - txt_val.get_width()//2, y + 90))

        rect_menos = pygame.Rect(x + 25, y + 170, 50, 45)
        rect_mas = pygame.Rect(x + 125, y + 170, 50, 45)
        pygame.draw.rect(pantalla, (60, 25, 25), rect_menos, border_radius=4)
        pygame.draw.rect(pantalla, (25, 60, 35), rect_mas, border_radius=4)
        lbl_m = fuente_grande.render("-", True, (255, 255, 255))
        lbl_p = fuente_grande.render("+", True, (255, 255, 255))
        pantalla.blit(lbl_m, (rect_menos.x + 18, rect_menos.y + 4))
        pantalla.blit(lbl_p, (rect_mas.x + 16, rect_mas.y + 4))

        controles.append((nombre, rect_menos, rect_mas))

    # Desafíos
    botones_desafio = []
    pos_m = pygame.mouse.get_pos()
    for i, d_ in enumerate(DESAFIOS):
        rb = pygame.Rect(62 + i * 218, 450, 208, 44)
        elegido = desafio_elegido is d_
        hecho = d_["id"] in progreso.stats["desafios"]
        pygame.draw.rect(pantalla, (50, 38, 14) if elegido else ((28, 30, 34) if rb.collidepoint(pos_m) else (18, 20, 24)), rb, border_radius=5)
        pygame.draw.rect(pantalla, (240, 190, 70) if elegido else (90, 80, 60), rb, 2, border_radius=5)
        etiqueta = ("★ " if hecho else "") + d_["nombre"]
        s_ = fuente_cam.render(etiqueta, True, (255, 230, 150) if (elegido or hecho) else (200, 200, 200))
        pantalla.blit(s_, (rb.centerx - s_.get_width() // 2, rb.centery - s_.get_height() // 2))
        botones_desafio.append((d_, rb))
    hechos = sum(1 for d_ in DESAFIOS if d_["id"] in progreso.stats["desafios"])
    s_ = fuente_cam.render(f"DESAFÍOS SUPERADOS: {hechos}/{len(DESAFIOS)}", True, (150, 140, 110))
    pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, 500))

    rect_start = pygame.Rect(ANCHO_VENTANA//2 - 140, 525, 280, 55)
    pygame.draw.rect(pantalla, (25, 120, 60), rect_start, border_radius=6)
    txt_start = fuente_grande.render("INICIAR NOCHE", True, (255, 255, 255))
    pantalla.blit(txt_start, (rect_start.centerx - txt_start.get_width() // 2, rect_start.centery - txt_start.get_height() // 2))

    # Modo infinito
    rect_inf = pygame.Rect(ANCHO_VENTANA//2 - 140, 595, 280, 46)
    sobre = rect_inf.collidepoint(pos_m)
    pygame.draw.rect(pantalla, (70, 40, 12) if sobre else (40, 26, 10), rect_inf, border_radius=6)
    pygame.draw.rect(pantalla, (240, 160, 60), rect_inf, 2, border_radius=6)
    s_ = fuente_media.render("MODO INFINITO", True, (255, 210, 150))
    pantalla.blit(s_, (rect_inf.centerx - s_.get_width() // 2, rect_inf.centery - s_.get_height() // 2))
    records = progreso.stats["records_infinito"]
    detalle = f"{T('RÉCORD')}: {texto_tiempo_infinito(records[0])}" if records else T("Sin 6 AM: cada hora son más rápidos. ¿Cuánto aguantas?")
    s_ = fuente_cam.render(detalle, True, (170, 150, 120))
    pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, 650))
    if records:
        x_r = 940
        s_ = fuente_cam.render("MEJORES TIEMPOS", True, (200, 170, 110))
        pantalla.blit(s_, (x_r, 560))
        for k, seg in enumerate(records[:5]):
            s_ = fuente_cam.render(f"{k + 1}. {texto_tiempo_infinito(seg)}", True, (170, 160, 140))
            pantalla.blit(s_, (x_r, 580 + k * 18))

    rect_volver = pygame.Rect(40, 40, 110, 35)
    pygame.draw.rect(pantalla, (40, 45, 50), rect_volver, border_radius=4)
    txt_v = fuente_pequeña.render("< VOLVER", True, (220, 220, 220))
    pantalla.blit(txt_v, (rect_volver.x + 20, rect_volver.y + 10))

    return controles, rect_start, rect_volver, botones_desafio, rect_inf

def dibujar_pantalla_victoria(t_transcurrido):
    pantalla.fill((4, 6, 8))
    cx = ANCHO_VENTANA // 2
    cy = ALTO_VENTANA // 2
    str_hora = "5 AM" if t_transcurrido < 1.8 else "6 AM"
    txt_num = fuente_reloj_6am.render(str_hora, True, (245, 250, 255))
    pantalla.blit(txt_num, (cx - txt_num.get_width()//2, cy - 80))
    txt_sub = fuente_media.render(f"NOCHE {noche_actual} COMPLETADA", True, (40, 220, 140))
    pantalla.blit(txt_sub, (cx - txt_sub.get_width()//2, cy + 30))

def dibujar_pantalla_periodico():
    """Periódico del final. Usa periodico.png / periodico_verdadero.png si existen."""
    final = final_actual or FINAL_NORMAL
    p = final["periodico"]
    verdadero = final is FINAL_VERDADERO
    pantalla.fill((12, 12, 14))
    img = ASSETS.get("periodico_verdadero" if verdadero else "periodico")
    if img:
        pantalla.blit(img, (0, 0))
    else:
        rect_hoja = pygame.Rect(180, 30, 840, 630)
        pygame.draw.rect(pantalla, (215, 205, 185), rect_hoja)
        pygame.draw.rect(pantalla, (60, 50, 40), rect_hoja, 4)
        _c = lambda txt, fnt, y, col: pantalla.blit(fnt.render(txt, True, col), (rect_hoja.centerx - fnt.size(txt)[0] // 2, y))
        _c(p["cabecera"], fuente_grande, 48, (25, 20, 15))
        _c(p["fecha"], fuente_cam, 90, (70, 60, 50))
        pygame.draw.line(pantalla, (40, 35, 30), (210, 110), (990, 110), 3)
        pygame.draw.line(pantalla, (40, 35, 30), (210, 115), (990, 115), 1)
        _c(p["titular"], fuente_grande, 128, (20, 15, 10))
        _c(p["bajada"], fuente_media, 170, (80, 30, 20))
        rect_foto = pygame.Rect(230, 215, 300, 230)
        pygame.draw.rect(pantalla, (40, 38, 35), rect_foto)
        pygame.draw.rect(pantalla, (20, 18, 15), rect_foto, 3)
        if verdadero:
            # Silueta de un hombre de traje entre dos policías
            for dx, alto, color in ((-80, 150, (60, 58, 55)), (80, 150, (60, 58, 55)), (0, 165, (95, 90, 85))):
                cx = rect_foto.centerx + dx
                pygame.draw.circle(pantalla, color, (cx, rect_foto.bottom - alto), 20)
                pygame.draw.rect(pantalla, color, (cx - 30, rect_foto.bottom - alto + 22, 60, alto - 22))
        else:
            sp_foto = sprite("barnaby_cam") or sprite("bunny_cam")
            if sp_foto:
                gris = sp_foto.copy()
                gris.fill((150, 140, 125, 255), special_flags=pygame.BLEND_RGBA_MULT)
                dibujar_sprite_centrado(pantalla, gris, rect_foto.centerx, rect_foto.centery, 0.42, 200)
        pantalla.blit(fuente_cam.render(p["pie_foto"], True, (60, 55, 50)), (230, 455))
        for idx, lin in enumerate(p["articulo"]):
            pantalla.blit(fuente_pequeña.render(lin, True, (35, 30, 25)), (560, 220 + idx * 19))
        color_sello = (40, 110, 50) if verdadero else (160, 40, 40)
        txt_sello = fuente_grande.render(p["sello"], True, color_sello)
        sello = pygame.Rect(0, 0, txt_sello.get_width() + 40, 56)
        sello.center = (780, 560)
        pygame.draw.rect(pantalla, color_sello, sello, 3)
        pantalla.blit(txt_sello, (sello.x + 20, sello.y + 10))

    txt_cont = fuente_cam.render("[PULSA ESPACIO O HAZ CLIC PARA CONTINUAR]", True, (180, 190, 195))
    pantalla.blit(txt_cont, (ANCHO_VENTANA // 2 - txt_cont.get_width() // 2, ALTO_VENTANA - 25))

RECT_BTN_REINTENTAR = pygame.Rect(ANCHO_VENTANA // 2 - 290, 520, 270, 55)
RECT_BTN_MENU_MUERTE = pygame.Rect(ANCHO_VENTANA // 2 + 20, 520, 270, 55)
captura_pausa = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))

def dibujar_boton_menu(rect, texto, color_borde, activo=True):
    hover = rect.collidepoint(pygame.mouse.get_pos()) and activo
    pygame.draw.rect(pantalla, (30, 36, 42) if hover else (18, 22, 26), rect, border_radius=6)
    pygame.draw.rect(pantalla, color_borde if activo else (45, 55, 60), rect, 2, border_radius=6)
    txt = fuente_media.render(texto, True, (255, 255, 255) if activo else (90, 100, 105))
    pantalla.blit(txt, (rect.centerx - txt.get_width() // 2, rect.centery - txt.get_height() // 2))

def dibujar_menu_pausa():
    capa = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
    capa.fill((0, 0, 0, 190))
    pantalla.blit(capa, (0, 0))
    txt = fuente_titulo.render("PAUSA", True, (220, 230, 235))
    pantalla.blit(txt, (ANCHO_VENTANA // 2 - txt.get_width() // 2, 170))
    if es_infinito():
        sub = fuente_cam.render(f"{T('MODO INFINITO')}  //  {infinito_horas} H  //  {T('[ESC] PARA CONTINUAR')}", True, (130, 160, 150))
    else:
        sub = fuente_cam.render(f"NOCHE {noche_actual}  //  {hora} AM  //  [ESC] PARA CONTINUAR", True, (130, 160, 150))
    pantalla.blit(sub, (ANCHO_VENTANA // 2 - sub.get_width() // 2, 230))
    botones = []
    for i, (clave, texto, color) in enumerate([("CONTINUAR", "CONTINUAR", (40, 160, 110)),
                                               ("REINTENTAR", "REINICIAR NOCHE", (220, 140, 40)),
                                               ("AJUSTES", "AJUSTES", (110, 130, 150)),
                                               ("MENU", "MENÚ PRINCIPAL", (160, 40, 40))]):
        rect = pygame.Rect(ANCHO_VENTANA // 2 - 170, 280 + i * 70, 340, 55)
        dibujar_boton_menu(rect, texto, color)
        botones.append((clave, rect))
    return botones

def dibujar_pantalla_muerte():
    pantalla.fill((6, 4, 4))
    img = ASSETS.get(f"jumpscare_{animatronico_atacante}")
    if img:
        cara = img.copy()
        cara.fill((70, 45, 45), special_flags=pygame.BLEND_RGB_MULT)
        dx = random.randint(-3, 3) if random.random() < 0.15 else 0
        pantalla.blit(cara, ((ANCHO_VENTANA - cara.get_width()) // 2 + dx, (ALTO_VENTANA - cara.get_height()) // 2))
    # Estática y franjas de interferencia
    for _ in range(1400):
        g = random.randint(30, 140)
        pantalla.set_at((random.randrange(ANCHO_VENTANA), random.randrange(ALTO_VENTANA)), (g, g, g))
    if random.random() < 0.3:
        y = random.randrange(ALTO_VENTANA)
        pantalla.fill((60, 20, 20), (0, y, ANCHO_VENTANA, random.randint(3, 14)), special_flags=pygame.BLEND_RGB_ADD)

    txt_go = fuente_titulo.render("GAME OVER", True, (230, 40, 40))
    pantalla.blit(txt_go, (ANCHO_VENTANA // 2 - txt_go.get_width() // 2, 150))
    txt_res = fuente_media.render(mensaje_muerte, True, (255, 200, 200))
    pantalla.blit(txt_res, (ANCHO_VENTANA // 2 - txt_res.get_width() // 2, 225))
    if es_infinito():
        txt_hora = fuente_pequeña.render(f"{T('MODO INFINITO')}  //  {T('RESISTISTE')} {texto_tiempo_infinito(infinito_ultimo)}", True, (240, 190, 110))
        pantalla.blit(txt_hora, (ANCHO_VENTANA // 2 - txt_hora.get_width() // 2, 262))
        records = progreso.stats["records_infinito"]
        if infinito_record_nuevo and int(tiempo_juego() * 2) % 2 == 0:
            s_ = fuente_media.render("¡NUEVO RÉCORD!", True, (255, 215, 60))
            pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, 300))
        elif records and not infinito_record_nuevo:
            s_ = fuente_pequeña.render(f"{T('RÉCORD')}: {texto_tiempo_infinito(records[0])}", True, (170, 160, 130))
            pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, 305))
    else:
        txt_hora = fuente_pequeña.render(f"NOCHE {noche_actual}  //  RESISTISTE HASTA LAS {hora} AM", True, (170, 180, 185))
        pantalla.blit(txt_hora, (ANCHO_VENTANA // 2 - txt_hora.get_width() // 2, 262))

    dibujar_boton_menu(RECT_BTN_REINTENTAR, "[R] REINTENTAR NOCHE", (220, 140, 40))
    dibujar_boton_menu(RECT_BTN_MENU_MUERTE, "[ESC] MENÚ PRINCIPAL", (160, 40, 40))

# -------------------------------------------------------------
# Menú de ajustes
# -------------------------------------------------------------
# (clave, texto, tipo, parámetros). tipo: "barra" (mín, máx, paso, sufijo), "si_no", "opciones" ([(valor, texto)...])
OPCIONES_AJUSTES = [
    ("vol_general", "VOLUMEN GENERAL", "barra", (0, 100, 5, "%")),
    ("vol_efectos", "EFECTOS DE SONIDO", "barra", (0, 100, 5, "%")),
    ("vol_musica", "MÚSICA Y AMBIENTE", "barra", (0, 100, 5, "%")),
    ("vol_voces", "VOCES DE LAS LLAMADAS", "barra", (0, 100, 5, "%")),
    ("brillo", "BRILLO", "barra", (50, 150, 5, "%")),
    ("crt", "EFECTO MONITOR CRT", "si_no", None),
    ("pantalla_completa", "PANTALLA COMPLETA  [F11]", "si_no", None),
    ("escalado", "ESCALADO DE IMAGEN", "opciones", [("ajustar", "AJUSTAR (SIN DEFORMAR)"), ("estirar", "ESTIRAR (SIN BORDES)")]),
    ("vel_giro", "VELOCIDAD DE GIRO EN LA OFICINA", "barra", (50, 200, 10, "%")),
    ("mostrar_fps", "MOSTRAR FPS", "si_no", None),
    ("dificultad", "DIFICULTAD (HISTORIA)", "opciones", [(k, v["nombre"]) for k, v in DIFICULTADES.items()]),
    ("idioma", "IDIOMA / LANGUAGE", "opciones", [("es", "ESPAÑOL"), ("en", "ENGLISH")]),
    ("subtitulos", "SUBTÍTULOS DE SONIDOS", "si_no", None),
]
AYUDA_AJUSTES = {
    "escalado": "AJUSTAR mantiene la imagen sin deformar (puede dejar bordes negros). ESTIRAR llena toda la pantalla.",
    "brillo": "Si la oficina se ve muy oscura en tu monitor, subilo un poco.",
    "crt": "Líneas de monitor viejo y desplazamiento de color. Apagarlo mejora el rendimiento.",
    "vel_giro": "Qué tan rápido gira la vista al llevar el mouse a los bordes de la oficina.",
    "pantalla_completa": "También se cambia en cualquier momento con F11.",
    "dificultad": "Se aplica a las noches 1 a 6 desde la próxima noche. HISTORIA: más fácil, para ver la historia.",
    "idioma": "Cambia el idioma de todo el juego.",
    "subtitulos": "Muestra en pantalla los sonidos importantes (pasos, respiración, golpes) y de qué lado vienen.",
}
Y_AJUSTES, ALTO_FILA_AJUSTES = 96, 34
X_CONTROL, ANCHO_CONTROL = 640, 400

def cambiar_ajuste(clave, direccion=1, valor=None):
    """Cambia un ajuste (direccion = -1 / +1, o un valor exacto) y lo aplica al instante."""
    global crt_activo
    _, _, tipo, params = next(o for o in OPCIONES_AJUSTES if o[0] == clave)
    if tipo == "barra":
        mn, mx, paso, _ = params
        nuevo = valor if valor is not None else AJUSTES[clave] + paso * direccion
        AJUSTES[clave] = int(max(mn, min(mx, round(nuevo / paso) * paso)))
    elif tipo == "si_no":
        AJUSTES[clave] = not AJUSTES[clave]
    else:
        valores = [v for v, _ in params]
        AJUSTES[clave] = valores[(valores.index(AJUSTES[clave]) + direccion) % len(valores)]
    if clave == "crt":
        crt_activo = AJUSTES["crt"]
    if clave == "idioma":
        aplicar_idioma()
    if clave in ("pantalla_completa", "escalado"):
        ventana.aplicar_modo()
    if clave in ("vol_general", "vol_musica", "vol_voces"):
        g = AJUSTES["vol_general"] / 100.0
        CANAL_MUSICA.set_volume(g * AJUSTES["vol_musica"] / 100.0)
        CANAL_AMBIENTE.set_volume(g * AJUSTES["vol_musica"] / 100.0)
        CANAL_VOZ.set_volume(g * AJUSTES["vol_voces"] / 100.0)

def controles_fila_ajuste(i):
    y = Y_AJUSTES + i * ALTO_FILA_AJUSTES
    fila = pygame.Rect(150, y, 900, ALTO_FILA_AJUSTES - 6)
    menos = pygame.Rect(X_CONTROL, y + 2, 34, 28)
    mas = pygame.Rect(X_CONTROL + ANCHO_CONTROL - 34, y + 2, 34, 28)
    barra = pygame.Rect(menos.right + 12, y + 8, mas.left - menos.right - 24, 10)
    return fila, menos, mas, barra

RECT_AJ_RESTABLECER = pygame.Rect(ANCHO_VENTANA // 2 - 420, 606, 260, 46)
RECT_AJ_CONTROLES = pygame.Rect(ANCHO_VENTANA // 2 - 130, 606, 260, 46)
RECT_AJ_VOLVER = pygame.Rect(ANCHO_VENTANA // 2 + 160, 606, 260, 46)

def dibujar_menu_ajustes():
    if ajustes_volver_a == "PAUSA":
        pantalla.blit(captura_pausa, (0, 0))
        capa = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        capa.fill((4, 6, 8, 225))
        pantalla.blit(capa, (0, 0))
    else:
        pantalla.fill((8, 10, 12))
    txt = fuente_titulo.render("AJUSTES", True, (220, 230, 235))
    pantalla.blit(txt, (ANCHO_VENTANA // 2 - txt.get_width() // 2, 20))
    sub = fuente_cam.render("[ARRIBA/ABAJO] ELEGIR   [IZQ/DER] CAMBIAR   [ESC] VOLVER   //   SE GUARDA SOLO", True, (110, 140, 130))
    pantalla.blit(sub, (ANCHO_VENTANA // 2 - sub.get_width() // 2, 72))

    pos = pygame.mouse.get_pos()
    for i, (clave, texto, tipo, params) in enumerate(OPCIONES_AJUSTES):
        fila, menos, mas, barra = controles_fila_ajuste(i)
        elegida = (i == ajustes_seleccion)
        if elegida:
            pygame.draw.rect(pantalla, (22, 34, 32), fila, border_radius=5)
            pygame.draw.rect(pantalla, (50, 120, 95), fila, 1, border_radius=5)
        etiqueta = fuente_panel.render(texto, True, (235, 245, 240) if elegida else (165, 180, 175))
        pantalla.blit(etiqueta, (fila.x + 20, fila.centery - etiqueta.get_height() // 2))

        for rb, simbolo in ((menos, "<"), (mas, ">")):
            hover = rb.collidepoint(pos)
            pygame.draw.rect(pantalla, (40, 60, 56) if hover else (24, 30, 32), rb, border_radius=4)
            pygame.draw.rect(pantalla, (80, 110, 100), rb, 1, border_radius=4)
            s_txt = fuente_media.render(simbolo, True, (220, 235, 230))
            pantalla.blit(s_txt, (rb.centerx - s_txt.get_width() // 2, rb.centery - s_txt.get_height() // 2))

        valor = AJUSTES[clave]
        if tipo == "barra":
            mn, mx, _, sufijo = params
            pygame.draw.rect(pantalla, (14, 18, 20), barra, border_radius=6)
            lleno = barra.copy()
            lleno.width = int(barra.width * (valor - mn) / (mx - mn))
            pygame.draw.rect(pantalla, (40, 200, 130), lleno, border_radius=6)
            pygame.draw.circle(pantalla, (230, 255, 240), (lleno.right, barra.centery), 9)
            v_txt = fuente_cam.render(f"{valor}{sufijo}", True, (200, 220, 210))
            pantalla.blit(v_txt, (barra.centerx - v_txt.get_width() // 2, barra.bottom + 1))
        else:
            if tipo == "si_no":
                texto_valor, color = ("SÍ", (80, 230, 140)) if valor else ("NO", (230, 110, 100))
            else:
                texto_valor, color = dict(params)[valor], (240, 200, 110)
            v_txt = fuente_pequeña.render(texto_valor, True, color)
            pantalla.blit(v_txt, (barra.centerx - v_txt.get_width() // 2, barra.centery - v_txt.get_height() // 2))

    clave_sel = OPCIONES_AJUSTES[ajustes_seleccion][0]
    if clave_sel in AYUDA_AJUSTES:
        ayuda = fuente_cam.render(AYUDA_AJUSTES[clave_sel], True, (140, 160, 150))
        pantalla.blit(ayuda, (ANCHO_VENTANA // 2 - ayuda.get_width() // 2, 578))

    dibujar_boton_menu(RECT_AJ_RESTABLECER, "RESTABLECER", (180, 120, 40))
    dibujar_boton_menu(RECT_AJ_CONTROLES, "CONTROLES / MANDO", (110, 130, 200))
    dibujar_boton_menu(RECT_AJ_VOLVER, "[ESC] VOLVER", (40, 160, 110))

# -------------------------------------------------------------
# Pantalla de controles: cambiar teclas y ver el mando
# -------------------------------------------------------------
controles_seleccion = 0
controles_escuchando = None      # Acción que espera una tecla nueva
controles_aviso, controles_aviso_hasta = "", 0.0
RECT_CT_RESTABLECER = pygame.Rect(ANCHO_VENTANA // 2 - 300, 616, 280, 46)
RECT_CT_VOLVER = pygame.Rect(ANCHO_VENTANA // 2 + 20, 616, 280, 46)

def filas_controles():
    return [pygame.Rect(70, 128 + i * 48, 650, 42) for i in range(len(mapa_teclas.ACCIONES))]

def dibujar_controles():
    pantalla.fill((8, 10, 12))
    txt = fuente_titulo.render("CONTROLES", True, (220, 230, 235))
    pantalla.blit(txt, (ANCHO_VENTANA // 2 - txt.get_width() // 2, 20))
    sub = fuente_cam.render("CLIC (O ENTER) EN UNA ACCIÓN Y PULSA LA TECLA NUEVA  //  [ESC] VOLVER", True, (110, 140, 130))
    pantalla.blit(sub, (ANCHO_VENTANA // 2 - sub.get_width() // 2, 80))
    pos = pygame.mouse.get_pos()
    nombres = mapa_teclas.etiquetas()
    for i, (fila, (accion, nombre, _, alt)) in enumerate(zip(filas_controles(), mapa_teclas.ACCIONES)):
        escuchando = controles_escuchando == accion
        elegida = i == controles_seleccion or fila.collidepoint(pos)
        pygame.draw.rect(pantalla, (40, 34, 14) if escuchando else ((24, 32, 30) if elegida else (14, 17, 19)), fila, border_radius=5)
        pygame.draw.rect(pantalla, (240, 200, 70) if escuchando else ((60, 160, 110) if elegida else (40, 48, 52)), fila, 1, border_radius=5)
        pantalla.blit(fuente_pequeña.render(nombre, True, (215, 225, 220)), (fila.x + 16, fila.centery - 9))
        caja = pygame.Rect(fila.right - 285, fila.y + 6, 135, fila.h - 12)
        if escuchando:
            texto_tecla = "PULSA UNA TECLA..." if int(tiempo_juego() * 3) % 2 == 0 else ""
            color_t = (255, 220, 90)
        else:
            texto_tecla, color_t = nombres[accion], (255, 255, 255)
        pygame.draw.rect(pantalla, (30, 34, 40), caja, border_radius=4)
        s_ = fuente_pequeña.render(texto_tecla, True, color_t)
        pantalla.blit(s_, (caja.centerx - s_.get_width() // 2, caja.centery - s_.get_height() // 2))
        if alt is not None:
            s_ = fuente_cam.render(T("TAMBIÉN") + " " + mapa_teclas.nombre_tecla(alt), True, (110, 120, 120))
            pantalla.blit(s_, (caja.right + 10, caja.centery - s_.get_height() // 2))

    # Mando
    x_m = 770
    pantalla.blit(fuente_panel.render("MANDO", True, (90, 220, 140)), (x_m, 128))
    nombre_m = mando.nombre_mando()
    estado_m = (T("CONECTADO") + ": " + nombre_m[:26]) if nombre_m else T("NO SE DETECTÓ NINGÚN MANDO")
    pantalla.blit(fuente_cam.render(estado_m, True, (200, 220, 210) if nombre_m else (150, 120, 110)), (x_m, 160))
    for k, (boton, desc) in enumerate(mando.DESCRIPCION):
        y = 192 + k * 30
        caja = pygame.Rect(x_m, y, 92, 24)
        pygame.draw.rect(pantalla, (30, 34, 40), caja, border_radius=4)
        s_ = fuente_cam.render(boton, True, (255, 230, 150))
        pantalla.blit(s_, (caja.centerx - s_.get_width() // 2, caja.centery - s_.get_height() // 2))
        pantalla.blit(fuente_cam.render(desc, True, (180, 190, 185)), (caja.right + 12, caja.centery - 8))
    for k, linea in enumerate(partir_texto(T("Los botones del mando usan las teclas de la izquierda."), fuente_cam, 390)):
        pantalla.blit(fuente_cam.render(linea, True, (100, 110, 105)), (x_m, 500 + k * 18))

    if tiempo_juego() < controles_aviso_hasta:
        s_ = fuente_pequeña.render(controles_aviso, True, (255, 120, 100))
        pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, 580))
    dibujar_boton_menu(RECT_CT_RESTABLECER, "RESTABLECER TECLAS", (180, 120, 40))
    dibujar_boton_menu(RECT_CT_VOLVER, "[ESC] VOLVER", (40, 160, 110))

def abrir_controles():
    global estado_actual, controles_escuchando, controles_seleccion
    controles_escuchando, controles_seleccion = None, 0
    estado_actual = ESTADO_CONTROLES

def salir_de_ajustes():
    global estado_actual
    guardar_ajustes(AJUSTES)
    reproducir_sonido(sfx_reboot_click)
    estado_actual = ESTADO_JUEGO if ajustes_volver_a == "PAUSA" else ESTADO_MENU

# -------------------------------------------------------------
# Modo desarrollador (código secreto + atajos + panel de información)
# -------------------------------------------------------------
_buffer_codigo = ""
_buffer_digitos = ""
dev_congelados = False       # F6: los animatrónicos no se mueven
dev_panel = True             # F10: mostrar u ocultar el panel
dev_aviso, dev_t_aviso = "", 0.0
dev_jumpscare_idx = 0

def dev_avisar(texto):
    global dev_aviso, dev_t_aviso
    dev_aviso, dev_t_aviso = texto, tiempo_juego() + 2.5
    ventana.capa_extra = dibujar_capas_superiores

def revisar_eventos_desarrollo(eventos):
    """Se llama con todos los eventos del juego: detecta el código secreto y los atajos F4-F10."""
    global _buffer_codigo, MODO_DESARROLLO, dev_congelados, dev_panel, dev_jumpscare_idx
    global noche_desbloqueada, juego_completado_5_noches, evidencias, tiempo_inicio
    global _buffer_digitos
    for e in eventos:
        if e.type != pygame.KEYDOWN:
            continue
        if e.unicode and e.unicode.isdigit() and estado_actual in (ESTADO_MENU, ESTADO_EXTRAS):
            _buffer_digitos = (_buffer_digitos + e.unicode)[-4:]
            if _buffer_digitos == "0303":
                _buffer_digitos = ""
                progreso.desbloquear("cinta_cero")
                reproducir_sonido(sfx_glitch_8bit)
                mostrar_relato(CINTA_SECRETA["titulo"], CINTA_SECRETA["lineas"], lambda: iniciar_minijuego(0, "MENU"), (220, 60, 60))
        if e.unicode and e.unicode.isalnum():
            _buffer_codigo = (_buffer_codigo + e.unicode.lower())[-len(CODIGO_DESARROLLO):]
            if _buffer_codigo == CODIGO_DESARROLLO.lower():
                _buffer_codigo = ""
                MODO_DESARROLLO = not MODO_DESARROLLO
                progreso.bloqueado = MODO_DESARROLLO
                if not MODO_DESARROLLO:
                    dev_congelados = False
                reproducir_sonido(sfx_ir_lock)
                dev_avisar("MODO DESARROLLADOR " + ("ACTIVADO" if MODO_DESARROLLO else "DESACTIVADO"))
                continue
        if not MODO_DESARROLLO:
            continue
        en_noche = estado_actual == ESTADO_JUEGO and not juego_terminado and not en_jumpscare and not pausado
        if e.key == pygame.K_F4:
            global noche6_desbloqueada
            noche_desbloqueada, juego_completado_5_noches, noche6_desbloqueada = 5, True, True
            dev_avisar("NOCHES Y CINTAS DESBLOQUEADAS (SOLO ESTA SESIÓN)")
        elif e.key == pygame.K_F5:
            evidencias = set() if len(evidencias) == 4 else {1, 2, 3, 4}
            dev_avisar(f"PRUEBAS: {len(evidencias)}/4 (SOLO ESTA SESIÓN)")
        elif e.key == pygame.K_F6:
            dev_congelados = not dev_congelados
            dev_avisar("ANIMATRÓNICOS CONGELADOS" if dev_congelados else "ANIMATRÓNICOS ACTIVOS")
        elif e.key == pygame.K_F7 and en_noche:
            tiempo_inicio -= DURACION_HORA_SEGUNDOS
            dev_avisar("+1 HORA")
        elif e.key == pygame.K_F8 and en_noche:
            nombre = ["Barnaby", "Silas", "Penny", "Rusty Bunny", "Unidad 0"][dev_jumpscare_idx % 5]
            dev_jumpscare_idx += 1
            iniciar_jumpscare(nombre, f"PRUEBA DE JUMPSCARE: {nombre.upper()}")
        elif e.key == pygame.K_F9 and estado_actual == ESTADO_MINIJUEGO and minijuego_actual and minijuego_actual.fase == "juego":
            minijuego_actual.prueba = True
            minijuego_actual.ganar()
            dev_avisar("CINTA GANADA (CON PRUEBA)")
        elif e.key == pygame.K_F10:
            dev_panel = not dev_panel
            ventana.capa_extra = dibujar_capas_superiores
    if MODO_DESARROLLO:
        ventana.capa_extra = dibujar_capas_superiores

def dibujar_capa_desarrollo(sup):
    ahora_dev = tiempo_juego()
    if not MODO_DESARROLLO and ahora_dev > dev_t_aviso:
        return
    f = fuente_cam
    if MODO_DESARROLLO and dev_panel:
        lineas = [("MODO DESARROLLADOR  //  escribe '" + CODIGO_DESARROLLO + "' para salir  //  logros desactivados", (255, 90, 90)),
                  ("F2 6 AM   F3 recargar   F4 desbloquear   F5 pruebas   F6 congelar", (220, 220, 220)),
                  ("F7 +1 hora   F8 jumpscare   F9 ganar cinta   F10 ocultar panel", (220, 220, 220))]
        if estado_actual == ESTADO_JUEGO:
            lineas.append((f"NOCHE {noche_actual}  {hora} AM  //  BAT {bateria:.0f}%  OX {oxigeno:.0f}%  BOBINA {bobina_generador:.0f}%  IR {carga_ir:.0f}%", (120, 230, 160)))
            for a in (barnaby, silas, penny, bunny):
                estado_a = "CONGELADO" if dev_congelados else f"IA {a.nivel_ia}+{a.bonus_hora}"
                lineas.append((f"{a.nombre.upper():12s} {a.sala():16s} {estado_a}", (160, 200, 230)))
            if unidad0.activa:
                lineas.append((f"UNIDAD 0     {unidad0.sala():16s} sin vigilar {unidad0.sin_vigilar:.1f}/{unidad0.limite:.0f}s", (230, 230, 255)))
            if modificadores:
                lineas.append(("DESAFÍO: " + ", ".join(modificadores), (240, 200, 90)))
        elif estado_actual == ESTADO_MINIJUEGO and minijuego_actual:
            lineas.append((f"CINTA {minijuego_numero}  fase: {minijuego_actual.fase}  pos: {int(minijuego_actual.px)},{int(minijuego_actual.py)}", (120, 230, 160)))
        alto = 8 + 17 * len(lineas)
        fondo = pygame.Surface((560, alto), pygame.SRCALPHA)
        fondo.fill((0, 0, 0, 185))
        sup.blit(fondo, (8, sup.get_height() - alto - 112))
        for i, (texto, color) in enumerate(lineas):
            sup.blit(f.render(texto, True, color), (14, sup.get_height() - alto - 108 + i * 17))
    elif MODO_DESARROLLO:
        sup.blit(f.render("DEV", True, (255, 90, 90)), (8, 8))
    if ahora_dev < dev_t_aviso:
        txt = fuente_media.render(dev_aviso, True, (255, 255, 255))
        caja = pygame.Rect(0, 0, txt.get_width() + 30, txt.get_height() + 16)
        caja.midtop = (sup.get_width() // 2, 120)
        sup.fill((40, 8, 8), caja)
        pygame.draw.rect(sup, (255, 80, 80), caja, 2)
        sup.blit(txt, (caja.x + 15, caja.y + 8))

ventana.al_recibir_eventos = revisar_eventos_desarrollo

# -------------------------------------------------------------
# Estadísticas, logros, EXTRAS y créditos
# -------------------------------------------------------------
uso_puerta_noche = False      # Para el logro "Puertas abiertas"

def registrar_fin_de_noche():
    """Se llama a las 6 AM: suma estadísticas y revisa logros de la noche."""
    progreso.sumar("noches_superadas")
    progreso.stats["bateria_final_suma"] += bateria
    progreso.stats["noches_con_bateria"] += 1
    progreso.stats["mejor_bateria"] = max(progreso.stats["mejor_bateria"], bateria)
    if noche_actual == 1:
        progreso.desbloquear("primer_turno")
    if noche_actual == 5:
        progreso.desbloquear("fin_contrato")
        if progreso.stats["muertes_partida"] == 0:
            progreso.desbloquear("intocable")
    if noche_actual == 6:
        progreso.desbloquear("horas_extra")
    if noche_actual == "CUSTOM" and all(v == 20 for v in ia_custom.values()):
        progreso.desbloquear("veinte")
    if noche_actual != "CUSTOM" and noche_actual != 1:
        if not uso_puerta_noche:
            progreso.desbloquear("puertas_abiertas")
        if bateria > 50:
            progreso.desbloquear("ahorro")
    revisar_fin_de_noche_extra()

def revisar_fin_de_noche_extra():
    global noche6_superada
    if noche_actual == 6:
        noche6_superada = True
    if noche_actual == "CUSTOM" and desafio_elegido:
        progreso.agregar_a_lista("desafios", desafio_elegido["id"])
        if all(d_["id"] in progreso.stats["desafios"] for d_ in DESAFIOS):
            progreso.desbloquear("turno_completo")

def dibujar_capas_superiores(sup):
    """Se dibuja encima de todo: avisos de logros y panel del modo desarrollador."""
    dibujar_capa_desarrollo(sup)
    dibujar_aviso_logro(sup)

aviso_logro_actual, aviso_logro_hasta = None, 0.0

def dibujar_aviso_logro(sup):
    global aviso_logro_actual, aviso_logro_hasta
    ahora_l = pygame.time.get_ticks() / 1000.0
    if (aviso_logro_actual is None or ahora_l > aviso_logro_hasta) and progreso.avisos:
        aviso_logro_actual = progreso.avisos.pop(0)
        aviso_logro_hasta = ahora_l + 4.0
        reproducir_sonido(sfx_campana_3, 0.5, 0.5)
        guardar_progreso()
    if aviso_logro_actual and ahora_l <= aviso_logro_hasta:
        _, nombre, desc, _ = NOMBRES_LOGROS[aviso_logro_actual]
        caja = pygame.Rect(sup.get_width() - 430, sup.get_height() - 190, 410, 70)
        sup.fill((20, 16, 6), caja)
        pygame.draw.rect(sup, (240, 200, 60), caja, 2)
        pygame.draw.circle(sup, (240, 200, 60), (caja.x + 35, caja.centery), 18)
        pygame.draw.circle(sup, (255, 240, 170), (caja.x + 35, caja.centery), 9)
        sup.blit(fuente_cam.render("LOGRO DESBLOQUEADO", True, (240, 200, 60)), (caja.x + 65, caja.y + 10))
        sup.blit(fuente_pequeña.render(T(nombre), True, (255, 255, 255)), (caja.x + 65, caja.y + 28))
        sup.blit(fuente_cam.render(T(desc)[:52], True, (190, 190, 180)), (caja.x + 65, caja.y + 48))

def boton_lista(items, x, y0, paso, ancho=340, alto=52):
    """Dibuja una columna de botones. items = [(clave, texto, color, habilitado)]. Devuelve [(clave, rect, habilitado)]."""
    salida = []
    pos = pygame.mouse.get_pos()
    for i, (clave, texto, color, habil) in enumerate(items):
        rect = pygame.Rect(x, y0 + i * paso, ancho, alto)
        hover = habil and rect.collidepoint(pos)
        pygame.draw.rect(pantalla, (30, 34, 38) if hover else ((18, 22, 26) if habil else (14, 16, 18)), rect, border_radius=6)
        pygame.draw.rect(pantalla, color if habil else (45, 55, 60), rect, 2, border_radius=6)
        txt = fuente_grande.render(texto, True, (255, 255, 255) if habil else (90, 100, 105))
        pantalla.blit(txt, (rect.x + 25, rect.centery - txt.get_height() // 2))
        salida.append((clave, rect, habil))
    return salida

def dibujar_extras():
    pantalla.fill((8, 10, 12))
    txt = fuente_titulo.render("EXTRAS", True, (220, 230, 235))
    pantalla.blit(txt, (ANCHO_VENTANA // 2 - txt.get_width() // 2, 70))
    sub = fuente_pequeña.render(f"PRUEBAS {len(evidencias)}/4   //   LOGROS {len(progreso.logros)}/{len(LOGROS)}", True, (130, 160, 150))
    pantalla.blit(sub, (ANCHO_VENTANA // 2 - sub.get_width() // 2, 130))
    return boton_lista([("ARCHIVO", "ARCHIVO 1982", (200, 170, 70), cinta_disponible(1)),
                        ("LOGROS", "LOGROS", (240, 200, 60), True),
                        ("ESTADISTICAS", "ESTADÍSTICAS", (60, 180, 220), True),
                        ("CREDITOS", "CRÉDITOS", (150, 130, 200), True),
                        ("VOLVER", "VOLVER", (40, 160, 110), True)], ANCHO_VENTANA // 2 - 170, 200, 72)

RECT_VOLVER_ABAJO = pygame.Rect(ANCHO_VENTANA // 2 - 140, 630, 280, 48)

def dibujar_logros():
    pantalla.fill((8, 10, 12))
    txt = fuente_titulo.render("LOGROS", True, (240, 200, 60))
    pantalla.blit(txt, (ANCHO_VENTANA // 2 - txt.get_width() // 2, 25))
    sub = fuente_pequeña.render(f"{len(progreso.logros)} DE {len(LOGROS)} DESBLOQUEADOS", True, (170, 160, 120))
    pantalla.blit(sub, (ANCHO_VENTANA // 2 - sub.get_width() // 2, 80))
    paso = min(57, 505 // ((len(LOGROS) + 1) // 2))   # Se compacta si hay muchos logros
    for i, (id_l, nombre, desc, secreto) in enumerate(LOGROS):
        col, fila = i % 2, i // 2
        caja = pygame.Rect(40 + col * 570, 108 + fila * paso, 550, paso - 6)
        tiene = id_l in progreso.logros
        pygame.draw.rect(pantalla, (26, 22, 10) if tiene else (16, 18, 20), caja, border_radius=5)
        pygame.draw.rect(pantalla, (200, 165, 50) if tiene else (45, 50, 55), caja, 1, border_radius=5)
        pygame.draw.circle(pantalla, (240, 200, 60) if tiene else (40, 44, 48), (caja.x + 26, caja.centery), 15)
        if tiene:
            pygame.draw.circle(pantalla, (255, 240, 170), (caja.x + 26, caja.centery), 7)
        if secreto and not tiene:
            nombre, desc = "???", "Logro secreto."
        pantalla.blit(fuente_pequeña.render(nombre, True, (255, 250, 230) if tiene else (130, 135, 140)), (caja.x + 52, caja.y + caja.height // 2 - 19))
        pantalla.blit(fuente_cam.render(desc, True, (190, 185, 170) if tiene else (95, 100, 105)), (caja.x + 52, caja.y + caja.height // 2 + 2))
    dibujar_boton_menu(RECT_VOLVER_ABAJO, "[ESC] VOLVER", (40, 160, 110))

def dibujar_resumen():
    st = progreso.stats
    pantalla.fill((6, 8, 9))
    titulo = "RESUMEN DE TU TURNO" if resumen_volver_a == ESTADO_CREDITOS else "ESTADÍSTICAS"
    txt = fuente_titulo.render(titulo, True, (220, 230, 235))
    pantalla.blit(txt, (60, 30))
    pantalla.blit(fuente_pequeña.render("ENSAMBLADORA DUNMORE S.A. // REGISTRO DEL GUARDIA NOCTURNO", True, (110, 140, 130)), (62, 88))

    letra, titulo_nota = progreso.nota(len(evidencias))
    caja = pygame.Rect(800, 25, 360, 110)
    pygame.draw.rect(pantalla, (18, 22, 24), caja, border_radius=8)
    pygame.draw.rect(pantalla, (240, 200, 60), caja, 2, border_radius=8)
    s_ = fuente_reloj_6am.render(letra, True, (240, 200, 60))
    pantalla.blit(s_, (caja.x + 20, caja.y + 12))
    pantalla.blit(fuente_cam.render("CALIFICACIÓN", True, (160, 150, 120)), (caja.x + 130, caja.y + 30))
    pantalla.blit(fuente_pequeña.render(titulo_nota, True, (255, 255, 255)), (caja.x + 130, caja.y + 52))

    def columna(x, y, encabezado, filas):
        pantalla.blit(fuente_panel.render(encabezado, True, (90, 220, 140)), (x, y))
        pygame.draw.line(pantalla, (40, 80, 60), (x, y + 26), (x + 330, y + 26), 1)
        for i, (nombre, valor) in enumerate(filas):
            pantalla.blit(fuente_pequeña.render(nombre, True, (180, 190, 185)), (x, y + 38 + i * 26))
            v = fuente_pequeña.render(str(valor), True, (255, 255, 255))
            pantalla.blit(v, (x + 330 - v.get_width(), y + 38 + i * 26))

    columna(60, 160, "GENERAL", [
        ("Noches superadas", st["noches_superadas"]),
        ("Tiempo de turno", formato_tiempo(st["tiempo_jugado"])),
        ("Muertes", st["muertes"]),
        ("Batería promedio a las 6 AM", f"{progreso.bateria_promedio():.0f}%"),
        ("Mejor batería a las 6 AM", f"{st['mejor_bateria']:.0f}%"),
        ("Pruebas encontradas", f"{len(evidencias)}/4"),
        ("Cintas completadas", st["cintas_completadas"]),
        ("Intentos fallidos en cintas", st["cintas_fallos"]),
        ("Logros", f"{len(progreso.logros)}/{len(LOGROS)}"),
        ("Récord modo infinito", texto_tiempo_infinito(st["records_infinito"][0]) if st["records_infinito"] else "-"),
    ])
    columna(440, 160, "DEFENSAS", [
        ("Compuertas cerradas", st["puertas_cerradas"]),
        ("Persianas bajadas", st["persianas"]),
        ("Veces que usaste la linterna", st["linterna"]),
        ("Cámaras revisadas", st["camaras_vistas"]),
        ("Señuelos de audio", st["senuelos"]),
        ("Reinicios de sistemas", st["reinicios_sistema"]),
        ("Penny frenada en la puerta", st["penny_bloqueada"]),
        ("Rusty frenado en la ventana", st["bunny_rechazado"]),
        ("Barnaby encandilado", st["barnaby_cegado"]),
        ("Silas atrapado en ductos", st["silas_atrapado"]),
        ("Unidad 0 rechazada", st["unidad0_rechazada"]),
    ])
    causas = ["Barnaby", "Penny", "Rusty Bunny", "Silas", "Unidad 0", "Apagón", "Asfixia"]
    columna(820, 160, "MUERTES POR", [(c.upper(), st["muertes_por"].get(c, 0)) for c in causas])
    pantalla.blit(fuente_cam.render("Las estadísticas se acumulan en todas tus partidas.", True, (100, 110, 105)), (60, 470))
    texto_boton = "[ESPACIO] CRÉDITOS" if resumen_volver_a == ESTADO_CREDITOS else "[ESC] VOLVER"
    dibujar_boton_menu(RECT_VOLVER_ABAJO, texto_boton, (40, 160, 110))

def abrir_resumen(volver_a):
    global estado_actual, resumen_volver_a
    resumen_volver_a = volver_a
    estado_actual = ESTADO_RESUMEN

def abrir_creditos(volver_a):
    global estado_actual, creditos_volver_a, t_creditos
    creditos_volver_a, t_creditos = volver_a, tiempo_juego()
    estado_actual = ESTADO_CREDITOS

def dibujar_creditos():
    pantalla.fill((3, 3, 4))
    t = tiempo_juego() - t_creditos
    y = ALTO_VENTANA - t * 55
    for texto, tipo in CREDITOS:
        fuente, color = {"titulo": (fuente_grande, (230, 60, 60)), "seccion": (fuente_pequeña, (110, 140, 130)),
                         "nombre": (fuente_media, (235, 235, 230)), "nota": (fuente_cam, (120, 120, 120))}.get(tipo, (fuente_cam, (0, 0, 0)))
        if texto and -50 < y < ALTO_VENTANA + 10:
            s_ = fuente.render(texto, True, color)
            pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, int(y)))
        y += 48 if tipo == "titulo" else 36
    return y < 120   # True cuando terminó de pasar todo

def fin_del_juego_y_resumen():
    """Después del relato final: estadísticas y créditos."""
    abrir_resumen(ESTADO_CREDITOS)

# -------------------------------------------------------------
# Tutorial de la noche 1: resalta lo que menciona la llamada
# -------------------------------------------------------------
# índice de la línea de la llamada -> (objetivo, texto)
TUTORIAL_NOCHE1 = {
    1: ("monitor", "[{monitor}] O CLIC: ABRIR LAS CÁMARAS"),
    3: ("puerta", "[{puerta}] O CLIC: COMPUERTA"),
    4: ("persiana", "MANTÉN APRETADO: PERSIANA"),
    5: ("pasillo", "MANTÉN [{linterna}] O CLIC DERECHO: LINTERNA"),
    6: ("techo", "[{techo}]: MIRAR AL TECHO  //  [{bajar}]: VOLVER"),
    7: ("terminal", "[{panel}] O CLIC: PANEL DE MANTENIMIENTO"),
}

def dibujar_tutorial():
    if noche_actual != 1 or not llamada_activa or llamada_muteada or llamada_equivocada:
        return
    paso = TUTORIAL_NOCHE1.get(indice_dialogo)
    if not paso or monitor_abierto or mirando_techo or panel_mantenimiento_abierto:
        return
    objetivo, texto = paso
    texto = TK(texto)
    oficina = {"puerta": RECT_BTN_PUERTA_IZQ, "persiana": RECT_BTN_PERSIANA,
               "pasillo": pygame.Rect(780, 170, 240, 250), "terminal": pygame.Rect(480, 360, 65, 85)}
    pulso = 2 + int(2 * (1 + math.sin(tiempo_juego() * 6)))
    color = (255, 220, 60)
    if objetivo in oficina:
        r_ = oficina[objetivo].move(-int(cam_x), 0).inflate(14, 14)
        if r_.right < 0 or r_.left > ANCHO_VENTANA:
            derecha = r_.left > ANCHO_VENTANA
            flecha = "LLEVA EL MOUSE AL BORDE  >>" if derecha else "<<  LLEVA EL MOUSE AL BORDE"
            s_ = fuente_pequeña.render(flecha, True, color)
            pantalla.blit(s_, (ANCHO_VENTANA - s_.get_width() - 30 if derecha else 30, ALTO_VENTANA // 2))
        else:
            pygame.draw.rect(pantalla, color, r_, pulso, border_radius=6)
            s_ = fuente_pequeña.render(texto, True, color)
            x_ = max(10, min(ANCHO_VENTANA - s_.get_width() - 10, r_.centerx - s_.get_width() // 2))
            y_ = r_.bottom + 8 if r_.bottom + 30 < ALTO_VENTANA - 110 else r_.top - 26
            pantalla.fill((0, 0, 0), (x_ - 6, y_ - 3, s_.get_width() + 12, s_.get_height() + 6))
            pantalla.blit(s_, (x_, y_))
    else:
        r_ = pygame.Rect(ANCHO_VENTANA // 2 - 200, ALTO_VENTANA - 45, 400, 35) if objetivo == "monitor" else pygame.Rect(ANCHO_VENTANA // 2 - 150, 105, 300, 30)
        pygame.draw.rect(pantalla, color, r_.inflate(10, 10), pulso, border_radius=8)
        s_ = fuente_pequeña.render(texto, True, color)
        y_ = r_.top - 34 if objetivo == "monitor" else r_.y + 6
        pantalla.fill((0, 0, 0), (ANCHO_VENTANA // 2 - s_.get_width() // 2 - 6, y_ - 3, s_.get_width() + 12, s_.get_height() + 6))
        pantalla.blit(s_, (ANCHO_VENTANA // 2 - s_.get_width() // 2, y_))

# -------------------------------------------------------------
# 17. Bucle Principal de Juego
# -------------------------------------------------------------
ventana.capa_extra = dibujar_capas_superiores   # Avisos de logros y panel de desarrollador
JUEGO_LISTO = True   # (lo usan las pruebas automáticas)
while True:
    dt = min(reloj.tick(60) / 1000.0, 0.1)
    if progreso.sin_guardar:
        progreso.sin_guardar = False
        guardar_progreso()
    if not pausado:
        reloj_juego += dt
        actualizar_audio_continuo()
    mouse_pos = pygame.mouse.get_pos()
    mouse_click = pygame.mouse.get_pressed()

    if estado_actual == ESTADO_MENU:
        opciones_menu = dibujar_menu_principal()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F1:
                crt_activo = not crt_activo
                AJUSTES["crt"] = crt_activo
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                alternar_pantalla_completa()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for tipo, rect, habilitado in opciones_menu:
                    if rect.collidepoint(mouse_pos) and habilitado:
                        reproducir_sonido(sfx_linterna)
                        if tipo == "NUEVO":
                            progreso.stats["muertes_partida"] = 0
                            mostrar_relato(INTRO_JUEGO["titulo"], INTRO_JUEGO["lineas"], lambda: presentar_noche(1), fondo=fondo_relato_oficina())
                        elif tipo == "NOCHE6":
                            presentar_noche(6)
                        elif tipo == "EXTRAS":
                            estado_actual = ESTADO_EXTRAS
                        elif tipo == "CONTINUAR":
                            presentar_noche(min(noche_desbloqueada, 5))
                        elif tipo == "ARCHIVO":
                            estado_actual = ESTADO_ARCHIVO
                        elif tipo == "CUSTOM":
                            estado_actual = ESTADO_CUSTOM
                        elif tipo == "AJUSTES":
                            ajustes_volver_a = "MENU"
                            ajustes_seleccion = 0
                            estado_actual = ESTADO_AJUSTES
                        elif tipo == "SALIR":
                            pygame.quit()
                            sys.exit()

        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_CUSTOM:
        controles_ia, btn_iniciar, btn_volver, botones_desafio, btn_infinito = dibujar_menu_custom()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F1:
                crt_activo = not crt_activo
                AJUSTES["crt"] = crt_activo
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                alternar_pantalla_completa()
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_volver.collidepoint(mouse_pos):
                    estado_actual = ESTADO_MENU
                if btn_iniciar.collidepoint(mouse_pos):
                    comenzar_noche("CUSTOM")
                elif btn_infinito.collidepoint(mouse_pos):
                    reproducir_sonido(sfx_linterna)
                    comenzar_noche("INFINITO")
                for d_, rb in botones_desafio:
                    if rb.collidepoint(mouse_pos):
                        desafio_elegido = None if desafio_elegido is d_ else d_
                        reproducir_sonido(sfx_linterna)
                for nombre, r_menos, r_mas in controles_ia:
                    if (r_menos.collidepoint(mouse_pos) or r_mas.collidepoint(mouse_pos)) and desafio_elegido:
                        ia_custom.update(desafio_elegido["ia"])   # Parte de los valores del desafío
                        desafio_elegido = None
                    if r_menos.collidepoint(mouse_pos):
                        ia_custom[nombre] = max(0, ia_custom[nombre] - 1)
                        guardar_progreso()
                        reproducir_sonido(sfx_linterna)
                    elif r_mas.collidepoint(mouse_pos):
                        ia_custom[nombre] = min(20, ia_custom[nombre] + 1)
                        guardar_progreso()
                        reproducir_sonido(sfx_linterna)

        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_VICTORIA:
        t_transcurrido = tiempo_juego() - tiempo_inicio_6am
        if t_transcurrido >= 0.2 and not campanas_tocadas[0]:
            reproducir_sonido(sfx_campana_1)
            campanas_tocadas[0] = True
        if t_transcurrido >= 1.0 and not campanas_tocadas[1]:
            reproducir_sonido(sfx_campana_2)
            campanas_tocadas[1] = True
        if t_transcurrido >= 1.8 and not campanas_tocadas[2]:
            reproducir_sonido(sfx_campana_3)
            campanas_tocadas[2] = True

        dibujar_pantalla_victoria(t_transcurrido)
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if t_transcurrido >= 2.5:
                    t_transcurrido = 99   # Salta directo a lo que sigue (abajo)

        if t_transcurrido >= 3.6:
            if noche_actual == 5:
                final_actual = FINAL_VERDADERO if len(evidencias) == 4 else FINAL_NORMAL
                estado_actual = ESTADO_PERIODICO
                tiempo_inicio_periodico = tiempo_juego()
            elif isinstance(noche_actual, int) and noche_actual < 5:
                iniciar_minijuego(noche_actual, "NOCHE")
            elif noche_actual == 6:
                mostrar_relato(FINAL_NOCHE6["titulo"], FINAL_NOCHE6["lineas"], fin_del_juego_y_resumen, (220, 60, 60))
            else:
                estado_actual = ESTADO_MENU

        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_PERIODICO:
        dibujar_pantalla_periodico()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F1:
                crt_activo = not crt_activo
                AJUSTES["crt"] = crt_activo
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                alternar_pantalla_completa()
            if (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1) or (evento.type == pygame.KEYDOWN and evento.key in [pygame.K_SPACE, pygame.K_RETURN]):
                if tiempo_juego() - tiempo_inicio_periodico >= 1.5:
                    color_final = (255, 210, 90) if final_actual is FINAL_VERDADERO else (220, 70, 70)
                    if final_actual is FINAL_VERDADERO and not final_verdadero_visto:
                        final_verdadero_visto = True
                        noche6_desbloqueada = True
                        progreso.desbloquear("fin_del_turno")
                        guardar_progreso()
                    lineas_final = list(final_actual["lineas"])
                    if final_actual is FINAL_VERDADERO:
                        lineas_final += ["", "(NOCHE 6 DESBLOQUEADA EN EL MENÚ)"]
                    mostrar_relato(final_actual["titulo"], lineas_final, fin_del_juego_y_resumen, color_final)

        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_MINIJUEGO:
        eventos_mj = pygame.event.get()
        for evento in eventos_mj:
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F1:
                crt_activo = not crt_activo
                AJUSTES["crt"] = crt_activo
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                alternar_pantalla_completa()

        minijuego_actual.actualizar(dt, eventos_mj, pygame.key.get_pressed())
        minijuego_actual.dibujar(pantalla)
        if minijuego_actual.terminado:
            if not minijuego_actual.salteado:
                progreso.stats["cintas_completadas"] += 1
                progreso.stats["cintas_fallos"] += minijuego_actual.intentos
                if minijuego_actual.prueba and minijuego_actual.intentos == 0:
                    progreso.desbloquear("una_toma")
            if minijuego_numero == 0:
                # La cinta secreta tiene su propia prueba: no cuenta para el final verdadero
                if minijuego_actual.prueba:
                    progreso.stats["cinta0_prueba"] = True
                if not minijuego_actual.salteado:
                    progreso.desbloquear("del_otro_lado")
            elif minijuego_actual.prueba and minijuego_numero not in evidencias:
                evidencias.add(minijuego_numero)
            if len(evidencias) == 4:
                progreso.desbloquear("archivista")
            guardar_progreso()
            estado_actual = ESTADO_ARCHIVO if minijuego_origen == "ARCHIVO" else ESTADO_MENU
        aberracion_mj = 3 if minijuego_actual.flash > 0 else 1
        aplicar_postprocesado_crt(dt, intensidad_aberracion=aberracion_mj)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_RELATO:
        eventos_r = pygame.event.get()
        for evento in eventos_r:
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
                alternar_pantalla_completa()
        relato_actual.actualizar(dt, eventos_r)
        relato_actual.dibujar(pantalla)
        if relato_actual.terminado:
            relato_despues()
        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_TITULO_NOCHE:
        dibujar_titulo_noche()
        saltar = False
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (evento.type == pygame.KEYDOWN and evento.key not in (pygame.K_F1, pygame.K_F11)) or (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1):
                saltar = tiempo_juego() - t_titulo_noche > 0.4
        if saltar or tiempo_juego() - t_titulo_noche >= 3.4:
            comenzar_noche(noche_a_presentar)
        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_EXTRAS:
        botones_ex = dibujar_extras()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                estado_actual = ESTADO_MENU
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for clave_b, rect_b, habil in botones_ex:
                    if habil and rect_b.collidepoint(evento.pos):
                        reproducir_sonido(sfx_linterna)
                        if clave_b == "ARCHIVO":
                            estado_actual = ESTADO_ARCHIVO
                        elif clave_b == "LOGROS":
                            estado_actual = ESTADO_LOGROS
                        elif clave_b == "ESTADISTICAS":
                            abrir_resumen(ESTADO_EXTRAS)
                        elif clave_b == "CREDITOS":
                            abrir_creditos(ESTADO_EXTRAS)
                        else:
                            estado_actual = ESTADO_MENU
        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_LOGROS:
        dibujar_logros()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE) or \
               (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and RECT_VOLVER_ABAJO.collidepoint(evento.pos)):
                reproducir_sonido(sfx_linterna)
                estado_actual = ESTADO_EXTRAS
        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_RESUMEN:
        dibujar_resumen()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            salir = (evento.type == pygame.KEYDOWN and evento.key in (pygame.K_ESCAPE, pygame.K_SPACE, pygame.K_RETURN)) or \
                    (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1 and RECT_VOLVER_ABAJO.collidepoint(evento.pos))
            if salir:
                reproducir_sonido(sfx_linterna)
                if resumen_volver_a == ESTADO_CREDITOS:
                    abrir_creditos(ESTADO_MENU)
                else:
                    estado_actual = resumen_volver_a
        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_CREDITOS:
        terminaron = dibujar_creditos()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if (evento.type == pygame.KEYDOWN and evento.key not in (pygame.K_F1, pygame.K_F11)) or (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1):
                terminaron = True
        if terminaron:
            estado_actual = creditos_volver_a
        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_ARCHIVO:
        dibujar_archivo()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                estado_actual = ESTADO_EXTRAS
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if RECT_ARCHIVO_VOLVER.collidepoint(evento.pos):
                    reproducir_sonido(sfx_linterna)
                    estado_actual = ESTADO_EXTRAS
                for n, rect in zip(numeros_archivo(), botones_archivo()):
                    if rect.collidepoint(evento.pos) and cinta_disponible(n):
                        reproducir_sonido(sfx_linterna)
                        iniciar_minijuego(n, "ARCHIVO")
        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_CONTROLES:
        dibujar_controles()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                guardar_ajustes(AJUSTES)
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and controles_escuchando:
                if evento.key != pygame.K_ESCAPE:
                    if mapa_teclas.asignar(controles_escuchando, evento.key):
                        reproducir_sonido(sfx_reboot_click)
                        guardar_ajustes(AJUSTES)
                    else:
                        controles_aviso, controles_aviso_hasta = T("ESA TECLA NO SE PUEDE USAR"), tiempo_juego() + 2.0
                        reproducir_sonido(sfx_alarma_error, 0.4, 0.4)
                controles_escuchando = None
                continue
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    guardar_ajustes(AJUSTES)
                    estado_actual = ESTADO_AJUSTES
                elif evento.key == pygame.K_UP:
                    controles_seleccion = (controles_seleccion - 1) % len(mapa_teclas.ACCIONES)
                elif evento.key == pygame.K_DOWN:
                    controles_seleccion = (controles_seleccion + 1) % len(mapa_teclas.ACCIONES)
                elif evento.key == pygame.K_RETURN:
                    controles_escuchando = mapa_teclas.ACCIONES[controles_seleccion][0]
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if RECT_CT_VOLVER.collidepoint(evento.pos):
                    guardar_ajustes(AJUSTES)
                    reproducir_sonido(sfx_linterna)
                    estado_actual = ESTADO_AJUSTES
                elif RECT_CT_RESTABLECER.collidepoint(evento.pos):
                    mapa_teclas.restablecer()
                    guardar_ajustes(AJUSTES)
                    reproducir_sonido(sfx_reboot_click)
                for i, fila in enumerate(filas_controles()):
                    if fila.collidepoint(evento.pos):
                        controles_seleccion = i
                        controles_escuchando = mapa_teclas.ACCIONES[i][0]
                        reproducir_sonido(sfx_linterna)
        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_AJUSTES:
        dibujar_menu_ajustes()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                guardar_ajustes(AJUSTES)
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                    salir_de_ajustes()
                elif evento.key in (pygame.K_UP, pygame.K_w):
                    ajustes_seleccion = (ajustes_seleccion - 1) % len(OPCIONES_AJUSTES)
                elif evento.key in (pygame.K_DOWN, pygame.K_s):
                    ajustes_seleccion = (ajustes_seleccion + 1) % len(OPCIONES_AJUSTES)
                elif evento.key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN, pygame.K_SPACE):
                    d = -1 if evento.key in (pygame.K_LEFT, pygame.K_a) else 1
                    cambiar_ajuste(OPCIONES_AJUSTES[ajustes_seleccion][0], d)
                    reproducir_sonido(sfx_linterna)
                elif evento.key == pygame.K_F11:
                    cambiar_ajuste("pantalla_completa")
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if RECT_AJ_VOLVER.collidepoint(evento.pos):
                    salir_de_ajustes()
                elif RECT_AJ_CONTROLES.collidepoint(evento.pos):
                    reproducir_sonido(sfx_linterna)
                    abrir_controles()
                elif RECT_AJ_RESTABLECER.collidepoint(evento.pos):
                    for k, v in AJUSTES_POR_DEFECTO.items():
                        if AJUSTES[k] != v:
                            AJUSTES[k] = v
                    crt_activo = AJUSTES["crt"]
                    mapa_teclas.cargar(AJUSTES)
                    ventana.aplicar_modo()
                    aplicar_idioma()
                    reproducir_sonido(sfx_reboot_click)
                for i, (clave, _, tipo, params) in enumerate(OPCIONES_AJUSTES):
                    fila, menos, mas, barra = controles_fila_ajuste(i)
                    if not fila.collidepoint(evento.pos):
                        continue
                    ajustes_seleccion = i
                    if menos.collidepoint(evento.pos):
                        cambiar_ajuste(clave, -1)
                    elif mas.collidepoint(evento.pos):
                        cambiar_ajuste(clave, 1)
                    elif tipo != "barra" and evento.pos[0] >= X_CONTROL:
                        cambiar_ajuste(clave, 1)
                    reproducir_sonido(sfx_linterna)
            if evento.type == pygame.MOUSEMOTION:
                for i in range(len(OPCIONES_AJUSTES)):
                    if controles_fila_ajuste(i)[0].collidepoint(evento.pos):
                        ajustes_seleccion = i
        # Arrastrar las barras con el mouse
        if mouse_click[0]:
            for i, (clave, _, tipo, params) in enumerate(OPCIONES_AJUSTES):
                if tipo != "barra":
                    continue
                barra = controles_fila_ajuste(i)[3]
                if barra.inflate(16, 22).collidepoint(mouse_pos):
                    mn, mx, _, _ = params
                    t = max(0.0, min(1.0, (mouse_pos[0] - barra.x) / barra.width))
                    cambiar_ajuste(clave, valor=mn + t * (mx - mn))
        if estado_actual == ESTADO_AJUSTES:
            aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    # JUGANDO (Turno Activo)
    if pausado:
        pantalla.blit(captura_pausa, (0, 0))
        botones_pausa = dibujar_menu_pausa()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            accion = None
            if evento.type == pygame.KEYDOWN and mapa_teclas.es("pausa", evento.key):
                accion = "CONTINUAR"
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for nombre_b, rect_b in botones_pausa:
                    if rect_b.collidepoint(evento.pos):
                        accion = nombre_b
            if accion == "AJUSTES":
                reproducir_sonido(sfx_reboot_click)
                ajustes_volver_a = "PAUSA"
                ajustes_seleccion = 0
                estado_actual = ESTADO_AJUSTES
                break
            if accion:
                pausado = False
                pygame.mixer.unpause()
                reproducir_sonido(sfx_reboot_click)
                if accion == "REINTENTAR":
                    comenzar_noche(noche_actual)
                elif accion == "MENU":
                    pygame.mixer.stop()
                    estado_actual = ESTADO_MENU
        if estado_actual == ESTADO_JUEGO:
            pygame.display.flip()
        continue

    rect_toggle_camara = pygame.Rect(ANCHO_VENTANA//2 - 200, ALTO_VENTANA - 45, 400, 35)
    btn_modo_rect = pygame.Rect(840, 345, 330, 36)
    btn_lure_rect = pygame.Rect(840, 305, 330, 32)
    rect_btn_bobina = RECT_BTN_BOBINA

    if lure_cooldown > 0:
        lure_cooldown = max(0.0, lure_cooldown - dt)
    if trampa_cooldown > 0:
        trampa_cooldown = max(0.0, trampa_cooldown - dt)

    if monitor_abierto and progreso_monitor < 1.0:
        progreso_monitor = min(1.0, progreso_monitor + (dt / DURACION_TRANSICION_MONITOR))
    elif not monitor_abierto and progreso_monitor > 0.0:
        progreso_monitor = max(0.0, progreso_monitor - (dt / DURACION_TRANSICION_MONITOR))

    if persiana_der_sostenida and progreso_persiana < 1.0:
        progreso_persiana = min(1.0, progreso_persiana + VEL_TRANSICION_PERSIANA * dt)
    elif not persiana_der_sostenida and progreso_persiana > 0.0:
        progreso_persiana = max(0.0, progreso_persiana - VEL_TRANSICION_PERSIANA * dt)

    if not juego_terminado and not en_jumpscare and not en_apagon:
        if bobina_cargando and monitor_abierto and progreso_monitor >= 0.95 and not modo_ventilacion and camara_seleccionada == "CAM_08":
            bobina_generador = min(100.0, bobina_generador + 24.0 * dt)
            reproducir_sonido(sfx_bobina_cuerda, 0.4, 0.4)
        else:
            # La bobina se presenta en la llamada de la noche 3: antes no se descarga
            drenaje_bobina = 0.0 if noche_actual in [1, 2] else (3.2 if noche_actual in [3, 4] else 4.2)
            bobina_generador = max(0.0, bobina_generador - drenaje_bobina * dt)

        if bobina_generador <= 0.0:
            if not apagon_bobina_activo:
                apagon_bobina_activo = True
                tiempo_inicio_apagon_bobina = tiempo_juego()
                reproducir_sonido(sfx_apagon_down)
        else:
            apagon_bobina_activo = False

        if tiempo_juego() >= tiempo_siguiente_fallo:
            fallo_elegido = random.choice(["VENT", "CAM"])
            if fallo_elegido == "VENT" and not error_ventilacion:
                error_ventilacion = True
                reproducir_sonido(sfx_alarma_error)
                subtitulo("ALARMA: FALLA DE VENTILACIÓN", 0, 3.0)
            elif fallo_elegido == "CAM" and not error_camaras:
                error_camaras = True
                reproducir_sonido(sfx_alarma_error)
                subtitulo("ALARMA: FALLA DE CÁMARAS", 0, 3.0)
            tiempo_siguiente_fallo = tiempo_juego() + random.uniform(*intervalo_fallas(base=(25.0, 50.0)))

    if reboot_activo and not en_apagon:
        if tiempo_juego() - reboot_tiempo_inicio >= DURACION_REBOOT:
            if reboot_activo in ["VENT", "ALL"]:
                error_ventilacion = False
            if reboot_activo in ["CAM", "ALL"]:
                error_camaras = False
            reboot_activo = None
            reproducir_sonido(sfx_reboot_click)

    lista_dialogos_actual = llamada_lista
    if llamada_activa and not llamada_muteada and not en_apagon:
        ahora = tiempo_juego()
        if indice_dialogo == 0 and ahora - tiempo_repique >= 2.2:
            reproducir_sonido(sfx_timbre)
            subtitulo("TELÉFONO SONANDO", 0, 2.3)
            tiempo_repique = ahora
        if ahora - tiempo_ultimo_texto >= 5.5:
            tiempo_ultimo_texto = ahora
            indice_dialogo += 1
            if indice_dialogo >= len(lista_dialogos_actual):
                llamada_activa = False
                if isinstance(noche_actual, int) and not llamada_equivocada:
                    progreso.agregar_a_lista("llamadas_completas", noche_actual)
                    progreso.revisar_contadores()

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F1:
            crt_activo = not crt_activo
            AJUSTES["crt"] = crt_activo

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F11:
            alternar_pantalla_completa()

        if evento.type == pygame.KEYDOWN and mapa_teclas.es("pausa", evento.key) and not juego_terminado and not en_jumpscare:
            pausado = True
            captura_pausa = pantalla.copy()
            pygame.mixer.pause()
            continue

        if not juego_terminado and not en_jumpscare and not en_apagon:
            if evento.type == pygame.KEYDOWN:
                if mapa_teclas.es("panel", evento.key) and not monitor_abierto and not mirando_techo:
                    panel_mantenimiento_abierto = not panel_mantenimiento_abierto
                    reproducir_sonido(sfx_reboot_click)

                if not panel_mantenimiento_abierto:
                    if mapa_teclas.es("monitor", evento.key) and not mirando_techo:
                        monitor_abierto = not monitor_abierto
                        reproducir_sonido(sfx_monitor_movimiento)
                        reproducir_sonido(sfx_estatica_cctv)
                    if monitor_abierto and mapa_teclas.es("vision", evento.key) and not ir_agotado and not modificadores.get("sin_ir"):
                        vision_nocturna_cam = not vision_nocturna_cam
                        reproducir_sonido(sfx_linterna)
                    if not monitor_abierto:
                        if mapa_teclas.es("techo", evento.key):
                            mirando_techo = True
                        elif mapa_teclas.es("bajar", evento.key):
                            mirando_techo = False
                        elif mirando_techo and mapa_teclas.es("sellar", evento.key):
                            ventilacion_sellada = not ventilacion_sellada
                            reproducir_sonido(sfx_puerta)
                        if not mirando_techo and mapa_teclas.es("puerta", evento.key):
                            alternar_puerta()

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if panel_mantenimiento_abierto:
                    btn_rv, btn_rc, btn_rall, btn_close = dibujar_panel_mantenimiento()
                    if btn_rv.collidepoint(mouse_pos) and not reboot_activo:
                        reboot_activo = "VENT"
                        progreso.sumar("reinicios_sistema")
                        reboot_tiempo_inicio = tiempo_juego()
                        reproducir_sonido(sfx_reboot_click)
                    elif btn_rc.collidepoint(mouse_pos) and not reboot_activo:
                        reboot_activo = "CAM"
                        progreso.sumar("reinicios_sistema")
                        reboot_tiempo_inicio = tiempo_juego()
                        reproducir_sonido(sfx_reboot_click)
                    elif btn_rall.collidepoint(mouse_pos) and not reboot_activo:
                        reboot_activo = "ALL"
                        progreso.sumar("reinicios_sistema")
                        reboot_tiempo_inicio = tiempo_juego()
                        reproducir_sonido(sfx_reboot_click)
                    elif btn_close.collidepoint(mouse_pos):
                        panel_mantenimiento_abierto = False
                        reproducir_sonido(sfx_reboot_click)
                else:
                    rect_mute_btn = pygame.Rect(775, 20, 140, 82)
                    if llamada_activa and not llamada_muteada and rect_mute_btn.collidepoint(mouse_pos):
                        llamada_muteada = True
                        CANAL_VOZ.stop()
                        reproducir_sonido(sfx_timbre)

                    if rect_toggle_camara.collidepoint(mouse_pos) and not mirando_techo:
                        monitor_abierto = not monitor_abierto
                        reproducir_sonido(sfx_monitor_movimiento)
                        reproducir_sonido(sfx_estatica_cctv)

                    if monitor_abierto and progreso_monitor >= 0.8:
                        if btn_modo_rect.collidepoint(mouse_pos):
                            modo_ventilacion = not modo_ventilacion
                            camara_seleccionada = "VENT_01" if modo_ventilacion else "CAM_01"
                            reproducir_sonido(sfx_estatica_cctv)

                        if modo_ventilacion and btn_lure_rect.collidepoint(mouse_pos) and lure_cooldown <= 0.0:
                            lure_cooldown = 10.0
                            progreso.sumar("senuelos")
                            reproducir_sonido(sfx_lure_audio, 0.7, 0.7)
                            if silas.sala().startswith("VENT"):
                                silas.nodo_actual = max(1, silas.nodo_actual - 1)
                                reproducir_sonido(sfx_conducto_metal, 0.6, 0.6)

                        if evento.button == 3 and not modo_ventilacion and not ir_agotado and not modificadores.get("sin_ir") and (100 <= mouse_pos[0] <= 820 and 80 <= mouse_pos[1] <= 560):
                            vision_nocturna_cam = not vision_nocturna_cam
                            reproducir_sonido(sfx_linterna)

                        dict_actual = CAMARAS_VENT if modo_ventilacion else CAMARAS_PLANTA
                        for cam_id, data in dict_actual.items():
                            if data["rect"].collidepoint(mouse_pos):
                                if evento.button == 1:
                                    camara_seleccionada = cam_id
                                    progreso.sumar("camaras_vistas")
                                    # Secreto: muy rara vez algo pasa frente a la cámara
                                    if isinstance(noche_actual, int) and noche_actual >= 2 and not modo_ventilacion and random.random() < 1 / 45:
                                        fantasma_cam, fantasma_hasta = cam_id, tiempo_juego() + 1.3
                                        reproducir_sonido(sfx_glitch_8bit, 0.6, 0.6)
                                        progreso.desbloquear("fantasma")
                                    reproducir_sonido(sfx_estatica_cctv)
                                elif evento.button == 3 and modo_ventilacion:
                                    if trampa_ducto == cam_id:
                                        trampa_ducto = None  # Reabrir la compuerta manualmente
                                        reproducir_sonido(sfx_puerta)
                                    elif trampa_ducto is None and trampa_cooldown <= 0.0:
                                        trampa_ducto = cam_id
                                        reproducir_sonido(sfx_puerta)
                    elif not mirando_techo and progreso_monitor <= 0.2:
                        x_of = mouse_pos[0] + cam_x
                        y_of = mouse_pos[1]
                        if 480 <= x_of <= 545 and 360 <= y_of <= 445:
                            panel_mantenimiento_abierto = True
                            reproducir_sonido(sfx_reboot_click)
                        if RECT_BTN_PUERTA_IZQ.collidepoint(x_of, y_of):
                            alternar_puerta()
                        if RECT_BTN_LUZ_IZQ.collidepoint(x_of, y_of):
                            luz_izq = not luz_izq
                            reproducir_sonido(sfx_linterna, 0.9, 0.2)
                        if RECT_BTN_PERSIANA.collidepoint(x_of, y_of):
                            if not persiana_der_sostenida:
                                tiempo_inicio_persiana = tiempo_juego()
                                progreso.sumar("persianas")
                                reproducir_sonido(sfx_persiana, 0.2, 0.9)
                            persiana_der_sostenida = True
                        if RECT_BTN_LUZ_DER.collidepoint(x_of, y_of):
                            luz_der = not luz_der
                            reproducir_sonido(sfx_linterna, 0.2, 0.9)

        elif juego_terminado:
            accion = None
            if evento.type == pygame.KEYDOWN:
                if evento.key in [pygame.K_r, pygame.K_SPACE, pygame.K_RETURN]:
                    accion = "REINTENTAR"
                elif evento.key == pygame.K_ESCAPE:
                    accion = "MENU"
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if RECT_BTN_REINTENTAR.collidepoint(evento.pos):
                    accion = "REINTENTAR"
                elif RECT_BTN_MENU_MUERTE.collidepoint(evento.pos):
                    accion = "MENU"
            if accion == "REINTENTAR":
                reproducir_sonido(sfx_linterna)
                comenzar_noche(noche_actual)
            elif accion == "MENU":
                reproducir_sonido(sfx_linterna)
                estado_actual = ESTADO_MENU

    if en_jumpscare:
        tiempo_transcurrido = tiempo_juego() - tiempo_inicio_jumpscare
        progreso_js = min(1.0, tiempo_transcurrido / DURACION_JUMPSCARE)
        amp_shake = max(1, int(intensidad_shake * (1.0 - progreso_js)))
        shake_x = random.randint(-amp_shake, amp_shake)
        shake_y = random.randint(-amp_shake, amp_shake)
        dibujar_jumpscare(progreso_js)
        pantalla.blit(pantalla.copy(), (shake_x, shake_y))
        if progreso_js >= 1.0:
            en_jumpscare = False
            juego_terminado = True

        aplicar_postprocesado_crt(dt, intensidad_aberracion=6)
        pygame.display.flip()
        continue

    if juego_terminado:
        if estado_actual == ESTADO_JUEGO:
            dibujar_pantalla_muerte()
            aplicar_postprocesado_crt(dt, intensidad_aberracion=2)
            pygame.display.flip()
        continue

    if monitor_abierto and progreso_monitor >= 0.8 and not modo_ventilacion and camara_seleccionada == "CAM_08":
        bobina_cargando = mouse_click[0] and rect_btn_bobina.collidepoint(mouse_pos)
    else:
        bobina_cargando = False

    if not monitor_abierto and not mirando_techo and not panel_mantenimiento_abierto and not en_apagon and mouse_click[0] and progreso_monitor <= 0.2:
        x_of = mouse_pos[0] + cam_x
        y_of = mouse_pos[1]
        if RECT_BTN_PERSIANA.collidepoint(x_of, y_of):
            if not persiana_der_sostenida:
                tiempo_inicio_persiana = tiempo_juego()
                progreso.sumar("persianas")
                reproducir_sonido(sfx_persiana, 0.2, 0.9)
            persiana_der_sostenida = True
        else:
            persiana_der_sostenida = False
    else:
        if persiana_der_sostenida:
            reproducir_sonido(sfx_persiana, 0.2, 0.9)
        persiana_der_sostenida = False

    if glitch_cam_timer > 0:
        glitch_cam_timer = max(0.0, glitch_cam_timer - dt)

    # Carga de la visión nocturna IR
    if monitor_abierto and vision_nocturna_cam and not error_camaras:
        carga_ir = max(0.0, carga_ir - DESCARGA_IR * dt)
        if carga_ir <= 0.0:
            vision_nocturna_cam = False
            ir_agotado = True
            reproducir_sonido(sfx_alarma_error, 0.5, 0.5)
    else:
        carga_ir = min(100.0, carga_ir + RECARGA_IR * dt)
        if ir_agotado and carga_ir >= 40.0:
            ir_agotado = False
            reproducir_sonido(sfx_reboot_click)

    # Pistas de sonido: se escucha dónde está cada uno aunque no lo mires
    if not juego_terminado and not en_jumpscare and not en_apagon:
        ahora_cue = tiempo_juego()
        pistas = []
        if penny.sala() == "PUERTA_IZQ" and not puerta_izq_cerrada:
            pistas.append(("penny", 2.6, sfx_respiracion, 0.45, 0.05, "RESPIRACIÓN DETRÁS DE LA PUERTA", -1))
        if silas.sala() == "REJILLA_OFICINA":
            pistas.append(("silas", 1.7, sfx_golpe_techo, 0.5, 0.5, "GOLPES EN EL TECHO", 0))
        if bunny.sala() == "VENTANA_DER" and progreso_persiana < 0.85:
            pistas.append(("bunny", 2.1, sfx_golpe_vidrio, 0.05, 0.5, "GOLPES EN EL VIDRIO", 1))
        for clave_p, cada, sfx_p, vi, vd, texto_p, lado_p in pistas:
            if ahora_cue - ultimo_aviso_sonoro.get(clave_p, -99) >= cada:
                ultimo_aviso_sonoro[clave_p] = ahora_cue
                reproducir_sonido(sfx_p, vi, vd)
                subtitulo(texto_p, lado_p, cada + 0.3)

    teclas = pygame.key.get_pressed()
    intento_linterna = not monitor_abierto and not mirando_techo and not panel_mantenimiento_abierto and not en_apagon and progreso_monitor <= 0.2 and (mouse_click[2] or mapa_teclas.mantenida("linterna", teclas))

    if intento_linterna and not linterna_sobrecalentada:
        if not linterna_pasillo:
            progreso.sumar("linterna")
        linterna_pasillo = True
        calor_linterna = min(100.0, calor_linterna + 38.0 * dt)
        if calor_linterna >= 100.0:
            linterna_sobrecalentada = True
            linterna_pasillo = False
            reproducir_sonido(sfx_alarma_error)
    else:
        linterna_pasillo = False
        calor_linterna = max(0.0, calor_linterna - 30.0 * dt)
        if calor_linterna <= 20.0:
            linterna_sobrecalentada = False

    barras_uso = 1 if not en_apagon else 0
    if monitor_abierto: barras_uso += 1
    if monitor_abierto and vision_nocturna_cam: barras_uso += 1
    if panel_mantenimiento_abierto: barras_uso += 1
    if puerta_izq_cerrada: barras_uso += 1
    if persiana_der_sostenida: barras_uso += 1
    if linterna_pasillo: barras_uso += 1
    if (luz_izq or luz_der) and not apagon_bobina_activo: barras_uso = min(5, barras_uso + 1)
    barras_uso = min(5, barras_uso)

    if monitor_abierto and progreso_monitor >= 0.8 and vision_nocturna_cam and not error_camaras and not en_apagon:
        if tiempo_juego() - tiempo_ultimo_hum_ir >= 0.38:
            reproducir_sonido(sfx_ir_hum, 0.25, 0.25)
            tiempo_ultimo_hum_ir = tiempo_juego()

    if not juego_terminado:
        if not monitor_abierto and not mirando_techo and not persiana_der_sostenida and not panel_mantenimiento_abierto and progreso_monitor <= 0.2:
            if mouse_pos[0] < 150:
                cam_x -= 650 * AJUSTES["vel_giro"] / 100.0 * dt
            elif mouse_pos[0] > ANCHO_VENTANA - 150:
                cam_x += 650 * AJUSTES["vel_giro"] / 100.0 * dt
            cam_x = max(0, min(cam_x, ANCHO_OFICINA - ANCHO_VENTANA))

        progreso.stats["tiempo_jugado"] += dt
        if modificadores.get("puerta_limitada") and puerta_izq_cerrada:
            puerta_t_cerrada += dt
            if puerta_t_cerrada >= 5.0:
                puerta_izq_cerrada = False
                puerta_trabada_hasta = tiempo_juego() + 4.0
                reproducir_sonido(sfx_alarma_error, 0.8, 0.1)
        if not en_apagon:
            mult_bat = 1.0 if noche_actual in ("CUSTOM", "INFINITO") else DIFICULTADES.get(AJUSTES.get("dificultad"), DIFICULTADES["normal"])["bateria"]
            bateria -= (barras_uso * 0.14) * mult_bat * dt
            if bateria <= 0:
                bateria = 0
                en_apagon = True
                tiempo_inicio_apagon = tiempo_juego()
                tiempo_ultima_nota_apagon = tiempo_juego()
                monitor_abierto = False
                progreso_monitor = 0.0
                panel_mantenimiento_abierto = False
                mirando_techo = False
                puerta_izq_cerrada = False
                persiana_der_sostenida = False
                ventilacion_sellada = False
                linterna_pasillo = False
                luz_izq = False
                luz_der = False
                reproducir_sonido(sfx_apagon_down)
        else:
            t_ap = tiempo_juego() - tiempo_inicio_apagon
            if 2.5 < t_ap < 12.0 and caja_musica:
                if indice_nota_apagon == 0:
                    indice_nota_apagon = 1
                    reproducir_sonido(caja_musica, 0.6, 0.6)
                    subtitulo("UNA CAJA DE MÚSICA EN LA OSCURIDAD", -1, 9.0)
            elif 2.5 < t_ap < 12.0:
                if tiempo_juego() - tiempo_ultima_nota_apagon >= 0.75:
                    tiempo_ultima_nota_apagon = tiempo_juego()
                    nota = NOTAS_CAJA_MUSICA[indice_nota_apagon % len(NOTAS_CAJA_MUSICA)]
                    reproducir_sonido(nota, 0.5, 0.5)
                    indice_nota_apagon += 1
            elif t_ap >= 13.5:
                iniciar_jumpscare("Barnaby", "SIN ENERGÍA: BARNABY TE ATRAPÓ EN LA OSCURIDAD")

        if not en_apagon:
            if ventilacion_sellada or error_ventilacion:
                velocidad_caida_ox = 6.0 if (ventilacion_sellada and error_ventilacion) else 3.8
                if modificadores.get("oxigeno_rapido"):
                    velocidad_caida_ox *= 1.6
                oxigeno -= velocidad_caida_ox * dt
                if oxigeno <= 0:
                    oxigeno = 0
                    juego_terminado = True
                    mensaje_muerte = "FALLO EN VENTILACIÓN: ASFIXIA POR GASES INDUSTRIALES"
                    animatronico_atacante = ""
                    progreso.muerte("Asfixia")
                    registrar_infinito()
                    guardar_progreso()
            else:
                oxigeno = min(100.0, oxigeno + (3.3 if modificadores.get("oxigeno_rapido") else 5.5) * dt)

            barnaby.actualizar()
            # Unidad 0 (noche 6): solo se mueve si nadie la mira
            mirando = camara_seleccionada if (monitor_abierto and progreso_monitor >= 0.95 and not modo_ventilacion and not error_camaras) else None
            evento_u0 = unidad0.actualizar(0.0 if dev_congelados else dt, mirando)
            if evento_u0 == "avanzo":
                reproducir_sonido(sfx_estatica_cctv, 0.7, 0.7)
                subtitulo("INTERFERENCIA EN LAS CÁMARAS", 0)
                if mirando:
                    glitch_cam_timer = 0.45
            elif evento_u0 == "rechazada":
                progreso.sumar("unidad0_rechazada")
                reproducir_sonido(sfx_ir_lock, 0.8, 0.8)
            elif evento_u0 == "ataque":
                iniciar_jumpscare("Unidad 0", "LA UNIDAD 0 TE ESTABA MIRANDO")
            if unidad0.nervios() > 0.7 and tiempo_juego() - ultimo_aviso_unidad0 > 1.2:
                ultimo_aviso_unidad0 = tiempo_juego()
                subtitulo("ESTÁTICA... ALGO SE MUEVE", 0, 1.5)
                reproducir_sonido(sfx_estatica_cctv, 0.25, 0.25)
            silas.actualizar()
            penny.actualizar()
            bunny.actualizar()

            # Compuerta de ducto: funciona en cualquier ducto. Si Silas está en el ducto
            # cerrado, vuelve al inicio, la compuerta se reabre y hay que esperar para rearmarla.
            if trampa_ducto and silas.sala() == trampa_ducto:
                silas.volver_al_inicio()
                progreso.sumar("silas_atrapado")
                trampa_ducto = None
                trampa_cooldown = COOLDOWN_TRAMPA
                reproducir_sonido(sfx_conducto_metal, 0.5, 0.5)

            if linterna_pasillo and barnaby.nodo_actual in [2, 3]:
                progreso_cegado_barnaby += dt
                if progreso_cegado_barnaby >= 1.4:
                    barnaby.volver_al_inicio()
                    progreso.sumar("barnaby_cegado")
                    progreso_cegado_barnaby = 0.0
                    reproducir_sonido(sfx_paso_metal, 0.5, 0.5)
            else:
                progreso_cegado_barnaby = max(0.0, progreso_cegado_barnaby - 0.8 * dt)

            if bunny.nodo_actual == 4:
                if persiana_der_sostenida and progreso_persiana >= 0.85 and (tiempo_juego() - tiempo_inicio_persiana >= 2.0):
                    bunny.volver_al_inicio()
                    progreso.sumar("bunny_rechazado")
                    bunny.tiempo_en_ataque = 0.0
                    reproducir_sonido(sfx_paso_metal, 0.1, 0.9)
                else:
                    bunny.tiempo_en_ataque += dt
                    if bunny.tiempo_en_ataque >= 7.0 and (not persiana_der_sostenida or progreso_persiana < 0.85):
                        bunny.nodo_actual = 5

            if penny.nodo_actual == 3:
                if puerta_izq_cerrada:
                    penny.volver_al_inicio()
                    progreso.sumar("penny_bloqueada")
                    penny.tiempo_en_ataque = 0.0
                    reproducir_sonido(sfx_paso_metal, 0.9, 0.1)
                else:
                    penny.tiempo_en_ataque += dt
                    if penny.tiempo_en_ataque >= 6.5:
                        penny.nodo_actual = 4

            if barnaby.nodo_actual == 4:
                iniciar_jumpscare("Barnaby", "BARNABY TE ALCANZÓ EN EL ESCRITORIO")
            elif silas.sala() == "OFICINA":
                if not ventilacion_sellada:
                    iniciar_jumpscare("Silas", "SILAS CAYÓ DE LA VENTILACIÓN SUPERIOR")
                else:
                    silas.volver_al_inicio()
            elif penny.nodo_actual == 4:
                iniciar_jumpscare("Penny", "PENNY ENTRÓ POR LA PUERTA IZQUIERDA")
            elif bunny.nodo_actual == 5:
                iniciar_jumpscare("Rusty Bunny", "RUSTY BUNNY DESTRUYÓ EL CRISTAL DE LA VENTANA")

        segundos_pasados = tiempo_juego() - tiempo_inicio
        hora = 12 + int(segundos_pasados // DURACION_HORA_SEGUNDOS)
        if hora > 12: hora -= 12

        # Más agresivos a las 2, 3 y 4 AM (solo en las noches de la historia)
        con_bonus = noche_actual not in ("CUSTOM", "INFINITO") and DIFICULTADES.get(AJUSTES.get("dificultad"), DIFICULTADES["normal"])["bonus_hora"]
        bonus = {2: 1, 3: 2, 4: 3, 5: 3}.get(hora, 0) if con_bonus else 0
        for a in (barnaby, silas, penny, bunny):
            a.bonus_hora = bonus

        if es_infinito():
            while infinito_horas < int(segundos_pasados // DURACION_HORA_SEGUNDOS) and not juego_terminado and not en_jumpscare:
                avanzar_hora_infinito()
        elif segundos_pasados >= DURACION_HORA_SEGUNDOS * 6:
            tiempo_inicio_6am = tiempo_juego()
            campanas_tocadas = [False, False, False]
            registrar_fin_de_noche()
            if isinstance(noche_actual, int) and noche_actual == noche_desbloqueada and noche_desbloqueada < 5:
                noche_desbloqueada += 1
            if noche_actual == 5:
                juego_completado_5_noches = True
            if noche_actual == "CUSTOM" and all(v == 20 for v in ia_custom.values()):
                record_20_20_20_20 = True
            guardar_progreso()
            estado_actual = ESTADO_VICTORIA

    if panel_mantenimiento_abierto:
        dibujar_panel_mantenimiento()
    elif mirando_techo:
        dibujar_vista_techo()
    else:
        dibujar_oficina()
        pantalla.blit(superficie_oficina, (0, 0), (int(cam_x), 0, ANCHO_VENTANA, ALTO_VENTANA))
        dibujar_parpadeo_luz()

        if progreso_monitor > 0.0:
            dibujar_sistema_camaras()
            alto_recorte = int(ALTO_VENTANA * progreso_monitor)
            y_origen_feed = ALTO_VENTANA - alto_recorte

            pantalla.blit(pantalla_camaras, (0, y_origen_feed), (0, 0, ANCHO_VENTANA, alto_recorte))

            pygame.draw.rect(pantalla, (45, 55, 65), (0, y_origen_feed - 14, ANCHO_VENTANA, 14))
            pygame.draw.line(pantalla, (110, 130, 150), (0, y_origen_feed - 14), (ANCHO_VENTANA, y_origen_feed - 14), 2)
            for hx in range(0, ANCHO_VENTANA, 60):
                pygame.draw.circle(pantalla, (25, 30, 35), (hx + 30, y_origen_feed - 7), 3)

    if not panel_mantenimiento_abierto and progreso_monitor <= 0.8:
        dibujar_panel_llamada()
        dibujar_tutorial()

    if oxigeno < 45.0 and not juego_terminado and not en_apagon:
        overlay_asfixia = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        factor_peligro = (45.0 - oxigeno) / 45.0
        grosor_tunel = int(180 * factor_peligro)
        alpha_tunel = min(240, int(120 + 130 * factor_peligro))

        pygame.draw.rect(overlay_asfixia, (0, 0, 0, alpha_tunel), (0, 0, ANCHO_VENTANA, ALTO_VENTANA), grosor_tunel)
        pygame.draw.circle(overlay_asfixia, (0, 0, 0, 0), (ANCHO_VENTANA // 2, ALTO_VENTANA // 2), max(120, int(420 * (1.0 - factor_peligro))))

        if error_ventilacion and int(tiempo_juego() * 3) % 2 == 0:
            overlay_asfixia.fill((70, 0, 0, 50), special_flags=pygame.BLEND_RGBA_ADD)

        pantalla.blit(overlay_asfixia, (0, 0))

    if not mirando_techo and not panel_mantenimiento_abierto and not en_apagon:
        color_tab = (40, 160, 220) if monitor_abierto else (60, 70, 80)
        pygame.draw.rect(pantalla, color_tab, rect_toggle_camara, border_radius=6)
        txt_tab = fuente_pequeña.render(TK("[{monitor} / CLIC] MONITOR CCTV"), True, (255, 255, 255))
        pantalla.blit(txt_tab, (ANCHO_VENTANA//2 - 105, ALTO_VENTANA - 35))

    if not en_apagon:
        txt_hora = fuente_grande.render(f"{hora} AM", True, (255, 255, 255))
        if es_infinito():
            txt_tag_noche = fuente_pequeña.render(T("MODO INFINITO") + f"  //  {infinito_horas} H", True, (240, 170, 80))
            pantalla.blit(txt_tag_noche, (ANCHO_VENTANA - 20 - txt_tag_noche.get_width(), 60))
        else:
            txt_tag_noche = fuente_pequeña.render(f"NOCHE {noche_actual}", True, (180, 190, 200))
            pantalla.blit(txt_tag_noche, (ANCHO_VENTANA - 130, 60))
        pantalla.blit(txt_hora, (ANCHO_VENTANA - 130, 25))

        if (error_ventilacion or error_camaras or apagon_bobina_activo) and int(tiempo_juego() * 3) % 2 == 0:
            msg_hud = "[!] GENERADOR CAM_08 VACÍO" if apagon_bobina_activo else TK("[!] ERROR DE SISTEMA - PULSA [{panel}]")
            txt_err_hud = fuente_pequeña.render(msg_hud, True, (255, 60, 60))
            pantalla.blit(txt_err_hud, (ANCHO_VENTANA - 270, 95))

        if tiempo_juego() < puerta_trabada_hasta:
            txt_tr = fuente_pequeña.render("[!] LA COMPUERTA SE TRABÓ", True, (255, 120, 60))
            pantalla.blit(txt_tr, (30, ALTO_VENTANA - 122))
        color_bat = (50, 220, 50) if bateria > 30 else (220, 50, 50)
        txt_bat = fuente_media.render(f"BATERÍA: {int(bateria)}%", True, color_bat)
        pantalla.blit(txt_bat, (30, ALTO_VENTANA - 95))

        txt_uso = fuente_pequeña.render("USO:", True, (200, 200, 200))
        pantalla.blit(txt_uso, (30, ALTO_VENTANA - 70))
        for b in range(5):
            rect_b = pygame.Rect(75 + (b * 16), ALTO_VENTANA - 70, 12, 16)
            c_barra = (40, 220, 80) if barras_uso <= 2 else ((240, 210, 40) if barras_uso <= 3 else (240, 50, 50))
            pygame.draw.rect(pantalla, c_barra if b < barras_uso else (40, 45, 50), rect_b)
            pygame.draw.rect(pantalla, (20, 22, 25), rect_b, 1)

        color_ox = (80, 200, 255) if oxigeno > 40 else (255, 80, 80)
        txt_ox = fuente_media.render(f"OXÍGENO: {int(oxigeno)}%", True, color_ox)
        pantalla.blit(txt_ox, (30, ALTO_VENTANA - 42))

        col_calor = (255, 70, 70) if linterna_sobrecalentada else ((240, 190, 50) if calor_linterna > 65 else (170, 210, 230))
        estado_lin = "SOBRECALENTADA" if linterna_sobrecalentada else f"{int(calor_linterna)}%"
        txt_cal = fuente_pequeña.render(f"BULBO LINTERNA: {estado_lin}", True, col_calor)
        pantalla.blit(txt_cal, (30, ALTO_VENTANA - 20))

    if not juego_terminado and not en_jumpscare:
        dibujar_subtitulos()

    # Easter Eggs Alucinaciones VHS
    if not juego_terminado and not en_jumpscare and random.random() < 0.0008:
        overlay_aluc = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        overlay_aluc.fill((8, 4, 4))
        frases_lore = FRASES_ALUCINACION
        txt_aluc = fuente_titulo.render(random.choice(frases_lore), True, (220, 30, 30))
        overlay_aluc.blit(txt_aluc, (ANCHO_VENTANA//2 - txt_aluc.get_width()//2, ALTO_VENTANA//2 - 30))
        sp_aluc = sprite("barnaby_oficina") or sprite("silas_techo")
        if sp_aluc:
            dibujar_sprite_centrado(overlay_aluc, sp_aluc, ANCHO_VENTANA//2, ALTO_VENTANA//2, 1.3, 120)
        pantalla.blit(overlay_aluc, (0, 0))
        reproducir_sonido(sfx_glitch_8bit, 0.7, 0.7)

    # Atajos de Desarrollador F2 y F3
    if MODO_DESARROLLO and teclas[pygame.K_F2] and not juego_terminado:
        tiempo_inicio = tiempo_juego() - (DURACION_HORA_SEGUNDOS * 6)
    if MODO_DESARROLLO and teclas[pygame.K_F3] and not juego_terminado:
        bateria = 100.0
        oxigeno = 100.0
        bobina_generador = 100.0

    aberracion = 1
    if error_ventilacion or error_camaras or oxigeno < 40 or en_apagon or apagon_bobina_activo:
        aberracion = 3

    aplicar_postprocesado_crt(dt, intensidad_aberracion=aberracion)
    pygame.display.flip()
