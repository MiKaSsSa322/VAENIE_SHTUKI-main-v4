"""Синтез звуков оружия (numpy/scipy) -> WAV -> OGG Vorbis (ffmpeg). Всё оригинально, без сторонних семплов."""
import os, subprocess, tempfile
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 44100
OUT = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/frontiermilitary/sounds')
os.makedirs(OUT, exist_ok=True)

def t_(d): return np.arange(int(SR * d)) / SR
def bp(x, lo, hi, order=3):
    b, a = signal.butter(order, [lo / (SR / 2), hi / (SR / 2)], 'band'); return signal.lfilter(b, a, x)
def lp(x, f, order=3):
    b, a = signal.butter(order, f / (SR / 2), 'low'); return signal.lfilter(b, a, x)
def hp(x, f, order=3):
    b, a = signal.butter(order, f / (SR / 2), 'high'); return signal.lfilter(b, a, x)
def env(t, attack, tau):
    e = np.exp(-t / tau); a = np.clip(t / max(attack, 1e-5), 0, 1); return e * a
def mixs(*xs):
    n = max(len(x) for x in xs); out = np.zeros(n)
    for x in xs: out[:len(x)] += x
    return out
def place(buf, x, at):
    i = int(at * SR); n = min(len(x), len(buf) - i)
    if n > 0: buf[i:i + n] += x[:n]
def damped_sine(f, d, tau, amp=1.0, phase=0):
    t = t_(d); return amp * np.sin(2 * np.pi * f * t + phase) * np.exp(-t / tau)
def finish(x, peak=0.9):
    x = x / (np.max(np.abs(x)) + 1e-9); x = np.tanh(x * 1.6) / np.tanh(1.6); return x * peak

def gunshot(seed, tail=0.9, body_f=620, thump=(110, 48)):
    rng = np.random.default_rng(seed); d = tail
    t = t_(d); n = len(t); buf = np.zeros(n)
    noise = rng.standard_normal(n)
    crack = hp(noise, 1400) * env(t, 0.0004, 0.0035) * 1.5                  # резкий фронт
    snap = bp(noise, 2500, 9000) * env(t, 0.0002, 0.0018) * 1.1
    body = lp(rng.standard_normal(n), body_f) * env(t, 0.001, 0.045) * 2.2   # «хлопок»
    f = np.linspace(thump[0], thump[1], n); ph = 2 * np.pi * np.cumsum(f) / SR
    thumpw = np.sin(ph) * env(t, 0.002, 0.07) * 1.6                          # низкий удар
    buf += crack + snap + body + thumpw
    # эхо/реверб: несколько ранних отражений + диффузный хвост
    tailn = bp(rng.standard_normal(n), 180, 4200) * env(t, 0.02, 0.22) * 0.38
    buf += np.roll(tailn, 0)
    for dly, g in ((0.017, .30), (0.031, .22), (0.052, .16), (0.083, .11)):
        sh = np.zeros(n); k = int(dly * SR); sh[k:] = (crack + body * .6)[:n - k]; buf += lp(sh, 3500) * g
    # лёгкая ресэмплинг-вариация тембра
    return finish(buf, 0.95)

def dry_click():
    d = 0.18; buf = np.zeros(int(SR * d)); rng = np.random.default_rng(5)
    place(buf, mixs(damped_sine(2300, .05, .006, 1.0), damped_sine(3900, .05, .004, .6), bp(rng.standard_normal(int(.05 * SR)), 1500, 8000) * env(t_(.05), .0002, .004) * .8), 0.0)
    place(buf, mixs(damped_sine(1700, .05, .008, .5), damped_sine(2900, .05, .005, .4)), 0.045)
    return finish(buf, 0.6)

def mag_out():
    d = 0.42; buf = np.zeros(int(SR * d)); rng = np.random.default_rng(8)
    place(buf, mixs(damped_sine(3100, .04, .004, 1.0), damped_sine(1900, .05, .007, .7)), 0.0)  # кнопка
    sl = bp(rng.standard_normal(int(.16 * SR)), 900, 3800) * np.hanning(int(.16 * SR)) * 0.55          # скольжение
    place(buf, sl, 0.04)
    place(buf, mixs(damped_sine(380, .12, .03, .9), lp(rng.standard_normal(int(.12 * SR)), 900) * env(t_(.12), .001, .02) * .8), 0.19)  # выпал
    return finish(buf, 0.7)

