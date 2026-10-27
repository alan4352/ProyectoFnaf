# -*- coding: utf-8 -*-
"""Historia de FNAF: Industrial Sector (1982).

Todos los textos de la historia están acá: llamadas de cada noche, introducción,
cintas (minijuegos), pruebas y finales. Se pueden editar sin tocar el resto del código.

RESUMEN DE LA HISTORIA
----------------------
Ensambladora Dunmore S.A. fabricaba animatrónicos para parques de diversiones.
En 1982 probó una aleación experimental, la "matriz M-82", que graba los movimientos de
quien calibra cada unidad. Cuatro operarios del turno noche calibraron a la banda:

    Walter Ibarra (capataz)              -> BARNABY
    Marta Peña (soldadora)               -> PENNY
    Rubén "Rusty" Ortiz (depósito)       -> RUSTY BUNNY
    Tomás Silva (técnico de ventilación) -> SILAS

La noche del 3 de marzo de 1982, para cumplir un pedido urgente, el jefe de planta
Ernesto Varela ordenó no apagar los hornos y cerró las salidas de emergencia con
candados nuevos "para evitar robos". Una caldera explotó. Los cuatro murieron.
Varela informó "una falla eléctrica sin víctimas" y los anotó como "renunciados".

Desde entonces, a las 3 AM los servos se activan solos: cada unidad repite el último
turno de su operario, buscando la única salida que quedaba... la oficina de Varela,
que ahora es la oficina de seguridad. Ahí estás vos.

Octubre de 1982: la planta cierra para siempre el sábado 23 a las 6:00 AM.
Te contratan como guardia por cinco noches. Quien te llama cada noche es Varela.

Las cintas (minijuegos) muestran la noche del accidente desde los ojos de cada operario.
En cada una hay una PRUEBA escondida. Con las cuatro pruebas, el final cambia.
"""

# -------------------------------------------------------------
# Introducción (al empezar un juego nuevo)
# -------------------------------------------------------------
INTRO_JUEGO = {
    "titulo": "ENSAMBLADORA DUNMORE S.A. // SECTOR B",
    "lineas": [
        "Buenos días. Lunes 18 de octubre de 1982.",
        "",
        "Queda contratado como guardia nocturno por cinco noches,",
        "hasta el cierre definitivo de la planta: sábado 23, 6:00 AM.",
        "",
        "Su tarea: vigilar las cámaras y que nadie entre a la oficina de seguridad.",
        "Las unidades de entretenimiento están desconectadas desde marzo.",
        "Si escucha ruidos, ignórelos. Es una planta vieja.",
        "",
        "Turno: 12:00 AM a 6:00 AM. No abandone la oficina.",
        "",
        "                                  E. Varela, Jefe de Planta",
    ],
}

# Títulos antes de cada noche (FNAF clásico: "NOCHE 1 - 12:00 AM")
TITULOS_NOCHE = {
    1: "LUNES 18 DE OCTUBRE, 1982",
    2: "MARTES 19 DE OCTUBRE, 1982",
    3: "MIÉRCOLES 20 DE OCTUBRE, 1982",
    4: "JUEVES 21 DE OCTUBRE, 1982",
    5: "VIERNES 22 DE OCTUBRE, 1982 // ÚLTIMA NOCHE",
}

