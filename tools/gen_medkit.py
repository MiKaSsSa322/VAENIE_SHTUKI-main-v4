"""Руки от первого лица для аптечки: перематывание предплечья бинтом, 7 стадий (use_0..use_6)."""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
import gen_pistol as gp
from gen_pistol import Part, pn, sh, mix, MOD, RES, write, part_to_element
from tune_fp import solve
import numpy as np

def mat_skin(face, p, e, ctx):
    c = sh((212, 168, 134), (pn(round(p[0] * 3), round(p[1] * 3), round(p[2] * 3)) - .5) * 8)
    if e < 0.2: c = sh(c, -12)
    return c
def mat_gauze(face, p, e, ctx):
    c = (232, 228, 214)
    if int(p[0] * 3 + p[1] * 2) % 2 == 0: c = sh(c, -10)
    if face in ('north', 'south') and abs(p[1] - 8) < 0.2: c = sh(c, -6)
    if e < 0.18: c = sh(c, -22)
    if ctx.get('blood') and pn(round(p[0]), round(p[1]), 3) > 0.86: c = (178, 70, 60)
    return c
def mat_cross(face, p, e, ctx):
    c = (236, 234, 224)
    u, v = (p[0] - 4.25) / 2.5, (p[2] - 8) / 3.0
    if abs(u) < 0.2 and abs(v) < 0.8 or abs(v) < 0.2 and abs(u) < 0.5: c = (196, 40, 36)
    return c
gp.MATS.update({'skin': mat_skin, 'gauze': mat_gauze, 'cross': mat_cross})

XR = 8.5
def parts():
    P = []
    P.append(Part('sleeve_l', (-9, 5.2, 5.2), (0.2, 10.4, 10.8), 'sleeve', 'static'))
    P.append(Part('forearm', (0, 6, 6), (9.2, 9.6, 10), 'skin', 'static'))
    P.append(Part('hand_l', (9.2, 5.6, 5.6), (13, 10, 10.4), 'skin', 'static'))
    P.append(Part('thumb_l', (9.6, 9.8, 6.6), (11.8, 11, 8.6), 'skin', 'static'))
    for i in range(6):
        P.append(Part(f'wrap{i}', (XR - 1.3 * (i + 1), 5.6, 5.6), (XR - 1.3 * i, 10, 10.4), 'gauze', f'wrap{i}', ctx={'blood': i == 2}))
    P.append(Part('patch', (3.0, 10.0, 6.5), (5.5, 10.1, 9.5), 'cross', 'patch', faces=['up']))
    P.append(Part('roll', (XR - 1.2, 10.5, 6.2), (XR + 1.2, 13.0, 9.8), 'gauze', 'move'))
    P.append(Part('strip', (XR - 0.4, 9.9, 6.8), (XR + 0.4, 10.6, 9.2), 'gauze', 'move'))
    P.append(Part('r_fingers', (XR - 1.8, 13.0, 5.8), (XR + 1.8, 14.4, 10.2), 'glove', 'move'))
    P.append(Part('r_palm', (XR - 0.4, 14.4, 6.0), (XR + 3.4, 16.4, 10.0), 'glove', 'move'))
    P.append(Part('r_sleeve', (XR + 1.5, 15.0, 5.6), (XR + 7.0, 19.5, 10.4), 'sleeve', 'move', rot={'origin': [XR + 1.5, 15.5, 8], 'axis': 'z', 'angle': -22.5}))
    return P

def main():
    gp.ATLAS = 256; gp.UVS = 16.0
    P = parts()
    gp.build_atlas(P, 'medkit', os.path.join(RES, 'textures/item/medkit_hands.png'), None, dens=3)
    # display: рука с бинтом — левое нижнее поле кадра, предплечье уходит влево-вниз
    d, a, b, cost = solve((13, 8, 8), (-7, 8, 8), np.array([0.10, -0.12]), np.array([-0.70, -0.60]), [0, 0, 0, 12, 8, 0.7], roll=0)
    d = {k: [round(float(v), 3) for v in vals] for k, vals in d.items()}
    disp = {'firstperson_righthand': d, 'firstperson_lefthand': d}
    tex = {'0': f'{MOD}:item/medkit_hands', 'particle': f'{MOD}:item/medkit_hands'}
    for k in range(7):
        els = []
        for p in P:
            T = (0, 0, 0)
            if p.group.startswith('wrap'):
                if int(p.group[4:]) >= k: continue
            elif p.group == 'patch':
                if k < 6: continue
            elif p.group == 'move': T = (-1.3 * k, 0, 0)
            els.append(part_to_element(p, T))
        write(os.path.join(RES, f'models/item/medkit/use_{k}.json'), {'textures': tex, 'elements': els, 'display': disp})
    m = {'parent': 'minecraft:item/generated', 'textures': {'layer0': f'{MOD}:item/medkit'},
         'overrides': [{'predicate': {f'{MOD}:med_state': 100 + k}, 'model': f'{MOD}:item/medkit/use_{k}'} for k in range(7)]}
    write(os.path.join(RES, 'models/item/medkit.json'), m)
    print('medkit hands ok', d)

if __name__ == '__main__':
    main()
