# -*- coding: utf-8 -*-
"""Suite de verificación automatizada para FNAF: Industrial Sector (1982).
Comprueba sintaxis, integridad de assets (imágenes, animaciones, audios, voces),
paridad de textos ES/EN y lógica de progreso/IA sin requerir ventana gráfica."""
import os
import sys
import py_compile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RAIZ)


def verificar_sintaxis():
    archivos_py = [f for f in os.listdir(RAIZ) if f.endswith(".py")]
    assert archivos_py, "No se encontraron archivos .py en la raíz"
    for nombre in sorted(archivos_py):
        py_compile.compile(os.path.join(RAIZ, nombre), doraise=True)
    print(f"[OK] Sintaxis verificada en {len(archivos_py)} módulos Python.")


def verificar_historia_e_idioma():
    import historia as h_es
    import historia_en as h_en
    import idioma

    claves = [
        "INTRO_JUEGO", "TITULOS_NOCHE", "DIALOGOS_NOCHES", "CINTAS",
        "FINAL_NORMAL", "FINAL_VERDADERO", "FRASES_ALUCINACION",
        "FINAL_NOCHE6", "LLAMADA_EQUIVOCADA", "CINTA_SECRETA", "CREDITOS",
    ]
    for c in claves:
        assert hasattr(h_es, c), f"Falta {c} en historia.py"
        assert hasattr(h_en, c), f"Falta {c} en historia_en.py"

    for n in range(1, 6):
        assert len(h_es.DIALOGOS_NOCHES[n]) == len(h_en.DIALOGOS_NOCHES[n]), f"Desfase en DIALOGOS_NOCHES[{n}]"
    for c in range(1, 5):
        assert c in h_es.CINTAS and c in h_en.CINTAS, f"Falta cinta {c}"

    idioma.ACTUAL["idioma"] = "en"
    assert idioma.T("NUEVO JUEGO") == "NEW GAME"
    assert idioma.T("Supera la noche 1") == "Survive night 1"
    idioma.ACTUAL["idioma"] = "es"
    print("[OK] Paridad de historia ES/EN y traducciones verificada.")


def verificar_assets():
    import recursos

    requeridos = [
        # Oficina y periódicos
        "oficina_base.jpg", "oficina_puerta_abierta.jpg", "techo_rejilla.jpg",
        "periodico.jpg", "periodico_verdadero.jpg",
        # Cámaras y ductos
        *(f"cam_0{i}.jpg" for i in range(1, 9)),
        *(f"vent_0{i}.jpg" for i in range(1, 5)),
        "vent_bloqueada.jpg", "vent_tunel.jpg",
        # Sprites base y animaciones en oficina
        "barnaby_cam.png", "barnaby_oficina.png", "barnaby_cerca.png",
        "penny_cam.png", "penny_puerta.png",
        "bunny_cam.png", "bunny_ventana.png",
        "silas_vent.png", "silas_techo.png",
        "unidad0.png",
        # Sprites específicos por cámara
        "barnaby_cam02.png", "barnaby_cam07.png",
        "penny_cam03.png", "penny_cam06.png",
        "bunny_cam04.png", "bunny_cam05.png", "bunny_cam08.png",
        "silas_vent02.png", "silas_vent03.png", "silas_vent04.png",
        "unidad0_cam06.png", "unidad0_cam02.png", "unidad0_cam07.png",
        *(f"{sp}_{k:02d}.png" for sp in ("barnaby_oficina", "barnaby_cerca", "penny_puerta", "bunny_ventana", "silas_techo", "unidad0") for k in range(3)),
        # Jumpscares animados
        *(f"jumpscare_{a}_{k:02d}.jpg" for a in ("barnaby", "penny", "bunny", "silas", "unidad0") for k in range(3)),
        # Audio: gritos y llamadas
        *(f"grito_{a}.ogg" for a in ("barnaby", "penny", "bunny", "silas", "unidad0")),
        *(f"llamada_noche_{n}.ogg" for n in range(1, 6)),
    ]
    faltantes = [r for r in requeridos if r.lower() not in recursos.INDICE_ASSETS]
    assert not faltantes, f"Assets faltantes: {faltantes}"
    print(f"[OK] {len(requeridos)} assets principales verificados en assets/.")


def verificar_logica_modulos():
    from unidad0 import Unidad0, SEGUNDOS_PARA_RECHAZAR
    from progreso import Progreso

    u0 = Unidad0()
    u0.reiniciar(True, limite=5.0)
    assert u0.sala() == "CAM_04"
    assert u0.actualizar(5.1, None) == "avanzo"
    assert u0.sala() == "CAM_06"
    u0.nodo = 3  # CAM_07 (pasillo)
    assert u0.en_pasillo()
    assert u0.actualizar(SEGUNDOS_PARA_RECHAZAR + 0.1, "CAM_07") == "rechazada"
    assert u0.nodo == 0

    p = Progreso({})
    p.desbloquear("primer_turno")
    assert "primer_turno" in p.logros
    print("[OK] Lógica de Unidad0 y Progreso verificada.")


if __name__ == "__main__":
    verificar_sintaxis()
    verificar_historia_e_idioma()
    verificar_assets()
    verificar_logica_modulos()
    print("TODAS LAS VERIFICACIONES PASARON CORRECTAMENTE.")
