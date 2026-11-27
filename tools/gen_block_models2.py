"""Модели, блокстейты, лут, теги и рецепты для ВСЕХ блоков мода (старые 4 + 19 новых)."""
import os, json, sys
sys.path.insert(0, os.path.dirname(__file__))
from gen_block_models import w, box, plane_x, plane_z, rot_y, STD_DISPLAY, model, DIRS, A, D, MOD, face

SIDES4 = ('north', 'east', 'south', 'west')
def allf(uv, faces=DIRS): return {d: uv for d in faces}
def T(name): return f'{MOD}:block/{name}'

def blockstate_single(name, model_name=None):
    w(f'{A}/blockstates/{name}.json', {'variants': {'': {'model': T(model_name or name)}}})
def blockstate_facing(name):
    v = {}
    for ang, d in ((0, 'north'), (90, 'east'), (180, 'south'), (270, 'west')):
        v[f'facing={d}'] = {'model': T(name), **({'y': ang} if ang else {})}
    w(f'{A}/blockstates/{name}.json', {'variants': v})
def item_from_block(name): w(f'{A}/models/item/{name}.json', {'parent': T(name)})
def item_model_copy(name, m):
    m = dict(m); m['display'] = STD_DISPLAY; w(f'{A}/models/item/{name}.json', m)

# --------------------------------------------------------------- простые кубы
def cubes():
    simple = {'sandbag_block': None, 'hesco_barrier': None, 'bunker_concrete': None, 'steel_hull_plate': None, 'camo_concrete': None}
    for n in simple:
        w(f'{A}/models/block/{n}.json', {'parent': 'minecraft:block/cube_all', 'textures': {'all': T(n)}})
        blockstate_single(n); item_from_block(n)
    w(f'{A}/models/block/steel_grating.json', {'parent': 'minecraft:block/cube_all', 'render_type': 'minecraft:cutout', 'textures': {'all': T('steel_grating')}})
    blockstate_single('steel_grating'); item_from_block('steel_grating')
    w(f'{A}/models/block/armored_glass.json', {'parent': 'minecraft:block/cube_all', 'render_type': 'minecraft:translucent', 'textures': {'all': T('armored_glass')}})
    blockstate_single('armored_glass'); item_from_block('armored_glass')
    for n in ('ammo_crate', 'supply_crate'):
        w(f'{A}/models/block/{n}.json', {'parent': 'minecraft:block/cube_bottom_top',
          'textures': {'top': T(n + '_top'), 'bottom': T(n + '_top'), 'side': T(n + '_side')}})
        blockstate_single(n); item_from_block(n)

# --------------------------------------------------------------- кастомные модели
def razor_wire():
    t = '#t'
    els = [plane_x(8, 0, 9, 0, 16, t, (0, 0, 16, 16)), plane_z(8, 0, 9, 0, 16, t, (0, 0, 16, 16)),
           {'from': [0, 1, 0], 'to': [16, 1, 16], 'faces': {'up': face(t, (0, 0, 16, 16)), 'down': face(t, (0, 0, 16, 16))}}]
    m = model({'t': T('razor_wire'), 'particle': T('razor_wire')}, els, cutout=True)
    w(f'{A}/models/block/razor_wire.json', m); blockstate_single('razor_wire'); item_model_copy('razor_wire', m)

def camo_net():
    t = '#t'
    els = [{'from': [0, y, 0], 'to': [16, y, 16], 'faces': {'up': face(t, (0, 0, 16, 16)), 'down': face(t, (0, 0, 16, 16))}} for y in (0.35, 0.9)]
    m = model({'t': T('camo_net'), 'particle': T('camo_net')}, els, cutout=True)
    w(f'{A}/models/block/camo_net.json', m); blockstate_single('camo_net'); item_model_copy('camo_net', m)

