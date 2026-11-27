"""Текстуры брони «Боевая экипировка»: слои (64x32, стандартная раскладка) и иконки предметов."""
import os, sys, math, random
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))
from pxlib import *

RES = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/frontiermilitary/textures')
PREV = '/home/claude/preview'
os.makedirs(f'{RES}/models/armor', exist_ok=True)

OLIVE, DARK, BROWN, TAN = (78, 90, 56), (46, 54, 38), (100, 84, 56), (128, 118, 84)
COYOTE = (140, 118, 82); BLACK = (32, 33, 32); STRAP = (44, 46, 42); GRAY = (84, 88, 90)

def hnoise(x, y, s=0):
    v = math.sin(x * 12.9898 + y * 78.233 + s * 37.7) * 43758.5453
    return v - math.floor(v)

def camo(X, Y):
    n = math.sin(X * 0.78 + Y * 0.31) * math.sin(Y * 0.83 - X * 0.22) + 0.55 * math.sin(X * 0.37 + Y * 1.1 + 2)
    c = OLIVE if n < -0.15 else DARK if n < 0.35 else BROWN if n < 0.75 else TAN
    return shade(c, (hnoise(X, Y) - .5) * 8)

class Layer:
    def __init__(s): s.cv = Canvas(64, 32)
    def box(s, u, v, dx, dy, dz, shader):
        regions = {'top': (u + dz, v, dx, dz), 'bottom': (u + dz + dx, v, dx, dz), 'right': (u, v + dz, dz, dy),
                   'front': (u + dz, v + dz, dx, dy), 'left': (u + dz + dx, v + dz, dz, dy), 'back': (u + 2 * dz + dx, v + dz, dx, dy)}
        for face, (x0, y0, w, h) in regions.items():
            for j in range(h):
                for i in range(w):
                    c = shader(face, i, j, w, h, x0 + i, y0 + j)
                    if c is not None: s.cv.set(x0 + i, y0 + j, c)

# ----------------------------------------------------------- слой 1: каска, жилет, рукава, берцы
def helmet_shader(face, i, j, w, h, X, Y):
    if face == 'bottom': return None
    if face == 'front':
        if j > 3: return None
        c = camo(X, Y)
        if j == 3: c = shade(COYOTE, -10)                       # кант
        if j <= 1 and 3 <= i <= 4: c = BLACK                    # крепление ПНВ
        return c
    if face in ('right', 'left'):
        if j > 4 and not (i in (3, 4) and j <= 7): return None
        if j > 4: return STRAP                                  # подбородочный ремень
        c = camo(X, Y)
        if j == 4: c = shade(COYOTE, -10)
        return c
    if face == 'back':
        if j > 5: return None
        c = camo(X, Y)
        if j == 5: c = shade(COYOTE, -10)
        return c
    c = camo(X, Y)                                              # top
    if i in (0, w - 1) or j in (0, h - 1): c = shade(c, -14)
    return c

def chest_shader(face, i, j, w, h, X, Y):
    if face == 'bottom': return None
    base = shade(COYOTE, (hnoise(X, Y, 3) - .5) * 8)
    if face == 'top': return shade(STRAP, 6) if i in (1, 2, w - 3, w - 2) else base
    if face in ('right', 'left'):
        if j >= 7: return shade(STRAP, 10 if (j % 2) else -4)  # камербанд с резинками
        return base if j > 1 else shade(STRAP, 4)
    # front/back
    if j == 0 and i in (1, 2, 5, 6): return STRAP                # лямки
    if j <= 2 and i in (1, 2, 5, 6): return shade(STRAP, 8)
    c = base
    if face == 'front':
        if 1 <= i <= 6 and 2 <= j <= 6:                          # карман бронеплиты
            edge = i in (1, 6) or j in (2, 6)
            c = shade(OLIVE, -6) if edge else shade(OLIVE, 6 + ((i + j) % 2) * 3)
        if j >= 8:                                               # подсумки под магазины
            col = i // 2 if i < 6 else 3
            if i in (0, 2, 4, 6) or j == 8: c = shade(DARK, 6)
            else: c = shade(OLIVE, -4 + (i % 2) * 5)
            if j == 9 and i % 2 == 1: c = shade(COYOTE, -30)    # клапан
        if j in (7,) : c = shade(STRAP, 8)
    else:
        if 1 <= i <= 6 and 2 <= j <= 7: c = shade(OLIVE, -4 + ((i + j) % 2) * 4)
        if j >= 8: c = shade(STRAP, 8 if j % 2 else 0)
    if j % 3 == 1 and 7 <= j and face == 'front': c = shade(c, -6)
    return c

