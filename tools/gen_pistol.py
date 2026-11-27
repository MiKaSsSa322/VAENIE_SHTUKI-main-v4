"""Генератор 3D-модели служебного пистолета: атлас текстур + JSON-модели состояний + руки от первого лица.
Оружие направлено стволом в -Z, верх +Y, правая сторона +X."""
import os, sys, json, math, random
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(__file__))

MOD = 'frontiermilitary'
RES = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets', MOD)
ATLAS = 256; DENS = 4; UVS = ATLAS / 16.0   # текселей на единицу UV

# ------------------------------------------------------------------ шум и цвета
def pn(x, y, z):
    v = math.sin(x * 12.9898 + y * 78.233 + z * 37.719) * 43758.5453
    return v - math.floor(v)
def sh(c, d): return tuple(max(0, min(255, int(round(v + d)))) for v in c)
def mix(a, b, t): return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3))

# ------------------------------------------------------------------ шейдеры материалов
def mat_slide(face, p, e, ctx):
    c = sh((44, 48, 53), (pn(*[round(v * 4) for v in p]) - .5) * 5)
    x, y, z = p
    if face in ('east', 'west'):
        if 10.6 < z < 12.9 and 9.95 < y < 12.35:                      # задние насечки
            k = int((z - 10.6) / 0.55); c = sh(c, -16 if k % 2 == 0 else 8)
        if 3.0 < z < 4.4 and 9.95 < y < 12.35:                        # передние насечки
            k = int((z - 3.0) / 0.55); c = sh(c, -16 if k % 2 == 0 else 8)
        if y < 10.0: c = sh(c, -10)
        if face == 'east' and 6.2 < z < 9.0 and 10.4 < y < 12.2:      # окно выброса гильз
            edge = min(z - 6.2, 9.0 - z, y - 10.4, 12.2 - y)
            c = (74, 78, 84) if edge < 0.22 else (14, 15, 17)
            if edge >= 0.22 and 7.0 < z < 8.4 and 10.6 < y < 11.1: c = (96, 74, 30)   # гильза-патрон в патроннике
        if face == 'west' and 5.0 < z < 9.2 and 10.75 < y < 11.0 and int(z * 2.5) % 2 == 0:
            c = sh(c, 38)                                              # гравировка
        if face == 'west' and 7.0 < z < 7.5 and 11.4 < y < 11.7: c = (150, 40, 34)     # красная метка
    if face == 'up':
        if abs(x - 8) < 0.25: c = sh(c, -6)
    if e < 0.22: c = sh(c, 24 if face != 'down' else -10)
    return c

def mat_poly(face, p, e, ctx):
    c = sh((124, 104, 76), (pn(*[round(v * 5) for v in p]) - .5) * 9)
    x, y, z = p
    if ctx.get('grip') and face in ('east', 'west', 'north', 'south'):
        k = int(math.floor(z * 3)) + int(math.floor(y * 3))
        if k % 2: c = sh(c, -12)
    if ctx.get('rail') and face == 'down' and 2.6 < z < 8.8 and int((z - 2.6) / 0.7) % 2 == 0: c = sh(c, -28)
    if ctx.get('rail') and face in ('east', 'west') and 3.0 < z < 8.4 and 8.5 < y < 9.1 and int((z - 3.0) / 0.9) % 2 == 0: c = sh(c, -22)
    if e < 0.2: c = sh(c, 14)
    return c

def mat_poly_dark(face, p, e, ctx):
    c = sh((54, 48, 40), (pn(*[round(v * 5) for v in p]) - .5) * 7)
    if e < 0.2: c = sh(c, 16)
    return c

def mat_steel(face, p, e, ctx):
    c = sh((96, 100, 106), (pn(round(p[0] * 2), round(p[1] * 6), round(p[2] * 2)) - .5) * 14)
    if e < 0.2: c = sh(c, 26)
    return c

def mat_dark(face, p, e, ctx):
    c = sh((26, 28, 30), (pn(*[round(v * 4) for v in p]) - .5) * 5)
    if e < 0.18: c = sh(c, 14)
    return c

