# latvia-data — открытые данные для веб-приложения

Файлы:
- `schema.sql` — схема БД (SQLite/PostgreSQL) под все 9 источников
- `data/sources.json` — каталог источников: URL, лицензия, статус, что делать дальше
- `data/fuel_stations_sample.json` — пример формата (10 из 485 АЗС, без координат)
- `scripts/fetch_all.py` — загрузка в `latvia.db` (hydro — готово, АЗС — best-effort)

Статусы в sources.json: `ready` / `ready_html` — можно качать скриптом; `needs_endpoint` — страница рисуется JS, нужен URL данных из DevTools → Network (или со страницы карточки на transportdata.gov.lv).
Координаты АЗС нужно получить отдельно (карта viss.lv или геокодирование адресов).
