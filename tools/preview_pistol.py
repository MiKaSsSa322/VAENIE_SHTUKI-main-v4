import sys, os, json; sys.path.insert(0, os.path.dirname(__file__))
from preview import *
from PIL import Image, ImageDraw
P = '/home/claude/preview'
def mq(name):
    m = load_json(os.path.join(ASSETS, 'models/item', name + '.json'))
    tex = {k: v for k, v in m['textures'].items()}
    return model_quads(m), m
def side(name, ang=-90, size=(300, 220), scale=2.6, pitch=0, ctr=(0, 0)):
    q, m = mq(name)
    M = mat_rxyz(pitch, ang, 0) @ mat_t(-.5, -.5, -.5)
    return render([(q, np.eye(4))], M, size, 'ortho', ortho_scale=scale, ortho_center=ctr)
def gui(name):
    q, m = mq(name); d = m['display']['gui']
    M = mat_t(0, 0, -2) @ mat_t(d['translation'][0]/16, d['translation'][1]/16, d['translation'][2]/16) @ mat_rxyz(*d['rotation']) @ mat_s(*d['scale']) @ mat_t(-.5, -.5, -.5)
    return render([(q, np.eye(4))], M, (320, 320), 'ortho', ortho_scale=1.0 * 1.1)
def fp(gun, hands, size=(800, 450)):
    sets = []
    d = load_json(os.path.join(ASSETS, 'models/item', gun + '.json'))['display']['firstperson_righthand']
    base = mat_t(0.56, -0.52, -0.72) @ display_matrix(d)
    for n in (gun, hands):
        if n: sets.append((mq(n)[0], np.eye(4)))
    return render(sets, base, size, 'persp', fov=70, bg=(96, 132, 70))
if __name__ == '__main__':
    mode = sys.argv[1]
    if mode == 'states':
        names = ['state_0', 'state_1', 'state_3', 'state_4', 'state_5', 'state_6', 'state_7', 'state_8']
        tiles = [side('pistol/' + n, -90, (400, 260), 3.0) for n in names]
        sh = Image.new('RGB', (1600, 520))
        for i, t in enumerate(tiles): sh.paste(t, ((i % 4) * 400, (i // 4) * 260))
        sh.save(f'{P}/pistol_states.png')
    elif mode == 'gui':
        t = gui('pulse_sidearm'); t.save(f'{P}/pistol_gui.png')
    elif mode == 'fp':
        a = fp('pistol/state_0', 'pistol/hands_0'); a.save(f'{P}/pistol_fp.png')