def mat_muzzle(face, p, e, ctx):
    c = mat_steel(face, p, e, ctx)
    if face == 'north':
        d = math.hypot(p[0] - 8, p[1] - 11)
        if d < 0.38: c = (6, 6, 8)
        elif d < 0.55: c = (150, 154, 160)
    return c

def mat_lens(face, p, e, ctx):
    if face == 'north':
        d = math.hypot(p[0] - 8, p[1] - 7.65)
        if d < 0.42: return (252, 246, 214)
        if d < 0.6:  return (170, 168, 150)
    return mat_dark(face, p, e, ctx)

def mat_sightdot(face, p, e, ctx):
    c = mat_dark(face, p, e, ctx)
    if face in ('north', 'south') and abs(p[1] - 13.0) < 0.22: c = (236, 236, 224)
    return c

def mat_glove(face, p, e, ctx):
    c = sh((36, 38, 38), (pn(*[round(v * 5) for v in p]) - .5) * 6)
    if int(math.floor(p[2] * 2 + p[1] * 2)) % 3 == 0: c = sh(c, -6)   # прострочка
    if e < 0.18: c = sh(c, 8)
    if ctx.get('knuckle') and face == 'up': c = sh((120, 100, 72), (pn(*[round(v * 4) for v in p]) - .5) * 8)
    return c

def mat_sleeve(face, p, e, ctx):
    x, y, z = p
    n = math.sin(x * 1.9 + z * 0.8) * math.sin(y * 2.3 + z * 1.1) + 0.6 * math.sin(x * 3.1 - z * 1.7 + y)
    pal = [(70, 76, 50), (104, 98, 70), (52, 56, 40), (118, 108, 78)]
    c = pal[0] if n < -0.2 else pal[1] if n < 0.35 else pal[2] if n < 0.8 else pal[3]
    c = sh(c, (pn(*[round(v * 4) for v in p]) - .5) * 8)
    if e < 0.2: c = sh(c, -10)
    return c

MATS = {'slide': mat_slide, 'poly': mat_poly, 'polydark': mat_poly_dark, 'steel': mat_steel, 'dark': mat_dark,
        'muzzle': mat_muzzle, 'lens': mat_lens, 'sight': mat_sightdot, 'glove': mat_glove, 'sleeve': mat_sleeve}

# ------------------------------------------------------------------ геометрия граней
DIRS = ['north', 'east', 'south', 'west', 'up', 'down']
def face_point(frm, to, d, a, b):
    sx, sy, sz = to[0] - frm[0], to[1] - frm[1], to[2] - frm[2]
    if d == 'north': return (to[0] - a * sx, to[1] - b * sy, frm[2])
    if d == 'south': return (frm[0] + a * sx, to[1] - b * sy, to[2])
    if d == 'west':  return (frm[0], to[1] - b * sy, frm[2] + a * sz)
    if d == 'east':  return (to[0], to[1] - b * sy, to[2] - a * sz)
    if d == 'up':    return (frm[0] + a * sx, to[1], frm[2] + b * sz)
    if d == 'down':  return (frm[0] + a * sx, frm[1], to[2] - b * sz)
def face_size(frm, to, d):
    sx, sy, sz = to[0] - frm[0], to[1] - frm[1], to[2] - frm[2]
    return {'north': (sx, sy), 'south': (sx, sy), 'east': (sz, sy), 'west': (sz, sy), 'up': (sx, sz), 'down': (sx, sz)}[d]

class Part:
    def __init__(s, name, frm, to, mat, group='static', rot=None, faces=None, ctx=None, special=None):
        s.name, s.frm, s.to, s.mat, s.group, s.rot = name, list(frm), list(to), mat, group, rot
        s.faces = faces or DIRS; s.ctx = ctx or {}; s.special = special; s.uv = {}

def grip_rot(): return {'origin': [8, 7.4, 9.0], 'axis': 'x', 'angle': -22.5}

