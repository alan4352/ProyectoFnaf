# Configuración para armar el APK de Android con buildozer.
# No se usa directo: herramientas/preparar_android.py copia el juego a build_android/
# (con main.py, que es lo que Android ejecuta) y pone este archivo ahí.
[app]
title = FNAF Industrial Sector
package.name = fnafindustrial
package.domain = io.github.alan4352
source.dir = .
source.include_exts = py,png,jpg,ogg,wav,mp3,ttf,json
version = 1.1
requirements = python3,pygame
p4a.local_recipes = ./recipes
source.exclude_dirs = recipes, bin
orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/assets/icono.png
android.archs = arm64-v8a, armeabi-v7a
android.api = 34
android.minapi = 24
android.accept_sdk_license = True
p4a.bootstrap = sdl2
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 0
