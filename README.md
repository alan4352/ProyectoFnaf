# FNAF: Industrial Sector (1982)

Juego de terror al estilo *Five Nights at Freddy's*, hecho en Python con Pygame.
Tenés que sobrevivir 5 noches en una planta industrial abandonada, vigilando a cuatro animatrónicos
desde la oficina de seguridad.

## Historia

Octubre de 1982. La Ensambladora Dunmore cierra para siempre su planta del Sector B y te contratan como
guardia por cinco noches. Pero en marzo pasó algo que nadie quiere contar, y las unidades de
entretenimiento siguen buscando la salida a las 3 de la mañana.

Después de cada noche (1 a 4) se reproduce una **cinta de 1982**: un minijuego de 8 bits que muestra la
noche del accidente desde los ojos de uno de los operarios. En cada cinta hay una **prueba escondida**.
Con las cuatro pruebas, el final cambia. Las cintas se pueden repetir desde **ARCHIVO 1982** en el menú.

Todos los textos de la historia están en `historia.py` (llamadas, cintas, pruebas y finales) y su
traducción al inglés en `historia_en.py`.

## Contenido

- **5 noches** con llamadas que cuentan la historia, y una **noche 6 secreta** (se desbloquea con el final
  verdadero) con un enemigo nuevo: la **Unidad 0**, que solo se mueve cuando nadie la mira.
- **4 cintas de 1982** (minijuegos de 8 bits) con una prueba escondida cada una y **dos finales**.
- **Custom Night** con IA de 0 a 20 y **5 desafíos** con reglas especiales.
- **Modo infinito** (en la Custom Night): no hay 6 AM, cada hora son más rápidos y se guardan tus 5 mejores tiempos.
- **20 logros** (algunos secretos) y **estadísticas** de toda la partida, con un resumen y créditos al terminar.
- **Tutorial** guiado en la noche 1, **dificultad** Historia / Normal / Pesadilla e idioma **español / inglés**.
- **Subtítulos de sonidos** (opcional): muestran pasos, golpes y respiraciones, y de qué lado vienen.
- **Teclas configurables** y soporte para **mando** (joystick).
- **Versión web**: se puede jugar en el navegador (ver más abajo).
- Algunos **secretos** raros... (una pista: mira bien la pared de la oficina).

## Cómo jugar

```
pip install pygame-ce
python fnaf_fabrica.py
```

Se usa **pygame-ce** (la versión de pygame mantenida por la comunidad): el código es el mismo, pero tiene
versión lista para instalar en Python nuevos (3.14, 3.15), donde el `pygame` clásico no instala.

Para crear el `.exe`, hacé doble clic en `compilar.bat`: crea el entorno, instala lo necesario
(`requirements.txt`) y compila. El `.exe` queda en `dist\FNAF_Industrial.exe` (con el ícono del juego) y el
progreso se guarda en `save_data.json` y `ajustes.json`, junto al `.exe`.

**Compilación automática:** cada vez que subís cambios a GitHub, el juego se compila solo en Windows
(pestaña **Actions** del repositorio → la última ejecución → **Artifacts** → `FNAF_Industrial-windows`).
Si creás una etiqueta `v1.1`, `v1.2`, etc., además se publica una **Release** con el zip listo.

Para publicarlo (itch.io o GitHub), seguí `publicacion/PUBLICAR.md`; el texto para la página está en
`publicacion/PAGINA_ITCH.md` y las capturas en `publicacion/capturas/`.

## Controles

| Acción | Tecla / mouse |
|---|---|
| Abrir / cerrar monitor de cámaras | `ESPACIO`, `C` o clic en la barra de abajo |
| Puerta izquierda | `A` o botón PUERTA |
| Luces | Botones LUZ (izquierda y derecha) |
| Persiana derecha | Mantener apretado el botón PERSIANA |
| Linterna al pasillo | Mantener `F` o clic derecho |
| Mirar al techo / volver | `W` / `S` (o flechas) |
| Sellar la rejilla del techo | `ESPACIO` mirando al techo |
| Panel de mantenimiento | `M` o clic en la terminal MANT. |
| Visión nocturna IR (en cámaras) | `V` o clic derecho sobre la imagen |
| Compuerta de ducto | Clic derecho sobre un ducto en el mapa de ventilación |
| Señuelo de audio | Botón en el mapa de ventilación |
| Recargar la bobina (CAM_08, desde la noche 3) | Mantener el botón en CAM_08 |
| Pausa | `ESC` o `P` |
| Reintentar tras morir | `R` |
| Efecto CRT on/off | `F1` |
| Pantalla completa | `F11` |
| Ajustes (volumen, brillo, pantalla...) | Botón AJUSTES en el menú principal o en la pausa |

