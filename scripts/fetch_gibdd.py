"""Выгрузка ДТП по Уфе со stat.gibdd.ru по месяцам.

Запуск из корня репозитория:
    python scripts/fetch_gibdd.py
    python scripts/fetch_gibdd.py --start 2026-09 --end 2026-09   # пробный запуск, один месяц
    python scripts/fetch_gibdd.py --out путь/к/data/raw           # другая папка вывода

Результат:
    <out>/accidents.csv     ДТП без сведений об участниках и автомобилях
    <out>/gibdd_raw/ГГГГ-ММ.json   полные ответы сайта (содержат сведения об участниках;
                                   не публиковать и не коммитить)
Источник: http://stat.gibdd.ru. Условия использования данных на сайте не найдены,
см. карточку DS-01 в data/sources.md.
"""
import argparse
import csv
import json
import time
from pathlib import Path

import requests

BASE = "http://stat.gibdd.ru/map/"
REG, TOWN = "80", "80417"       # Республика Башкортостан, г. Уфа (коды из справочника сайта)
PAGE = 50                       # размер страницы карточек

FIELDS = ["kart_id", "date", "time", "district", "dtp_type", "killed", "injured",
          "vehicles", "participants", "city", "street", "house", "lat", "lon",
          "road_class", "road_elements", "weather", "surface", "lighting", "factors"]


def parse_ym(text):
    y, m = text.split("-")
    return int(y), int(m)


def months(start, end):
    y, m = start
    while (y, m) <= end:
        yield y, m
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)


def make_session():
    s = requests.Session()
    s.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/130.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Content-Type": "application/json;charset=UTF-8",
        "Origin": "http://stat.gibdd.ru",
        "Referer": "http://stat.gibdd.ru/",
    })
    s.get("http://stat.gibdd.ru/", timeout=60)   # куки сессии
    return s


def unwrap(x):
    """Сайт отдаёт JSON внутри строки: раскодируем, пока это строка."""
    while isinstance(x, str):
        try:
            x = json.loads(x)
        except ValueError:
            break
    return x


def post(session, endpoint, payload, tries=3):
    for i in range(tries):
        try:
            r = session.post(BASE + endpoint, json=payload, timeout=60)
            r.raise_for_status()
            return unwrap(r.text)
        except Exception as e:
            print("  ошибка:", e, "· повтор", i + 1)
            time.sleep(5)
    raise RuntimeError(f"запрос {endpoint} не удался")


def fetch_month(session, y, m):
    cards, st = [], 1
    while True:
        inner = {"date": [f"MONTHS:{m}.{y}"], "ParReg": REG,
                 "order": {"type": "1", "fieldName": "dat"}, "reg": TOWN,
                 "ind": "1", "st": str(st), "en": str(st + PAGE - 1)}
        resp = post(session, "getDTPCardData", {"data": json.dumps(inner, separators=(",", ":"))})
        data = unwrap(resp.get("data")) if isinstance(resp, dict) else None
        page = data.get("tab") if isinstance(data, dict) else None
        if not page:
            break
        cards += page
        if len(page) < PAGE:
            break
        st += PAGE
        time.sleep(1)
    return cards


def joined(v):
    return "; ".join(v) if isinstance(v, list) else (v or "")


def to_row(card):
    info = card.get("infoDtp", {})
    return {
        "kart_id": card["KartId"], "date": card["date"], "time": card["Time"],
        "district": card["District"], "dtp_type": card["DTP_V"],
        "killed": card["POG"], "injured": card["RAN"],
        "vehicles": card["K_TS"], "participants": card["K_UCH"],
        "city": info.get("n_p", ""), "street": info.get("street", ""), "house": info.get("house", ""),
        "lat": info.get("COORD_W", ""), "lon": info.get("COORD_L", ""),
        "road_class": info.get("dor_z", ""), "road_elements": joined(info.get("sdor")),
        "weather": joined(info.get("s_pog")), "surface": info.get("s_pch", ""),
        "lighting": info.get("osv", ""), "factors": joined(info.get("factor")),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--start", default="2023-10", help="первый месяц, ГГГГ-ММ")
    ap.add_argument("--end", default="2026-09", help="последний месяц, ГГГГ-ММ")
    ap.add_argument("--out", default="data/raw", help="папка вывода (по умолчанию data/raw)")
    args = ap.parse_args()

    out = Path(args.out)
    raw = out / "gibdd_raw"
    raw.mkdir(parents=True, exist_ok=True)
    session = make_session()

    for y, m in months(parse_ym(args.start), parse_ym(args.end)):
        f = raw / f"{y}-{m:02d}.json"
        if f.exists():
            continue                                  # месяц уже скачан
        cards = fetch_month(session, y, m)
        print(f"{m:02d}.{y}: {len(cards)} карточек")
        if cards:                                     # пустые месяцы не кэшируем
            f.write_text(json.dumps(cards, ensure_ascii=False), encoding="utf-8")
        time.sleep(2)

    rows, seen = [], set()
    for f in sorted(raw.glob("*.json")):
        for card in json.loads(f.read_text(encoding="utf-8")):
            if card["KartId"] not in seen:
                seen.add(card["KartId"])
                rows.append(to_row(card))
    if not rows:
        print("Нет данных: проверьте доступ к сайту и период.")
        return
    with open(out / "accidents.csv", "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    with_xy = sum(1 for r in rows if r["lat"] and r["lon"])
    print(f"Всего ДТП: {len(rows)} · с координатами: {with_xy} · файл: {out / 'accidents.csv'}")


if __name__ == "__main__":
    main()