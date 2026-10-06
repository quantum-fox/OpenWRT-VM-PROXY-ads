#!/usr/bin/env python3
"""Собирает файлы geosite для Xray из списков в lists/: для каждого lists/ads-<имя>.txt получается dist/geosite_ADS-<ИМЯ>.dat с тегом ADS-<ИМЯ>
(lists/ads-ru.txt -> dist/geosite_ADS-RU.dat, тег ADS-RU; lists/ads-global.txt -> dist/geosite_ADS-GLOBAL.dat, тег ADS-GLOBAL).
Типы правил: домен (по умолчанию, сам домен и поддомены) / full: (точное имя) / regexp: (регулярное выражение). Пустой список файл не создаёт."""
import glob, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

def varint(n):
    out = bytearray()
    while True:
        c = n & 0x7f; n >>= 7
        if n: out.append(c | 0x80)
        else: out.append(c); return bytes(out)

def domain(kind, value):   # Domain { Type type = 1; string value = 2 }; Plain=0 Regex=1 Domain=2 Full=3
    v = value.encode()
    return b'\x08' + varint(kind) + b'\x12' + varint(len(v)) + v

def build(src, tag, out):
    rules = []
    for n, line in enumerate(open(src, encoding='utf-8'), 1):
        line = line.split('#', 1)[0].strip()
        if not line: continue
        if line.startswith('full:'): kind, val = 3, line[5:]
        elif line.startswith('regexp:'): kind, val = 1, line[7:]
        else: kind, val = 2, line
        if not val or ' ' in val: print(f'{src}, строка {n}: некорректное значение "{line}"'); sys.exit(1)
        rules.append(domain(kind, val.lower() if kind != 1 else val))
    if os.path.exists(out): os.remove(out)
    if not rules: print(f'{os.path.basename(src)}: пусто - файл не создаётся'); return
    t = tag.encode()
    site = b'\x0a' + varint(len(t)) + t + b''.join(b'\x12' + varint(len(r)) + r for r in rules)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, 'wb').write(b'\x0a' + varint(len(site)) + site)
    print(f'{os.path.basename(src)} -> {out}: {len(rules)} правил, {os.path.getsize(out)} байт (тег {tag})')

for src in sorted(glob.glob(os.path.join(ROOT, 'lists', 'ads-*.txt'))):
    name = os.path.basename(src)[4:-4].upper()
    build(src, f'ADS-{name}', os.path.join(ROOT, 'dist', f'geosite_ADS-{name}.dat'))