Las teclas de la oficina se pueden cambiar en **AJUSTES > CONTROLES / MANDO** (se guardan en `ajustes.json`).

### Mando

Se detecta solo al conectarlo. El stick izquierdo mueve un cursor (como el mouse) y en las cintas mueve al
personaje.

| Botón (Xbox) | Acción |
|---|---|
| A | Clic |
| B | Clic derecho (linterna, visión IR, compuerta de ducto) |
| X | Compuerta |
| Y | Cámaras |
| LB / RB | Mirar al techo / Panel de mantenimiento |
| BACK / START | Visión nocturna / Pausa |
| Cruceta | Flechas (techo, volver, moverse por los menús) |

## Animatrónicos

- **Barnaby**: viene por el pasillo (CAM_07). Encandilalo con la linterna antes de que llegue.
- **Penny**: llega a la puerta izquierda. Cerrala a tiempo (se escucha su respiración).
- **Rusty Bunny**: aparece en la ventana derecha. Mantené la persiana bajada unos segundos.
- **Silas**: se mueve por los ductos (dos rutas posibles). Usá la compuerta, el señuelo o sellá el techo
  (sellar consume oxígeno). Se lo escucha golpear la rejilla cuando está arriba.

A las 2, 3 y 4 AM se vuelven más agresivos.

**Unidad 0** (noche 6): recorre cuatro cámaras y avanza cuando pasa mucho tiempo sin que la mires.
Cuando llega al pasillo (CAM_07), mírala fijo unos segundos para que retroceda.

## Versión web (navegador)

