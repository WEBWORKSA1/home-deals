"""Home.Deals build core: data loading, date rules, signals, charts, layout."""
from __future__ import annotations

import datetime as dt
import hashlib
import html
import json
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from content.catalog import SITE, ICONS, CATEGORIES, HUBS, MONTHS, EVENTS, EXTRA_RECALL_CATS  # noqa: E402

DATA = ROOT / "data"
TODAY = dt.date.fromisoformat(os.environ["HD_TODAY"]) if os.environ.get("HD_TODAY") else dt.datetime.now(dt.timezone.utc).date()
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
               "November", "December"]
CAT = {c["slug"]: c for c in CATEGORIES}
HUB = {h["id"]: h for h in HUBS}


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------
def E(value) -> str:
    return html.escape(str(value), quote=True)


def load(name: str):
    path = DATA / f"{name}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        return None


def ic(name: str, cls: str = "ic") -> str:
    return (f'<svg class="{cls}" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" '
            f'stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{ICONS[name]}</svg>')


def fdate(iso: str | dt.date | None, style: str = "long") -> str:
    if not iso:
        return ""
    d = iso if isinstance(iso, dt.date) else dt.date.fromisoformat(str(iso)[:10])
    if style == "long":
        return f"{MONTH_NAMES[d.month - 1]} {d.day}, {d.year}"
    if style == "month":
        return f"{MONTH_NAMES[d.month - 1]} {d.year}"
    if style == "short":
        return f"{MONTH_NAMES[d.month - 1][:3]} {d.day}"
    if style == "weekday":
        return f"{d.strftime('%A')}, {MONTH_NAMES[d.month - 1]} {d.day}"
    return d.isoformat()


def money(value: float, cents: bool = False) -> str:
    return f"${value:,.2f}" if cents else f"${value:,.0f}"


def signed(value: float, digits: int = 1, unit: str = "%") -> str:
    sign = "+" if value > 0 else ("−" if value < 0 else "")
    return f"{sign}{abs(value):.{digits}f}{unit}"


def luminance(hex_color: str) -> float:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    f = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4  # noqa: E731
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def on_color(hex_color: str) -> str:
    """Ink or white, whichever has the higher contrast on the given chip colour."""
    lum = luminance(hex_color)
    ink = (lum + 0.05) / (luminance("#17233B") + 0.05)
    white = 1.05 / (lum + 0.05)
    return "#17233B" if ink >= white else "#FFFFFF"


def asset_v(rel: str) -> str:
    path = ROOT / rel
    return hashlib.sha1(path.read_bytes()).hexdigest()[:8] if path.exists() else "0"


# --------------------------------------------------------------------------
# data
# --------------------------------------------------------------------------
RATES, PULSE, MARKET, ENERGY = load("rates"), load("pulse"), load("market"), load("energy")
RECALLS, VIDEOS, ALERTS = load("recalls"), load("videos"), load("alerts")
R30 = (RATES or {}).get("summary", {}).get("30")
R15 = (RATES or {}).get("summary", {}).get("15")
PSER = (PULSE or {}).get("series", {})
MSER = (MARKET or {}).get("series", {})
ESER = (ENERGY or {}).get("series", {})
KWH = ESER.get("electricity_kwh")


def yoy_phrase(series: dict | None, short: bool = False) -> str:
    """'about 1.3% lower than a year ago' from a price-index entry."""
    if not series or series.get("yoy") is None:
        return ""
    yoy = series["yoy"]
    about = "about " if series.get("yoy_approx") else ""
    if abs(yoy) < 0.15:
        return "level with a year ago" if not short else "flat on last year"
    word = "higher" if yoy > 0 else "lower"
    if short:
        return f"{about}{abs(yoy):.1f}% {word} than last year"
    return f"{about}{abs(yoy):.1f}% {word} than a year ago"


# --------------------------------------------------------------------------
# sale events (rule-based dates)
# --------------------------------------------------------------------------
def nth_weekday(year: int, month: int, weekday: int, n: int) -> dt.date:
    d = dt.date(year, month, 1)
    d += dt.timedelta(days=(weekday - d.weekday()) % 7)
    return d + dt.timedelta(weeks=n - 1)


