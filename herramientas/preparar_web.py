# -*- coding: utf-8 -*-
"""Arma la versión web del juego (para jugar en el navegador) con pygbag.

En el navegador el bucle principal tiene que "devolver el control" a la página en cada
cuadro (con `await asyncio.sleep(0)`), si no la pestaña se congela. Para no tocar el
código del juego de escritorio, este script genera una copia en `build_web/` donde:
  - el `while True:` principal de fnaf_fabrica.py queda dentro de `async def`,
  - se agregan las declaraciones `global` necesarias (las calcula solo),
  - y se guarda como `main.py`, que es lo que pygbag busca.

Uso (desde la carpeta del proyecto):
    pip install pygbag
    python herramientas/preparar_web.py            # solo prepara build_web/
    python herramientas/preparar_web.py --compilar # prepara y compila (build_web/build/web)
    python -m pygbag build_web                     # prueba local en http://localhost:8000
"""
import ast
import os
import shutil
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, "build_web")
MODULOS = ["audio.py", "controles.py", "datos.py", "efectos.py", "guardado.py", "historia.py", "historia_en.py",
           "idioma.py", "mando.py", "minijuegos.py", "progreso.py", "recursos.py", "unidad0.py", "ventana.py"]


def nombres_asignados(nodo):
    """Todos los nombres que se asignan dentro del bucle (pasan a ser globales)."""
    nombres = set()
    for n in ast.walk(nodo):
        if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)):
            nombres.add(n.id)
        elif isinstance(n, (ast.Import, ast.ImportFrom)):
            for alias in n.names:
                nombres.add((alias.asname or alias.name).split(".")[0])
        elif isinstance(n, ast.ExceptHandler) and n.name:
            nombres.add(n.name)
        elif isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            nombres.add(n.name)
    return nombres


def convertir(codigo):
    arbol = ast.parse(codigo)
    bucles = [n for n in arbol.body if isinstance(n, ast.While)]
    if len(bucles) != 1:
        raise SystemExit(f"Se esperaba un solo 'while' principal y hay {len(bucles)}")
    bucle = bucles[0]
    if arbol.body[-1] is not bucle:
        raise SystemExit("El bucle principal tiene que ser lo último del archivo")
    lineas = codigo.splitlines()
    antes = lineas[:bucle.lineno - 1]
    cuerpo = lineas[bucle.lineno - 1:]
    globales = sorted(nombres_asignados(bucle))
    # Los mensajes y errores de Python van a la consola del navegador (F12), para poder depurar
    consola = ["import sys",
               "if sys.platform == 'emscripten':",
               "    import platform as _plataforma_web",
               "    class _ConsolaWeb:",
               "        def write(self, texto):",
               "            if texto.strip():",
               "                _plataforma_web.window.console.log(texto)",
               "        def flush(self):",
               "            pass",
               "    sys.stdout = sys.stderr = _ConsolaWeb()",
               ""]
    salida = consola + list(antes)
    salida += ["", "# --- Agregado por herramientas/preparar_web.py (versión navegador) ---",
               "import asyncio", "", "async def _bucle_principal():"]
    for i in range(0, len(globales), 8):
        salida.append("    global " + ", ".join(globales[i:i + 8]))
    primera = True
    for linea in cuerpo:
        salida.append(("    " + linea) if linea.strip() else linea)
        if primera:
            salida.append("        await asyncio.sleep(0)")
            primera = False
    salida += ["", "asyncio.run(_bucle_principal())", ""]
    nuevo = "\n".join(salida)
    ast.parse(nuevo)   # Que siga siendo Python válido
    return nuevo


def preparar():
    if os.path.isdir(DESTINO):
        shutil.rmtree(DESTINO)
    os.makedirs(DESTINO)
    for m in MODULOS:
        shutil.copy2(os.path.join(RAIZ, m), DESTINO)
    shutil.copytree(os.path.join(RAIZ, "assets"), os.path.join(DESTINO, "assets"))
    with open(os.path.join(RAIZ, "fnaf_fabrica.py"), encoding="utf-8") as f:
        codigo = f.read()
    with open(os.path.join(DESTINO, "main.py"), "w", encoding="utf-8") as f:
        f.write(convertir(codigo))
    icono = os.path.join(RAIZ, "assets", "icono.png")
    if os.path.exists(icono):
        shutil.copy2(icono, os.path.join(DESTINO, "favicon.png"))
    print("Listo:", DESTINO)


if __name__ == "__main__":
    preparar()
    if "--compilar" in sys.argv:
        subprocess.check_call([sys.executable, "-m", "pygbag", "--build", "--title", "FNAF Industrial Sector",
                               DESTINO])
        print("Versión web en:", os.path.join(DESTINO, "build", "web"))
