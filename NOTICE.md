# Источники и лицензии

Лицензия репозитория: **GNU GPL v3** (файл [LICENSE](LICENSE)); автор собственных дополнений (`lists/own`, скрипты): quantum-fox.
Причина: база содержит производные данные от источников, распространяемых на условиях GPL-3.0.

| Источник | Что взято | Лицензия |
|---|---|---|
| [runetfreedom/russia-v2ray-rules-dat](https://github.com/runetfreedom/russia-v2ray-rules-dat) (список `category-ads-all`), собран на основе [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) | `lists/upstream/runetfreedom.txt` | GPL-3.0 (v2fly - MIT) |
| [AdGuard DNS filter](https://github.com/AdguardTeam/AdGuardSDNSFilter) | `lists/upstream/adguard.txt` (только простые правила `\|\|домен^`; исключения `@@` учтены) | GPL-3.0 |
| [Peter Lowe's Ad and tracking server list](https://pgl.yoyo.org/adservers/) | `lists/upstream/peterlowe.txt` | на странице списка автор разрешает объединять его с другими и публиковать (формальной лицензии нет) |
| собственные дополнения | `lists/own/*.txt` | GPL-3.0 (как весь репозиторий) |

В `lists/upstream/*.txt` каждый домен записан один раз (в источнике с более высоким приоритетом); в шапке файла - источник, адрес, дата получения.
