# OpenWRT-VM-PROXY-ads: списки рекламных и трекерных доменов

> **English summary.** Small shared lists of advertising/tracker/counter domains (Russian and global) for the **OpenWRT-VM-PROXY** router project. `tools/build.py` turns each `lists/ads-*.txt` into an Xray/v2ray `geosite` file in `dist/` (`ads-ru.txt` -> `geosite_ADS-RU.dat`, tag `ADS-RU`). On the router the file is appended to `geosite.dat` with `pw2-geosite` (PassWall2 ignores `ext:` entries) and used as `geosite:ads-ru`. Contributions: public ad/tracker domains only, no personal data. License: MIT. Documentation is in Russian.


Небольшие общие списки доменов рекламы, трекеров и счётчиков для прокси-роутера проекта **OpenWRT-VM-PROXY**. Дополняют стандартные списки (`geosite:category-ads-all`, российская база `runetfreedom`) тем, что в них не попало или попало с опозданием. Формат совместим с Xray/v2ray (`geosite`).

## Зачем отдельный репозиторий
- Списки меняются часто (каждый день могут появляться новые домены), а скрипты роутера - редко: так их можно обновлять без нового выпуска продукта.
- Любой может предложить домен (Pull Request / Issue) и увидеть историю: что и почему добавлено.
- Роутер получает только готовые маленькие файлы из `dist/`.

## Что внутри
| Файл | Назначение |
|---|---|
| `lists/ads-ru.txt` | **российские** рекламные сети, счётчики, трекеры |
| `lists/ads-global.txt` | остальные страны (мировые рекламные и трекерные домены) |
| `tools/build.py` | собирает по одному файлу `dist/geosite_ADS-<ИМЯ>.dat` на каждый список (`ads-ru.txt` → `geosite_ADS-RU.dat`, тег `ADS-RU`; `ads-global.txt` → `geosite_ADS-GLOBAL.dat`, тег `ADS-GLOBAL`); пустой список файл не создаёт |
| `dist/` | готовые файлы для роутера (создаются `build.py`; в Git хранятся) |

Разделение на RU и остальные нужно, чтобы можно было включать их независимо (например, российский список - только тем, кто пользуется российскими сервисами).

## Формат списка
```
# комментарий
example-ads.com              # домен и все поддомены
full:tracker.example.net     # только точное имя
regexp:^ad[0-9]+\.example\.org$   # регулярное выражение
```
Не добавляйте домены, без которых сайт перестаёт работать (CDN, API, логин): блокируются **все** запросы к домену. Перед добавлением проверьте домен, чтобы он действительно рекламный/счётчик (например, DevTools браузера, вкладка «Сеть»).

## Как собрать
```
python tools/build.py          # -> dist/geosite_ADS-RU.dat (и другие)
```

## Как подключить на роутере (проект OpenWRT-VM-PROXY)
PassWall2 не поддерживает записи `ext:` в правилах, поэтому файл дописывается в стандартный `geosite.dat` командой `pw2-geosite` и становится обычным тегом `geosite:ads-ru`:
1. Положить `geosite_ADS-RU.dat` на роутер в `/usr/share/pw2/data/` (например `ssh openwrt "cat > /usr/share/pw2/data/geosite_ADS-RU.dat" < dist\geosite_ADS-RU.dat`).
2. `ssh openwrt pw2-geosite merge`.
3. В `/etc/pw2-routing.conf` добавить `ADS_GEOSITE_EXTRA="geosite:ads-ru"`, затем `pw2-routing-apply`.
(В планах: команда `pw2-ads update`, которая сама скачает файлы из этого репозитория; пока - вручную.)

## Правила для вкладов
- Только публичные домены рекламных и трекерных сервисов. **Никаких** личных данных, адресов почты, IP-адресов, ссылок с токенами.
- Один домен - одна строка, в комментарии указывайте источник или причину.

## Лицензия
MIT - см. [LICENSE](LICENSE). Автор: quantum-fox.
