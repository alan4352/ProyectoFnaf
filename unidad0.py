# -*- coding: utf-8 -*-
"""Unidad 0: el enemigo de la noche 6.

Regla: solo se mueve cuando NADIE LA MIRA. Recorre cuatro cámaras; mientras la estés
viendo en el monitor, no avanza. Si pasa demasiado tiempo sin que la mires, salta a la
siguiente cámara. Cuando llega al pasillo (CAM_07), hay que mirarla fijo unos segundos
para que retroceda; si se te acaba el tiempo ahí, ataca.
"""

RUTA = ["CAM_04", "CAM_06", "CAM_02", "CAM_07"]
# Dónde se dibuja en cada cámara: (x, y, escala)
POSICIONES = {"CAM_04": (300, 330, 0.55), "CAM_06": (610, 345, 0.60), "CAM_02": (250, 335, 0.62), "CAM_07": (460, 352, 0.86)}
SEGUNDOS_PARA_RECHAZAR = 3.5


class Unidad0:
    def __init__(self):
        self.reiniciar(False)

    def reiniciar(self, activa, limite=12.0):
        self.activa = activa
        self.limite = limite          # Segundos sin vigilar antes de moverse
        self.nodo = 0
        self.sin_vigilar = 0.0
        self.mirada = 0.0             # Tiempo mirándola fijo en el pasillo

    def sala(self):
        return RUTA[self.nodo]

    def en_pasillo(self):
        return self.nodo == len(RUTA) - 1

    def nervios(self):
        """0 a 1: qué tan cerca está de moverse (para las pistas de sonido)."""
        return min(1.0, self.sin_vigilar / self.limite) if self.activa else 0.0

    def actualizar(self, dt, camara_mirada):
        """camara_mirada: la cámara que se está viendo con el monitor abierto, o None.
        Devuelve None, "avanzo", "rechazada" o "ataque"."""
        if not self.activa:
            return None
        if camara_mirada == self.sala():
            self.sin_vigilar = max(0.0, self.sin_vigilar - dt * 4)
            if self.en_pasillo():
                self.mirada += dt
                if self.mirada >= SEGUNDOS_PARA_RECHAZAR:
                    self.nodo, self.mirada, self.sin_vigilar = 0, 0.0, 0.0
                    return "rechazada"
            return None
        self.mirada = 0.0
        self.sin_vigilar += dt
        if self.sin_vigilar >= self.limite:
            self.sin_vigilar = 0.0
            if self.en_pasillo():
                return "ataque"
            self.nodo += 1
            return "avanzo"
        return None
