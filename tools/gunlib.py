"""Общая библиотека генерации 3D-оружия (снайперская, дробовик): атлас, состояния, руки, display."""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
import gen_pistol as gp
from gen_pistol import Part, pn, sh, mix, DIRS, MOD, RES, write, part_to_element
from preview import model_quads, mat_rxyz, mat_t

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

def base_display(quads, grip, s):
    tp = [0, round(-s * (grip[1] - 8), 3), round(-s * (grip[2] - 8), 3)]
    d = {'gui': fit_gui(quads, [16, -125, 0]),
         'ground': {'rotation': [0, 0, 0], 'translation': [0, 2, 0], 'scale': [0.4] * 3},
         'fixed': fit_gui(quads, [0, 90, 0], 1.45),
         'thirdperson_righthand': {'rotation': [0, 0, 0], 'translation': tp, 'scale': [s] * 3},
         'thirdperson_lefthand': {'rotation': [0, 0, 0], 'translation': tp, 'scale': [s] * 3},
         'firstperson_righthand': {'rotation': [4, 7, 0], 'translation': [-8, 3, -9], 'scale': [s] * 3},
         'firstperson_lefthand': {'rotation': [4, -7, 0], 'translation': [8, 3, -9], 'scale': [s] * 3},
         'head': {'rotation': [0, 0, 0], 'translation': [0, 0, 0], 'scale': [0.6] * 3}}
    d['fixed']['translation'][2] = 0
    return d

def generate(name, parts, hand_parts, lefts, STATES, HANDS, state_elements, atlas=512, dens=3, grip=(8, 5, 20), s=0.55, extra_hand_parts=()):
    gp.ATLAS = atlas; gp.UVS = atlas / 16.0
    tex_dir = os.path.join(RES, 'textures/item')
    gp.build_atlas(parts, name, os.path.join(tex_dir, f'{name}_atlas.png'), None, dens=dens)
    els0 = state_elements(parts, STATES[0])
    quads = model_quads({'textures': {'0': f'{MOD}:item/{name}_atlas'}, 'elements': els0})
    disp = base_display(quads, grip, s)
    p = os.path.join(os.path.dirname(__file__), f'{name}_display.json')
    if os.path.exists(p): disp.update(json.load(open(p)))
    gtex = {'0': f'{MOD}:item/{name}_atlas', 'particle': f'{MOD}:item/{name}_atlas'}
    for sid, st in STATES.items():
        m = {'textures': gtex, 'elements': state_elements(parts, st), 'display': disp, 'gui_light': 'side'}
        if sid == 0:
            ov = [{'predicate': {f'{MOD}:gun_state': k}, 'model': f'{MOD}:item/{name}/state_{k}'} for k in range(1, 9)]
            ov += [{'predicate': {f'{MOD}:gun_state': 100 + k}, 'model': f'{MOD}:item/{name}/hands_{k}'} for k in HANDS]
            m['overrides'] = ov
            write(os.path.join(RES, f'models/item/{name}.json'), m)
        write(os.path.join(RES, f'models/item/{name}/state_{sid}.json'), m)
    allp = hand_parts + [q for l in lefts.values() for q in l]
    gp.build_atlas(allp, name + '_h', os.path.join(tex_dir, f'{name}_hands.png'), None, dens=2)
    htex = {'0': f'{MOD}:item/{name}_hands', 'particle': f'{MOD}:item/{name}_hands'}
    for hid, (kind, shift) in HANDS.items():
        els = [part_to_element(q, (0, 0, 0)) for q in hand_parts] + [part_to_element(q, (0, 0, shift)) for q in lefts.get(kind, [])]
        write(os.path.join(RES, f'models/item/{name}/hands_{hid}.json'), {'textures': htex, 'elements': els, 'display': disp})
    print(name, 'OK: states', len(STATES), 'hands', len(HANDS))