def arm_shader(face, i, j, w, h, X, Y):
    if face in ('top',): return shade(OLIVE, -10)
    if face == 'bottom': return None
    if j >= 9: return None                                        # кисть открыта
    c = camo(X, Y)
    if j <= 1: c = shade(OLIVE, -12)                               # наплечник
    if 5 <= j <= 7 and face in ('front', 'right', 'left', 'back') and ((face == 'back') or (face in ('left', 'right'))): c = shade(GRAY, -20 + (j % 2) * 6)  # налокотник
    if j == 8: c = shade(COYOTE, -20)                              # манжета
    return c

def boot_shader(face, i, j, w, h, X, Y):
    if face == 'top': return None
    if face == 'bottom': return shade(GRAY, -34 + ((i + j) % 2) * 8)    # подошва с протектором
    if j < 7: return None
    if j == 7: return shade(COYOTE, -6)                          # блузовка штанин
    if j == 11: return shade((20, 20, 20), 0)                      # подошва
    c = shade(BLACK, (hnoise(X, Y, 5) - .5) * 7 + (6 if j == 8 else 0))
    if face == 'front' and j in (8, 9) and i in (1, 2): c = shade(COYOTE, -20 + (i % 2) * 10)   # шнуровка
    return c

# ----------------------------------------------------------- слой 2: брюки + пояс
def leg_shader(face, i, j, w, h, X, Y):
    if face in ('top', 'bottom'): return None
    c = camo(X + 17, Y + 3)
    if j == 11: c = shade(c, -26)                                    # манжета
    if face in ('left', 'right') and 2 <= j <= 7 and 0 <= i < w:   # карго-карман
        edge = j in (2, 7) or i in (0, w - 1)
        c = shade(OLIVE, -22) if edge else shade(c, -6)
        if j == 3: c = shade(DARK, 0)                              # клапан
    if face == 'front' and 6 <= j <= 8: c = shade(GRAY, -26 + (j % 2) * 8)    # наколенник
    if j == 0: c = shade(c, -10)
    return c

def belt_shader(face, i, j, w, h, X, Y):
    if face in ('top', 'bottom'): return None
    if j < 8: return None
    if j in (9, 10): 
        c = shade(STRAP, 6 + (j == 9) * 6)
        if face == 'front' and i in (3, 4): c = shade(GRAY, 30 + (j == 9) * 20)   # пряжка
        return c
    return camo(X + 17, Y + 3)

def make_layers():
    l1 = Layer()
    l1.box(0, 0, 8, 8, 8, helmet_shader)
    l1.box(16, 16, 8, 12, 4, chest_shader)
    l1.box(40, 16, 4, 12, 4, arm_shader)
    l1.box(0, 16, 4, 12, 4, boot_shader)
    l2 = Layer()
    l2.box(0, 16, 4, 12, 4, leg_shader)
    l2.box(16, 16, 8, 12, 4, belt_shader)
    return l1, l2

