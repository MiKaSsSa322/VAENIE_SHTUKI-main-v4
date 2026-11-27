"""Генератор 3D-модели АК-74: атлас, 9 состояний, 6 поз рук. Ствол направлен в -Z."""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
import gen_pistol as gp
from gen_pistol import Part, pn, sh, mix, DIRS, MOD, RES, write, part_to_element, HAND_STATES
from preview import model_quads, mat_rxyz, mat_t, mat_s, np

# ------------------------------------------------------------------ материалы
def mat_wood(face, p, e, ctx):
    x, y, z = p
    across = y if face in ('east', 'west', 'north', 'south') else x
    grain = math.sin(across * 6.5 + math.sin(z * 0.9) * 1.3 + pn(round(x * 2), round(y * 3), 0) * 2.0)
    c = (152, 94, 50) if grain > -0.2 else (126, 74, 40)
    c = sh(c, (pn(round(x * 3), round(y * 5), round(z * 1.5)) - .5) * 10)
    if grain < -0.78: c = sh(c, -24)
    if ctx.get('grooves') and face in ('east', 'west') and int(z * 1.6) % 2 == 0 and 9.2 < y < 10.8: c = sh(c, -16)
    if e < 0.2: c = sh(c, 14)
    return c

def mat_plum(face, p, e, ctx):
    x, y, z = p
    c = sh((116, 44, 34), (pn(round(x * 3), round(y * 4), round(z * 3)) - .5) * 9)
    if face in ('east', 'west') and int(y * 1.7) % 2 == 0: c = sh(c, -22)            # рёбра магазина
    if face in ('north',) and int(y * 1.7) % 2 == 0: c = sh(c, -14)
    if e < 0.2: c = sh(c, 16)
    return c

def mat_blued(face, p, e, ctx):
    x, y, z = p
    c = sh((38, 42, 46), (pn(round(x * 3), round(y * 4), round(z * 3)) - .5) * 6)
    if face in ('east', 'west'):
        if ctx.get('port') and face == 'east' and 14.0 < z < 18.2 and 10.0 < y < 12.2:
            edge = min(z - 14.0, 18.2 - z, y - 10.0, 12.2 - y)
            return (70, 72, 74) if edge < 0.22 else (10, 10, 12)
        if ctx.get('rivets') and (abs((z * 2) % 5 - 2.5) < 0.35) and (abs(y - 9.3) < 0.3 or abs(y - 12.2) < 0.3): c = (110, 112, 112)
        if ctx.get('ribline') and abs(y - 10.6) < 0.18: c = sh(c, -16)
    if face == 'up' and ctx.get('cover') and int(z * 1.5) % 4 == 0: c = sh(c, -12)
    if e < 0.25: c = mix(c, (96, 98, 100), 0.55)                                     # потёртость на кромках
    return c

def mat_brake(face, p, e, ctx):
    x, y, z = p
    c = sh((52, 56, 60), (pn(round(x * 3), round(y * 4), round(z * 3)) - .5) * 6)
    if face in ('east', 'west') and (-4.9 < z < -4.2 or -3.6 < z < -2.9) and 10.9 < y < 12.1: c = (10, 10, 12)
    if face == 'north':
        d = math.hypot(x - 8, y - 11.5)
        if d < 0.38: c = (6, 6, 8)
        elif d < 0.58: c = (140, 144, 150)
    if e < 0.2: c = sh(c, 18)
    return c

gp.MATS.update({'wood': mat_wood, 'plum': mat_plum, 'blued': mat_blued, 'brake': mat_brake})

# ------------------------------------------------------------------ геометрия
def mag_rot(): return {'origin': [8, 3.8, 15.9], 'axis': 'x', 'angle': 22.5}
def grip_rot(): return {'origin': [8, 8.4, 19.0], 'axis': 'x', 'angle': -22.5}