def gun_parts():
    P = []
    # --- затвор (двигается)
    P.append(Part('slide', (7.0, 9.7, 2.0), (9.0, 12.6, 13.2), 'slide', 'slide'))
    P.append(Part('front_sight', (7.8, 12.6, 2.3), (8.2, 13.3, 2.9), 'sight', 'slide'))
    P.append(Part('rear_sight_l', (7.15, 12.6, 12.0), (7.65, 13.3, 12.8), 'dark', 'slide'))
    P.append(Part('rear_sight_r', (8.35, 12.6, 12.0), (8.85, 13.3, 12.8), 'dark', 'slide'))
    # --- ствол (неподвижен; при отдаче затвор открывает его)
    P.append(Part('barrel', (7.45, 10.4, 1.1), (8.55, 11.6, 5.0), 'muzzle', 'static'))
    # --- рамка
    P.append(Part('dust_cover', (7.2, 8.2, 2.4), (8.8, 9.7, 9.0), 'poly', 'static', ctx={'rail': True}))
    P.append(Part('frame_mid', (7.1, 6.9, 8.6), (8.9, 9.7, 13.4), 'poly', 'static'))
    P.append(Part('guard_front', (7.4, 6.5, 6.0), (8.6, 8.2, 6.8), 'poly', 'static'))
    P.append(Part('guard_bottom', (7.4, 6.4, 6.0), (8.6, 7.1, 9.2), 'poly', 'static'))
    P.append(Part('trigger', (7.75, 7.1, 7.9), (8.25, 8.5, 8.4), 'steel', 'static', faces=['east', 'west', 'north', 'south', 'up']))
    P.append(Part('light', (7.1, 7.1, 2.9), (8.9, 8.2, 5.9), 'lens', 'static'))
    P.append(Part('grip', (6.9, 2.4, 9.0), (9.1, 7.4, 13.4), 'poly', 'static', rot=grip_rot(), ctx={'grip': True},
                  faces=['north', 'east', 'south', 'west', 'up']))
    P.append(Part('slide_stop', (6.85, 8.95, 6.8), (7.05, 9.45, 9.0), 'steel', 'lever', faces=['north', 'east', 'south', 'west', 'up', 'down']))
    # --- магазин
    P.append(Part('mag_body', (7.2, 2.6, 9.4), (8.8, 7.3, 13.0), 'steel', 'mag', rot=grip_rot()))
    P.append(Part('mag_plate', (6.8, 1.9, 9.2), (9.2, 2.6, 13.6), 'polydark', 'mag', rot=grip_rot()))
    # --- вспышка (спец. текстура)
    P.append(Part('flash_a', (6.4, 9.4, 0.9), (9.6, 12.6, 0.9), 'flash', 'flash', faces=['north', 'south'], special='flash'))
    P.append(Part('flash_b', (8.0, 9.4, -0.9), (8.0, 12.6, 2.5), 'flash', 'flash', faces=['east', 'west'], special='flash'))
    P.append(Part('flash_c', (6.8, 11.0, -0.5), (9.2, 11.0, 2.3), 'flash', 'flash', faces=['up', 'down'], special='flash'))
    return P

def hand_parts():
    P = []
    R = grip_rot()
    # правая рука (опорная перчатка на хвате) — неподвижна
    for k in range(4):
        y0 = 3.2 + k * 1.1
        P.append(Part(f'finger{k}', (6.45, y0, 8.45), (9.3, y0 + 1.0, 11.0), 'glove', 'right', rot=R, faces=['north', 'west', 'south', 'up', 'down', 'east']))
    P.append(Part('r_palm', (9.0, 3.0, 10.2), (10.5, 7.7, 14.4), 'glove', 'right', rot=R))
    P.append(Part('r_hand_back', (8.0, 6.6, 11.8), (10.6, 9.6, 15.0), 'glove', 'right', ctx={'knuckle': True}))
    P.append(Part('r_thumb', (6.55, 7.25, 5.4), (7.12, 8.35, 10.4), 'glove', 'right'))
    P.append(Part('r_wrist', (7.7, 6.2, 14.8), (10.5, 9.6, 17.0), 'glove', 'right'))
    P.append(Part('r_sleeve', (7.2, 5.4, 16.8), (11.0, 10.2, 31.5), 'sleeve', 'right',
                  rot={'origin': [9, 7.8, 16.8], 'axis': 'x', 'angle': 22.5}))
    return P

