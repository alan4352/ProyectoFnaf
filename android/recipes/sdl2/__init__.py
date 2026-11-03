# SDL2 compilado optimizado.
# python-for-android compila SDL con ndk-build en modo depuración (NDK_DEBUG=1, sin optimizar: -O0)
# aunque el APK se arme en modo release, porque el paso que compila las librerías no se entera.
# SDL hace todo el trabajo de mostrar la imagen, así que sin optimizar el juego va muy lento.
from pythonforandroid.recipes.sdl2 import LibSDL2Recipe


class SDL2Optimizado(LibSDL2Recipe):
    def build_arch(self, arch):
        antes = self.ctx.build_as_debuggable
        self.ctx.build_as_debuggable = False     # => NDK_DEBUG=0 (compilación optimizada)
        try:
            super().build_arch(arch)
        finally:
            self.ctx.build_as_debuggable = antes


recipe = SDL2Optimizado()
