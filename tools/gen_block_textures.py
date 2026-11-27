import os, sys, random
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/frontiermilitary/textures/block')
PREV = '/home/claude/preview'
os.makedirs(ROOT, exist_ok=True); os.makedirs(PREV, exist_ok=True)

def vnoise(w, h, rng, cell=4):
    """Сглаженный value-noise 0..1, бесшовный по периоду w/h."""
    gw, gh = max(1, w // cell), max(1, h // cell)
    g = rng.random((gh, gw))
    out = np.zeros((h, w))
    for y in range(h):
        for x in range(w):
            fx, fy = x / cell, y / cell
            x0, y0 = int(fx) % gw, int(fy) % gh
            x1, y1 = (x0 + 1) % gw, (y0 + 1) % gh
            tx, ty = fx - int(fx), fy - int(fy)
            tx, ty = tx * tx * (3 - 2 * tx), ty * ty * (3 - 2 * ty)
            out[y, x] = (g[y0, x0] * (1 - tx) + g[y0, x1] * tx) * (1 - ty) + (g[y1, x0] * (1 - tx) + g[y1, x1] * tx) * ty
    return out

# ---------------------------------------------------------------- бетон
def concrete():
    rng = np.random.default_rng(11); r = random.Random(11)
    cv = Canvas(16, 16)
    base = (132, 132, 127)
    n1 = vnoise(16, 16, rng, 4); n2 = vnoise(16, 16, rng, 2)
    for y in range(16):
        for x in range(16):
            d = (n1[y, x] - .5) * 14 + (n2[y, x] - .5) * 8 + r.uniform(-3, 3)
            # загрязнение к низу (v растёт вниз)
            d -= max(0, y - 10) * 1.6
            cv.set(x, y, shade(base, d))
    # заполнитель: тёмные и светлые крупинки, поры
    for _ in range(11): cv.set(r.randrange(16), r.randrange(16), (104, 104, 100))
    for _ in range(9):  cv.set(r.randrange(16), r.randrange(16), (156, 155, 148))
    for _ in range(7):  cv.set(r.randrange(16), r.randrange(16), (88, 88, 86))
    # разметка: выцветшая жёлтая полоса (строки 2-3 -> высота 12..14)
    for y in (2, 3):
        for x in range(16):
            c = (176, 152, 64) if y == 2 else (160, 138, 58)
            wear = r.random()
            if wear < .22: c = mix(c, (132, 132, 127), .6)   # облупилась
            cv.set(x, y, shade(c, r.uniform(-6, 6)))
    # тонкая трещина
    x, y = 11, 6
    for _ in range(8):
        cv.set(x, y, (92, 92, 90)); y += 1; x += r.choice([-1, 0, 0, -1])
    # потёки под полосой
    for x in (3, 9, 13):
        for y in range(4, 4 + r.randint(2, 4)):
            c = cv.get(x, y); cv.set(x, y, shade(c[:3], -9))
    # фаска: верхний ряд светлее
    for x in range(16):
        c = cv.get(x, 0); cv.set(x, 0, shade(c[:3], 8))
    return cv

# ---------------------------------------------------------------- сталь решётки
def bars():
    rng = np.random.default_rng(23); r = random.Random(23)
    cv = Canvas(16, 16)
    base = (58, 64, 68)
    n = vnoise(16, 16, rng, 4)
    for y in range(16):
        for x in range(16):
            d = (n[y, x] - .5) * 10 + r.uniform(-2.5, 2.5)
            # блик по столбцам (цилиндрический): x=1..2 светлее, x=15,0 темнее
            prof = {0: -16, 1: 22, 2: 12, 3: 4, 4: 0, 5: -3, 6: -5, 7: -8,
                    8: -8, 9: -5, 10: -3, 11: 0, 12: 4, 13: 12, 14: 22, 15: -16}[x]
            cv.set(x, y, shade(base, d + prof * .8))
    # ржавчина понизу и сколы краски
    for _ in range(22):
        x, y = r.randrange(16), r.randint(8, 15)
        cv.set(x, y, mix(cv.get(x, y)[:3], (124, 74, 44), .75))
    for _ in range(8):
        cv.set(r.randrange(16), r.randrange(16), (118, 126, 130))  # сколы до металла
    for y in range(0, 16, 5):    # сварные швы поперёк
        for x in range(16): cv.set(x, y, shade(cv.get(x, y)[:3], -10))
    return cv

# ---------------------------------------------------------------- оцинковка (стойки)
def fence_post():
    rng = np.random.default_rng(37); r = random.Random(37)
    cv = Canvas(16, 16)
    base = (150, 157, 160)
    n = vnoise(16, 16, rng, 2)
    for y in range(16):
        for x in range(16):
            d = (n[y, x] - .5) * 16 + r.uniform(-3, 3)         # «спангл» оцинковки
            prof = {0: -26, 1: -10, 2: 8, 3: 22, 4: 26, 5: 14, 6: 0, 7: -12}[x % 8]
            cv.set(x, y, shade(base, d + prof * .7))
    for _ in range(14):                                       # ржавые потёки
        x, y = r.randrange(16), r.randint(9, 15)
        cv.set(x, y, mix(cv.get(x, y)[:3], (140, 92, 58), .65))
    for y in (5, 11):                                         # хомуты/сварка
        for x in range(16): cv.set(x, y, shade(cv.get(x, y)[:3], -30))
    return cv

# ---------------------------------------------------------------- сетка-рабица + колючка
def mesh():
    cv = Canvas(16, 16)
    steel = (146, 154, 157); hi = (200, 207, 208); lo = (84, 90, 93)
    for y in range(11):               # строки 0..10 — сетка (период 8)
        for x in range(16):
            a = (x + y) % 8 == 0
            b = (x - y) % 8 == 0
            if a and b: cv.set(x, y, lo)       # узел
            elif a:     cv.set(x, y, hi)
            elif b:     cv.set(x, y, steel)
    # строки 11..15 — колючая проволока (две скрутки + шипы), для плоскости высотой 4..5
    w1, w2 = (96, 100, 102), (62, 66, 68)
    for x in range(16):
        cv.set(x, 12, w1 if x % 2 else w2)
        cv.set(x, 14, w2 if x % 2 else w1)
    for bx in (3, 11):                 # шипы-крестики между нитями
        cv.set(bx, 11, hi); cv.set(bx, 13, hi); cv.set(bx - 1, 12, steel); cv.set(bx + 1, 12, steel)
        cv.set(bx - 1, 13, steel); cv.set(bx + 1, 13, steel); cv.set(bx, 15, hi)
        cv.set(bx - 1, 11, steel); cv.set(bx + 1, 11, steel); cv.set(bx - 1, 15, steel); cv.set(bx + 1, 15, steel)
    return cv

# ---------------------------------------------------------------- фонарь поста
def lamp():
    r = random.Random(5)
    cv = Canvas(16, 16)
    od = (74, 82, 58)                    # оливковый металл
    for y in range(0, 4):                # строки 0-3: корпус/колпак
        for x in range(16):
            d = {0: 14, 1: 4, 2: -6, 3: -14}[y] + r.uniform(-3, 3)
            cv.set(x, y, shade(od, d))
    for x in range(16):                  # матовые швы
        if x % 8 == 0: cv.set(x, 1, shade(cv.get(x, 1)[:3], -18))
    # строки 4-11: стекло — левая половина (x0-7) тёплое свечение, правая (x8-15) тёмная клетка
    for y in range(4, 12):
        for x in range(8):
            cx, cy = 3.5, 7.5
            dist = ((x - cx) ** 2 / 14 + (y - cy) ** 2 / 20) ** .5
            t = max(0, 1 - dist)
            c = mix((190, 120, 40), (255, 236, 150), t ** 1.2)
            cv.set(x, y, shade(c, r.uniform(-4, 4)))
        for x in range(8, 16):
            cv.set(x, y, shade((46, 50, 42), {8: 10, 9: 0, 10: -6, 11: -8}.get(x % 8, 0) + r.uniform(-3, 3)))
    # строки 12-15: цепь (альфа) и тёмный металл
    link = (58, 62, 60); linkhi = (120, 126, 120)
    for y in range(12, 16):
        for x in range(0, 8):
            if (x in (2, 5) and True) or (y in (12, 15) and 2 <= x <= 5):
                cv.set(x, y, linkhi if y in (12, 13) else link)
        for x in range(8, 16):
            cv.set(x, y, shade((44, 48, 44), r.uniform(-4, 4)))
    return cv

if __name__ == '__main__':
    out = {'concrete_barrier': concrete(), 'security_bars': bars(), 'metal_fence': fence_post(),
           'metal_fence_mesh': mesh(), 'watch_post_lamp': lamp()}
    for name, cv in out.items():
        cv.save(os.path.join(ROOT, name + '.png')); cv.preview(f'{PREV}/tex_{name}.png', 16)
    print('block textures done')