def fuel_drum():
    s, tp = '#s', '#t'
    parts = [((3, 5), (13, 11)), ((5, 3), (11, 5)), ((5, 11), (11, 13)), ((4, 4), (5, 5)), ((11, 4), (12, 5)), ((4, 11), (5, 12)), ((11, 11), (12, 12))]
    els = []
    for (x1, z1), (x2, z2) in parts:
        faces = {}
        for d in SIDES4:
            faces[d] = face(s, (0, 0, (x2 - x1) if d in ('north', 'south') else (z2 - z1), 14))
        faces['up'] = face(tp, (x1, z1, x2, z2))
        els.append({'from': [x1, 0, z1], 'to': [x2, 14, z2], 'faces': faces})
    els.append({'from': [4, 14, 4], 'to': [12, 14.5, 12], 'faces': {'up': face(tp, (4, 4, 12, 12))}})
    m = model({'s': T('fuel_drum'), 't': T('fuel_drum_top'), 'particle': T('fuel_drum')}, els)
    w(f'{A}/models/block/fuel_drum.json', m); blockstate_single('fuel_drum'); item_model_copy('fuel_drum', m)

def tank_trap():
    t = '#t'
    def beam(frm, to, axis):
        long_uv = (0, 0, 16, 3); end_uv = (0, 0, 3, 3)
        if axis == 'x': f = {'north': long_uv, 'south': long_uv, 'up': long_uv, 'down': long_uv, 'east': end_uv, 'west': end_uv}
        elif axis == 'y': f = {'north': long_uv, 'south': long_uv, 'east': long_uv, 'west': long_uv, 'up': end_uv, 'down': end_uv}
        else: f = {'east': long_uv, 'west': long_uv, 'up': long_uv, 'down': long_uv, 'north': end_uv, 'south': end_uv}
        return {'from': frm, 'to': to, 'rotation': {'angle': 45, 'axis': axis, 'origin': [8, 8, 8]}, 'faces': {d: face(t, uv) for d, uv in f.items()}}
    els = [beam([0, 6.5, 6.5], [16, 9.5, 9.5], 'x'), beam([6.5, 0, 6.5], [9.5, 16, 9.5], 'y'), beam([6.5, 6.5, 0], [9.5, 9.5, 16], 'z'),
           box((6, 6, 6), (10, 10, 10), t, allf((4, 4, 8, 8)))]
    m = model({'t': T('tank_trap'), 'particle': T('tank_trap')}, els)
    w(f'{A}/models/block/tank_trap.json', m); blockstate_single('tank_trap'); item_model_copy('tank_trap', m)

def map_table():
    m_, wd = '#m', '#w'
    els = [{'from': [0, 12, 0], 'to': [16, 14, 16], 'faces': {'up': face(m_, (0, 0, 16, 16)), 'down': face(wd, (0, 0, 16, 16)),
            **{d: face(wd, (0, 0, 16, 2)) for d in SIDES4}}}]
    for (x, z) in ((0.5, 0.5), (12.5, 0.5), (0.5, 12.5), (12.5, 12.5)):
        els.append(box((x, 0, z), (x + 3, 12, z + 3), wd, {**allf((0, 2, 3, 14), SIDES4)}, SIDES4))
    els.append(box((3.5, 7, 1), (12.5, 8.5, 2.5), wd, allf((0, 0, 9, 1.5)), SIDES4 + ('up',)))
    els.append(box((3.5, 7, 13.5), (12.5, 8.5, 15), wd, allf((0, 0, 9, 1.5)), SIDES4 + ('up',)))
    for (x, z) in ((5, 5), (10.5, 9)):                      # булавки-флажки на карте
        els.append(box((x, 14, z), (x + .7, 15.6, z + .7), m_, allf((3, 2, 4, 3)), SIDES4 + ('up',)))
    m = model({'m': T('map_table'), 'w': T('map_table_wood'), 'particle': T('map_table_wood')}, els)
    w(f'{A}/models/block/map_table.json', m); blockstate_facing('map_table'); item_model_copy('map_table', m)