def last_weekday(year: int, month: int, weekday: int) -> dt.date:
    d = dt.date(year + (month == 12), month % 12 + 1, 1) - dt.timedelta(days=1)
    return d - dt.timedelta(days=(d.weekday() - weekday) % 7)


def event_date(rule: tuple, year: int) -> dt.date:
    kind = rule[0]
    if kind == "fixed":
        return dt.date(year, rule[1], rule[2])
    if kind == "nth":
        return nth_weekday(year, rule[1], rule[2], rule[3])
    if kind == "last":
        return last_weekday(year, rule[1], rule[2])
    if kind == "blackfriday":
        return nth_weekday(year, 11, 3, 4) + dt.timedelta(days=1 + rule[1])
    raise ValueError(rule)


def upcoming_events(today: dt.date = TODAY, limit: int = 8) -> list[dict]:
    out = []
    for year in (today.year - 1, today.year, today.year + 1):
        for ev in EVENTS:
            day = event_date(ev["rule"], year)
            start, end = day - dt.timedelta(days=ev["lead"]), day + dt.timedelta(days=ev["tail"])
            if end < today:
                continue
            out.append({**ev, "date": day, "start": start, "end": end, "live": start <= today <= end})
    out.sort(key=lambda x: (x["date"], x["id"]))
    seen, uniq = set(), []
    for ev in out:
        if ev["id"] in seen:
            continue
        seen.add(ev["id"])
        uniq.append(ev)
    return uniq[:limit]


# --------------------------------------------------------------------------
# buy-or-wait signals
# --------------------------------------------------------------------------
SIGNAL_LABEL = {"buy": "Buy window", "fair": "Fair", "wait": "Wait"}


def cat_signal(cat: dict, today: dt.date = TODAY) -> dict:
    m = today.month
    best = cat["best"]
    in_season = m in best
    gaps = sorted(((b - m) % 12 or 12, b) for b in best)
    ahead, next_month = gaps[0]
    series = PSER.get(cat["pulse"]) if cat.get("pulse") else None
    overall = PSER.get("all")
    if in_season:
        level = "buy"
        reason = f"{MONTH_NAMES[m - 1]} is one of the strongest months of the year for this category."
    elif ahead <= 2:
        level = "wait"
        when = "next month" if ahead == 1 else f"in {MONTH_NAMES[next_month - 1]}"
        reason = f"A stronger sale window opens {when}."
    else:
        level = "fair"
        reason = f"No seasonal edge this month. The next strong window is {MONTH_NAMES[next_month - 1]}."
    trend = ""
    if series and series.get("yoy") is not None:
        trend = "Prices are " + yoy_phrase(series)
        if overall and overall.get("yoy") is not None and series["yoy"] > 0.15:
            gap = series["yoy"] - overall["yoy"]
            trend += (", rising more slowly than overall inflation" if gap < -0.5
                      else ", rising faster than overall inflation" if gap > 0.5 else ", in line with overall inflation")
        trend += "."
    return {"level": level, "label": SIGNAL_LABEL[level], "reason": reason, "trend": trend, "series": series,
            "in_season": in_season, "next_month": MONTH_NAMES[next_month - 1], "ahead": ahead}


def market_meter() -> dict | None:
    """0-100 score: higher means national conditions lean towards buyers."""
    supply, hpi = MSER.get("months_supply"), MSER.get("hpi")
    if not (supply and hpi and R30 and hpi.get("yoy") is not None):
        return None
    clamp = lambda x: max(0.0, min(1.0, x))  # noqa: E731
    s_supply = clamp((supply["value"] - 4.0) / 6.0)
    s_price = clamp((6.0 - hpi["yoy"]) / 8.0)
    span = max(0.01, R30["high_52w"] - R30["low_52w"])
    s_rate = clamp(1 - (R30["rate"] - R30["low_52w"]) / span)
    score = round(100 * (0.40 * s_supply + 0.35 * s_price + 0.25 * s_rate))
    label = "Buyers have leverage" if score >= 60 else "Balanced" if score >= 40 else "Sellers have the edge"
    return {"score": score, "label": label,
            "parts": [("Supply of new homes", round(s_supply * 100), f"{supply['value']:.1f} months of supply in {fdate(supply['date'], 'month')}. Around six is considered balanced."),
                      ("Price growth", round(s_price * 100), f"House prices {signed(hpi['yoy'])} over the year to {fdate(hpi['date'], 'month')} (FHFA index)."),
                      ("Mortgage rates", round(s_rate * 100), f"30-year average {R30['rate']:.2f}%, within a 52-week range of {R30['low_52w']:.2f}% to {R30['high_52w']:.2f}%.")]}