def mag_in():
    d = 0.5; buf = np.zeros(int(SR * d)); rng = np.random.default_rng(9)
    sl = bp(rng.standard_normal(int(.2 * SR)), 800, 3600) * np.hanning(int(.2 * SR)) * 0.5
    place(buf, sl, 0.0)
    place(buf, mixs(damped_sine(2600, .06, .006, 1.0), damped_sine(1500, .08, .012, .9), lp(rng.standard_normal(int(.08 * SR)), 2500) * env(t_(.08), .0005, .012)), 0.2)  # защёлка
    place(buf, damped_sine(260, .15, .04, .8), 0.2)
    return finish(buf, 0.75)

def slide_back():
    d = 0.3; buf = np.zeros(int(SR * d)); rng = np.random.default_rng(12)
    n = int(.17 * SR); tt = t_(.17)
    scr = bp(rng.standard_normal(n), 1200, 6500) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 95 * tt))) * np.hanning(n) * 0.7   # трещотка
    place(buf, scr, 0.0)
    place(buf, mixs(damped_sine(2100, .06, .007, .8), damped_sine(3300, .05, .004, .5)), 0.17)
    return finish(buf, 0.65)

def slide_forward():
    d = 0.3; buf = np.zeros(int(SR * d)); rng = np.random.default_rng(14)
    n = int(.06 * SR); place(buf, bp(rng.standard_normal(n), 1500, 5500) * np.hanning(n) * .5, 0.0)    # пружина
    place(buf, mixs(damped_sine(1800, .1, .012, 1.0), damped_sine(2900, .08, .006, .7), damped_sine(240, .14, .05, 1.1),
                    hp(rng.standard_normal(int(.06 * SR)), 1800) * env(t_(.06), .0002, .006) * .9), 0.06)  # удар затвора
    return finish(buf, 0.8)

def medkit_rip():
    d = 0.45; n = int(d * SR); rng = np.random.default_rng(31); t = t_(d)
    mod = (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * 140 * t * (1 + 0.6 * t / d)))) * (0.6 + 0.4 * rng.random(n))   # липучка
    x = bp(rng.standard_normal(n), 1800, 9000) * mod * np.hanning(n) * 0.9
    x += lp(rng.standard_normal(n), 600) * env(t, .005, .08) * 0.25
    return finish(x, 0.7)

def medkit_done():
    buf = np.zeros(int(0.3 * SR)); rng = np.random.default_rng(32)
    place(buf, mixs(damped_sine(900, .08, .02, .7), damped_sine(1700, .06, .01, .5), bp(rng.standard_normal(int(.08 * SR)), 1500, 6000) * env(t_(.08), .0004, .01) * .6), 0.0)
    place(buf, mixs(damped_sine(520, .15, .05, .5)), 0.06)
    return finish(buf, 0.6)

def generator_pull():
    d = 0.5; n = int(d * SR); t = t_(d); rng = np.random.default_rng(33)
    f = np.linspace(60, 200, n); ph = 2 * np.pi * np.cumsum(f) / SR
    ratchet = bp(rng.standard_normal(n), 800, 4500) * (0.5 + 0.5 * np.sign(np.sin(ph * 0.5))) * np.hanning(n) * 0.8
    thud = damped_sine(120, .12, .03, 0.8)
    buf = ratchet; buf[:len(thud)] += thud * 0.0
    place(buf, thud, 0.38)
    return finish(buf, 0.75)

def generator_start():
    d = 1.6; n = int(d * SR); t = t_(d); rng = np.random.default_rng(34)
    rate = np.linspace(6, 30, n); ph = np.cumsum(rate) / SR                    # кашель двигателя -> ровный ход
    pulses = np.maximum(0, np.sin(2 * np.pi * ph)) ** 3
    f0 = np.linspace(38, 62, n); body = np.sin(2 * np.pi * np.cumsum(f0) / SR) + 0.5 * np.sin(4 * np.pi * np.cumsum(f0) / SR)
    x = lp(rng.standard_normal(n), 700) * pulses * 0.9 + body * pulses * 0.6 + hp(rng.standard_normal(n), 3000) * pulses * 0.12
    x *= np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.25)
    return finish(x, 0.85)

