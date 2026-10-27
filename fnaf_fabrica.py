import sys
import os
import time
import math
import random
import json
import pygame

# -------------------------------------------------------------
# 0. Configuración de Directorios y Carga Segura de Assets
# -------------------------------------------------------------
def ruta_recurso(ruta_relativa):
    """Obtiene la ruta absoluta para recursos (compatible con PyInstaller)."""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath("."), ruta_relativa)
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

ANCHO_VENTANA = 1200
ALTO_VENTANA = 700
ANCHO_OFICINA = 1800
ALTO_OFICINA = 700

pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
pygame.display.set_caption("FNAF: Industrial Sector (1982)")
reloj = pygame.time.Clock()

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
                fn = pygame.font.Font(font_match, tamaño)
                fn.set_bold(negrita)
                return fn
            except:
                pass
    return pygame.font.SysFont(None, tamaño, bold=negrita)

fuente_cam = cargar_fuente(13, True)
fuente_pequeña = cargar_fuente(15, True)
fuente_media = cargar_fuente(20, True)
fuente_grande = cargar_fuente(34, True)
fuente_titulo = cargar_fuente(46, True)
fuente_reloj_6am = cargar_fuente(72, True)
fuente_panel = cargar_fuente(18, True)
fuente_llamada = cargar_fuente(16, True)
fuente_8bit = cargar_fuente(14, True)

# -------------------------------------------------------------
# 2. Generador de Audio Procedural Sintético (WAV en memoria)
# -------------------------------------------------------------
def crear_sonido_procedural(duracion, frecuencia_base, tipo="seno", fade=True, mod=0.0):
  tasa = 44100
  n_muestras = int(tasa * duracion)
  muestras = bytearray()
 
  for i in range(n_muestras):
    t = i / tasa
    frec = frecuencia_base + (math.sin(2.0 * math.pi * mod * t) * (frecuencia_base * 0.2) if mod > 0 else 0)
   
    if tipo == "seno":
      val = math.sin(2.0 * math.pi * frec * t)
    elif tipo == "cuadrada":
      val = 1.0 if math.sin(2.0 * math.pi * frec * t) >= 0 else -1.0
    elif tipo == "ruido":
      val = random.uniform(-1.0, 1.0)
    elif tipo == "sierra":
      val = 2.0 * (t * frec - math.floor(0.5 + t * frec))
    else:
      val = 0.0

    if fade:
      factor_fade = 1.0 - (i / n_muestras)
      val *= factor_fade

    val_int = int(max(-32767, min(32767, val * 28000)))
    b = val_int.to_bytes(2, byteorder='little', signed=True)
    muestras.extend(b)
    muestras.extend(b)

  import io
  import wave
  buffer_io = io.BytesIO()
  with wave.open(buffer_io, 'wb') as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(tasa)
    wf.writeframes(muestras)
  buffer_io.seek(0)
  return pygame.mixer.Sound(buffer_io)

sfx_puerta = crear_sonido_procedural(0.35, 110, "cuadrada")
sfx_linterna = crear_sonido_procedural(0.08, 1200, "cuadrada")
sfx_persiana = crear_sonido_procedural(0.45, 95, "sierra")
sfx_monitor_movimiento = crear_sonido_procedural(0.22, 280, "seno")
sfx_estatica_cctv = crear_sonido_procedural(0.18, 0, "ruido", fade=False)
sfx_alarma_error = crear_sonido_procedural(0.4, 880, "cuadrada", mod=8.0)
sfx_reboot_click = crear_sonido_procedural(0.05, 1800, "seno")
sfx_apagon_down = crear_sonido_procedural(1.2, 160, "sierra")
sfx_jumpscare = crear_sonido_procedural(2.2, 180, "ruido", fade=False)
sfx_bobina_cuerda = crear_sonido_procedural(0.12, 600, "sierra")
sfx_lure_audio = crear_sonido_procedural(0.5, 440, "seno", mod=4.0)
sfx_ir_hum = crear_sonido_procedural(0.35, 65, "seno", fade=False)
sfx_ir_lock = crear_sonido_procedural(0.18, 1450, "cuadrada")
sfx_paso_metal = crear_sonido_procedural(0.18, 140, "cuadrada")
sfx_conducto_metal = crear_sonido_procedural(0.25, 90, "sierra")
sfx_timbre = crear_sonido_procedural(0.4, 750, "seno", mod=12.0)
sfx_campana_1 = crear_sonido_procedural(0.8, 523, "seno")
sfx_campana_2 = crear_sonido_procedural(0.8, 659, "seno")
sfx_campana_3 = crear_sonido_procedural(1.2, 784, "seno")
sfx_paso_8bit = crear_sonido_procedural(0.06, 220, "cuadrada")
sfx_glitch_8bit = crear_sonido_procedural(0.3, 0, "ruido")

NOTAS_CAJA_MUSICA = [
  crear_sonido_procedural(0.4, f, "seno") for f in [523, 587, 659, 698, 784, 880]
]

def reproducir_sonido(sfx, vol_izq=1.0, vol_der=1.0):
  canal = sfx.play()
  if canal:
    canal.set_volume(vol_izq, vol_der)

# -------------------------------------------------------------
# 3. Guardado y Carga de Progreso (save_data.json)
# -------------------------------------------------------------
def ruta_guardado():
  return ruta_recurso("save_data.json")

def guardar_partida(datos):
  try:
    with open(ruta_guardado(), "w", encoding="utf-8") as f:
      json.dump(datos, f, indent=4)
  except:
    pass

def cargar_partida():
  try:
    if os.path.exists(ruta_guardado()):
      with open(ruta_guardado(), "r", encoding="utf-8") as f:
        return json.load(f)
  except:
    pass
  return {
    "noche_desbloqueada": 1,
    "juego_completado_5_noches": False,
    "ia_custom": {"Barnaby": 10, "Silas": 10, "Penny": 10, "Rusty Bunny": 10},
    "record_20_20_20_20": False
  }

datos_guardados = cargar_partida()
noche_desbloqueada = datos_guardados.get("noche_desbloqueada", 1)
juego_completado_5_noches = datos_guardados.get("juego_completado_5_noches", False)
ia_custom = datos_guardados.get("ia_custom", {"Barnaby": 10, "Silas": 10, "Penny": 10, "Rusty Bunny": 10})
record_20_20_20_20 = datos_guardados.get("record_20_20_20_20", False)

# -------------------------------------------------------------
# 4. Carga Segura de Sprites y Texturas
# -------------------------------------------------------------
ASSETS = {}

def cargar_imagen_opcional(nombre_archivo, subcarpeta="assets"):
  p = ruta_recurso(os.path.join(subcarpeta, nombre_archivo))
  if os.path.exists(p):
    try:
      return pygame.image.load(p).convert_alpha()
    except:
      return None
  return None

ASSETS["oficina_base"] = cargar_imagen_opcional("oficina.png")
ASSETS["techo_rejilla"] = cargar_imagen_opcional("techo.png")
ASSETS["barnaby_oficina"] = cargar_imagen_opcional("barnaby_oficina.png")
ASSETS["barnaby_cam"] = cargar_imagen_opcional("barnaby_cam.png")
ASSETS["silas_techo"] = cargar_imagen_opcional("silas_techo.png")
ASSETS["silas_vent"] = cargar_imagen_opcional("silas_vent.png")
ASSETS["penny_puerta"] = cargar_imagen_opcional("penny_puerta.png")
ASSETS["penny_cam"] = cargar_imagen_opcional("penny_cam.png")
ASSETS["bunny_ventana"] = cargar_imagen_opcional("bunny_ventana.png")
ASSETS["bunny_cam"] = cargar_imagen_opcional("bunny_cam.png")
ASSETS["periodico"] = cargar_imagen_opcional("periodico.png")

for i in range(1, 9):
  ASSETS[f"cam_0{i}"] = cargar_imagen_opcional(f"cam_0{i}.png")
ASSETS["vent_tunel"] = cargar_imagen_opcional("vent_tunel.png")
ASSETS["vent_bloqueada"] = cargar_imagen_opcional("vent_bloqueada.png")

# -------------------------------------------------------------
# 5. Efectos CRT y Post-Procesado
# -------------------------------------------------------------
crt_activo = True

def aplicar_postprocesado_crt(dt, intensidad_aberracion=1):
  if not crt_activo:
    return

  ancho, alto = ANCHO_VENTANA, ALTO_VENTANA
  if intensidad_aberracion > 0:
    shift = intensidad_aberracion
    superficie_crt.blit(pantalla, (0, 0))
    capa_r = superficie_crt.copy()
    capa_b = superficie_crt.copy()
    pantalla.blit(capa_r, (shift, 0), special_flags=pygame.BLEND_RGB_ADD)
    pantalla.blit(capa_b, (-shift, 0), special_flags=pygame.BLEND_RGB_ADD)

  # Líneas de escaneo analógicas
  for y in range(0, alto, 3):
    pygame.draw.line(pantalla, (0, 0, 0, 45), (0, y), (ancho, y), 1)

  # Viñeta oscura periférica
  vignette = pygame.Surface((ancho, alto), pygame.SRCALPHA)
  pygame.draw.rect(vignette, (0, 0, 0, 70), (0, 0, ancho, alto), 35)
  pantalla.blit(vignette, (0, 0))

# -------------------------------------------------------------
# 6. Renderizado Auxiliar de Sprites
# -------------------------------------------------------------
def dibujar_sprite_centrado(superficie, img, cx, cy, escala=1.0, brillo=255):
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
  col_alerta = (200, 50, 50) if int(time.time() * 3) % 2 == 0 else (110, 25, 25)
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
  col_alerta_techo = (235, 50, 50) if int(time.time() * 4) % 2 == 0 else (90, 18, 18)
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
  col_borde = (220, 50, 50) if int(time.time() * 3) % 2 == 0 else (100, 20, 20)
  pygame.draw.rect(superforde := col_borde, caja_aviso, 2, border_radius=3)
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

tiempo_inicio_periodico = 0.0
estado_actual = ESTADO_MENU
noche_actual = 1

