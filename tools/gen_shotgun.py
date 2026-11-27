"""Помповый дробовик (5 патронов). Ствол в -Z; подвижное цевьё — группа 'handle'."""
import os, sys, math
sys.path.insert(0, os.path.dirname(__file__))
import gen_pistol as gp, gunlib
from gen_pistol import Part, pn, sh, mix
import gen_ak74  # wood / blued / brake

def mat_shell(face, p, e, ctx):
    if p[2] < (ctx.get('zb', 0)) or False: pass
    c = sh((176, 40, 36), (pn(round(p[0] * 4), round(p[1] * 4), round(p[2] * 4)) - .5) * 8)
    if p[1] < ctx.get('ybrass', 6.9) + 0.45: c = (206, 168, 66)           # латунное донце
    if e < 0.15: c = sh(c, 14)
    return c
gp.MATS['shell'] = mat_shell

def gun_parts():
    P = []
    P.append(Part('barrel', (7.4, 11.0, -6.0), (8.6, 12.2, 10.0), 'blued'))
    P.append(Part('bead', (7.85, 12.2, -5.8), (8.15, 12.8, -5.4), 'steel'))
    P.append(Part('mag_tube', (7.5, 9.6, -4.0), (8.5, 10.8, 10.0), 'blued'))
    P.append(Part('tube_cap', (7.4, 9.5, -4.4), (8.6, 10.9, -4.0), 'dark'))
    P.append(Part('forend', (6.8, 8.6, 2.0), (9.2, 10.8, 9.0), 'wood', 'handle', ctx={'grooves': True}))
    P.append(Part('receiver', (6.9, 9.0, 10.0), (9.1, 12.8, 17.0), 'blued', ctx={'port': True}))
    P.append(Part('guard_f', (7.4, 7.4, 13.0), (8.6, 9.0, 13.7), 'blued'))
    P.append(Part('guard_b', (7.4, 7.4, 13.0), (8.6, 8.1, 17.5), 'blued'))
    P.append(Part('guard_r', (7.4, 7.4, 16.8), (8.6, 9.0, 17.5), 'blued'))
    P.append(Part('trigger', (7.8, 8.1, 14.6), (8.2, 9.0, 15.1), 'steel', faces=['east', 'west', 'north', 'south', 'up']))
    P.append(Part('stock_a', (7.0, 8.8, 17.0), (9.0, 12.0, 21.0), 'wood'))
    P.append(Part('stock_b', (7.0, 7.4, 21.0), (9.0, 11.4, 25.0), 'wood'))
    P.append(Part('pad', (6.9, 7.2, 25.0), (9.1, 11.6, 25.7), 'dark'))
    P.append(Part('shell', (7.4, 6.4, 10.8), (8.6, 8.0, 13.2), 'shell', 'shell', ctx={'ybrass': 6.4}))
    P.append(Part('flash_a', (6.0, 9.7, -6.7), (10.0, 13.7, -6.7), 'flash', 'flash', faces=['north', 'south'], special='flash'))
    P.append(Part('flash_b', (8.0, 9.7, -9.5), (8.0, 13.7, -4.0), 'flash', 'flash', faces=['east', 'west'], special='flash'))
    P.append(Part('flash_c', (6.0, 11.6, -9.5), (10.0, 11.6, -4.0), 'flash', 'flash', faces=['up', 'down'], special='flash'))
    return P

def hand_parts():
    P = []
    P.append(Part('r_fingers', (6.6, 8.2, 16.6), (9.2, 9.9, 18.6), 'glove', 'right'))
    P.append(Part('r_palm', (8.8, 8.0, 17.4), (10.2, 10.8, 21.2), 'glove', 'right'))
    P.append(Part('r_back', (8.2, 10.2, 18.0), (10.4, 12.4, 22.0), 'glove', 'right', ctx={'knuckle': True}))
    P.append(Part('r_thumb', (6.5, 10.6, 16.8), (7.1, 11.8, 20.6), 'glove', 'right'))
    P.append(Part('r_wrist', (7.9, 8.4, 21.0), (10.4, 12.2, 23.0), 'glove', 'right'))
    P.append(Part('r_sleeve', (7.5, 7.6, 22.8), (11.0, 12.4, 31.9), 'sleeve', 'right', rot={'origin': [9, 10, 22.8], 'axis': 'x', 'angle': 22.5}))
    return P