def warning_sign():
    f_, b_ = '#f', '#b'
    els = [box((7.5, 0, 8), (8.5, 6, 9), b_, allf((0, 0, 1, 6)), SIDES4),
           {'from': [3, 6, 7], 'to': [13, 16, 8], 'faces': {'north': face(f_, (0, 0, 16, 16)), 'south': face(b_, (0, 0, 16, 16)),
            'east': face(b_, (0, 0, 1, 10)), 'west': face(b_, (0, 0, 1, 10)), 'up': face(b_, (0, 0, 10, 1)), 'down': face(b_, (0, 0, 10, 1))}}]
    m = model({'f': T('warning_sign'), 'b': T('warning_sign_back'), 'particle': T('warning_sign_back')}, els)
    w(f'{A}/models/block/warning_sign.json', m); blockstate_facing('warning_sign'); item_model_copy('warning_sign', m)

def radio_station():
    t = '#t'; case = (0, 0, 16, 8); dark = (0, 14, 16, 16)
    els = [
      {'from': [2, 0, 3], 'to': [14, 8, 13], 'faces': {'north': face(t, case), 'south': face(t, case), 'east': face(t, (0, 0, 10, 8)), 'west': face(t, (0, 0, 10, 8)),
        'up': face(t, (0, 0, 12, 8)), 'down': face(t, dark)}},
      {'from': [3, 1.5, 2.9], 'to': [7.5, 6.5, 3.0], 'faces': {'north': face(t, (0, 8, 8, 14))}},
      {'from': [8.5, 1.5, 2.9], 'to': [13, 6.5, 3.0], 'faces': {'north': face(t, (8, 8, 16, 14))}},
      box((11.5, 8, 10.5), (13, 9, 12), t, allf((0, 14, 2, 16)), SIDES4 + ('up',)),
      box((12, 9, 11), (12.5, 16, 11.5), t, allf((0, 14, 1, 16)), SIDES4 + ('up',)),
      box((4, 8, 7), (5, 10, 9), t, allf((0, 14, 2, 16)), SIDES4),
      box((11, 8, 7), (12, 10, 9), t, allf((0, 14, 2, 16)), SIDES4),
      box((4, 10, 7), (12, 11, 9), t, allf((0, 14, 8, 16)), SIDES4 + ('up',)),
    ]
    m = model({'t': T('radio_station'), 'particle': T('radio_station')}, els)
    w(f'{A}/models/block/radio_station.json', m); blockstate_facing('radio_station'); item_model_copy('radio_station', m)