DIFICULTAD_NOCHES = {
  1: {"Barnaby": 3, "Silas": 2, "Penny": 1, "Rusty Bunny": 1},
  2: {"Barnaby": 6, "Silas": 5, "Penny": 3, "Rusty Bunny": 4},
  3: {"Barnaby": 9, "Silas": 8, "Penny": 6, "Rusty Bunny": 7},
  4: {"Barnaby": 12, "Silas": 11, "Penny": 9, "Rusty Bunny": 10},
  5: {"Barnaby": 15, "Silas": 14, "Penny": 13, "Rusty Bunny": 14},
}

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
trampa_ducto = "VENT_02"

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

mj_jugador_x = 120.0
mj_jugador_y = 480.0
mj_tiempo_inicio = 0.0
mj_anim_paso = 0
mj_evento_activado = False
mj_tiempo_evento = 0.0
mj_cinta_recogida = False
mj_valvulas_cerradas = 0
mj_obstaculo_x = 900.0
mj_noche_asociada = 1

DIALOGOS_NOCHES = {
  1: [
    "--- TRANSMISIÓN ENTRANTE: SUPERVISIÓN DE TURNO (NOCHE 1) ---",
    "¿Hola? ¿Me escuchas? Bien... bienvenido a la planta de ensamblaje.",
    "A tu izquierda tienes la compuerta blindada [Tecla A]. Si ves a Penny, ciérrala.",
    "A la derecha está la persiana: MANTÉN PRESIONADO EL BOTÓN contra Rusty Bunny.",
    "En el techo [W / Arriba]: sellar con [ESPACIO] te deja sin aire. Cuidado.",
    "El panel [M] reinicia turbinas y cámaras si fallan. Suerte."
  ],
  2: [
    "--- TRANSMISIÓN ENTRANTE: SUPERVISIÓN DE TURNO (NOCHE 2) ---",
    "Sigues de pie, me alegro. Los reportes de 1982 no eran fallas ordinarias.",
    "Silas solía estar en la nave de prensas, pero aprendió a meterse en los tubos.",
    "Agregamos un SEÑUELO DE AUDIO en el mapa de ventilación [CLIC EN SEÑUELO].",
    "Si Silas se acerca a la escotilla, actívalo en un ducto vecino para despistarlo.",
    "También instalamos visión nocturna IR [V / Clic Der] en cámaras para congelarlos."
  ],
  3: [
    "--- TRANSMISIÓN ENTRANTE: SUPERVISIÓN DE TURNO (NOCHE 3) ---",
    "Atención aquí: el generador auxiliar en la CAM_08 tiene fugas de voltaje.",
    "Debes mantener presionada la cuerda de la bobina en CAM_08 para que no caiga a cero.",
    "Si la bobina se descarga, las luces de la oficina fallarán y Rusty Bunny correrá.",
    "No te descuides: la linterna frontal recalienta si la dejas encendida."
  ],
  4: [
    "--- TRANSMISIÓN ENTRANTE: REGISTRO DE AUDIO ARCHIVADO (NOCHE 4) ---",
    "Grabación 1982: 'La gerencia ordenó no apagar los hornos de calderas.'",
    "Penny no debió ser ensamblada con esa matriz de aleación experimental.",
    "Los sensores analógicos detectan vibraciones dentro de las paredes.",
    "Si el nivel de oxígeno cae demasiado, sufrirás alucinaciones y sordera por hipoxia.",
    "Vigila la bobina de la CAM_08 y mantén las turbinas ventilando a toda costa."
  ],
  5: [
    "--- TRANSMISIÓN FINAL: ALERTA ROJA DE INSTALACIÓN (NOCHE 5) ---",
    "Si estás escuchando esto, los protocolos de contención se han roto por completo.",
    "Todas las unidades están en modo de sobremarcha autónoma buscando la oficina.",
    "Recarga la bobina en CAM_08 constantemente y usa el señuelo contra Silas.",
    "Si logras aguantar hasta las 6:00 AM, las puertas de la planta se sellarán solas."
  ]
}

llamada_activa = False
llamada_muteada = False
indice_dialogo = 0
tiempo_ultimo_texto = 0.0
tiempo_repique = 0.0

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

class Animatronico:
  def __init__(self, nombre, ruta, nivel_ia, tiempo_tick):
    self.nombre = nombre
    self.ruta = ruta
    self.nodo_actual = 0
    self.nivel_ia = nivel_ia
    self.tiempo_tick = tiempo_tick
    self.ultimo_tick = time.time()
    self.tiempo_en_ataque = 0.0

  def reiniciar(self, nivel_ia):
    self.nodo_actual = 0
    self.nivel_ia = nivel_ia
    self.ultimo_tick = time.time()
    self.tiempo_en_ataque = 0.0

  def actualizar(self):
    if self.nivel_ia <= 0:
      return

    sala_actual = str(self.ruta[self.nodo_actual])
    if monitor_abierto and progreso_monitor >= 0.95 and vision_nocturna_cam and not error_camaras and (camara_seleccionada in sala_actual):
      self.ultimo_tick = time.time()
      return

    ahora = time.time()
    tick_efectivo = self.tiempo_tick
    if self.nombre == "Rusty Bunny" and apagon_bobina_activo:
      tick_efectivo *= 0.5

    if ahora - self.ultimo_tick >= tick_efectivo:
      self.ultimo_tick = ahora
      if random.randint(1, 20) <= self.nivel_ia:
        self.avanzar()

  def avanzar(self):
    global glitch_cam_timer
    if self.nodo_actual < len(self.ruta) - 1:
      nodo_anterior = self.ruta[self.nodo_actual]
      self.nodo_actual += 1
      nodo_nuevo = self.ruta[self.nodo_actual]

      if monitor_abierto and (camara_seleccionada in str(nodo_anterior) or camara_seleccionada in str(nodo_nuevo)):
        glitch_cam_timer = 0.45
        reproducir_sonido(sfx_estatica_cctv, 0.9, 0.9)

      if self.nombre == "Penny":
        reproducir_sonido(sfx_paso_metal, 0.9, 0.1)
      elif self.nombre == "Rusty Bunny":
        reproducir_sonido(sfx_paso_metal, 0.1, 0.9)
      elif self.nombre == "Silas":
        reproducir_sonido(sfx_conducto_metal, 0.6, 0.6)
      elif self.nombre == "Barnaby":
        reproducir_sonido(sfx_paso_metal, 0.5, 0.5)

barnaby = Animatronico("Barnaby", ["CAM_01", "CAM_02", "CAM_07_LEJOS", "CAM_07_CERCA", "OFICINA"], 10, 7.5)
silas = Animatronico("Silas", ["CAM_02_MESAS", "VENT_01", "VENT_02", "VENT_04", "REJILLA_OFICINA", "OFICINA"], 9, 8.0)
penny = Animatronico("Penny", ["CAM_01", "CAM_03", "CAM_06", "PUERTA_IZQ", "OFICINA"], 8, 8.5)
bunny = Animatronico("Rusty Bunny", ["CAM_01", "CAM_04", "CAM_05", "CAM_08", "VENTANA_DER", "OFICINA"], 9, 7.8)

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

  noche_actual = noche
  cam_x = 300
  mirando_techo = False
  monitor_abierto = False
  progreso_monitor = 0.0
  progreso_persiana = 0.0
  modo_ventilacion = False
  panel_mantenimiento_abierto = False
  camara_seleccionada = "CAM_01"
  trampa_ducto = "VENT_02"
  bateria = 100.0
  oxigeno = 100.0
  hora = 12
  tiempo_inicio = time.time()
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
  tiempo_siguiente_fallo = time.time() + random.uniform(22.0, 40.0)

  if noche == "CUSTOM":
    difs = ia_custom
  else:
    difs = DIFICULTAD_NOCHES.get(noche, DIFICULTAD_NOCHES[1])

  barnaby.reiniciar(difs["Barnaby"])
  silas.reiniciar(difs["Silas"])
  penny.reiniciar(difs["Penny"])
  bunny.reiniciar(difs["Rusty Bunny"])

  if isinstance(noche, int) and noche in DIALOGOS_NOCHES:
    llamada_activa = True
    llamada_muteada = False
    indice_dialogo = 0
    tiempo_ultimo_texto = time.time()
    tiempo_repique = time.time()
  else:
    llamada_activa = False

  estado_actual = ESTADO_JUEGO

def iniciar_jumpscare(nombre, causa):
  global en_jumpscare, animatronico_atacante, tiempo_inicio_jumpscare
  global mensaje_muerte, monitor_abierto, mirando_techo, panel_mantenimiento_abierto, intensidad_shake
  global progreso_monitor
  en_jumpscare = True
  animatronico_atacante = nombre
  tiempo_inicio_jumpscare = time.time()
  mensaje_muerte = causa
  monitor_abierto = False
  progreso_monitor = 0.0
  mirando_techo = False
  panel_mantenimiento_abierto = False
  intensidad_shake = 30.0
  reproducir_sonido(sfx_jumpscare)

def iniciar_minijuego(noche):
  global estado_actual, mj_jugador_x, mj_jugador_y, mj_tiempo_inicio
  global mj_evento_activado, mj_tiempo_evento, mj_cinta_recogida, mj_valvulas_cerradas, mj_obstaculo_x, mj_noche_asociada
  estado_actual = ESTADO_MINIJUEGO
  mj_noche_asociada = noche if isinstance(noche, int) else 1
  mj_jugador_x = 120.0
  mj_jugador_y = 480.0
  mj_tiempo_inicio = time.time()
  mj_evento_activado = False
  mj_tiempo_evento = 0.0
  mj_cinta_recogida = False
  mj_valvulas_cerradas = 0
  mj_obstaculo_x = 900.0

