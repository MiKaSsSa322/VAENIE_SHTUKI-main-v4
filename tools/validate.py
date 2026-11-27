"""Проверка целостности ресурсов мода без запуска игры."""
import os, json, sys, re
ROOT = os.path.join(os.path.dirname(__file__), '..', 'src/main/resources')
MOD = 'frontiermilitary'
A = f'{ROOT}/assets/{MOD}'
errors, warns = [], []
ALLOWED_VANILLA_PARENTS = {'minecraft:item/generated', 'minecraft:block/cube_all', 'minecraft:block/cube_bottom_top'}

def exists_tex(ref):
    ns, p = ref.split(':') if ':' in ref else ('minecraft', ref)
    if ns != MOD: return None
    return os.path.exists(f'{A}/textures/{p}.png')
def exists_model(ref):
    ns, p = ref.split(':')
    if ns != MOD: return ref in ALLOWED_VANILLA_PARENTS
    return os.path.exists(f'{A}/models/{p}.json')

# 1. все JSON парсятся
njson = 0
for d, _, fs in os.walk(ROOT):
    for f in fs:
        if f.endswith('.json') or f.endswith('.mcmeta'):
            try: json.load(open(os.path.join(d, f), encoding='utf-8')); njson += 1
            except Exception as e: errors.append(f'JSON {d}/{f}: {e}')

# 2. модели: parent, textures, uv-диапазоны, пустые элементы
nmodels = 0
for d, _, fs in os.walk(f'{A}/models'):
    for f in fs:
        path = os.path.join(d, f); m = json.load(open(path, encoding='utf-8')); nmodels += 1
        rel = os.path.relpath(path, A)
        if 'parent' in m and not exists_model(m['parent']): errors.append(f'{rel}: parent не найден {m["parent"]}')
        tex = m.get('textures', {})
        for k, v in tex.items():
            if not v.startswith('#') and exists_tex(v) is False: errors.append(f'{rel}: текстура не найдена {v}')
        for e in m.get('elements', []):
            for dname, fc in e['faces'].items():
                t = fc['texture']
                if t.startswith('#') and t[1:] not in tex: errors.append(f'{rel}: ключ текстуры {t} не объявлен')
                u = fc['uv']
                if any(c < -0.01 or c > 16.01 for c in u): errors.append(f'{rel}: uv вне 0..16 {u} ({e.get("name")})')
            for c in e['from'] + e['to']:
                if c < -16 or c > 32: errors.append(f'{rel}: координата вне -16..32')
        for ov in m.get('overrides', []):
            if not exists_model(ov['model']): errors.append(f'{rel}: override-модель не найдена {ov["model"]}')

# 3. блокстейты
for f in os.listdir(f'{A}/blockstates'):
    bs = json.load(open(f'{A}/blockstates/{f}', encoding='utf-8'))
    refs = []
    if 'variants' in bs:
        for v in bs['variants'].values(): refs += [v['model']] if isinstance(v, dict) else [x['model'] for x in v]
    for p in bs.get('multipart', []): refs.append(p['apply']['model'])
    for r in refs:
        if not exists_model(r): errors.append(f'blockstate {f}: нет модели {r}')

# 4. регистрации Java -> ресурсы
java = ''.join(open(os.path.join(d, f), encoding='utf-8').read() for d, _, fs in os.walk(os.path.join(ROOT, '../java')) for f in fs if f.endswith('.java'))
regs = re.findall(r'(?:ITEMS|SOUNDS|ENTITIES)\.register\("([a-z_.]+)"', java) + re.findall(r'register\("([a-z_]+)",\s*\(\)\s*->\s*new (?:Fence|IronBars|Wall|Lantern)', java)
blocks = re.findall(r'register\("([a-z_]+)",\s*\n?\s*\(\)\s*->\s*new (?:FenceBlock|IronBarsBlock|WallBlock|LanternBlock|Block|FacingBlock|ShapedBlock|RazorWireBlock|GlassBlock|FuelDrumBlock|GeneratorBlock|FloodlightBlock|CarpetBlock|PowerCableBlock)', java)
items = re.findall(r'ITEMS\.register\("([a-z0-9_]+)"', java)
sounds = re.findall(r'reg\("([a-z_.]+)"\)', java)
lang_en = json.load(open(f'{A}/lang/en_us.json', encoding='utf-8')); lang_ru = json.load(open(f'{A}/lang/ru_ru.json', encoding='utf-8'))
if set(lang_en) != set(lang_ru): errors.append(f'lang: ключи различаются {set(lang_en) ^ set(lang_ru)}')
for b in blocks:
    for key in (f'block.{MOD}.{b}',):
        if key not in lang_en or key not in lang_ru: errors.append(f'lang: нет {key}')
    if not os.path.exists(f'{A}/blockstates/{b}.json'): errors.append(f'нет blockstate {b}')
    if not os.path.exists(f'{A}/models/item/{b}.json'): errors.append(f'нет item-модели {b}')
    if not os.path.exists(f'{ROOT}/data/{MOD}/loot_tables/blocks/{b}.json'): errors.append(f'нет loot table {b}')
for i in items:
    if i in blocks: continue
    if f'item.{MOD}.{i}' not in lang_en or f'item.{MOD}.{i}' not in lang_ru: errors.append(f'lang: нет item.{MOD}.{i}')
    if not os.path.exists(f'{A}/models/item/{i}.json'): errors.append(f'нет item-модели {i}')
# 5. звуки
sj = json.load(open(f'{A}/sounds.json', encoding='utf-8'))
for s in sounds:
    if s not in sj: errors.append(f'sounds.json: нет события {s}')
for k, v in sj.items():
    for snd in v['sounds']:
        if not os.path.exists(f'{A}/sounds/{snd["name"].split(":")[1]}.ogg'): errors.append(f'нет файла звука {snd["name"]}')
    if v.get('subtitle') and v['subtitle'] not in lang_en: errors.append(f'нет субтитра {v["subtitle"]}')
# 6. текстуры: размеры и отсутствие пустых
from PIL import Image
for d, _, fs in os.walk(f'{A}/textures'):
    for f in fs:
        im = Image.open(os.path.join(d, f)).convert('RGBA'); 
        if im.getextrema()[3][1] == 0: errors.append(f'пустая текстура {f}')

print(f'JSON файлов: {njson}, моделей: {nmodels}, блоков: {len(blocks)} {blocks}, предметов: {len(items)} {items}, звуковых событий: {len(sounds)}')
print('ОШИБКИ:' if errors else 'Ошибок ресурсов нет.')
for e in errors: print(' -', e)
sys.exit(1 if errors else 0)