# -------------------------------------------------------------
# Llamadas de cada noche (se muestran como subtítulos; cada línea dura unos 5 segundos)
# -------------------------------------------------------------
DIALOGOS_NOCHES = {
    1: [
        "--- TRANSMISIÓN ENTRANTE: SUPERVISIÓN DE TURNO (NOCHE 1) ---",
        "¿Hola? ¿Me escuchas? Bien. Bienvenido a la planta Dunmore. Te hablo desde supervisión.",
        "Esa oficina era la del jefe de planta. Es la única con salida propia, por eso tiene compuerta blindada.",
        "A tu izquierda, la compuerta [Tecla A]. Si ves a Penny en la puerta, ciérrala.",
        "A la derecha, la persiana: MANTÉN PRESIONADO EL BOTÓN si ves a Rusty Bunny en el vidrio.",
        "Si Barnaby viene por el pasillo, encándilalo con la linterna [F]. No la dejes prendida mucho: se recalienta.",
        "Arriba [W] está la rejilla de ventilación. Sellarla [ESPACIO] te deja sin aire. Úsala poco.",
        "Si algo falla, el panel [M] reinicia turbinas y cámaras. Ah, y si escuchas respirar del otro lado de la puerta... ciérrala.",
        "Son unidades viejas. Se mueven un poco de noche. No es nada personal. Buenas noches.",
    ],
    2: [
        "--- TRANSMISIÓN ENTRANTE: SUPERVISIÓN DE TURNO (NOCHE 2) ---",
        "Sigues ahí. Bien. El último guardia no volvió para la segunda noche. Renunció, supongo.",
        "Silas era la unidad de mantenimiento. Aprendió a meterse en los ductos de ventilación.",
        "En el mapa de ductos tienes un SEÑUELO DE AUDIO: úsalo para alejarlo de la oficina.",
        "Y con clic derecho sobre un ducto cierras su compuerta. Si pasa por ahí, vuelve al principio.",
        "La visión nocturna [V] los paraliza mientras los miras, pero la batería del IR dura poco.",
        "Si escuchas golpes en el techo, es Silas en la rejilla. Mira arriba y séllala a tiempo.",
        "Varios técnicos renunciaron en marzo. Mucho papeleo. No importa. Buenas noches.",
    ],
    3: [
        "--- TRANSMISIÓN ENTRANTE: SUPERVISIÓN DE TURNO (NOCHE 3) ---",
        "Desde esta noche el generador auxiliar de la CAM_08 pierde voltaje.",
        "Mantén presionado el botón de la bobina en CAM_08 para que no se descargue.",
        "Si la bobina llega a cero, fallan las luces de la oficina y Rusty corre mucho más rápido.",
        "Rusty era del depósito... digo, la unidad del depósito. Lo calibraron ahí.",
        "Si encuentras cintas viejas por la planta, no las escuches. Son propiedad de la empresa.",
        "No preguntes por marzo. Buenas noches.",
    ],
    4: [
        "--- REPRODUCIENDO CINTA ARCHIVADA // 03-MAR-1982 // 02:52 AM ---",
        "'Habla Walter Ibarra, capataz del turno noche. Si alguien escucha esto...'",
        "'Varela cerró las salidas de emergencia con candados nuevos esta tarde. Dice que por los robos.'",
        "'La caldera tres está pasando de presión y no nos deja apagar los hornos. Hay un pedido.'",
        "'Marta fue a cerrar las válvulas. Tomás está en los ductos. Rubén fue a buscar la llave maestra.'",
        "'Si esto sale mal, que se sepa que fue Varela. Que se sepa que no renun...'",
        "--- [CORTE] --- Disculpa. Esa cinta no debía estar en el sistema. Vigila la bobina.",
    ],
    5: [
        "--- TRANSMISIÓN FINAL // LÍNEA PRIVADA ---",
        "Ya escuchaste la cinta. Así que no tiene sentido seguir fingiendo. Soy Ernesto Varela.",
        "Yo firmé la orden de no apagar los hornos. Yo cambié los candados. Había un pedido. Había plazos.",
        "Ellos no te buscan a ti. Buscan esta oficina. La salida. Me buscan a mí.",
        "Esta noche están todos despiertos. Recarga la bobina, usa el señuelo, cierra todo.",
        "A las 6:00 la planta se sella para siempre. Con ellos adentro. Y lo que pasó en marzo, también.",
        "Aguanta hasta las seis. Después, nadie tiene que saber nada.",
    ],
}

