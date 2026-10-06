#!/usr/bin/env python3
"""Собирает dist/geosite_custom.dat (формат geosite для Xray) из lists/ads-custom.txt. Тег списка: CUSTOM-ADS.
Типы правил: домен (по умолчанию, сам домен и поддомены) / full: (точное имя) / regexp: (регулярное выражение)."""
import os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SRC = os.path.join(ROOT, 'lists', 'ads-custom.txt'); OUT = os.path.join(ROOT, 'dist', 'geosite_custom.dat')

def varint(n):
    out = bytearray()
    while True:
        c = n & 0x7f; n >>= 7
        if n: out.append(c | 0x80)
        else: out.append(c); return bytes(out)

def domain(kind, value):   # Domain { Type type = 1; string value = 2 }; Plain=0 Regex=1 Domain=2 Full=3
    v = value.encode()
    return b'\x08' + varint(kind) + b'\x12' + varint(len(v)) + v

rules = []
for n, line in enumerate(open(SRC, encoding='utf-8'), 1):
    line = line.split('#', 1)[0].strip()
    if not line: continue
    if line.startswith('full:'): kind, val = 3, line[5:]
    elif line.startswith('regexp:'): kind, val = 1, line[7:]
    else: kind, val = 2, line
    if not val or ' ' in val: print(f'строка {n}: некорректное значение "{line}"'); sys.exit(1)
    rules.append(domain(kind, val.lower() if kind != 1 else val))
tag = b'CUSTOM-ADS'
site = b'\x0a' + varint(len(tag)) + tag + b''.join(b'\x12' + varint(len(r)) + r for r in rules)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'wb').write(b'\x0a' + varint(len(site)) + site)
print(f'записано {OUT}: {len(rules)} правил, {os.path.getsize(OUT)} байт')
