# Receta de pygame para python-for-android, con una versión más nueva que la que trae por defecto
# (la 2.1.0 no compila con Python 3.14). Cython regenera los archivos .c para esta versión de Python.
from pythonforandroid.recipes.pygame import Pygame2Recipe


class PygameNuevo(Pygame2Recipe):
    version = "2.6.1"
    hostpython_prerequisites = ["setuptools", "cython>=3.1"]


recipe = PygameNuevo()