def left_hand(kind):
    """kind: 'idle' | 'mag' | 'away' | 'plate' | 'slide'. -> список Part"""
    P = []; R = grip_rot()
    if kind == 'idle':
        P.append(Part('l_palm', (5.0, 3.0, 8.8), (6.8, 8.2, 12.6), 'glove', 'left', rot=R))
        for k in range(3):
            y0 = 3.1 + k * 1.25
            P.append(Part(f'l_finger{k}', (6.3, y0, 7.5), (9.7, y0 + 1.15, 8.5), 'glove', 'left', rot=R))
        P.append(Part('l_thumb', (6.2, 7.9, 3.8), (6.95, 8.9, 9.0), 'glove', 'left'))
        P.append(Part('l_sleeve', (3.2, 2.4, 12.2), (6.4, 6.8, 28.5), 'sleeve', 'left',
                      rot={'origin': [5, 4.6, 12.2], 'axis': 'x', 'angle': 22.5}))
    elif kind in ('mag', 'plate'):
        d = 0.0 if kind == 'mag' else 2.6
        dz, dy = 0.383 * d, -0.924 * d
        P.append(Part('l_cup', (5.7, 0.3 + dy, 9.2), (10.3, 3.0 + dy, 14.0), 'glove', 'left', rot={'origin': [8, 7.4 + dy, 9.0], 'axis': 'x', 'angle': -22.5}))
        P.append(Part('l_cup_t', (5.5, 2.4 + dy, 9.6), (6.2, 4.6 + dy, 12.6), 'glove', 'left', rot={'origin': [8, 7.4 + dy, 9.0], 'axis': 'x', 'angle': -22.5}))
        P.append(Part('l_sleeve', (3.0, -1.5 + dy, 12.0), (6.2, 2.5 + dy, 28.5), 'sleeve', 'left',
                      rot={'origin': [5, 0.5 + dy, 12.0], 'axis': 'x', 'angle': 22.5}))
    elif kind == 'slide':
        P.append(Part('l_palm', (5.7, 9.1, 5.6), (7.0, 12.8, 11.4), 'glove', 'left'))
        P.append(Part('l_fingers', (6.0, 12.6, 6.4), (8.9, 13.6, 10.8), 'glove', 'left'))
        P.append(Part('l_thumb', (7.0, 9.0, 9.6), (7.9, 9.7, 12.4), 'glove', 'left'))
        P.append(Part('l_sleeve', (2.6, 8.0, 10.6), (6.2, 13.0, 27.5), 'sleeve', 'left',
                      rot={'origin': [4.5, 10, 10.6], 'axis': 'x', 'angle': 22.5}))
    return P

# ------------------------------------------------------------------ атлас
class Atlas:
    def __init__(s, name):
        s.name = name; s.img = np.zeros((ATLAS, ATLAS, 4), np.uint8); s.x = 1; s.y = 1; s.rowh = 0
    def alloc(s, w, h):
        w, h = int(w), int(h)
        if s.x + w + 2 > ATLAS: s.x = 1; s.y += s.rowh + 2; s.rowh = 0
        assert s.y + h + 1 <= ATLAS, f'атлас {s.name} переполнен'
        r = (s.x, s.y, w, h); s.x += w + 2; s.rowh = max(s.rowh, h); return r

def paint_flash(atlas, rect):
    x0, y0, w, h = rect
    for j in range(h):
        for i in range(w):
            dx, dy = (i + .5) / w * 2 - 1, (j + .5) / h * 2 - 1
            r = math.hypot(dx, dy); ang = math.atan2(dy, dx)
            star = 0.35 + 0.65 * abs(math.cos(ang * 2.5 + 0.4)) ** 3     # лучи
            lim = 0.95 * star
            if r < lim:
                t = r / lim
                col = mix((255, 252, 220), (255, 150, 40), t ** 0.8)
                a = int(255 * (1 - t ** 3))
                atlas.img[y0 + j, x0 + i] = (*col, max(0, min(255, a)))

