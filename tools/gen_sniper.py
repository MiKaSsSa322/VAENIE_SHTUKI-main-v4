"""Снайперская винтовка с оптическим прицелом. Ствол в -Z."""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import gen_pistol as gp, gunlib
from gen_pistol import Part, pn, sh, mix
import gen_ak74  # материалы wood/plum/blued/brake регистрируются при импорте

def mat_odpoly(face, p, e, ctx):
    c = sh((74, 84, 58), (pn(round(p[0] * 4), round(p[1] * 4), round(p[2] * 4)) - .5) * 9)
    if (int(p[2] * 3) + int(p[1] * 3)) % 2 and face in ('east', 'west'): c = sh(c, -7)
    if e < 0.2: c = sh(c, 14)
    return c
def mat_scope(face, p, e, ctx):
    c = sh((30, 32, 34), (pn(round(p[0] * 4), round(p[1] * 4), round(p[2] * 4)) - .5) * 5)
    if face == 'north' and ctx.get('lens'):
        d = math.hypot(p[0] - 8, p[1] - 14.0)
        if d < 0.8: return mix((60, 40, 120), (30, 110, 120), min(1, d / 0.8))
        if d < 0.95: return (110, 112, 116)
    if face == 'south' and ctx.get('eye'):
        d = math.hypot(p[0] - 8, p[1] - 14.0)
        if d < 0.55: return (10, 10, 14)
    if face in ('east', 'west') and ctx.get('rings') and int(p[2] * 2) % 3 == 0: c = sh(c, 14)
    if e < 0.2: c = sh(c, 12)
    return c
gp.MATS.update({'odpoly': mat_odpoly, 'scope': mat_scope})

def mr(): return {'origin': [8, 10.0, 22.0], 'axis': 'x', 'angle': -22.5}
def gun_parts():
    P = []
    P.append(Part('brake', (7.1, 10.1, -8.0), (8.9, 11.9, -5.2), 'brake'))
    P.append(Part('barrel', (7.35, 10.35, -5.2), (8.65, 11.65, 10.0), 'blued'))
    P.append(Part('forend', (6.9, 8.4, 2.0), (9.1, 10.4, 14.0), 'odpoly'))
    P.append(Part('bipod_l', (6.5, 7.0, 0.0), (7.0, 8.6, 5.5), 'steel'))
    P.append(Part('bipod_r', (9.0, 7.0, 0.0), (9.5, 8.6, 5.5), 'steel'))
    P.append(Part('receiver', (6.9, 10.0, 10.0), (9.1, 12.6, 20.0), 'blued', ctx={'port': True, 'rivets': False}))
    P.append(Part('rail', (7.3, 12.6, 10.5), (8.7, 13.1, 19.5), 'dark'))
    P.append(Part('guard_f', (7.4, 8.2, 18.0), (8.6, 10.0, 18.7), 'blued'))
    P.append(Part('guard_b', (7.4, 8.2, 18.0), (8.6, 8.9, 22.0), 'blued'))
    P.append(Part('guard_r', (7.4, 8.2, 21.3), (8.6, 10.0, 22.0), 'blued'))
    P.append(Part('trigger', (7.8, 8.9, 19.6), (8.2, 10.0, 20.1), 'steel', faces=['east', 'west', 'north', 'south', 'up']))
    P.append(Part('grip', (7.2, 4.4, 22.0), (8.8, 10.0, 25.0), 'odpoly', rot=mr(), faces=['north', 'east', 'south', 'west', 'up']))
    P.append(Part('stock_a', (7.1, 8.6, 22.0), (8.9, 11.6, 26.0), 'odpoly'))
    P.append(Part('cheek', (7.2, 11.6, 22.5), (8.8, 12.6, 26.0), 'odpoly'))
    P.append(Part('stock_b', (7.1, 7.2, 26.0), (8.9, 11.2, 29.0), 'odpoly'))
    P.append(Part('pad', (7.0, 7.0, 29.0), (9.0, 11.4, 29.7), 'dark'))
    # оптика
    P.append(Part('scope_tube', (7.35, 13.35, 10.0), (8.65, 14.65, 20.0), 'scope', ctx={'rings': True}))
    P.append(Part('scope_obj', (7.0, 13.0, 6.5), (9.0, 15.0, 10.0), 'scope', ctx={'lens': True}))
    P.append(Part('scope_eye', (7.2, 13.2, 20.0), (8.8, 14.8, 23.0), 'scope', ctx={'eye': True}))
    P.append(Part('ring_f', (7.2, 13.0, 11.0), (8.8, 14.9, 12.0), 'dark'))
    P.append(Part('ring_r', (7.2, 13.0, 18.0), (8.8, 14.9, 19.0), 'dark'))
    P.append(Part('turret_e', (7.6, 14.65, 14.0), (8.4, 15.5, 15.2), 'dark'))
    P.append(Part('turret_w', (8.65, 13.6, 14.0), (9.5, 14.4, 15.2), 'dark'))
    P.append(Part('handle_arm', (9.1, 11.1, 16.2), (10.4, 11.7, 17.0), 'steel', 'handle'))
    P.append(Part('handle_knob', (10.2, 10.7, 15.8), (11.3, 11.9, 17.4), 'dark', 'handle'))
    P.append(Part('mag_body', (7.4, 6.5, 12.0), (8.6, 10.2, 17.0), 'dark', 'mag', faces=['north', 'east', 'south', 'west', 'down']))
    P.append(Part('mag_plate', (7.2, 6.1, 11.8), (8.8, 6.5, 17.2), 'polydark', 'mag'))
    P.append(Part('flash_a', (6.0, 9.0, -8.8), (10.0, 13.0, -8.8), 'flash', 'flash', faces=['north', 'south'], special='flash'))
    P.append(Part('flash_b', (8.0, 9.0, -11.5), (8.0, 13.0, -6.0), 'flash', 'flash', faces=['east', 'west'], special='flash'))
    P.append(Part('flash_c', (6.0, 11.0, -11.5), (10.0, 11.0, -6.0), 'flash', 'flash', faces=['up', 'down'], special='flash'))
    return P

