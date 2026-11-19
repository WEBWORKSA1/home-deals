#!/usr/bin/env python3
"""Home.Deals data refresh.

Pulls every self-updating data set the site shows and writes compact JSON
files into /data. Standard library only, so it runs on a stock GitHub
Actions runner with no install step.

Design rules
  * Public, key-free sources only (U.S. government open data, Freddie Mac
    averages published through FRED, public YouTube channel feeds).
  * A failed source never wipes good data: the previous file is kept and the
    failure is written to data/_status.json.
  * Output files hold no run timestamp, so an unchanged source produces no
    git diff. Only _status.json records when the run happened.
"""
from __future__ import annotations

import csv
import datetime as dt
import gzip
import io
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
DATA.mkdir(exist_ok=True)

UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
      "Chrome/126.0 Safari/537.36 HomeDealsBot/1.0 (+https://home.deals/editorial-policy/)")

STATUS: dict = {"sources": {}}
TODAY = dt.datetime.now(dt.timezone.utc).date()


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def fetch(url: str, timeout: int = 40, headers: dict | None = None, retries: int = 2) -> bytes:
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": UA,
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip",
                **(headers or {}),
            })
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read()
                if resp.headers.get("Content-Encoding", "").lower() == "gzip" or raw[:2] == b"\x1f\x8b":
                    try:
                        raw = gzip.decompress(raw)
                    except OSError:
                        pass
                return raw
        except Exception as exc:  # noqa: BLE001 - every failure is reported, none is fatal
            last = exc
            time.sleep(2 + attempt * 3)
    raise RuntimeError(f"{type(last).__name__}: {last}")


def load(name: str, default=None):
    path = DATA / name
    if path.exists():
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return default
    return default


