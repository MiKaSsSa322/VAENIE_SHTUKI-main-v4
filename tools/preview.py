"""QA-рендерер: растеризует JSON-модели Minecraft (кубоиды, UV, rotation, display) для проверки без игры.
Порядок вершин/UV взят из FaceBakery 1.20.1; ориентация осей — как в игре."""
import os, json, math
import numpy as np
from PIL import Image

ASSETS = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources/assets/frontiermilitary')
_tex_cache = {}

def load_tex(ref):
    if ref not in _tex_cache:
        ns, p = ref.split(':') if ':' in ref else ('minecraft', ref)
        path = os.path.join(ASSETS, 'textures', p + '.png')
        _tex_cache[ref] = np.array(Image.open(path).convert('RGBA'))
    return _tex_cache[ref]

FACE_VERTS = {   # (axis choice per vertex) порядок как в FaceInfo
    'down':  [('min','min','max'), ('min','min','min'), ('max','min','min'), ('max','min','max')],
    'up':    [('min','max','min'), ('min','max','max'), ('max','max','max'), ('max','max','min')],
    'north': [('max','max','min'), ('max','min','min'), ('min','min','min'), ('min','max','min')],
    'south': [('min','max','max'), ('min','min','max'), ('max','min','max'), ('max','max','max')],
    'west':  [('min','max','min'), ('min','min','min'), ('min','min','max'), ('min','max','max')],
    'east':  [('max','max','max'), ('max','min','max'), ('max','min','min'), ('max','max','min')],
}
NORMALS = {'down': (0,-1,0), 'up': (0,1,0), 'north': (0,0,-1), 'south': (0,0,1), 'west': (-1,0,0), 'east': (1,0,0)}

def rot_axis(p, axis, ang, origin):
    a = math.radians(ang); c, s = math.cos(a), math.sin(a)
    x, y, z = (p[0]-origin[0], p[1]-origin[1], p[2]-origin[2])
    if axis == 'x': y, z = y*c - z*s, y*s + z*c
    elif axis == 'y': x, z = x*c + z*s, -x*s + z*c
    else: x, y = x*c - y*s, x*s + y*c
    return (x+origin[0], y+origin[1], z+origin[2])

def model_quads(m, textures_override=None):
    """-> список (verts[4] в 1/16 блока, uv[4] в 0..16, tex_ref, normal)"""
    texmap = dict(m.get('textures', {}))
    if textures_override: texmap.update(textures_override)
    def resolve(t):
        while t.startswith('#'): t = texmap[t[1:]]
        return t
    out = []
    for e in m['elements']:
        f, t = e['from'], e['to']
        rot = e.get('rotation')
        for d, fd in e['faces'].items():
            verts = []
            for (ax, ay, az) in FACE_VERTS[d]:
                p = (f[0] if ax=='min' else t[0], f[1] if ay=='min' else t[1], f[2] if az=='min' else t[2])
                if rot: p = rot_axis(p, rot['axis'], rot['angle'], rot['origin'])
                verts.append(p)
            u1, v1, u2, v2 = fd['uv']
            uvs = [(u1, v1), (u1, v2), (u2, v2), (u2, v1)]
            n = NORMALS[d]
            if rot:
                n = rot_axis(n, rot['axis'], rot['angle'], (0,0,0))
            out.append((verts, uvs, resolve(fd['texture']), n))
    return out

def mat_t(x, y, z):
    m = np.eye(4); m[:3, 3] = (x, y, z); return m
def mat_s(x, y=None, z=None):
    m = np.eye(4); m[0,0], m[1,1], m[2,2] = x, y if y is not None else x, z if z is not None else x; return m
def mat_rxyz(rx, ry, rz):
    """Как ItemTransform: Quaternionf.rotationXYZ => R = Rx*Ry*Rz."""
    def Rx(a): a=math.radians(a); c,s=math.cos(a),math.sin(a); return np.array([[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]])
    def Ry(a): a=math.radians(a); c,s=math.cos(a),math.sin(a); return np.array([[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]])
    def Rz(a): a=math.radians(a); c,s=math.cos(a),math.sin(a); return np.array([[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]])
    return Rx(rx) @ Ry(ry) @ Rz(rz)
def mat_ry_deg(a): return mat_rxyz(0, a, 0)

def display_matrix(d):
    """translate(T/16) * R * scale * translate(-0.5): модель в 1/16 -> блоки."""
    t = d.get('translation', [0,0,0]); r = d.get('rotation', [0,0,0]); s = d.get('scale', [1,1,1])
    return mat_t(t[0]/16, t[1]/16, t[2]/16) @ mat_rxyz(*r) @ mat_s(*s) @ mat_t(-0.5, -0.5, -0.5)

def shade_of(n):
    ax = np.abs(n).argmax()
    if ax == 1: return 1.0 if n[1] > 0 else 0.5
    if ax == 2: return 0.8
    return 0.6