def build_atlas(parts, name, tex_path, tex_ref, dens=DENS):
    at = Atlas(name)
    flash_rect = None
    for p in parts:
        for d in p.faces:
            fw, fh = face_size(p.frm, p.to, d)
            if p.special == 'flash':
                if flash_rect is None:
                    flash_rect = at.alloc(24, 24); paint_flash(at, flash_rect)
                x0, y0, w, h = flash_rect; p.uv[d] = (x0 / UVS, y0 / UVS, (x0 + w) / UVS, (y0 + h) / UVS); continue
            if fw < 1e-6 or fh < 1e-6: continue
            w = max(1, int(math.ceil(fw * dens))); h = max(1, int(math.ceil(fh * dens)))
            x0, y0, w, h = at.alloc(w, h)
            for j in range(h):
                for i in range(w):
                    a, b = (i + .5) / w, (j + .5) / h
                    pt = face_point(p.frm, p.to, d, a, b)
                    e = min(min(a, 1 - a) * fw, min(b, 1 - b) * fh)
                    c = MATS[p.mat](d, pt, e, p.ctx)
                    at.img[y0 + j, x0 + i] = (c[0], c[1], c[2], 255)
            p.uv[d] = (x0 / UVS, y0 / UVS, (x0 + w) / UVS, (y0 + h) / UVS)
    Image.fromarray(at.img, 'RGBA').save(tex_path)
    return at

# ------------------------------------------------------------------ состояния -> JSON
def part_to_element(p, T):
    dx, dy, dz = T
    e = {'name': p.name, 'from': [round(p.frm[0] + dx, 4), round(p.frm[1] + dy, 4), round(p.frm[2] + dz, 4)],
         'to': [round(p.to[0] + dx, 4), round(p.to[1] + dy, 4), round(p.to[2] + dz, 4)]}
    if p.rot:
        o = p.rot['origin']; e['rotation'] = {'angle': p.rot['angle'], 'axis': p.rot['axis'],
                                              'origin': [round(o[0] + dx, 4), round(o[1] + dy, 4), round(o[2] + dz, 4)]}
    e['faces'] = {d: {'uv': [round(v, 4) for v in p.uv[d]], 'texture': '#0'} for d in p.faces if d in p.uv}
    return e

# состояние -> (смещение затвора, смещение магазина вдоль хвата d, магазин есть?, вспышка, рычаг поднят)
STATES = {
    0: dict(slide=0.0, mag=0.0, magon=True, flash=False, lever=False),
    1: dict(slide=2.6, mag=0.0, magon=True, flash=True, lever=False),
    2: dict(slide=1.2, mag=0.0, magon=True, flash=False, lever=False),
    3: dict(slide=2.6, mag=0.0, magon=True, flash=False, lever=True),
    4: dict(slide=0.0, mag=2.4, magon=True, flash=False, lever=False),
    5: dict(slide=0.0, mag=0.0, magon=False, flash=False, lever=False),
    6: dict(slide=0.0, mag=2.6, magon=True, flash=False, lever=False),
    7: dict(slide=2.6, mag=0.0, magon=True, flash=False, lever=False),
    8: dict(slide=1.2, mag=0.0, magon=True, flash=False, lever=False),
}
HAND_STATES = {  # индекс руки -> (вид левой руки, смещение затвора для руки)
    0: ('away', 0), 1: ('mag', 0), 2: ('away', 0), 3: ('plate', 0), 4: ('slide', 2.6), 5: ('slide', 1.2)}