def gun_parts():
    P = []
    P.append(Part('brake', (7.15, 10.65, -6.0), (8.85, 12.35, -2.6), 'brake'))
    P.append(Part('fs_base', (7.0, 10.3, -2.6), (9.0, 13.0, -0.8), 'blued'))
    P.append(Part('fs_post', (7.8, 13.0, -2.2), (8.2, 14.8, -1.8), 'dark'))
    P.append(Part('fs_ear_l', (7.15, 13.0, -2.5), (7.5, 14.3, -1.2), 'blued', faces=['north', 'east', 'west', 'up']))
    P.append(Part('fs_ear_r', (8.5, 13.0, -2.5), (8.85, 14.3, -1.2), 'blued', faces=['north', 'east', 'west', 'up']))
    P.append(Part('barrel', (7.4, 10.9, -2.6), (8.6, 12.1, 6.0), 'blued'))
    P.append(Part('gas_block', (7.3, 12.1, 4.0), (8.7, 13.2, 5.6), 'blued'))
    P.append(Part('lower_hg', (6.7, 8.8, 2.0), (9.3, 11.4, 11.8), 'wood', ctx={'grooves': True}))
    P.append(Part('upper_hg', (7.1, 12.3, 4.6), (8.9, 14.0, 12.0), 'wood'))
    P.append(Part('rear_sight', (7.3, 13.2, 10.2), (8.7, 14.5, 11.6), 'blued'))
    P.append(Part('rec_front', (6.9, 8.6, 11.8), (9.1, 12.8, 21.5), 'blued', ctx={'port': True, 'rivets': True, 'ribline': True}))
    P.append(Part('dust_cover', (7.0, 12.8, 12.4), (9.0, 14.0, 21.0), 'blued', ctx={'cover': True}))
    P.append(Part('guard_front', (7.4, 6.2, 13.5), (8.6, 8.6, 14.3), 'blued'))
    P.append(Part('guard_bottom', (7.4, 6.2, 13.5), (8.6, 7.0, 18.5), 'blued'))
    P.append(Part('guard_rear', (7.4, 6.2, 17.7), (8.6, 8.6, 18.5), 'blued'))
    P.append(Part('trigger', (7.8, 7.0, 15.6), (8.2, 8.6, 16.1), 'steel', faces=['east', 'west', 'north', 'south', 'up']))
    P.append(Part('pistol_grip', (7.2, 2.2, 19.0), (8.8, 8.4, 22.0), 'polydark', rot=grip_rot(), faces=['north', 'east', 'south', 'west', 'up']))
    P.append(Part('stock_a', (7.1, 8.0, 21.5), (8.9, 12.4, 25.0), 'wood'))
    P.append(Part('stock_b', (7.1, 6.6, 25.0), (8.9, 11.2, 28.2), 'wood'))
    P.append(Part('buttplate', (7.0, 6.3, 28.2), (9.0, 11.5, 28.8), 'dark'))
    P.append(Part('safety', (9.1, 10.0, 13.0), (9.3, 11.0, 19.0), 'steel', faces=['north', 'east', 'south', 'up', 'down']))
    P.append(Part('handle', (9.1, 11.0, 16.0), (10.0, 12.0, 17.5), 'steel', 'handle'))
    P.append(Part('mag_a', (7.3, 3.8, 13.8), (8.7, 8.6, 18.0), 'plum', 'mag', faces=['north', 'east', 'south', 'west', 'down']))
    P.append(Part('mag_b', (7.3, -1.2, 13.8), (8.7, 3.8, 18.0), 'plum', 'mag', rot=mag_rot()))
    P.append(Part('mag_plate', (7.1, -1.6, 13.6), (8.9, -1.2, 18.2), 'polydark', 'mag', rot=mag_rot()))
    P.append(Part('flash_a', (6.0, 9.5, -6.7), (10.0, 13.5, -6.7), 'flash', 'flash', faces=['north', 'south'], special='flash'))
    P.append(Part('flash_b', (8.0, 9.5, -9.2), (8.0, 13.5, -4.0), 'flash', 'flash', faces=['east', 'west'], special='flash'))
    P.append(Part('flash_c', (6.0, 11.5, -9.2), (10.0, 11.5, -4.0), 'flash', 'flash', faces=['up', 'down'], special='flash'))
    return P

