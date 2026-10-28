"""Genera el audio del juego (assets/audio/*.ogg) por síntesis.
Uso: python herramientas/sintetizar_audio.py assets/audio

Necesita numpy, scipy y ffmpeg instalados (no hacen falta para jugar, solo para regenerar el audio).
Cambiá los parámetros de cada función para modificar un sonido y volvé a ejecutarlo.
"""
import os, subprocess, sys, tempfile
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
RNG = np.random.default_rng(1982)
SALIDA = sys.argv[1]
os.makedirs(SALIDA, exist_ok=True)


# ------------------------------------------------------------------ utilidades
def t_(seg):
    return np.arange(int(seg * SR)) / SR

def ruido(seg):
    return RNG.uniform(-1, 1, int(seg * SR))

def rosa(seg):
    b = ruido(seg)
    f = np.fft.rfft(b)
    frec = np.fft.rfftfreq(len(b), 1 / SR)
    frec[0] = 1
    f /= np.sqrt(frec)
    x = np.fft.irfft(f, len(b))
    return x / (np.abs(x).max() + 1e-9)

def marron(seg):
    x = np.cumsum(ruido(seg))
    x = signal.sosfilt(signal.butter(1, 20, "hp", fs=SR, output="sos"), x)
    return x / (np.abs(x).max() + 1e-9)

def filtro(x, tipo, f, orden=2):
    sos = signal.butter(orden, f, tipo, fs=SR, output="sos")
    return signal.sosfilt(sos, x)

def resonador(x, f, q=30):
    b, a = signal.iirpeak(f, q, fs=SR)
    return signal.lfilter(b, a, x)

def decae(seg, tau):
    return np.exp(-t_(seg) / tau)

def ataque(n, seg_ataque):
    e = np.ones(n)
    k = min(n, int(seg_ataque * SR))
    if k > 0:
        e[:k] = np.linspace(0, 1, k)
    return e

def fundido(x, ini=0.005, fin=0.02):
    x = x.copy()
    a, b = int(ini * SR), int(fin * SR)
    if a:
        x[:a] *= np.linspace(0, 1, a)
    if b:
        x[-b:] *= np.linspace(1, 0, b)
    return x

def mezclar(base, x, en_seg, ganancia=1.0):
    i = int(en_seg * SR)
    j = min(len(base), i + len(x))
    if j > i:
        base[i:j] += x[: j - i] * ganancia
    return base

def saw(f, seg, fase=0.0):
    t = t_(seg)
    return 2 * ((f * t + fase) % 1) - 1

def cuadrada(f, seg):
    return np.sign(np.sin(2 * np.pi * f * t_(seg)))

def seno(f, seg):
    return np.sin(2 * np.pi * f * t_(seg))

def seno_var(f_arr):
    return np.sin(2 * np.pi * np.cumsum(f_arr) / SR)

def metal(f0, seg, tau=0.4, parciales=(1.0, 2.76, 5.40, 8.93, 13.34), brillo=0.6):
    """Golpe metálico: parciales no armónicos con decaimiento."""
    x = np.zeros(int(seg * SR))
    for k, r in enumerate(parciales):
        x += (brillo ** k) * np.sin(2 * np.pi * f0 * r * t_(seg) + RNG.uniform(0, 6)) * decae(seg, tau / (1 + 0.6 * k))
    return x

def campana(f0, seg, tau=1.6):
    return metal(f0, seg, tau, parciales=(0.5, 1.0, 1.19, 1.56, 2.0, 2.51, 3.01), brillo=0.7)

def reverb(x, seg=1.8, mezcla=0.3, brillo=4000, estereo=True):
    n = int(seg * SR)
    def ir():
        r = ruido(seg) * np.exp(-t_(seg) * 6.0 / seg)
        r = filtro(r, "lowpass", brillo)
        return r / np.sqrt(np.sum(r ** 2))
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    salida = np.zeros((len(x) + n - 1, 2))
    for c in range(2):
        mojado = signal.fftconvolve(x[:, c], ir() if estereo or c == 0 else ir())
        salida[:, c] = mojado * mezcla
        salida[: len(x), c] += x[:, c] * (1 - mezcla * 0.5)
    return salida

def panear(x, p):
    """p = -1 izquierda ... 1 derecha"""
    a = (p + 1) * np.pi / 4
    return np.stack([x * np.cos(a), x * np.sin(a)], 1)

