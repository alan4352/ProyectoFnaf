#!/bin/bash
# Instala el APK en el emulador, lo abre, empieza una noche y guarda logcat, capturas y el registro de errores.
PAQUETE=io.github.alan4352.fnafindustrial
mkdir -p prueba
adb install -r build_android/bin/*.apk > prueba/instalar.txt 2>&1
adb logcat -c
adb shell am start -n $PAQUETE/org.kivy.android.PythonActivity
sleep 40
adb exec-out screencap -p > prueba/captura_1_menu.png
# Convierte coordenadas del juego (1200x700) a la pantalla del emulador (la imagen se escala centrada)
TAM=$(adb shell wm size | grep -o '[0-9]*x[0-9]*' | tail -1)
W=${TAM%x*}; H=${TAM#*x}
if [ "$W" -lt "$H" ]; then T=$W; W=$H; H=$T; fi
toque() { python3 -c "
w,h=$W,$H; k=min(w/1200,h/700); ox=(w-1200*k)/2; oy=(h-700*k)/2
print(int(ox+$1*k), int(oy+$2*k))" | { read X Y; adb shell input tap $X $Y; }; }
echo "pantalla ${W}x${H}" > prueba/pantalla.txt
toque 560 240          # NUEVO JUEGO
sleep 3
adb exec-out screencap -p > prueba/captura_2_intro.png
adb shell input keyevent 4   # Atrás = ESC: saltea la introducción
sleep 8
adb exec-out screencap -p > prueba/captura_3_noche.png
toque 1112 474         # Botón táctil LINTERNA... (solo una prueba de toque)
sleep 1
toque 1112 360         # TECHO
sleep 2
adb exec-out screencap -p > prueba/captura_4_techo.png
toque 1112 360         # BAJAR
sleep 1
toque 600 672          # Pestaña del monitor de cámaras
sleep 3
adb exec-out screencap -p > prueba/captura_5_camaras.png
adb shell pidof $PAQUETE > prueba/proceso.txt 2>&1 || echo "NO ESTA CORRIENDO" >> prueba/proceso.txt
adb logcat -d > prueba/logcat.txt
adb shell run-as $PAQUETE cat files/app/registro_error.txt > prueba/registro_error.txt 2>&1 || true
exit 0
