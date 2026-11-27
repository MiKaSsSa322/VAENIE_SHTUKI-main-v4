"""Численный подбор first-person display так, чтобы оружие лежало как во view-model CS2:
правый нижний угол, ствол к центру. Цели — экранные NDC-координаты двух точек модели."""
import sys, os, json, math
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from scipy.optimize import least_squares
from preview import mat_t, mat_rxyz, mat_s, display_matrix

FOV, ASPECT = 70.0, 16 / 9
F = 1.0 / math.tan(math.radians(FOV) / 2)

def ndc(d, p):
    M = mat_t(0.56, -0.52, -0.72) @ display_matrix(d)
    v = M @ np.array([p[0] / 16, p[1] / 16, p[2] / 16, 1.0])
    return np.array([v[0] / -v[2] * F / ASPECT, v[1] / -v[2] * F]), -v[2]

def solve(front, rear, t_front, t_rear, init, roll=-2.0):
    def mk(x):
        tx, ty, tz, yaw, pitch, s = x
        return {'rotation': [pitch, yaw, roll], 'translation': [tx, ty, tz], 'scale': [s] * 3}
    def res(x):
        d = mk(x)
        a, _ = ndc(d, front); b, _ = ndc(d, rear)
        r = list(a - t_front) + list(b - t_rear)
        r += [0.002 * (x[2] - init[2]), 0.01 * (x[5] - init[5])]        # слабая регуляризация
        return r
    sol = least_squares(res, init, bounds=([-30, -30, -30, -40, -30, 0.3], [30, 30, 30, 40, 30, 1.2]))
    d = mk(sol.x)
    a, za = ndc(d, front); b, zb = ndc(d, rear)
    return d, a, b, sol.cost

if __name__ == '__main__':
    out = {}
    # (дульный срез / передняя точка), (задняя верхняя точка), цели на экране
    cfg = {
     'pistol': dict(front=(8, 11.0, 1.1), rear=(8, 12.6, 13.2), tf=(0.20, -0.10), tr=(0.52, -0.36), init=[-4, 0, -4, 8, 6, 0.8]),
     'ak74':   dict(front=(8, 11.5, -6.0), rear=(8, 14.0, 21.0), tf=(0.06, -0.06), tr=(0.52, -0.46), init=[-8, 0, -9, 10, 4, 0.62]),
    }
    for name, c in cfg.items():
        d, a, b, cost = solve(c['front'], c['rear'], np.array(c['tf']), np.array(c['tr']), c['init'])
        # зеркальный вариант для левой руки
        L = {'rotation': [d['rotation'][0], -d['rotation'][1], -d['rotation'][2]], 'translation': [-d['translation'][0], d['translation'][1], d['translation'][2]], 'scale': d['scale']}
        d = {k: ([round(v, 3) for v in vals]) for k, vals in d.items()}; L = {k: [round(v, 3) for v in vals] for k, vals in L.items()}
        out[name] = {'firstperson_righthand': d, 'firstperson_lefthand': L}
        print(name, 'cost=%.5f' % cost, 'front->', np.round(a, 3), 'rear->', np.round(b, 3), d)
    json.dump(out, open(os.path.join(os.path.dirname(__file__), 'fp_tuned.json'), 'w'), indent=1)
