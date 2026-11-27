import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
RES = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/frontiermilitary/textures')
PREV = '/home/claude/preview'
os.makedirs(f'{RES}/item', exist_ok=True); os.makedirs(f'{RES}/entity', exist_ok=True)

def fiber():
    """Катушка арамидного (кевларового) волокна: золотая нить на оливковых фланцах."""
    cv = Canvas(16, 16)
    r = random.Random(3)
    OUT = (28, 32, 26)
    fl = {'h': (118, 130, 100), 'd': (78, 90, 66), 's': (52, 60, 46)}
    # фланцы (верх rows 1-2, низ rows 13-14), ширина cols 2..13
    for (ya, yb) in ((1, 3), (12, 14)):
        for y in range(ya, yb + 1):
            for x in range(2, 14):
                edge = x in (2, 13) or y in (ya, yb)
                if edge: c = OUT
                else:
                    c = fl['h'] if (y == ya + 1 and x < 11) else fl['d'] if x < 11 else fl['s']
                cv.set(x, y, c)
    # цилиндрическая обмотка rows 4..11, cols 3..12
    prof = [(244, 214, 100), (230, 190, 70), (214, 172, 56), (196, 150, 44), (176, 130, 36),
            (150, 108, 30), (122, 86, 26), (96, 68, 22)]  # слева светло -> справа тёмно
    for y in range(4, 12):
        for i, x in enumerate(range(4, 12)):
            c = prof[i]
            wrap = (y + (i // 3)) % 2          # диагональная намотка
            if wrap: c = shade(c, -16)
            cv.set(x, y, shade(c, r.randint(-3, 3)))
        cv.set(3, y, OUT); cv.set(12, y, OUT)
    # перемычки тени под фланцем
    for x in range(4, 12): cv.set(x, 4, shade(cv.get(x, 4)[:3], -22)); cv.set(x, 11, shade(cv.get(x, 11)[:3], -14))
    # диагональные «волокна» поверх намотки
    for i in range(7):
        x, y = 4 + i, 10 - i if 10 - i >= 4 else 4
        c = cv.get(x, y)[:3]; cv.set(x, y, shade(c, 26))
    # растрёпанный кончик нити на верхнем фланце
    cv.set(9, 0, (232, 196, 80)); cv.set(10, 0, (186, 142, 46)); cv.set(10, 1, (232, 196, 80))
    return cv

def ration():
    """Ретортный пакет (MRE): песочно-коричневый, оливковая этикетка, зубчатые швы."""
    P = {'O': (46, 36, 24), 't': (190, 160, 108), 'T': (214, 186, 132), 'd': (152, 124, 80), 'D': (118, 94, 58),
         'g': (84, 98, 58), 'G': (62, 74, 44), 'w': (232, 228, 214), 'k': (40, 40, 36), 'r': (176, 52, 40),
         's': (120, 104, 76)}
    rows = [
        "................",
        "...OsOsOsOsOs...",
        "..OTTTTTTTTTtO..",
        "..OTtttttttttO..",
        "..OTtGGGGGGGtO..",
        "..OTtgwwwwwgtO..",
        "..OTtgwkkkwgtO..",
        "..OTtgwrrrwgtO..",
        "..OTtgwkkkwgtd..",
        "..OTtgwwwwwgdD..",
        "..OTtGGGGGGdDD..",
        "..OTttttttdDDO..",
        "..OtttttdddDDO..",
        "...OsOsOsOsOs...",
        "................",
        "................",
    ]
    cv = from_ascii(rows, P)
    cv.set(3, 14, (0,0,0), 0)
    # надрыв-ключ в левом верхнем углу
    cv.set(2, 2, (0,0,0), 0); cv.set(2, 3, P['d'])
    return cv

def ammo():
    """Картонная пачка патронов: оливковая коробка + латунные гильзы сверху."""
    P = {'O': (30, 34, 26), 'g': (92, 106, 64), 'G': (70, 82, 48), 'h': (122, 136, 88), 'w': (226, 222, 205),
         'b': (214, 170, 62), 'B': (160, 120, 36), 'y': (246, 212, 110), 'k': (44, 44, 40), 'r': (170, 54, 40),
         'c': (176, 112, 70)}
    rows = [
        "................",
        "................",
        "...yb.yb.yb.yb..",
        "...bB.bB.bB.bB..",
        "...bB.bB.bB.bB..",
        "..cbBcbBcbBcbBc.",
        ".OOOOOOOOOOOOOOO",
        ".OhhhhhhhhhhhhhO",
        ".OggggggggggggGO",
        ".OgwwwwwwwwwwgGO",
        ".Ogwk.k.k.k.wgGO",
        ".OgwrrrrrrrrwgGO",
        ".OgwwwwwwwwwwgGO",
        ".OGGGGGGGGGGGGGO",
        ".OOOOOOOOOOOOOOO",
        "................",
    ]
    cv = from_ascii([r.replace('.', '.') for r in rows], P)
    # чёрные «буквы» этикетки: пиксельный штрих-код
    for x in (4, 6, 8, 10): cv.set(x, 10, P['k'])
    for x in (5, 7, 9): cv.set(x, 10, P['w'])
    return cv

def rifle_ammo():
    """Картонная пачка винтовочных патронов: длинные гильзы со стальной лакировкой и латунным пояском."""
    P = {'O': (30, 34, 26), 'g': (92, 106, 64), 'G': (70, 82, 48), 'h': (122, 136, 88), 'w': (226, 222, 205),
         's': (150, 152, 146), 'S': (104, 106, 102), 'b': (214, 170, 62), 'B': (160, 120, 36), 'k': (44, 44, 40), 'r': (170, 54, 40), 'c': (176, 112, 70), 't': (190, 80, 50)}
    rows = [
        "................",
        "...tb.tb.tb.tb..",
        "...sS.sS.sS.sS..",
        "...sS.sS.sS.sS..",
        "...sS.sS.sS.sS..",
        "...bB.bB.bB.bB..",
        ".OOOOOOOOOOOOOOO",
        ".OhhhhhhhhhhhhhO",
        ".OggggggggggggGO",
        ".OgwwwwwwwwwwgGO",
        ".Ogwk.k.k.k.wgGO",
        ".OgwrrrrrrrrwgGO",
        ".OgwwwwwwwwwwgGO",
        ".OGGGGGGGGGGGGGO",
        ".OOOOOOOOOOOOOOO",
        "................"]
    cv = from_ascii(rows, P)
    for x in (4, 6, 8, 10): cv.set(x, 10, P['k'])
    for x in (5, 7, 9): cv.set(x, 10, P['w'])
    return cv

def tracer():
    """Трассер пули: яркое ядро, тёплый ореол. Рисуется вдоль U (длина), прозрачный фон."""
    cv = Canvas(16, 16)
    for x in range(16):
        t = x / 15.0                                  # 0 = хвост, 1 = головка
        for y in range(16):
            d = abs(y - 7.5)
            if d > 2.1: continue
            core = d < 0.9
            a = int(255 * (0.15 + 0.85 * t) * (1.0 if core else 0.45))
            c = mix((255, 150, 40), (255, 250, 200), t) if core else mix((255, 110, 20), (255, 200, 90), t)
            cv.set(x, y, c, a)
    return cv

if __name__ == '__main__':
    out = {'reinforced_fiber': fiber(), 'field_ration': ration(), 'pistol_ammo': ammo(), 'rifle_ammo': rifle_ammo()}
    for n, cv in out.items():
        cv.save(f'{RES}/item/{n}.png'); cv.preview(f'{PREV}/item_{n}.png', 20)
    t = tracer(); t.save(f'{RES}/entity/bullet_tracer.png'); t.preview(f'{PREV}/item_tracer.png', 20)
    from PIL import Image
    ims = [Image.open(f'{PREV}/item_{n}.png') for n in ('reinforced_fiber', 'field_ration', 'pistol_ammo', 'tracer')]
    sh = Image.new('RGB', (sum(i.width for i in ims) + 50, 340), (30, 30, 34)); x = 10
    for i in ims: sh.paste(i, (x, 10)); x += i.width + 10
    sh.save(f'{PREV}/sheet_items.png')