def saturar(x, k=3.0):
    return np.tanh(k * x) / np.tanh(k)

def bitcrush(x, bits=6, paso=4):
    y = np.repeat(x[::paso], paso)[: len(x)]
    q = 2 ** (bits - 1)
    return np.round(y * q) / q

def normalizar(x, pico_db=-1.0):
    m = np.abs(x).max()
    return x / m * (10 ** (pico_db / 20)) if m > 0 else x

def lazo(x, cruce=2.0):
    """Hace un bucle sin cortes: funde el final con el principio."""
    n = int(cruce * SR)
    cuerpo = x[: len(x) - n].copy()
    rampa = np.linspace(0, 1, n)
    if x.ndim == 2:
        rampa = rampa[:, None]
    cuerpo[:n] = cuerpo[:n] * rampa + x[len(x) - n:] * (1 - rampa)
    return cuerpo

def guardar(nombre, x, pico_db=-1.0, calidad=6):
    x = normalizar(x, pico_db)
    x = np.clip(x, -1, 1)
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wavfile.write(tmp.name, SR, (x * 32767).astype(np.int16))
    destino = os.path.join(SALIDA, nombre + ".ogg")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp.name, "-c:a", "libvorbis", "-q:a", str(calidad), destino], check=True)
    os.unlink(tmp.name)
    print(f"{nombre:20s} {len(x)/SR:5.1f} s  {os.path.getsize(destino)//1024:4d} KB")


# ------------------------------------------------------------------ elementos
def crujido(seg=1.4, f_res=(320, 780, 1500)):
    """Metal que cruje: pulsos de 'pegar y soltar' que pasan por resonancias."""
    x = np.zeros(int(seg * SR))
    tiempo = 0.0
    tasa = RNG.uniform(25, 45)
    while tiempo < seg:
        i = int(tiempo * SR)
        if i < len(x):
            x[i] = RNG.uniform(0.5, 1.0)
        tasa *= RNG.uniform(0.97, 1.05)
        tiempo += 1.0 / max(8, tasa)
    y = sum(resonador(x, f * RNG.uniform(0.9, 1.1), q=25) for f in f_res)
    env = np.sin(np.linspace(0, np.pi, len(y))) ** 0.7
    return y * env

def gota(f=None):
    f = f or RNG.uniform(900, 1600)
    seg = 0.25
    barrido = f * (1 + 0.6 * np.exp(-t_(seg) * 40))
    return seno_var(barrido) * decae(seg, 0.03)

def golpe_lejano(f0=70):
    x = metal(f0, 1.5, tau=0.5, brillo=0.5) + filtro(ruido(1.5), "lowpass", 400) * decae(1.5, 0.05)
    return filtro(x, "lowpass", 1800)

def nota_caja(f, seg=1.4):
    """Púa de caja de música."""
    x = (np.sin(2 * np.pi * f * t_(seg)) + 0.35 * np.sin(2 * np.pi * f * 3.0 * t_(seg)) * decae(seg, 0.12)
         + 0.15 * np.sin(2 * np.pi * f * 5.2 * t_(seg)) * decae(seg, 0.05))
    return x * decae(seg, 0.45) * ataque(int(seg * SR), 0.002)

NOTAS = {n: 440 * 2 ** ((i - 9) / 12) for i, n in enumerate(["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"])}
def nota(n, octava):
    return NOTAS[n] * 2 ** (octava - 4)


# ------------------------------------------------------------------ AMBIENTE Y MÚSICA
def ambiente():
    seg = 47.0
    t = t_(seg)
    lfo = 0.75 + 0.25 * np.sin(2 * np.pi * 0.04 * t)
    dron = (saw(55, seg) + saw(55.35, seg, 0.3) + 0.6 * saw(82.4, seg, 0.6))
    dron = filtro(dron, "lowpass", 260, 4) * lfo * 0.35
    cuarto = filtro(marron(seg), "lowpass", 180) * 0.5
    zumbido = (np.sin(2 * np.pi * 120 * t) + 0.5 * np.sin(2 * np.pi * 240 * t) + 0.3 * np.sin(2 * np.pi * 360 * t))
    zumbido = saturar(zumbido * 0.6, 2) * 0.05 * (0.8 + 0.2 * np.sin(2 * np.pi * 0.31 * t))
    base = dron + cuarto + zumbido
    eventos = np.zeros(len(t))
    for _ in range(6):
        eventos = mezclar(eventos, crujido(RNG.uniform(0.8, 1.8)), RNG.uniform(3, 41), RNG.uniform(0.25, 0.45))
    for _ in range(11):
        eventos = mezclar(eventos, gota(), RNG.uniform(2.5, 43), RNG.uniform(0.12, 0.25))
    for _ in range(3):
        eventos = mezclar(eventos, golpe_lejano(RNG.uniform(55, 90)), RNG.uniform(4, 40), 0.35)
    estereo = panear(base, 0) * 1.4 + reverb(panear(eventos, RNG.uniform(-0.6, 0.6)), 2.5, 0.55, 3000)[: len(t)]
    return lazo(estereo, 2.0)