def field_generator():
    body = (0, 0, 16, 6); tank = (0, 6, 16, 10); dark = (0, 14, 16, 16)
    def build(t, handle_out):
        els = [
          box((2, 0, 2), (14, 1, 14), t, allf(dark)),
          {'from': [3, 1, 3], 'to': [13, 7, 13], 'faces': {'north': face(t, body), 'south': face(t, body), 'east': face(t, body), 'west': face(t, body), 'up': face(t, body)}},
          {'from': [4, 2, 2.9], 'to': [9, 6, 3.0], 'faces': {'north': face(t, (0, 10, 8, 14))}},
          {'from': [13, 2, 4], 'to': [13.1, 6, 12], 'faces': {'east': face(t, (8, 10, 16, 14))}},
          box((3.5, 7, 4), (12.5, 11, 12), t, allf(tank, ('north', 'south', 'east', 'west', 'up')), ('north', 'south', 'east', 'west', 'up')),
          box((10, 7, 10), (12.5, 9.5, 15), t, allf(dark), DIRS),
          box((7, 11, 7), (9, 12, 9), t, allf(dark), SIDES4 + ('up',)),
          box((2.6, 3.0, 6.2), (3.0, 5.8, 9.8), t, allf(dark), DIRS),                         # корпус рекойл-стартера
        ]
        hx = -2.2 if handle_out else 1.2
        els.append(box((hx, 3.8, 7.2), (hx + 1.4, 5.2, 8.8), t, allf(dark), DIRS))            # рукоять шнура
        els.append(box((hx + 1.4, 4.3, 7.9), (2.6, 4.7, 8.1), t, allf((0, 12, 4, 13)), DIRS)) # шнур
        for (x, z) in ((2, 2), (13, 2), (2, 13), (13, 13)):
            els.append(box((x, 1, z), (x + 1, 12.5, z + 1), t, allf(dark), SIDES4 + ('up',)))
        els += [box((2, 12, 2), (14, 13, 3), t, allf(dark), DIRS), box((2, 12, 13), (14, 13, 14), t, allf(dark), DIRS),
                box((2, 12, 3), (3, 13, 13), t, allf(dark), DIRS), box((13, 12, 3), (14, 13, 13), t, allf(dark), DIRS)]
        return els
    for name, tex, out in (('field_generator', 'field_generator', False), ('field_generator_pull', 'field_generator', True), ('field_generator_run', 'field_generator_on', False)):
        m = model({'t': T(tex), 'particle': T(tex)}, build('#t', out))
        w(f'{A}/models/block/{name}.json', m)
        if name == 'field_generator': item_model_copy('field_generator', m)
    v = {}
    for ang, d in ((0, 'north'), (90, 'east'), (180, 'south'), (270, 'west')):
        for stage in range(6):
            mn = 'field_generator_run' if stage == 5 else ('field_generator_pull' if stage in (1, 3) else 'field_generator')
            v[f'facing={d},stage={stage}'] = {'model': T(mn), **({'y': ang} if ang else {})}
    w(f'{A}/blockstates/field_generator.json', {'variants': v})

def floodlight():
    case = (0, 0, 16, 8); dark = (8, 8, 16, 16)
    def build(t):
        return [
          box((4, 0, 4), (12, 1, 12), t, allf(dark), DIRS),
          box((7.5, 1, 7.5), (8.5, 9.5, 8.5), t, allf((8, 8, 9, 16)), SIDES4),
          box((6, 9, 6.5), (10, 10, 9.5), t, allf(dark), DIRS),
          {'from': [4, 9.5, 3], 'to': [12, 15.5, 9], 'faces': {'north': face(t, case), 'south': face(t, case), 'east': face(t, (0, 0, 6, 6)), 'west': face(t, (0, 0, 6, 6)), 'up': face(t, (0, 0, 8, 6)), 'down': face(t, case)}},
          {'from': [4.5, 10, 2.9], 'to': [11.5, 15, 3.0], 'faces': {'north': face(t, (0, 8, 8, 16))}},
          box((5, 15.5, 4), (11, 16, 8), t, allf(dark), DIRS)]
    for name, tex in (('floodlight', 'floodlight'), ('floodlight_off', 'floodlight_off')):
        m = model({'t': T(tex), 'particle': T(tex)}, build('#t'))
        w(f'{A}/models/block/{name}.json', m)
        if name == 'floodlight': item_model_copy('floodlight', m)
    v = {}
    for ang, d in ((0, 'north'), (90, 'east'), (180, 'south'), (270, 'west')):
        for lit in ('true', 'false'):
            v[f'facing={d},lit={lit}'] = {'model': T('floodlight' if lit == 'true' else 'floodlight_off'), **({'y': ang} if ang else {})}
    w(f'{A}/blockstates/floodlight.json', {'variants': v})

# --------------------------------------------------------------- стена из мешков
def sandbag_rows(kind):
    """Ряды мешков для половинки стены (север, z 0..8). -> список (x1,y1,z1,x2,y2,z2)."""
    rows = [(0, 5, 2.9), (5, 10, 2.2), (10, 14 if kind == 'low' else 16, 1.5)]
    out = []
    for i, (y0, y1, hw) in enumerate(rows):
        cuts = [(0, 4), (4, 8)] if i % 2 == 0 else [(0, 2), (2, 6), (6, 8)]
        for (z1, z2) in cuts: out.append((8 - hw, y0, z1, 8 + hw, y1, z2))
    return out
