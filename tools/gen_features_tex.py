import os, sys, random, math
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *
import gen_block_textures2 as bt
RES = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/frontiermilitary/textures')

# --- генератор «включён»: яркие индикаторы
g = bt.generator()
for (x, y) in ((1, 11), (2, 11), (3, 11), (1, 12), (2, 12), (3, 12)): g.set(x, y, (210, 206, 190))
g.set(2, 11, (120, 255, 150))
for (x, y) in ((5, 11), (6, 11), (5, 12), (6, 12)): g.set(x, y, (120, 255, 150))
g.save(f'{RES}/block/field_generator_on.png')
# --- прожектор «выключен»: тусклая линза
f = bt.flood()
for y in range(8, 16):
    for x in range(8):
        r, gg, b, a = f.get(x, y)
        if r > 150: f.set(x, y, (96, 104, 104))
f.save(f'{RES}/block/floodlight_off.png')

# --- иконки
def medkit():
    P = {'O': (24, 28, 20), 'h': (116, 128, 84), 'G': (84, 96, 58), 'd': (52, 60, 40), 'W': (232, 230, 218), 'r': (196, 40, 36), 's': (150, 150, 140)}
    rows = ["................", ".....OOOOOO.....", ".....OssssO.....", "..OOOOOOOOOOOO..", "..OhhhhhhhhhhO..",
            "..OGGWWWWWWGGO..", "..OGGWWWWWWGGO..", "..OGGWWWWWWGGO..", "..OGGWWWWWWGGO..", "..OGGWWWWWWGGO..",
            "..OGGWWWWWWGGO..", "..OGGGGGGGGGGO..", "..OddddddddddO..", "..OOOOOOOOOOOO..", "................", "................"]
    cv = from_ascii(rows, P)
    for y in range(5, 11): cv.set(7, y, P['r']); cv.set(8, y, P['r'])
    for x in range(6, 10): cv.set(x, 7, P['r']); cv.set(x, 8, P['r'])
    for x in range(3, 13): cv.set(x, 3, shade(cv.get(x, 3)[:3], 0))
    for x in range(4, 12, 2): cv.set(x, 12, (170, 170, 160))      # молния
    return cv

def canister(filled):
    cv = Canvas(16, 16); r = random.Random(9 if filled else 10)
    body = (86, 100, 60); dk = (28, 34, 22); cap = (214, 120, 36) if filled else (120, 122, 118)
    for y in range(4, 15):
        for x in range(2, 14):
            c = shade(body, {2: -26, 3: 8, 4: 16, 5: 10, 12: -10, 13: -30}.get(x, 0) + r.randint(-3, 3))
            if y in (4, 14): c = dk
            cv.set(x, y, c)
    for y in range(4, 15): cv.set(2, y, dk); cv.set(13, y, dk)
    for x in range(2, 14): cv.set(x, 4, dk); cv.set(x, 14, dk)
    for i in range(6):                                              # рельефный «X»
        cv.set(4 + i, 6 + i, shade(body, -34)); cv.set(11 - i, 6 + i, shade(body, -34)); cv.set(4 + i, 7 + i, shade(body, 18)) if i < 5 else None
    for x in (3, 4, 5, 6, 7): cv.set(x, 1, dk); cv.set(x, 3, dk) if x in (3, 7) else None
    cv.set(3, 2, dk); cv.set(7, 2, dk); cv.set(4, 1, shade(body, 18)); cv.set(5, 1, shade(body, 18)); cv.set(6, 1, shade(body, 18))
    cv.rect(10, 2, 12, 3, cap); cv.rect(10, 1, 12, 1, shade(cap, 30)); cv.set(9, 2, dk); cv.set(13, 2, dk); cv.rect(9, 3, 13, 3, dk)
    cv.rect(10, 2, 12, 3, cap)
    if filled:
        for x in range(4, 12): cv.set(x, 12, (232, 190, 60)); cv.set(x, 13, (232, 190, 60)) if x % 2 else None
    else:
        for x in range(4, 12): cv.set(x, 12, (150, 150, 146))
    return cv

for n, cv in (('medkit', medkit()), ('empty_canister', canister(False)), ('fuel_canister', canister(True))):
    cv.save(f'{RES}/item/{n}.png')
print('textures ok')