def musica_menu():
    seg_acorde = 16.0
    acordes = [[("A", 2), ("C", 3), ("E", 3)], [("F", 2), ("A", 2), ("C", 3)],
               [("D", 2), ("F", 2), ("A", 2)], [("E", 2), ("G#", 2), ("B", 2)]]
    total = seg_acorde * 4 + 4
    pad = np.zeros(int(total * SR))
    for k, ac in enumerate(acordes):
        voz = np.zeros(int((seg_acorde + 4) * SR))
        for n, o in ac:
            f = nota(n, o)
            for d in (-0.15, 0.0, 0.17):
                voz += np.sin(2 * np.pi * (f + d) * t_(seg_acorde + 4))
            voz += 0.25 * filtro(saw(f, seg_acorde + 4, RNG.uniform()), "lowpass", 700)
        env = np.ones(len(voz))
        a = int(3.5 * SR)
        env[:a] = np.linspace(0, 1, a)
        env[-a:] = np.linspace(1, 0, a)
        pad = mezclar(pad, voz * env, k * seg_acorde, 0.08)
    # Melodía de caja de música (original), dispersa
    melodia = [("E", 5), ("A", 4), ("C", 5), ("B", 4), None, ("A", 4), ("E", 5), ("F", 5), ("E", 5), None, None,
               ("D", 5), ("F", 4), ("A", 4), ("G#", 4), None, ("A", 4), ("C", 5), ("B", 4), ("A", 4), None, None,
               ("B", 4), ("G#", 4), ("E", 4), ("F", 4), None, ("E", 4), None, None, None, None]
    caja = np.zeros(len(pad))
    paso = 64.0 / len(melodia)
    for i, n in enumerate(melodia):
        if n:
            f = nota(*n) * (1 + RNG.uniform(-0.004, 0.004))
            caja = mezclar(caja, nota_caja(f, 2.0), i * paso + RNG.uniform(0, 0.08), 0.22)
    siseo = filtro(rosa(total), "highpass", 2000) * 0.012
    mezcla = reverb(panear(pad, 0), 3.5, 0.45, 2500)[: len(pad)] + reverb(panear(caja, 0.15), 3.0, 0.6, 5000)[: len(pad)]
    mezcla += panear(siseo, 0)
    return lazo(mezcla, 4.0)

def caja_musica():
    """Para el apagón: melodía de caja de música que se va frenando."""
    mel = [("A", 5), ("E", 5), ("A", 5), ("C", 6), ("B", 5), ("A", 5), ("G#", 5), ("E", 5),
           ("F", 5), ("E", 5), ("D", 5), ("C", 5), ("B", 4), ("C", 5), ("B", 4), ("A", 4),
           ("A", 5), ("E", 5), ("A", 5), ("C", 6), ("B", 5), ("G#", 5), ("E", 5), ("A", 4)]
    total = 11.5
    x = np.zeros(int(total * SR))
    tiempo = 0.2
    paso = 0.36
    for i, n in enumerate(mel):
        desafinar = 1 - 0.012 * (i / len(mel)) ** 2
        x = mezclar(x, nota_caja(nota(*n) * desafinar, 1.6), tiempo, 0.5)
        tiempo += paso
        paso *= 1.035          # ritardando: el mecanismo se queda sin cuerda
        if tiempo > total - 1.5:
            break
    return reverb(panear(x, 0), 2.2, 0.45, 6000)[: len(x)]