def generator_run():
    d = 1.2; n = int(d * SR); t = t_(d); rng = np.random.default_rng(35)
    x = np.zeros(n)
    for k, a in ((55, 1.0), (110, 0.6), (165, 0.35), (220, 0.22)):
        x += a * np.sin(2 * np.pi * k * t)
    x *= 0.6 + 0.4 * np.sin(2 * np.pi * 27 * t)                                # частота вспышек цилиндра
    x += lp(rng.standard_normal(n), 900) * 0.25 + hp(rng.standard_normal(n), 2500) * 0.03
    x *= np.minimum(1, t / 0.05) * np.minimum(1, (d - t) / 0.08)
    return finish(x, 0.55)

def shotgun_pump():
    buf = np.zeros(int(0.45 * SR)); rng = np.random.default_rng(41)
    n = int(.12 * SR); place(buf, bp(rng.standard_normal(n), 700, 3500) * np.hanning(n) * .6, 0.0)
    place(buf, mixs(damped_sine(210, .12, .03, 1.0), damped_sine(1400, .08, .008, .7), hp(rng.standard_normal(int(.06 * SR)), 1500) * env(t_(.06), .0003, .008) * .8), 0.1)
    place(buf, mixs(damped_sine(300, .1, .02, .9), damped_sine(1900, .07, .006, .7)), 0.27)
    return finish(buf, 0.8)

def shell_in():
    buf = np.zeros(int(0.25 * SR)); rng = np.random.default_rng(42)
    place(buf, mixs(damped_sine(1100, .06, .01, .8), damped_sine(2600, .05, .005, .6), lp(rng.standard_normal(int(.05 * SR)), 3000) * env(t_(.05), .0004, .01) * .6), 0.0)
    place(buf, mixs(damped_sine(700, .1, .02, .6)), 0.07)
    return finish(buf, 0.65)

def save(name, x):
    wav = tempfile.mktemp(suffix='.wav')
    wavfile.write(wav, SR, (x * 32767).astype(np.int16))
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', wav, '-ac', '1', '-c:a', 'libvorbis', '-q:a', '5',
                    os.path.join(OUT, name + '.ogg')], check=True)
    os.remove(wav)
    print(f'{name}.ogg  {len(x)/SR:.2f}s  peak={np.max(np.abs(x)):.2f}  rms={np.sqrt(np.mean(x**2)):.3f}')

if __name__ == '__main__':
    for i, (seed, bf, th) in enumerate(((1, 620, (110, 48)), (2, 700, (120, 52)), (3, 560, (100, 44))), 1):
        save(f'pistol_shot_{i}', gunshot(seed, 0.9, bf, th))
    for i, (seed, bf, th) in enumerate(((11, 480, (85, 38)), (12, 520, (90, 40)), (13, 450, (80, 36))), 1):
        save(f'rifle_shot_{i}', gunshot(seed, 1.3, bf, th))
    save('medkit_rip', medkit_rip()); save('medkit_done', medkit_done()); save('generator_pull', generator_pull())
    save('generator_start', generator_start()); save('generator_run', generator_run())
    for i, (seed, bf, th) in enumerate(((21, 380, (70, 32)), (22, 410, (74, 34))), 1):
        save(f'sniper_shot_{i}', gunshot(seed, 2.0, bf, th))
    for i, (seed, bf, th) in enumerate(((23, 300, (60, 30)), (24, 330, (64, 32))), 1):
        save(f'shotgun_shot_{i}', gunshot(seed, 1.1, bf, th))
    save('shotgun_pump', shotgun_pump()); save('shell_in', shell_in())
    save('pistol_dry', dry_click()); save('mag_out', mag_out()); save('mag_in', mag_in())
    save('slide_back', slide_back()); save('slide_forward', slide_forward())