# --------------------------------------------------------------------------
# charts (inline SVG, no JavaScript)
# --------------------------------------------------------------------------
def spark(values: list[float], w: int = 132, h: int = 40, cls: str = "spark") -> str:
    values = [v for v in values if v is not None]
    if len(values) < 3:
        return ""
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    step = (w - 6) / (len(values) - 1)
    pts = [(3 + i * step, 4 + (h - 8) * (1 - (v - lo) / span)) for i, v in enumerate(values)]
    path = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<svg class="{cls}" viewBox="0 0 {w} {h}" width="{w}" height="{h}" aria-hidden="true" focusable="false">'
            f'<polyline points="{path}" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linejoin="round" stroke-linecap="round"/>'
            f'<circle cx="{pts[-1][0]:.1f}" cy="{pts[-1][1]:.1f}" r="3" fill="currentColor"/></svg>')


def rate_chart(s30: list, s15: list, since: dt.date, label: str) -> str:
    """Line chart of weekly mortgage rates from `since` to the latest reading."""
    a = [(dt.date.fromisoformat(d), v) for d, v in s30 if dt.date.fromisoformat(d) >= since]
    b = [(dt.date.fromisoformat(d), v) for d, v in s15 if dt.date.fromisoformat(d) >= since]
    if len(a) < 4:
        return ""
    W, H, L, Rm, T, B = 720, 300, 46, 60, 14, 30
    allv = [v for _, v in a + b]
    lo = int(min(allv) * 2) / 2 - 0.0
    hi = (int(max(allv) * 2) + 1) / 2
    if lo > min(allv) - 0.1:
        lo -= 0.5
    d0, d1 = a[0][0], a[-1][0]
    days = max(1, (d1 - d0).days)
    X = lambda d: L + (W - L - Rm) * (d - d0).days / days  # noqa: E731
    Y = lambda v: T + (H - T - B) * (1 - (v - lo) / (hi - lo))  # noqa: E731
    out = [f'<svg class="chart" viewBox="0 0 {W} {H}" role="img" aria-label="{E(label)}">']
    v = lo
    while v <= hi + 1e-9:
        out.append(f'<line class="grid" x1="{L}" x2="{W - Rm}" y1="{Y(v):.1f}" y2="{Y(v):.1f}"/>'
                   f'<text class="axis" x="{L - 8}" y="{Y(v) + 4:.1f}" text-anchor="end">{v:.1f}%</text>')
        v += 0.5 if (hi - lo) <= 3 else 1.0
    span_years = days / 365
    marks = []
    if span_years > 2:
        marks = [(dt.date(y, 1, 1), str(y)) for y in range(d0.year + 1, d1.year + 1)]
    else:
        y, m = d0.year, d0.month
        while True:
            m += 1
            if m > 12:
                y, m = y + 1, 1
            tick = dt.date(y, m, 1)
            if tick > d1:
                break
            if m % 2 == 1:
                marks.append((tick, MONTH_NAMES[m - 1][:3] + (f" {y}" if m == 1 else "")))
    for tick, text in marks:
        if tick <= d0:
            continue
        out.append(f'<line class="grid tick" x1="{X(tick):.1f}" x2="{X(tick):.1f}" y1="{H - B}" y2="{H - B + 5}"/>'
                   f'<text class="axis" x="{X(tick):.1f}" y="{H - 8}" text-anchor="middle">{text}</text>')
    for series, cls, name in ((b, "line line-2", "15-year"), (a, "line", "30-year")):
        if len(series) < 2:
            continue
        pts = " ".join(f"{X(d):.1f},{Y(val):.1f}" for d, val in series)
        ex, ey = X(series[-1][0]), Y(series[-1][1])
        out.append(f'<polyline class="{cls}" points="{pts}"/><circle class="{cls} dot" cx="{ex:.1f}" cy="{ey:.1f}" r="3.5"/>'
                   f'<text class="end {cls}" x="{ex + 8:.1f}" y="{ey + 4:.1f}">{name}</text>')
    out.append("</svg>")
    return "".join(out)
