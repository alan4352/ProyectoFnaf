# Receta de pygame para python-for-android, con una versión más nueva que la que trae por defecto
# (la 2.1.0 no compila con Python 3.14). Cython regenera los archivos .c para esta versión de Python.
from os.path import join

from pythonforandroid.recipes.pygame import Pygame2Recipe


def _reemplazar(ruta, viejo, nuevo):
    with open(ruta, encoding="utf-8") as f:
        texto = f.read()
    if viejo in texto:
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(texto.replace(viejo, nuevo))


class PygameNuevo(Pygame2Recipe):
    version = "2.6.1"
    hostpython_prerequisites = ["setuptools", "cython>=3.1"]

    def prebuild_arch(self, arch):
        carpeta = self.get_build_dir(arch.arch)
        # La configuración para Android de pygame 2.6.1 se olvida de los archivos simd_blitters:
        # sin ellos surface.so no carga ("cannot locate symbol alphablit_alpha_sse2...") y con él
        # tampoco display, draw, image... Se agregan igual que en la configuración de escritorio.
        _reemplazar(join(carpeta, "buildconfig", "Setup.Android.SDL2.in"),
                    "surface src_c/surface.c",
                    "surface src_c/simd_blitters_sse2.c src_c/simd_blitters_avx2.c src_c/surface.c")
        # Cython 3.1 ya no permite asignar __dict__ en _sprite.pyx (módulo que el juego no usa).
        _reemplazar(join(carpeta, "src_c", "cython", "pygame", "_sprite.pyx"),
                    "        self.__dict__ = {}\n", "        pass\n")
        super().prebuild_arch(arch)


recipe = PygameNuevo()