def hand_parts():
    P = []; R = grip_rot()
    for k in range(3):
        y0 = 3.2 + k * 1.15
        P.append(Part(f'finger{k}', (6.5, y0, 17.9), (9.5, y0 + 1.0, 20.6), 'glove', 'right', rot=R))
    P.append(Part('r_palm', (9.0, 3.5, 20.0), (10.4, 8.4, 23.6), 'glove', 'right', rot=R))
    P.append(Part('r_back', (8.4, 7.4, 20.8), (10.6, 10.2, 24.4), 'glove', 'right', ctx={'knuckle': True}))
    P.append(Part('r_trigger_finger', (7.0, 7.1, 15.0), (7.7, 8.3, 17.6), 'glove', 'right'))
    P.append(Part('r_thumb', (6.5, 8.2, 17.5), (7.1, 9.2, 21.0), 'glove', 'right'))
    P.append(Part('r_wrist', (7.9, 6.6, 24.2), (10.4, 10.2, 26.4), 'glove', 'right'))
    P.append(Part('r_sleeve', (7.5, 5.8, 26.2), (11.0, 10.6, 31.9), 'sleeve', 'right',
                  rot={'origin': [9, 8, 26.2], 'axis': 'x', 'angle': 22.5}))
    return P

def left_hand(kind):
    P = []
    if kind == 'idle':
        P.append(Part('l_palm', (6.2, 6.8, 3.2), (9.8, 8.8, 9.2), 'glove', 'left'))
        P.append(Part('l_side', (5.7, 8.8, 3.2), (6.7, 12.0, 9.0), 'glove', 'left'))
        P.append(Part('l_top', (6.2, 12.0, 3.4), (8.4, 13.0, 8.4), 'glove', 'left'))
        P.append(Part('l_thumb', (9.3, 9.2, 3.6), (10.3, 11.6, 8.4), 'glove', 'left'))
        P.append(Part('l_sleeve', (2.4, 3.4, 8.6), (6.0, 8.4, 31.5), 'sleeve', 'left',
                      rot={'origin': [4, 6, 8.6], 'axis': 'x', 'angle': 22.5}))
    elif kind in ('mag', 'plate'):
        d = 0.0 if kind == 'mag' else 3.0
        P.append(Part('l_cup', (6.1, -2.8 - d, 12.8), (9.9, 1.2 - d, 18.8), 'glove', 'left'))
        P.append(Part('l_sleeve', (2.6, -4.0 - d, 14.0), (6.0, 0.4 - d, 31.5), 'sleeve', 'left',
                      rot={'origin': [4, -1.5 - d, 14.0], 'axis': 'x', 'angle': 22.5}))
    elif kind == 'slide':
        P.append(Part('l_fingers', (9.0, 10.4, 14.0), (10.9, 12.6, 18.6), 'glove', 'left'))
        P.append(Part('l_bridge', (6.0, 14.2, 13.4), (11.0, 15.0, 17.4), 'sleeve', 'left'))
        P.append(Part('l_sleeve', (2.8, 10.0, 14.6), (5.8, 15.4, 29.0), 'sleeve', 'left',
                      rot={'origin': [4, 12, 14.6], 'axis': 'x', 'angle': 22.5}))
    return P

STATES = {
    0: dict(bolt=0.0, mag=0.0, magon=True, flash=False),
    1: dict(bolt=2.4, mag=0.0, magon=True, flash=True),
    2: dict(bolt=1.2, mag=0.0, magon=True, flash=False),
    3: dict(bolt=2.4, mag=0.0, magon=True, flash=False),
    4: dict(bolt=0.0, mag=2.6, magon=True, flash=False),
    5: dict(bolt=0.0, mag=0.0, magon=False, flash=False),
    6: dict(bolt=0.0, mag=3.2, magon=True, flash=False),
    7: dict(bolt=2.4, mag=0.0, magon=True, flash=False),
    8: dict(bolt=1.2, mag=0.0, magon=True, flash=False),
}
HANDS = {0: ('idle', 0), 1: ('mag', 0), 2: ('away', 0), 3: ('plate', 0), 4: ('slide', 2.4), 5: ('slide', 1.2)}

def state_elements(parts, s):
    els = []
    for p in parts:
        T = (0, 0, 0)
        if p.group == 'handle': T = (0, 0, s['bolt'])
        elif p.group == 'mag':
            if not s['magon']: continue
            T = (0, -s['mag'], 0)
        elif p.group == 'flash' and not s['flash']: continue
        els.append(part_to_element(p, T))
    return els

# ------------------------------------------------------------------ display
def bbox(quads, M):
    pts = []
    for verts, _, _, _ in quads:
        for v in verts:
            p = M @ np.array([v[0] / 16, v[1] / 16, v[2] / 16, 1.0]); pts.append(p[:3])
    a = np.array(pts); return a.min(0), a.max(0)