# -------------------------------------------------------------
# Cintas (minijuegos después de las noches 1 a 4)
# -------------------------------------------------------------
CINTAS = {
    1: {
        "titulo": "CINTA 1 DE 4 // 03-MAR-1982 // 02:41 AM",
        "personaje": "WALTER IBARRA, CAPATAZ",
        "intro": [
            "Las cintas transportadoras no se detienen: Varela no deja parar la línea.",
            "Walter quiere grabar un mensaje en la grabadora de la oficina del fondo.",
            "Cruza las cintas sin que te golpeen las cajas. Las cintas te arrastran.",
        ],
        "objetivo": "LLEGA A LA GRABADORA",
        "pista": "Algo brilla al costado de una de las cintas...",
        "outro": [
            "WALTER: 'Habla Walter Ibarra. Si alguien escucha esto...'",
            "Grabó todo lo que sabía. Escondió la cinta en el sistema de seguridad.",
            "Cuarenta minutos después, los servos de Barnaby se movieron solos por primera vez.",
        ],
        "prueba": "TARJETA DE FICHAJE DE W. IBARRA",
        "prueba_detalle": "Entrada: 22:00 hs. Salida: (en blanco).",
    },
    2: {
        "titulo": "CINTA 2 DE 4 // 03-MAR-1982 // 02:58 AM",
        "personaje": "MARTA PEÑA, SOLDADORA",
        "intro": [
            "La caldera tres está fuera de control. La presión no para de subir.",
            "Cierra las tres válvulas EN ORDEN (1, 2, 3) antes de que explote.",
            "Cuidado con los escapes de vapor: te empujan atrás y suben la presión.",
        ],
        "objetivo": "CIERRA LAS VÁLVULAS 1 - 2 - 3",
        "pista": "En el escritorio del fondo hay un papel con membrete...",
        "outro": [
            "Las válvulas cerraron. La puerta del cuarto de calderas, no: tenía candado nuevo.",
            "Marta esperó junto a los hornos.",
            "Meses después encontraron a Penny en el mismo lugar. Intacta. Tibia.",
        ],
        "prueba": "MEMO INTERNO FIRMADO POR E. VARELA",
        "prueba_detalle": "'NO APAGAR HORNOS BAJO NINGÚN CONCEPTO. CUMPLIR EL PEDIDO.'",
    },
    3: {
        "titulo": "CINTA 3 DE 4 // 03-MAR-1982 // 03:06 AM",
        "personaje": "TOMÁS SILVA, TÉCNICO DE VENTILACIÓN",
        "intro": [
            "El humo llena el Sector B. Tomás entra a los ductos para encender la turbina.",
            "Está oscuro: solo ves lo que alumbra tu linterna.",
            "Los ventiladores giran a intervalos. No pases mientras están encendidos.",
        ],
        "objetivo": "ENCIENDE LA TURBINA DE EXTRACCIÓN",
        "pista": "Hay un plano enrollado en algún ducto sin salida...",
        "outro": [
            "La turbina arrancó y el humo empezó a salir.",
            "Tomás siguió el aire hasta la rejilla de salida. Estaba soldada desde afuera.",
            "Silas nunca volvió a bajar de los ductos.",
        ],
        "prueba": "PLANO DE EVACUACIÓN DEL SECTOR B",
        "prueba_detalle": "Las cuatro salidas de emergencia están tachadas a mano. Firma: E.V.",
    },
    4: {
        "titulo": "CINTA 4 DE 4 // 03-MAR-1982 // 03:15 AM",
        "personaje": "RUBÉN 'RUSTY' ORTIZ, DEPÓSITO",
        "intro": [
            "La llave maestra abre la salida de emergencia del depósito.",
            "Está en el archivo de la gerencia. Alguien recorre el archivo con una linterna.",
            "Que no te vea. Toma la llave y vuelve a la puerta.",
        ],
        "objetivo": "TOMA LA LLAVE Y VUELVE A LA SALIDA",
        "pista": "Un cajón del archivo quedó entreabierto...",
        "outro": [
            "Rubén llegó a la salida con la llave maestra.",
            "La llave no entraba. Varela había cambiado el candado esa misma tarde.",
            "Golpeó el vidrio hasta el amanecer. Rusty todavía lo hace.",
        ],
        "prueba": "NÓMINA DEL TURNO NOCHE",
        "prueba_detalle": "Cuatro nombres tachados con la nota: 'RENUNCIARON. NO REPORTAR.'",
    },
}

