#!/bin/bash
# Instala el APK en el emulador, lo abre dos veces y guarda logcat, capturas y el registro de errores.
PAQUETE=io.github.alan4352.fnafindustrial
mkdir -p prueba
adb install -r build_android/bin/*.apk > prueba/instalar.txt 2>&1
adb logcat -c
adb shell am start -n $PAQUETE/org.kivy.android.PythonActivity
sleep 45
adb exec-out screencap -p > prueba/captura_1.png
adb shell input tap 600 400
sleep 10
adb exec-out screencap -p > prueba/captura_2.png
adb shell pidof $PAQUETE > prueba/proceso.txt 2>&1 || echo "NO ESTA CORRIENDO" >> prueba/proceso.txt
adb logcat -d > prueba/logcat.txt
adb shell run-as $PAQUETE ls -la files/app > prueba/archivos_app.txt 2>&1 || true
adb shell run-as $PAQUETE cat files/app/registro_error.txt > prueba/registro_error.txt 2>&1 || true
# Segunda vez (si se cerró de golpe, el lanzador muestra el error)
adb shell am force-stop $PAQUETE
adb logcat -c
adb shell am start -n $PAQUETE/org.kivy.android.PythonActivity
sleep 30
adb exec-out screencap -p > prueba/captura_3.png
adb logcat -d > prueba/logcat_2.txt
exit 0
