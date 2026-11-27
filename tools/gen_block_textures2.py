import os, sys, random, math
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from gen_block_textures import vnoise

ROOT = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/frontiermilitary/textures/block')
PREV = '/home/claude/preview'
os.makedirs(PREV, exist_ok=True)
OUT = {}

def noisy(cv, base, rng_seed, amp=8, cell=4, y0=0, y1=16, x0=0, x1=16):
    rng = np.random.default_rng(rng_seed); r = random.Random(rng_seed)
    n = vnoise(16, 16, rng, cell)
    for y in range(y0, y1):
        for x in range(x0, x1):
            cv.set(x, y, shade(base, (n[y, x] - .5) * amp * 2 + r.uniform(-amp / 3, amp / 3)))

# ---------------------------------------------------------------- мешки с песком
def sandbag():
    cv = Canvas(16, 16); r = random.Random(41)
    base = (176, 152, 104)
    for row in range(4):
        y0 = row * 4; off = 0 if row % 2 == 0 else 4
        for k in range(-1, 3):
            bx = off + k * 8
            for yy in range(4):
                for xx in range(8):
                    X = bx + xx; Y = y0 + yy
                    if not (0 <= X < 16): continue
                    c = shade(base, r.randint(-7, 7))
                    if yy == 0: c = shade(c, 16)                      # свет сверху
                    if yy == 3: c = shade(c, -22)                      # тень снизу
                    if xx in (0, 7): c = shade(c, -26)                 # швы-складки по краям
                    if (xx + yy) % 3 == 0 and yy in (1, 2): c = shade(c, -6)   # плетение мешковины
                    cv.set(X, Y, c)
            # завязка/шов посередине
            for yy in range(1, 3): 
                X = bx + 3 + (yy % 2)
                if 0 <= X < 16: cv.set(X, y0 + yy, shade(base, -34))
    return cv

# ---------------------------------------------------------------- хеско (габион)
def hesco():
    cv = Canvas(16, 16); r = random.Random(7)
    noisy(cv, (158, 138, 100), 7, 9, 2)
    for y in range(16):
        for x in range(16):
            if x % 5 == 0 or y % 5 == 0: cv.set(x, y, shade((62, 66, 68), r.randint(-6, 6)))   # проволочная сетка
            elif x % 5 == 1 or y % 5 == 1: cv.set(x, y, shade(cv.get(x, y)[:3], 12))
    for x in range(0, 16, 5):
        for y in range(0, 16, 5): cv.set(x, y, (104, 110, 112))       # узлы
    return cv

# ---------------------------------------------------------------- колючая проволока (кольца, cutout)
def razor():
    cv = Canvas(16, 16)
    steel = (150, 156, 160); dark = (70, 74, 78)
    for cx in (3.5, 8.5, 13.5):
        for a in range(0, 360, 6):
            x = cx + 3.3 * math.cos(math.radians(a)); y = 7.5 + 6.2 * math.sin(math.radians(a))
            cv.set(int(round(x)), int(round(y)), steel if a < 180 else dark)
    for x in range(16):
        cv.set(x, 1 if x % 2 else 2, dark); cv.set(x, 13 if x % 2 else 14, dark)
    for bx in (1, 6, 11, 15):
        cv.set(bx, 0, steel); cv.set(bx, 3, steel); cv.set(bx, 12, steel); cv.set(bx, 15, steel)
    return cv

# ---------------------------------------------------------------- ящик для боеприпасов
def ammo_crate_side():
    cv = Canvas(16, 16); r = random.Random(3)
    noisy(cv, (82, 92, 58), 3, 5, 2)
    for y in range(16):                                   # доски
        for x in range(16):
            if y in (5, 10): cv.set(x, y, shade(cv.get(x, y)[:3], -22))
    for yy in range(0, 16):                               # стальная окантовка
        for xx in (0, 1, 14, 15): cv.set(xx, yy, shade((52, 56, 50), r.randint(-4, 4) + (10 if xx in (0, 14) else 0)))
    for yy in (0, 15):
        for xx in range(16): cv.set(xx, yy, shade((52, 56, 50), r.randint(-4, 4)))
    for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)): cv.set(x, y, (140, 146, 140))     # заклёпки
    for xx in range(4, 12):                               # жёлтая трафаретная маркировка
        for yy in (6, 7, 8):
            if (xx + yy) % 2 == 0 or yy == 7: cv.set(xx, yy, (214, 182, 60))
    return cv