# ------------------------------------------------------------------ GRITOS (jumpscares)
def grito(f0, aspereza=1.0, extra=None, seg=2.3):
    n = int(seg * SR)
    t = t_(seg)
    glide = f0 * (1.6 * np.exp(-t * 6) + 1.0 - 0.25 * t / seg)
    vibr = 1 + 0.03 * np.sin(2 * np.pi * 7 * t) + 0.01 * RNG.standard_normal(n).cumsum() / np.sqrt(n)
    f = glide * vibr
    voz = sum((0.8 ** k) * (2 * ((np.cumsum(f * (k + 1)) / SR) % 1) - 1) for k in range(3))
    formantes = resonador(voz, 800, 4) + resonador(voz, 1700, 5) * 0.8 + resonador(voz, 2900, 6) * 0.5
    chirrido = np.sin(2 * np.pi * 1900 * t + 9 * np.sin(2 * np.pi * 233 * t)) * 0.4 * decae(seg, 0.9)
    ruido_gr = filtro(ruido(seg), "bandpass", [300, 6000]) * 0.6
    x = (formantes * 0.6 + voz * 0.3 + chirrido * aspereza + ruido_gr) * ataque(n, 0.01)
    env = np.minimum(1, 4 * np.exp(-np.maximum(0, t - 1.4) * 3))
    x = saturar(x * 2.5, 2.5) * env
    if extra is not None:
        x = mezclar(x, extra, 0.0, 1.0)
    graves = seno_var(70 * (1.4 - 0.4 * t / seg)) * decae(seg, 0.6) * 0.8
    return fundido(x + graves, 0.002, 0.15)

def vidrio_roto(seg=1.2):
    x = np.zeros(int(seg * SR))
    for _ in range(45):
        f = RNG.uniform(2500, 7500)
        x = mezclar(x, metal(f, 0.25, 0.04, brillo=0.4), RNG.exponential(0.12), RNG.uniform(0.1, 0.4))
    x += filtro(ruido(seg), "highpass", 3000) * decae(seg, 0.08) * 1.2
    return x


# ------------------------------------------------------------------ EFECTOS
def puerta():
    seg = 0.9
    hidraulica = filtro(ruido(0.3), "bandpass", [1500, 6000]) * np.linspace(0.2, 1, int(0.3 * SR)) * 0.4
    golpe = np.zeros(int(seg * SR))
    golpe = mezclar(golpe, seno_var(70 * (1 + np.exp(-t_(0.5) * 30))) * decae(0.5, 0.12) * 1.5, 0.22)
    golpe = mezclar(golpe, metal(132, 0.68, 0.25), 0.22, 0.7)
    golpe = mezclar(golpe, filtro(ruido(0.08), "lowpass", 2500) * decae(0.08, 0.015), 0.22, 1.2)
    x = mezclar(golpe, hidraulica, 0.0, 1.0)
    return reverb(x, 0.6, 0.25, 3500)[:, 0][: int(seg * SR)]

def persiana():
    seg = 0.85
    x = np.zeros(int(seg * SR))
    tiempo, intervalo = 0.0, 0.03
    while tiempo < 0.7:
        clic = filtro(ruido(0.015), "bandpass", [1800, 5000]) * decae(0.015, 0.003)
        x = mezclar(x, clic, tiempo, RNG.uniform(0.5, 1.0))
        x = mezclar(x, metal(RNG.uniform(380, 460), 0.08, 0.03, brillo=0.5), tiempo, 0.3)
        tiempo += intervalo
        intervalo *= 1.06
    x = mezclar(x, metal(95, 0.3, 0.1) + seno(55, 0.3) * decae(0.3, 0.08), 0.72, 0.8)
    return x

def linterna():
    x = np.zeros(int(0.12 * SR))
    for i, tt in enumerate((0.0, 0.045)):
        clic = filtro(ruido(0.012), "bandpass", [2500, 7000]) * decae(0.012, 0.002)
        x = mezclar(x, clic + metal(1800 + 400 * i, 0.012, 0.004) * 0.3, tt)
    return x

def monitor_movimiento():
    seg = 0.4
    barrido = np.zeros(int(seg * SR))
    r = ruido(seg)
    for k, fc in enumerate(np.linspace(400, 2500, 8)):
        i0 = int(k * len(r) / 8)
        i1 = int((k + 1) * len(r) / 8)
        barrido[i0:i1] = filtro(r, "bandpass", [fc * 0.7, fc * 1.3])[i0:i1]
    barrido *= np.sin(np.linspace(0, np.pi, len(barrido)))
    clac = filtro(ruido(0.03), "bandpass", [800, 3000]) * decae(0.03, 0.006)
    return mezclar(barrido * 0.5, clac, 0.32, 1.0)

