import os, sys, random, math, json
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
from gen_armor import Layer, hnoise
from gen_block_models import w, box, face, DIRS, STD_DISPLAY, model
MOD = 'frontiermilitary'
RES = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/frontiermilitary')
TX = f'{RES}/textures'

# ------------------------------------------------------------ оптический прицел (оверлей, 1024x1024)
def scope_overlay():
    S = 1024; ss = 2; N = S * ss
    im = Image.new('RGBA', (N, N), (0, 0, 0, 255)); d = ImageDraw.Draw(im)
    r = int(N * 0.47); c = N // 2
    d.ellipse([c - r, c - r, c + r, c + r], fill=(0, 0, 0, 0))
    ring = int(N * 0.006); d.ellipse([c - r, c - r, c + r, c + r], outline=(28, 28, 30, 255), width=ring * 3)
    line = 3 * ss
    d.rectangle([c - r, c - line // 2, c + r, c + line // 2], fill=(8, 8, 10, 235))                 # тонкое перекрестие
    d.rectangle([c - line // 2, c - r, c + line // 2, c + r], fill=(8, 8, 10, 235))
    th = int(N * 0.014)
    for (x0, y0, x1, y1) in ((c - r, c - th, c - int(r * .12), c + th), (c + int(r * .12), c - th, c + r, c + th),
                             (c - th, c - r, c + th, c - int(r * .12)), (c - th, c + int(r * .12), c + th, c + r)):
        d.rectangle([x0, y0, x1, y1], fill=(8, 8, 10, 255))                                           # толстые «столбы»
    for k in range(1, 9):                                                                              # метки-миллирадианы
        for sgn in (-1, 1):
            off = int(r * 0.09 * k) * sgn
            d.rectangle([c + off - 2 * ss, c - 7 * ss, c + off + 2 * ss, c + 7 * ss], fill=(8, 8, 10, 235))
            d.rectangle([c - 7 * ss, c + off - 2 * ss, c + 7 * ss, c + off + 2 * ss], fill=(8, 8, 10, 235))
    d.ellipse([c - 4 * ss, c - 4 * ss, c + 4 * ss, c + 4 * ss], fill=(200, 30, 30, 255))             # красная точка
    # мягкое виньетирование по краю линзы
    vg = Image.new('L', (N, N), 0); vd = ImageDraw.Draw(vg)
    for i in range(30):
        a = int(110 * (i / 30) ** 2); rr = r - int(N * 0.05) + int(N * 0.05 * i / 30)
        vd.ellipse([c - rr, c - rr, c + rr, c + rr], outline=a, width=ss * 2)
    im2 = Image.new('RGBA', (N, N), (0, 0, 0, 0)); im2.paste(Image.new('RGBA', (N, N), (0, 0, 0, 255)), mask=vg)
    im = Image.alpha_composite(im, im2).resize((S, S), Image.LANCZOS)
    os.makedirs(f'{TX}/gui', exist_ok=True); im.save(f'{TX}/gui/scope.png')

# ------------------------------------------------------------ патроны
def ammo_sniper():
    P = {'O': (30, 34, 26), 'h': (122, 136, 88), 'g': (92, 106, 64), 'G': (70, 82, 48), 'w': (226, 222, 205), 'k': (44, 44, 40), 'c': (176, 96, 52),
         'C': (130, 70, 38), 'y': (214, 170, 62), 'B': (160, 120, 36)}
    rows = ["................", "...cc.cc.cc.cc..", "...cC.cC.cC.cC..", "...yB.yB.yB.yB..", "...yB.yB.yB.yB..", "...yB.yB.yB.yB..",
            ".OOOOOOOOOOOOOOO", ".OhhhhhhhhhhhhhO", ".OggggggggggggGO", ".OgwwwwwwwwwwgGO", ".Ogwk.k.k.k.wgGO", ".OgwkkkkkkkkwgGO",
            ".OgwwwwwwwwwwgGO", ".OGGGGGGGGGGGGGO", ".OOOOOOOOOOOOOOO", "................"]
    cv = from_ascii(rows, P)
    for x in (4, 6, 8, 10): cv.set(x, 10, P['k'])
    return cv
def ammo_shells():
    P = {'O': (30, 20, 20), 'r': (190, 44, 40), 'R': (140, 28, 28), 'h': (226, 90, 80), 'y': (214, 170, 62), 'B': (150, 112, 36), 'w': (230, 226, 210), 'k': (50, 40, 40)}
    rows = ["................", "..OOO..OOO..OOO.", ".OhrRO.OhrRO.OhrRO"[:16], ".OhrRO.OhrRO.OhrR"[:16], ".OhrRO.OhrRO.OhrR"[:16], ".OhrRO.OhrRO.OhrR"[:16],
            ".OwwwO.OwwwO.OwwO"[:16], ".OyyyO.OyyyO.OyyO"[:16], ".OyByO.OyByO.OyBO"[:16], ".OOOOO.OOOOO.OOOO"[:16], "................", "................", "................", "................", "................", "................"]
    cv = from_ascii([r.ljust(16, '.')[:16] for r in rows], P)
    # подставка-картонка
    for x in range(1, 15): cv.set(x, 10, (70, 82, 48)); cv.set(x, 11, (92, 106, 64)); cv.set(x, 12, (92, 106, 64)); cv.set(x, 13, (50, 60, 36))
    for x in range(2, 14): cv.set(x, 11, (226, 222, 205)) if 5 < x < 11 else None
    return cv

# ------------------------------------------------------------ кабель
def cable_tex(on):
    cv = Canvas(16, 16); r = random.Random(77)
    stripe = (255, 222, 90) if on else (150, 120, 30)
    for y in range(16):
        for x in range(16):
            c = shade((30, 32, 34), r.randint(-3, 3) + {0: 8, 1: 4, 2: 0}.get(x % 4, -4))
            if y in (7, 8): c = shade(stripe, r.randint(-6, 6))
            cv.set(x, y, c)
    for x in range(16): cv.set(x, 0, (60, 62, 64))
    return cv
def cable_icon():
    cv = Canvas(16, 16)
    for a in range(0, 720, 5):
        t = math.radians(a); rad = 3.2 + a / 720 * 3.0
        x = 7.5 + rad * math.cos(t); y = 8.0 + rad * 0.82 * math.sin(t)
        c = (34, 36, 38) if (a // 40) % 2 else (150, 120, 30)
        cv.set(int(round(x)), int(round(y)), c); cv.set(int(round(x)) + 1, int(round(y)), (24, 26, 28))
    for (x, y) in ((13, 3), (14, 3), (14, 4), (2, 13), (1, 13), (1, 12)): cv.set(x, y, (196, 120, 60))
    return cv

# ------------------------------------------------------------ маскировочный халат (ghillie)
PAL = [(62, 80, 42), (84, 102, 54), (50, 64, 34), (108, 98, 62), (74, 66, 44), (96, 112, 62)]
def shag(X, Y, bias=0):
    k = hnoise(X, Y // 2, 7) ; v = hnoise(X * 3 + 1, Y, 9)
    c = PAL[int(k * 6 + bias) % 6]
    c = shade(c, (v - .5) * 26)
    if hnoise(X, Y, 11) > 0.93: c = (124, 112, 74)
    return c
def g_helm(face, i, j, w, h, X, Y):
    if face == 'bottom': return None
    if face == 'front': return shag(X, Y) if j <= 2 else None
    if face in ('right', 'left'): return shag(X, Y) if (j <= 5 or hnoise(X, Y, 3) > 0.5) else None
    if face == 'back': return shag(X, Y) if j <= 6 or hnoise(X, Y, 4) > 0.4 else None
    return shag(X, Y)
def g_chest(face, i, j, w, h, X, Y):
    if face == 'bottom': return None
    if face in ('right', 'left', 'front', 'back', 'top') and j >= 11 and hnoise(X, Y, 5) > 0.55: return None   # бахрома по подолу
    return shag(X, Y, 1)
def g_arm(face, i, j, w, h, X, Y):
    if face == 'bottom': return None
    if j >= 10 and hnoise(X, Y, 6) > 0.5: return None
    return shag(X, Y, 2)
def g_boot(face, i, j, w, h, X, Y):
    if face == 'top': return None
    if j < 6: return None
    if face == 'bottom': return (36, 34, 28)
    if j == 6 and hnoise(X, Y, 8) > 0.5: return None
    return shag(X, Y, 3)
def g_leg(face, i, j, w, h, X, Y):
    if face in ('top', 'bottom'): return None
    if j >= 10 and hnoise(X, Y, 12) > 0.6: return None
    return shag(X, Y, 4)
def g_belt(face, i, j, w, h, X, Y):
    if face in ('top', 'bottom') or j < 8: return None
    return shag(X, Y, 5)

def ghillie_layers():
    l1 = Layer(); l1.box(0, 0, 8, 8, 8, g_helm); l1.box(16, 16, 8, 12, 4, g_chest); l1.box(40, 16, 4, 12, 4, g_arm); l1.box(0, 16, 4, 12, 4, g_boot)
    l2 = Layer(); l2.box(0, 16, 4, 12, 4, g_leg); l2.box(16, 16, 8, 12, 4, g_belt)
    return l1, l2

def masked_icon(rows, seed):
    cv = Canvas(16, 16); r = random.Random(seed)
    mask = [[ch != '.' for ch in row] for row in rows]
    for y in range(16):
        for x in range(16):
            if y < len(mask) and x < len(mask[y]) and mask[y][x]:
                cv.set(x, y, shag(x, y, seed))
    for y in range(16):
        for x in range(16):
            if cv.get(x, y)[3] and not all(0 <= x + dx < 16 and 0 <= y + dy < 16 and cv.get(x + dx, y + dy)[3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                cv.set(x, y, shade(cv.get(x, y)[:3], -34))
    for _ in range(10):
        x, y = r.randrange(16), r.randrange(15)
        if cv.get(x, y)[3] and not cv.get(x, y + 1)[3]: cv.set(x, y + 1, shade(PAL[r.randrange(6)], -10))
    return cv
HOOD = ["................", ".....XXXXXX.....", "...XXXXXXXXXX...", "..XXXXXXXXXXXX..", ".XXXXXXXXXXXXXX.", ".XXXXXXXXXXXXXX.", ".XXXXXX..XXXXXX.", ".XXXXX....XXXXX.", ".XXXXX....XXXXX.",
        ".XXXX......XXXX.", ".XXX........XXX.", "..X..........X.."]
JACKET = ["................", "..XXX......XXX..", ".XXXXXXXXXXXXXX.", "XXXXXXXXXXXXXXXX", "XXXXXXXXXXXXXXXX", "XXXXXXXXXXXXXXXX", "XXXX.XXXXXX.XXXX", "XXX..XXXXXX..XXX",
          "XXX..XXXXXX..XXX", "XXX..XXXXXX..XXX", ".XX..XXXXXX..XX.", "......XXXXXX....", "......XXXXXX...."]
TROUS = ["................", "...XXXXXXXXXX...", "...XXXXXXXXXX...", "...XXXXXXXXXX...", "...XXXXXXXXXX...", "...XXXXX.XXXX...", "...XXXX..XXXX...", "...XXXX..XXXX...", "...XXXX..XXXX...",
         "...XXXX..XXXX...", "...XXXX..XXXX...", "...XXX....XXX...", "...XXX....XXX..."]
BOOTS = ["................", "................", "................", "...XXXX..XXXX...", "..XXXXX..XXXXX..", "..XXXXX..XXXXX..", "..XXXXX..XXXXX..", "..XXXXX..XXXXX..", "..XXXXX..XXXXX..",
         ".XXXXXXX.XXXXXXX", ".XXXXXXX.XXXXXXX", "................"]
def main():
    scope_overlay()
    for n, cv in (('sniper_ammo', ammo_sniper()), ('shotgun_shells', ammo_shells()), ('power_cable', cable_icon())): cv.save(f'{TX}/item/{n}.png')
    cable_tex(False).save(f'{TX}/block/power_cable.png'); cable_tex(True).save(f'{TX}/block/power_cable_on.png')
    l1, l2 = ghillie_layers(); l1.cv.save(f'{TX}/models/armor/ghillie_layer_1.png'); l2.cv.save(f'{TX}/models/armor/ghillie_layer_2.png')
    for n, rows, seed in (('ghillie_hood', HOOD, 1), ('ghillie_jacket', JACKET, 2), ('ghillie_trousers', TROUS, 3), ('ghillie_wraps', BOOTS, 4)):
        masked_icon(rows, seed).save(f'{TX}/item/{n}.png')
    # --- модели предметов
    for n in ('sniper_ammo', 'shotgun_shells', 'ghillie_hood', 'ghillie_jacket', 'ghillie_trousers', 'ghillie_wraps'):
        w(f'{RES}/models/item/{n}.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{MOD}:item/{n}'}})
    w(f'{RES}/models/item/power_cable.json', {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{MOD}:item/power_cable'}})
    # --- блок кабеля: узел + 6 рук, варианты off/on
    SIDES = {d: (0, 0, 16, 3) for d in DIRS}
    for suffix, tex in (('', 'power_cable'), ('_on', 'power_cable_on')):
        node = [box((6.5, 6.5, 6.5), (9.5, 9.5, 9.5), '#t', {d: (0, 6.5, 3, 9.5) for d in DIRS})]
        arm = [box((6.5, 6.5, 0), (9.5, 9.5, 6.5), '#t', {'north': (0, 6.5, 3, 9.5), 'up': (6.5, 0, 9.5, 6.5), 'down': (6.5, 0, 9.5, 6.5), 'east': (0, 6.5, 6.5, 9.5), 'west': (0, 6.5, 6.5, 9.5)}, ('north', 'up', 'down', 'east', 'west'))]
        tx = {'t': f'{MOD}:block/{tex}', 'particle': f'{MOD}:block/{tex}'}
        w(f'{RES}/models/block/power_cable_node{suffix}.json', model(tx, node))
        w(f'{RES}/models/block/power_cable_arm{suffix}.json', model(tx, arm))
    parts = []
    for powered in ('false', 'true'):
        suffix = '_on' if powered == 'true' else ''
        parts.append({'when': {'powered': powered}, 'apply': {'model': f'{MOD}:block/power_cable_node{suffix}'}})
        for d, rot in (('north', {}), ('east', {'y': 90}), ('south', {'y': 180}), ('west', {'y': 270}), ('up', {'x': 270}), ('down', {'x': 90})):
            parts.append({'when': {d: 'true', 'powered': powered}, 'apply': {'model': f'{MOD}:block/power_cable_arm{suffix}', **rot}})
    w(f'{RES}/blockstates/power_cable.json', {'multipart': parts})
    print('features2 resources ok')
main()
