# Receta de pygame para python-for-android, con una versión más nueva que la que trae por defecto
# (la 2.1.0 no compila con Python 3.14). Cython regenera los archivos .c para esta versión de Python.
from os.path import join

from pythonforandroid.recipes.pygame import Pygame2Recipe


class PygameNuevo(Pygame2Recipe):
    version = "2.6.1"
    hostpython_prerequisites = ["setuptools", "cython>=3.1"]

    def prebuild_arch(self, arch):
        super().prebuild_arch(arch)
        # Cython 3.1 ya no permite asignar __dict__ en _sprite.pyx (módulo que el juego no usa):
        # se quita esa línea para que compile.
        ruta = join(self.get_build_dir(arch.arch), "src_c", "cython", "pygame", "_sprite.pyx")
        with open(ruta, encoding="utf-8") as f:
            texto = f.read()
        texto = texto.replace("        self.__dict__ = {}\n", "        pass\n")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto)


recipe = PygameNuevo()