def estatica():
    seg = 0.25
    x = filtro(ruido(seg), "bandpass", [900, 6000]) * 0.5
    for _ in range(25):
        x = mezclar(x, ruido(0.004) * RNG.uniform(0.5, 1.5), RNG.uniform(0, seg - 0.01))
    return fundido(x, 0.003, 0.03)

def alarma():
    x = np.zeros(int(0.62 * SR))
    for i, f in enumerate((880, 660, 880, 660)):
        tono = filtro(cuadrada(f, 0.13), "lowpass", 3500) * ataque(int(0.13 * SR), 0.004)
        x = mezclar(x, fundido(tono, 0.003, 0.01), i * 0.15, 0.5)
    return x

def relay():
    x = np.zeros(int(0.09 * SR))
    for tt in (0.0, 0.018):
        x = mezclar(x, filtro(ruido(0.006), "highpass", 2000) * decae(0.006, 0.0015), tt)
    return mezclar(x, metal(1200, 0.06, 0.012, brillo=0.3) * 0.4, 0.0)

def apagon():
    seg = 1.8
    t = t_(seg)
    f = 120 * np.maximum(0.2, 1 - t / 1.4) ** 1.5
    hum = seno_var(f) + 0.5 * seno_var(2 * f) + 0.3 * seno_var(3 * f)
    hum *= np.maximum(0, 1 - t / 1.5)
    clunk = metal(60, seg, 0.3) * 1.2 + seno_var(45 * (1 + np.exp(-t * 20))) * decae(seg, 0.2) * 1.5
    return reverb(hum * 0.6 + clunk, 1.2, 0.3, 2500)[:, 0][: len(t)]

def ratchet():
    x = np.zeros(int(0.18 * SR))
    for i in range(3):
        x = mezclar(x, filtro(ruido(0.01), "bandpass", [1500, 4500]) * decae(0.01, 0.002), i * 0.035)
    x = mezclar(x, metal(620, 0.1, 0.05) * 0.25, 0.08)
    return x

def senuelo():
    seg = 0.9
    x = np.zeros(int(seg * SR))
    for i, n in enumerate([("C", 5), ("E", 5), ("G", 5), ("E", 5), ("C", 6), ("G", 5)]):
        tono = filtro(cuadrada(nota(*n), 0.13) * decae(0.13, 0.07), "lowpass", 2500)
        x = mezclar(x, tono, i * 0.13, 0.5)
    x = bitcrush(x * (1 + 0.3 * np.sin(2 * np.pi * 5 * t_(seg))), 5, 3)
    return filtro(x, "bandpass", [300, 3000])

def ir_hum():
    seg = 0.4
    x = 0.25 * seno(3100, seg) + 0.6 * seno(60, seg) + 0.3 * seno(120, seg)
    return fundido(x, 0.03, 0.03)

def ir_lock():
    x = np.zeros(int(0.22 * SR))
    for i, f in enumerate((1450, 1950)):
        x = mezclar(x, fundido(seno(f, 0.08), 0.003, 0.02), i * 0.1, 0.6)
    return x

def paso_metal():
    seg = 0.3
    golpe = seno_var(85 * (1 + np.exp(-t_(seg) * 40))) * decae(seg, 0.05)
    reja = metal(RNG.uniform(520, 600), seg, 0.08, brillo=0.65) * 0.35
    raspon = filtro(ruido(seg), "bandpass", [2000, 6000]) * decae(seg, 0.02) * 0.4
    return golpe + reja + raspon

def conducto():
    seg = 0.55
    exc = filtro(ruido(seg), "lowpass", 1500) * decae(seg, 0.04)
    hueco = sum(resonador(exc, f, 18) * (0.8 ** k) for k, f in enumerate((180, 360, 540, 760)))
    raspado = filtro(ruido(seg), "bandpass", [1200, 4000]) * np.sin(np.linspace(0, np.pi, int(seg * SR))) * 0.15
    return hueco + raspado

def timbre():
    seg = 0.7
    x = np.zeros(int(seg * SR))
    tiempo, i = 0.0, 0
    while tiempo < 0.55:
        f = 1180 if i % 2 == 0 else 1420
        x = mezclar(x, campana(f, 0.15, 0.08) * 0.5, tiempo)
        tiempo += 1 / 22
        i += 1
    return fundido(x, 0.002, 0.12)

def campanada(f):
    seg = 3.0
    x = campana(f, seg, 1.4)
    return reverb(x, 2.5, 0.35, 6000)[:, 0][: int(seg * SR)]

