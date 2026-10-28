# -*- coding: utf-8 -*-
"""Idioma de la interfaz (español / inglés).

Todos los textos del juego pasan por las fuentes de FuenteTraducible: si el idioma es
inglés, cada texto se busca en UI_EN (texto exacto) o en PATRONES_EN (textos con números
o nombres que cambian). Si no se encuentra, se muestra tal cual.
La historia (llamadas, cintas, finales) está traducida aparte en historia_en.py.

Para agregar una traducción: sumá una línea a UI_EN con el texto en español exacto.
"""
import re
import pygame

ACTUAL = {"idioma": "es"}

UI_EN = {
    # Menús
    "NUEVO JUEGO": "NEW GAME", "CUSTOM NIGHT": "CUSTOM NIGHT", "EXTRAS": "EXTRAS", "AJUSTES": "SETTINGS",
    "SALIR": "QUIT", "NOCHE 6": "NIGHT 6", "ARCHIVO 1982": "1982 ARCHIVE", "LOGROS": "ACHIEVEMENTS",
    "ESTADÍSTICAS": "STATISTICS", "CRÉDITOS": "CREDITS", "VOLVER": "BACK", "< VOLVER": "< BACK",
    "[ESC] VOLVER": "[ESC] BACK", "[ESPACIO] CRÉDITOS": "[SPACE] CREDITS", "INICIAR NOCHE": "START NIGHT",
    "PAUSA": "PAUSE", "CONTINUAR": "CONTINUE", "REINICIAR NOCHE": "RESTART NIGHT", "MENÚ PRINCIPAL": "MAIN MENU",
    "GAME OVER": "GAME OVER", "[R] REINTENTAR NOCHE": "[R] RETRY NIGHT", "[ESC] MENÚ PRINCIPAL": "[ESC] MAIN MENU",
    "[CUALQUIER TECLA] CONTINUAR": "[ANY KEY] CONTINUE", "[PULSA ESPACIO O HAZ CLIC PARA CONTINUAR]": "[PRESS SPACE OR CLICK TO CONTINUE]",
    "★ RÉCORD 20/20/20/20 COMPLETADO ★": "★ 20/20/20/20 RECORD COMPLETE ★",
    "ENSAMBLADORA DUNMORE S.A. PRESENTA": "DUNMORE ASSEMBLY CO. PRESENTS", "INICIANDO": "STARTING",
    "CARGANDO IMÁGENES": "LOADING IMAGES",
    # Ajustes
    "[ARRIBA/ABAJO] ELEGIR   [IZQ/DER] CAMBIAR   [ESC] VOLVER   //   SE GUARDA SOLO": "[UP/DOWN] SELECT   [LEFT/RIGHT] CHANGE   [ESC] BACK   //   SAVES AUTOMATICALLY",
    "VOLUMEN GENERAL": "MASTER VOLUME", "EFECTOS DE SONIDO": "SOUND EFFECTS", "MÚSICA Y AMBIENTE": "MUSIC AND AMBIENCE",
    "VOCES DE LAS LLAMADAS": "PHONE CALL VOICES", "BRILLO": "BRIGHTNESS", "EFECTO MONITOR CRT": "CRT MONITOR EFFECT",
    "PANTALLA COMPLETA  [F11]": "FULLSCREEN  [F11]", "ESCALADO DE IMAGEN": "IMAGE SCALING",
    "VELOCIDAD DE GIRO EN LA OFICINA": "OFFICE TURN SPEED", "MOSTRAR FPS": "SHOW FPS",
    "DIFICULTAD (HISTORIA)": "DIFFICULTY (STORY)", "IDIOMA / LANGUAGE": "LANGUAGE / IDIOMA",
    "SÍ": "YES", "NO": "NO", "AJUSTAR (SIN DEFORMAR)": "FIT (NO STRETCHING)", "ESTIRAR (SIN BORDES)": "STRETCH (NO BORDERS)",
    "HISTORIA (FÁCIL)": "STORY (EASY)", "NORMAL": "NORMAL", "PESADILLA": "NIGHTMARE", "RESTABLECER": "RESET",
    "AJUSTAR mantiene la imagen sin deformar (puede dejar bordes negros). ESTIRAR llena toda la pantalla.":
        "FIT keeps the image undistorted (may leave black borders). STRETCH fills the whole screen.",
    "Si la oficina se ve muy oscura en tu monitor, subilo un poco.": "If the office looks too dark on your monitor, raise it a bit.",
    "Líneas de monitor viejo y desplazamiento de color. Apagarlo mejora el rendimiento.":
        "Old monitor scanlines and color shift. Turning it off improves performance.",
    "Qué tan rápido gira la vista al llevar el mouse a los bordes de la oficina.":
        "How fast the view turns when you move the mouse to the edges of the office.",
    "También se cambia en cualquier momento con F11.": "You can also toggle it anytime with F11.",
    "Se aplica a las noches 1 a 6 desde la próxima noche. HISTORIA: más fácil, para ver la historia.":
        "Applies to nights 1-6 starting next night. STORY: easier, to enjoy the story.",
    "Cambia el idioma de todo el juego.": "Changes the language of the whole game.",
    # Oficina y HUD
    "PUERTA": "DOOR", "LUZ": "LIGHT", "PERSIANA": "SHUTTER", "MANT.": "MAINT.", "USO:": "USAGE:",
    "SOBRECALENTADA": "OVERHEATED", "[ESPACIO / CLIC] MONITOR CCTV": "[SPACE / CLICK] CCTV MONITOR",
    "[!] ERROR DE SISTEMA - PULSA [M]": "[!] SYSTEM ERROR - PRESS [M]", "[!] GENERADOR CAM_08 VACÍO": "[!] CAM_08 GENERATOR EMPTY",
    "[!] LA COMPUERTA SE TRABÓ": "[!] THE DOOR IS JAMMED", "[MUTE CALL]": "[MUTE CALL]",
    "SECTOR 01 // COMPUERTA SELLADA": "SECTOR 01 // DOOR SEALED", "SELLADO NEUMÁTICO ACTIVO": "PNEUMATIC SEAL ACTIVE",
    "DRENAJE DE OXÍGENO EN CURSO": "OXYGEN DRAINING", "[PERSIANA CERRADA // RESISTENCIA MECÁNICA]": "[SHUTTER CLOSED // MECHANICAL RESISTANCE]",
    "¡SILAS EN LA REJILLA DEL TECHO!": "SILAS IN THE CEILING VENT!",
    "[ESPACIO] Sellar Compuerta - [ABAJO / S] Bajar a la Oficina": "[SPACE] Seal Vent - [DOWN / S] Back to Office",
    # Panel de mantenimiento
    "PANEL DE CONTROL Y MANTENIMIENTO": "CONTROL AND MAINTENANCE PANEL", "SUBSISTEMAS INDUSTRIALES // TERMINAL REBOOT": "INDUSTRIAL SUBSYSTEMS // REBOOT TERMINAL",
    "TURBINA DE VENTILACIÓN:": "VENTILATION TURBINE:", "MATRIZ DE CÁMARAS CCTV:": "CCTV CAMERA ARRAY:",
    "ERROR CRÍTICO // PRESIÓN CERO": "CRITICAL ERROR // ZERO PRESSURE", "OPERACIONAL (100%)": "OPERATIONAL (100%)",
    "SEÑAL PERDIDA // SIN VIDEO": "SIGNAL LOST // NO VIDEO", "REINICIAR VENT.": "REBOOT VENT.", "REINICIAR CCTV": "REBOOT CCTV",
    "[REINICIAR TODO]": "[REBOOT ALL]", "[M / CLIC] VOLVER A OFICINA": "[M / CLICK] BACK TO OFFICE",
    # Cámaras
    "[CCTV OFFLINE - SYSTEM ERROR]": "[CCTV OFFLINE - SYSTEM ERROR]",
    "Fallo en tarjeta de video analógica. Reiniciar desde Panel [M].": "Analog video card failure. Reboot from Panel [M].",
    "[SEÑAL PERDIDA - FALLO EN SENSOR CCTV]": "[SIGNAL LOST - CCTV SENSOR FAILURE]",
    "[AUDIO: PISADAS METÁLICAS EN CALDERA]": "[AUDIO: METALLIC FOOTSTEPS IN BOILER ROOM]",
    "BOBINA GENERADOR AUXILIAR": "BACKUP GENERATOR COIL", "[MANTENER: CARGAR BOBINA]": "[HOLD: CHARGE COIL]",
    "[CARGANDO ENERGÍA...]": "[CHARGING...]", "[INTERFERENCIA DE MOVIMIENTO]": "[MOTION INTERFERENCE]",
    "[VER DUCTOS DE AIRE]": "[VIEW AIR DUCTS]", "[VER PLANTA DE FÁBRICA]": "[VIEW FACTORY FLOOR]",
    "[EMITIR SEÑUELO DE AUDIO]": "[PLAY AUDIO LURE]", "COMPUERTA LISTA: CLIC DER EN UN DUCTO": "GATE READY: RIGHT-CLICK A DUCT",
    "PLANO SECTOR B // NIVEL 1": "SECTOR B MAP // LEVEL 1", "OFICINA [TÚ]": "OFFICE [YOU]",
    "COMPUERTA CERRADA REMOTAMENTE": "GATE CLOSED REMOTELY", "[FLUIDO BLOQUEADO]": "[FLOW BLOCKED]",
    "NO LE QUITES LOS OJOS DE ENCIMA": "DON'T TAKE YOUR EYES OFF IT", "SALIDA": "EXIT", "DESCONOCIDO": "UNKNOWN",
    "LÍNEA ENSAMBLAJE 1": "ASSEMBLY LINE 1", "NAVE DE PRENSAS": "PRESS HALL", "CALDERAS (SIN VIDEO)": "BOILERS (NO VIDEO)",
    "DEPÓSITO CHATARRA": "SCRAP STORAGE", "BAHÍA DE CARGA": "LOADING BAY", "TÚNEL TUBERÍAS O.": "W. PIPE TUNNEL",
    "CORREDOR CINTAS": "CONVEYOR CORRIDOR", "GENERADORES E.": "E. GENERATORS", "TOMA AIRE PRINCIPAL": "MAIN AIR INTAKE",
    "BIFURCACIÓN NORTE": "NORTH JUNCTION", "DUCTO EXTRACTOR E.": "E. EXHAUST DUCT", "DUCTO TECHO GUARDIA": "GUARD ROOF DUCT",
    # Muertes
    "BARNABY TE ALCANZÓ EN EL ESCRITORIO": "BARNABY REACHED YOUR DESK",
    "SILAS CAYÓ DE LA VENTILACIÓN SUPERIOR": "SILAS DROPPED FROM THE CEILING VENT",
    "PENNY ENTRÓ POR LA PUERTA IZQUIERDA": "PENNY CAME IN THROUGH THE LEFT DOOR",
    "RUSTY BUNNY DESTRUYÓ EL CRISTAL DE LA VENTANA": "RUSTY BUNNY SMASHED THE WINDOW",
    "SIN ENERGÍA: BARNABY TE ATRAPÓ EN LA OSCURIDAD": "NO POWER: BARNABY GOT YOU IN THE DARK",
    "FALLO EN VENTILACIÓN: ASFIXIA POR GASES INDUSTRIALES": "VENTILATION FAILURE: SUFFOCATED BY INDUSTRIAL FUMES",
    "LA UNIDAD 0 TE ESTABA MIRANDO": "UNIT 0 WAS WATCHING YOU",
    # Tutorial
    "[ESPACIO] O CLIC: ABRIR LAS CÁMARAS": "[SPACE] OR CLICK: OPEN CAMERAS", "[A] O CLIC: COMPUERTA": "[A] OR CLICK: DOOR",
    "MANTÉN APRETADO: PERSIANA": "HOLD DOWN: SHUTTER", "MANTÉN [F] O CLIC DERECHO: LINTERNA": "HOLD [F] OR RIGHT-CLICK: FLASHLIGHT",
    "[W]: MIRAR AL TECHO  //  [S]: VOLVER": "[W]: LOOK UP  //  [S]: BACK", "[M] O CLIC: PANEL DE MANTENIMIENTO": "[M] OR CLICK: MAINTENANCE PANEL",
    "LLEVA EL MOUSE AL BORDE  >>": "MOVE THE MOUSE TO THE EDGE  >>", "<<  LLEVA EL MOUSE AL BORDE": "<<  MOVE THE MOUSE TO THE EDGE",
    # Archivo, extras, logros, resumen
    "BLOQUEADA": "LOCKED", "[ REPRODUCIR ]": "[ PLAY ]", "PRUEBA:": "EVIDENCE:", "PRUEBA: ???": "EVIDENCE: ???",
    "TIENES TODAS LAS PRUEBAS. SOBREVIVE A LA NOCHE 5 PARA USARLAS.": "YOU HAVE ALL THE EVIDENCE. SURVIVE NIGHT 5 TO USE IT.",
    "LOGRO DESBLOQUEADO": "ACHIEVEMENT UNLOCKED", "Logro secreto.": "Secret achievement.",
    "RESUMEN DE TU TURNO": "YOUR SHIFT SUMMARY", "ENSAMBLADORA DUNMORE S.A. // REGISTRO DEL GUARDIA NOCTURNO": "DUNMORE ASSEMBLY CO. // NIGHT GUARD RECORD",
    "CALIFICACIÓN": "GRADE", "GENERAL": "GENERAL", "DEFENSAS": "DEFENSES", "MUERTES POR": "DEATHS BY",
    "Noches superadas": "Nights survived", "Tiempo de turno": "Time on shift", "Muertes": "Deaths",
    "Batería promedio a las 6 AM": "Average power at 6 AM", "Mejor batería a las 6 AM": "Best power at 6 AM",
    "Pruebas encontradas": "Evidence found", "Cintas completadas": "Tapes completed", "Intentos fallidos en cintas": "Failed tape attempts",
    "Logros": "Achievements", "Compuertas cerradas": "Doors closed", "Persianas bajadas": "Shutters lowered",
    "Veces que usaste la linterna": "Times you used the flashlight", "Cámaras revisadas": "Cameras checked",
    "Señuelos de audio": "Audio lures", "Reinicios de sistemas": "System reboots", "Penny frenada en la puerta": "Penny stopped at the door",
    "Rusty frenado en la ventana": "Rusty stopped at the window", "Barnaby encandilado": "Barnaby blinded",
    "Silas atrapado en ductos": "Silas trapped in ducts", "Unidad 0 rechazada": "Unit 0 repelled",
    "BARNABY": "BARNABY", "PENNY": "PENNY", "RUSTY BUNNY": "RUSTY BUNNY", "SILAS": "SILAS", "UNIDAD 0": "UNIT 0",
    "APAGÓN": "BLACKOUT", "ASFIXIA": "SUFFOCATION",
    "Las estadísticas se acumulan en todas tus partidas.": "Statistics add up across all your playthroughs.",
    "GUARDIA EJEMPLAR": "MODEL GUARD", "GUARDIA CONFIABLE": "RELIABLE GUARD", "SOBREVIVIENTE": "SURVIVOR",
    "CARNE DE CAÑÓN": "CANNON FODDER", "SIN TURNOS TODAVÍA": "NO SHIFTS YET",
    "(NOCHE 6 DESBLOQUEADA EN EL MENÚ)": "(NIGHT 6 UNLOCKED IN THE MENU)",
    # Logros
    "PRIMER TURNO": "FIRST SHIFT", "Supera la noche 1.": "Survive night 1.",
    "FIN DE CONTRATO": "END OF CONTRACT", "Supera la noche 5.": "Survive night 5.",
    "ARCHIVISTA": "ARCHIVIST", "Encuentra las 4 pruebas de las cintas.": "Find all 4 pieces of evidence in the tapes.",
    "FIN DEL TURNO": "END OF SHIFT", "Consigue el final verdadero.": "Get the true ending.",
    "HORAS EXTRA": "OVERTIME", "Supera la noche 6.": "Survive night 6.",
    "INTOCABLE": "UNTOUCHABLE", "Supera las 5 noches sin morir ni una vez.": "Survive all 5 nights without dying once.",
    "PUERTAS ABIERTAS": "OPEN DOORS", "Supera una noche (2 o más) sin cerrar la compuerta.": "Survive a night (2 or later) without closing the door.",
    "AHORRO DE ENERGÍA": "POWER SAVER", "Termina una noche (2 o más) con más del 50% de batería.": "Finish a night (2 or later) with over 50% power.",
    "UNA SOLA TOMA": "ONE TAKE", "Termina una cinta con su prueba sin fallar ni una vez.": "Finish a tape with its evidence without failing once.",
    "COMPUERTA CERRADA": "GATE SHUT", "Atrapa a Silas con la compuerta de ducto 10 veces.": "Trap Silas with a duct gate 10 times.",
    "ENCANDILADO": "BLINDED", "Ahuyenta a Barnaby con la linterna 15 veces.": "Scare Barnaby away with the flashlight 15 times.",
    "NO LE QUITES LOS OJOS": "DON'T LOOK AWAY", "Rechaza a la Unidad 0 cinco veces.": "Repel Unit 0 five times.",
    "BUEN OYENTE": "GOOD LISTENER", "Escucha completas las llamadas de las 5 noches.": "Listen to all 5 nights' calls in full.",
    "20/20/20/20": "20/20/20/20", "Supera la Custom Night con todos en 20.": "Beat the Custom Night with everyone at 20.",
    "TURNO COMPLETO": "FULL SHIFT", "Supera todos los desafíos de la Custom Night.": "Beat every Custom Night challenge.",
    "¿VISTE ESO?": "DID YOU SEE THAT?", "Algo pasó frente a una cámara.": "Something passed in front of a camera.",
    "NÚMERO EQUIVOCADO": "WRONG NUMBER", "Recibe una llamada que no era para ti.": "Get a call that wasn't meant for you.",
    "0303": "0303", "Encuentra la cinta que nadie debía escuchar.": "Find the tape no one was supposed to hear.",
    # Custom Night
    "Configura la IA de cada uno (0 a 20) o elige un desafío abajo.": "Set each one's AI (0 to 20) or pick a challenge below.",
    "TURNO DE MARTA": "MARTA'S SHIFT", "SIN AIRE": "NO AIR", "A CIEGAS": "BLIND", "LA BANDA COMPLETA": "THE FULL BAND",
    "Solo Penny, al máximo. La compuerta se traba si queda cerrada más de 5 segundos.": "Only Penny, at max. The door jams if it stays closed over 5 seconds.",
    "Silas al máximo. El oxígeno cae más rápido y la ventilación falla seguido.": "Silas at max. Oxygen drops faster and the ventilation fails often.",
    "Los cuatro en 10, pero la noche empieza con 55% de batería.": "All four at 10, but the night starts at 55% power.",
    "Sin visión nocturna y con fallas de cámaras frecuentes.": "No night vision and frequent camera failures.",
    "Los cuatro en 15. Sin trucos.": "All four at 15. No tricks.", "DESAFÍO": "CHALLENGE",
    # Cintas (minijuegos)
    "MOVERTE: FLECHAS / WASD    //    ESC: SALTAR LA CINTA (SIN PRUEBA)": "MOVE: ARROWS / WASD    //    ESC: SKIP TAPE (NO EVIDENCE)",
    "PRUEBA: ENCONTRADA": "EVIDENCE: FOUND", "PRUEBA NO ENCONTRADA.": "EVIDENCE NOT FOUND.",
    "Puedes repetir esta cinta desde ARCHIVO 1982 en el menú.": "You can replay this tape from the 1982 ARCHIVE in the menu.",
    "¡TE GOLPEÓ UNA CAJA!": "A BOX HIT YOU!", "¡VAPOR! LA PRESIÓN SUBE": "STEAM! THE PRESSURE RISES",
    "¡LA CALDERA EXPLOTÓ! INTENTA DE NUEVO": "THE BOILER EXPLODED! TRY AGAIN", "PRESIÓN CALDERA 3": "BOILER 3 PRESSURE",
    "¡EL VENTILADOR TE ARRASTRÓ!": "THE FAN PULLED YOU IN!", "¡TE VIERON!": "YOU WERE SEEN!",
    "¡TE VIERON! LA LLAVE VOLVIÓ A SU LUGAR": "YOU WERE SEEN! THE KEY WENT BACK", "TIENES LA LLAVE. ¡VUELVE A LA SALIDA!": "YOU HAVE THE KEY. GET BACK TO THE EXIT!",
    "LLAVE MAESTRA: EN TU PODER": "MASTER KEY: IN HAND", "LLAVE MAESTRA: NO": "MASTER KEY: NO",
}