def save(name: str, obj) -> None:
    text = json.dumps(obj, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
    (DATA / name).write_text(text, encoding="utf-8")


def record(name: str, ok: bool, **info) -> None:
    STATUS["sources"][name] = {"ok": ok, **info}
    flag = "ok " if ok else "ERR"
    print(f"[{flag}] {name}: {info}", flush=True)


def clean(text: str | None, limit: int = 0) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", str(text))
    text = (text.replace("&nbsp;", " ").replace("&amp;", "&").replace("&quot;", '"')
            .replace("&#39;", "'").replace("&rsquo;", "'").replace("&lsquo;", "'")
            .replace("&ldquo;", '"').replace("&rdquo;", '"').replace("&ndash;", "-")
            .replace("&mdash;", "-").replace("&reg;", "").replace("&trade;", ""))
    # the site never publishes email addresses, including ones quoted in public notices
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", "the address in the official notice", text)
    text = re.sub(r"\s+", " ", text).strip()
    if limit and len(text) > limit:
        cut = text[:limit].rsplit(" ", 1)[0].rstrip(",;:. ")
        text = cut + "…"
    return text


# --------------------------------------------------------------------------
# FRED (St. Louis Fed) CSV — no API key needed
# --------------------------------------------------------------------------
def fred_series(series_id: str, start: str) -> list[list]:
    url = ("https://fred.stlouisfed.org/graph/fredgraph.csv?"
           + urllib.parse.urlencode({"id": series_id, "cosd": start}))
    raw = fetch(url).decode("utf-8-sig", "replace")
    rows = list(csv.reader(io.StringIO(raw)))
    if not rows or len(rows[0]) < 2 or "date" not in rows[0][0].lower():
        raise RuntimeError(f"unexpected CSV header: {rows[:1]!r}")
    out = []
    for row in rows[1:]:
        if len(row) < 2:
            continue
        date, val = row[0].strip(), row[1].strip()
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            continue
        try:
            out.append([date, float(val)])
        except ValueError:
            continue  # "." marks a missing observation
    if not out:
        raise RuntimeError("no observations parsed")
    return out


def pct(a: float, b: float) -> float:
    return round((a / b - 1.0) * 100.0, 2)


def value_near(obs: list[list], target: dt.date, tolerance_days: int) -> tuple[float, str, bool] | None:
    """Observation closest to target date (exact month preferred)."""
    best = None
    for date, val in obs:
        d = dt.date.fromisoformat(date)
        gap = abs((d - target).days)
        if gap <= tolerance_days and (best is None or gap < best[0]):
            best = (gap, val, date)
    if best is None:
        return None
    return best[1], best[2], best[0] > 20


def year_ago_value(obs: list[list], d: dt.date) -> tuple[float, bool] | None:
    """Value 12 months before d. If that month was never published (for
    example the October 2025 CPI gap), use the geometric mean of the months
    on either side and flag the result as approximate."""
    by_month = {x[0][:7]: x[1] for x in obs}
    key = lambda n: months_back(d, n).isoformat()[:7]  # noqa: E731
    if key(12) in by_month:
        return by_month[key(12)], False
    before, after = by_month.get(key(13)), by_month.get(key(11))
    if before and after:
        return (before * after) ** 0.5, True
    if before or after:
        return (before or after), True
    return None


def months_back(d: dt.date, n: int) -> dt.date:
    y, m = d.year, d.month - n
    while m <= 0:
        y, m = y - 1, m + 12
    return dt.date(y, m, 1)


# --------------------------------------------------------------------------
# 1. Mortgage rates — Freddie Mac PMMS weekly averages
# --------------------------------------------------------------------------
def freddie_csv() -> dict[str, list[list]]:
    raw = fetch("https://www.freddiemac.com/pmms/docs/PMMS_history.csv").decode("utf-8-sig", "replace")
    rows = list(csv.reader(io.StringIO(raw)))
    head = [h.strip().lower() for h in rows[0]]
    idx30, idx15 = head.index("pmms30"), head.index("pmms15")
    out = {"30": [], "15": []}
    for row in rows[1:]:
        try:
            d = dt.datetime.strptime(row[0].strip(), "%m/%d/%Y").date()
        except (ValueError, IndexError):
            continue
        if d < dt.date(2021, 1, 1):
            continue
        for key, idx in (("30", idx30), ("15", idx15)):
            try:
                out[key].append([d.isoformat(), float(row[idx])])
            except (ValueError, IndexError):
                pass
    if not out["30"]:
        raise RuntimeError("no PMMS rows parsed")
    return out


def update_rates() -> None:
    series, via = {}, "FRED"
    try:
        series["30"] = fred_series("MORTGAGE30US", "2021-01-01")
        series["15"] = fred_series("MORTGAGE15US", "2021-01-01")
    except Exception as exc:  # noqa: BLE001
        first_error = str(exc)
        try:
            series, via = freddie_csv(), "Freddie Mac"
        except Exception as exc2:  # noqa: BLE001
            record("rates", False, error=f"FRED: {first_error} | Freddie Mac: {exc2}")
            return
    out = {
        "source": "Freddie Mac Primary Mortgage Market Survey (weekly U.S. averages)",
        "via": via,
        "series": series,
        "summary": {},
    }
    for key, obs in series.items():
        if not obs:
            continue
        last_date, last = obs[-1]
        prev = obs[-2][1] if len(obs) > 1 else last
        year = obs[-52:]
        year_ago = value_near(obs, dt.date.fromisoformat(last_date) - dt.timedelta(days=364), 10)
        out["summary"][key] = {
            "date": last_date,
            "rate": last,
            "week_change": round(last - prev, 2),
            "high_52w": max(v for _, v in year),
            "low_52w": min(v for _, v in year),
            "year_ago": year_ago[0] if year_ago else None,
        }
    save("rates.json", out)
    record("rates", True, via=via, latest=out["summary"].get("30"))


# --------------------------------------------------------------------------
# 2. Price Pulse — BLS consumer price indexes for home categories
# --------------------------------------------------------------------------
CPI_SERIES = [
    # key, BLS series id (CPI-U, U.S. city average, not seasonally adjusted), label
    ("all", "CUUR0000SA0", "All items (overall inflation)"),
    ("furnishings", "CUUR0000SAH3", "Household furnishings and operations"),
    ("furniture", "CUUR0000SEHJ", "Furniture and bedding"),
    ("appliances", "CUUR0000SEHK", "Appliances"),
    ("major_appliances", "CUUR0000SEHK01", "Major appliances"),
    ("tools", "CUUR0000SEHM", "Tools, hardware, outdoor equipment and supplies"),
    ("linens", "CUUR0000SEHH", "Window and floor coverings and other linens"),
    ("decor", "CUUR0000SEHL", "Other household equipment and furnishings"),
    ("housekeeping", "CUUR0000SEHN", "Housekeeping supplies"),
    ("tvs", "CUUR0000SERA01", "Televisions"),
    ("energy", "CUUR0000SAH21", "Household energy"),
    ("electricity", "CUUR0000SEHF01", "Electricity"),
]
# FRED carries only some of these; used when the BLS API is unreachable.
FRED_CPI_FALLBACK = {"all": "CPIAUCNS", "furnishings": "CUUR0000SAH3", "energy": "CUUR0000SAH21",
                     "electricity": "CUUR0000SEHF01"}


def bls_series(ids: list[str], start_year: int, end_year: int) -> dict[str, list[list]]:
    """One POST to the BLS public API v1 (no key). Returns {id: [[YYYY-MM-01, value], ...]} oldest first."""
    body = json.dumps({"seriesid": ids, "startyear": str(start_year), "endyear": str(end_year)}).encode()
    req = urllib.request.Request("https://api.bls.gov/publicAPI/v1/timeseries/data/", data=body, method="POST",
                                 headers={"Content-Type": "application/json", "User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as resp:
        payload = json.loads(resp.read().decode("utf-8", "replace"))
    if payload.get("status") != "REQUEST_SUCCEEDED":
        raise RuntimeError(f"BLS status {payload.get('status')}: {payload.get('message')}")
    out = {}
    for serie in payload.get("Results", {}).get("series", []):
        rows = []
        for item in serie.get("data", []):
            period = item.get("period", "")
            if not re.match(r"^M(0[1-9]|1[0-2])$", period):
                continue  # skip annual and half-year averages
            try:
                rows.append([f"{item['year']}-{period[1:]}-01", float(item["value"])])
            except (KeyError, ValueError):
                continue  # "-" marks a month that was never published
        rows.sort()
        if rows:
            out[serie.get("seriesID", "")] = rows
    return out


def series_metrics(obs: list[list]) -> dict:
    last_date, last = obs[-1]
    d = dt.date.fromisoformat(last_date)
    out = {"date": last_date, "index": round(last, 3)}
    base = year_ago_value(obs, d)
    if base:
        out["yoy"] = pct(last, base[0])
        out["yoy_approx"] = bool(base[1])
    # the same comparison three published months earlier shows which way prices are heading
    if len(obs) > 3:
        d3_date, d3_val = obs[-4]
        base3 = year_ago_value(obs, dt.date.fromisoformat(d3_date))
        if base3:
            out["yoy_3m_ago"] = pct(d3_val, base3[0])
            if "yoy" in out:
                out["momentum"] = round(out["yoy"] - out["yoy_3m_ago"], 2)
    out["spark"] = [[x[0][:7], round(x[1], 2)] for x in obs[-37:]]
    return out


def update_pulse() -> None:
    result, errors, via = {}, {}, "BLS public API"
    try:
        data = bls_series([sid for _, sid, _ in CPI_SERIES], TODAY.year - 4, TODAY.year)
        for key, sid, label in CPI_SERIES:
            if data.get(sid) and len(data[sid]) > 14:
                result[key] = {"id": sid, "label": label, **series_metrics(data[sid])}
            else:
                errors[sid] = "not returned"
    except Exception as exc:  # noqa: BLE001
        errors["bls"] = str(exc)[:200]
    if "all" not in result:
        via = "FRED"
        start = (TODAY - dt.timedelta(days=365 * 4 + 40)).isoformat()
        for key, sid, label in CPI_SERIES:
            fred_id = FRED_CPI_FALLBACK.get(key)
            if not fred_id or key in result:
                continue
            try:
                result[key] = {"id": sid, "label": label, **series_metrics(fred_series(fred_id, start))}
            except Exception as exc:  # noqa: BLE001
                errors[fred_id] = str(exc)[:160]
            time.sleep(0.6)
    if "all" not in result or len(result) < 4:
        record("pulse", False, error=errors or "too few series")
        return
    previous = (load("pulse.json", {}) or {}).get("series", {})
    if len(result) < len(previous) and previous.get("all", {}).get("date") == result["all"]["date"]:
        # a thinner answer for the same month: keep the fuller file we already have
        record("pulse", True, kept_previous=True, series=len(previous), skipped=errors)
        return
    save("pulse.json", {
        "source": "U.S. Bureau of Labor Statistics, Consumer Price Index for All Urban Consumers (U.S. city average, not seasonally adjusted)",
        "via": via,
        "series": result,
    })
    record("pulse", True, via=via, series=len(result), latest=result["all"]["date"], skipped=errors)


# --------------------------------------------------------------------------
# 3. Housing market inputs (public-domain federal series) + energy prices
# --------------------------------------------------------------------------
def update_market() -> None:
    wanted = [
        ("months_supply", "MSACSR", "Monthly supply of new houses (Census Bureau / HUD)"),
        ("hpi", "HPIPONM226S", "FHFA purchase-only house price index, seasonally adjusted"),
        ("median_price", "MSPUS", "Median sales price of houses sold (Census Bureau / HUD)"),
        ("new_home_sales", "HSN1F", "New one-family houses sold, annual rate, thousands (Census Bureau / HUD)"),
    ]
    start = (TODAY - dt.timedelta(days=365 * 6)).isoformat()
    result, errors = {}, {}
    for key, sid, label in wanted:
        try:
            obs = fred_series(sid, start)
            last_date, last = obs[-1]
            item = {"id": sid, "label": label, "date": last_date, "value": last,
                    "spark": [[x[0][:7], x[1]] for x in obs[-25:]]}
            base = value_near(obs, months_back(dt.date.fromisoformat(last_date), 12), 50)
            if base:
                item["yoy"] = pct(last, base[0])
                item["year_ago"] = base[0]
            result[key] = item
        except Exception as exc:  # noqa: BLE001
            errors[sid] = str(exc)
        time.sleep(0.6)
    if len(result) < 2:
        record("market", False, error=errors)
        return
    save("market.json", {"source": "U.S. Census Bureau, HUD and FHFA series retrieved from FRED", "series": result})
    record("market", True, series=list(result), skipped=errors)


def update_energy() -> None:
    wanted = [
        ("electricity_kwh", "APU000072610", "Average price of electricity per kWh, U.S. city average (BLS)"),
        ("gas_therm", "APU000072620", "Average price of utility (piped) gas per therm, U.S. city average (BLS)"),
    ]
    start = (TODAY - dt.timedelta(days=365 * 3)).isoformat()
    result, errors = {}, {}
    for key, sid, label in wanted:
        try:
            obs = fred_series(sid, start)
            last_date, last = obs[-1]
            item = {"id": sid, "label": label, "date": last_date, "value": last}
            base = value_near(obs, months_back(dt.date.fromisoformat(last_date), 12), 50)
            if base:
                item["yoy"] = pct(last, base[0])
            result[key] = item
        except Exception as exc:  # noqa: BLE001
            errors[sid] = str(exc)
        time.sleep(0.6)
    if not result:
        record("energy", False, error=errors)
        return
    save("energy.json", {"source": "U.S. Bureau of Labor Statistics average price data, retrieved from FRED", "series": result})
    record("energy", True, series=list(result), skipped=errors)


# --------------------------------------------------------------------------
# 4. Product recalls — U.S. Consumer Product Safety Commission open API
# --------------------------------------------------------------------------
RECALL_RULES = [
    # (category slug, regex). First match wins, so specific rules come first.
    ("nursery", r"\b(crib|bassinet|high ?chairs?|baby gate|play ?yard|playpen|infant|nursery|toddler bed|changing table|baby loungers?|crib bumpers?|swaddle)"),
    ("mattresses", r"\b(mattress(es)?|bed rails?|pillows?|weighted blankets?|electric blankets?|heated blankets?|comforters?|bedding|duvets?)\b"),
    ("kitchen", r"\b(air fryers?|pressure cookers?|multi-?cookers?|blenders?|toasters?|toaster ovens?|coffee ?makers?|espresso|kettles?|slow cookers?|rice cookers?|cookware|frying pans?|sauce ?pans?|dutch ovens?|knife|knives|juicers?|food processors?|stand mixers?|waffle|griddles?|mugs?|tumblers?|drinkware|bakeware|cutting boards?)\b"),
    ("appliances", r"\b(ranges?|ovens?|cooktops?|stoves?|refrigerators?|mini ?fridges?|freezers?|dishwashers?|clothes washers?|washing machines?|dryers?|microwaves?|range hoods?|water heaters?|garbage disposals?|ice makers?|wine coolers?)\b"),
    ("heating-cooling", r"\b(space heaters?|heaters?|fireplaces?|fire tables?|ceiling fans?|fans?|air conditioners?|dehumidifiers?|humidifiers?|furnaces?|heat pumps?|thermostats?|air purifiers?|boilers?|wood stoves?|pellet stoves?)\b"),
    ("smart-home", r"\b(smoke alarms?|smoke detectors?|carbon monoxide|co alarms?|power strips?|extension cords?|surge protectors?|outlets?|circuit breakers?|doorbells?|security cameras?|smart locks?|garage door openers?|light switches|dimmers?|gfci|electrical panels?|power banks?|portable chargers?)\b"),
    ("cleaning", r"\b(vacuums?|steam cleaners?|steam mops?|carpet cleaners?|robot(ic)? vacuums?|mops?)\b"),
    ("tools", r"\b(saws?|drills?|nailers?|grinders?|sanders?|ladders?|step stools?|power tools?|generators?|pressure washers?|air compressors?|workbench(es)?|jack stands?|chainsaws?|log splitters?|impact drivers?|routers|utility knives|multi-?tools?|clamps?|tool sets?|welders?|hoists?)\b"),
    ("outdoor", r"\b(grills?|fire pits?|patio|umbrellas?|hammocks?|pools?|lawn mowers?|mowers?|string trimmers?|leaf blowers?|snow (blowers?|throwers?)|garden|hoses?|porch swings?|gazebos?|playsets?|swing sets?|trampolines?|pergolas?|outdoor furniture|hot tubs?|spas?|planters?|torches?)\b"),
    ("furniture", r"\b(dressers?|chests?|nightstands?|bookcases?|bookshelves|cabinets?|chairs?|stools?|sofas?|couch(es)?|tables?|desks?|beds?|bed frames?|bunk beds?|futons?|recliners?|ottomans?|shelves|shelving|armoires?|vanit(y|ies)|benches|tv stands?|wardrobes?|loveseats?|sectionals?|furniture)\b"),
    ("decor-lighting", r"\b(lamps?|lights?|lighting|lanterns?|candles?|chandeliers?|sconces?|mirrors?|rugs?|curtains?|blinds|window coverings?|shades|roman shades|wall art|bulbs?|led strips?|night ?lights?|christmas trees?|holiday decorations?|wax warmers?|diffusers?)\b"),
]
RECALL_EXCLUDE = re.compile(
    r"\b(sterilizers?|bottle warmers?|e-?bikes?|bicycles?|scooters?|hoverboards?|helmets?|atvs?|utvs?|off-road|motorcycles?|pajamas?|sleepwear|"
    r"hoodies?|jackets?|clothing|garments?|necklaces?|jewelry|toys?|dolls?|rattles?|teethers?|pacifiers?|strollers?|"
    r"car seats?|magnets?|firearms?|rifles?|crossbows?|golf carts?|snowmobiles?|kayaks?|life jackets?|skis?|"
    r"climbing|backpacks?|vapes?|medication|supplements?|minoxidil|pills?|treadmills?|exercise|dumbbells?)\b", re.I)


def classify_recall(title: str, products: str) -> str | None:
    text = f"{title} {products}".lower()
    title_l = title.lower()
    for slug, pattern in RECALL_RULES:
        if re.search(pattern, title_l, re.I):
            if RECALL_EXCLUDE.search(title_l) and slug not in ("nursery", "mattresses"):
                # e.g. "E-bike battery chargers": not a home-goods recall
                if not re.search(pattern, re.sub(RECALL_EXCLUDE, " ", title_l), re.I):
                    return None
            return slug
    if RECALL_EXCLUDE.search(title_l):
        return None
    for slug, pattern in RECALL_RULES:
        if re.search(pattern, text, re.I):
            return slug
    return None


def names(items, key="Name") -> list[str]:
    out = []
    for item in items or []:
        value = clean(item.get(key) if isinstance(item, dict) else item)
        if value and value not in out:
            out.append(value)
    return out


def update_recalls() -> None:
    start = (TODAY - dt.timedelta(days=300)).isoformat()
    url = "https://www.saferproducts.gov/RestWebServices/Recall?" + urllib.parse.urlencode(
        {"format": "json", "RecallDateStart": start})
    try:
        payload = json.loads(fetch(url, timeout=90).decode("utf-8", "replace"))
    except Exception as exc:  # noqa: BLE001
        record("recalls", False, error=str(exc), url=url)
        return
    if not isinstance(payload, list):
        record("recalls", False, error=f"unexpected payload type {type(payload).__name__}")
        return
    out, seen_all = [], 0
    for rec in payload:
        seen_all += 1
        title = clean(rec.get("Title"))
        date = str(rec.get("RecallDate") or "")[:10]
        if not title or not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            continue
        products = names(rec.get("Products"))
        slug = classify_recall(title, " ".join(products))
        if not slug:
            continue
        units = ""
        for p in rec.get("Products") or []:
            units = clean(p.get("NumberOfUnits")) or units
        link = clean(rec.get("URL"))
        if not link.startswith("http"):
            continue
        out.append({
            "id": rec.get("RecallID"),
            "number": clean(rec.get("RecallNumber")),
            "date": date,
            "title": title,
            "cat": slug,
            "hazard": clean("; ".join(names(rec.get("Hazards"))), 210),
            "remedy": clean("; ".join(names(rec.get("Remedies"))), 190),
            "remedy_type": names(rec.get("RemedyOptions"), "Option")[:3],
            "units": clean(units, 60),
            "sold_at": clean((names(rec.get("Retailers")) or [""])[0], 120),
            "url": link.replace("http://", "https://"),
        })
    out.sort(key=lambda r: (r["date"], r["id"] or 0), reverse=True)
    out = out[:90]
    if not out:
        record("recalls", False, error=f"0 home recalls matched out of {seen_all}")
        return
    save("recalls.json", {
        "source": "U.S. Consumer Product Safety Commission recall database (SaferProducts.gov API)",
        "window_start": start,
        "items": out,
    })
    record("recalls", True, total_in_window=seen_all, home_related=len(out), newest=out[0]["date"])


# --------------------------------------------------------------------------
# 5. Video hub — public YouTube channel feeds
# --------------------------------------------------------------------------
CHANNELS = [
    # handle, topic. A handle that stops resolving is skipped and reported, never fatal.
    ("thisoldhouse", "repairs"),
    ("HomeRenoVisionDIY", "repairs"),
    ("familyhandyman", "repairs"),
    ("EverydayHomeRepairs", "repairs"),
    ("seejanedrill", "repairs"),
    ("HomeRepairTutor", "repairs"),
    ("TheHonestCarpenter", "repairs"),
    ("LRN2DIY", "repairs"),
    ("vancouvercarpenter", "repairs"),
    ("StudPack", "projects"),
    ("essentialcraftsman", "projects"),
    ("Fixthisbuildthat", "projects"),
    ("buildshow", "projects"),
    ("AprilWilkerson", "projects"),
    ("Lowes", "projects"),
    ("homedepot", "projects"),
    ("ProjectFarm", "buying"),
    ("consumerreports", "buying"),
    ("BobVila", "buying"),
    ("TechnologyConnections", "energy"),
]
SKIP_TITLE = re.compile(r"(#shorts?\b|commission meeting|livestream|live stream|\blive\b:|trailer|giveaway)", re.I)
YT_HEADERS = {"Cookie": "CONSENT=YES+cb; SOCS=CAI"}
CHANNEL_ID_PATTERNS = [
    r'"externalId":"(UC[0-9A-Za-z_-]{22})"',
    r'<link rel="canonical" href="https://www\.youtube\.com/channel/(UC[0-9A-Za-z_-]{22})"',
    r'feeds/videos\.xml\?channel_id=(UC[0-9A-Za-z_-]{22})',
    r'"browseId":"(UC[0-9A-Za-z_-]{22})"',
    r'"channelId":"(UC[0-9A-Za-z_-]{22})"',
]
NS = {"a": "http://www.w3.org/2005/Atom", "yt": "http://www.youtube.com/xml/schemas/2015",
      "media": "http://search.yahoo.com/mrss/"}


def resolve_channel(handle: str) -> str:
    page = fetch(f"https://www.youtube.com/@{handle}", headers=YT_HEADERS, retries=1).decode("utf-8", "replace")
    for pattern in CHANNEL_ID_PATTERNS:
        m = re.search(pattern, page)
        if m:
            return m.group(1)
    raise RuntimeError("channel id not found in page")


def update_videos() -> None:
    cache = load("youtube_channels.json", {}) or {}
    videos, failures = [], {}
    for handle, topic in CHANNELS:
        try:
            info = cache.get(handle) or {}
            if not info.get("id"):
                info = {"id": resolve_channel(handle)}
                time.sleep(1.0)
            feed = fetch("https://www.youtube.com/feeds/videos.xml?channel_id=" + info["id"], retries=1)
            root = ET.fromstring(feed)
            name = (root.findtext("a:title", default="", namespaces=NS) or handle).strip()
            info["name"] = name
            cache[handle] = info
            kept = 0
            for entry in root.findall("a:entry", NS):
                vid = entry.findtext("yt:videoId", default="", namespaces=NS)
                title = clean(entry.findtext("a:title", default="", namespaces=NS))
                published = (entry.findtext("a:published", default="", namespaces=NS) or "")[:10]
                link = entry.find("a:link", NS)
                href = link.get("href", "") if link is not None else ""
                if not re.match(r"^[0-9A-Za-z_-]{11}$", vid) or not title:
                    continue
                if "/shorts/" in href or SKIP_TITLE.search(title):
                    continue
                videos.append({"id": vid, "title": title[:140], "channel": name, "handle": handle,
                               "topic": topic, "published": published})
                kept += 1
                if kept >= 3:
                    break
            time.sleep(0.5)
        except Exception as exc:  # noqa: BLE001
            failures[handle] = str(exc)[:160]
    save("youtube_channels.json", cache)
    if len(videos) < 6:
        record("videos", False, error="too few videos", failures=failures)
        return
    videos.sort(key=lambda v: v["published"], reverse=True)
    save("videos.json", {"source": "Public YouTube channel feeds; videos play in the official YouTube player",
                         "items": videos[:60]})
    record("videos", True, videos=len(videos), channels=len(cache), failures=failures)


# --------------------------------------------------------------------------
# 6. Consumer alerts — Federal Trade Commission feeds (public domain)
# --------------------------------------------------------------------------
FTC_FEEDS = [
    "https://consumer.ftc.gov/blog/gd-rss.xml",
    "https://www.ftc.gov/feeds/press-release-consumer-protection.xml",
]
ALERT_BROAD = re.compile(
    r"\b(home|house|housing|contractors?|home repair|roof|solar|utility|utilities|mortgage|rent|rental|renters?|"
    r"landlord|moving|movers|warranty|appliances?|furniture|mattress|foreclosure|real estate|homeowners?|hvac|"
    r"energy bill|storm|disaster|flood|wildfire|hurricane|tornado|online shopping|holiday shopping|black friday|"
    r"cyber monday|fake reviews?|price|pricing|hidden fees?|junk fees?|sales? tax|rebates?)\b", re.I)
ALERT_STRICT = re.compile(
    r"\b(homes?|housing|rent|rental|landlord|tenants?|mortgage|contractor|solar|appliances?|furniture|mattress|"
    r"warranty|moving|price transparency|advertised|shelf|overcharg|junk fees?|fake reviews?|retail|stores|"
    r"shopping|refunds?|made in usa)\b", re.I)
ALERT_SKIP = re.compile(r"\b(auto|car|vehicle|dealership|crypto|health|medical|telehealth|ads auction|merger|acquisition|workshop|commissioner|testif)", re.I)


def parse_feed(raw: bytes) -> list[dict]:
    root = ET.fromstring(raw)
    items = []
    for node in root.iter():
        tag = node.tag.rsplit("}", 1)[-1]
        if tag not in ("item", "entry"):
            continue
        fields = {}
        for child in node:
            ctag = child.tag.rsplit("}", 1)[-1]
            if ctag == "link":
                fields["link"] = (child.text or "").strip() or child.get("href", "")
            elif ctag in ("title", "pubDate", "published", "updated", "date", "description", "summary"):
                fields.setdefault(ctag, (child.text or "").strip())
        items.append(fields)
    return items


def parse_date(text: str) -> str:
    text = (text or "").strip()
    for fmt in ("%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %Z", "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%d"):
        try:
            return dt.datetime.strptime(text[:31], fmt).date().isoformat()
        except ValueError:
            continue
    m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
    if m:
        return m.group(1)
    m = re.search(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b", text)  # e.g. "Thu, 11/12/2026 - 10:00"
    if m:
        try:
            return dt.date(int(m.group(3)), int(m.group(1)), int(m.group(2))).isoformat()
        except ValueError:
            return ""
    m = re.search(r"\b(\d{1,2}) (Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* (\d{4})\b", text)
    if m:
        try:
            return dt.datetime.strptime(f"{m.group(1)} {m.group(2)} {m.group(3)}", "%d %b %Y").date().isoformat()
        except ValueError:
            return ""
    return ""


def update_alerts() -> None:
    tried, items = {}, []
    for url in FTC_FEEDS:
        try:
            parsed = parse_feed(fetch(url, retries=1))
            tried[url] = len(parsed)
            for it in parsed:
                title, link = clean(it.get("title")), (it.get("link") or "").strip()
                date = parse_date(it.get("pubDate") or it.get("published") or it.get("updated") or it.get("date") or "")
                if not title or not link.startswith("http") or "ftc.gov" not in link:
                    continue
                press = "press-release" in url
                if ALERT_SKIP.search(title):
                    continue
                if press and not ALERT_STRICT.search(title):
                    continue
                if not press and not ALERT_BROAD.search(title + " " + clean(it.get("description") or it.get("summary"))):
                    continue
                if not date:
                    m = re.search(r"/(20\d{2})/(\d{2})/", link)
                    date = f"{m.group(1)}-{m.group(2)}-01" if m else ""
                items.append({"title": title[:170], "url": link, "date": date,
                              "kind": "enforcement" if press else "advice"})
        except Exception as exc:  # noqa: BLE001
            tried[url] = f"error: {str(exc)[:120]}"
    seen, unique = set(), []
    for it in sorted(items, key=lambda x: x["date"], reverse=True):
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        unique.append(it)
    if not unique:
        record("alerts", False, error="no matching items", feeds=tried)
        return
    save("alerts.json", {"source": "U.S. Federal Trade Commission consumer alerts and press releases",
                         "items": unique[:24]})
    record("alerts", True, items=len(unique), feeds=tried)


# --------------------------------------------------------------------------
def main() -> int:
    only = set(sys.argv[1:])
    jobs = [("rates", update_rates), ("pulse", update_pulse), ("market", update_market),
            ("energy", update_energy), ("recalls", update_recalls), ("videos", update_videos),
            ("alerts", update_alerts)]
    for name, job in jobs:
        if only and name not in only:
            continue
        try:
            job()
        except Exception as exc:  # noqa: BLE001
            record(name, False, error=f"unhandled {type(exc).__name__}: {exc}")
    STATUS["generated_at"] = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    STATUS["ok"] = sum(1 for s in STATUS["sources"].values() if s["ok"])
    STATUS["failed"] = sum(1 for s in STATUS["sources"].values() if not s["ok"])
    save("_status.json", STATUS)
    print(f"done: {STATUS['ok']} ok, {STATUS['failed']} failed")
    return 0  # never fail the workflow: the site keeps its last good data


if __name__ == "__main__":
    sys.exit(main())