def fit_gui(quads, rot, fill=0.96):
    M = mat_rxyz(*rot) @ mat_t(-.5, -.5, -.5)
    lo, hi = bbox(quads, M)
    s = fill / max(hi[0] - lo[0], hi[1] - lo[1]); c = (lo + hi) / 2
    return {'rotation': rot, 'translation': [round(-16 * s * c[0], 3), round(-16 * s * c[1], 3), 0], 'scale': [round(s, 4)] * 3}

def build_display(quads):
    s = 0.55
    grip = (8, 5.0, 20.5)             # центр пистолетной рукояти
    c = (8, 8, 8)
    tp = [0, round(-s * (grip[1] - c[1]) , 3), round(-s * (grip[2] - c[2]), 3)]
    fp_r = {'rotation': [4, 7, 0], 'translation': [-4.2, 4.9, -8.5], 'scale': [s] * 3}
    fp_l = {'rotation': [4, -7, 0], 'translation': [4.2, 4.9, -8.5], 'scale': [s] * 3}
    d = {'gui': fit_gui(quads, [16, -125, 0]),
         'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.4, 0.4, 0.4]},
         'fixed': fit_gui(quads, [0, 90, 0], 1.45),
         'thirdperson_righthand': {'rotation': [0, 0, 0], 'translation': tp, 'scale': [s] * 3},
         'thirdperson_lefthand': {'rotation': [0, 0, 0], 'translation': tp, 'scale': [s] * 3},
         'firstperson_righthand': fp_r, 'firstperson_lefthand': fp_l,
         'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [0.6] * 3}}
    d['fixed']['translation'][2] = 0
    p = os.path.join(os.path.dirname(__file__), 'ak74_display.json')
    if os.path.exists(p): d.update(json.load(open(p)))     # ручная подстройка поверх авто-значений
    return d

def main():
    gp.ATLAS = 512; gp.UVS = 512 / 16.0
    parts = gun_parts()
    tex_dir = os.path.join(RES, 'textures/item')
    gp.build_atlas(parts, 'ak', os.path.join(tex_dir, 'ak74_atlas.png'), None, dens=3)
    # квады для расчёта display берём из сгенерированного состояния 0
    probe = {'textures': {'0': f'{MOD}:item/ak74_atlas'}, 'elements': state_elements(parts, STATES[0])}
    for e in probe['elements']:
        for f in e['faces'].values(): f['texture'] = '#0'
    quads = model_quads({'textures': {'0': f'{MOD}:item/ak74_atlas'}, 'elements': probe['elements']})
    disp = build_display(quads)
    gtex = {'0': f'{MOD}:item/ak74_atlas', 'particle': f'{MOD}:item/ak74_atlas'}
    for sid, s in STATES.items():
        m = {'textures': gtex, 'elements': state_elements(parts, s), 'display': disp, 'gui_light': 'side'}
        if sid == 0:
            ov = [{'predicate': {f'{MOD}:gun_state': k}, 'model': f'{MOD}:item/ak74/state_{k}'} for k in range(1, 9)]
            ov += [{'predicate': {f'{MOD}:gun_state': 100 + k}, 'model': f'{MOD}:item/ak74/hands_{k}'} for k in HANDS]
            m['overrides'] = ov
            write(os.path.join(RES, 'models/item/ak74.json'), m)
        write(os.path.join(RES, f'models/item/ak74/state_{sid}.json'), m)
    hp = hand_parts(); lefts = {k: left_hand(k) for k in ('idle', 'mag', 'plate', 'slide')}
    uniq = hp + [p for l in lefts.values() for p in l]
    gp.build_atlas(uniq, 'ak_hands', os.path.join(tex_dir, 'ak74_hands.png'), None, dens=2)
    htex = {'0': f'{MOD}:item/ak74_hands', 'particle': f'{MOD}:item/ak74_hands'}
    for hid, (kind, shift) in HANDS.items():
        els = [part_to_element(p, (0, 0, 0)) for p in hp] + [part_to_element(p, (0, 0, shift)) for p in lefts.get(kind, [])]
        write(os.path.join(RES, f'models/item/ak74/hands_{hid}.json'), {'textures': htex, 'elements': els, 'display': disp})
    print('ak74: states', len(STATES), 'hands', len(HANDS), 'atlas OK')

if __name__ == '__main__':
    main()