def render(quad_sets, M, size=(640, 360), proj='persp', fov=70, ortho_scale=1.0, bg=(70, 78, 90),
           cam_clip=0.04, lighting=True, ortho_center=(0, 0)):
    """quad_sets: [(quads, extra_matrix)] — вершины /16 -> блоки -> extra -> M."""
    W, H = size
    img = np.zeros((H, W, 3), dtype=np.float32); img[:] = bg
    zbuf = np.full((H, W), np.inf)
    aspect = W / H
    f = 1.0 / math.tan(math.radians(fov) / 2)
    for quads, extra in quad_sets:
        T = M @ extra
        for verts, uvs, tex, n in quads:
            tx = load_tex(tex); th, tw = tx.shape[:2]
            pts = []
            for v in verts:
                p = T @ np.array([v[0]/16, v[1]/16, v[2]/16, 1.0]); pts.append(p[:3])
            nn = (T[:3, :3] @ np.array(n)); nn = nn / (np.linalg.norm(nn) + 1e-9)
            # освещение: из «мирового» направления (до проекции) — берём нормаль после extra
            nw = (extra[:3, :3] @ np.array(n)); sh = shade_of(nw) if lighting else 1.0
            for tri in ((0, 1, 2), (0, 2, 3)):
                P = [pts[i] for i in tri]; UV = [uvs[i] for i in tri]
                if proj == 'persp':
                    if any(-p[2] < cam_clip for p in P): continue
                    S = [((p[0] / -p[2]) * f / aspect * (W/2) + W/2, (-p[1] / -p[2]) * f * (H/2) + H/2, 1.0 / -p[2]) for p in P]
                else:
                    S = [(p[0] * ortho_scale * (H/2) + W/2 + ortho_center[0], -p[1] * ortho_scale * (H/2) + H/2 + ortho_center[1], -p[2]) for p in P]
                xs = [s[0] for s in S]; ys = [s[1] for s in S]
                x0, x1 = max(0, int(math.floor(min(xs)))), min(W - 1, int(math.ceil(max(xs))))
                y0, y1 = max(0, int(math.floor(min(ys)))), min(H - 1, int(math.ceil(max(ys))))
                if x0 > x1 or y0 > y1: continue
                (ax, ay, aw), (bx, by, bw), (cx, cy, cw) = S
                den = (by - cy) * (ax - cx) + (cx - bx) * (ay - cy)
                if abs(den) < 1e-9: continue
                gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
                l1 = ((by - cy) * (gx - cx) + (cx - bx) * (gy - cy)) / den
                l2 = ((cy - ay) * (gx - cx) + (ax - cx) * (gy - cy)) / den
                l3 = 1 - l1 - l2
                inside = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
                if not inside.any(): continue
                if proj == 'persp':
                    iw = l1 * aw + l2 * bw + l3 * cw
                    z = 1.0 / np.maximum(iw, 1e-9)
                    u = (l1 * UV[0][0] * aw + l2 * UV[1][0] * bw + l3 * UV[2][0] * cw) / np.maximum(iw, 1e-9)
                    v = (l1 * UV[0][1] * aw + l2 * UV[1][1] * bw + l3 * UV[2][1] * cw) / np.maximum(iw, 1e-9)
                else:
                    z = l1 * aw + l2 * bw + l3 * cw
                    u = l1 * UV[0][0] + l2 * UV[1][0] + l3 * UV[2][0]
                    v = l1 * UV[0][1] + l2 * UV[1][1] + l3 * UV[2][1]
                px = np.clip((u / 16 * tw).astype(int), 0, tw - 1); py = np.clip((v / 16 * th).astype(int), 0, th - 1)
                texel = tx[py, px]
                alpha = texel[..., 3]
                ok = inside & (alpha > 127)
                sub_z = zbuf[y0:y1 + 1, x0:x1 + 1]
                ok &= z < sub_z
                if not ok.any(): continue
                col = texel[..., :3].astype(np.float32) * sh
                sub_img = img[y0:y1 + 1, x0:x1 + 1]
                sub_img[ok] = col[ok]; sub_z[ok] = z[ok]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))

def load_json(path):
    with open(path, encoding='utf-8') as f: return json.load(f)

def block_model(name):
    return load_json(os.path.join(ASSETS, 'models/block', name + '.json'))
def item_model(name):
    return load_json(os.path.join(ASSETS, 'models/item', name + '.json'))

def eval_multipart(state_name, state):
    """state: dict north/east/south/west/up -> значение; возвращает [(model_name, y_deg)]."""
    bs = load_json(os.path.join(ASSETS, 'blockstates', state_name + '.json'))
    out = []
    for part in bs['multipart']:
        when = part.get('when')
        if when is None or all(str(state.get(k)) == v for k, v in when.items()):
            ap = part['apply']; out.append((ap['model'].split('/')[-1], ap.get('y', 0)))
    return out

def block_view(state_name, state, size=(300, 300), ortho_scale=0.62):
    sets = []
    for mname, y in eval_multipart(state_name, state):
        q = model_quads(block_model(mname))
        # blockstate y=N: по часовой сверху => math Ry(-N) вокруг центра блока
        ex = mat_t(.5, 0, .5) @ mat_rxyz(0, -y, 0) @ mat_t(-.5, 0, -.5)
        sets.append((q, ex))
    # изометрия как GUI блока: rotX 30, rotY 225
    M = mat_rxyz(30, 225, 0) @ mat_t(-.5, -.5, -.5)
    return render(sets, M, size, proj='ortho', ortho_scale=ortho_scale)
