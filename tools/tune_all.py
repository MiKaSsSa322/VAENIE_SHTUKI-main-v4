"""Подбор положения от бедра (CS2) и позы прицеливания (ADS) для всех стволов; пишет *_display.json и AimPoses.java."""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from preview import mat_t, display_matrix
from tune_fp import ndc, solve

HERE = os.path.dirname(__file__)
JAVA = os.path.join(HERE, '..', 'src/main/java/com/frontiermilitary/client/AimPoses.java')
CFG = {
 # name: (hip front, hip rear, tf, tr, init, ads front, ads rear, ads tf, ads tr)
 'pulse_sidearm': dict(file='pistol', hip=None, af=(8, 13.3, 2.6), ar=(8, 13.3, 12.4), atf=(0, -0.075), atr=(0, -0.11)),
 'ak74': dict(file='ak74', hip=None, af=(8, 14.8, -2.0), ar=(8, 14.5, 10.9), atf=(0, -0.07), atr=(0, -0.10)),
 'sniper': dict(file='sniper', hip=((8, 11.0, -8.0), (8, 14.0, 23.0), (0.04, -0.10), (0.52, -0.40), [-8, 0, -9, 10, 4, 0.5]),
                af=(8, 14.0, 6.8), ar=(8, 14.0, 22.5), atf=(0, 0.0), atr=(0, 0.0)),
 'shotgun': dict(file='shotgun', hip=((8, 12.0, -6.0), (8, 12.8, 16.5), (0.08, -0.12), (0.52, -0.42), [-7, 0, -8, 10, 4, 0.6]),
                 af=(8, 12.8, -5.6), ar=(8, 12.8, 16.8), atf=(0, -0.07), atr=(0, -0.10)),
}

def load_fp(name, file):
    if name == 'pulse_sidearm': return json.load(open(os.path.join(HERE, 'pistol_display.json')))['firstperson_righthand']
    return json.load(open(os.path.join(HERE, f'{file}_display.json')))['firstperson_righthand']

def solve_ads(d_hip, af, ar, tf, tr):
    s = d_hip['scale'][0]
    def mk(x): return {'rotation': [x[4], x[3], d_hip['rotation'][2] * 0], 'translation': [x[0], x[1], x[2]], 'scale': [s] * 3}
    def res(x):
        d = mk(x); a, _ = ndc(d, af); b, _ = ndc(d, ar)
        return list(a - np.array(tf)) + list(b - np.array(tr))
    x0 = [d_hip['translation'][0] * 0.2, d_hip['translation'][1], d_hip['translation'][2], 0, 0]
    sol = least_squares(res, x0)
    return mk(sol.x)

def M(d): return mat_t(0.56, -0.52, -0.72) @ display_matrix(d)

rows = []
for name, c in CFG.items():
    if c['hip'] is not None:
        d, a, b, cost = solve(c['hip'][0], c['hip'][1], np.array(c['hip'][2]), np.array(c['hip'][3]), c['hip'][4])
        d = {k: [round(float(v), 3) for v in vals] for k, vals in d.items()}
        fp = {'firstperson_righthand': d, 'firstperson_lefthand': {'rotation': [d['rotation'][0], -d['rotation'][1], -d['rotation'][2]],
              'translation': [-d['translation'][0], d['translation'][1], d['translation'][2]], 'scale': d['scale']}}
        path = os.path.join(HERE, f"{c['file']}_display.json")
        old = json.load(open(path)) if os.path.exists(path) else {}
        old.update(fp); json.dump(old, open(path, 'w'), indent=1)
    d_hip = load_fp(name, c['file'])
    d_ads = solve_ads(d_hip, c['af'], c['ar'], c['atf'], c['atr'])
    delta = M(d_ads) @ np.linalg.inv(M(d_hip))
    rv = Rotation.from_matrix(delta[:3, :3]).as_rotvec(); ang = float(np.linalg.norm(rv)); ax = rv / ang if ang > 1e-9 else np.array([0, 1, 0.0])
    t = delta[:3, 3]
    a, _ = ndc(d_ads, c['af']); b, _ = ndc(d_ads, c['ar'])
    print(f"{name}: ADS front->{np.round(a,3)} rear->{np.round(b,3)} t={np.round(t,3)} angle={math.degrees(ang):.1f}")
    rows.append((name, t, math.degrees(ang), ax))

with open(JAVA, 'w') as f:
    f.write('package com.frontiermilitary.client;\n\n/** Сгенерировано tools/tune_all.py: смещение камерного пространства для позы прицеливания (ADS). */\n')
    f.write('public final class AimPoses {\n    private AimPoses() {}\n\n')
    f.write('    /** {tx, ty, tz, angleDeg, axisX, axisY, axisZ} или null. */\n    public static float[] get(String itemName) {\n        switch (itemName) {\n')
    for name, t, ang, ax in rows:
        v = ', '.join(f'{x:.5f}F' for x in (t[0], t[1], t[2], ang, ax[0], ax[1], ax[2]))
        f.write(f'            case "{name}": return new float[]{{{v}}};\n')
    f.write('            default: return null;\n        }\n    }\n}\n')
print('AimPoses.java written')