# -------------------------------------------------------------
# Finales (después de la noche 5)
# -------------------------------------------------------------
FINAL_NORMAL = {
    "periodico": {
        "cabecera": "THE INDUSTRIAL CHRONICLE",
        "fecha": "SÁBADO 23 DE OCTUBRE DE 1982  //  EDICIÓN MATUTINA",
        "titular": "PLANTA DUNMORE CERRÓ SUS PUERTAS",
        "bajada": "LA GERENCIA SELLÓ EL SECTOR B Y DESMANTELA LAS LÍNEAS",
        "articulo": [
            "La Ensambladora Dunmore cerró esta mañana",
            "su planta del Sector B tras años de pérdidas",
            "y reiteradas fallas eléctricas.",
            "",
            "El jefe de planta, Ernesto Varela, aseguró",
            "que 'no hubo heridos en toda la historia",
            "de la planta' y que las unidades de",
            "entretenimiento serán destruidas.",
            "",
            "El último guardia nocturno no pudo",
            "ser contactado por este diario.",
        ],
        "pie_foto": "Unidades mecánicas confinadas en el Sector B.",
        "sello": "CASO CERRADO",
    },
    "titulo": "FINAL: CASO CERRADO",
    "lineas": [
        "Sobreviviste a las cinco noches.",
        "A las 6:00 AM las compuertas se sellaron. Con ellos adentro.",
        "Las cintas nunca salieron de la planta. Nadie preguntó por marzo.",
        "",
        "Pero a las 3 AM, en el Sector B, cuatro unidades siguen buscando la salida.",
        "",
        "(Hay pruebas que no encontraste. Revisa el ARCHIVO 1982 en el menú.)",
    ],
}

FINAL_VERDADERO = {
    "periodico": {
        "cabecera": "THE INDUSTRIAL CHRONICLE",
        "fecha": "LUNES 25 DE OCTUBRE DE 1982  //  EDICIÓN EXTRAORDINARIA",
        "titular": "LA VERDAD DEL SECTOR B",
        "bajada": "CUATRO OPERARIOS MURIERON EN MARZO. JEFE DE PLANTA DETENIDO",
        "articulo": [
            "Un guardia nocturno entregó a la justicia",
            "cuatro pruebas halladas en la planta Dunmore:",
            "una tarjeta de fichaje, un memo, un plano",
            "y una nómina adulterada.",
            "",
            "Walter Ibarra, Marta Peña, Rubén Ortiz y",
            "Tomás Silva no renunciaron: murieron el",
            "3 de marzo, encerrados por orden de",
            "Ernesto Varela, hoy detenido.",
            "",
            "Sus familias podrán despedirlos.",
        ],
        "pie_foto": "Ernesto Varela, al salir de la fiscalía.",
        "sello": "CASO REABIERTO",
    },
    "titulo": "FINAL VERDADERO: FIN DEL TURNO",
    "lineas": [
        "Sobreviviste a las cinco noches. Y te llevaste las pruebas.",
        "",
        "El domingo, la policía abrió las salidas de emergencia del Sector B.",
        "Barnaby, Penny, Rusty y Silas estaban sentados frente a la puerta abierta.",
        "Apagados. Por primera vez desde marzo.",
        "",
        "Walter, Marta, Rubén y Tomás terminaron su turno.",
        "",
        "GRACIAS POR JUGAR.",
    ],
}

# Frases de las alucinaciones (destellos rojos durante la noche)
FRASES_ALUCINACION = [
    "TERMINEN EL TURNO",
    "LAS SALIDAS ESTABAN CERRADAS",
    "VARELA LO SABÍA",
    "NO RENUNCIAMOS",
    "¿POR QUÉ NO ABRIERON?",
    "03-MAR-1982 // 03:15 AM",
]