def paso_8bit():
    x = np.zeros(int(0.07 * SR))
    for i, f in enumerate((220, 180)):
        x = mezclar(x, cuadrada(f, 0.025) * 0.5, i * 0.03)
    return bitcrush(x, 4, 2)

def glitch_8bit():
    seg = 0.35
    x = np.zeros(int(seg * SR))
    tiempo = 0.0
    while tiempo < seg - 0.03:
        f = RNG.choice([110, 147, 220, 330, 466, 880, 1320])
        x = mezclar(x, cuadrada(f, 0.025) * 0.4, tiempo)
        tiempo += 0.025
    x += ruido(seg) * 0.25 * (RNG.uniform(size=int(seg * SR)) > 0.7)
    return bitcrush(x, 3, 6)

def respiracion():
    seg = 1.05
    r = ruido(seg)
    n = len(r)
    inh = filtro(r, "bandpass", [700, 2000]) * np.concatenate([np.sin(np.linspace(0, np.pi, int(n * 0.45))), np.zeros(n - int(n * 0.45))])
    exh = filtro(r, "bandpass", [300, 1100]) * np.concatenate([np.zeros(int(n * 0.5)), np.sin(np.linspace(0, np.pi, n - int(n * 0.5)))])
    servo = filtro(saw(92, seg), "lowpass", 400) * 0.08 * np.sin(np.linspace(0, np.pi, n))
    return inh * 0.8 + exh + servo

def golpes_techo():
    seg = 0.7
    x = np.zeros(int(seg * SR))
    for i in range(3):
        g = metal(RNG.uniform(115, 130), 0.3, 0.09, parciales=(1.0, 2.6, 4.8, 7.1), brillo=0.55)
        g += seno(60, 0.3) * decae(0.3, 0.05)
        x = mezclar(x, g, i * 0.18, RNG.uniform(0.8, 1.0))
    return reverb(x, 0.5, 0.25, 3000)[:, 0][: int(seg * SR)]

def golpe_vidrio():
    seg = 0.15
    return metal(2200, seg, 0.03, parciales=(1.0, 1.6, 2.3, 3.1), brillo=0.6) + filtro(ruido(seg), "highpass", 2500) * decae(seg, 0.005) * 0.5


# ------------------------------------------------------------------ exportar
if __name__ == "__main__":
    guardar("ambiente", ambiente(), -10, 4)
    guardar("musica_menu", musica_menu(), -6, 4)
    guardar("caja_musica", caja_musica(), -4)
    guardar("grito_barnaby", grito(150, 0.7), -0.5)
    guardar("grito_penny", grito(380, 1.3), -0.5)
    guardar("grito_bunny", grito(250, 1.0, extra=vidrio_roto() * 0.9), -0.5)
    silas_gr = grito(210, 1.6) * (0.75 + 0.25 * np.sign(np.sin(2 * np.pi * 28 * t_(2.3))))
    guardar("grito_silas", silas_gr, -0.5)
    guardar("jumpscare", grito(120, 0.5) + filtro(ruido(2.3), "lowpass", 900) * 0.4, -0.5)
    guardar("puerta", puerta(), -1.5)
    guardar("persiana", persiana(), -3)
    guardar("linterna", linterna(), -6)
    guardar("monitor_movimiento", monitor_movimiento(), -6)
    guardar("estatica_cctv", estatica(), -8)
    guardar("alarma_error", alarma(), -6)
    guardar("reboot_click", relay(), -6)
    guardar("apagon_down", apagon(), -1.5)
    guardar("bobina_cuerda", ratchet(), -8)
    guardar("lure_audio", senuelo(), -5)
    guardar("ir_hum", ir_hum(), -16)
    guardar("ir_lock", ir_lock(), -6)
    guardar("paso_metal", paso_metal(), -3)
    guardar("conducto_metal", conducto(), -3)
    guardar("timbre", timbre(), -4)
    guardar("campana_1", campanada(523.25), -3)
    guardar("campana_2", campanada(659.25), -3)
    guardar("campana_3", campanada(783.99), -3)
    guardar("paso_8bit", paso_8bit(), -10)
    guardar("glitch_8bit", glitch_8bit(), -6)
    guardar("respiracion", respiracion(), -2)
    guardar("golpe_techo", golpes_techo(), -2)
    guardar("golpe_vidrio", golpe_vidrio(), -6)