# Textos con partes variables. Cada parte {1}, {2}... se traduce también si está en UI_EN.
PATRONES_EN = [
    (r"^CONTINUAR \(N\.(\d+)\)$", "CONTINUE (N.{1})"),
    (r"^NOCHE (\S+)$", "NIGHT {1}"),
    (r"^NOCHE (\S+) COMPLETADA$", "NIGHT {1} COMPLETE"),
    (r"^NOCHE (\S+)  //  (\d+) AM  //  \[ESC\] PARA CONTINUAR$", "NIGHT {1}  //  {2} AM  //  [ESC] TO CONTINUE"),
    (r"^NOCHE (\S+)  //  RESISTISTE HASTA LAS (\d+) AM$", "NIGHT {1}  //  YOU LASTED UNTIL {2} AM"),
    (r"^BATERÍA: (.*)$", "POWER: {1}"),
    (r"^OXÍGENO: (.*)$", "OXYGEN: {1}"),
    (r"^BULBO LINTERNA: (.*)$", "FLASHLIGHT BULB: {1}"),
    (r"^\[F1\] POST-PROCESADO CRT: ACTIVO$", "[F1] CRT POST-PROCESSING: ON"),
    (r"^\[F1\] POST-PROCESADO CRT: OFF$", "[F1] CRT POST-PROCESSING: OFF"),
    (r"^PRUEBAS: (\d+)/4   LOGROS: (\d+/\d+)$", "EVIDENCE: {1}/4   ACHIEVEMENTS: {2}"),
    (r"^PRUEBAS (\d+)/4   //   LOGROS (\d+/\d+)$", "EVIDENCE {1}/4   //   ACHIEVEMENTS {2}"),
    (r"^(\d+) DE (\d+) DESBLOQUEADOS$", "{1} OF {2} UNLOCKED"),
    (r"^CINTAS RECUPERADAS DEL SISTEMA DE SEGURIDAD  //  PRUEBAS: (.*)$", "TAPES RECOVERED FROM THE SECURITY SYSTEM  //  EVIDENCE: {1}"),
    (r"^CINTA (\d+)$", "TAPE {1}"),
    (r"^Supera la noche (\d+)$", "Survive night {1}"),
    (r"^\[(\w+)\] - (.*)$", "[{1}] - {2}"),
    (r"^RESTABLECIENDO SISTEMA\.\.\. (.*)$", "RESTORING SYSTEM... {1}"),
    (r"^SEÑUELO RECARGANDO \((.*)\)$", "LURE RECHARGING ({1})"),
    (r"^COMPUERTA CERRADA EN (.*)$", "GATE CLOSED AT {1}"),
    (r"^COMPUERTA REARMANDO \((.*)\)$", "GATE RESETTING ({1})"),
    (r"^LÍNEA ACTIVA // SUPERVISIÓN TURNO (.*)$", "LINE ACTIVE // SHIFT SUPERVISION {1}"),
    (r"^\[IR LOCK // ANOMALÍA PARALIZADA - (.*)\]$", "[IR LOCK // ANOMALY FROZEN - {1}]"),
    (r"^\[VISIÓN NOCTURNA IR: (.*) - CLIC DER / V\]$", "[IR NIGHT VISION: {1} - RIGHT CLICK / V]"),
    (r"^\[IR RECARGANDO\.\.\. (.*)\]$", "[IR RECHARGING... {1}]"),
    (r"^\[CLIC DER / V\] VISIÓN NOCTURNA IR \((.*)\)$", "[RIGHT CLICK / V] IR NIGHT VISION ({1})"),
    (r"^DESAFÍOS SUPERADOS: (.*)$", "CHALLENGES BEATEN: {1}"),
    (r"^★ (.*)$", "★ {1}"),
    (r"^OBJETIVO: (.*)$", "OBJECTIVE: {1}"),
    (r"^PRUEBA ENCONTRADA: (.*)$", "EVIDENCE FOUND: {1}"),
    (r"^¡PRUEBA ENCONTRADA! (.*)$", "EVIDENCE FOUND! {1}"),
    (r"^INTENTOS: (\d+)   //   ESC: SALTAR$", "ATTEMPTS: {1}   //   ESC: SKIP"),
    (r"^VÁLVULA (\d+) CERRADA$", "VALVE {1} CLOSED"),
    (r"^PRIMERO LA VÁLVULA (\d+)$", "VALVE {1} FIRST"),
    (r"^PREPARANDO SONIDO: (.*)$", "PREPARING SOUND: {1}"),
    (r"^(\d+)h (\d+)m$", "{1}h {2}m"),
]
_PATRONES = [(re.compile(p), t) for p, t in PATRONES_EN]


def traducir(texto):
    if ACTUAL["idioma"] != "en" or not texto:
        return texto
    if texto in UI_EN:
        return UI_EN[texto]
    if texto.upper() in UI_EN and texto.isupper():
        return UI_EN[texto.upper()]
    for patron, plantilla in _PATRONES:
        m = patron.match(texto)
        if m:
            salida = plantilla
            for i, g in enumerate(m.groups(), 1):
                salida = salida.replace("{" + str(i) + "}", traducir(g) if g else "")
            return salida
    return texto


T = traducir


class FuenteTraducible(pygame.font.Font):
    """Fuente que traduce el texto antes de dibujarlo o medirlo."""
    def render(self, texto, *args, **kwargs):
        return super().render(traducir(texto), *args, **kwargs)

    def size(self, texto):
        return super().size(traducir(texto))
