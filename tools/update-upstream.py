#!/usr/bin/env python3
"""Обновляет lists/upstream/*.txt из публичных источников (скачивает, разбирает, убирает повторы между источниками).
  python tools/update-upstream.py [--proxy http://host:port] [--only runetfreedom,adguard,peterlowe]

Источники (в порядке приоритета; домен записывается только в первый источник, где встретился):
  runetfreedom  список category-ads-all из https://github.com/runetfreedom/russia-v2ray-rules-dat (geosite.dat, ~70 МБ; GPL-3.0)
  adguard       https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt (только простые правила ||домен^ [$important]; исключения @@ учитываются; GPL-3.0)
  peterlowe     https://pgl.yoyo.org/adservers/ (простой список доменов; автор разрешает объединять и публиковать)
Результат - текстовые файлы lists/upstream/<источник>.txt: один домен на строку, в шапке источник, дата и лицензия. Затем: python tools/build.py"""
import os, re, sys, datetime, urllib.request, tempfile
sys.path.insert(0, os.path.dirname(__file__))
import geosite_lib as g

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
OUT = os.path.join(ROOT, 'lists', 'upstream')
SOURCES = {
    'runetfreedom': ('https://github.com/runetfreedom/russia-v2ray-rules-dat/releases/latest/download/geosite.dat', 'GPL-3.0',
                     'runetfreedom/russia-v2ray-rules-dat, список category-ads-all (на основе v2fly/domain-list-community, MIT)'),
    'adguard': ('https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt', 'GPL-3.0', 'AdGuard DNS filter (AdguardTeam/AdGuardSDNSFilter)'),
    'peterlowe': ('https://pgl.yoyo.org/adservers/serverlist.php?hostformat=nohtml&showintro=0&mimetype=plaintext', 'свободное распространение разрешено автором',
                  "Peter Lowe's Ad and tracking server list (pgl.yoyo.org)"),
}
VALID = re.compile(r'^[a-z0-9]([a-z0-9._-]*[a-z0-9])?\.[a-z0-9-]{2,}$')

def fetch(url, proxy):
    h = [urllib.request.ProxyHandler({'http': proxy, 'https': proxy})] if proxy else []
    req = urllib.request.Request(url, headers={'User-Agent': 'OpenWRT-VM-PROXY-ads/1.0'})
    return urllib.request.build_opener(*h).open(req, timeout=300).read()

def parse_runetfreedom(data):
    path = os.path.join(tempfile.gettempdir(), 'ru-geosite.dat'); open(path, 'wb').write(data)
    rules = g.load_tag(path, {'category-ads-all'})['category-ads-all']
    return {v.lower() for t, v, _ in rules if t == 2}                 # только "домен и поддомены"

def parse_adguard(data):
    txt = data.decode('utf-8', 'replace'); dom = set(); exc = set()
    for l in txt.splitlines():
        l = l.strip().lower()
        if l.startswith('@@||'):
            m = re.match(r'^@@\|\|([a-z0-9._-]+)\^', l)
            if m: exc.add(m.group(1))
            continue
        m = re.match(r'^\|\|([a-z0-9._-]+)\^(\$important)?$', l)
        if m: dom.add(m.group(1))
    return dom - exc

def parse_peterlowe(data):
    return {l.strip().lower() for l in data.decode('utf-8', 'replace').splitlines() if l.strip() and not l.startswith('#')}

PARSERS = {'runetfreedom': parse_runetfreedom, 'adguard': parse_adguard, 'peterlowe': parse_peterlowe}

def main():
    proxy = sys.argv[sys.argv.index('--proxy') + 1] if '--proxy' in sys.argv else None
    only = sys.argv[sys.argv.index('--only') + 1].split(',') if '--only' in sys.argv else list(SOURCES)
    os.makedirs(OUT, exist_ok=True); seen = set(); today = datetime.date.today().isoformat()
    for name in SOURCES:                                              # порядок = приоритет
        url, lic, title = SOURCES[name]; path = os.path.join(OUT, name + '.txt')
        if name not in only:
            if os.path.exists(path):                                  # источник не обновляем, но его домены учитываем при дедупликации
                seen |= {l.strip() for l in open(path, encoding='utf-8') if l.strip() and not l.startswith('#')}
            continue
        print(f'{name}: скачиваю {url} ...', flush=True)
        raw = PARSERS[name](fetch(url, proxy))
        good = sorted(d for d in raw if VALID.match(d) and d not in seen)
        bad = len(raw) - len([d for d in raw if VALID.match(d)])
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(f'# Источник: {title}\n# Адрес: {url}\n# Лицензия источника: {lic}\n# Получено: {today}; домены, уже встреченные в источниках с более высоким приоритетом, не повторяются\n')
            f.write('\n'.join(good) + '\n')
        seen |= set(good)
        print(f'  всего {len(raw)}, новых для базы {len(good)} (отброшено некорректных {bad}) -> {path}')

if __name__ == '__main__':
    main()