def lefts():
    return {
     'idle': [Part('l_palm', (6.0, 7.0, 2.2), (9.8, 8.6, 8.8), 'glove', 'left'), Part('l_side', (5.6, 8.6, 2.4), (6.7, 10.9, 8.6), 'glove', 'left'),
              Part('l_top', (6.2, 10.9, 2.6), (9.0, 11.8, 8.0), 'glove', 'left'),
              Part('l_sleeve', (2.4, 3.6, 8.4), (6.0, 7.8, 31.0), 'sleeve', 'left', rot={'origin': [4, 5.6, 8.4], 'axis': 'x', 'angle': 22.5})],
     'mag': [Part('l_cup', (6.2, 4.4, 9.6), (9.8, 6.8, 14.2), 'glove', 'left'),
             Part('l_sleeve', (2.6, 1.6, 11.0), (6.0, 5.4, 31.0), 'sleeve', 'left', rot={'origin': [4, 3.4, 11.0], 'axis': 'x', 'angle': 22.5})],
     'plate': [Part('l_cup', (6.2, 5.6, 9.6), (9.8, 8.0, 14.2), 'glove', 'left'),
               Part('l_sleeve', (2.6, 2.8, 11.0), (6.0, 6.6, 31.0), 'sleeve', 'left', rot={'origin': [4, 4.6, 11.0], 'axis': 'x', 'angle': 22.5})],
     'slide': [Part('l_palm', (6.0, 7.0, 2.2), (9.8, 8.6, 8.8), 'glove', 'left'), Part('l_side', (5.6, 8.6, 2.4), (6.7, 10.9, 8.6), 'glove', 'left'),
               Part('l_top', (6.2, 10.9, 2.6), (9.0, 11.8, 8.0), 'glove', 'left'),
               Part('l_sleeve', (2.4, 3.6, 8.4), (6.0, 7.8, 27.0), 'sleeve', 'left', rot={'origin': [4, 5.6, 8.4], 'axis': 'x', 'angle': 22.5})]}

# bolt = ход цевья; shell: None нет / 'low' под окном / 'in' у окна
STATES = {0: dict(bolt=0, shell=None, flash=False), 1: dict(bolt=0, shell=None, flash=True), 2: dict(bolt=0, shell=None, flash=False),
          3: dict(bolt=0, shell=None, flash=False), 4: dict(bolt=0, shell='low', flash=False), 5: dict(bolt=0, shell=None, flash=False),
          6: dict(bolt=0, shell='in', flash=False), 7: dict(bolt=3.2, shell=None, flash=False), 8: dict(bolt=1.6, shell=None, flash=False)}
HANDS = {0: ('idle', 0), 1: ('mag', 0), 2: ('away', 0), 3: ('plate', 0), 4: ('slide', 3.2), 5: ('slide', 1.6)}

def state_elements(parts, s):
    els = []
    for p in parts:
        T = (0, 0, 0)
        if p.group == 'handle': T = (0, 0, s['bolt'])
        elif p.group == 'shell':
            if s['shell'] is None: continue
            T = (0, -1.4 if s['shell'] == 'low' else 0, 0)
        elif p.group == 'flash' and not s['flash']: continue
        els.append(gp.part_to_element(p, T))
    return els

if __name__ == '__main__':
    gunlib.generate('shotgun', gun_parts(), hand_parts(), lefts(), STATES, HANDS, state_elements, atlas=512, dens=3, grip=(8, 9.5, 19), s=0.6)