def ammo_crate_top():
    cv = Canvas(16, 16); r = random.Random(4)
    noisy(cv, (78, 88, 55), 4, 5, 2)
    for xx in range(16):
        for yy in (0, 1, 14, 15): cv.set(xx, yy, shade((52, 56, 50), r.randint(-4, 4)))
    for yy in range(16):
        for xx in (0, 1, 14, 15): cv.set(xx, yy, shade((52, 56, 50), r.randint(-4, 4)))
    for xx in range(5, 11): cv.set(xx, 7, (36, 38, 36)); cv.set(xx, 8, (110, 116, 110))   # ручка
    cv.set(4, 7, (36, 38, 36)); cv.set(11, 7, (36, 38, 36))
    for yy in (3, 12): cv.rect(6, yy, 9, yy + 1, (150, 150, 140))                           # замки
    return cv

# ---------------------------------------------------------------- ящик снабжения (дерево)
def supply_crate_side():
    cv = Canvas(16, 16); r = random.Random(5)
    for y in range(16):
        base = (160, 124, 76) if (y // 4) % 2 == 0 else (148, 114, 70)
        for x in range(16): cv.set(x, y, shade(base, r.randint(-6, 6) + (-14 if y % 4 == 3 else 0)))
    for y in range(16):                                    # каркас
        for x in (0, 1, 14, 15): cv.set(x, y, shade((106, 80, 48), r.randint(-4, 4)))
    for x in range(16):
        for y in (0, 1, 14, 15): cv.set(x, y, shade((106, 80, 48), r.randint(-4, 4)))
    for i in range(2, 14):                                 # диагональная связь
        cv.set(i, i, shade((96, 70, 40), 0)); cv.set(i, i + 1 if i + 1 < 14 else i, shade((96, 70, 40), 4))
    cv.rect(5, 6, 10, 9, (222, 218, 200)); cv.rect(7, 6, 8, 9, (190, 50, 40)); cv.rect(5, 7, 10, 8, (190, 50, 40))   # красный крест
    cv.rect(5, 6, 10, 9, (222, 218, 200)); cv.rect(7, 5, 8, 10, (190, 50, 40)); cv.rect(6, 7, 9, 8, (190, 50, 40))
    return cv
def supply_crate_top():
    cv = Canvas(16, 16); r = random.Random(6)
    for y in range(16):
        for x in range(16): cv.set(x, y, shade((156, 120, 74), r.randint(-6, 6) + (-14 if x % 4 == 3 else 0)))
    for y in range(16):
        for x in (0, 1, 14, 15): cv.set(x, y, shade((106, 80, 48), r.randint(-4, 4)))
    for x in range(16):
        for y in (0, 1, 14, 15): cv.set(x, y, shade((106, 80, 48), r.randint(-4, 4)))
    return cv

# ---------------------------------------------------------------- бочка
def drum_side():
    cv = Canvas(16, 16); r = random.Random(8)
    for y in range(16):
        for x in range(16):
            prof = {0: -18, 1: -4, 2: 10, 3: 18, 4: 16, 5: 8, 6: 0, 7: -8}[(x % 8)]
            cv.set(x, y, shade((84, 96, 62), prof + r.randint(-3, 3)))
    for y in (2, 7, 13):                                   # рёбра жёсткости
        for x in range(16): cv.set(x, y, shade(cv.get(x, y)[:3], -24)); cv.set(x, y + 1, shade(cv.get(x, y + 1)[:3], 16))
    for x in range(2, 14):                                 # белый трафарет «FUEL»-полоса
        cv.set(x, 5, (226, 222, 205)); cv.set(x, 4, (226, 222, 205)) if x % 3 else None
    for _ in range(10):
        x, y = r.randrange(16), r.randrange(16)
        cv.set(x, y, mix(cv.get(x, y)[:3], (130, 78, 46), .6))
    return cv
def drum_top():
    cv = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            d = math.hypot(x - 7.5, y - 7.5)
            c = (70, 80, 54) if d < 7.5 else (40, 46, 36)
            if 6.2 < d < 7.5: c = (100, 112, 80)
            cv.set(x, y, shade(c, ((x * 7 + y * 3) % 5) - 2))
    cv.rect(9, 9, 11, 11, (30, 32, 30)); cv.rect(10, 10, 10, 10, (120, 124, 120))   # пробка
    cv.rect(4, 4, 5, 5, (30, 32, 30))
    return cv

# ---------------------------------------------------------------- бетон/сталь/камуфляж
def bunker():
    cv = Canvas(16, 16); r = random.Random(12)
    noisy(cv, (92, 94, 92), 12, 6, 4)
    for x in range(16): cv.set(x, 0, shade((92, 94, 92), -30)); cv.set(x, 8, shade((92, 94, 92), -26)); cv.set(x, 9, shade((92, 94, 92), 14))
    for y in range(16): cv.set(0, y, shade((92, 94, 92), -30)); cv.set(15, y, shade((92, 94, 92), 12))
    for (x, y) in ((2, 2), (13, 2), (2, 11), (13, 11), (2, 6), (13, 6)): cv.set(x, y, (60, 62, 62)); cv.set(x, y - 1, (126, 128, 126)) if y > 0 else None
    for _ in range(14): cv.set(r.randrange(16), r.randrange(16), shade((92, 94, 92), r.choice([-20, 18])))
    return cv
def hull():
    cv = Canvas(16, 16); r = random.Random(13)
    noisy(cv, (92, 100, 108), 13, 6, 4)
    for y in range(16):
        for x in range(16):
            if x in (0, 8) or y in (0, 8): cv.set(x, y, shade((92, 100, 108), -34))
            elif x in (1, 9) or y in (1, 9): cv.set(x, y, shade((92, 100, 108), 20))
    for (x, y) in ((3, 3), (6, 3), (3, 6), (6, 6), (11, 3), (14, 3), (11, 6), (14, 6), (3, 11), (6, 11), (3, 14), (6, 14), (11, 11), (14, 11), (11, 14), (14, 14)):
        cv.set(x, y, (60, 66, 72)); cv.set(x - 1, y - 1 if y > 0 else y, (140, 150, 158)) if x > 0 and y > 0 else None
    for _ in range(18): cv.set(r.randrange(16), r.randrange(16), mix(cv.get(r.randrange(16), r.randrange(16))[:3], (120, 80, 50), .5))
    return cv
def camo_concrete():
    cv = Canvas(16, 16); r = random.Random(14)
    rng = np.random.default_rng(14)
    n1 = vnoise(16, 16, rng, 8); n2 = vnoise(16, 16, rng, 4)
    pal = [(98, 106, 72), (142, 132, 100), (70, 78, 52), (112, 96, 70)]
    for y in range(16):
        for x in range(16):
            v = n1[y, x] * .6 + n2[y, x] * .4
            c = pal[0] if v < .35 else pal[1] if v < .5 else pal[2] if v < .65 else pal[3]
            cv.set(x, y, shade(c, r.randint(-5, 5)))
    for _ in range(8): cv.set(r.randrange(16), r.randrange(16), (88, 88, 84))
    return cv
def grating():
    cv = Canvas(16, 16); r = random.Random(15)
    for y in range(16):
        for x in range(16):
            if x % 4 == 0 or y % 4 == 0:
                cv.set(x, y, shade((74, 80, 84), r.randint(-5, 5) + (14 if (x % 4 == 0 and x % 8 == 0) else 0)))
            elif x % 4 == 1 or y % 4 == 1:
                cv.set(x, y, shade((46, 50, 54), 0))
    for y in range(0, 16, 4):
        for x in range(0, 16, 4): cv.set(x, y, (110, 116, 120))
    for x in range(16): cv.set(x, 0, (96, 102, 106)); cv.set(x, 15, (60, 64, 68)) if False else None
    return cv
def glass():
    cv = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            edge = min(x, y, 15 - x, 15 - y)
            if edge == 0: cv.set(x, y, (58, 64, 68))
            elif edge == 1: cv.set(x, y, (112, 120, 126))
            else: cv.set(x, y, (120, 160, 150), 70)
    for i in range(3, 10): cv.set(i + 1, 11 - i + 2, (210, 235, 230), 120); cv.set(i + 2, 12 - i + 2, (210, 235, 230), 80)
    for (x, y) in ((1, 1), (14, 1), (1, 14), (14, 14)): cv.set(x, y, (60, 66, 70))
    return cv
def camo_net():
    cv = Canvas(16, 16); r = random.Random(16); rng = np.random.default_rng(16)
    n = vnoise(16, 16, rng, 4)
    pal = [(70, 84, 48), (96, 104, 62), (60, 66, 42), (120, 108, 72)]
    for y in range(16):
        for x in range(16):
            if (x + y) % 4 == 0 or (x - y) % 4 == 0:        # сетка из шнура
                cv.set(x, y, (54, 56, 40))
            elif n[y, x] > .45 and r.random() < .75:        # лоскуты камуфляжной ткани
                cv.set(x, y, shade(pal[int(n[y, x] * 10) % 4], r.randint(-8, 8)))
    return cv
def tank_trap():
    cv = Canvas(16, 16); r = random.Random(17)
    for y in range(16):
        for x in range(16):
            prof = {0: -22, 1: -6, 2: 8, 3: 14, 4: 8, 5: -6, 6: -14, 7: -22}[x % 8]
            cv.set(x, y, shade((92, 78, 66), prof + r.randint(-5, 5)))
    for _ in range(40): cv.set(r.randrange(16), r.randrange(16), mix(cv.get(r.randrange(16), r.randrange(16))[:3], (150, 82, 44), .55))
    for y in (4, 11):
        for x in range(16): cv.set(x, y, shade(cv.get(x, y)[:3], -26))
    return cv

# ---------------------------------------------------------------- знак
def sign():
    cv = Canvas(16, 16)
    for y in range(16):
        for x in range(16):
            cv.set(x, y, (232, 192, 36) if (x + y) % 8 < 4 else (30, 30, 30)) if (y < 3 or y > 12) else cv.set(x, y, (232, 192, 36))
    for y in range(16):
        for x in (0, 15): cv.set(x, y, (30, 30, 30))
    for x in range(16): cv.set(x, 0, (30, 30, 30)); cv.set(x, 15, (30, 30, 30))
    for y in range(4, 10): cv.rect(7, y, 8, y, (24, 24, 24))              # «!»
    cv.rect(7, 11, 8, 12, (24, 24, 24))
    cv.rect(3, 3, 4, 3, (24, 24, 24)); cv.rect(11, 3, 12, 3, (24, 24, 24))
    return cv
def sign_back():
    cv = Canvas(16, 16); noisy(cv, (92, 98, 102), 19, 6, 4); return cv

# ---------------------------------------------------------------- радиостанция
def radio():
    cv = Canvas(16, 16); r = random.Random(20)
    noisy(cv, (78, 88, 58), 20, 6, 4, 0, 8)                              # корпус y0-7
    for (x, y) in ((1, 1), (14, 1), (1, 6), (14, 6)): cv.set(x, y, (130, 138, 120))
    for x in range(16): cv.set(x, 0, shade(cv.get(x, 0)[:3], 14)); cv.set(x, 7, shade(cv.get(x, 7)[:3], -24))
    for y in range(8, 14):                                               # панель приборов x0-7
        for x in range(8): cv.set(x, y, (30, 32, 34))
    for (cx, cy) in ((2, 10), (5, 10)):
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if dx * dx + dy * dy <= 2: cv.set(cx + dx, cy + dy, (186, 190, 184))
        cv.set(cx, cy, (24, 24, 24)); cv.set(cx + 1, cy - 1, (200, 60, 40))
    for x in (1, 3, 5): cv.set(x, 8, (60, 200, 80) if x != 3 else (220, 70, 50))
    for x in range(1, 7): cv.set(x, 13, (120, 124, 118)) if x % 2 else None
    for y in range(8, 14):                                               # решётка динамика x8-15
        for x in range(8, 16):
            cv.set(x, y, (24, 26, 26) if (x % 2 == 0 and y % 2 == 0) else (56, 60, 60))
    for y in range(14, 16):
        for x in range(16): cv.set(x, y, shade((38, 40, 40), r.randint(-3, 3) + (10 if y == 14 else 0)))
    return cv
# ---------------------------------------------------------------- генератор
def generator():
    cv = Canvas(16, 16); r = random.Random(21)
    noisy(cv, (92, 102, 64), 21, 6, 4, 0, 6)                             # корпус y0-5
    for x in range(16): cv.set(x, 2, shade(cv.get(x, 2)[:3], -20)); cv.set(x, 3, shade(cv.get(x, 3)[:3], 12))
    noisy(cv, (150, 54, 40), 22, 5, 4, 6, 10)                           # топливный бак y6-9
    for x in range(16): cv.set(x, 6, shade(cv.get(x, 6)[:3], 18)); cv.set(x, 9, shade(cv.get(x, 9)[:3], -24))
    for y in range(10, 14):                                              # панель x0-7 y10-13
        for x in range(8): cv.set(x, y, (28, 30, 30))
    cv.rect(1, 11, 3, 12, (210, 206, 190)); cv.set(2, 11, (190, 50, 40)); cv.rect(5, 11, 6, 12, (70, 200, 90))
    for y in range(10, 14):                                              # вентиляция x8-15
        for x in range(8, 16): cv.set(x, y, (20, 22, 22) if y % 2 == 0 else (60, 64, 62))
    for y in range(14, 16):
        for x in range(16): cv.set(x, y, shade((46, 46, 44), r.randint(-3, 3)))
    return cv
# ---------------------------------------------------------------- прожектор
def flood():
    cv = Canvas(16, 16); r = random.Random(23)
    noisy(cv, (66, 72, 62), 23, 5, 4, 0, 8)
    for x in range(16): cv.set(x, 0, shade(cv.get(x, 0)[:3], 14)); cv.set(x, 7, shade(cv.get(x, 7)[:3], -20))
    for y in range(8, 16):                                               # линза x0-7 y8-15: яркая
        for x in range(8):
            d = math.hypot(x - 3.5, y - 11.5)
            cv.set(x, y, mix((255, 250, 220), (200, 196, 160), min(1, d / 5)) if d < 4.6 else (40, 44, 40))
    for y in range(8, 16):                                               # тёмный металл x8-15
        for x in range(8, 16): cv.set(x, y, shade((36, 40, 38), r.randint(-4, 4) + (8 if x == 8 else 0)))
    return cv
# ---------------------------------------------------------------- стол с картой
def map_table():
    cv = Canvas(16, 16); r = random.Random(24)
    for y in range(16):
        for x in range(16):
            base = (206, 190, 140)
            if (x * 3 + y * 5) % 11 == 0: base = (176, 160, 112)
            cv.set(x, y, shade(base, r.randint(-4, 4)))
    for x in range(0, 16, 4):
        for y in range(16): cv.set(x, y, (150, 134, 96))
    for y in range(0, 16, 4):
        for x in range(16): cv.set(x, y, (150, 134, 96))
    for (x, y) in ((3, 2), (4, 3), (5, 3), (6, 4), (9, 7), (10, 7), (11, 8), (12, 9), (6, 11), (7, 12), (8, 12)): cv.set(x, y, (190, 52, 40))
    for (x, y) in ((7, 1), (8, 1), (12, 13), (13, 13)): cv.set(x, y, (52, 84, 170))
    for x in range(16): cv.set(x, 0, (96, 74, 44)); cv.set(x, 15, (96, 74, 44))
    for y in range(16): cv.set(0, y, (96, 74, 44)); cv.set(15, y, (96, 74, 44))
    return cv
def map_table_wood():
    cv = Canvas(16, 16); r = random.Random(25)
    for y in range(16):
        for x in range(16): cv.set(x, y, shade((128, 96, 58), r.randint(-6, 6) + (-14 if y % 4 == 3 else 0)))
    return cv

ALL = {
 'sandbag_block': sandbag(), 'hesco_barrier': hesco(), 'razor_wire': razor(),
 'ammo_crate_side': ammo_crate_side(), 'ammo_crate_top': ammo_crate_top(),
 'supply_crate_side': supply_crate_side(), 'supply_crate_top': supply_crate_top(),
 'fuel_drum': drum_side(), 'fuel_drum_top': drum_top(),
 'bunker_concrete': bunker(), 'steel_hull_plate': hull(), 'camo_concrete': camo_concrete(),
 'steel_grating': grating(), 'armored_glass': glass(), 'camo_net': camo_net(), 'tank_trap': tank_trap(),
 'warning_sign': sign(), 'warning_sign_back': sign_back(), 'radio_station': radio(),
 'field_generator': generator(), 'floodlight': flood(), 'map_table': map_table(), 'map_table_wood': map_table_wood(),
}
if __name__ == '__main__':
    from PIL import Image
    names = list(ALL)
    for n, cv in ALL.items(): cv.save(os.path.join(ROOT, n + '.png'))
    S = 8; cols = 8; rows = (len(names) + cols - 1) // cols
    sheet = Image.new('RGB', (cols * (16 * S + 8) + 8, rows * (16 * S + 8) + 8), (40, 42, 48))
    for i, n in enumerate(names):
        cv = ALL[n]; im = Image.fromarray(cv.px, 'RGBA'); bg = Image.new('RGBA', im.size, (70, 74, 82, 255)); bg.alpha_composite(im)
        sheet.paste(bg.resize((16 * S, 16 * S), Image.NEAREST).convert('RGB'), (8 + (i % cols) * (16 * S + 8), 8 + (i // cols) * (16 * S + 8)))
    sheet.save(f'{PREV}/sheet_blocks2.png'); print(len(names), 'textures', sheet.size)
