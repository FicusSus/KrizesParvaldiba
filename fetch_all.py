#!/usr/bin/env python3
"""Скачивает доступные источники в SQLite (latvia.db). Только stdlib.
Запуск из папки latvia-data:  python3 scripts/fetch_all.py
Источники со status=needs_endpoint (см. data/sources.json) требуют сначала найти URL данных."""
import csv, html, io, json, re, sqlite3, time, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "latvia.db"
UA = {"User-Agent": "Mozilla/5.0 (latvia-data fetcher)"}

def get(url):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return r.read().decode("utf-8-sig", errors="replace")

def num(x):
    try: return float(x)
    except (TypeError, ValueError): return None

def load_hydro(con):
    sources = json.loads((ROOT / "data/sources.json").read_text(encoding="utf-8"))
    url = next(s["csv"] for s in sources if s["id"] == "hydro")
    rows = csv.DictReader(io.StringIO(get(url)))
    con.executemany(
        "INSERT OR REPLACE INTO hydro_forecast VALUES (?,?,?,?,?,?,?,?,?,?)",
        [(r["DATUMS"][:10], r["STATION_ID"], r["PARAM"],
          *(num(r[k]) for k in ("MINIM", "V95", "V75", "MEDIANA", "V25", "V5", "MAXIM"))) for r in rows])
    con.execute("INSERT OR IGNORE INTO hydro_station(id) SELECT DISTINCT station_id FROM hydro_forecast")
    print("hydro_forecast:", con.execute("select count(*) from hydro_forecast").fetchone()[0])

def load_fuel(con, max_pages=40):
    """Best-effort разбор HTML каталога viss.lv — результат стоит проверить глазами."""
    total = 0
    for page in range(1, max_pages + 1):
        page_html = get(f"https://viss.lv/katalogs/degvielas_uzpildes_stacijas?page={page}")
        found = {}
        for pid, title, inner in re.findall(
                r'<a[^>]+href="https://viss\.lv/\?p=(\d+)"[^>]*title="([^"]+)"[^>]*>(.*?)</a>', page_html, re.S):
            t = html.unescape(title)
            text = html.unescape(re.sub(r"<[^>]+>", " ", inner)).strip()
            if text.startswith(t) and len(text) > len(t):
                found[int(pid)] = (t, text[len(t):].strip())
        if not found:
            break
        for pid, (name, addr) in found.items():
            con.execute("INSERT OR REPLACE INTO fuel_station(viss_id,name,address) VALUES (?,?,?)", (pid, name, addr))
        total += len(found)
        time.sleep(1)
    print("fuel_station:", total)

if __name__ == "__main__":
    con = sqlite3.connect(DB)
    con.executescript((ROOT / "schema.sql").read_text(encoding="utf-8"))
    load_hydro(con)
    load_fuel(con)
    con.commit()
    print("OK ->", DB)
