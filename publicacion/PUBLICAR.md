# Cómo publicar FNAF: Industrial Sector

Guía paso a paso para armar el `.exe` y subir el juego a **itch.io** (recomendado) o a **GitHub Releases**.

---

## 1. Compilar el `.exe` (en tu computadora con Windows)

1. Tené instalado **Python 3.10 o más nuevo** (desde python.org, marcando *"Add Python to PATH"*).
2. Hacé doble clic en **`compilar.bat`**. El script hace todo solo:
   - crea el entorno virtual `venv` si no existe,
   - instala `pygame-ce` y `pyinstaller` (de `requirements.txt`),
   - compila el juego con el ícono `icono.ico`.
3. El juego queda en **`dist\FNAF_Industrial.exe`**. Es un solo archivo: lleva adentro todas las imágenes.

> Si la instalación falla con un error de `pygame` o de *wheel*, borrá la carpeta `venv` y volvé a
> ejecutar `compilar.bat`. El juego usa **pygame-ce**, que tiene versión lista para Python 3.10 a 3.15.

### Opción sin compilar en tu computadora: GitHub Actions

El repositorio compila el juego solo cada vez que subís cambios. Entrá a la pestaña **Actions**,
abrí la última ejecución de *"Compilar juego (Windows)"* y descargá **FNAF_Industrial-windows** en
*Artifacts*: es un zip con el `.exe` y un `LEEME.txt`, listo para compartir.

Para una versión oficial: en GitHub, *Releases → Draft a new release → Choose a tag*, escribí `v1.1`
(o el número que toque) y publicala. GitHub compila el juego y adjunta el zip a esa Release solo.

## 2. Probar antes de publicar

Copiá `FNAF_Industrial.exe` a una carpeta vacía (por ejemplo, el escritorio) y comprobá:

- [ ] Abre la pantalla de carga y el menú, con el ícono del juego en la barra de tareas.
- [ ] Se escuchan los sonidos.
- [ ] Una noche completa funciona (usá el modo desarrollador `dunmore` + `F2` para ir rápido).
- [ ] Al cerrar y volver a abrir, se mantiene el progreso (aparecen `save_data.json` y `ajustes.json`
      junto al `.exe`).
- [ ] La pantalla completa (`F11`) y el cambio de idioma funcionan.
- [ ] **Desactivá el modo desarrollador** (si lo activaste, volvé a escribir `dunmore`; no queda guardado).

## 3. Armar el archivo para descargar

Si usaste GitHub Actions, el zip ya viene armado. Si compilaste en tu computadora, creá una carpeta
llamada `FNAF_Industrial_v1.0` con:

- `FNAF_Industrial.exe`
- `publicacion/LEEME.txt` (controles e instrucciones en español e inglés)

Comprimila en **`FNAF_Industrial_v1.0.zip`** (clic derecho → *Enviar a* → *Carpeta comprimida*).
**No** incluyas `save_data.json` ni `ajustes.json`: son tus partidas.

## 4. Subirlo a itch.io

1. Creá una cuenta en **itch.io** y entrá a *Dashboard → Create new project*.
2. Completá:
   - **Title:** FNAF: Industrial Sector (1982)
   - **Project URL:** por ejemplo `fnaf-industrial-sector`
   - **Short description:** la línea corta de `PAGINA_ITCH.md`
   - **Classification:** Games · **Kind of project:** Downloadable
   - **Pricing:** *No payments* (es un fan game: tiene que ser gratis)
3. En **Uploads**, subí `FNAF_Industrial_v1.0.zip` y marcá **Windows**.
4. **Details → Description:** pegá el texto de `PAGINA_ITCH.md` (español, inglés o los dos).
5. **Genre:** Survival / Horror. **Tags:** `fnaf`, `fan-game`, `horror`, `survival-horror`, `point-and-click`,
   `pixel-art`, `jumpscare`, `retro`, `singleplayer`.
6. **Cover image:** `publicacion/portada_630x500.png`.
7. **Screenshots:** las 6 imágenes de `publicacion/capturas/`.
8. En **Content disclosures / Age** indicá que tiene *jumpscares*, *terror* y *violencia leve*.
9. Guardá como **Draft**, revisá la página con *View page* y, cuando esté bien, pasala a **Public**.

## 5. (Opcional) GitHub Releases

1. Subí el código a tu repositorio (`alan4352/ProyectoFnaf`).
2. En GitHub: *Releases → Draft a new release*, etiqueta `v1.0`, título "FNAF: Industrial Sector v1.0".
3. Adjuntá `FNAF_Industrial_v1.0.zip` y pegá la descripción de `PAGINA_ITCH.md`.

---

## Avisos importantes

- **Antivirus / Windows SmartScreen:** los `.exe` hechos con PyInstaller a veces aparecen como
  "aplicación no reconocida" o dan **falsos positivos** en algunos antivirus, porque el archivo no está
  firmado. Es normal en juegos indie. Avisalo en la página: *"Si Windows muestra un aviso, elegí
  'Más información → Ejecutar de todas formas'"*.
  Si te da muchos problemas, podés compilar en modo carpeta (cambiá `--onefile` por `--onedir` en
  `compilar.bat` y subí la carpeta `dist\FNAF_Industrial` comprimida), que suele marcarse menos.
- **Fan game:** *Five Nights at Freddy's* es de Scott Cawthon. Los fan games son bienvenidos por la
  comunidad, pero **publicalo gratis** y aclará en la descripción que es un juego de fans no oficial
  y sin fines de lucro (ya está en el texto de `PAGINA_ITCH.md` y en los créditos).
- **Versiones nuevas:** cuando cambies algo, subí el número en `VERSION` (al principio de
  `fnaf_fabrica.py`; se ve abajo a la derecha en el menú), recompilá y subí el zip nuevo con ese número.
