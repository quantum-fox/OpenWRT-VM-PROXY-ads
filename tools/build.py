#!/usr/bin/env python3
"""Собирает готовые файлы geosite для Xray/PassWall2 в dist/ из lists/upstream/*.txt (чужие базы) и lists/own/*.txt (ваши дополнения):
  dist/geosite_ADS-RU.dat      тег ADS-RU      - российская реклама: домены в зонах .ru/.su/.рф + всё из lists/own/ads-ru.txt
  dist/geosite_ADS-GLOBAL.dat  тег ADS-GLOBAL  - зарубежная реклама и трекеры: все остальные домены + lists/own/ads-global.txt
Правила: домен (по умолчанию, сам домен и поддомены) / full:домен (точное имя) / regexp:выражение - только в lists/own. Домены, для которых в базе уже есть родительский домен
(например a.b.com при наличии b.com), отбрасываются (они и так блокируются, а память экономится)."""
import glob, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import geosite_lib as g
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
RU_ZONES = ('.ru', '.su', '.xn--p1ai')

def read(path):
    out = []
    if not os.path.exists(path): return out
    for n, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.split('#', 1)[0].strip()
        if not line: continue
        if line.startswith('full:'): out.append((3, line[5:].lower()))
        elif line.startswith('regexp:'): out.append((1, line[7:]))
        elif ' ' in line: print(f'{path}, строка {n}: пробел в "{line}"'); sys.exit(1)
        else: out.append((2, line.lower()))
    return out

def dedupe(domains):
    s = set(domains); keep = []
    for d in sorted(s):
        p = d.split('.')
        if not any('.'.join(p[i:]) in s for i in range(1, len(p) - 1)): keep.append(d)
    return keep

def write(tag, rules, out):
    os.makedirs(os.path.dirname(out), exist_ok=True)
    if not rules:
        if os.path.exists(out): os.remove(out)
        print(f'{tag}: пусто - файл не создаётся'); return
    def enc(kind, v):
        b = v.encode(); return b'\x08' + g.wr_varint(kind) + b'\x12' + g.wr_varint(len(b)) + b
    open(out, 'wb').write(g.build(tag, [enc(k, v) for k, v in rules]))
    print(f'{os.path.relpath(out, ROOT)}: {len(rules)} правил, {os.path.getsize(out)} байт (тег {tag})')

up = []
for p in sorted(glob.glob(os.path.join(ROOT, 'lists', 'upstream', '*.txt'))):
    up += [v for k, v in read(p)]
own_ru = read(os.path.join(ROOT, 'lists', 'own', 'ads-ru.txt'))
own_gl = read(os.path.join(ROOT, 'lists', 'own', 'ads-global.txt'))
ru_up = [d for d in up if d.endswith(RU_ZONES)]
gl_up = [d for d in up if not d.endswith(RU_ZONES)]
ru = [(2, d) for d in dedupe(set(ru_up) | {v for k, v in own_ru if k == 2})] + [(k, v) for k, v in own_ru if k != 2]
gl = [(2, d) for d in dedupe(set(gl_up) | {v for k, v in own_gl if k == 2})] + [(k, v) for k, v in own_gl if k != 2]
write('ADS-RU', ru, os.path.join(ROOT, 'dist', 'geosite_ADS-RU.dat'))
write('ADS-GLOBAL', gl, os.path.join(ROOT, 'dist', 'geosite_ADS-GLOBAL.dat'))
