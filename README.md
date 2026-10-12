# OpenWRT-VM-PROXY-ads: база рекламных и трекерных доменов

> **English summary.** A self-contained, regularly updated base of advertising / tracker / counter domains for the **OpenWRT-VM-PROXY** router project (~205k domains). `lists/upstream` stores the merged public sources as plain text (runetfreedom, AdGuard DNS filter, Peter Lowe's list; deduplicated), `lists/own` holds the maintainer's additions. `tools/build.py` produces ready Xray/v2ray `geosite` files in `dist/`: `geosite_ADS-RU.dat` (tag `ADS-RU`, Russian zones + own RU entries) and `geosite_ADS-GLOBAL.dat` (tag `ADS-GLOBAL`, everything else). On the router, `pw2-geosite` appends the files to `geosite.dat` (PassWall2 ignores `ext:` entries) and they are used as `geosite:ads-ru` / `geosite:ads-global`. License: GPL-3.0 (see `NOTICE.md`). Documentation is in Russian.

Полная собственная база рекламных и трекерных доменов (~205 тысяч) для прокси-роутера проекта **OpenWRT-VM-PROXY**: всё лежит в Git в виде обычного текста, чтобы база всегда была под рукой и её можно было дополнять.

## Что внутри
| Путь | Назначение |
|---|---|
| `lists/upstream/*.txt` | **чужие публичные базы** в виде текста, без повторов между источниками: `runetfreedom.txt` (~149 тыс.), `adguard.txt` (~57 тыс. новых), `peterlowe.txt` (~0,3 тыс. новых) |
| `lists/own/ads-ru.txt`, `lists/own/ads-global.txt` | **ваши дополнения**: российские и зарубежные (сюда добавляйте домены вручную) |
| `tools/update-upstream.py` | скачивает источники и обновляет `lists/upstream/` |
| `tools/build.py` | собирает готовые файлы в `dist/` из `upstream + own` |
| `dist/geosite_ADS-RU.dat` | тег `ADS-RU`: российские зоны (`.ru`, `.su`, `.рф`) + `lists/own/ads-ru.txt` (~1,4 тыс. правил) |
| `dist/geosite_ADS-GLOBAL.dat` | тег `ADS-GLOBAL`: все остальные (~203 тыс. правил, 5,3 МБ) |

Разделение на RU и остальные нужно, чтобы файлы можно было включать независимо. Из `upstream` в RU попадают домены в российских зонах; прочее - в GLOBAL. Российские рекламные сервисы в зонах `.com` и т. п. (например, `yandexadexchange.net`) добавляйте в `lists/own/ads-ru.txt`.

## Как пользоваться
```
python tools/update-upstream.py     # скачать источники (раз в неделю-месяц); при блокировках: --proxy http://10.99.77.1:8080
python tools/build.py               # собрать dist/*.dat (несколько секунд)
git add -A; git commit -m "Обновление базы"; git push
```
Что изменилось после обновления источников - видно в `git diff --stat lists/upstream`.

## Формат `lists/own/*.txt`
```
# комментарий
example-ads.com              # домен и все поддомены
full:tracker.example.net     # только точное имя
regexp:^ad[0-9]+\.example\.org$   # регулярное выражение
```
Не добавляйте домены, без которых сайт перестаёт работать (CDN, API, вход): блокируются **все** запросы к домену. Сайты, чья реклама приходит с тех же адресов, что и сам сайт (YouTube, Авито), этим способом не блокируются - для них нужен uBlock Origin в браузере.

## Как подключить на роутере (проект OpenWRT-VM-PROXY)
Проект уже содержит готовые копии этих файлов и подключает их сам (`pw2-update`, версия 1.3.0 и выше). Вручную, если нужна свежая версия базы:
1. Положить `geosite_ADS-GLOBAL.dat` и `geosite_ADS-RU.dat` на роутер в `/usr/share/pw2/data/` (`ssh openwrt "cat > /usr/share/pw2/data/geosite_ADS-GLOBAL.dat" < dist\geosite_ADS-GLOBAL.dat`, то же для `ADS-RU`).
2. `ssh openwrt pw2-geosite refresh` (подключает файлы к `geosite.dat` заново), затем `pw2-routing-apply`.
PassWall2 не поддерживает записи `ext:` в правилах, поэтому файлы дописываются в стандартный `geosite.dat` командой `pw2-geosite` и используются как `geosite:ads-global` и `geosite:ads-ru`.

## Правила для вкладов
- Только публичные домены рекламных и трекерных сервисов. **Никаких** личных данных, адресов почты, IP-адресов, ссылок с токенами.
- Один домен - одна строка, в комментарии указывайте источник или причину.

## Лицензия
GPL-3.0 - см. [LICENSE](LICENSE) и [NOTICE.md](NOTICE.md) (источники и их лицензии). Автор дополнений: quantum-fox.