La versión web se arma con [pygbag](https://pypi.org/project/pygbag/):

```
pip install pygbag
python herramientas/preparar_web.py --compilar
python -m pygbag build_web        # para probarla en http://localhost:8000
```

`preparar_web.py` copia el juego a `build_web/` y convierte el bucle principal para que funcione en el navegador
(el código de escritorio no se toca). En el navegador el progreso se guarda en el almacenamiento de la página, y
el efecto CRT arranca apagado porque baja mucho los FPS.

En GitHub, cada push arma la versión web (workflow **Version web**, zip `FNAF_Industrial-web`, listo para subir a
itch.io como juego HTML5). Desde `main` además se publica en GitHub Pages, si está activado en
*Settings > Pages > Source: GitHub Actions*.

## Archivos del proyecto

| Archivo | Qué tiene |
|---|---|
| `fnaf_fabrica.py` | Juego principal: estado de la partida, dibujo de pantallas y bucle principal |
| `historia.py` | **Toda la historia**: llamadas, introducción, cintas, pruebas y los dos finales |
| `minijuegos.py` | Las 4 cintas de 8 bits (los mapas son texto y se pueden editar) y las pantallas de relato |
| `datos.py` | Dificultad por noche, cámaras y rutas. **Para ajustar el balance** |
| `recursos.py` | Rutas de archivos y carga de imágenes y sonidos desde `assets/` |
| `audio.py` | Sonidos sintéticos de respaldo y carga de audio real |
| `guardado.py` | Guardado del progreso |
| `efectos.py` | Efecto de monitor CRT |
| `ventana.py` | Ventana, pantalla completa, escalado (ajustar/estirar), brillo y FPS |
| `historia_en.py` | La historia traducida al inglés |
| `idioma.py` | Traducción de la interfaz al inglés (diccionario de textos) |
| `progreso.py` | Estadísticas y logros |
| `unidad0.py` | El enemigo de la noche 6 |
| `controles.py` | Teclas configurables de la oficina |
| `mando.py` | Soporte para mando (joystick) |
| `herramientas/preparar_web.py` | Arma la versión web (pygbag) |
| `datos.py` | También: niveles de dificultad y desafíos de la Custom Night |

### Modo desarrollador

Escribí **`dunmore`** en el teclado (conviene hacerlo en el menú) para activarlo o desactivarlo.
Aparece un panel con información de la partida y estos atajos:

| Tecla | Acción |
|---|---|
| `F2` | Saltar a las 6 AM |
| `F3` | Recargar batería, oxígeno y bobina |
| `F4` | Desbloquear todas las noches (incluida la 6) y las cintas (solo esa sesión) |
| `F5` | Dar o quitar las 4 pruebas (solo esa sesión) |
| `F6` | Congelar a los animatrónicos |
| `F7` | Adelantar una hora |
| `F8` | Probar un jumpscare (va rotando entre los cinco) |
| `F9` | Ganar la cinta actual con su prueba |
| `F10` | Ocultar o mostrar el panel |

La palabra se cambia en `CODIGO_DESARROLLO`, al principio de `fnaf_fabrica.py`.
Con el modo desarrollador activo no se ganan logros (las estadísticas sí se cuentan).

## Ajustes

Desde el menú principal o la pausa: volumen general, efectos, música/ambiente y voces; brillo;
efecto CRT; pantalla completa; escalado de imagen; velocidad de giro; FPS; dificultad; idioma;
subtítulos de sonidos y controles (teclas y mando).
Se guardan solos en `ajustes.json`, junto al juego.

El juego se dibuja en 1200×700 (proporción 12:7). En monitores con otra proporción (5:4, 16:10, 16:9)
**Ajustar** deja bordes negros para no deformar la imagen, y **Estirar** llena toda la pantalla.

## Assets

El juego busca los archivos **por nombre** en cualquier subcarpeta de `assets/`, así que podés ordenarlos
como quieras. Las imágenes pueden ser `.png` o `.jpg` (para fondos conviene `.jpg`: pesan mucho menos).
Si falta un archivo, el juego usa un dibujo o sonido generado por código.

### Imágenes

| Archivo | Uso | Tamaño recomendado |
|---|---|---|
| `oficina_base` | Oficina (panorámica) | 1800 × 1005 |
| `oficina_puerta_abierta` | *Opcional:* oficina con la puerta izquierda abierta | 1800 × 1005 |
| `techo_rejilla` | Vista del techo | 1254 × 700 |
| `cam_01` … `cam_08` | Cámaras de la planta (`cam_03` no hace falta: es "sin video") | 720 × 538 |
| `vent_tunel` | Ductos de ventilación | 720 × 538 |
| `vent_01` … `vent_04` | *Opcional:* una imagen distinta por ducto | 720 × 538 |
| `vent_bloqueada` | *Opcional:* ducto con la compuerta cerrada | 720 × 538 |
| `jumpscare_barnaby`, `_silas`, `_penny`, `_bunny` | Jumpscares | 1380 × 1030 |
| `icono` | Ícono de la ventana (el `.exe` usa `icono.ico`, en la carpeta principal) | 256 × 256 |
| `periodico` | *Opcional:* periódico del final normal | 1200 × 700 |
| `periodico_verdadero` | *Opcional:* periódico del final verdadero | 1200 × 700 |
| `barnaby_cam`, `barnaby_oficina`, `silas_vent`, `silas_techo`, `penny_cam`, `penny_puerta`, `bunny_cam`, `bunny_ventana` | Sprites con fondo transparente (`.png`) | — |

Si cambiás `oficina_base`, revisá las medidas de la puerta y la ventana en `fnaf_fabrica.py`
(`RECT_PUERTA_IMG`, `VENT_X0`, `LINEA_BARRA_PERSIANA`, `LINEA_BASE_VIDRIO`, etc.).

### Animaciones

Cualquier sprite o jumpscare se puede animar agregando cuadros numerados:
`barnaby_cam_00.png`, `barnaby_cam_01.png`, `barnaby_cam_02.png`…
Se reproducen en bucle (8 cuadros por segundo los sprites, 14 los jumpscares).
Con 2 o 3 cuadros ya alcanza para un parpadeo o un tic.

### Audio (`.ogg`, `.wav` o `.mp3`, por ejemplo en `assets/audio/`)

El juego ya trae audio propio en `assets/audio/` (ambiente, música del menú, caja de música del apagón,
gritos, efectos), generado por síntesis con `herramientas/sintetizar_audio.py`. Para cambiar un sonido,
reemplazá el archivo por uno tuyo con el mismo nombre, o editá el script y volvé a generarlo
(necesita numpy, scipy y ffmpeg; no hacen falta para jugar).

| Archivo | Cuándo suena |
|---|---|
| `ambiente` | Bucle de fondo durante la noche |
| `musica_menu` | Bucle en el menú |
| `caja_musica` | Melodía durante el apagón |
| `grito_barnaby`, `grito_silas`, `grito_penny`, `grito_bunny` | Jumpscare de cada uno |
| `llamada_noche_1` … `llamada_noche_5` | Voz de la llamada de cada noche |
| `puerta`, `persiana`, `linterna`, `monitor_movimiento`, `estatica_cctv` | Acciones de la oficina |
| `paso_metal`, `conducto_metal`, `respiracion`, `golpe_techo`, `golpe_vidrio` | Movimientos y pistas de los animatrónicos |
| `alarma_error`, `reboot_click`, `apagon_down`, `bobina_cuerda`, `lure_audio`, `ir_hum`, `ir_lock`, `timbre` | Sistemas |
| `campana_1`, `campana_2`, `campana_3` | Campanadas de las 6 AM |
| `jumpscare`, `paso_8bit`, `glitch_8bit` | Respaldo de jumpscare y minijuegos |

Al arrancar, la consola muestra qué imágenes, animaciones y sonidos encontró.
