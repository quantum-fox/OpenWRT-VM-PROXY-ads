"""Минимальный разбор/сборка geosite.dat (protobuf без библиотек).
GeoSiteList { repeated GeoSite entry = 1; }
GeoSite { string country_code = 1; repeated Domain domain = 2; }
Domain { Type type = 1; string value = 2; repeated Attribute attribute = 3; }
"""
import sys

def rd_varint(b, i):
    r = 0; s = 0
    while True:
        c = b[i]; i += 1
        r |= (c & 0x7f) << s
        if not c & 0x80: return r, i
        s += 7

def wr_varint(n):
    out = bytearray()
    while True:
        c = n & 0x7f; n >>= 7
        if n: out.append(c | 0x80)
        else: out.append(c); return bytes(out)

def fields(b):
    i = 0
    while i < len(b):
        k, i = rd_varint(b, i); f, t = k >> 3, k & 7
        if t == 0: v, i = rd_varint(b, i)
        elif t == 2:
            l, i = rd_varint(b, i); v = b[i:i+l]; i += l
        elif t == 1: v = b[i:i+8]; i += 8
        elif t == 5: v = b[i:i+4]; i += 4
        else: raise ValueError(t)
        yield f, t, v

def load_tag(path, wanted):
    """вернуть {tag: [(type, value, raw_domain_bytes)]} только для нужных тегов (файл читается целиком)"""
    b = open(path, 'rb').read(); res = {}
    for f, t, v in fields(b):
        if f != 1: continue
        code = None; doms = []
        for f2, t2, v2 in fields(v):
            if f2 == 1: code = v2.decode()
            elif f2 == 2: doms.append(v2)
        if code and code.lower() in wanted:
            out = []
            for d in doms:
                typ = 0; val = ''
                for f3, t3, v3 in fields(d):
                    if f3 == 1: typ = v3
                    elif f3 == 2: val = v3.decode()
                out.append((typ, val, d))
            res[code.lower()] = out
    return res

def build(tag, raw_domains):
    parts = [b'\x0a' + wr_varint(len(tag)) + tag.encode()]
    parts += [b'\x12' + wr_varint(len(d)) + d for d in raw_domains]      # join вместо += : иначе сборка 200 тысяч правил занимает минуты (квадратичное копирование)
    site = b''.join(parts)
    return b'\x0a' + wr_varint(len(site)) + site

if __name__ == '__main__':
    cmd = sys.argv[1]
    if cmd == 'compare':
        a = load_tag(sys.argv[2], {'category-ads-all'})['category-ads-all']
        b = load_tag(sys.argv[3], {'category-ads-all'})['category-ads-all']
        sa = {(t, v) for t, v, _ in a}; sb = {(t, v) for t, v, _ in b}
        print('наш geosite.dat:', len(sa), '| RU geosite.dat:', len(sb), '| общих:', len(sa & sb), '| только в RU:', len(sb - sa), '| только у нас:', len(sa - sb))
        extra = sorted(v for t, v in (sb - sa))
        print('примеры только в RU (50):', ', '.join(extra[:50]))
        print('RU-реклама из нашего списка расширений есть в RU-базе?', [d for d in ('mc.yandex.ru','an.yandex.ru','adfox.ru','ad.mail.ru','top-fwz1.mail.ru','counter.yadro.ru','tns-counter.ru','yandexadexchange.net') if any(v == d or v.endswith('.'+d) for t, v in sb)])
    elif cmd == 'extract':
        tags = sys.argv[4].split(',')
        got = load_tag(sys.argv[2], set(tags)); out = b''
        for tag in tags:
            out += build(tag.upper(), [raw for _, _, raw in got[tag]])
            print(tag, len(got[tag]), 'правил')
        open(sys.argv[3], 'wb').write(out); print('записано', len(out), 'байт')