def state_elements(parts, s):
    els = []
    for p in parts:
        T = (0, 0, 0)
        if p.group == 'slide': T = (0, 0, s['slide'])
        elif p.group == 'lever': T = (0, 0.45 if s['lever'] else 0, s['slide'] if s['lever'] else 0)
        elif p.group == 'mag':
            if not s['magon']: continue
            d = s['mag']; T = (0, -0.924 * d, 0.383 * d)
        elif p.group == 'flash':
            if not s['flash']: continue
        els.append(part_to_element(p, T))
    return els

def hand_elements(hparts, kind_parts, shift):
    els = [part_to_element(p, (0, 0, 0)) for p in hparts]
    els += [part_to_element(p, (0, 0, shift)) for p in kind_parts]
    return els

# Параметры отображения (подбираются по превью)
DISPLAY = {
    'gui': {'rotation': [20, -135, 0], 'translation': [0, 0, 0], 'scale': [1.15, 1.15, 1.15]},
    'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.55, 0.55, 0.55]},
    'fixed': {'rotation': [0, 90, 0], 'translation': [0, 0, 0], 'scale': [1.0, 1.0, 1.0]},
    'thirdperson_righthand': {'rotation': [0, 0, 0], 'translation': [0, 3.0, -3.0], 'scale': [0.85, 0.85, 0.85]},
    'thirdperson_lefthand': {'rotation': [0, 0, 0], 'translation': [0, 3.0, -3.0], 'scale': [0.85, 0.85, 0.85]},
    'firstperson_righthand': {'rotation': [0, 4, 0], 'translation': [-1.5, -0.5, 0], 'scale': [0.75, 0.75, 0.75]},
    'firstperson_lefthand': {'rotation': [0, -4, 0], 'translation': [1.5, -0.5, 0], 'scale': [0.75, 0.75, 0.75]},
    'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [0.8, 0.8, 0.8]},
}
def load_display():
    p = os.path.join(os.path.dirname(__file__), 'pistol_display.json')
    if os.path.exists(p):
        return json.load(open(p))
    return DISPLAY

def write(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f: json.dump(obj, f, indent=1, ensure_ascii=False); f.write('\n')

def main():
    disp = load_display()
    # --- оружие
    gp = gun_parts()
    tex_dir = os.path.join(RES, 'textures/item'); os.makedirs(tex_dir, exist_ok=True)
    build_atlas(gp, 'gun', os.path.join(tex_dir, 'pistol_atlas.png'), None)
    gtex = {'0': f'{MOD}:item/pistol_atlas', 'particle': f'{MOD}:item/pistol_atlas'}
    for sid, s in STATES.items():
        m = {'textures': gtex, 'elements': state_elements(gp, s), 'display': disp, 'gui_light': 'side'}
        if sid == 0:
            ov = [{'predicate': {f'{MOD}:gun_state': k}, 'model': f'{MOD}:item/pistol/state_{k}'} for k in range(1, 9)]
            ov += [{'predicate': {f'{MOD}:gun_state': 100 + k}, 'model': f'{MOD}:item/pistol/hands_{k}'} for k in HAND_STATES]
            m['overrides'] = ov
            write(os.path.join(RES, 'models/item/pulse_sidearm.json'), m)
        write(os.path.join(RES, f'models/item/pistol/state_{sid}.json'), m)
    # --- руки (общий атлас перчаток/рукавов)
    hp = hand_parts()
    all_left = {k: left_hand(k) for k in ('idle', 'mag', 'plate', 'slide')}
    uniq = hp + [p for k in all_left.values() for p in k]
    build_atlas(uniq, 'hands', os.path.join(tex_dir, 'pistol_hands.png'), None, dens=2)
    htex = {'0': f'{MOD}:item/pistol_hands', 'particle': f'{MOD}:item/pistol_hands'}
    for hid, (kind, shift) in HAND_STATES.items():
        kp = all_left.get(kind, [])
        m = {'textures': htex, 'elements': hand_elements(hp, kp, shift), 'display': disp}
        write(os.path.join(RES, f'models/item/pistol/hands_{hid}.json'), m)
    print('pistol: states', len(STATES), 'hand poses', len(HAND_STATES))

if __name__ == '__main__':
    main()
