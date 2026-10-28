# -*- coding: utf-8 -*-
"""Cintas de 1982: los cuatro minijuegos de 8 bits y las pantallas de relato.

Cada minijuego se dibuja en un lienzo chico (300x175) y se agranda x4 sin suavizar,
para que se vea como un juego de 8 bits. Los mapas son texto: cada carácter es una
baldosa de 10x10 píxeles. Se pueden editar acá abajo:
    '#' pared   '.' piso   'P' inicio   'G' objetivo   'E' prueba escondida
    '1' '2' '3' válvulas (cinta 2)   'T' turbina (cinta 3)   'K' llave y 'X' salida (cinta 4)
    'C' candado de una salida (cinta 0, la secreta)

Uso desde el juego:
    mj = crear_minijuego(numero, contexto)
    cada cuadro: mj.actualizar(dt, eventos, teclas); mj.dibujar(pantalla)
    al terminar: mj.terminado == True, mj.prueba == True si encontró la prueba
"""
import math
import random
import pygame

from historia import CINTAS

W, H = 300, 175          # Resolución interna
ESCALA = 4               # 300x175 -> 1200x700
T = 10                   # Tamaño de baldosa
OY = 25                  # Los mapas empiezan debajo de la franja de textos de arriba
VEL_JUGADOR = 58.0


# -------------------------------------------------------------
# Utilidades
# -------------------------------------------------------------
def leer_mapa(lineas):
    muros, puntos = [], {}
    for fila, linea in enumerate(lineas):
        assert len(linea) == 30, f"La fila {fila} del mapa mide {len(linea)} (deben ser 30)"
        for col, c in enumerate(linea):
            if c == "#":
                muros.append(pygame.Rect(col * T, OY + fila * T, T, T))
            elif c != ".":
                puntos.setdefault(c, []).append((col, fila))
    return muros, puntos


def centro_baldosa(col, fila):
    return col * T + T // 2, OY + fila * T + T // 2


class MaquinaDeEscribir:
    """Texto que aparece letra por letra."""
    def __init__(self, lineas, velocidad=55.0):
        self.lineas = list(lineas)
        self.total = sum(len(l) for l in self.lineas)
        self.mostrados = 0.0
        self.velocidad = velocidad

    @property
    def completa(self):
        return self.mostrados >= self.total

    def completar(self):
        self.mostrados = self.total

    def actualizar(self, dt):
        self.mostrados = min(self.total, self.mostrados + self.velocidad * dt)

    def lineas_visibles(self):
        quedan = int(self.mostrados)
        salida = []
        for l in self.lineas:
            salida.append(l[:max(0, quedan)])
            quedan -= len(l)
        return salida


def _pulsado(eventos):
    for e in eventos:
        if e.type == pygame.KEYDOWN and e.key not in (pygame.K_F1, pygame.K_F11, pygame.K_ESCAPE):
            return True
        if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
            return True
    return False


def _escape(eventos):
    return any(e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE for e in eventos)