def sandbag_els(boxes, tex='#c'):
    els = []
    for (x1, y1, z1, x2, y2, z2) in boxes:
        row = int(y1 // 5)
        uvh = (0, (row % 4) * 4, 8, (row % 4) * 4 + 4)
        uvs = {d: uvh for d in SIDES4}; uvs['up'] = (0, 0, 8, 4); uvs['down'] = (0, 0, 8, 4)
        els.append(box((x1, y1, z1), (x2, y2, z2), tex, uvs, ('north', 'east', 'south', 'west', 'up') + (('down',) if y1 == 0 else ())))
    return els
def sandbag_wall():
    tex = {'c': T('sandbag_block'), 'particle': T('sandbag_block')}
    post = []
    for (y0, y1, hw) in ((0, 5, 4), (5, 10, 3.4), (10, 14, 2.8)):
        post.append((8 - hw, y0, 8 - hw, 8 + hw, y1, 8 + hw))
    w(f'{A}/models/block/sandbag_wall_post.json', model(tex, sandbag_els(post)))
    w(f'{A}/models/block/sandbag_wall_side.json', model(tex, sandbag_els(sandbag_rows('low'))))
    w(f'{A}/models/block/sandbag_wall_side_tall.json', model(tex, sandbag_els(sandbag_rows('tall'))))
    inv = sandbag_els(sandbag_rows('low')) + rot_y(sandbag_els(sandbag_rows('low')), 180)
    w(f'{A}/models/item/sandbag_wall.json', model(tex, inv, STD_DISPLAY))
    ms = [{'when': {'up': 'true'}, 'apply': {'model': T('sandbag_wall_post')}}]
    for ang, d in ((0, 'north'), (90, 'east'), (180, 'south'), (270, 'west')):
        for h, mn in (('low', 'sandbag_wall_side'), ('tall', 'sandbag_wall_side_tall')):
            ap = {'model': T(mn)}
            if ang: ap['y'] = ang
            ms.append({'when': {d: h}, 'apply': ap})
    w(f'{A}/blockstates/sandbag_wall.json', {'multipart': ms})

# --------------------------------------------------------------- data
OLD = ['metal_fence', 'security_bars', 'concrete_barrier', 'watch_post_lamp']
NEW = ['sandbag_block', 'sandbag_wall', 'hesco_barrier', 'razor_wire', 'ammo_crate', 'supply_crate', 'fuel_drum', 'bunker_concrete',
       'steel_hull_plate', 'camo_concrete', 'camo_net', 'radio_station', 'field_generator', 'floodlight', 'tank_trap', 'armored_glass',
       'map_table', 'steel_grating', 'warning_sign']
ALLB = OLD + NEW
PICKAXE = ['metal_fence', 'security_bars', 'concrete_barrier', 'watch_post_lamp', 'hesco_barrier', 'bunker_concrete', 'steel_hull_plate',
           'camo_concrete', 'radio_station', 'field_generator', 'floodlight', 'tank_trap', 'steel_grating', 'fuel_drum', 'razor_wire', 'warning_sign']
AXE = ['ammo_crate', 'supply_crate', 'map_table']
SHOVEL = ['sandbag_block', 'sandbag_wall']
HOE = ['camo_net']
NEEDS_STONE = ['metal_fence', 'security_bars', 'concrete_barrier', 'watch_post_lamp', 'bunker_concrete', 'steel_hull_plate', 'tank_trap', 'camo_concrete']

def ids(l): return [f'{MOD}:{b}' for b in l]
def tag(path, values): w(f'{D}/minecraft/tags/{path}.json', {'replace': False, 'values': ids(values)})

def data():
    tag('blocks/mineable/pickaxe', PICKAXE); tag('blocks/mineable/axe', AXE); tag('blocks/mineable/shovel', SHOVEL); tag('blocks/mineable/hoe', HOE)
    tag('blocks/needs_stone_tool', NEEDS_STONE)
    tag('blocks/fences', ['metal_fence']); tag('items/fences', ['metal_fence'])
    tag('blocks/walls', ['concrete_barrier', 'sandbag_wall']); tag('items/walls', ['concrete_barrier', 'sandbag_wall'])
    for b in [x for x in ALLB if x not in ('ammo_crate', 'supply_crate', 'field_generator', 'fuel_drum')]:
        w(f'{D}/{MOD}/loot_tables/blocks/{b}.json', {'type': 'minecraft:block', 'pools': [{'rolls': 1.0, 'bonus_rolls': 0.0,
          'entries': [{'type': 'minecraft:item', 'name': f'{MOD}:{b}'}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}],
          'random_sequence': f'{MOD}:blocks/{b}'})

SILK = {'condition': 'minecraft:match_tool', 'predicate': {'enchantments': [{'enchantment': 'minecraft:silk_touch', 'levels': {'min': 1}}]}}
NOT_SILK = {'condition': 'minecraft:inverted', 'term': SILK}
def loot_item(name, lo, hi, chance=1.0):
    pool = {'rolls': 1.0, 'bonus_rolls': 0.0, 'conditions': [NOT_SILK, {'condition': 'minecraft:survives_explosion'}],
            'entries': [{'type': 'minecraft:item', 'name': name, 'functions': [{'function': 'minecraft:set_count', 'count': {'type': 'minecraft:uniform', 'min': lo, 'max': hi}}]}]}
    if chance < 1.0: pool['conditions'].append({'condition': 'minecraft:random_chance', 'chance': chance})
    return pool
def loot_crate(block, pools):
    base = {'rolls': 1.0, 'bonus_rolls': 0.0, 'conditions': [SILK], 'entries': [{'type': 'minecraft:item', 'name': f'{MOD}:{block}'}]}
    w(f'{D}/{MOD}/loot_tables/blocks/{block}.json', {'type': 'minecraft:block', 'pools': [base] + pools, 'random_sequence': f'{MOD}:blocks/{block}'})
def loot_fuel(block):
    w(f'{D}/{MOD}/loot_tables/blocks/{block}.json', {'type': 'minecraft:block', 'pools': [{'rolls': 1.0, 'bonus_rolls': 0.0,
      'entries': [{'type': 'minecraft:item', 'name': f'{MOD}:{block}', 'functions': [{'function': 'minecraft:copy_state', 'block': f'{MOD}:{block}', 'properties': ['fuel']}]}],
      'conditions': [{'condition': 'minecraft:survives_explosion'}]}], 'random_sequence': f'{MOD}:blocks/{block}'})
def loot_special():
    # ящик с боеприпасами: патроны для КАЖДОГО оружия мода в случайном количестве
    loot_crate('ammo_crate', [loot_item(f'{MOD}:pistol_ammo', 6, 24, 0.9), loot_item(f'{MOD}:rifle_ammo', 10, 36, 0.9),
                              loot_item(f'{MOD}:sniper_ammo', 3, 10, 0.85), loot_item(f'{MOD}:shotgun_shells', 4, 14, 0.85),
                              loot_item('minecraft:gunpowder', 1, 3, 0.5), loot_item('minecraft:iron_nugget', 2, 6, 0.4)])
    # ящик снабжения: нити, сухпайки и аптечки: минимум 1, с малым шансом 2 и 3
    loot_crate('supply_crate', [loot_item(f'{MOD}:reinforced_fiber', 2, 5), loot_item('minecraft:string', 2, 6, 0.75),
                                loot_item(f'{MOD}:field_ration', 1, 4),
                                loot_item(f'{MOD}:medkit', 1, 1),            # гарантированная
                                loot_item(f'{MOD}:medkit', 1, 1, 0.18),      # 2-я: 18%
                                loot_item(f'{MOD}:medkit', 1, 1, 0.05)])     # 3-я: 5%
    loot_fuel('field_generator'); loot_fuel('fuel_drum')
    w(f'{D}/{MOD}/loot_tables/blocks/power_cable.json', {'type': 'minecraft:block', 'pools': [{'rolls': 1.0, 'bonus_rolls': 0.0,
      'entries': [{'type': 'minecraft:item', 'name': f'{MOD}:power_cable'}], 'conditions': [{'condition': 'minecraft:survives_explosion'}]}],
      'random_sequence': f'{MOD}:blocks/power_cable'})

def I(x): return {'item': x}
def TG(x): return {'tag': x}
def shaped(name, pattern, key, count=1, cat='building'):
    w(f'{D}/{MOD}/recipes/{name}.json', {'type': 'minecraft:crafting_shaped', 'category': cat, 'pattern': pattern, 'key': key,
      'result': {'item': f'{MOD}:{name}', 'count': count}})
def shapeless(name, ings, count=1, cat='misc'):
    w(f'{D}/{MOD}/recipes/{name}.json', {'type': 'minecraft:crafting_shapeless', 'category': cat, 'ingredients': ings,
      'result': {'item': f'{MOD}:{name}', 'count': count}})

def recipes():
    ing, nug, fib = I('minecraft:iron_ingot'), I('minecraft:iron_nugget'), I(f'{MOD}:reinforced_fiber')
    cg = I('minecraft:gray_concrete'); planks = TG('minecraft:planks')
    shapeless('reinforced_fiber', [I('minecraft:string')] * 3 + [nug], 3, 'misc')
    shaped('metal_fence', ['IBI', 'IBI'], {'I': ing, 'B': I('minecraft:iron_bars')}, 4)
    shaped('security_bars', ['INI', 'INI', 'INI'], {'I': ing, 'N': nug}, 4)
    shaped('concrete_barrier', ['CCC', 'CCC'], {'C': cg}, 6)
    shaped('watch_post_lamp', ['N', 'L', 'I'], {'N': nug, 'L': I('minecraft:lantern'), 'I': ing}, 1)
    shaped('sandbag_block', ['SS', 'SS'], {'S': I('minecraft:sand')}, 4)
    shaped('sandbag_wall', ['BBB', 'BBB'], {'B': I(f'{MOD}:sandbag_block')}, 6)
    shaped('hesco_barrier', ['NDN', 'DDD', 'NDN'], {'N': nug, 'D': I('minecraft:dirt')}, 2)
    shaped('razor_wire', ['NNN', 'NSN', 'NNN'], {'N': nug, 'S': I('minecraft:string')}, 3)
    shaped('ammo_crate', ['PPP', 'IGI', 'PPP'], {'P': planks, 'I': ing, 'G': I('minecraft:gunpowder')}, 1)
    shaped('supply_crate', ['PPP', 'PFP', 'PPP'], {'P': planks, 'F': I(f'{MOD}:field_ration')}, 1)
    shaped('fuel_drum', ['III', 'ICI', 'III'], {'I': ing, 'C': I('minecraft:coal')}, 1)
    shaped('bunker_concrete', ['NCN', 'CCC', 'NCN'], {'N': nug, 'C': cg}, 4)
    shaped('steel_hull_plate', ['II', 'II'], {'I': ing}, 4)
    shapeless('camo_concrete', [cg, I('minecraft:green_dye'), I('minecraft:brown_dye')], 2, 'building')
    shaped('camo_net', ['FVF', 'VFV', 'FVF'], {'F': fib, 'V': I('minecraft:vine')}, 4)
    shaped('radio_station', ['ICI', 'IRI', 'III'], {'I': ing, 'C': I('minecraft:copper_ingot'), 'R': I('minecraft:redstone')}, 1, 'redstone')
    shaped('field_generator', ['III', 'IFI', 'IRI'], {'I': ing, 'F': I('minecraft:furnace'), 'R': I('minecraft:redstone')}, 1, 'redstone')
    shaped('floodlight', [' L ', 'III', ' I '], {'L': I('minecraft:redstone_lamp'), 'I': ing}, 1, 'redstone')
    shaped('tank_trap', ['I I', 'III', 'I I'], {'I': ing}, 1)
    shaped('armored_glass', ['GNG', 'GGG', 'GNG'], {'G': I('minecraft:glass'), 'N': nug}, 2)
    shaped('map_table', ['PPP', 'WWW', 'S S'], {'P': I('minecraft:paper'), 'W': planks, 'S': I('minecraft:stick')}, 1)
    shaped('steel_grating', ['BB', 'BB'], {'B': I('minecraft:iron_bars')}, 4)
    shaped('warning_sign', ['III', 'IDI', ' S '], {'I': ing, 'D': I('minecraft:yellow_dye'), 'S': I('minecraft:stick')}, 2)

def extra_recipes():
    ing, nug = I('minecraft:iron_ingot'), I('minecraft:iron_nugget')
    fib = I(f'{MOD}:reinforced_fiber'); cu = I('minecraft:copper_ingot'); pl = TG('minecraft:planks')
    shaped('power_cable', ['SSS', 'CCC', 'SSS'], {'S': I('minecraft:string'), 'C': cu}, 6, 'redstone')
    shaped('sniper', ['  I', 'IIB', 'FW '], {'I': ing, 'B': I('minecraft:spyglass'), 'F': fib, 'W': pl}, 1, 'equipment')
    shaped('shotgun', ['III', 'WBR', '  W'], {'I': ing, 'W': pl, 'B': I('minecraft:iron_bars'), 'R': I('minecraft:redstone')}, 1, 'equipment')
    shapeless('sniper_ammo', [I('minecraft:gunpowder'), ing, cu, cu], 6, 'equipment')
    shapeless('shotgun_shells', [I('minecraft:gunpowder'), I('minecraft:paper'), I('minecraft:iron_nugget'), I('minecraft:iron_nugget')], 6, 'equipment')
    shaped('ghillie_hood', ['FVF', 'F F'], {'F': fib, 'V': I('minecraft:vine')}, 1, 'equipment')
    shaped('ghillie_jacket', ['F F', 'FVF', 'VFV'], {'F': fib, 'V': I('minecraft:vine')}, 1, 'equipment')
    shaped('ghillie_trousers', ['FVF', 'V V', 'F F'], {'F': fib, 'V': I('minecraft:vine')}, 1, 'equipment')
    shaped('ghillie_wraps', ['F F', 'V V'], {'F': fib, 'V': I('minecraft:vine')}, 1, 'equipment')
    shaped('empty_canister', ['NIN', 'I I', 'III'], {'N': nug, 'I': ing}, 1, 'misc')
    shapeless('fuel_canister', [I(f'{MOD}:empty_canister'), I('minecraft:coal'), I('minecraft:coal'), I('minecraft:coal')], 1, 'misc')
    shaped('medkit', ['PWP', 'WGW', 'PWP'], {'P': I('minecraft:paper'), 'W': I('minecraft:white_wool'), 'G': I('minecraft:glistering_melon_slice')}, 1, 'misc')

if __name__ == '__main__':
    cubes(); razor_wire(); camo_net(); fuel_drum(); tank_trap(); map_table(); warning_sign(); radio_station(); field_generator(); floodlight(); sandbag_wall()
    data(); loot_special(); recipes(); extra_recipes(); print('blocks:', len(ALLB), 'models, states, loot, tags, recipes written')
