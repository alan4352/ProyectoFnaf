# -*- coding: utf-8 -*-
"""Estadísticas de la partida y logros.

Las estadísticas se acumulan en save_data.json y se muestran en el resumen final
(después del último final) y en EXTRAS > ESTADÍSTICAS.
"""

ESTADISTICAS_POR_DEFECTO = {
    "noches_superadas": 0,
    "muertes": 0,
    "muertes_por": {},            # {"Barnaby": 3, "Asfixia": 1, ...}
    "muertes_partida": 0,         # Muertes desde el último NUEVO JUEGO (para el logro "Intocable")
    "tiempo_jugado": 0.0,         # Segundos dentro de las noches
    "puertas_cerradas": 0,
    "persianas": 0,
    "linterna": 0,
    "camaras_vistas": 0,
    "senuelos": 0,
    "silas_atrapado": 0,
    "penny_bloqueada": 0,
    "bunny_rechazado": 0,
    "barnaby_cegado": 0,
    "unidad0_rechazada": 0,
    "reinicios_sistema": 0,
    "cintas_completadas": 0,
    "cintas_fallos": 0,
    "bateria_final_suma": 0.0,
    "noches_con_bateria": 0,
    "mejor_bateria": 0.0,
    "llamadas_completas": [],     # Noches cuya llamada se escuchó entera
    "desafios": [],               # Desafíos de Custom Night superados
    "records_infinito": [],       # Mejores 5 tiempos del modo infinito (segundos)
}

# (id, nombre, descripción, secreto)
LOGROS = [
    ("primer_turno", "PRIMER TURNO", "Supera la noche 1.", False),
    ("fin_contrato", "FIN DE CONTRATO", "Supera la noche 5.", False),
    ("archivista", "ARCHIVISTA", "Encuentra las 4 pruebas de las cintas.", False),
    ("fin_del_turno", "FIN DEL TURNO", "Consigue el final verdadero.", False),
    ("horas_extra", "HORAS EXTRA", "Supera la noche 6.", True),
    ("intocable", "INTOCABLE", "Supera las 5 noches sin morir ni una vez.", False),
    ("puertas_abiertas", "PUERTAS ABIERTAS", "Supera una noche (2 o más) sin cerrar la compuerta.", False),
    ("ahorro", "AHORRO DE ENERGÍA", "Termina una noche (2 o más) con más del 50% de batería.", False),
    ("una_toma", "UNA SOLA TOMA", "Termina una cinta con su prueba sin fallar ni una vez.", False),
    ("compuerta", "COMPUERTA CERRADA", "Atrapa a Silas con la compuerta de ducto 10 veces.", False),
    ("encandilado", "ENCANDILADO", "Ahuyenta a Barnaby con la linterna 15 veces.", False),
    ("ojos_abiertos", "NO LE QUITES LOS OJOS", "Rechaza a la Unidad 0 cinco veces.", True),
    ("buen_oyente", "BUEN OYENTE", "Escucha completas las llamadas de las 5 noches.", False),
    ("veinte", "20/20/20/20", "Supera la Custom Night con todos en 20.", False),
    ("turno_completo", "TURNO COMPLETO", "Supera todos los desafíos de la Custom Night.", False),
    ("fantasma", "¿VISTE ESO?", "Algo pasó frente a una cámara.", True),
    ("numero_equivocado", "NÚMERO EQUIVOCADO", "Recibe una llamada que no era para ti.", True),
    ("maraton", "MARATÓN", "Resiste 10 horas en el modo infinito.", False),
    ("cinta_cero", "0303", "Encuentra la cinta que nadie debía escuchar.", True),
]
NOMBRES_LOGROS = {l[0]: l for l in LOGROS}


class Progreso:
    def __init__(self, guardado):
        self.stats = {}
        for k, v in ESTADISTICAS_POR_DEFECTO.items():
            v = guardado.get("estadisticas", {}).get(k, v)
            self.stats[k] = dict(v) if isinstance(v, dict) else (list(v) if isinstance(v, list) else v)
        self.logros = set(guardado.get("logros", []))
        self.avisos = []              # Logros recién desbloqueados para mostrar
        self.bloqueado = False        # True en modo desarrollador: no se ganan logros
        self.sin_guardar = False      # Hay un logro nuevo que todavía no se guardó

    def sumar(self, clave, n=1):
        self.stats[clave] = self.stats.get(clave, 0) + n
        self.revisar_contadores()

    def muerte(self, causa):
        self.stats["muertes"] += 1
        self.stats["muertes_partida"] += 1
        self.stats["muertes_por"][causa] = self.stats["muertes_por"].get(causa, 0) + 1

    def agregar_a_lista(self, clave, valor):
        if valor not in self.stats[clave]:
            self.stats[clave].append(valor)

    def desbloquear(self, id_logro):
        if self.bloqueado or id_logro in self.logros or id_logro not in NOMBRES_LOGROS:
            return False
        self.logros.add(id_logro)
        self.avisos.append(id_logro)
        self.sin_guardar = True
        return True

    def revisar_contadores(self):
        if self.stats["silas_atrapado"] >= 10:
            self.desbloquear("compuerta")
        if self.stats["barnaby_cegado"] >= 15:
            self.desbloquear("encandilado")
        if self.stats["unidad0_rechazada"] >= 5:
            self.desbloquear("ojos_abiertos")
        if all(n in self.stats["llamadas_completas"] for n in (1, 2, 3, 4, 5)):
            self.desbloquear("buen_oyente")

    def a_dict(self):
        return {"estadisticas": self.stats, "logros": sorted(self.logros)}

    # --- Resumen ---
    def bateria_promedio(self):
        n = self.stats["noches_con_bateria"]
        return self.stats["bateria_final_suma"] / n if n else 0.0

    def nota(self, pruebas):
        """Calificación del guardia según muertes por noche superada."""
        if self.stats["noches_superadas"] == 0:
            return "-", "SIN TURNOS TODAVÍA"
        noches = max(1, self.stats["noches_superadas"])
        ratio = self.stats["muertes"] / noches
        if ratio <= 0.3:
            letra, titulo = "A", "GUARDIA EJEMPLAR"
        elif ratio <= 1.0:
            letra, titulo = "B", "GUARDIA CONFIABLE"
        elif ratio <= 2.5:
            letra, titulo = "C", "SOBREVIVIENTE"
        else:
            letra, titulo = "D", "CARNE DE CAÑÓN"
        if pruebas == 4 and letra != "D":
            letra += "+"
        return letra, titulo


def formato_tiempo(segundos):
    s = int(segundos)
    h, m = s // 3600, (s % 3600) // 60
    return f"{h}h {m:02d}m" if h else f"{m}m {s % 60:02d}s"