def _centrado(pantalla, fuente, texto, y, color):
    s = fuente.render(texto, True, color)
    pantalla.blit(s, (pantalla.get_width() // 2 - s.get_width() // 2, y))


# -------------------------------------------------------------
# Pantalla de relato (introducción del juego, finales...)
# -------------------------------------------------------------
class Relato:
    """Pantalla negra con título y texto a máquina. Termina al apretar una tecla."""
    def __init__(self, ctx, titulo, lineas, color_titulo=(90, 220, 140), fondo=None):
        self.ctx = ctx
        self.fondo = fondo          # Imagen más ancha que la pantalla: se recorre de lado a lado
        self.titulo = titulo
        self.color_titulo = color_titulo
        self.maquina = MaquinaDeEscribir(lineas, velocidad=48.0)
        self.terminado = False
        self.t = 0.0

    def actualizar(self, dt, eventos, teclas=None):
        self.t += dt
        self.maquina.actualizar(dt)
        if _pulsado(eventos) or _escape(eventos):
            if self.maquina.completa or _escape(eventos):
                self.terminado = True
            else:
                self.maquina.completar()

    def dibujar(self, pantalla):
        f = self.ctx["fuentes"]
        pantalla.fill((5, 6, 7))
        if self.fondo:
            sobrante = max(0, self.fondo.get_width() - pantalla.get_width())
            fase = (math.sin(self.t * 0.12 - math.pi / 2) + 1) / 2      # Va y vuelve despacio
            pantalla.blit(self.fondo, (-int(sobrante * fase), 0))
            # Franja oscura detrás del texto
            capa = pygame.Surface((960, 380), pygame.SRCALPHA)
            capa.fill((0, 0, 0, 120))
            pantalla.blit(capa, (pantalla.get_width() // 2 - 480, 120))
        _centrado(pantalla, f["pequeña"], self.titulo, 70, self.color_titulo)
        y = 140
        for linea in self.maquina.lineas_visibles():
            s = f["media"].render(linea, True, (220, 225, 220))
            pantalla.blit(s, (pantalla.get_width() // 2 - 430, y))
            y += 34
        if self.maquina.completa and int(self.t * 2) % 2 == 0:
            _centrado(pantalla, f["cam"], "[CUALQUIER TECLA] CONTINUAR", 650, (150, 160, 160))


# -------------------------------------------------------------
# Personajes en pixel art
# -------------------------------------------------------------
SPRITE_OPERARIO = [
    "..hhhh..",
    ".hhhhhh.",
    "..ssss..",
    "..sese..",
    "..ssss..",
    ".bbbbbb.",
    "sbbbbbbs",
    ".bbbbbb.",
]
PIERNAS = [[".ll..ll.", ".ll..ll."], ["..llll..", "..l..l.."]]

OPERARIOS = {
    0: {"h": (70, 62, 55), "s": (215, 175, 140), "e": (20, 20, 20), "b": (75, 78, 90), "l": (30, 30, 36)},       # Varela (traje)
    1: {"h": (230, 200, 40), "s": (232, 182, 140), "e": (20, 20, 20), "b": (50, 90, 170), "l": (40, 40, 60)},    # Walter
    2: {"h": (125, 125, 135), "s": (125, 125, 135), "e": (30, 200, 230), "b": (220, 120, 40), "l": (70, 45, 30)},  # Marta (máscara)
    3: {"h": (190, 50, 50), "s": (210, 160, 120), "e": (20, 20, 20), "b": (60, 140, 80), "l": (30, 60, 40)},      # Tomás
    4: {"h": (120, 80, 40), "s": (190, 140, 100), "e": (20, 20, 20), "b": (180, 40, 40), "l": (40, 40, 50)},      # Rubén
}


def dibujar_operario(sup, x, y, colores, paso):
    filas = SPRITE_OPERARIO + PIERNAS[paso % 2]
    for fy, fila in enumerate(filas):
        for fx, c in enumerate(fila):
            if c != ".":
                sup.set_at((int(x) + fx - 1, int(y) + fy - 2), colores[c])


# -------------------------------------------------------------
# Base de las cintas
# -------------------------------------------------------------
class Cinta:
    numero = 0
    MAPA = []

    def __init__(self, ctx):
        self.ctx = ctx
        self.datos = CINTAS[self.numero]
        self.colores = OPERARIOS[self.numero]
        self.lienzo = pygame.Surface((W, H))
        self.fase = "intro"
        self.maquina = MaquinaDeEscribir(self.datos["intro"])
        self.terminado = False
        self.prueba = False
        self.salteado = False
        self.t = 0.0
        self.intentos = 0
        self.flash = 0.0
        self.color_flash = (255, 40, 40)
        self.mensaje, self.t_mensaje = "", 0.0
        self.paso, self.dist_paso = 0, 0.0
        self.muros, self.puntos = leer_mapa(self.MAPA)
        self.inicio = centro_baldosa(*self.puntos["P"][0])
        self.px, self.py = self.inicio
        e = self.puntos.get("E", [None])[0]
        self.rect_prueba = pygame.Rect(e[0] * T + 2, OY + e[1] * T + 2, 6, 6) if e else None
        self.preparar()

    # --- Para redefinir en cada cinta ---
    def preparar(self): pass
    def actualizar_nivel(self, dt): pass
    def dibujar_nivel(self, l): pass
    def dibujar_hud_extra(self, pantalla): pass

    # --- Comunes ---
    def sonar(self, clave, vol=0.8):
        self.ctx["sonar"](clave, vol)

    def avisar(self, texto, segundos=2.2):
        self.mensaje, self.t_mensaje = texto, segundos

    def rect_jugador(self, x=None, y=None):
        x = self.px if x is None else x
        y = self.py if y is None else y
        return pygame.Rect(int(x) - 3, int(y) - 3, 6, 7)

    def mover(self, dx, dy):
        """Mueve con colisión contra las paredes (eje por eje)."""
        if dx:
            nx = self.px + dx
            if self.rect_jugador(nx, self.py).collidelist(self.muros) == -1:
                self.px = nx
        if dy:
            ny = self.py + dy
            if self.rect_jugador(self.px, ny).collidelist(self.muros) == -1:
                self.py = ny

    def volver_al_inicio(self):
        self.px, self.py = self.inicio

    def fallar(self, texto):
        self.intentos += 1
        self.flash, self.color_flash = 0.45, (255, 40, 40)
        self.sonar("glitch")
        self.avisar(texto)
        self.volver_al_inicio()

    def ganar(self):
        self.fase = "outro"
        lineas = list(self.datos["outro"]) + [""]
        if self.prueba:
            lineas += ["PRUEBA ENCONTRADA: " + self.datos["prueba"], self.datos["prueba_detalle"]]
        else:
            lineas += ["PRUEBA NO ENCONTRADA.", "Puedes repetir esta cinta desde ARCHIVO 1982 en el menú."]
        self.maquina = MaquinaDeEscribir(lineas)
        self.sonar("ok")

    def actualizar(self, dt, eventos, teclas):
        self.t += dt
        if self.fase in ("intro", "outro"):
            self.maquina.actualizar(dt)
            if self.fase == "intro" and _escape(eventos):
                self.salteado, self.terminado = True, True
            elif _pulsado(eventos):
                if not self.maquina.completa:
                    self.maquina.completar()
                elif self.fase == "intro":
                    self.fase = "juego"
                else:
                    self.terminado = True
            return

        if _escape(eventos):
            self.salteado, self.terminado = True, True
            return
        self.flash = max(0.0, self.flash - dt)
        self.t_mensaje = max(0.0, self.t_mensaje - dt)

        dx = (teclas[pygame.K_RIGHT] or teclas[pygame.K_d]) - (teclas[pygame.K_LEFT] or teclas[pygame.K_a])
        dy = (teclas[pygame.K_DOWN] or teclas[pygame.K_s]) - (teclas[pygame.K_UP] or teclas[pygame.K_w])
        if dx and dy:
            dx, dy = dx * 0.7071, dy * 0.7071
        if dx or dy:
            self.mover(dx * VEL_JUGADOR * dt, dy * VEL_JUGADOR * dt)
            self.dist_paso += VEL_JUGADOR * dt
            if self.dist_paso > 7:
                self.dist_paso = 0.0
                self.paso += 1
                self.sonar("paso", 0.35)

        if self.rect_prueba and not self.prueba and self.rect_jugador().colliderect(self.rect_prueba):
            self.prueba = True
            self.flash, self.color_flash = 0.3, (255, 230, 120)
            self.sonar("prueba")
            self.avisar("¡PRUEBA ENCONTRADA! " + self.datos["prueba"], 3.0)

        self.actualizar_nivel(dt)

    # --- Dibujo ---
    def dibujar_muros(self, l, color, borde):
        for m in self.muros:
            l.fill(color, m)
            l.fill(borde, (m.x, m.y, m.w, 1))

    def dibujar_prueba(self, l):
        if self.rect_prueba and not self.prueba:
            r = self.rect_prueba
            l.fill((235, 230, 205), r)
            l.fill((150, 140, 120), (r.x + 1, r.y + 2, 4, 1))
            if int(self.t * 4) % 2 == 0:
                l.set_at((r.right, r.y - 1), (255, 255, 200))
                l.set_at((r.x - 1, r.bottom), (255, 240, 150))

    def dibujar(self, pantalla):
        f = self.ctx["fuentes"]
        if self.fase in ("intro", "outro"):
            pantalla.fill((5, 6, 7))
            _centrado(pantalla, f["pequeña"], self.datos["titulo"], 60, (90, 220, 140))
            _centrado(pantalla, f["grande"], self.datos["personaje"], 95, (240, 240, 235))
            y = 190
            for i, linea in enumerate(self.maquina.lineas_visibles()):
                color = (220, 225, 220)
                if linea.startswith("PRUEBA ENCONTRADA"):
                    color = (255, 210, 90)
                elif linea.startswith("PRUEBA NO"):
                    color = (150, 150, 150)
                _centrado(pantalla, f["media"], linea, y, color)
                y += 36
            if self.fase == "intro" and self.maquina.completa:
                _centrado(pantalla, f["pequeña"], "OBJETIVO: " + self.datos["objetivo"], y + 20, (240, 210, 80))
                _centrado(pantalla, f["cam"], "MOVERTE: FLECHAS / WASD    //    ESC: SALTAR LA CINTA (SIN PRUEBA)", y + 52, (130, 150, 140))
            if self.maquina.completa and int(self.t * 2) % 2 == 0:
                _centrado(pantalla, f["cam"], "[CUALQUIER TECLA] CONTINUAR", 650, (150, 160, 160))
            return

        l = self.lienzo
        l.fill((0, 0, 0))
        self.dibujar_nivel(l)
        dibujar_operario(l, self.px - 3, self.py - 3, self.colores, self.paso)
        self.dibujar_luz(l)
        pygame.transform.scale(l, (W * ESCALA, H * ESCALA), pantalla)

        if self.flash > 0:
            capa = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
            capa.fill((*self.color_flash, int(160 * self.flash / 0.45)))
            pantalla.blit(capa, (0, 0))

        # Franja de arriba
        pantalla.fill((6, 6, 8), (0, 0, pantalla.get_width(), OY * ESCALA - 4))
        pantalla.blit(f["8bit"].render(self.datos["titulo"] + "  //  " + self.datos["personaje"], True, (90, 220, 140)), (20, 12))
        pantalla.blit(f["pequeña"].render("OBJETIVO: " + self.datos["objetivo"], True, (240, 210, 80)), (20, 38))
        prueba_txt = "PRUEBA: ENCONTRADA" if self.prueba else "PRUEBA: ???"
        s = f["8bit"].render(prueba_txt, True, (255, 210, 90) if self.prueba else (110, 110, 110))
        pantalla.blit(s, (pantalla.get_width() - s.get_width() - 20, 12))
        s = f["8bit"].render(f"INTENTOS: {self.intentos}   //   ESC: SALTAR", True, (120, 130, 130))
        pantalla.blit(s, (pantalla.get_width() - s.get_width() - 20, 38))
        if not self.prueba and self.t < 12:
            pantalla.blit(f["8bit"].render(self.datos["pista"], True, (150, 150, 160)), (20, 66))
        self.dibujar_hud_extra(pantalla)
        if self.t_mensaje > 0:
            s = f["media"].render(self.mensaje, True, (255, 255, 255))
            fondo = pygame.Rect(0, 0, s.get_width() + 30, s.get_height() + 16)
            fondo.center = (pantalla.get_width() // 2, pantalla.get_height() - 50)
            pantalla.fill((10, 10, 12), fondo)
            pygame.draw.rect(pantalla, (200, 60, 60), fondo, 2)
            pantalla.blit(s, (fondo.x + 15, fondo.y + 8))

    def dibujar_luz(self, l):
        pass


# -------------------------------------------------------------
# CINTA 1: Walter cruza las cintas transportadoras (estilo Frogger)
# -------------------------------------------------------------
class CintaWalter(Cinta):
    numero = 1
    MAPA = [
        "##############################",
        "#............................#",
        "#.............G..............#",
        "#............................#",
        "#............................#",
        "#............................#",
        "#E...........................#",
        "#............................#",
        "#............................#",
        "#............................#",
        "#............................#",
        "#............................#",
        "#............................#",
        "#.............P..............#",
        "##############################",
    ]
    # (fila, dirección, velocidad px/s, cantidad de cajas)
    CARRILES = [(4, 1, 24, 3), (6, -1, 33, 3), (8, 1, 40, 4), (10, -1, 30, 3), (11, 1, 52, 2)]

    def preparar(self):
        self.rect_meta = pygame.Rect(self.puntos["G"][0][0] * T, OY + self.puntos["G"][0][1] * T, T, T)
        self.cajas = []
        for fila, direc, vel, n in self.CARRILES:
            hueco = 280 / n
            for i in range(n):
                ancho = random.choice([12, 16, 20])
                x = 10 + i * hueco + random.uniform(0, hueco - ancho - 8)
                self.cajas.append({"fila": fila, "dir": direc, "vel": vel, "x": x, "w": ancho})

    def carril_de(self, y):
        for fila, direc, vel, _ in self.CARRILES:
            if OY + fila * T <= y < OY + (fila + 1) * T:
                return direc, vel
        return None

    def actualizar_nivel(self, dt):
        for c in self.cajas:
            c["x"] += c["dir"] * c["vel"] * dt
            if c["dir"] > 0 and c["x"] > 290:
                c["x"] = 10 - c["w"]
            elif c["dir"] < 0 and c["x"] + c["w"] < 10:
                c["x"] = 290
        carril = self.carril_de(self.py)
        if carril:
            self.mover(carril[0] * carril[1] * dt, 0)   # La cinta te arrastra
        rj = self.rect_jugador()
        for c in self.cajas:
            if rj.colliderect(pygame.Rect(int(c["x"]), OY + c["fila"] * T + 1, c["w"], T - 2)):
                self.fallar("¡TE GOLPEÓ UNA CAJA!")
                return
        if rj.colliderect(self.rect_meta):
            self.ganar()

    def dibujar_nivel(self, l):
        l.fill((34, 30, 34), (0, OY, W, 150))
        for x in range(10, 290, 20):
            for y in range(OY + 10, OY + 140, 20):
                l.fill((38, 34, 38), (x, y, 10, 10))
        for fila, direc, vel, _ in self.CARRILES:
            y = OY + fila * T
            l.fill((22, 22, 26), (10, y, 280, T))
            desfase = int(self.t * vel * direc) % 8
            for x in range(10 + desfase - 8, 290, 8):
                if 10 <= x < 290:
                    l.fill((48, 48, 54), (x, y + 1, 2, T - 2))
            l.fill((90, 80, 30), (10, y, 280, 1))
            l.fill((90, 80, 30), (10, y + T - 1, 280, 1))
        # Oficina del fondo con la grabadora
        l.fill((45, 38, 30), (10, OY + 10, 280, 20))
        m = self.rect_meta
        l.fill((60, 60, 70), m.inflate(4, 2))
        l.fill((30, 30, 34), (m.x + 1, m.y + 2, 8, 5))
        if int(self.t * 3) % 2 == 0:
            l.set_at((m.x + 8, m.y + 1), (255, 60, 60))   # Luz de REC
        for c in self.cajas:
            r = pygame.Rect(int(c["x"]), OY + c["fila"] * T + 1, c["w"], T - 2)
            l.fill((130, 90, 45), r)
            pygame.draw.rect(l, (80, 50, 25), r, 1)
            pygame.draw.line(l, (80, 50, 25), r.topleft, r.bottomright)
        self.dibujar_muros(l, (60, 56, 62), (95, 90, 100))
        self.dibujar_prueba(l)


# -------------------------------------------------------------
# CINTA 2: Marta cierra las válvulas antes de que explote la caldera
# -------------------------------------------------------------
class CintaMarta(Cinta):
    numero = 2
    MAPA = [
        "##############################",
        "#............................#",
        "#.....1...............3......#",
        "#..........######............#",
        "#..........######............#",
        "#..........######............#",
        "#............................#",
        "#..............2.............#",
        "#....####............####....#",
        "#....####............####....#",
        "#............................#",
        "#............................#",
        "#E...........................#",
        "#.............P..............#",
        "##############################",
    ]
    # Chorros de vapor: (col, fila, largo, horizontal, desfase)
    CHORROS = [(9, 1, 7, False, 0.0), (20, 1, 7, False, 1.1), (1, 11, 8, True, 0.6), (15, 9, 3, False, 1.7)]
    CICLO, ACTIVO = 2.4, 1.0
    SUBIDA_PRESION = 2.4

    def preparar(self):
        self.valvulas = {}
        for n in "123":
            c, f = self.puntos[n][0]
            self.valvulas[int(n)] = pygame.Rect(c * T + 1, OY + f * T + 1, 8, 8)
        self.reiniciar_caldera()

    def reiniciar_caldera(self):
        self.cerradas = 0
        self.presion = 0.0
        self.volver_al_inicio()

    def chorro_estado(self, desfase):
        fase = (self.t + desfase) % self.CICLO
        if fase < self.ACTIVO:
            return "activo"
        if fase > self.CICLO - 0.35:
            return "aviso"
        return "apagado"

    def rect_chorro(self, col, fila, largo, horiz):
        if horiz:
            return pygame.Rect(col * T, OY + fila * T + 2, largo * T, T - 4)
        return pygame.Rect(col * T + 2, OY + fila * T, T - 4, largo * T)

    def actualizar_nivel(self, dt):
        self.presion += self.SUBIDA_PRESION * dt
        if self.presion >= 100:
            self.intentos += 1
            self.flash, self.color_flash = 0.45, (255, 255, 255)
            self.sonar("explosion")
            self.avisar("¡LA CALDERA EXPLOTÓ! INTENTA DE NUEVO")
            self.reiniciar_caldera()
            return
        rj = self.rect_jugador()
        for col, fila, largo, horiz, desf in self.CHORROS:
            if self.chorro_estado(desf) == "activo" and rj.colliderect(self.rect_chorro(col, fila, largo, horiz)):
                self.presion = min(99.0, self.presion + 8)
                self.fallar("¡VAPOR! LA PRESIÓN SUBE")
                return
        for n, r in self.valvulas.items():
            if n > self.cerradas and rj.colliderect(r):
                if n == self.cerradas + 1:
                    self.cerradas += 1
                    self.sonar("ok")
                    self.avisar(f"VÁLVULA {n} CERRADA")
                    if self.cerradas == 3:
                        self.ganar()
                elif self.t_mensaje <= 0:
                    self.presion = min(99.0, self.presion + 5)
                    self.sonar("error")
                    self.avisar(f"PRIMERO LA VÁLVULA {self.cerradas + 1}")

    def dibujar_nivel(self, l):
        l.fill((38, 22, 18), (0, OY, W, 150))
        for x in range(0, W, 10):
            l.fill((44, 26, 20), (x, OY, 1, 150))
        # Hornos de fondo con brillo
        brillo = 120 + int(40 * math.sin(self.t * 6))
        for c, f in [(12, 3), (5, 8), (22, 8)]:
            l.fill((brillo, 50, 20), (c * T + 3, OY + f * T + 3, 14, 4))
        self.dibujar_muros(l, (70, 40, 32), (110, 70, 50))
        for col, fila, largo, horiz, desf in self.CHORROS:
            estado = self.chorro_estado(desf)
            r = self.rect_chorro(col, fila, largo, horiz)
            boquilla = (r.x, r.y, 3, r.h) if horiz else (r.x, r.y, r.w, 3)
            l.fill((100, 100, 110), boquilla)
            if estado == "activo":
                for _ in range(40):
                    px = random.randint(r.left, r.right - 1)
                    py = random.randint(r.top, r.bottom - 1)
                    g = random.randint(190, 250)
                    l.set_at((px, py), (g, g, g))
            elif estado == "aviso":
                for _ in range(6):
                    l.set_at((random.randint(r.left, r.right - 1), random.randint(r.top, r.bottom - 1)), (140, 140, 140))
        for n, r in self.valvulas.items():
            cerrada = n <= self.cerradas
            color = (60, 200, 90) if cerrada else (210, 50, 40)
            pygame.draw.circle(l, color, r.center, 4)
            pygame.draw.circle(l, (30, 30, 30), r.center, 1)
            ang = 0 if cerrada else self.t * 3
            for k in range(2):
                a = ang + k * math.pi / 2
                l.set_at((int(r.centerx + 3 * math.cos(a)), int(r.centery + 3 * math.sin(a))), (240, 240, 240))
        # Escritorio de la prueba
        if self.rect_prueba:
            l.fill((90, 60, 35), self.rect_prueba.inflate(6, 2).move(0, 2))
        self.dibujar_prueba(l)

    def dibujar_hud_extra(self, pantalla):
        f = self.ctx["fuentes"]
        x, y, ancho = 760, 64, 260
        etiqueta = f["8bit"].render("PRESIÓN CALDERA 3", True, (230, 200, 190))
        pantalla.blit(etiqueta, (x - etiqueta.get_width() - 12, y + 2))
        pygame.draw.rect(pantalla, (25, 20, 20), (x, y, ancho, 18))
        color = (60, 200, 90) if self.presion < 50 else ((240, 190, 40) if self.presion < 80 else (240, 50, 40))
        pygame.draw.rect(pantalla, color, (x, y, int(ancho * self.presion / 100), 18))
        pygame.draw.rect(pantalla, (160, 150, 150), (x, y, ancho, 18), 1)
        for n in (1, 2, 3):
            cerrada = n <= self.cerradas
            s = f["8bit"].render(f"V{n}", True, (90, 230, 120) if cerrada else (230, 90, 80))
            pantalla.blit(s, (x + ancho + 14 + (n - 1) * 34, y + 2))
        # Números de las válvulas sobre el mapa
        for n, r in self.valvulas.items():
            s = f["8bit"].render(str(n), True, (255, 255, 255))
            pantalla.blit(s, (r.centerx * ESCALA - s.get_width() // 2, (r.top - 7) * ESCALA))


# -------------------------------------------------------------
# CINTA 3: Tomás en los ductos a oscuras
# -------------------------------------------------------------
class CintaTomas(Cinta):
    numero = 3
    MAPA = [
        "##############################",
        "#P.....#.........#......#....#",
        "#.####.#.#######.#.####.#.##.#",
        "#.#....#.#.....#...#..#...#..#",
        "#.#.####.#.###.#####.#.####.##",
        "#.#......#.#E#.......#......T#",
        "#.######.#.#.#########.#######",
        "#......#...#.........#.......#",
        "######.#####.#######.#######.#",
        "#....#.......#.....#.......#.#",
        "#.##.#########.###.#######.#.#",
        "#.#..........#.#.........#...#",
        "#.#.########.#.#.#######.###.#",
        "#...#..........#.......#.....#",
        "##############################",
    ]
    RADIO_LUZ = 34

    def preparar(self):
        c, f = self.puntos["T"][0]
        self.rect_meta = pygame.Rect(c * T, OY + f * T, T, T)
        # Ventiladores sobre el camino a la turbina (se calculan solos aunque cambies el mapa)
        camino = self.camino_bfs(self.puntos["P"][0], self.puntos["T"][0])
        self.ventiladores = []
        for i, k in enumerate((0.22, 0.45, 0.68, 0.86)):
            col, fila = camino[int(len(camino) * k)]
            self.ventiladores.append({"rect": pygame.Rect(col * T, OY + fila * T, T, T), "desfase": i * 0.8})
        # Máscara de luz (círculo con borde suave)
        r = self.RADIO_LUZ
        self.luz = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        for y in range(r * 2):
            for x in range(r * 2):
                d = math.hypot(x - r, y - r) / r
                self.luz.set_at((x, y), (0, 0, 0, int(250 * min(1.0, d ** 1.6))))
        self.oscuridad = pygame.Surface((W, H), pygame.SRCALPHA)

    def camino_bfs(self, a, b):
        libres = {(c, f) for f, linea in enumerate(self.MAPA) for c, ch in enumerate(linea) if ch != "#"}
        prev, cola = {a: None}, [a]
        while cola:
            actual = cola.pop(0)
            if actual == b:
                break
            for dc, df in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                v = (actual[0] + dc, actual[1] + df)
                if v in libres and v not in prev:
                    prev[v] = actual
                    cola.append(v)
        camino, n = [], b
        while n is not None:
            camino.append(n)
            n = prev.get(n)
        return camino[::-1]

    def ventilador_activo(self, v):
        return (self.t + v["desfase"]) % 2.6 < 1.3

    def actualizar_nivel(self, dt):
        rj = self.rect_jugador()
        for v in self.ventiladores:
            if self.ventilador_activo(v) and rj.colliderect(v["rect"].inflate(-2, -2)):
                self.fallar("¡EL VENTILADOR TE ARRASTRÓ!")
                return
        if rj.colliderect(self.rect_meta):
            self.ganar()

    def dibujar_nivel(self, l):
        l.fill((26, 28, 30), (0, OY, W, 150))
        for x in range(0, W, 5):
            l.fill((30, 32, 34), (x, OY, 1, 150))
        self.dibujar_muros(l, (70, 74, 80), (110, 116, 122))
        for v in self.ventiladores:
            r = v["rect"]
            activo = self.ventilador_activo(v)
            pygame.draw.circle(l, (50, 55, 60), r.center, 4)
            ang = self.t * 18 if activo else 0.3
            for k in range(3):
                a = ang + k * 2.094
                pygame.draw.line(l, (200, 210, 220) if activo else (110, 115, 120), r.center,
                                 (r.centerx + 4 * math.cos(a), r.centery + 4 * math.sin(a)))
        self.dibujar_prueba(l)

    def dibujar_luz(self, l):
        o = self.oscuridad
        o.fill((0, 0, 0, 250))
        parpadeo = random.randint(-1, 1) if random.random() < 0.2 else 0
        o.blit(self.luz, (int(self.px) - self.RADIO_LUZ + parpadeo, int(self.py) - self.RADIO_LUZ), special_flags=pygame.BLEND_RGBA_MIN)
        l.blit(o, (0, 0))
        # La turbina siempre brilla (es la guía) y los ventiladores encendidos zumban en rojo
        m = self.rect_meta
        brillo = 150 + int(80 * math.sin(self.t * 4))
        l.fill((40, 90, brillo), m.inflate(-2, -2))
        l.fill((200, 240, 255), (m.centerx - 1, m.centery - 1, 2, 2))
        for v in self.ventiladores:
            if self.ventilador_activo(v):
                l.set_at(v["rect"].center, (255, 60, 60))
        l.fill((0, 0, 0), (0, 0, W, OY))


# -------------------------------------------------------------
# CINTA 4: Rubén roba la llave maestra sin que lo vean
# -------------------------------------------------------------
class CintaRuben(Cinta):
    numero = 4
    MAPA = [
        "##############################",
        "#............#...............#",
        "#..##..##....#..##..##..##...#",
        "#..##..##....#..##..##..##...#",
        "#..##..##...................K#",
        "#..##..##....#..##..##..##...#",
        "#............#..##..##..##...#",
        "#######..#####...............#",
        "#............#####..######...#",
        "#..##..##....................#",
        "#..##..##..........##..##..E.#",
        "#..##..##....#.....##..##....#",
        "#............#...............#",
        "#XP..........#...............#",
        "##############################",
    ]
    # Recorrido del guardia (baldosas)
    RONDA = [(11, 12), (11, 9), (17, 9), (27, 9), (27, 4), (15, 4), (15, 1), (15, 4), (15, 7), (21, 7), (19, 7), (19, 9), (11, 9)]
    VEL_GUARDIA = 30.0
    LARGO_VISION, ANGULO_VISION = 52.0, math.radians(30)

    def preparar(self):
        c, f = self.puntos["K"][0]
        self.rect_llave = pygame.Rect(c * T + 2, OY + f * T + 3, 6, 4)
        c, f = self.puntos["X"][0]
        self.rect_salida = pygame.Rect(c * T, OY + f * T, T, T)
        self.muros_salida = self.rect_salida
        self.muros.append(self.muros_salida)    # La salida es una pared hasta tener la llave
        self.tiene_llave = False
        self.ronda = [centro_baldosa(c, f) for c, f in self.RONDA]
        self.gx, self.gy = self.ronda[0]
        self.objetivo = 1
        self.dir_guardia = 0.0

    def volver_al_inicio(self):
        super().volver_al_inicio()
        if getattr(self, "tiene_llave", False):
            self.tiene_llave = False
            self.avisar("¡TE VIERON! LA LLAVE VOLVIÓ A SU LUGAR")

    def ve_al_jugador(self):
        dx, dy = self.px - self.gx, self.py - self.gy
        dist = math.hypot(dx, dy)
        if dist > self.LARGO_VISION or dist < 1:
            return dist < 6
        dif = (math.atan2(dy, dx) - self.dir_guardia + math.pi) % (2 * math.pi) - math.pi
        if abs(dif) > self.ANGULO_VISION:
            return False
        pasos = int(dist / 3)
        for i in range(1, pasos):
            x = self.gx + dx * i / pasos
            y = self.gy + dy * i / pasos
            if any(m.collidepoint(x, y) for m in self.muros):
                return False
        return True

    def actualizar_nivel(self, dt):
        tx, ty = self.ronda[self.objetivo]
        dx, dy = tx - self.gx, ty - self.gy
        dist = math.hypot(dx, dy)
        paso = self.VEL_GUARDIA * dt
        if dist <= paso:
            self.gx, self.gy = tx, ty
            self.objetivo = (self.objetivo + 1) % len(self.ronda)
        else:
            self.gx += dx / dist * paso
            self.gy += dy / dist * paso
            objetivo_dir = math.atan2(dy, dx)
            dif = (objetivo_dir - self.dir_guardia + math.pi) % (2 * math.pi) - math.pi
            self.dir_guardia += max(-6 * dt, min(6 * dt, dif))

        if self.ve_al_jugador():
            self.fallar("¡TE VIERON!")
            return
        rj = self.rect_jugador()
        if not self.tiene_llave and rj.colliderect(self.rect_llave):
            self.tiene_llave = True
            self.sonar("ok")
            self.avisar("TIENES LA LLAVE. ¡VUELVE A LA SALIDA!")
        if self.tiene_llave and rj.inflate(10, 10).colliderect(self.rect_salida):
            self.ganar()

    def dibujar_nivel(self, l):
        l.fill((30, 28, 26), (0, OY, W, 150))
        for y in range(OY, OY + 150, 10):
            l.fill((34, 32, 30), (0, y, W, 1))
        for m in self.muros:
            if m is self.muros_salida:
                continue
            l.fill((60, 50, 40), m)
            l.fill((85, 72, 58), (m.x, m.y + 3, m.w, 1))
            l.fill((85, 72, 58), (m.x, m.y + 7, m.w, 1))
        # Salida
        s = self.rect_salida
        l.fill((90, 60, 30), s)
        l.fill((60, 200, 90) if self.tiene_llave else (200, 50, 40), (s.right - 3, s.centery, 2, 2))
        # Llave
        if not self.tiene_llave:
            k = self.rect_llave
            l.fill((240, 210, 50), k)
            l.fill((30, 28, 26), (k.x + 1, k.y + 1, 2, 2))
            if int(self.t * 3) % 2 == 0:
                l.set_at((k.right, k.y - 1), (255, 255, 200))
        # Cajón entreabierto con la prueba
        if self.rect_prueba:
            l.fill((70, 70, 78), self.rect_prueba.inflate(4, 4))
        self.dibujar_prueba(l)
        # Cono de visión del guardia
        cono = pygame.Surface((W, H), pygame.SRCALPHA)
        a1, a2 = self.dir_guardia - self.ANGULO_VISION, self.dir_guardia + self.ANGULO_VISION
        puntos = [(self.gx, self.gy)]
        for k in range(9):
            a = a1 + (a2 - a1) * k / 8
            puntos.append((self.gx + self.LARGO_VISION * math.cos(a), self.gy + self.LARGO_VISION * math.sin(a)))
        pygame.draw.polygon(cono, (255, 240, 150, 55), puntos)
        l.blit(cono, (0, 0))
        # Guardia (una sombra alta con linterna)
        gx, gy = int(self.gx), int(self.gy)
        l.fill((8, 8, 10), (gx - 3, gy - 6, 7, 11))
        l.set_at((gx - 1, gy - 4), (230, 230, 255))
        l.set_at((gx + 1, gy - 4), (230, 230, 255))
        l.set_at((gx + int(4 * math.cos(self.dir_guardia)), gy + int(4 * math.sin(self.dir_guardia))), (255, 250, 200))

    def dibujar_hud_extra(self, pantalla):
        f = self.ctx["fuentes"]
        txt = "LLAVE MAESTRA: EN TU PODER" if self.tiene_llave else "LLAVE MAESTRA: NO"
        pantalla.blit(f["8bit"].render(txt, True, (240, 210, 60) if self.tiene_llave else (160, 160, 160)), (700, 66))


# -------------------------------------------------------------
# CINTA 0 (secreta): Varela cambia los candados de las salidas
# -------------------------------------------------------------
class Vigilante:
    """Alguien que recorre una ronda con linterna y ve en un cono."""
    def __init__(self, ronda, velocidad, largo=48.0, angulo=math.radians(28)):
        self.ronda = [centro_baldosa(c, f) for c, f in ronda]
        self.x, self.y = self.ronda[0]
        self.objetivo = 1
        self.dir = 0.0
        self.velocidad = velocidad
        self.largo, self.angulo = largo, angulo
        self.paso, self.dist = 0, 0.0

    def actualizar(self, dt):
        tx, ty = self.ronda[self.objetivo]
        dx, dy = tx - self.x, ty - self.y
        dist = math.hypot(dx, dy)
        paso = self.velocidad * dt
        if dist <= paso:
            self.x, self.y = tx, ty
            self.objetivo = (self.objetivo + 1) % len(self.ronda)
        else:
            self.x += dx / dist * paso
            self.y += dy / dist * paso
            dif = (math.atan2(dy, dx) - self.dir + math.pi) % (2 * math.pi) - math.pi
            self.dir += max(-6 * dt, min(6 * dt, dif))
            self.dist += paso
            if self.dist > 7:
                self.dist, self.paso = 0.0, self.paso + 1

    def ve(self, px, py, muros):
        dx, dy = px - self.x, py - self.y
        dist = math.hypot(dx, dy)
        if dist > self.largo or dist < 1:
            return dist < 6
        dif = (math.atan2(dy, dx) - self.dir + math.pi) % (2 * math.pi) - math.pi
        if abs(dif) > self.angulo:
            return False
        pasos = int(dist / 3)
        for i in range(1, pasos):
            if any(m.collidepoint(self.x + dx * i / pasos, self.y + dy * i / pasos) for m in muros):
                return False
        return True

    def dibujar_cono(self, cono):
        a1, a2 = self.dir - self.angulo, self.dir + self.angulo
        puntos = [(self.x, self.y)]
        for k in range(9):
            a = a1 + (a2 - a1) * k / 8
            puntos.append((self.x + self.largo * math.cos(a), self.y + self.largo * math.sin(a)))
        pygame.draw.polygon(cono, (255, 240, 150, 50), puntos)


COLORES_TURNO_NOCHE = {"h": (40, 40, 40), "s": (200, 150, 110), "e": (20, 20, 20), "b": (150, 110, 50), "l": (50, 45, 40)}


class CintaVarela(Cinta):
    numero = 0
    MAPA = [
        "#############C################",
        "#.....#......................#",
        "#.G...#..##..##..##..##..##..#",
        "#..P..#..##..##..##..##..##..#",
        "#.....#......................#",
        "###.###..####..........####..#",
        "#............................C",
        "#..##..##...##########...##..#",
        "C..##..##...#.......E#...##..#",
        "#...........#........#.......#",
        "#..##..##...####..####...##..#",
        "#..##..##................##..#",
        "#............................#",
        "#............................#",
        "##################C###########",
    ]
    RONDAS = [
        ([(7, 4), (27, 4), (27, 12), (23, 12), (23, 6), (7, 6)], 24.0),
        ([(1, 12), (11, 12), (11, 9), (1, 9)], 20.0),
        ([(13, 9), (19, 9), (16, 9), (16, 13), (28, 13), (16, 13), (16, 9)], 22.0),
    ]
    SEGUNDOS_CANDADO = 1.6

    def preparar(self):
        self.candados = []
        for c, f in self.puntos["C"]:
            rect = pygame.Rect(c * T, OY + f * T, T, T)
            self.muros.append(rect)                   # La puerta es una pared
            self.candados.append({"rect": rect, "hecho": False, "progreso": 0.0})
        c, f = self.puntos["G"][0]
        self.rect_oficina = pygame.Rect(c * T - 4, OY + f * T - 4, T + 8, T + 8)
        self.vigilantes = [Vigilante(ronda, vel) for ronda, vel in self.RONDAS]

    def hechos(self):
        return sum(1 for k in self.candados if k["hecho"])

    def volver_al_inicio(self):
        super().volver_al_inicio()
        for k in getattr(self, "candados", []):
            k["progreso"] = 0.0

    def actualizar_nivel(self, dt):
        for v in self.vigilantes:
            v.actualizar(dt)
            if v.ve(self.px, self.py, self.muros):
                self.fallar("¡TE VIERON! NADIE PUEDE SABERLO")
                return
        rj = self.rect_jugador()
        for k in self.candados:
            if k["hecho"]:
                continue
            if rj.inflate(8, 8).colliderect(k["rect"]):
                antes = int(k["progreso"] * 4)
                k["progreso"] += dt
                if int(k["progreso"] * 4) != antes:
                    self.sonar("paso", 0.5)      # Clic de la llave
                if k["progreso"] >= self.SEGUNDOS_CANDADO:
                    k["hecho"] = True
                    self.sonar("ok")
                    if self.hechos() == len(self.candados):
                        self.avisar("LISTO. VUELVE A TU OFICINA", 3.0)
                    else:
                        self.avisar(f"CANDADO CAMBIADO ({self.hechos()}/{len(self.candados)})")
            else:
                k["progreso"] = max(0.0, k["progreso"] - dt * 2)
        if self.hechos() == len(self.candados) and rj.colliderect(self.rect_oficina):
            self.ganar()

    def dibujar_nivel(self, l):
        l.fill((22, 22, 26), (0, OY, W, 150))
        for y in range(OY, OY + 150, 10):
            l.fill((26, 26, 30), (0, y, W, 1))
        candados = [k["rect"] for k in self.candados]
        for m in self.muros:
            if m in candados:
                continue
            l.fill((52, 50, 58), m)
            l.fill((70, 68, 78), (m.x, m.y, m.w, 1))
        # Oficina de Varela: alfombra y escritorio
        o = self.rect_oficina
        l.fill((60, 25, 25), (T, OY + T, 5 * T, 4 * T))
        l.fill((90, 60, 35), (o.x + 2, o.y + 3, o.w - 4, 6))
        # Puertas con candado
        for k in self.candados:
            r = k["rect"]
            l.fill((110, 30, 30) if not k["hecho"] else (70, 70, 80), r)
            l.fill((200, 200, 210) if k["hecho"] else (200, 170, 60), (r.centerx - 2, r.centery - 2, 4, 4))
            if not k["hecho"] and int(self.t * 3) % 2 == 0:
                l.set_at((r.centerx, r.y + 1), (255, 240, 160))
            if 0 < k["progreso"] and not k["hecho"]:
                ancho = int(12 * k["progreso"] / self.SEGUNDOS_CANDADO)
                bx = min(max(r.centerx - 6, 1), W - 14)
                by = min(max(r.y - 5, OY + 1), OY + 145)
                l.fill((20, 20, 20), (bx - 1, by - 1, 14, 3))
                l.fill((240, 210, 60), (bx, by, ancho, 1))
        if self.rect_prueba:
            l.fill((60, 58, 66), self.rect_prueba.inflate(4, 4))
        self.dibujar_prueba(l)
        cono = pygame.Surface((W, H), pygame.SRCALPHA)
        for v in self.vigilantes:
            v.dibujar_cono(cono)
        l.blit(cono, (0, 0))
        for v in self.vigilantes:
            dibujar_operario(l, v.x - 3, v.y - 3, COLORES_TURNO_NOCHE, v.paso)
            l.set_at((int(v.x + 4 * math.cos(v.dir)), int(v.y + 4 * math.sin(v.dir))), (255, 250, 200))
        if self.hechos() == len(self.candados) and int(self.t * 2) % 2 == 0:
            pygame.draw.rect(l, (240, 210, 60), self.rect_oficina, 1)

    def dibujar_hud_extra(self, pantalla):
        f = self.ctx["fuentes"]
        n = self.hechos()
        completo = n == len(self.candados)
        texto = f"CANDADOS: {n}/{len(self.candados)}"
        pantalla.blit(f["8bit"].render(texto, True, (240, 210, 60) if completo else (200, 120, 110)), (760, 66))


MINIJUEGOS = {0: CintaVarela, 1: CintaWalter, 2: CintaMarta, 3: CintaTomas, 4: CintaRuben}


def crear_minijuego(numero, ctx):
    return MINIJUEGOS[numero](ctx)