def hand_parts():
    P = []; R = mr()
    for k in range(3):
        y0 = 4.8 + k * 1.15
        P.append(Part(f'finger{k}', (6.5, y0, 21.0), (9.5, y0 + 1.0, 23.8), 'glove', 'right', rot=R))
    P.append(Part('r_palm', (9.0, 5.0, 23.0), (10.4, 9.6, 26.4), 'glove', 'right', rot=R))
    P.append(Part('r_back', (8.4, 9.0, 23.6), (10.6, 11.6, 27.0), 'glove', 'right', ctx={'knuckle': True}))
    P.append(Part('r_thumb', (6.5, 10.0, 20.5), (7.1, 11.0, 24.0), 'glove', 'right'))
    P.append(Part('r_wrist', (7.9, 8.0, 27.0), (10.4, 11.6, 28.8), 'glove', 'right'))
    P.append(Part('r_sleeve', (7.5, 7.2, 28.6), (11.0, 12.0, 31.9), 'sleeve', 'right', rot={'origin': [9, 9.6, 28.6], 'axis': 'x', 'angle': 22.5}))
    return P
def lefts():
    return {
     'idle': [Part('l_palm', (6.2, 6.6, 3.0), (9.8, 8.4, 9.5), 'glove', 'left'), Part('l_side', (5.7, 8.4, 3.0), (6.8, 10.8, 9.2), 'glove', 'left'),
              Part('l_thumb', (9.2, 8.8, 3.4), (10.2, 10.6, 8.6), 'glove', 'left'),
              Part('l_sleeve', (2.4, 3.0, 8.8), (6.0, 8.0, 31.0), 'sleeve', 'left', rot={'origin': [4, 5.6, 8.8], 'axis': 'x', 'angle': 22.5})],
     'mag': [Part('l_cup', (6.1, 3.2, 11.0), (9.9, 7.2, 17.8), 'glove', 'left'),
             Part('l_sleeve', (2.6, 0.5, 13.0), (6.0, 5.0, 31.0), 'sleeve', 'left', rot={'origin': [4, 2.8, 13.0], 'axis': 'x', 'angle': 22.5})],
     'plate': [Part('l_cup', (6.1, 0.4, 11.0), (9.9, 4.4, 17.8), 'glove', 'left'),
               Part('l_sleeve', (2.6, -2.2, 13.0), (6.0, 2.2, 31.0), 'sleeve', 'left', rot={'origin': [4, 0, 13.0], 'axis': 'x', 'angle': 22.5})],
     'slide': [Part('l_fingers', (9.0, 10.4, 14.5), (11.2, 12.6, 18.2), 'glove', 'left'), Part('l_bridge', (6.0, 15.0, 14.0), (11.0, 15.8, 18.0), 'sleeve', 'left'),
               Part('l_sleeve', (2.8, 11.0, 14.6), (5.8, 16.0, 28.5), 'sleeve', 'left', rot={'origin': [4, 13, 14.6], 'axis': 'x', 'angle': 22.5})]}

STATES = {0: dict(bolt=0, mag=0, magon=True, flash=False), 1: dict(bolt=0, mag=0, magon=True, flash=True),
          2: dict(bolt=0, mag=0, magon=True, flash=False), 3: dict(bolt=0, mag=0, magon=True, flash=False),
          4: dict(bolt=0, mag=2.6, magon=True, flash=False), 5: dict(bolt=0, mag=0, magon=False, flash=False),
          6: dict(bolt=0, mag=3.2, magon=True, flash=False), 7: dict(bolt=3.2, mag=0, magon=True, flash=False),
          8: dict(bolt=1.6, mag=0, magon=True, flash=False)}
HANDS = {0: ('idle', 0), 1: ('mag', 0), 2: ('away', 0), 3: ('plate', 0), 4: ('slide', 3.2), 5: ('slide', 1.6)}

def state_elements(parts, s):
    els = []
    for p in parts:
        T = (0, 0, 0)
        if p.group == 'handle': T = (0, 0, s['bolt'])
        elif p.group == 'mag':
            if not s['magon']: continue
            T = (0, -s['mag'], 0)
        elif p.group == 'flash' and not s['flash']: continue
        els.append(gp.part_to_element(p, T))
    return els

if __name__ == '__main__':
    gunlib.generate('sniper', gun_parts(), hand_parts(), lefts(), STATES, HANDS, state_elements, atlas=512, dens=3, grip=(8, 6, 23.5), s=0.5)