# ----------------------------------------------------------- иконки
def icons():
    P = {'O': (24, 28, 20), 'g': (116, 128, 84), 'G': (84, 96, 58), 'd': (52, 60, 40), 'b': (106, 88, 58), 'K': (30, 30, 30),
         'r': (150, 130, 92), 's': (44, 46, 42), 't': (140, 118, 82), 'T': (170, 148, 106), 'h': (150, 160, 118), 'k': (20, 20, 20),
         'y': (118, 100, 64), 'z': (86, 90, 92)}
    helm = ["................",
            "......OOOO......",
            "....OOhgGGOO....",
            "...OhgGGGbGGO...",
            "..OgGGGdGGGGGO..",
            "..OGGbGGGGdGGO..",
            ".OgGGGGGGGGGGGO.",
            ".OGdGGGbGGGGGdO.",
            ".OGGGGGGGGGGGGO.",
            ".OrrrrrrKKrrrrO.",
            ".OOOOOOOKKOOOOO.",
            "..OsO......OsO..",
            "..OsO......OsO..",
            "...O........O...",
            "................",
            "................"]
    vest = ["................",
            "..OOO......OOO..",
            "..OsGO....OGsO..",
            "..OsGOOOOOOGsO..",
            "..OGGGGGGGGGGO..",
            ".OGGOOOOOOOOGGO.",
            ".OGOGGGGGGGGOGO.",
            ".OGOGGhGGGGGOGO.",
            ".OGOGGGGGGGGOGO.",
            ".OGOOOOOOOOOOGO.",
            ".OsssssssssssO..",
            ".OdOGGOdOGGOdO..",
            ".OdOGGOdOGGOdO..",
            ".OOOtOOOOtOOOO..",
            "................",
            "................"]
    trou = ["................",
            "...OOOOOOOOOO...",
            "..OsssssssssssO.",
            "..OGGGGGOGGGGGO.",
            "..OGGGGGOGGGGGO.",
            "..OGdddGOGdddGO.",
            "..OGdGdGOGdGdGO.",
            "..OGdddGOGdddGO.",
            "..OGGGGGOGGGGGO.",
            "..OGzzzGOGzzzGO.",
            "..OGzzzGOGzzzGO.",
            "..OGGGGGOGGGGGO.",
            "..OGGGGGOGGGGGO.",
            "..OtttGOGtttGO..",
            "...OOOO.OOOO....",
            "................"]
    boots = ["................",
             "................",
             "...OOOO..OOOO...",
             "..OtttO.OtttO...",
             "..OkkkO.OkkkO...",
             "..OkTkO.OkTkO...",
             "..OkkkO.OkkkO...",
             "..OkTkO.OkTkO...",
             "..OkkkO.OkkkO...",
             "..OkkkkOOkkkkO..",
             ".OkkkkkkOkkkkkO.",
             ".OkkkkkkOkkkkkO.",
             ".OzzzzzzOzzzzzO.",
             ".OOOOOOOOOOOOOO.",
             "................",
             "................"]
    return {'combat_helmet': from_ascii(helm, P), 'plate_carrier': from_ascii(vest, P),
            'combat_trousers': from_ascii(trou, P), 'combat_boots': from_ascii(boots, P)}

if __name__ == '__main__':
    l1, l2 = make_layers()
    l1.cv.save(f'{RES}/models/armor/combat_layer_1.png'); l2.cv.save(f'{RES}/models/armor/combat_layer_2.png')
    ic = icons()
    for n, cv in ic.items(): cv.save(f'{RES}/item/{n}.png')
    # превью
    S = 8
    sheet = Image.new('RGB', (4 * 16 * S + 5 * 8 + 2 * 64 * 5 + 24, 64 * 5 + 24), (40, 42, 48)); x = 8
    for n, cv in ic.items():
        im = Image.fromarray(cv.px, 'RGBA'); bg = Image.new('RGBA', im.size, (70, 74, 82, 255)); bg.alpha_composite(im)
        sheet.paste(bg.resize((16 * S, 16 * S), Image.NEAREST).convert('RGB'), (x, 8)); x += 16 * S + 8
    for l in (l1, l2):
        im = Image.fromarray(l.cv.px, 'RGBA'); bg = Image.new('RGBA', im.size, (70, 74, 82, 255)); bg.alpha_composite(im)
        sheet.paste(bg.resize((64 * 5, 32 * 5), Image.NEAREST).convert('RGB'), (x, 8)); x += 64 * 5 + 8
    sheet.save(f'{PREV}/armor_sheet.png'); print('armor textures done')