# -------------------------------------------------------------
# 10. Minijuegos 8-Bit Distintos por Noche
# -------------------------------------------------------------
def actualizar_y_dibujar_minijuego(dt):
  global mj_jugador_x, mj_jugador_y, mj_anim_paso, mj_evento_activado, mj_tiempo_evento
  global mj_cinta_recogida, mj_valvulas_cerradas, mj_obstaculo_x, estado_actual

  pantalla.fill((8, 10, 12))
  pygame.draw.rect(pantalla, (25, 20, 24), (60, 60, ANCHO_VENTANA - 120, ALTO_VENTANA - 120))
  pygame.draw.rect(pantalla, (55, 45, 50), (60, 60, ANCHO_VENTANA - 120, ALTO_VENTANA - 120), 8)

  teclas = pygame.key.get_pressed()
  moviendose = False
  vel = 180.0 * dt

  if not mj_evento_activado:
    if teclas[pygame.K_LEFT] or teclas[pygame.K_a]:
      mj_jugador_x -= vel
      moviendose = True
    if teclas[pygame.K_RIGHT] or teclas[pygame.K_d]:
      mj_jugador_x += vel
      moviendose = True
    if teclas[pygame.K_UP] or teclas[pygame.K_w]:
      mj_jugador_y -= vel
      moviendose = True
    if teclas[pygame.K_DOWN] or teclas[pygame.K_s]:
      mj_jugador_y += vel
      moviendose = True

  mj_jugador_x = max(100, min(ANCHO_VENTANA - 150, mj_jugador_x))
  mj_jugador_y = max(300, min(ALTO_VENTANA - 150, mj_jugador_y))

  if moviendose:
    mj_anim_paso += 1
    if mj_anim_paso % 18 == 0:
      reproducir_sonido(sfx_paso_8bit)

  px = int(mj_jugador_x)
  py = int(mj_jugador_y)

  if mj_noche_asociada == 1:
    for y in range(80, 240, 25):
      for x in range(80, ANCHO_VENTANA - 100, 50):
        offset = 20 if (y // 25) % 2 == 0 else 0
        pygame.draw.rect(pantalla, (45, 30, 35), (x + offset, y, 44, 20))
    for y in range(260, ALTO_VENTANA - 80, 40):
      pygame.draw.line(pantalla, (18, 15, 18), (80, y), (ANCHO_VENTANA - 80, y), 2)

    pygame.draw.rect(pantalla, (60, 65, 75), (500, 200, 180, 160))
    pygame.draw.rect(pantalla, (90, 95, 110), (520, 220, 140, 120))

    rect_cinta = pygame.Rect(950, 460, 30, 20)
    if not mj_cinta_recogida:
      pygame.draw.rect(pantalla, (220, 180, 60), rect_cinta)
      pygame.draw.rect(pantalla, (30, 30, 30), (955, 465, 8, 8))
      pygame.draw.rect(pantalla, (30, 30, 30), (967, 465, 8, 8))

    rect_jugador = pygame.Rect(px, py - 40, 45, 90)
    if rect_jugador.colliderect(rect_cinta) and not mj_cinta_recogida:
      mj_cinta_recogida = True
      mj_evento_activado = True
      mj_tiempo_evento = time.time()
      reproducir_sonido(sfx_glitch_8bit)

    txt_l1 = fuente_8bit.render("REGISTRO 1982 // NOCHE 1: EL CASSETTE PERDIDO", True, (240, 240, 240))
    pantalla.blit(txt_l1, (90, 80))
    if not mj_cinta_recogida:
      txt_guia = fuente_8bit.render("> ENCUENTRA LA CINTA DE SEGURIDAD AL FINAL DEL SECTOR", True, (200, 200, 80))
      pantalla.blit(txt_guia, (90, 110))
    else:
      txt_lore1 = fuente_8bit.render("CINTA RECUPERADA: 'LOS SERVOS ACTIVARON SOLOS A LAS 3 AM'", True, (255, 60, 60))
      txt_lore2 = fuente_8bit.render("LA PLANTA OCULTÓ EL ACCIDENTE DE 1982.", True, (255, 200, 200))
      pantalla.blit(txt_lore1, (90, 110))
      pantalla.blit(txt_lore2, (90, 135))

  elif mj_noche_asociada == 2:
    pygame.draw.rect(pantalla, (40, 18, 12), (70, 70, ANCHO_VENTANA - 140, ALTO_VENTANA - 140))
    for x in [350, 650, 950]:
      pygame.draw.rect(pantalla, (70, 30, 20), (x - 20, 280, 40, 220))
      if int(time.time() * 4) % 2 == 0 and not mj_evento_activado:
        pygame.draw.circle(pantalla, (230, 230, 240), (x, 260), random.randint(12, 22))

    valvulas = [pygame.Rect(330, 450, 40, 40), pygame.Rect(630, 450, 40, 40), pygame.Rect(930, 450, 40, 40)]
    for i, v in enumerate(valvulas):
      c_valv = (80, 220, 80) if i < mj_valvulas_cerradas else (220, 60, 40)
      pygame.draw.rect(pantalla, c_valv, v)
      pygame.draw.circle(pantalla, (255, 255, 255), v.center, 8)

    rect_jugador = pygame.Rect(px, py - 40, 45, 90)
    for i, v in enumerate(valvulas):
      if rect_jugador.colliderect(v) and i == mj_valvulas_cerradas:
        mj_valvulas_cerradas += 1
        reproducir_sonido(sfx_reboot_click)
        if mj_valvulas_cerradas >= 3:
          mj_evento_activado = True
          mj_tiempo_evento = time.time()
          reproducir_sonido(sfx_glitch_8bit)

    txt_l1 = fuente_8bit.render("REGISTRO 1982 // NOCHE 2: FUGAS EN CALDERAS", True, (240, 240, 240))
    pantalla.blit(txt_l1, (90, 80))
    if not mj_evento_activado:
      txt_guia = fuente_8bit.render(f"> CIERRA LAS 3 VÁLVULAS DE PRESIÓN ROJAS [{mj_valvulas_cerradas}/3]", True, (240, 160, 60))
      pantalla.blit(txt_guia, (90, 110))
    else:
      txt_lore1 = fuente_8bit.render("VÁLVULAS SELLADAS // PENNY FUE VISTA DE PIE JUNTO AL FUEGO", True, (255, 60, 60))
      txt_lore2 = fuente_8bit.render("LAS LLAMAS NO CONSUMIERON SU ENDOESQUELETO.", True, (255, 200, 200))
      pantalla.blit(txt_lore1, (90, 110))
      pantalla.blit(txt_lore2, (90, 135))

  elif mj_noche_asociada == 3:
    for x in range(120, ANCHO_VENTANA - 120, 160):
      pygame.draw.rect(pantalla, (20, 35, 45), (x, 260, 110, 260))
      pygame.draw.rect(pantalla, (45, 75, 90), (x, 260, 110, 260), 4)

    rect_filtro = pygame.Rect(980, 340, 45, 45)
    pygame.draw.rect(pantalla, (60, 180, 240), rect_filtro)
    pygame.draw.line(pantalla, (255, 255, 255), (rect_filtro.left + 5, rect_filtro.centery), (rect_filtro.right - 5, rect_filtro.centery), 3)

    rect_jugador = pygame.Rect(px, py - 40, 45, 90)
    if rect_jugador.colliderect(rect_filtro) and not mj_evento_activado:
      mj_evento_activado = True
      mj_tiempo_evento = time.time()
      reproducir_sonido(sfx_glitch_8bit)

    txt_l1 = fuente_8bit.render("REGISTRO 1982 // NOCHE 3: ESCANEO DE DUCTOS", True, (240, 240, 240))
    pantalla.blit(txt_l1, (90, 80))
    if not mj_evento_activado:
      txt_guia = fuente_8bit.render("> ACTIVA LA TURBINA AZUL AL FINAL DEL DUCTO", True, (100, 220, 255))
      pantalla.blit(txt_guia, (90, 110))
    else:
      txt_lore1 = fuente_8bit.render("TURBINA FORZADA // ALGO SALIÓ ARRASTRÁNDOSE HACIA EL TECHO", True, (255, 60, 60))
      txt_lore2 = fuente_8bit.render("SILAS NUNCA VOLVIÓ A BAJAR DE LAS TUBERÍAS SUPERIORES.", True, (255, 200, 200))
      pantalla.blit(txt_lore1, (90, 110))
      pantalla.blit(txt_lore2, (90, 135))

  else:
    for x in [240, 520, 800]:
      pygame.draw.rect(pantalla, (30, 28, 35), (x, 260, 140, 220))
      pygame.draw.rect(pantalla, (60, 55, 70), (x, 260, 140, 220), 4)

    rect_llave = pygame.Rect(1020, 440, 35, 20)
    if not mj_evento_activado:
      pygame.draw.rect(pantalla, (240, 210, 50), rect_llave)
      pygame.draw.circle(pantalla, (240, 210, 50), (rect_llave.left, rect_llave.centery), 10)

    mj_obstaculo_x -= 65.0 * dt
    if mj_obstaculo_x < 180:
      mj_obstaculo_x = 980.0
    bx = int(mj_obstaculo_x)
    pygame.draw.rect(pantalla, (12, 10, 14), (bx, 310, 60, 140))
    pygame.draw.circle(pantalla, (180, 230, 255), (bx + 20, 330), 4)
    pygame.draw.circle(pantalla, (180, 230, 255), (bx + 40, 330), 4)

    rect_jugador = pygame.Rect(px, py - 40, 45, 90)
    if rect_jugador.colliderect(rect_llave) and not mj_evento_activado:
      mj_evento_activado = True
      mj_tiempo_evento = time.time()
      reproducir_sonido(sfx_glitch_8bit)

    txt_l1 = fuente_8bit.render("REGISTRO 1982 // NOCHE 4: ARCHIVO MAESTRO", True, (240, 240, 240))
    pantalla.blit(txt_l1, (90, 80))
    if not mj_evento_activado:
      txt_guia = fuente_8bit.render("> RECUPERA LA LLAVE DORADA MAESTRA EVITANDO LA SOMBRA", True, (240, 220, 80))
      pantalla.blit(txt_guia, (90, 110))
    else:
      txt_lore1 = fuente_8bit.render("LLAVE RECUPERADA // SECTOR BLOQUEADO POR PROTOCOLO", True, (255, 60, 60))
      txt_lore2 = fuente_8bit.render("MAÑANA A LAS 6 AM ESTE LUGAR QUEDARÁ CLAUSURADO.", True, (255, 200, 200))
      pantalla.blit(txt_lore1, (90, 110))
      pantalla.blit(txt_lore2, (90, 135))

  pygame.draw.rect(pantalla, (235, 185, 140), (px + 10, py - 40, 24, 24))
  pygame.draw.rect(pantalla, (40, 40, 50), (px + 6, py - 46, 32, 10))
  pygame.draw.rect(pantalla, (35, 80, 160), (px + 6, py - 16, 32, 40))
  pygame.draw.rect(pantalla, (220, 220, 100), (px + 36, py - 6, 12, 8))

  offset_pie = 6 if (mj_anim_paso // 10) % 2 == 0 else -6
  pygame.draw.rect(pantalla, (25, 45, 90), (px + 8 + offset_pie, py + 24, 12, 28))
  pygame.draw.rect(pantalla, (25, 45, 90), (px + 24 - offset_pie, py + 24, 12, 28))

  if mj_evento_activado and (time.time() - mj_tiempo_evento >= 4.5):
    estado_actual = ESTADO_MENU
  elif time.time() - mj_tiempo_inicio >= 30.0:
    estado_actual = ESTADO_MENU

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
        sp_bunny = ASSETS.get("bunny_ventana") or ASSETS.get("bunny_cam")
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
    dibujar_boton_industrial(superficie_oficina, 1720, 255, 50, 50, persiana_der_sostenida, (240, 160, 30), "PERSIANA")
    dibujar_boton_industrial(superficie_oficina, 1720, 330, 50, 50, luz_der_efectiva, (255, 240, 80), "LUZ")

    # --- 3. ELEMENTOS DE MANTENIMIENTO Y PUERTA IZQUIERDA ---
    if en_apagon:
        capa_oscura = pygame.Surface((ANCHO_OFICINA, ALTO_OFICINA), pygame.SRCALPHA)
        capa_oscura.fill((0, 0, 0, 225))
        superficie_oficina.blit(capa_oscura, (0, 0))

        t_ap = time.time() - tiempo_inicio_apagon
        if 2.5 < t_ap < 12.0:
            if random.random() < 0.75:
                sp_b = ASSETS.get("barnaby_oficina") or ASSETS.get("barnaby_cam")
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
            sp_penny = ASSETS.get("penny_puerta") or ASSETS.get("penny_cam")
            brillo_p = 255 if luz_izq_efectiva else 35
            dibujar_sprite_centrado(superficie_oficina, sp_penny, 230, 420, 1.0, brillo_p)

    dibujar_boton_industrial(superficie_oficina, 40, 470, 50, 50, puerta_izq_cerrada, (240, 40, 40), "PUERTA")
    dibujar_boton_industrial(superficie_oficina, 40, 545, 50, 50, luz_izq_efectiva, (255, 240, 80), "LUZ")

    # Pasillo Frontal y Barnaby
    if linterna_pasillo:
        if not ASSETS.get("oficina_base"):
            pygame.draw.polygon(superficie_oficina, (85, 80, 60), [(650, 180), (1150, 180), (1050, 500), (750, 500)])
            pygame.draw.rect(superficie_oficina, (38, 38, 32), (750, 240, 300, 260))
        else:
            haz = pygame.Surface((500, 400), pygame.SRCALPHA)
            pygame.draw.ellipse(haz, (255, 245, 190, 65), (30, 20, 440, 360))
            superficie_oficina.blit(haz, (650, 180))

        sp_barnaby = ASSETS.get("barnaby_oficina") or ASSETS.get("barnaby_cam")
        if barnaby.nodo_actual == 2:
            dibujar_sprite_centrado(superficie_oficina, sp_barnaby, 900, 360, 0.58, 180)
        elif barnaby.nodo_actual == 3:
            dibujar_sprite_centrado(superficie_oficina, sp_barnaby, 900, 370, 1.05, 255)

        if barnaby.nodo_actual in [2, 3]:
            ancho_b = int((progreso_cegado_barnaby / 1.4) * 140)
            pygame.draw.rect(superficie_oficina, (20, 25, 30), (830, 210, 140, 10))
            pygame.draw.rect(superficie_oficina, (255, 220, 60), (830, 210, ancho_b, 10))
            pygame.draw.rect(superficie_oficina, (200, 200, 200), (830, 210, 140, 10), 1)

    # --- 4. TROFEOS APOYADOS EN LA MESA (SUPERFICIE Y = 520, X = 740 y X = 815) ---
    y_mesa = 520

    if juego_completado_5_noches or noche_desbloqueada >= 5:
        # Sombra proyectada directamente sobre el tablero
        s_base1 = pygame.Surface((52, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(s_base1, (0, 0, 0, 190), (0, 0, 52, 14))
        superficie_oficina.blit(s_base1, (718, y_mesa - 5))

        # Base de madera oscura
        pygame.draw.rect(superficie_oficina, (28, 20, 14), (722, y_mesa - 16, 44, 16), border_radius=2)
        pygame.draw.rect(superficie_oficina, (52, 38, 28), (724, y_mesa - 14, 40, 12), border_radius=1)
        pygame.draw.rect(superficie_oficina, (190, 195, 205), (734, y_mesa - 10, 20, 6))

        # Copa de plata
        pygame.draw.rect(superficie_oficina, (120, 128, 136), (740, y_mesa - 34, 8, 20))
        pygame.draw.line(superficie_oficina, (220, 230, 240), (742, y_mesa - 34), (742, y_mesa - 15), 2)
        pygame.draw.polygon(superficie_oficina, (140, 150, 160), [(732, y_mesa - 56), (756, y_mesa - 56), (750, y_mesa - 34), (738, y_mesa - 34)])
        pygame.draw.polygon(superficie_oficina, (225, 235, 245), [(737, y_mesa - 56), (744, y_mesa - 56), (741, y_mesa - 34)])
        pygame.draw.circle(superficie_oficina, (170, 180, 192), (744, y_mesa - 58), 13)
        pygame.draw.circle(superficie_oficina, (230, 240, 250), (744, y_mesa - 58), 8)
        pygame.draw.circle(superficie_oficina, (255, 255, 255), (742, y_mesa - 60), 2)

    if record_20_20_20_20:
        # Sombra proyectada directamente sobre el tablero
        s_base2 = pygame.Surface((56, 14), pygame.SRCALPHA)
        pygame.draw.ellipse(s_base2, (0, 0, 0, 190), (0, 0, 56, 14))
        superficie_oficina.blit(s_base2, (790, y_mesa - 5))

        # Base de caoba con placa dorada
        pygame.draw.rect(superficie_oficina, (32, 16, 12), (794, y_mesa - 18, 48, 18), border_radius=2)
        pygame.draw.rect(superficie_oficina, (58, 30, 22), (796, y_mesa - 16, 44, 14), border_radius=1)
        pygame.draw.rect(superficie_oficina, (220, 180, 50), (806, y_mesa - 12, 24, 7))

        # Busto dorado de Barnaby
        cx, cy = 818, y_mesa - 44
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

    if silas.nodo_actual == 4:
      sp_silas_t = ASSETS.get("silas_techo") or ASSETS.get("silas_vent")
      dibujar_sprite_centrado(pantalla, sp_silas_t, ANCHO_VENTANA//2, ALTO_VENTANA//2 - 20, 1.0, 220)
      txt_aviso = fuente_pequeña.render("¡SILAS EN LA REJILLA DEL TECHO!", True, (255, 90, 90))
      pantalla.blit(txt_aviso, (ANCHO_VENTANA//2 - 130, ALTO_VENTANA//2 + 130))

  txt_info = fuente_media.render("[ESPACIO] Sellar Compuerta - [ABAJO / S] Bajar a la Oficina", True, (200, 200, 200))
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
    prog = min(1.0, (time.time() - reboot_tiempo_inicio) / DURACION_REBOOT)
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
def dibujar_feed_ventilacion():
  if trampa_ducto == camara_seleccionada and ASSETS.get("vent_bloqueada"):
    pantalla_camaras.blit(pygame.transform.scale(ASSETS["vent_bloqueada"], (720, 480)), (100, 80))
  elif ASSETS.get("vent_tunel"):
    pantalla_camaras.blit(pygame.transform.scale(ASSETS["vent_tunel"], (720, 480)), (100, 80))
  else:
    pygame.draw.rect(pantalla_camaras, (22, 25, 27), (100, 80, 720, 480))
    pygame.draw.rect(pantalla_camaras, (8, 10, 11), (300, 200, 320, 240))

  if trampa_ducto == camara_seleccionada and not ASSETS.get("vent_bloqueada"):
    rect_compuerta = pygame.Rect(280, 185, 360, 265)
    dibujar_compuerta_ducto_remota(pantalla_camaras, rect_compuerta)

  silas_en_cam = (
    (camara_seleccionada == "VENT_01" and silas.nodo_actual == 1) or
    (camara_seleccionada == "VENT_02" and silas.nodo_actual == 2) or
    (camara_seleccionada == "VENT_04" and silas.nodo_actual == 3)
  )

  if silas_en_cam and trampa_ducto != camara_seleccionada:
    pos_x, pos_y = 460, 335
    dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("silas_vent"), pos_x, pos_y, 0.70, 225)

def dibujar_sistema_camaras():
  pantalla_camaras.fill((8, 12, 10))

  # --- 1. RECORTE ESTRICTO DENTRO DE LA PANTALLA CCTV (720x480) ---
  rect_pantalla_cctv = pygame.Rect(100, 80, 720, 480)
  pantalla_camaras.set_clip(rect_pantalla_cctv)

  if error_camaras:
    pygame.draw.rect(pantalla_camaras, (12, 8, 8), rect_pantalla_cctv)
    txt_err_cam = fuente_grande.render("[CCTV OFFLINE - SYSTEM ERROR]", True, (240, 50, 50))
    txt_sub_err = fuente_pequeña.render("Fallo en tarjeta de video analógica. Reiniciar desde Panel [M].", True, (200, 120, 120))
    pantalla_camaras.blit(txt_err_cam, (ANCHO_VENTANA//2 - txt_err_cam.get_width()//2 - 140, 270))
    pantalla_camaras.blit(txt_sub_err, (ANCHO_VENTANA//2 - txt_sub_err.get_width()//2 - 140, 320))
  elif modo_ventilacion:
    dibujar_feed_ventilacion()
  else:
    # Fondo de la cámara escalado con precisión a 720x480
    img_id = camara_seleccionada.lower()
    if ASSETS.get(img_id):
      feed_img = pygame.transform.scale(ASSETS[img_id], (720, 480))
      pantalla_camaras.blit(feed_img, (100, 80))
    else:
      pygame.draw.rect(pantalla_camaras, (18, 22, 20), rect_pantalla_cctv)
      if camara_seleccionada == "CAM_03":
        txt_alerta = fuente_grande.render("[SEÑAL PERDIDA - FALLO EN SENSOR CCTV]", True, (160, 60, 60))
        pantalla_camaras.blit(txt_alerta, (140, 260))

    brillo_boost = 35 if vision_nocturna_cam else 0

    # Posicionamiento calibrado de animatrónicos en el feed
    if camara_seleccionada == "CAM_01":
      if barnaby.nodo_actual == 0:
        dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("barnaby_cam"), 460, 340, 0.62, min(255, 230 + brillo_boost))
      if penny.nodo_actual == 0:
        dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("penny_cam"), 280, 350, 0.55, min(255, 220 + brillo_boost))
      if bunny.nodo_actual == 0:
        dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("bunny_cam"), 640, 340, 0.58, min(255, 225 + brillo_boost))

    elif camara_seleccionada == "CAM_02":
      if barnaby.nodo_actual == 1:
        dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("barnaby_cam"), 460, 330, 0.65, min(255, 220 + brillo_boost))

    elif camara_seleccionada == "CAM_03":
      if penny.nodo_actual == 1:
        txt_audio = fuente_media.render("[AUDIO: PISADAS METÁLICAS EN CALDERA]", True, (240, 180, 80))
        pantalla_camaras.blit(txt_audio, (170, 360))

    elif camara_seleccionada == "CAM_04":
      if bunny.nodo_actual == 1:
        dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("bunny_cam"), 460, 335, 0.62, min(255, 215 + brillo_boost))

    elif camara_seleccionada == "CAM_05":
      if bunny.nodo_actual == 2:
        dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("bunny_cam"), 460, 335, 0.68, min(255, 220 + brillo_boost))

    elif camara_seleccionada == "CAM_06":
      if penny.nodo_actual == 2:
        dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("penny_cam"), 460, 335, 0.68, min(255, 220 + brillo_boost))

    elif camara_seleccionada == "CAM_07":
      if barnaby.nodo_actual in [2, 3]:
        pos_y = 310 if barnaby.nodo_actual == 2 else 345
        escala_b = 0.50 if barnaby.nodo_actual == 2 else 0.75
        brillo_b = 180 if barnaby.nodo_actual == 2 else 245
        dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("barnaby_cam"), 460, pos_y, escala_b, min(255, brillo_b + brillo_boost))

    elif camara_seleccionada == "CAM_08":
            if bunny.nodo_actual == 3:
                dibujar_sprite_centrado(pantalla_camaras, ASSETS.get("bunny_cam"), 460, 335, 0.72, min(255, 235 + brillo_boost))

            rect_bobina_box = pygame.Rect(120, 100, 240, 75)
            pygame.draw.rect(pantalla_camaras, (20, 24, 28), rect_bobina_box, border_radius=6)
            pygame.draw.rect(pantalla_camaras, (50, 70, 85), rect_bobina_box, 2)

            col_bob = (50, 220, 90) if bobina_generador > 45 else ((240, 180, 40) if bobina_generador > 20 else (240, 50, 50))
            txt_b_tag = fuente_cam.render("BOBINA GENERADOR AUXILIAR", True, (210, 225, 235))
            pantalla_camaras.blit(txt_b_tag, (130, 108))

            pygame.draw.rect(pantalla_camaras, (10, 12, 14), (130, 130, 220, 18), border_radius=3)
            pygame.draw.rect(pantalla_camaras, col_bob, (130, 130, int(220 * (bobina_generador / 100.0)), 18), border_radius=3)

            rect_btn_bobina = pygame.Rect(120, 185, 240, 34)
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
                txt_nv = fuente_cam.render("[IR LOCK // ANOMALÍA PARALIZADA]", True, (255, 75, 75))
                pygame.draw.rect(pantalla_camaras, (255, 60, 60), (310, 190, 300, 280), 2)
            else:
                anomalia_detectada_previa = False
                txt_nv = fuente_cam.render("[VISIÓN NOCTURNA IR: ACTIVA - CLIC DER / V]", True, (100, 255, 140))
            pantalla_camaras.blit(txt_nv, (115, 92))
        else:
            txt_nv = fuente_cam.render("[CLIC DER / V] VISIÓN NOCTURNA IR", True, (120, 150, 135))
            pantalla_camaras.blit(txt_nv, (115, 92))

        if glitch_cam_timer > 0:
            pantalla_camaras.fill((12, 16, 14), rect_pantalla_cctv)
            for _ in range(18):
                gy = random.randint(80, 540)
                gh = random.randint(4, 22)
                c_bar = random.choice([(200, 240, 220), (40, 180, 120), (180, 50, 50)])
                pygame.draw.rect(pantalla_camaras, c_bar, (100, gy, 720, gh))
            txt_mov = fuente_grande.render("[INTERFERENCIA DE MOVIMIENTO]", True, (255, 90, 90))
            pantalla_camaras.blit(txt_mov, (460 - txt_mov.get_width() // 2, 295))

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
    escala = 1.0 + (progreso * 1.8)
    pygame.draw.circle(pantalla, (220, 40, 40), (cx, cy), int(100 * escala))

    for _ in range(450):
        rx = random.randint(0, ANCHO_VENTANA)
        ry = random.randint(0, ALTO_VENTANA)
        pantalla.set_at((rx, ry), (220, 220, 220))

# -------------------------------------------------------------
# 16. Subtítulos, Menús y Periódico de Victoria
# -------------------------------------------------------------
def dibujar_panel_llamada():
    lista_actual = DIALOGOS_NOCHES.get(noche_actual, DIALOGOS_NOCHES[1])
    if llamada_activa and not llamada_muteada and not en_apagon and indice_dialogo < len(lista_actual):
        rect_caja = pygame.Rect(40, 20, 720, 65)
        s_caja = pygame.Surface((rect_caja.width, rect_caja.height), pygame.SRCALPHA)
        s_caja.fill((12, 16, 20, 230))
        pantalla.blit(s_caja, (rect_caja.x, rect_caja.y))
        pygame.draw.rect(pantalla, (50, 90, 80), rect_caja, 2)

        if int(time.time() * 3) % 2 == 0:
            pygame.draw.circle(pantalla, (40, 240, 120), (rect_caja.x + 20, rect_caja.y + 22), 6)
        txt_tag = fuente_cam.render(f"LÍNEA ACTIVA // SUPERVISIÓN TURNO {noche_actual}", True, (40, 240, 120))
        pantalla.blit(txt_tag, (rect_caja.x + 35, rect_caja.y + 15))

        txt_dialogo = fuente_llamada.render(lista_actual[indice_dialogo], True, (240, 245, 240))
        pantalla.blit(txt_dialogo, (rect_caja.x + 20, rect_caja.y + 36))

        rect_mute = pygame.Rect(rect_caja.right + 15, 20, 140, 65)
        pygame.draw.rect(pantalla, (120, 30, 30), rect_mute, border_radius=4)
        pygame.draw.rect(pantalla, (220, 60, 60), rect_mute, 2)
        txt_m1 = fuente_pequeña.render("[MUTE CALL]", True, (255, 255, 255))
        pantalla.blit(txt_m1, (rect_mute.x + 25, rect_mute.y + 25))

def dibujar_menu_principal():
    pantalla.fill((8, 10, 12))

    sp_menu = ASSETS.get("barnaby_oficina") or ASSETS.get("barnaby_cam")
    if sp_menu:
        twitch_x = random.randint(-14, 14) if random.random() < 0.10 else 0
        twitch_y = random.randint(-8, 8) if random.random() < 0.10 else 0
        brillo_m = random.choice([30, 45, 150, 25]) if random.random() < 0.08 else 40
        dibujar_sprite_centrado(pantalla, sp_menu, 230 + twitch_x, 380 + twitch_y, 1.35, brillo_m)
        if random.random() < 0.92:
            pygame.draw.circle(pantalla, (160, 235, 255), (212 + twitch_x, 305 + twitch_y), 5)
            pygame.draw.circle(pantalla, (160, 235, 255), (248 + twitch_x, 305 + twitch_y), 5)

    txt_t1 = fuente_titulo.render("FNAF: INDUSTRIAL SECTOR", True, (220, 230, 235))
    pantalla.blit(txt_t1, (400, 90))

    txt_crt_info = fuente_cam.render(f"[F1] POST-PROCESADO CRT: {'ACTIVO' if crt_activo else 'OFF'}", True, (100, 180, 140))
    pantalla.blit(txt_crt_info, (400, 145))

    estrellas = (1 if (noche_desbloqueada >= 5 or juego_completado_5_noches) else 0) + (1 if record_20_20_20_20 else 0)
    for i in range(estrellas):
        sx = 400 + i * 50
        sy = 175
        pygame.draw.circle(pantalla, (245, 200, 40), (sx + 15, sy + 12), 14)
        pygame.draw.circle(pantalla, (255, 240, 150), (sx + 15, sy + 12), 8)
    if record_20_20_20_20:
        txt_rec = fuente_cam.render("★ RÉCORD 20/20/20/20 COMPLETADO ★", True, (255, 215, 50))
        pantalla.blit(txt_rec, (400 + estrellas * 55, 180))

    opciones = []
    rect_nuevo = pygame.Rect(400, 220, 340, 55)
    pygame.draw.rect(pantalla, (18, 24, 28), rect_nuevo, border_radius=6)
    pygame.draw.rect(pantalla, (40, 160, 110), rect_nuevo, 2)
    txt_n = fuente_grande.render("NUEVO JUEGO", True, (255, 255, 255))
    pantalla.blit(txt_n, (rect_nuevo.x + 25, rect_nuevo.y + 12))
    opciones.append(("NUEVO", rect_nuevo, True))

    rect_cont = pygame.Rect(400, 295, 340, 55)
    desbloq_cont = (noche_desbloqueada > 1)
    pygame.draw.rect(pantalla, (18, 24, 28) if desbloq_cont else (15, 18, 20), rect_cont, border_radius=6)
    pygame.draw.rect(pantalla, (40, 160, 220) if desbloq_cont else (45, 55, 60), rect_cont, 2)
    color_cont = (255, 255, 255) if desbloq_cont else (90, 100, 105)
    txt_c = fuente_grande.render(f"CONTINUAR (N.{noche_desbloqueada})", True, color_cont)
    pantalla.blit(txt_c, (rect_cont.x + 25, rect_cont.y + 12))
    opciones.append(("CONTINUAR", rect_cont, desbloq_cont))

    rect_cust = pygame.Rect(400, 370, 340, 55)
    desbloq_cust = (noche_desbloqueada >= 5 or juego_completado_5_noches)
    pygame.draw.rect(pantalla, (25, 20, 18) if desbloq_cust else (15, 18, 20), rect_cust, border_radius=6)
    pygame.draw.rect(pantalla, (220, 100, 40) if desbloq_cust else (45, 55, 60), rect_cust, 2)
    color_cu = (255, 255, 255) if desbloq_cust else (90, 100, 105)
    txt_cu = fuente_grande.render("CUSTOM NIGHT", True, color_cu)
    pantalla.blit(txt_cu, (rect_cust.x + 25, rect_cust.y + 12))
    opciones.append(("CUSTOM", rect_cust, desbloq_cust))

    rect_salir = pygame.Rect(400, 445, 340, 50)
    pygame.draw.rect(pantalla, (20, 16, 16), rect_salir, border_radius=6)
    pygame.draw.rect(pantalla, (160, 40, 40), rect_salir, 2)
    txt_s = fuente_grande.render("SALIR", True, (240, 180, 180))
    pantalla.blit(txt_s, (rect_salir.x + 25, rect_salir.y + 10))
    opciones.append(("SALIR", rect_salir, True))

    for _ in range(400):
        rx = random.randint(0, ANCHO_VENTANA)
        ry = random.randint(0, ALTO_VENTANA)
        pantalla.set_at((rx, ry), (random.randint(25, 100), random.randint(25, 100), random.randint(25, 100)))

    return opciones

def dibujar_menu_custom():
    pantalla.fill((12, 14, 16))
    txt_t = fuente_titulo.render("CONFIGURACIÓN DE ANIMATRÓNICOS", True, (240, 140, 40))
    pantalla.blit(txt_t, (ANCHO_VENTANA//2 - txt_t.get_width()//2, 50))

    animatronicos = ["Barnaby", "Silas", "Penny", "Rusty Bunny"]
    controles = []

    for i, nombre in enumerate(animatronicos):
        x = 140 + i * 250
        y = 180
        rect_card = pygame.Rect(x, y, 200, 260)
        pygame.draw.rect(pantalla, (20, 24, 28), rect_card, border_radius=8)
        pygame.draw.rect(pantalla, (50, 70, 85), rect_card, 2)

        txt_n = fuente_pequeña.render(nombre, True, (220, 230, 240))
        pantalla.blit(txt_n, (x + 100 - txt_n.get_width()//2, y + 20))

        val = ia_custom[nombre]
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

    rect_start = pygame.Rect(ANCHO_VENTANA//2 - 140, 510, 280, 55)
    pygame.draw.rect(pantalla, (25, 120, 60), rect_start, border_radius=6)
    txt_start = fuente_grande.render("INICIAR NOCHE", True, (255, 255, 255))
    pantalla.blit(txt_start, (rect_start.x + 35, rect_start.y + 12))

    rect_volver = pygame.Rect(40, 40, 110, 35)
    pygame.draw.rect(pantalla, (40, 45, 50), rect_volver, border_radius=4)
    txt_v = fuente_pequeña.render("< VOLVER", True, (220, 220, 220))
    pantalla.blit(txt_v, (rect_volver.x + 20, rect_volver.y + 10))

    return controles, rect_start, rect_volver

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
    pantalla.fill((12, 12, 14))

    if ASSETS.get("periodico"):
        img_per = pygame.transform.scale(ASSETS["periodico"], (ANCHO_VENTANA, ALTO_VENTANA))
        pantalla.blit(img_per, (0, 0))
    else:
        # Fondo papel envejecido/sepia
        rect_hoja = pygame.Rect(180, 40, 840, 620)
        pygame.draw.rect(pantalla, (215, 205, 185), rect_hoja)
        pygame.draw.rect(pantalla, (60, 50, 40), rect_hoja, 4)

        # Encabezado del periódico
        txt_cab = fuente_grande.render("THE INDUSTRIAL CHRONICLE", True, (25, 20, 15))
        pantalla.blit(txt_cab, (rect_hoja.centerx - txt_cab.get_width() // 2, 60))

        str_fecha = "OCTUBRE 23, 1982  //  EDICIÓN EXTRAORDINARIA  //  PRECIO: $0.25"
        txt_f = fuente_cam.render(str_fecha, True, (70, 60, 50))
        pantalla.blit(txt_f, (rect_hoja.centerx - txt_f.get_width() // 2, 100))

        pygame.draw.line(pantalla, (40, 35, 30), (210, 120), (990, 120), 3)
        pygame.draw.line(pantalla, (40, 35, 30), (210, 125), (990, 125), 1)

        # Titular Principal
        txt_tit1 = fuente_grande.render("PLANTA DE ENSAMBLAJE CLAUSURADA", True, (20, 15, 10))
        txt_subt = fuente_media.render("LA GERENCIA SELLA LOS HORNOS Y DESMANTELA LAS LÍNEAS", True, (80, 30, 20))
        pantalla.blit(txt_tit1, (rect_hoja.centerx - txt_tit1.get_width() // 2, 140))
        pantalla.blit(txt_subt, (rect_hoja.centerx - txt_subt.get_width() // 2, 180))

        # Marco de Foto de Prensa
        rect_foto = pygame.Rect(230, 225, 300, 230)
        pygame.draw.rect(pantalla, (40, 38, 35), rect_foto)
        pygame.draw.rect(pantalla, (20, 18, 15), rect_foto, 3)

        sp_foto = ASSETS.get("barnaby_cam") or ASSETS.get("bunny_cam")
        if sp_foto:
            dibujar_sprite_centrado(pantalla, sp_foto, rect_foto.centerx, rect_foto.centery, 0.48, 170)
        else:
            pygame.draw.circle(pantalla, (120, 115, 105), rect_foto.center, 55)

        txt_pie = fuente_cam.render("Unidades mecánicas confinadas en el Sector B.", True, (60, 55, 50))
        pantalla.blit(txt_pie, (230, 465))

        # Columnas de Texto de Prensa
        lineas_articulo = [
            "Tras recurrentes anomalías nocturnas y severas",
            "fallas en los circuitos neumáticos de los servos,",
            "el Ministerio de Industria ordenó el cese total",
            "de las operaciones de manufactura pesada.",
            "",
            "Los registros de audio archivados de 1982",
            "fueron confiscados. La guardia nocturna queda",
            "oficialmente disuelta a partir de las 6:00 AM.",
            "",
            "'No debimos alterar las matrices de aleación',",
            "declaró un técnico bajo condición de anonimato.",
            "Las compuertas y turbinas quedarán soldadas."
        ]
        for idx, lin in enumerate(lineas_articulo):
            txt_col = fuente_pequeña.render(lin, True, (35, 30, 25))
            pantalla.blit(txt_col, (560, 230 + (idx * 19)))

        # Sello de Confidencial / Archivado
        pygame.draw.rect(pantalla, (160, 40, 40), (620, 480, 290, 50), 3)
        txt_sello = fuente_grande.render("CASO CERRADO", True, (160, 40, 40))
        pantalla.blit(txt_sello, (640, 490))

    txt_cont = fuente_cam.render("[PULSA ESPACIO O HAZ CLIC PARA CONTINUAR]", True, (180, 190, 195))
    pantalla.blit(txt_cont, (ANCHO_VENTANA // 2 - txt_cont.get_width() // 2, ALTO_VENTANA - 25))

# -------------------------------------------------------------
# 17. Bucle Principal de Juego
# -------------------------------------------------------------
while True:
    dt = reloj.tick(60) / 1000.0
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
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                for tipo, rect, habilitado in opciones_menu:
                    if rect.collidepoint(mouse_pos) and habilitado:
                        reproducir_sonido(sfx_linterna)
                        if tipo == "NUEVO":
                            comenzar_noche(1)
                        elif tipo == "CONTINUAR":
                            comenzar_noche(noche_desbloqueada)
                        elif tipo == "CUSTOM":
                            estado_actual = ESTADO_CUSTOM
                        elif tipo == "SALIR":
                            pygame.quit()
                            sys.exit()

        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_CUSTOM:
        controles_ia, btn_iniciar, btn_volver = dibujar_menu_custom()
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F1:
                crt_activo = not crt_activo
            if evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1:
                if btn_volver.collidepoint(mouse_pos):
                    estado_actual = ESTADO_MENU
                if btn_iniciar.collidepoint(mouse_pos):
                    comenzar_noche("CUSTOM")
                for nombre, r_menos, r_mas in controles_ia:
                    if r_menos.collidepoint(mouse_pos):
                        ia_custom[nombre] = max(0, ia_custom[nombre] - 1)
                        guardar_partida({
                            "noche_desbloqueada": noche_desbloqueada,
                            "juego_completado_5_noches": juego_completado_5_noches,
                            "ia_custom": ia_custom,
                            "record_20_20_20_20": record_20_20_20_20
                        })
                        reproducir_sonido(sfx_linterna)
                    elif r_mas.collidepoint(mouse_pos):
                        ia_custom[nombre] = min(20, ia_custom[nombre] + 1)
                        guardar_partida({
                            "noche_desbloqueada": noche_desbloqueada,
                            "juego_completado_5_noches": juego_completado_5_noches,
                            "ia_custom": ia_custom,
                            "record_20_20_20_20": record_20_20_20_20
                        })
                        reproducir_sonido(sfx_linterna)

        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_VICTORIA:
        t_transcurrido = time.time() - tiempo_inicio_6am
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
                    if noche_actual == 5:
                        estado_actual = ESTADO_PERIODICO
                        tiempo_inicio_periodico = time.time()
                    elif isinstance(noche_actual, int) and noche_actual < 5:
                        iniciar_minijuego(noche_actual)
                    else:
                        estado_actual = ESTADO_MENU

        if t_transcurrido >= 3.6:
            if noche_actual == 5:
                estado_actual = ESTADO_PERIODICO
                tiempo_inicio_periodico = time.time()
            elif isinstance(noche_actual, int) and noche_actual < 5:
                iniciar_minijuego(noche_actual)
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
            if (evento.type == pygame.MOUSEBUTTONDOWN and evento.button == 1) or (evento.type == pygame.KEYDOWN and evento.key in [pygame.K_SPACE, pygame.K_RETURN]):
                if time.time() - tiempo_inicio_periodico >= 1.5:
                    estado_actual = ESTADO_MENU

        aplicar_postprocesado_crt(dt, intensidad_aberracion=1)
        pygame.display.flip()
        continue

    elif estado_actual == ESTADO_MINIJUEGO:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F1:
                crt_activo = not crt_activo

        actualizar_y_dibujar_minijuego(dt)
        aberracion_mj = 4 if mj_evento_activado else 1
        aplicar_postprocesado_crt(dt, intensidad_aberracion=aberracion_mj)
        pygame.display.flip()
        continue

    # JUGANDO (Turno Activo)
    rect_toggle_camara = pygame.Rect(ANCHO_VENTANA//2 - 200, ALTO_VENTANA - 45, 400, 35)
    btn_modo_rect = pygame.Rect(840, 345, 330, 36)
    btn_lure_rect = pygame.Rect(840, 305, 330, 32)
    rect_btn_bobina = pygame.Rect(120, 185, 240, 34)

    if lure_cooldown > 0:
        lure_cooldown = max(0.0, lure_cooldown - dt)

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
            drenaje_bobina = 2.2 if noche_actual in [1, 2] else (3.2 if noche_actual in [3, 4] else 4.2)
            bobina_generador = max(0.0, bobina_generador - drenaje_bobina * dt)

        if bobina_generador <= 0.0:
            if not apagon_bobina_activo:
                apagon_bobina_activo = True
                tiempo_inicio_apagon_bobina = time.time()
                reproducir_sonido(sfx_apagon_down)
        else:
            apagon_bobina_activo = False

        if time.time() >= tiempo_siguiente_fallo:
            fallo_elegido = random.choice(["VENT", "CAM"])
            if fallo_elegido == "VENT" and not error_ventilacion:
                error_ventilacion = True
                reproducir_sonido(sfx_alarma_error)
            elif fallo_elegido == "CAM" and not error_camaras:
                error_camaras = True
                reproducir_sonido(sfx_alarma_error)
            tiempo_siguiente_fallo = time.time() + random.uniform(25.0, 50.0)

    if reboot_activo and not en_apagon:
        if time.time() - reboot_tiempo_inicio >= DURACION_REBOOT:
            if reboot_activo in ["VENT", "ALL"]:
                error_ventilacion = False
            if reboot_activo in ["CAM", "ALL"]:
                error_camaras = False
            reboot_activo = None
            reproducir_sonido(sfx_reboot_click)

    lista_dialogos_actual = DIALOGOS_NOCHES.get(noche_actual, DIALOGOS_NOCHES[1])
    if llamada_activa and not llamada_muteada and not en_apagon:
        ahora = time.time()
        if indice_dialogo == 0 and ahora - tiempo_repique >= 2.2:
            reproducir_sonido(sfx_timbre)
            tiempo_repique = ahora
        if ahora - tiempo_ultimo_texto >= 5.5:
            tiempo_ultimo_texto = ahora
            indice_dialogo += 1
            if indice_dialogo >= len(lista_dialogos_actual):
                llamada_activa = False

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if evento.type == pygame.KEYDOWN and evento.key == pygame.K_F1:
            crt_activo = not crt_activo

        if not juego_terminado and not en_jumpscare and not en_apagon:
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_m and not monitor_abierto and not mirando_techo:
                    panel_mantenimiento_abierto = not panel_mantenimiento_abierto
                    reproducir_sonido(sfx_reboot_click)

                if not panel_mantenimiento_abierto:
                    if evento.key in [pygame.K_SPACE, pygame.K_c] and not mirando_techo:
                        monitor_abierto = not monitor_abierto
                        reproducir_sonido(sfx_monitor_movimiento)
                        reproducir_sonido(sfx_estatica_cctv)
                    if monitor_abierto and evento.key == pygame.K_v:
                        vision_nocturna_cam = not vision_nocturna_cam
                        reproducir_sonido(sfx_linterna)
                    if not monitor_abierto:
                        if evento.key in [pygame.K_UP, pygame.K_w]:
                            mirando_techo = True
                        elif evento.key in [pygame.K_DOWN, pygame.K_s]:
                            mirando_techo = False
                        if mirando_techo and evento.key == pygame.K_SPACE:
                            ventilacion_sellada = not ventilacion_sellada
                            reproducir_sonido(sfx_puerta)
                        if not mirando_techo and evento.key == pygame.K_a:
                            puerta_izq_cerrada = not puerta_izq_cerrada
                            reproducir_sonido(sfx_puerta, 0.9, 0.2)

            if evento.type == pygame.MOUSEBUTTONDOWN:
                if panel_mantenimiento_abierto:
                    btn_rv, btn_rc, btn_rall, btn_close = dibujar_panel_mantenimiento()
                    if btn_rv.collidepoint(mouse_pos) and not reboot_activo:
                        reboot_activo = "VENT"
                        reboot_tiempo_inicio = time.time()
                        reproducir_sonido(sfx_reboot_click)
                    elif btn_rc.collidepoint(mouse_pos) and not reboot_activo:
                        reboot_activo = "CAM"
                        reboot_tiempo_inicio = time.time()
                        reproducir_sonido(sfx_reboot_click)
                    elif btn_rall.collidepoint(mouse_pos) and not reboot_activo:
                        reboot_activo = "ALL"
                        reboot_tiempo_inicio = time.time()
                        reproducir_sonido(sfx_reboot_click)
                    elif btn_close.collidepoint(mouse_pos):
                        panel_mantenimiento_abierto = False
                        reproducir_sonido(sfx_reboot_click)
                else:
                    rect_mute_btn = pygame.Rect(775, 20, 140, 65)
                    if llamada_activa and not llamada_muteada and rect_mute_btn.collidepoint(mouse_pos):
                        llamada_muteada = True
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
                            reproducir_sonido(sfx_lure_audio, 0.7, 0.7)
                            if silas.nodo_actual in [1, 2, 3]:
                                silas.nodo_actual = max(1, silas.nodo_actual - 1)
                                reproducir_sonido(sfx_conducto_metal, 0.6, 0.6)

                        if evento.button == 3 and not modo_ventilacion and (100 <= mouse_pos[0] <= 820 and 80 <= mouse_pos[1] <= 560):
                            vision_nocturna_cam = not vision_nocturna_cam
                            reproducir_sonido(sfx_linterna)

                        dict_actual = CAMARAS_VENT if modo_ventilacion else CAMARAS_PLANTA
                        for cam_id, data in dict_actual.items():
                            if data["rect"].collidepoint(mouse_pos):
                                if evento.button == 1:
                                    camara_seleccionada = cam_id
                                    reproducir_sonido(sfx_estatica_cctv)
                                elif evento.button == 3 and modo_ventilacion:
                                    trampa_ducto = cam_id
                                    reproducir_sonido(sfx_puerta)
                    elif not mirando_techo and progreso_monitor <= 0.2:
                        x_of = mouse_pos[0] + cam_x
                        y_of = mouse_pos[1]
                        if 480 <= x_of <= 545 and 360 <= y_of <= 445:
                            panel_mantenimiento_abierto = True
                            reproducir_sonido(sfx_reboot_click)
                        if 40 <= x_of <= 90 and 470 <= y_of <= 520:
                            puerta_izq_cerrada = not puerta_izq_cerrada
                            reproducir_sonido(sfx_puerta, 0.9, 0.2)
                        if 40 <= x_of <= 90 and 545 <= y_of <= 595:
                            luz_izq = not luz_izq
                            reproducir_sonido(sfx_linterna, 0.9, 0.2)
                        if 1630 <= x_of <= 1680 and 460 <= y_of <= 510:
                            if not persiana_der_sostenida:
                                tiempo_inicio_persiana = time.time()
                                reproducir_sonido(sfx_persiana, 0.2, 0.9)
                            persiana_der_sostenida = True
                        if 1630 <= x_of <= 1680 and 535 <= y_of <= 585:
                            luz_der = not luz_der
                            reproducir_sonido(sfx_linterna, 0.2, 0.9)

        elif juego_terminado and evento.type == pygame.MOUSEBUTTONDOWN:
            estado_actual = ESTADO_MENU

    if en_jumpscare:
        tiempo_transcurrido = time.time() - tiempo_inicio_jumpscare
        progreso = min(1.0, tiempo_transcurrido / DURACION_JUMPSCARE)
        shake_x = random.randint(int(-intensidad_shake), int(intensidad_shake))
        shake_y = random.randint(int(-intensidad_shake), int(intensidad_shake))
        dibujar_jumpscare(progreso)
        pantalla.blit(pantalla.copy(), (shake_x, shake_y))
        if progreso >= 1.0:
            en_jumpscare = False
            juego_terminado = True

        aplicar_postprocesado_crt(dt, intensidad_aberracion=6)
        pygame.display.flip()
        continue

    if monitor_abierto and progreso_monitor >= 0.8 and not modo_ventilacion and camara_seleccionada == "CAM_08":
        bobina_cargando = mouse_click[0] and rect_btn_bobina.collidepoint(mouse_pos)
    else:
        bobina_cargando = False

    if not monitor_abierto and not mirando_techo and not panel_mantenimiento_abierto and not en_apagon and mouse_click[0] and progreso_monitor <= 0.2:
        x_of = mouse_pos[0] + cam_x
        y_of = mouse_pos[1]
        if 1630 <= x_of <= 1680 and 460 <= y_of <= 510:
            if not persiana_der_sostenida:
                tiempo_inicio_persiana = time.time()
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

    teclas = pygame.key.get_pressed()
    intento_linterna = not monitor_abierto and not mirando_techo and not panel_mantenimiento_abierto and not en_apagon and progreso_monitor <= 0.2 and (mouse_click[2] or teclas[pygame.K_f])

    if intento_linterna and not linterna_sobrecalentada:
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
        if time.time() - tiempo_ultimo_hum_ir >= 0.38:
            reproducir_sonido(sfx_ir_hum, 0.25, 0.25)
            tiempo_ultimo_hum_ir = time.time()

    if not juego_terminado:
        if not monitor_abierto and not mirando_techo and not persiana_der_sostenida and not panel_mantenimiento_abierto and progreso_monitor <= 0.2:
            if mouse_pos[0] < 150:
                cam_x -= 650 * dt
            elif mouse_pos[0] > ANCHO_VENTANA - 150:
                cam_x += 650 * dt
            cam_x = max(0, min(cam_x, ANCHO_OFICINA - ANCHO_VENTANA))

        if not en_apagon:
            bateria -= (barras_uso * 0.14) * dt
            if bateria <= 0:
                bateria = 0
                en_apagon = True
                tiempo_inicio_apagon = time.time()
                tiempo_ultima_nota_apagon = time.time()
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
            t_ap = time.time() - tiempo_inicio_apagon
            if 2.5 < t_ap < 12.0:
                if time.time() - tiempo_ultima_nota_apagon >= 0.75:
                    tiempo_ultima_nota_apagon = time.time()
                    nota = NOTAS_CAJA_MUSICA[indice_nota_apagon % len(NOTAS_CAJA_MUSICA)]
                    reproducir_sonido(nota, 0.5, 0.5)
                    indice_nota_apagon += 1
            elif t_ap >= 13.5:
                iniciar_jumpscare("Barnaby", "SIN ENERGÍA: BARNABY TE ATRAPÓ EN LA OSCURIDAD")

        if not en_apagon:
            if ventilacion_sellada or error_ventilacion:
                velocidad_caida_ox = 6.0 if (ventilacion_sellada and error_ventilacion) else 3.8
                oxigeno -= velocidad_caida_ox * dt
                if oxigeno <= 0:
                    oxigeno = 0
                    juego_terminado = True
                    mensaje_muerte = "FALLO EN VENTILACIÓN: ASFIXIA POR GASES INDUSTRIALES"
            else:
                oxigeno = min(100.0, oxigeno + 5.5 * dt)

            barnaby.actualizar()
            silas.actualizar()
            penny.actualizar()
            bunny.actualizar()

            if silas.nodo_actual == 2 and trampa_ducto == "VENT_02":
                silas.nodo_actual = 0
                reproducir_sonido(sfx_conducto_metal, 0.5, 0.5)

            if linterna_pasillo and barnaby.nodo_actual in [2, 3]:
                progreso_cegado_barnaby += dt
                if progreso_cegado_barnaby >= 1.4:
                    barnaby.nodo_actual = 0
                    progreso_cegado_barnaby = 0.0
                    reproducir_sonido(sfx_paso_metal, 0.5, 0.5)
            else:
                progreso_cegado_barnaby = max(0.0, progreso_cegado_barnaby - 0.8 * dt)

            if bunny.nodo_actual == 4:
                if persiana_der_sostenida and progreso_persiana >= 0.85 and (time.time() - tiempo_inicio_persiana >= 2.0):
                    bunny.nodo_actual = 0
                    bunny.tiempo_en_ataque = 0.0
                    reproducir_sonido(sfx_paso_metal, 0.1, 0.9)
                else:
                    bunny.tiempo_en_ataque += dt
                    if bunny.tiempo_en_ataque >= 7.0 and (not persiana_der_sostenida or progreso_persiana < 0.85):
                        bunny.nodo_actual = 5

            if penny.nodo_actual == 3:
                if puerta_izq_cerrada:
                    penny.nodo_actual = 0
                    penny.tiempo_en_ataque = 0.0
                    reproducir_sonido(sfx_paso_metal, 0.9, 0.1)
                else:
                    penny.tiempo_en_ataque += dt
                    if penny.tiempo_en_ataque >= 6.5:
                        penny.nodo_actual = 4

            if barnaby.nodo_actual == 4:
                iniciar_jumpscare("Barnaby", "BARNABY TE ALCANZÓ EN EL ESCRITORIO")
            elif silas.nodo_actual == 5:
                if not ventilacion_sellada:
                    iniciar_jumpscare("Silas", "SILAS CAYÓ DE LA VENTILACIÓN SUPERIOR")
                else:
                    silas.nodo_actual = 0
            elif penny.nodo_actual == 4:
                iniciar_jumpscare("Penny", "PENNY ENTRÓ POR LA PUERTA IZQUIERDA")
            elif bunny.nodo_actual == 5:
                iniciar_jumpscare("Rusty Bunny", "RUSTY BUNNY DESTRUYÓ EL CRISTAL DE LA VENTANA")

        segundos_pasados = time.time() - tiempo_inicio
        hora = 12 + int(segundos_pasados // DURACION_HORA_SEGUNDOS)
        if hora > 12: hora -= 12

        if segundos_pasados >= DURACION_HORA_SEGUNDOS * 6:
            tiempo_inicio_6am = time.time()
            campanas_tocadas = [False, False, False]
            if isinstance(noche_actual, int) and noche_actual == noche_desbloqueada and noche_desbloqueada < 5:
                noche_desbloqueada += 1
            if noche_actual == 5:
                juego_completado_5_noches = True
            if noche_actual == "CUSTOM" and all(v == 20 for v in ia_custom.values()):
                record_20_20_20_20 = True
            guardar_partida({
                "noche_desbloqueada": noche_desbloqueada,
                "juego_completado_5_noches": juego_completado_5_noches,
                "ia_custom": ia_custom,
                "record_20_20_20_20": record_20_20_20_20
            })
            estado_actual = ESTADO_VICTORIA

    if panel_mantenimiento_abierto:
        dibujar_panel_mantenimiento()
    elif mirando_techo:
        dibujar_vista_techo()
    else:
        dibujar_oficina()
        pantalla.blit(superficie_oficina, (0, 0), (int(cam_x), 0, ANCHO_VENTANA, ALTO_VENTANA))

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

    if oxigeno < 45.0 and not juego_terminado and not en_apagon:
        overlay_asfixia = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        factor_peligro = (45.0 - oxigeno) / 45.0
        grosor_tunel = int(180 * factor_peligro)
        alpha_tunel = min(240, int(120 + 130 * factor_peligro))

        pygame.draw.rect(overlay_asfixia, (0, 0, 0, alpha_tunel), (0, 0, ANCHO_VENTANA, ALTO_VENTANA), grosor_tunel)
        pygame.draw.circle(overlay_asfixia, (0, 0, 0, 0), (ANCHO_VENTANA // 2, ALTO_VENTANA // 2), max(120, int(420 * (1.0 - factor_peligro))))

        if error_ventilacion and int(time.time() * 3) % 2 == 0:
            overlay_asfixia.fill((70, 0, 0, 50), special_flags=pygame.BLEND_RGBA_ADD)

        pantalla.blit(overlay_asfixia, (0, 0))

    if not mirando_techo and not panel_mantenimiento_abierto and not en_apagon:
        color_tab = (40, 160, 220) if monitor_abierto else (60, 70, 80)
        pygame.draw.rect(pantalla, color_tab, rect_toggle_camara, border_radius=6)
        txt_tab = fuente_pequeña.render("[ESPACIO / CLIC] MONITOR CCTV", True, (255, 255, 255))
        pantalla.blit(txt_tab, (ANCHO_VENTANA//2 - 105, ALTO_VENTANA - 35))

    if not en_apagon:
        txt_hora = fuente_grande.render(f"{hora} AM", True, (255, 255, 255))
        txt_tag_noche = fuente_pequeña.render(f"NOCHE {noche_actual}", True, (180, 190, 200))
        pantalla.blit(txt_hora, (ANCHO_VENTANA - 130, 25))
        pantalla.blit(txt_tag_noche, (ANCHO_VENTANA - 130, 60))

        if (error_ventilacion or error_camaras or apagon_bobina_activo) and int(time.time() * 3) % 2 == 0:
            msg_hud = "[!] GENERADOR CAM_08 VACÍO" if apagon_bobina_activo else "[!] ERROR DE SISTEMA - PULSA [M]"
            txt_err_hud = fuente_pequeña.render(msg_hud, True, (255, 60, 60))
            pantalla.blit(txt_err_hud, (ANCHO_VENTANA - 270, 95))

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

    if juego_terminado:
        overlay = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        pantalla.blit(overlay, (0, 0))
        txt_res = fuente_grande.render(mensaje_muerte, True, (255, 50, 50))
        txt_sub_go = fuente_pequeña.render("Haz clic en cualquier lugar para regresar al menú principal", True, (180, 180, 190))
        pantalla.blit(txt_res, (ANCHO_VENTANA//2 - txt_res.get_width()//2, ALTO_VENTANA//2 - 25))
        pantalla.blit(txt_sub_go, (ANCHO_VENTANA//2 - txt_sub_go.get_width()//2, ALTO_VENTANA//2 + 25))

    # Easter Eggs Alucinaciones VHS
    if not juego_terminado and not en_jumpscare and random.random() < 0.0008:
        overlay_aluc = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        overlay_aluc.fill((8, 4, 4))
        frases_lore = [
            "ELLOS NOS ENSAMBLARON",
            "INCIDENTE 1982 // ARCHIVO BORRADO",
            "NO MIRES EL CONDUCTO",
            "IT'S ME // SECTOR INDUSTRIAL"
        ]
        txt_aluc = fuente_titulo.render(random.choice(frases_lore), True, (220, 30, 30))
        overlay_aluc.blit(txt_aluc, (ANCHO_VENTANA//2 - txt_aluc.get_width()//2, ALTO_VENTANA//2 - 30))
        sp_aluc = ASSETS.get("barnaby_oficina") or ASSETS.get("silas_techo")
        if sp_aluc:
            dibujar_sprite_centrado(overlay_aluc, sp_aluc, ANCHO_VENTANA//2, ALTO_VENTANA//2, 1.3, 120)
        pantalla.blit(overlay_aluc, (0, 0))
        reproducir_sonido(sfx_glitch_8bit, 0.7, 0.7)

    # Atajos de Desarrollador F2 y F3
    if teclas[pygame.K_F2] and not juego_terminado:
        tiempo_inicio = time.time() - (DURACION_HORA_SEGUNDOS * 6)
    if teclas[pygame.K_F3] and not juego_terminado:
        bateria = 100.0
        oxigeno = 100.0
        bobina_generador = 100.0

    aberracion = 1
    if error_ventilacion or error_camaras or oxigeno < 40 or en_apagon or apagon_bobina_activo:
        aberracion = 3

    aplicar_postprocesado_crt(dt, intensidad_aberracion=aberracion)
    pygame.display.flip()