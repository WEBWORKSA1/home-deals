#!/usr/bin/env python3
"""Home.Deals static site generator.

    python3 scripts/build.py

Reads /content (editorial) and /data (refreshed by update_data.py) and writes
every page, the sitemap, the feed and the search index into the repository
root, ready for GitHub Pages (deploy from branch: main, folder: / root).
Standard library only.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re

from hd_core import (ALERTS, CAT, E, ESER, HUB, KWH, MONTH_NAMES, MSER, PSER, PULSE, R15, R30, RATES, RECALLS, ROOT,
                     TODAY, VIDEOS, asset_v, cat_signal, event_date, fdate, ic, market_meter, money, on_color,
                     rate_chart, signed, spark, upcoming_events, yoy_phrase)
from content.catalog import CATEGORIES, EVENTS, EXTRA_RECALL_CATS, FLOATING_EVENTS, HUBS, MONTHS, SITE
from content.guides import GUIDES
from content.pages import (ABOUT, ACCESSIBILITY, ADVERTISE_FORMATS, CAREER_ROLES, COOKIES, DISCLAIMER, DISCLOSURE,
                           EDITORIAL, GIVEAWAY_STANDING_RULES, PRIVACY, SUPPORT_USES, TERMS, TOOLS)
from content.services import (CONTACT_PREF, HOW_IT_WORKS, OWNERSHIP, QUOTE_FAQS, RED_FLAGS, SERVICES, TIMING)

PAGES: list[dict] = []
CONTACT = SITE["contact_url"]
MONTH = MONTHS[TODAY.month - 1]
SVC = {s["slug"]: s for s in SERVICES}
TOOL = {t["slug"]: t for t in TOOLS}
GUIDE = {g["slug"]: g for g in GUIDES}

TOKENS = {
    "contact": CONTACT,
    "rate30": f"{R30['rate']:.2f}" if R30 else "7.00",
    "rate30_date": fdate(R30["date"]) if R30 else "the latest survey",
    "rate30_year_ago": f"{R30['year_ago']:.2f}" if R30 and R30.get("year_ago") else "a different level",
    "kwh": f"{KWH['value']:.2f}" if KWH else "0.18",
    "kwh_date": fdate(KWH["date"], "month") if KWH else "latest reading",
    "pulse_major_appliances_dir": yoy_phrase(PSER.get("major_appliances")) or "little changed",
}


def add(path: str, title: str, desc: str, body: str, **kw) -> None:
    PAGES.append({"path": path, "title": title, "desc": desc, "body": body, **kw})


# ==========================================================================
# shared components
# ==========================================================================
def sig_badge(level: str, label: str | None = None) -> str:
    labels = {"buy": "Buy window", "fair": "Fair", "wait": "Wait", "alert": "Recall"}
    return f'<span class="sig sig-{level}">{label or labels[level]}</span>'


def chip(href: str, color: str, title: str, lines: list[str], icon_name: str | None = None, code: str = "",
         badge: str = "", tag: str = "a", cls: str = "") -> str:
    fg = on_color(color)
    icon_html = ic(icon_name, "chip-ic") if icon_name else ""
    body = "".join(f"<span class=\"chip-line\">{line}</span>" for line in lines if line)
    code_html = f'<span class="chip-code">{E(code)}</span>' if code else ""
    attrs = f' href="{href}"' if tag == "a" else ""
    return (f'<{tag} class="chip {cls}"{attrs} style="--chip:{color};--chip-fg:{fg}">'
            f'<span class="chip-swatch">{icon_html}</span>'
            f'<span class="chip-cap"><strong class="chip-title">{E(title)}</strong>{badge}{body}{code_html}</span></{tag}>')


def faq_block(faqs: list[tuple[str, str]], heading: str = "Questions people ask") -> tuple[str, dict]:
    items = "".join(f'<details class="faq"><summary>{E(q)}</summary><div class="faq-a"><p>{a}</p></div></details>' for q, a in faqs)
    schema = {"@context": "https://schema.org", "@type": "FAQPage",
              "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}}
                             for q, a in faqs]}
    return f'<section class="sec"><h2>{E(heading)}</h2><div class="faqs">{items}</div></section>', schema


def field(name: str, label: str, kind: str = "text", required: bool = False, help_: str = "", options: list[str] | None = None,
          attrs: str = "", value: str = "", cls: str = "") -> str:
    if attrs and '"' not in attrs:
        attrs = re.sub(r"([\w-]+)=(\S+)", r'\1="\2"', attrs)
    req = " required" if required else ""
    opt = "" if required else ' <span class="opt">optional</span>'
    hid = f"{name}-help"
    help_html = f'<span class="help" id="{hid}">{help_}</span>' if help_ else ""
    described = f' aria-describedby="{hid}"' if help_ else ""
    if kind == "select":
        opts = "".join(f"<option{' selected' if o == value else ''}>{E(o)}</option>" for o in (options or []))
        control = f'<select name="{name}" id="f-{name}"{req}{described} {attrs}>{opts}</select>'
    elif kind == "textarea":
        control = f'<textarea name="{name}" id="f-{name}" rows="4"{req}{described} {attrs}>{E(value)}</textarea>'
    else:
        control = f'<input type="{kind}" name="{name}" id="f-{name}" value="{E(value)}"{req}{described} {attrs}>'
    return f'<div class="field {cls}"><label for="f-{name}">{label}{opt}</label>{control}{help_html}</div>'


CONSENT_BASIC = ('I agree that Home.Deals may contact me about this, and I have read the '
                 '<a href="{{root}}privacy/">privacy policy</a>.')
CONSENT_QUOTE = ('I agree that Home.Deals, and the providers it introduces for this request, may contact me by email, and by '
                 'phone or text if I give a number, including with automated technology. Consent is not a condition of any '
                 'purchase. I have read the <a href="{{root}}privacy/">privacy policy</a> and <a href="{{root}}terms/">terms</a>.')


def form(name: str, subject: str, fields: str, button: str, success: str, consent: str | None = CONSENT_BASIC, cls: str = "") -> str:
    consent_html = (f'<label class="check"><input type="checkbox" name="consent" value="yes" required><span>{consent}</span></label>'
                    if consent else "")
    return (f'<form class="form {cls}" data-form="{name}" data-subject="{E(subject)}" data-success="{E(success)}" novalidate>'
            f'{fields}'
            '<div class="hp" aria-hidden="true"><label>Leave this field empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>'
            f'{consent_html}'
            f'<div class="form-actions"><button class="btn btn-mark" type="submit">{button}</button></div>'
            '<p class="form-msg" role="status" aria-live="polite"></p>'
            '<noscript><p class="note">This form needs JavaScript. You can also reach us through the '
            '<a href="{{contact}}">contact page</a>.</p></noscript></form>')


def ad(slot: str) -> str:
    """Manual AdSense unit, rendered only when a slot id is configured. Auto ads need no markup."""
    slot_id = SITE["ad_slots"].get(slot)
    if not slot_id:
        return ""
    return ('<aside class="ad" aria-label="Advertisement"><span class="ad-label">Advertisement</span>'
            f'<ins class="adsbygoogle" style="display:block" data-ad-client="{SITE["adsense_client"]}" data-ad-slot="{slot_id}" '
            'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            '<script>(adsbygoogle = window.adsbygoogle || []).push({});</script></aside>')


def quotes_band(service: str | None = None) -> str:
    opts = "".join(f'<option value="{s["slug"]}"{" selected" if s["slug"] == service else ""}>{E(s["name"])}</option>' for s in SERVICES)
    return ('<section class="band band-ink"><div class="wrap band-grid">'
            '<div><h2>Planning a bigger project?</h2>'
            '<p>Tell us what you need and get a ballpark price range on the spot, then compare quotes from providers that cover your area. '
            'It is free, and there is no obligation to hire anyone.</p></div>'
            '<form class="mini" action="{{root}}quotes/" method="get">'
            f'<div class="field"><label for="mini-service">Project</label><select id="mini-service" name="service">{opts}</select></div>'
            '<div class="field"><label for="mini-zip">ZIP code</label><input type="text" id="mini-zip" name="zip" inputmode="numeric" pattern="[0-9]{5}" maxlength="5" autocomplete="postal-code" placeholder="e.g. 30301"></div>'
            '<button class="btn btn-mark" type="submit">Start my quote request</button>'
            '</form></div></section>')


def alerts_band(topic: str = "") -> str:
    fields = (field("email", "Email address", "email", True, attrs='autocomplete="email" placeholder="you@example.com"')
              + f'<input type="hidden" name="interest" value="{E(topic or "All home categories")}">')
    return ('<section class="band band-mark"><div class="wrap band-grid">'
            '<div><h2>Get told when a buy window opens</h2>'
            '<p>One short email when a category you care about moves into its strongest sale period, or when mortgage rates shift. '
            'No daily blasts. Stop any time.</p></div>'
            + form("alerts", "Deal alert sign-up", fields, "Send me deal alerts", "You are on the list. We will email you only when the timing is right.",
                   cls="form-inline")
            + '</div></section>')


def hub_row(h: dict) -> str:
    kind = {"retailer": "Retailer sale page", "community": "Deal community", "public": "Public program"}[h["kind"]]
    return (f'<li class="row hub" data-kind="{h["kind"]}" data-text="{E((h["name"] + " " + h["page"] + " " + h["note"]).lower())}">'
            f'<div class="row-main"><h3><a href="{E(h["url"])}" target="_blank" rel="noopener nofollow">{E(h["name"])}: {E(h["page"])}</a></h3>'
            f'<p>{E(h["note"])}</p></div><span class="tagline">{kind}</span></li>')


def guide_row(g: dict) -> str:
    return (f'<li class="row"><div class="row-main"><h3><a href="{{{{root}}}}guides/{g["slug"]}/">{E(g["title"])}</a></h3>'
            f'<p>{E(g["desc"])}</p></div><span class="tagline">{g["minutes"]} min read</span></li>')


def related_links(items: list[str]) -> str:
    out = []
    for ref in items:
        if ref.startswith("guides/") and ref[7:] in GUIDE:
            out.append((ref + "/", GUIDE[ref[7:]]["title"]))
        elif ref.startswith("tools/") and ref[6:] in TOOL:
            out.append((ref + "/", TOOL[ref[6:]]["name"]))
        elif ref.startswith("deals/") and ref[6:] in CAT:
            out.append((ref + "/", CAT[ref[6:]]["name"] + " deals"))
        elif ref.startswith("quotes/") and ref[7:] in SVC:
            out.append((ref + "/", SVC[ref[7:]]["name"] + " quotes and costs"))
        else:
            names = {"calendar": "The sale calendar", "price-pulse": "Price Pulse signals", "recalls": "Recall Radar",
                     "quotes": "Free project quotes", "rates": "Mortgage rates", "deals": "Deal Radar", "tools": "Calculators"}
            if ref in names:
                out.append((ref + "/", names[ref]))
    if not out:
        return ""
    links = "".join(f'<li><a href="{{{{root}}}}{href}">{E(text)}</a></li>' for href, text in out)
    return f'<aside class="related"><h2>Keep going</h2><ul>{links}</ul></aside>'


def recall_row(r: dict) -> str:
    cat = CAT.get(r["cat"])
    name, color = (cat["name"], cat["chip"]) if cat else EXTRA_RECALL_CATS.get(r["cat"], ("Home", "#888888"))
    remedy = ", ".join(r.get("remedy_type") or []) or "See notice"
    units = f'<span>{E(r["units"])} units</span>' if r.get("units") else ""
    return (f'<li class="row recall" data-kind="{r["cat"]}" data-text="{E(r["title"].lower())}" style="--chip:{color}">'
            f'<div class="row-main"><h3><a href="{E(r["url"])}" target="_blank" rel="noopener nofollow">{E(r["title"])}</a></h3>'
            f'<p>{E(r.get("hazard") or "")}</p>'
            f'<p class="meta"><span>{fdate(r["date"])}</span><span>{E(name)}</span><span>Remedy: {E(remedy)}</span>{units}</p></div></li>')


def video_card(v: dict) -> str:
    return (f'<li class="video" data-kind="{v["topic"]}" data-text="{E((v["title"] + " " + v["channel"]).lower())}">'
            f'<button class="video-btn" type="button" data-yt="{v["id"]}" aria-label="Play video: {E(v["title"])}">'
            f'<img src="https://i.ytimg.com/vi/{v["id"]}/hqdefault.jpg" alt="" loading="lazy" width="480" height="360">'
            f'<span class="video-play">{ic("play")}</span></button>'
            f'<h3>{E(v["title"])}</h3><p class="meta"><span>{E(v["channel"])}</span><span>{fdate(v["published"], "short")}</span></p></li>')


def filter_bar(target: str, kinds: list[tuple[str, str]], placeholder: str) -> str:
    chips = "".join(f'<button type="button" class="pill{" is-on" if i == 0 else ""}" data-kind="{k}" aria-pressed="{"true" if i == 0 else "false"}">{E(label)}</button>'
                    for i, (k, label) in enumerate(kinds))
    return (f'<div class="filter" data-filter="{target}"><div class="pills" role="group" aria-label="Filter">{chips}</div>'
            f'<label class="vh" for="q-{target}">Search this list</label>'
            f'<input type="search" id="q-{target}" placeholder="{E(placeholder)}" autocomplete="off">'
            f'<p class="filter-count" aria-live="polite"></p></div>')


def stamp(text: str) -> str:
    return f'<p class="stamp">{text}</p>'


def event_line(ev: dict) -> str:
    live = ' <span class="sig sig-buy">Sales running now</span>' if ev["live"] else ""
    return (f'<li class="row event" data-event="{ev["id"]}"><div class="row-main"><h3>{E(ev["name"])}{live}</h3>'
            f'<p>{E(ev["best"])}</p></div>'
            f'<span class="tagline"><span class="event-date">{fdate(ev["date"], "weekday")}</span>'
            f'<span class="event-count" data-count="{ev["date"].isoformat()}"></span></span></li>')


# ==========================================================================
# pages
# ==========================================================================
def build_home() -> None:
    # six chips with a mix of signals, so the deck shows what to buy and what to wait on
    by_level: dict[str, list] = {"buy": [], "wait": [], "fair": []}
    for c in CATEGORIES:
        by_level[cat_signal(c)["level"]].append(c)
    picks = by_level["buy"][:3] + by_level["wait"][:2] + by_level["fair"][:1]
    for c in CATEGORIES:
        if len(picks) >= 6:
            break
        if c not in picks:
            picks.append(c)
    order = {c["slug"]: n for n, c in enumerate(CATEGORIES)}
    deck = []
    for c in picks[:6]:
        slug, i = c["slug"], order[c["slug"]]
        s = cat_signal(c)
        trend = yoy_phrase(s["series"], short=True)
        deck.append(chip(f"{{{{root}}}}deals/{slug}/", c["chip"], c["name"], [("Prices " + trend) if trend else s["reason"]],
                         c["icon"], f'HD-{i + 1:02d} {c["paint"]}', sig_badge(s["level"]), cls="chip-deck"))
    events = upcoming_events(limit=3)
    head_ev = events[0] if events else None
    ev_text = ""
    if head_ev:
        running = " Sales are already running." if head_ev["live"] else ""
        ev_text = (f'<p class="hero-event"><a href="{{{{root}}}}calendar/">{E(head_ev["name"])} is {fdate(head_ev["date"], "weekday")}.</a>'
                   f'{running} <span data-count="{head_ev["date"].isoformat()}" data-count-style="sentence"></span></p>')

    figs = []
    if R30:
        figs.append(("rates/", "30-year mortgage rate", f'{R30["rate"]:.2f}%',
                     f'{signed(R30["week_change"], 2, " pts")} on the week, {fdate(R30["date"], "short")}'))
    meter = market_meter()
    if meter:
        figs.append(("market/", "Housing market meter", f'{meter["score"]} / 100', meter["label"]))
    if PSER.get("all"):
        figs.append(("price-pulse/", "Overall inflation", f'{PSER["all"]["yoy"]:.1f}%',
                     f'year over year, {fdate(PSER["all"]["date"], "month")}'))
    if RECALLS:
        recent = [r for r in RECALLS["items"] if (TODAY - dt.date.fromisoformat(r["date"])).days <= 31]
        figs.append(("recalls/", "Home product recalls", str(len(recent)), "announced in the last 31 days"))
    fig_html = "".join(f'<a class="fig" href="{{{{root}}}}{href}"><span class="fig-label">{E(label)}</span>'
                       f'<span class="fig-num">{E(num)}</span><span class="fig-note">{E(note)}</span></a>' for href, label, num, note in figs)

    def buy_list(items):
        return "".join(f'<li><a href="{{{{root}}}}deals/{slug}/">{E(label)}</a><span>{E(why)}</span></li>' for label, slug, why in items)

    cat_grid = "".join(
        chip(f"{{{{root}}}}deals/{c['slug']}/", c["chip"], c["name"], [c["blurb"]], c["icon"], badge=sig_badge(cat_signal(c)["level"]), cls="chip-sm")
        for c in CATEGORIES)
    tools_rows = "".join(f'<li class="row"><div class="row-main"><h3><a href="{{{{root}}}}tools/{t["slug"]}/">{E(t["name"])}</a></h3><p>{E(t["desc"])}</p></div></li>'
                         for t in TOOLS[:6])
    guides_rows = "".join(guide_row(g) for g in GUIDES[:5])
    recalls_rows = "".join(recall_row(r) for r in (RECALLS or {}).get("items", [])[:3])
    videos = "".join(video_card(v) for v in (VIDEOS or {}).get("items", [])[:4])

    body = f'''
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<h1 class="display">Know when to buy anything for your home.</h1>
<p class="lede">Home.Deals reads the sale calendar and public price data, then tells you which home categories are in a buy window this month and which are worth waiting on.</p>
<p class="hero-actions"><a class="btn btn-mark" href="{{{{root}}}}price-pulse/">See this month’s signals</a><a class="btn btn-line" href="{{{{root}}}}quotes/">Get free project quotes</a></p>
{ev_text}
</div>
<div class="deck" role="list" aria-label="Buy-or-wait signals for {MONTH["name"]}">{"".join(f'<div role="listitem">{c}</div>' for c in deck)}</div>
</div></section>
<section class="figs"><div class="wrap figs-grid">{fig_html}</div></section>

<section class="sec"><div class="wrap">
<div class="sec-head"><h2>What to buy in {MONTH["name"]}, and what can wait</h2><a class="more" href="{{{{root}}}}calendar/">See the full calendar</a></div>
<div class="two">
<div><h3 class="list-title">{sig_badge("buy", "Buy now")}</h3><ul class="why">{buy_list(MONTH["buy"])}</ul></div>
<div><h3 class="list-title">{sig_badge("wait", "Hold off")}</h3><ul class="why">{buy_list(MONTH["hold"])}</ul></div>
</div></div></section>

<section class="sec sec-tint"><div class="wrap">
<div class="sec-head"><h2>Every home category, with this month’s signal</h2><a class="more" href="{{{{root}}}}deals/">Open Deal Radar</a></div>
<div class="chip-grid">{cat_grid}</div>
</div></section>

{quotes_band()}

<section class="sec"><div class="wrap two two-wide">
<div><div class="sec-head"><h2>Calculators</h2><a class="more" href="{{{{root}}}}tools/">All calculators</a></div><ul class="rows">{tools_rows}</ul></div>
<div><div class="sec-head"><h2>Guides</h2><a class="more" href="{{{{root}}}}guides/">All guides</a></div><ul class="rows">{guides_rows}</ul></div>
</div></section>
{ad("home")}
'''
    if recalls_rows:
        body += f'''<section class="sec sec-tint"><div class="wrap">
<div class="sec-head"><h2>Recalled this month: check before you buy</h2><a class="more" href="{{{{root}}}}recalls/">Open Recall Radar</a></div>
<ul class="rows">{recalls_rows}</ul>{stamp("Source: U.S. Consumer Product Safety Commission.")}</div></section>'''
    if videos:
        body += f'''<section class="sec"><div class="wrap">
<div class="sec-head"><h2>Watch: repairs, projects and buying advice</h2><a class="more" href="{{{{root}}}}videos/">More videos</a></div>
<ul class="video-grid">{videos}</ul></div></section>'''
    body += alerts_band()
    body += f'''<section class="sec"><div class="wrap two">
<div class="plain"><h2>Giveaways</h2><p>Home.Deals runs prize rounds for readers when a prize is confirmed. Entry is always free.</p><p><a class="btn btn-line" href="{{{{root}}}}giveaways/">See giveaway rules and updates</a></p></div>
<div class="plain"><h2>Keep Home.Deals independent</h2><p>Reader support pays for the data pipeline, new guides, contributors and prizes.</p><p><a class="btn btn-line" href="{{{{root}}}}support/">Support the site</a></p></div>
</div></section>'''
    schema = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE["name"], "url": SITE["url"] + "/",
               "description": SITE["description"],
               "potentialAction": {"@type": "SearchAction", "target": SITE["url"] + "/search/?q={search_term_string}",
                                   "query-input": "required name=search_term_string"}},
              {"@context": "https://schema.org", "@type": "Organization", "name": SITE["name"], "url": SITE["url"] + "/",
               "logo": SITE["url"] + "/assets/img/icon-512.png"}]
    add("", f'{SITE["name"]}: {SITE["tagline"]}', SITE["description"], body, bare=True, schema=schema, section="Home")


def build_deals() -> None:
    rows = []
    for c in CATEGORIES:
        s = cat_signal(c)
        best = ", ".join(MONTH_NAMES[m - 1][:3] for m in c["best"])
        rows.append(f'<tr><th scope="row"><a href="{{{{root}}}}deals/{c["slug"]}/"><span class="dot" style="--chip:{c["chip"]}"></span>{E(c["name"])}</a></th>'
                    f'<td>{sig_badge(s["level"])}</td><td>{E(yoy_phrase(s["series"], short=True).capitalize() or "No index for this category")}</td><td>{best}</td></tr>')
    hubs = "".join(hub_row(h) for h in HUBS)
    body = f'''
<section class="sec"><div class="wrap">
<h2>This month’s signal by category</h2>
<div class="table-wrap"><table class="tbl"><thead><tr><th scope="col">Category</th><th scope="col">Signal for {MONTH["name"]}</th><th scope="col">Price trend</th><th scope="col">Strongest months</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table></div>
{stamp(f'Signals combine the sale calendar with Consumer Price Index data to {fdate(PSER["all"]["date"], "month")}. <a href="{{{{root}}}}editorial-policy/">How signals are set</a>.' if PSER.get("all") else 'Signals follow the sale calendar. <a href="{{root}}editorial-policy/">How signals are set</a>.')}
</div></section>
<section class="sec sec-tint"><div class="wrap">
<h2>Where real discounts are published</h2>
<p class="sec-lede">These are the official sale pages and long-running deal communities worth checking, with what each one is good for. Links open the source’s own page.</p>
{filter_bar("hubs", [("all", "All sources"), ("retailer", "Retailer sale pages"), ("community", "Deal communities"), ("public", "Public programs")], "Search stores and sources")}
<ul class="rows" id="hubs">{hubs}</ul>
<p class="note">Home.Deals is independent of every company listed. Names are used only to identify each company’s own page. See the <a href="{{{{root}}}}disclaimer/">trademark notice</a>.</p>
</div></section>
<section class="sec"><div class="wrap two">
<div class="plain"><h2>Reader-submitted deals</h2><p>Found a price on something for the home that beats its usual selling price by a clear margin? Send it in with the evidence. Deals that check out are published here with credit.</p>
<p><a class="btn btn-ink" href="{{{{root}}}}submit/">Submit a deal</a></p></div>
<div class="plain"><h2>Check a deal yourself</h2><p>Enter the sale price, the usual price, delivery and any coupon. The Deal Score checker returns the real discount.</p>
<p><a class="btn btn-line" href="{{{{root}}}}tools/deal-score/">Open the Deal Score checker</a></p></div>
</div></section>
{alerts_band()}'''
    add("deals/", "Deal Radar: where home deals are, and when to buy", "This month’s buy-or-wait signal for twelve home categories, plus the official sale pages and deal communities worth checking.",
        body, h1="Deal Radar", lede="A signal for every home category this month, and a guide to the places where genuine discounts are published.",
        crumbs=[("Deals", None)], section="Deals")

    for i, c in enumerate(CATEGORIES):
        s = cat_signal(c)
        intro = "".join(f"<p>{p}</p>" for p in c["intro"])
        timing = "".join(f'<tr><th scope="row">{E(when)}</th><td>{E(what)}</td></tr>' for when, what in c["timing"])
        good = "".join(f"<li>{E(x)}</li>" for x in c["good"])
        watch = "".join(f"<li>{E(x)}</li>" for x in c["watch"])
        hubs = "".join(hub_row(HUB[h]) for h in c["hubs"])
        trend_panel = ""
        if s["series"]:
            ser = s["series"]
            trend_panel = (f'<div class="panel"><h3>Price trend</h3><p class="big">{signed(ser["yoy"])}</p>'
                           f'<p>{E(ser["label"])} index, year over year to {fdate(ser["date"], "month")}'
                           f'{" (estimated base month)" if ser.get("yoy_approx") else ""}.</p>'
                           f'<div class="spark-wrap">{spark([v for _, v in ser["spark"]], 220, 56)}</div>'
                           f'<p class="stamp">Three years of the index. Source: U.S. Bureau of Labor Statistics.</p></div>')
        recalls = [r for r in (RECALLS or {}).get("items", []) if r["cat"] == c["slug"]][:3]
        recall_html = ""
        if recalls:
            recall_html = (f'<section class="sec"><div class="wrap"><div class="sec-head"><h2>Recent recalls in this category</h2>'
                           f'<a class="more" href="{{{{root}}}}recalls/">Open Recall Radar</a></div><ul class="rows">{"".join(recall_row(r) for r in recalls)}</ul></div></section>')
        faq_html, faq_schema = faq_block(c["faqs"])
        best = ", ".join(MONTH_NAMES[m - 1] for m in c["best"])
        body = f'''
<section class="sec"><div class="wrap split">
<div class="prose">{intro}
<h2>When prices drop</h2>
<div class="table-wrap"><table class="tbl"><tbody>{timing}</tbody></table></div>
<div class="two">
<div><h2>What a good deal looks like</h2><ul class="ticks">{good}</ul></div>
<div><h2>Watch for</h2><ul class="crosses">{watch}</ul></div>
</div>
</div>
<aside class="side">
<div class="panel panel-sig"><h3>Signal for {MONTH["name"]}</h3><p>{sig_badge(s["level"])}</p><p>{E(s["reason"])}</p>{f"<p>{E(s['trend'])}</p>" if s["trend"] else ""}
<p class="stamp">Strongest months: {best}.</p></div>
{trend_panel}
<div class="panel"><h3>Before you buy</h3><ul class="links">
<li><a href="{{{{root}}}}tools/deal-score/">Check the real discount</a></li>
<li><a href="{{{{root}}}}recalls/">Search recent recalls</a></li>
<li><a href="{{{{root}}}}calendar/">See the full sale calendar</a></li></ul></div>
</aside>
</div></section>
<section class="sec sec-tint"><div class="wrap"><h2>Where to look for {E(c["name"].lower())} deals</h2>
<ul class="rows">{hubs}</ul>
<p class="note">Links open each source’s own page. Home.Deals is not affiliated with these companies.</p></div></section>
{recall_html}
<div class="wrap">{faq_html}</div>
{ad("category")}
{alerts_band(c["name"])}'''
        add(f'deals/{c["slug"]}/', f'{c["name"]} deals: when to buy and what a good price looks like',
            f'{c["blurb"]} The best months to buy, what a real discount looks like, where to look and this month’s buy-or-wait signal.',
            body, h1=f'{c["name"]} deals', lede=c["blurb"] + " Here is when prices drop, how to judge an offer and where to look.",
            crumbs=[("Deals", "deals/"), (c["name"], None)], schema=[faq_schema], section="Deals",
            chip=(c["chip"], c["icon"], f'HD-{i + 1:02d} {c["paint"]}'))


def build_calendar() -> None:
    events = "".join(event_line(ev) for ev in upcoming_events(limit=7))
    months = []
    for m in MONTHS:
        cur = " is-now" if m["n"] == TODAY.month else ""
        buy = "".join(f'<li><a href="{{{{root}}}}deals/{slug}/">{E(label)}</a><span>{E(why)}</span></li>' for label, slug, why in m["buy"])
        hold = "".join(f'<li><a href="{{{{root}}}}deals/{slug}/">{E(label)}</a><span>{E(why)}</span></li>' for label, slug, why in m["hold"])
        months.append(f'<article class="month{cur}" id="{m["name"].lower()}" data-month="{m["n"]}"><h3>{m["name"]}<span class="now-tag">This month</span></h3>'
                      f'<h4>{sig_badge("buy", "Buy")}</h4><ul class="why">{buy}</ul><h4>{sig_badge("wait", "Hold off")}</h4><ul class="why">{hold}</ul></article>')
    floating = "".join(f'<li class="row"><div class="row-main"><h3>{E(n)}</h3><p>{E(note)}</p></div><span class="tagline">{E(when)}</span></li>'
                       for n, when, note in FLOATING_EVENTS)
    jump = "".join(f'<a class="pill" href="#{m["name"].lower()}">{m["name"][:3]}</a>' for m in MONTHS)
    faq_html, faq_schema = faq_block([
        ("What is the best month to buy furniture?", "January and July, when showrooms clear stock before the February and August collections arrive."),
        ("When do appliances go on sale?", "September and October for most major appliances, and May for refrigerators, with extra bundle offers on holiday weekends."),
        ("Is Black Friday really the cheapest time?", "For small kitchen appliances, vacuums, smart home devices and tool kits, usually yes. For furniture, linens, holiday decor and flooring installation, other months are better."),
        ("How are the countdowns calculated?", "From the calendar rules for each holiday, such as the third Monday in February for Presidents’ Day. Retailer-run events with dates that change each year are listed without a countdown."),
    ])
    body = f'''
<section class="sec"><div class="wrap">
<h2>Next sale events</h2>
<ul class="rows">{events}</ul>
{stamp("Dates follow the holiday rules. Many retailers start sales one to three weeks before the day itself.")}
</div></section>
<section class="sec sec-tint"><div class="wrap">
<div class="sec-head"><h2>Month by month</h2></div>
<nav class="pills jump" aria-label="Jump to a month">{jump}</nav>
<div class="months">{"".join(months)}</div>
</div></section>
<section class="sec"><div class="wrap"><h2>Events that move each year</h2><ul class="rows">{floating}</ul></div></section>
<div class="wrap">{faq_html}</div>
{ad("calendar")}
{alerts_band()}'''
    add("calendar/", "The home sale calendar: the best time to buy, month by month",
        "What to buy for the home each month and what to hold off on, with countdowns to Presidents’ Day, Memorial Day, Labor Day, Black Friday and more.",
        body, h1="The home sale calendar", lede="What to buy each month, what to hold off on, and how long until the next big sale.",
        crumbs=[("Calendar", None)], schema=[faq_schema], section="Calendar")


def build_pulse() -> None:
    rows = []
    for c in CATEGORIES:
        s = cat_signal(c)
        ser = s["series"]
        sp = spark([v for _, v in ser["spark"]], 132, 40) if ser else ""
        rows.append(f'<li class="row pulse-row"><span class="swatch" style="--chip:{c["chip"]}">{ic(c["icon"], "chip-ic")}</span>'
                    f'<div class="row-main"><h3><a href="{{{{root}}}}deals/{c["slug"]}/">{E(c["name"])}</a> {sig_badge(s["level"])}</h3>'
                    f'<p>{E(s["reason"])} {E(s["trend"])}</p></div><span class="pulse-spark">{sp}</span></li>')
    idx_rows = []
    order = ["all", "furnishings", "furniture", "major_appliances", "appliances", "tools", "linens", "decor", "housekeeping", "tvs", "energy", "electricity"]
    for key in order:
        ser = PSER.get(key)
        if not ser or ser.get("yoy") is None:
            continue
        mom = ser.get("momentum")
        direction = "—" if mom is None else ("Rising faster" if mom > 0.3 else "Easing" if mom < -0.3 else "Steady")
        idx_rows.append(f'<tr><th scope="row">{E(ser["label"])}</th><td class="num">{signed(ser["yoy"])}</td>'
                        f'<td class="num">{signed(ser["yoy_3m_ago"]) if ser.get("yoy_3m_ago") is not None else "—"}</td><td>{direction}</td>'
                        f'<td class="spark-cell">{spark([v for _, v in ser["spark"]], 110, 30)}</td></tr>')
    if PSER.get("all"):
        allser = PSER["all"]
        note = stamp(f'Consumer Price Index for All Urban Consumers, U.S. city average, to {fdate(allser["date"], "month")}. Source: U.S. Bureau of Labor Statistics. '
                     'The October 2025 index was not published, so comparisons that need it use an estimated base and are approximate.')
        table = (f'<div class="table-wrap"><table class="tbl"><thead><tr><th scope="col">Index</th><th scope="col" class="num">Change over 12 months</th>'
                 f'<th scope="col" class="num">Three months earlier</th><th scope="col">Direction</th><th scope="col">Three years</th></tr></thead><tbody>{"".join(idx_rows)}</tbody></table></div>{note}')
        headline = (f'Overall prices are {yoy_phrase(allser)}. Furniture and bedding are {yoy_phrase(PSER.get("furniture")) or "unchanged"}, '
                    f'and major appliances are {yoy_phrase(PSER.get("major_appliances")) or "unchanged"}.')
    else:
        table = '<p class="note">Price index data loads with the next automatic refresh.</p>'
        headline = "Signals below follow the sale calendar."
    faq_html, faq_schema = faq_block([
        ("What does “Buy window” mean?", "The current month is one of the historically strongest months for sales in that category. It describes conditions, not a particular offer."),
        ("What does “Wait” mean?", "A stronger sale period for the category starts within about two months. If the purchase is not urgent, holding off usually pays."),
        ("Why use the Consumer Price Index?", "It measures prices people actually paid, across the whole country, every month, and it is public. That makes it a fair check on whether a category is really getting cheaper."),
        ("Does a falling index mean every product is cheaper?", "No. It is an average. Individual products and stores vary, which is why each offer still needs checking against its own usual price."),
    ])
    body = f'''
<section class="sec"><div class="wrap">
<p class="sec-lede">{E(headline)}</p>
<ul class="rows">{"".join(rows)}</ul>
</div></section>
<section class="sec sec-tint"><div class="wrap"><h2>The price indexes behind the signals</h2>{table}
<p class="note">A signal looks at season first and shows the price trend beside it. Read the full method on the <a href="{{{{root}}}}editorial-policy/">how we work</a> page.</p></div></section>
<div class="wrap">{faq_html}</div>
{ad("pulse")}
{alerts_band()}'''
    add("price-pulse/", "Price Pulse: buy now or wait, for every home category",
        "A monthly buy-or-wait signal for furniture, appliances, tools, bedding and more, built from the sale calendar and U.S. Consumer Price Index data.",
        body, h1="Price Pulse", lede=f"Buy now or wait? A signal for each home category in {MONTH['name']}, with the price trend that sits behind it.",
        crumbs=[("Price Pulse", None)], schema=[faq_schema], section="Price Pulse")


def wizard_html(preselect: str | None = None) -> str:
    data = {"services": [{"slug": s["slug"], "name": s["name"], "mode": s.get("mode", "range"),
                          "q1": {"label": s["q1"]["label"], "options": [list(o) for o in s["q1"]["options"]]},
                          "q2": {"label": s["q2"]["label"], "options": [list(o) for o in s["q2"]["options"]]}} for s in SERVICES],
            "ownership": OWNERSHIP, "timing": TIMING, "contact": CONTACT_PREF, "preselect": preselect}
    tiles = "".join(f'<label class="tile"><input type="radio" name="service" value="{s["slug"]}"{" checked" if s["slug"] == preselect else ""}>'
                    f'<span class="tile-in">{ic(s["icon"])}<span>{E(s["name"])}</span></span></label>' for s in SERVICES)
    tiles += f'<label class="tile"><input type="radio" name="service" value="other"><span class="tile-in">{ic("quote")}<span>Something else</span></span></label>'
    own = "".join(f'<label class="tile tile-row"><input type="radio" name="ownership" value="{E(o)}"><span class="tile-in">{E(o)}</span></label>' for o in OWNERSHIP)
    timing = "".join(f'<label class="tile tile-row"><input type="radio" name="timing" value="{E(o)}"><span class="tile-in">{E(o)}</span></label>' for o in TIMING)
    pref = "".join(f'<label class="tile tile-row"><input type="radio" name="contact_pref" value="{E(o)}"{" checked" if i == 0 else ""}><span class="tile-in">{E(o)}</span></label>'
                   for i, o in enumerate(CONTACT_PREF))
    return f'''<div class="wizard" id="quote-wizard" data-wizard>
<script type="application/json" id="wizard-data">{json.dumps(data, ensure_ascii=False)}</script>
<ol class="steps" aria-label="Progress"><li class="is-on">Project</li><li>Details</li><li>Timing</li><li>Contact</li></ol>
<form class="form wizard-form" data-form="quote" data-subject="New quote request" novalidate>
<fieldset class="step is-on" data-step="1"><legend>What do you need done?</legend>
<div class="tiles">{tiles}</div>
<p class="step-err" role="alert"></p>
<div class="step-nav"><button type="button" class="btn btn-mark" data-next>Continue</button></div></fieldset>

<fieldset class="step" data-step="2"><legend>A couple of details</legend>
<div class="q" data-q="1"><p class="q-label"></p><div class="tiles tiles-col" data-q1></div></div>
<div class="q" data-q="2"><p class="q-label"></p><div class="tiles tiles-col" data-q2></div></div>
<div class="q" data-q="other"><div class="field"><label for="f-other">Describe the project</label><textarea id="f-other" name="project_description" rows="3"></textarea></div></div>
<p class="step-err" role="alert"></p>
<div class="step-nav"><button type="button" class="btn btn-line" data-back>Back</button><button type="button" class="btn btn-mark" data-next>Continue</button></div></fieldset>

<fieldset class="step" data-step="3"><legend>Your home and timing</legend>
<div class="estimate" data-estimate hidden><p class="estimate-label">Ballpark for what you described</p><p class="estimate-range" data-estimate-range></p>
<p class="estimate-note">A national range from published cost guides, adjusted for your answers. Real quotes depend on your home and region.</p></div>
<div class="q"><p class="q-label">Do you own the home?</p><div class="tiles tiles-col">{own}</div></div>
<div class="q"><p class="q-label">When do you want the work done?</p><div class="tiles tiles-col">{timing}</div></div>
<p class="step-err" role="alert"></p>
<div class="step-nav"><button type="button" class="btn btn-line" data-back>Back</button><button type="button" class="btn btn-mark" data-next>Continue</button></div></fieldset>

<fieldset class="step" data-step="4"><legend>Where should we send your matches?</legend>
<div class="grid-2">
{field("name", "Your name", "text", True, attrs='autocomplete="name"')}
{field("zip", "ZIP code", "text", True, attrs='inputmode="numeric" pattern="[0-9]{5}" maxlength="5" autocomplete="postal-code"')}
{field("email", "Email address", "email", True, attrs='autocomplete="email"')}
{field("phone", "Phone number", "tel", False, attrs='autocomplete="tel"', help_="Only if you would like a call or text")}
</div>
<div class="q"><p class="q-label">How should we contact you?</p><div class="tiles tiles-3">{pref}</div></div>
{field("notes", "Anything a provider should know", "textarea", False)}
<div class="hp" aria-hidden="true"><label>Leave this field empty<input type="text" name="_honey" tabindex="-1" autocomplete="off"></label></div>
<label class="check"><input type="checkbox" name="consent" value="yes" required><span>{CONSENT_QUOTE}</span></label>
<p class="step-err" role="alert"></p>
<div class="step-nav"><button type="button" class="btn btn-line" data-back>Back</button><button type="submit" class="btn btn-mark">Send my quote request</button></div>
<p class="form-msg" role="status" aria-live="polite"></p></fieldset>

<div class="step step-done" data-step="done" tabindex="-1"><h3>Request sent</h3>
<p>Thank you. A person will read your request and reply using the contact method you chose. If we have a provider to introduce in your area, we will tell you who they are first.</p>
<div class="estimate" data-estimate-done hidden><p class="estimate-label">Your ballpark</p><p class="estimate-range" data-estimate-range-done></p></div>
<p>While you wait, read <a href="{{{{root}}}}guides/compare-contractor-quotes/">how to compare contractor quotes line by line</a>.</p></div>
</form>
<noscript><p class="note">The quote form needs JavaScript. You can also send your request through the <a href="{{{{contact}}}}">contact page</a>.</p></noscript>
<ul class="assure"><li>{ic("check")}Free to use</li><li>{ic("check")}No obligation to hire</li><li>{ic("check")}Phone number optional</li><li>{ic("check")}We do not sell contact lists</li></ul>
</div>'''


def build_quotes() -> None:
    steps = "".join(f'<li><h3>{E(t)}</h3><p>{E(d)}</p></li>' for t, d in HOW_IT_WORKS)
    grid = "".join(chip(f'{{{{root}}}}quotes/{s["slug"]}/', "#17233B", s["name"], [s["headline"], s["headline_note"]], s["icon"], cls="chip-sm chip-svc")
                   for s in SERVICES)
    flags = "".join(f"<li>{E(x)}</li>" for x in RED_FLAGS)
    faq_html, faq_schema = faq_block(QUOTE_FAQS, "About quote requests")
    body = f'''
<section class="sec sec-wizard"><div class="wrap split split-wizard">
<div>{wizard_html()}</div>
<aside class="side"><div class="panel"><h3>How it works</h3><ol class="numbered">{steps}</ol></div>
<div class="panel"><h3>Good to know</h3><p>Home.Deals is an independent introduction service, not a contractor. Providers may pay us a referral fee. You never do. <a href="{{{{root}}}}disclosure/">How we are funded</a>.</p></div></aside>
</div></section>
<section class="sec sec-tint"><div class="wrap"><h2>Typical costs by project</h2>
<p class="sec-lede">Open a project for a cost table, the factors that move the price and a checklist for comparing quotes.</p>
<div class="chip-grid">{grid}</div>
{stamp("Typical U.S. installed prices compiled from published 2026 cost guides. Your quotes will vary with region, home and materials.")}</div></section>
<section class="sec"><div class="wrap two">
<div><h2>Warning signs in any quote</h2><ul class="crosses">{flags}</ul>
<p><a href="{{{{root}}}}guides/avoid-home-service-scams/">How to handle high-pressure sales</a></p></div>
<div><h2>Compare like with like</h2><p>Three quotes are only useful when they price the same job. Write a one-page scope, send the same page to every provider and compare materials, labour, allowances, permits and warranty line by line.</p>
<p><a href="{{{{root}}}}guides/compare-contractor-quotes/">Read the quote comparison method</a></p></div>
</div></section>
<div class="wrap">{faq_html}</div>'''
    add("quotes/", "Free home project quotes with an instant ballpark price",
        "Request quotes for roofing, solar, HVAC, windows, kitchens, bathrooms and more. See a ballpark price range immediately. Free, with no obligation.",
        body, h1="Compare quotes for a home project", lede="Answer a few questions, see a ballpark price straight away, and get introduced to providers that cover your area.",
        crumbs=[("Free quotes", None)], schema=[faq_schema], scripts=["wizard"], section="Quotes")

    for s in SERVICES:
        intro = "".join(f"<p>{p}</p>" for p in s["intro"])
        costs = "".join(f'<tr><th scope="row">{E(n)}</th><td class="num">{E(lo)} to {E(hi)}</td><td>{E(note)}</td></tr>' for n, lo, hi, note in s["costs"])
        li = lambda xs: "".join(f"<li>{E(x)}</li>" for x in xs)  # noqa: E731
        faq_html, faq_schema = faq_block(s["faqs"])
        body = f'''
<section class="sec"><div class="wrap split">
<div class="prose">
<div class="headline-cost"><p class="big">{E(s["headline"])}</p><p>{E(s["headline_note"].capitalize())}.</p></div>
{intro}
<h2>What {E(s["name"].lower())} costs</h2>
<div class="table-wrap"><table class="tbl"><thead><tr><th scope="col">Job</th><th scope="col" class="num">Typical range</th><th scope="col">Notes</th></tr></thead><tbody>{costs}</tbody></table></div>
{stamp("Typical U.S. installed prices compiled from published 2026 cost guides. Regional prices differ.")}
<div class="two"><div><h2>What moves the price</h2><ul class="ticks">{li(s["factors"])}</ul></div>
<div><h2>Compare quotes on these points</h2><ul class="ticks">{li(s["compare"])}</ul></div></div>
<h2>Questions to ask every provider</h2><ul class="ticks">{li(s["ask"])}</ul>
</div>
<aside class="side"><div class="panel"><h3>Before you sign</h3><ul class="links">
<li><a href="{{{{root}}}}guides/compare-contractor-quotes/">Compare quotes line by line</a></li>
<li><a href="{{{{root}}}}guides/avoid-home-service-scams/">Spot high-pressure sales</a></li>
<li><a href="{{{{root}}}}quotes/">See costs for other projects</a></li></ul></div></aside>
</div></section>
<section class="sec sec-tint sec-wizard" id="get-quotes"><div class="wrap narrow"><h2>Get {E(s["name"].lower())} quotes</h2>
<p class="sec-lede">Free, with no obligation. You will see a ballpark range before you share any contact details.</p>
{wizard_html(s["slug"])}</div></section>
<div class="wrap">{faq_html}</div>
{ad("service")}'''
        add(f'quotes/{s["slug"]}/', f'{s["name"]} cost in 2026 and free quotes',
            f'{s["name"]}: typical costs ({s["headline"]}), what moves the price, how to compare quotes and a free quote request with an instant ballpark.',
            body, h1=f'{s["name"]}: costs and free quotes', lede=s["short"] + " What it costs, what changes the price and how to compare quotes.",
            crumbs=[("Free quotes", "quotes/"), (s["name"], None)], schema=[faq_schema], scripts=["wizard"], section="Quotes",
            cta=("Get quotes", "#get-quotes"))


def payment(principal: float, rate_pct: float, years: int) -> float:
    r = rate_pct / 100 / 12
    n = years * 12
    return principal * r / (1 - (1 + r) ** -n) if r else principal / n


def build_rates() -> None:
    if not (RATES and R30):
        add("rates/", "Mortgage rates today", "Weekly average U.S. mortgage rates.", '<section class="sec"><div class="wrap"><p class="note">Rate data loads with the next automatic refresh.</p></div></section>',
            h1="Mortgage rates", crumbs=[("Mortgage rates", None)], section="Rates")
        return
    s30, s15 = RATES["series"]["30"], RATES["series"]["15"]
    last = dt.date.fromisoformat(R30["date"])
    label = f"Average 30-year and 15-year fixed mortgage rates to {fdate(last)}"
    chart1 = rate_chart(s30, s15, last - dt.timedelta(days=366), label + ", past year")
    chart5 = rate_chart(s30, s15, last - dt.timedelta(days=365 * 5 + 2), label + ", past five years")

    def kv(title, s):
        ya = f'{s["year_ago"]:.2f}%' if s.get("year_ago") else "n/a"
        return (f'<div class="panel kv"><h3>{title}</h3><p class="big">{s["rate"]:.2f}%</p>'
                f'<dl><div><dt>Change on the week</dt><dd>{signed(s["week_change"], 2, " pts")}</dd></div>'
                f'<div><dt>A year ago</dt><dd>{ya}</dd></div>'
                f'<div><dt>52-week range</dt><dd>{s["low_52w"]:.2f}% to {s["high_52w"]:.2f}%</dd></div></dl></div>')
    loan = 300000
    base = R30["rate"]
    rows = []
    for delta in (-1.0, -0.5, -0.25, 0, 0.25, 0.5, 1.0):
        rate = base + delta
        pay = payment(loan, rate, 30)
        diff = pay - payment(loan, base, 30)
        cls = ' class="is-now"' if delta == 0 else ""
        rows.append(f'<tr{cls}><th scope="row">{rate:.2f}%{" (this week)" if delta == 0 else ""}</th><td class="num">{money(pay)}</td>'
                    f'<td class="num">{"—" if delta == 0 else signed(diff, 0, "").replace("+", "+$").replace("−", "−$")}</td>'
                    f'<td class="num">{money(pay * 360 - loan)}</td></tr>')
    faq_html, faq_schema = faq_block([
        ("Where do these rates come from?", "They are Freddie Mac’s weekly national averages from its Primary Mortgage Market Survey, published each Thursday and retrieved from FRED at the Federal Reserve Bank of St. Louis."),
        ("Will I get this rate?", "Not necessarily. The survey is an average for borrowers with strong credit and a 20% down payment. Your rate depends on credit score, down payment, loan type, points and lender."),
        ("How often is this page updated?", "The site checks for new data four times a day. The survey itself is weekly."),
        ("Should I wait for rates to fall?", "Nobody can forecast rates reliably. A more useful question is whether the payment works for you today, and what a refinance would need to save to be worth doing later. The refinance calculator answers the second part."),
    ])
    body = f'''
<section class="sec"><div class="wrap">
<div class="two">{kv("30-year fixed", R30)}{kv("15-year fixed", R15) if R15 else ""}</div>
{stamp(f'Weekly U.S. averages for the week of {fdate(last)}. Source: Freddie Mac Primary Mortgage Market Survey, retrieved from FRED, Federal Reserve Bank of St. Louis.')}
</div></section>
<section class="sec sec-tint"><div class="wrap">
<div class="sec-head"><h2>How rates have moved</h2>
<div class="pills" role="group" aria-label="Chart range" data-toggle="rate-chart"><button type="button" class="pill is-on" data-show="y1" aria-pressed="true">1 year</button><button type="button" class="pill" data-show="y5" aria-pressed="false">5 years</button></div></div>
<div class="chart-box" id="rate-chart"><div data-pane="y1">{chart1}</div><div data-pane="y5" hidden>{chart5}</div></div>
</div></section>
<section class="sec"><div class="wrap split">
<div><h2>What a rate change does to a payment</h2>
<p class="sec-lede">Principal and interest on a {money(loan)} loan over 30 years.</p>
<div class="table-wrap"><table class="tbl"><thead><tr><th scope="col">Rate</th><th scope="col" class="num">Monthly payment</th><th scope="col" class="num">Difference</th><th scope="col" class="num">Total interest</th></tr></thead><tbody>{"".join(rows)}</tbody></table></div></div>
<aside class="side"><div class="panel"><h3>Run your own numbers</h3><ul class="links">
<li><a href="{{{{root}}}}tools/mortgage/">Mortgage payment calculator</a></li>
<li><a href="{{{{root}}}}tools/refinance/">Refinance break-even calculator</a></li>
<li><a href="{{{{root}}}}guides/refinance-math/">Refinance math when rates are high</a></li>
<li><a href="{{{{root}}}}market/">Housing market meter</a></li></ul></div></aside>
</div></section>
<div class="wrap">{faq_html}
<p class="note">Home.Deals is not a lender or broker and does not offer loans. Figures are national averages for information only.</p></div>
{ad("rates")}
{alerts_band("Mortgage rates")}'''
    add("rates/", f'Mortgage rates today: 30-year average {R30["rate"]:.2f}%',
        f'The average 30-year fixed mortgage rate is {R30["rate"]:.2f}% for the week of {fdate(last)}. Weekly averages, a five-year chart and payment tables.',
        body, h1="Mortgage rates", lede=(f'The national average for a 30-year fixed mortgage is {R30["rate"]:.2f}%, '
              + ("unchanged on the week." if abs(R30["week_change"]) < 0.005 else
                 f'{"down" if R30["week_change"] < 0 else "up"} {abs(R30["week_change"]):.2f} points on the week.')),
        crumbs=[("Mortgage rates", None)], schema=[faq_schema], section="Rates")


def build_market() -> None:
    meter = market_meter()
    if not meter:
        add("market/", "Housing market meter", "National housing conditions for buyers.", '<section class="sec"><div class="wrap"><p class="note">Housing data loads with the next automatic refresh.</p></div></section>',
            h1="Housing market meter", crumbs=[("Housing market", None)], section="Market")
        return
    parts = "".join(f'<li class="row"><div class="row-main"><h3>{E(n)}</h3><p>{E(text)}</p></div>'
                    f'<span class="bar" aria-hidden="true"><span style="width:{score}%"></span></span><span class="tagline">{score} / 100</span></li>'
                    for n, score, text in meter["parts"])
    stats = []
    labels = {"median_price": ("Median price of new houses sold", lambda v: money(v)), "months_supply": ("Months of supply, new houses", lambda v: f"{v:.1f}"),
              "hpi": ("FHFA house price index", lambda v: f"{v:.1f}"), "new_home_sales": ("New houses sold, annual rate", lambda v: f"{v:,.0f},000")}
    for key, (name, fmt) in labels.items():
        ser = MSER.get(key)
        if not ser:
            continue
        period = fdate(ser["date"], "month")
        if key == "median_price":  # a quarterly series: show the quarter, not its first month
            period = f'Q{(int(ser["date"][5:7]) - 1) // 3 + 1} {ser["date"][:4]}'
        stats.append(f'<tr><th scope="row">{name}</th><td class="num">{fmt(ser["value"])}</td><td class="num">{signed(ser["yoy"]) if ser.get("yoy") is not None else "—"}</td>'
                     f'<td>{period}</td><td class="spark-cell">{spark([v for _, v in ser["spark"]], 110, 30)}</td></tr>')
    faq_html, faq_schema = faq_block([
        ("What does the meter measure?", "National conditions for buyers, from 0 to 100. It combines the supply of new homes, the pace of house price growth and where mortgage rates sit in their 52-week range."),
        ("Does a high score mean I should buy?", "No. It says national conditions lean towards buyers. Your decision depends on your local market, your finances and how long you plan to stay."),
        ("Why new-home supply?", "It is published monthly by the Census Bureau and HUD and is in the public domain. It moves with builder incentives and price cuts, which are a direct form of “home deal”."),
    ])
    body = f'''
<section class="sec"><div class="wrap split">
<div><div class="meter" role="img" aria-label="Housing market meter: {meter["score"]} out of 100, {E(meter["label"])}">
<p class="big">{meter["score"]}<span class="big-unit"> / 100</span></p><p class="meter-label">{E(meter["label"])}</p>
<div class="meter-track"><span class="meter-mark" style="left:{meter["score"]}%"></span></div>
<div class="meter-scale"><span>Sellers have the edge</span><span>Balanced</span><span>Buyers have leverage</span></div></div>
<h2>What goes into the score</h2><ul class="rows">{parts}</ul></div>
<aside class="side"><div class="panel"><h3>If you are buying</h3><ul class="links">
<li><a href="{{{{root}}}}rates/">This week’s mortgage rates</a></li>
<li><a href="{{{{root}}}}tools/mortgage/">Mortgage payment calculator</a></li>
<li><a href="{{{{root}}}}guides/first-year-homeowner-budget/">A first-year budget for a new homeowner</a></li></ul></div>
<div class="panel"><h3>If you already own</h3><ul class="links">
<li><a href="{{{{root}}}}tools/refinance/">Refinance break-even calculator</a></li>
<li><a href="{{{{root}}}}quotes/">Compare quotes for a project</a></li></ul></div></aside>
</div></section>
<section class="sec sec-tint"><div class="wrap"><h2>The numbers</h2>
<div class="table-wrap"><table class="tbl"><thead><tr><th scope="col">Measure</th><th scope="col" class="num">Latest</th><th scope="col" class="num">Change over a year</th><th scope="col">Period</th><th scope="col">Two years</th></tr></thead><tbody>{"".join(stats)}</tbody></table></div>
{stamp("Sources: U.S. Census Bureau and HUD new residential sales, Federal Housing Finance Agency, Freddie Mac. Retrieved from FRED, Federal Reserve Bank of St. Louis.")}
<p class="note">The meter is an editorial summary of national data. It is not a forecast or advice about any property. <a href="{{{{root}}}}editorial-policy/">How it is calculated</a>.</p></div></section>
<div class="wrap">{faq_html}</div>
{ad("market")}'''
    add("market/", f'Housing market meter: {meter["score"]} out of 100, {meter["label"].lower()}',
        "A simple national read on whether housing conditions favour buyers or sellers, built from public data on supply, prices and mortgage rates.",
        body, h1="Housing market meter", lede="Deals on homes themselves: a national read on whether conditions currently favour buyers or sellers.",
        crumbs=[("Housing market", None)], schema=[faq_schema], section="Market")


def tool_form(t: dict) -> str:
    groups = []
    for title, fields in t["groups"]:
        inner = []
        for fid, label, kind, default, help_ in fields:
            default = default.replace("{{rate30}}", TOKENS["rate30"]).replace("{{kwh}}", TOKENS["kwh"])
            name = f'{t["slug"]}-{fid}'
            help_html = f'<span class="help">{E(help_)}</span>' if help_ else ""
            if kind.startswith("select:"):
                opts = "".join(f"<option{' selected' if o == default else ''}>{E(o)}</option>" for o in kind[7:].split("|"))
                control = f'<select id="{name}" data-f="{fid}">{opts}</select>'
            else:
                unit = {"money": '<span class="unit">$</span>', "pct": '<span class="unit unit-r">%</span>'}.get(kind, "")
                step = "1" if kind == "int" else "any"
                control = (f'<span class="input-unit input-{kind}">{unit}<input id="{name}" data-f="{fid}" type="number" inputmode="decimal" step="{step}" min="0" value="{E(default)}"></span>')
            inner.append(f'<div class="field"><label for="{name}">{E(label)}</label>{control}{help_html}</div>')
        groups.append(f'<fieldset class="tool-group"><legend>{E(title)}</legend><div class="grid-2">{"".join(inner)}</div></fieldset>')
    return (f'<form class="form tool" data-tool="{t["slug"]}" novalidate>{"".join(groups)}'
            f'<div class="form-actions"><button class="btn btn-mark" type="submit">{E(t["action"])}</button>'
            '<button class="btn btn-line" type="reset">Reset</button></div></form>'
            '<div class="result" data-result aria-live="polite"><p class="result-empty">Results appear here as you type.</p></div>'
            '<noscript><p class="note">The calculator needs JavaScript.</p></noscript>')


def build_tools() -> None:
    rows = "".join(f'<li class="row"><span class="swatch swatch-ink">{ic(t["icon"], "chip-ic")}</span><div class="row-main"><h3><a href="{{{{root}}}}tools/{t["slug"]}/">{E(t["name"])}</a></h3><p>{E(t["desc"])}</p></div></li>'
                   for t in TOOLS)
    body = f'''<section class="sec"><div class="wrap"><ul class="rows">{rows}</ul>
<p class="note">Calculators run in your browser. Nothing you enter is sent to us.</p></div></section>{ad("tools")}{quotes_band()}'''
    add("tools/", "Home calculators: deals, energy, repairs, paint, flooring and loans",
        "Free calculators for checking a discount, comparing unit prices, mortgage payments, refinancing, energy costs, repair or replace decisions, paint and flooring.",
        body, h1="Calculators", lede="Eight calculators for the decisions that cost the most around a home.", crumbs=[("Calculators", None)], section="Tools")
    for t in TOOLS:
        how = "".join(f"<li>{E(x)}</li>" for x in t["how"])
        faq_html, faq_schema = faq_block(t["faqs"])
        others = "".join(f'<li><a href="{{{{root}}}}tools/{o["slug"]}/">{E(o["name"])}</a></li>' for o in TOOLS if o["slug"] != t["slug"])
        body = f'''<section class="sec"><div class="wrap split">
<div><div class="tool-box">{tool_form(t)}</div>
<h2>How this calculator works</h2><ul class="ticks">{how}</ul>
<p class="note">Results are estimates from the figures you enter. They are not financial or professional advice.</p></div>
<aside class="side"><div class="panel"><h3>More calculators</h3><ul class="links">{others}</ul></div></aside>
</div></section>
<div class="wrap">{faq_html}</div>{ad("tool")}'''
        add(f'tools/{t["slug"]}/', t["name"], t["desc"], body, h1=t["name"], lede=t["desc"],
            crumbs=[("Calculators", "tools/"), (t["name"], None)], schema=[faq_schema], scripts=["tools"], section="Tools")


def build_recalls() -> None:
    items = (RECALLS or {}).get("items", [])[:72]
    present = []
    for r in items:
        if r["cat"] not in present:
            present.append(r["cat"])
    kinds = [("all", "All recalls")] + [(k, CAT[k]["name"] if k in CAT else EXTRA_RECALL_CATS[k][0]) for k in
                                        [c["slug"] for c in CATEGORIES if c["slug"] in present] + [k for k in EXTRA_RECALL_CATS if k in present]]
    rows = "".join(recall_row(r) for r in items) or '<li class="row"><div class="row-main"><p>Recall data loads with the next automatic refresh.</p></div></li>'
    alerts = "".join(f'<li class="row"><div class="row-main"><h3><a href="{E(a["url"])}" target="_blank" rel="noopener nofollow">{E(a["title"])}</a></h3></div>'
                     f'<span class="tagline">{fdate(a["date"], "short") if a.get("date") else ""}</span></li>' for a in (ALERTS or {}).get("items", [])[:8])
    alerts_html = (f'<section class="sec sec-tint"><div class="wrap"><h2>Consumer alerts on homes, pricing and shopping</h2><ul class="rows">{alerts}</ul>'
                   f'{stamp("Source: U.S. Federal Trade Commission.")}</div></section>') if alerts else ""
    faq_html, faq_schema = faq_block([
        ("What should I do if I own a recalled product?", "Stop using it and open the official notice. Each one explains the remedy, which is usually a refund, a free repair or a replacement, and how to claim it."),
        ("Is it legal to sell a recalled product?", "No. Selling or reselling a recalled consumer product is against U.S. federal law."),
        ("Which recalls are shown here?", "Recent recalls of products for the home: furniture, mattresses, appliances, heating and cooling, tools, outdoor equipment, lighting, decor and nursery items. Toys, clothing, vehicles and sports equipment are left out."),
        ("How current is this list?", "The site checks the Consumer Product Safety Commission’s public recall database four times a day."),
    ])
    newest = fdate(items[0]["date"]) if items else ""
    body = f'''
<section class="sec"><div class="wrap">
{filter_bar("recalls", kinds, "Search by brand or product")}
<ul class="rows" id="recalls">{rows}</ul>
{stamp(f'Showing the {len(items)} most recent home-related recalls. Newest notice: {newest}. Source: U.S. Consumer Product Safety Commission recall database. Always confirm details in the official notice.')}
</div></section>
{alerts_html}
<section class="sec"><div class="wrap two">
<div class="plain"><h2>Two-minute check before you buy</h2><ol class="numbered"><li><p>Find the brand and model number.</p></li><li><p>Search it here, then in the full database at CPSC.gov for older products.</p></li><li><p>No model number from the seller? Treat that as your answer.</p></li></ol></div>
<div class="plain"><h2>Why it matters for deals</h2><p>Clearance lots, marketplaces and secondhand listings are where recalled stock is most likely to turn up. A low price on an unfamiliar brand deserves a search first.</p>
<p><a href="{{{{root}}}}guides/recalls-before-you-buy/">Read the full guide to recalls</a></p></div>
</div></section>
<div class="wrap">{faq_html}</div>{ad("recalls")}'''
    add("recalls/", "Recall Radar: recent home product recalls",
        "Recent recalls of furniture, mattresses, appliances, heaters, tools and other home products from the U.S. Consumer Product Safety Commission, updated daily.",
        body, h1="Recall Radar", lede="Recent recalls of products for the home. Search a brand before you buy clearance, open-box or secondhand.",
        crumbs=[("Recall Radar", None)], schema=[faq_schema], section="Recalls")


def build_videos() -> None:
    items = (VIDEOS or {}).get("items", [])[:36]
    kinds = [("all", "All videos"), ("repairs", "Repairs"), ("projects", "Projects and tools"), ("buying", "Buying advice"), ("energy", "Appliances and energy")]
    grid = "".join(video_card(v) for v in items) or "<li>Videos load with the next automatic refresh.</li>"
    body = f'''<section class="sec"><div class="wrap">
{filter_bar("videos", kinds, "Search videos and channels")}
<ul class="video-grid" id="videos">{grid}</ul>
{stamp("Latest uploads from independent home improvement and consumer channels, refreshed several times a day. Videos play in the official YouTube player and belong to their creators. Home.Deals is not affiliated with these channels.")}
<p class="note">Nothing loads from YouTube until you press play. Know a channel that belongs here? <a href="{{{{contact}}}}" target="_blank" rel="noopener">Tell us</a>.</p>
</div></section>{ad("videos")}{quotes_band()}'''
    add("videos/", "Home repair, project and buying videos",
        "The latest videos on home repairs, DIY projects, tools, appliances and smart buying from established channels, in one place.",
        body, h1="Videos", lede="Repairs, projects and buying advice from established home improvement and consumer channels.",
        crumbs=[("Videos", None)], section="Videos")


def build_guides() -> None:
    topics: dict[str, list] = {}
    for g in GUIDES:
        topics.setdefault(g["topic"], []).append(g)
    sections = "".join(f'<h2>{E(topic)}</h2><ul class="rows">{"".join(guide_row(g) for g in gs)}</ul>' for topic, gs in topics.items())
    add("guides/", "Guides: buying, timing, projects and home money",
        "Plain-language guides to judging a deal, timing purchases, comparing contractor quotes, energy savings, refinancing and avoiding scams.",
        f'<section class="sec"><div class="wrap narrow-wide">{sections}</div></section>{ad("guides")}{alerts_band()}',
        h1="Guides", lede="How to judge a deal, time a purchase, compare quotes and keep the costs of a home under control.", crumbs=[("Guides", None)], section="Guides")
    for g in GUIDES:
        points = "".join(f"<li>{E(p)}</li>" for p in g["points"])
        body_html = g["body"]
        schema = {"@context": "https://schema.org", "@type": "Article", "headline": g["title"], "description": g["desc"],
                  "datePublished": g["date"], "dateModified": g["date"], "mainEntityOfPage": f'{SITE["url"]}/guides/{g["slug"]}/',
                  "author": {"@type": "Organization", "name": SITE["name"]}, "publisher": {"@type": "Organization", "name": SITE["name"],
                                                                                           "logo": {"@type": "ImageObject", "url": SITE["url"] + "/assets/img/icon-512.png"}}}
        body = f'''<article class="sec"><div class="wrap split">
<div class="prose"><div class="keypoints"><h2>In short</h2><ul>{points}</ul></div>
{body_html}
{ad("article")}
<p class="stamp">Published {fdate(g["date"])}. Figures marked with a date are refreshed automatically from public sources.</p></div>
<aside class="side">{related_links(g["related"])}
<div class="panel"><h3>Planning a project?</h3><p>See a ballpark price and compare quotes.</p><p><a class="btn btn-ink" href="{{{{root}}}}quotes/">Get free quotes</a></p></div></aside>
</div></article>{alerts_band()}'''
        add(f'guides/{g["slug"]}/', g["title"], g["desc"], body, h1=g["title"], lede=g["desc"],
            crumbs=[("Guides", "guides/"), (g["title"], None)], schema=[schema], section="Guides", meta_line=f'{g["topic"]}, {g["minutes"]} minute read')


def build_community() -> None:
    gv = SITE["giveaway"]
    rules = "".join(f'<li><h3>{E(t)}</h3><p>{E(d)}</p></li>' for t, d in GIVEAWAY_STANDING_RULES)
    if gv["active"] and gv["prize"] and gv["start"] and gv["end"]:
        status = (f'<div class="panel panel-sig"><h2>{E(gv["title"])}</h2><p class="big">{E(gv["prize"])}</p>'
                  f'<p>Approximate retail value {E(gv["prize_value"])}. {gv["winners"]} winner{"s" if gv["winners"] != 1 else ""}. '
                  f'Entries open {fdate(gv["start"])} and close {fdate(gv["end"])} at 11:59 p.m. Eastern Time. Sponsor: {E(gv["sponsor"])}.</p></div>')
        fields = (f'<div class="grid-2">{field("name", "Your name", "text", True, attrs="autocomplete=name")}{field("email", "Email address", "email", True, attrs="autocomplete=email")}'
                  f'{field("zip", "ZIP code", "text", True, attrs="inputmode=numeric maxlength=5")}{field("state", "State", "text", True, attrs="autocomplete=address-level1")}</div>'
                  '<label class="check"><input type="checkbox" name="age_18" value="yes" required><span>I am 18 or older and a legal resident of the 50 United States or D.C.</span></label>'
                  '<label class="check"><input type="checkbox" name="alerts_opt_in" value="yes"><span>Also send me deal alerts. Optional, and it does not affect my chances.</span></label>')
        entry = form("giveaway", f'Giveaway entry: {gv["title"]}', fields, "Enter the giveaway", "You are entered. Good luck.",
                     consent='I have read and accept the giveaway rules on this page and the <a href="{{root}}privacy/">privacy policy</a>.')
        entry_title = "Enter this round"
    else:
        status = ('<div class="panel"><h2>No round is open right now</h2><p>A giveaway opens only when a prize is confirmed, with its value, dates and eligibility published on this page first. '
                  'Leave your email and we will tell you when the next round opens.</p></div>')
        fields = field("email", "Email address", "email", True, attrs='autocomplete="email"')
        entry = form("giveaway-notify", "Giveaway: notify me", fields, "Tell me when a round opens", "Done. We will email you when the next round opens.")
        entry_title = "Hear about the next round"
    body = f'''<section class="sec"><div class="wrap split">
<div>{status}<h2>{entry_title}</h2><div class="tool-box">{entry}</div></div>
<aside class="side"><div class="panel"><h3>How giveaways work here</h3><ul class="ticks"><li>Free to enter, always</li><li>Winners drawn at random</li><li>No ad clicks, purchases or donations required</li><li>Prize and rules published before entries open</li></ul></div>
<div class="panel"><h3>Supply a prize</h3><p>Brands can sponsor a round and are credited throughout.</p><p><a href="{{{{root}}}}advertise/">Sponsorship options</a></p></div></aside>
</div></section>
<section class="sec sec-tint"><div class="wrap narrow-wide"><h2>Standing rules for every round</h2><ol class="numbered rules">{rules}</ol></div></section>'''
    add("giveaways/", "Giveaways and prizes", "Free-to-enter prize rounds for Home.Deals readers, with the rules that apply to every round.",
        body, h1="Giveaways", lede="Free prize rounds for readers. Each round is announced here with its prize and rules before entries open.",
        crumbs=[("Giveaways", None)], section="Community")

    uses = "".join(f'<li class="row"><div class="row-main"><h3>{E(t)}</h3><p>{E(d)}</p></div></li>' for t, d in SUPPORT_USES)
    links = {k: v for k, v in SITE["donate"].items() if v}
    names = {"paypal": "Support with PayPal", "stripe": "Support by card", "kofi": "Support on Ko-fi", "buymeacoffee": "Buy us a coffee"}
    if links:
        give = '<p class="hero-actions">' + "".join(f'<a class="btn btn-mark" href="{E(url)}" target="_blank" rel="noopener">{names[k]}</a>' for k, url in links.items()) + "</p>"
        give += "<p class=\"note\">Payments are handled by the payment provider. Home.Deals never sees your card details.</p>"
    else:
        fields = (f'<div class="grid-2">{field("name", "Your name", "text", True, attrs="autocomplete=name")}{field("email", "Email address", "email", True, attrs="autocomplete=email")}'
                  f'{field("amount", "Amount you would like to give", "select", True, options=["$5", "$10", "$25", "$50", "$100", "Another amount"])}'
                  f'{field("frequency", "How often", "select", True, options=["Once", "Monthly"])}</div>{field("message", "Message", "textarea", False)}')
        give = ('<p>Online payment is being set up. Make a pledge below and we will reply with a secure payment link. You are not charged anything by sending this form.</p>'
                + form("support", "Support pledge", fields, "Send my pledge", "Thank you. We will reply with a secure payment link."))
    body = f'''<section class="sec"><div class="wrap split">
<div><h2>Give what the site is worth to you</h2><div class="tool-box">{give}</div>
<h2>Where support goes</h2><ul class="rows">{uses}</ul></div>
<aside class="side"><div class="panel"><h3>Other ways to help</h3><ul class="links"><li><a href="{{{{root}}}}submit/">Submit a deal you have checked</a></li><li><a href="{{{{root}}}}careers/">Contribute your skills</a></li><li><a href="{{{{root}}}}advertise/">Sponsor a section</a></li></ul>
<p>Sharing the calendar with someone about to buy a mattress or a refrigerator helps too.</p></div>
<div class="panel"><h3>Plain facts</h3><p>Home.Deals is not a charity, and contributions are not tax-deductible. Supporters do not receive anything that affects what we publish. We never ask anyone to click on advertising.</p></div></aside>
</div></section>'''
    add("support/", "Support Home.Deals", "Reader support pays for the data pipeline, new guides, contributors and prizes that keep Home.Deals free and independent.",
        body, h1="Support Home.Deals", lede="The site is free to use. Voluntary support from readers keeps it independent and growing.",
        crumbs=[("Support", None)], section="Community")

    formats = "".join(f'<li class="row"><div class="row-main"><h3>{E(t)}</h3><p>{E(d)}</p></div></li>' for t, d in ADVERTISE_FORMATS)
    body = f'''<section class="sec"><div class="wrap split">
<div><h2>Ways to work with Home.Deals</h2><ul class="rows">{formats}</ul>
<p class="hero-actions"><a class="btn btn-mark" href="{{{{contact}}}}" target="_blank" rel="noopener">Contact us about sponsorship or partnership</a></p></div>
<aside class="side"><div class="panel"><h3>Who reads Home.Deals</h3><p>Homeowners, renters and buyers who are about to spend on furniture, appliances, tools or a home project, and want to time it well.</p></div>
<div class="panel"><h3>Our rules</h3><ul class="ticks"><li>Sponsored placements are labelled</li><li>Sponsors do not see or shape signals, calendars or guides</li><li>No pop-ups, no auto-playing audio</li><li>Quote partners must be licensed and insured where their trade requires it</li></ul></div></aside>
</div></section>'''
    add("advertise/", "Advertise, sponsor or partner with Home.Deals",
        "Sponsorship, advertising and partnership options on Home.Deals, including category and calculator sponsorship and quote partnerships for service providers.",
        body, h1="Advertise and partner", lede="Reach people at the moment they are deciding what to buy for their home, with placements that are always labelled.",
        crumbs=[("Advertise", None)], section="Community")

    roles = "".join(f'<li class="row"><div class="row-main"><h3>{E(t)}</h3><p>{E(d)}</p></div></li>' for t, d in CAREER_ROLES)
    fields = (f'<div class="grid-2">{field("name", "Your name", "text", True, attrs="autocomplete=name")}{field("email", "Email address", "email", True, attrs="autocomplete=email")}'
              f'{field("role", "Role you are interested in", "select", True, options=[t for t, _ in CAREER_ROLES] + ["Something else"])}'
              f'{field("links", "Portfolio or profile link", "url", False, attrs="placeholder=https://")}</div>'
              f'{field("about", "What would you like to do, and why are you a good fit?", "textarea", True)}')
    body = f'''<section class="sec"><div class="wrap split">
<div><h2>Roles we are looking for</h2><ul class="rows">{roles}</ul>
<h2>Tell us about yourself</h2><div class="tool-box">{form("careers", "Work with us application", fields, "Send my application", "Thank you. We read every application and reply to those that fit a current need.")}</div></div>
<aside class="side"><div class="panel"><h3>How it works</h3><p>Home.Deals is a small, independent project. Roles are freelance and project-based. Paid assignments are offered as the budget allows, and the rate is agreed in writing before any work begins.</p></div>
<div class="panel"><h3>What we value</h3><ul class="ticks"><li>Evidence over opinion</li><li>Plain language</li><li>Saying “we do not know” when that is true</li></ul></div></aside>
</div></section>'''
    add("careers/", "Work with Home.Deals", "Freelance and contributor roles at Home.Deals: deal scouts, guide writers, video makers, developers and regional partners.",
        body, h1="Work with us", lede="We are building a small team of contributors who care about getting the price right.", crumbs=[("Work with us", None)], section="Community")

    cats = "".join(f'<label class="tile tile-row"><input type="checkbox" name="categories" value="{E(c["name"])}"><span class="tile-in">{E(c["name"])}</span></label>' for c in CATEGORIES)
    cats += '<label class="tile tile-row"><input type="checkbox" name="categories" value="Mortgage rates"><span class="tile-in">Mortgage rates</span></label>'
    fields = (f'<div class="grid-2">{field("email", "Email address", "email", True, attrs="autocomplete=email")}{field("zip", "ZIP code", "text", False, attrs="inputmode=numeric maxlength=5", help_="For regional sales and rebates")}</div>'
              f'<fieldset class="q"><legend class="q-label">What should we watch for you?</legend><div class="tiles tiles-3">{cats}</div></fieldset>')
    body = f'''<section class="sec"><div class="wrap split">
<div><div class="tool-box">{form("alerts", "Deal alert sign-up", fields, "Send me deal alerts", "You are on the list. We will email you only when the timing is right.")}</div></div>
<aside class="side"><div class="panel"><h3>What you get</h3><ul class="ticks"><li>A short note when a category you picked enters a buy window</li><li>A heads-up before the big sale weekends</li><li>Rate moves, if you ask for them</li></ul></div>
<div class="panel"><h3>What you do not get</h3><ul class="crosses"><li>Daily emails</li><li>Your address passed to anyone else</li></ul></div></aside>
</div></section>'''
    add("alerts/", "Deal alerts for the home", "Sign up for a short email when a home category enters its strongest sale period or mortgage rates move.",
        body, h1="Deal alerts", lede="Pick the categories you care about and hear from us only when the timing is right.", crumbs=[("Deal alerts", None)], section="Community")

    fields = (f'<div class="grid-2">{field("deal_url", "Link to the deal", "url", True, attrs="placeholder=https://")}{field("store", "Store", "text", True)}'
              f'{field("item", "What is it?", "text", True)}{field("category", "Category", "select", True, options=[c["name"] for c in CATEGORIES])}'
              f'{field("price", "Deal price", "text", True, attrs="inputmode=decimal placeholder=$")}{field("usual_price", "Usual selling price", "text", True, attrs="inputmode=decimal placeholder=$", help_="What it normally sells for, not the crossed-out price")}</div>'
              f'{field("evidence", "How do you know it is a good price?", "textarea", True, help_="Price history, a competitor’s price or a past sale")}'
              f'<div class="grid-2">{field("name", "Name to credit", "text", False)}{field("email", "Email address", "email", False, help_="Only if you want a reply")}</div>')
    body = f'''<section class="sec"><div class="wrap split">
<div><div class="tool-box">{form("submit-deal", "Deal submission", fields, "Submit this deal", "Thank you. We check every submission before publishing.", consent='I found this deal myself, the details are accurate to the best of my knowledge, and I have read the <a href="{{root}}terms/">terms</a>.')}</div></div>
<aside class="side"><div class="panel"><h3>What makes the cut</h3><ul class="ticks"><li>Something for the home</li><li>Clearly below its usual selling price</li><li>From a seller with a real return policy</li><li>Not a recalled product</li></ul></div>
<div class="panel"><h3>Check it first</h3><p>Run the numbers through the Deal Score checker before you send it.</p><p><a href="{{{{root}}}}tools/deal-score/">Open the Deal Score checker</a></p></div></aside>
</div></section>'''
    add("submit/", "Submit a deal", "Send in a home deal you have checked against its usual price. Deals that hold up are published with credit.",
        body, h1="Submit a deal", lede="Found a price that genuinely beats the usual? Send it in with the evidence.", crumbs=[("Submit a deal", None)], section="Community")


def build_standing() -> None:
    fields = (f'<div class="grid-2">{field("name", "Your name", "text", True, attrs="autocomplete=name")}{field("email", "Email address", "email", True, attrs="autocomplete=email")}</div>'
              f'{field("topic", "What is it about?", "select", True, options=["A question about the site", "A correction", "A quote request I sent", "Deal alerts", "Something else"])}'
              f'{field("message", "Message", "textarea", True)}')
    body = f'''<section class="sec"><div class="wrap split">
<div><div class="panel panel-sig"><h2>Website, domain name, sponsorship, advertising and partnership</h2>
<p>For anything commercial, including interest in this website or its domain name, use the contact page.</p>
<p class="hero-actions"><a class="btn btn-mark" href="{{{{contact}}}}" target="_blank" rel="noopener">Open the contact page</a></p></div>
<h2>Send a quick message</h2><div class="tool-box">{form("contact", "Message from the contact page", fields, "Send message", "Message sent. We reply to every genuine enquiry.")}</div></div>
<aside class="side"><div class="panel"><h3>Faster answers</h3><ul class="links"><li><a href="{{{{root}}}}quotes/">Request project quotes</a></li><li><a href="{{{{root}}}}submit/">Submit a deal</a></li><li><a href="{{{{root}}}}editorial-policy/">How the data and signals work</a></li><li><a href="{{{{root}}}}privacy/">Privacy requests</a></li></ul></div></aside>
</div></section>'''
    add("contact/", "Contact Home.Deals", "How to reach Home.Deals about the site, corrections, sponsorship, advertising, partnership or the domain name.",
        body, h1="Contact", lede="Questions, corrections and commercial enquiries are all welcome.", crumbs=[("Contact", None)], section="About")

    prose_pages = [
        ("about/", "About Home.Deals", "What Home.Deals is, how it stays current and how it is funded.", "About Home.Deals",
         "An independent guide to buying for the home at the right time and the right price.", ABOUT, True),
        ("editorial-policy/", "How we work: data sources and method", "Where the numbers on Home.Deals come from, how buy-or-wait signals and the housing meter are calculated, and our editorial rules.",
         "How we work", "Data sources, the method behind every signal and the rules our content follows.", EDITORIAL, True),
        ("privacy/", "Privacy policy", "What information Home.Deals handles, how advertising cookies work and the choices you have.", "Privacy policy",
         "What we collect, why, and your choices.", PRIVACY, True),
        ("terms/", "Terms of use", "The terms that apply when you use Home.Deals.", "Terms of use", "The terms that apply when you use this site.", TERMS, True),
        ("disclaimer/", "Trademark, copyright and general disclaimer", "Home.Deals is an independent website and is not affiliated with any business trading under a similar name. Trademark and copyright notice.",
         "Trademark and copyright notice", "Who we are not, whose names appear here and why, and how to report a concern.", DISCLAIMER, True),
        ("disclosure/", "Advertising and affiliate disclosure", "How Home.Deals earns money: advertising, referral fees, affiliate links, sponsorship and reader support.",
         "Advertising disclosure", "How this site earns money.", DISCLOSURE, True),
        ("cookies/", "Cookie policy", "The cookies and local storage used on Home.Deals and how to control them.", "Cookie policy", "What is stored, by whom, and how to control it.", COOKIES, True),
        ("accessibility/", "Accessibility statement", "How Home.Deals approaches accessibility and how to report a problem.", "Accessibility", "Our approach and how to report a problem.", ACCESSIBILITY, True),
    ]
    for path, title, desc, h1, lede, text, ads in prose_pages:
        body = (f'<section class="sec"><div class="wrap narrow-wide"><div class="prose prose-page">{text}'
                f'<p class="stamp">Last updated {fdate(SITE["launched"])}.</p></div></div></section>')
        add(path, title, desc, body, h1=h1, lede=lede, crumbs=[(h1, None)], ads=ads, section="About")

    add("search/", "Search Home.Deals", "Search every page, guide and calculator on Home.Deals.",
        '<section class="sec"><div class="wrap narrow-wide"><form class="search-form" role="search" action="./" method="get">'
        '<label class="vh" for="search-q">Search</label><input type="search" id="search-q" name="q" placeholder="Try “mattress”, “roof cost” or “refinance”" autocomplete="off">'
        '<button class="btn btn-ink" type="submit">Search</button></form><div id="search-results" aria-live="polite"></div>'
        '<noscript><p class="note">Search needs JavaScript. Use the <a href="{{root}}sitemap/">sitemap</a> to browse every page.</p></noscript></div></section>',
        h1="Search", crumbs=[("Search", None)], ads=False, noindex=True, search=False, scripts=["search"], section="About")


def build_sitemap_page() -> None:
    groups: dict[str, list] = {}
    for p in PAGES:
        if p.get("noindex") or p["path"] in ("404.html",):
            continue
        groups.setdefault(p.get("section", "More"), []).append(p)
    html_parts = []
    for name, pages in groups.items():
        items = "".join(f'<li><a href="{{{{root}}}}{p["path"]}">{E(p.get("h1") or p["title"])}</a></li>' for p in pages)
        html_parts.append(f'<h2>{E(name)}</h2><ul class="cols">{items}</ul>')
    add("sitemap/", "Sitemap", "Every page on Home.Deals.", f'<section class="sec"><div class="wrap narrow-wide">{"".join(html_parts)}</div></section>',
        h1="Sitemap", crumbs=[("Sitemap", None)], ads=False, search=False, section="About")


def build_404() -> None:
    body = ('<section class="sec"><div class="wrap narrow-wide"><p class="sec-lede">That page is not here. It may have moved, or the link may be mistyped.</p>'
            '<p class="hero-actions"><a class="btn btn-mark" href="{{root}}">Go to the home page</a><a class="btn btn-line" href="{{root}}search/">Search the site</a></p>'
            '<ul class="links"><li><a href="{{root}}price-pulse/">This month’s buy-or-wait signals</a></li><li><a href="{{root}}calendar/">The sale calendar</a></li>'
            '<li><a href="{{root}}quotes/">Free project quotes</a></li><li><a href="{{root}}tools/">Calculators</a></li></ul></div></section>')
    add("404.html", "Page not found", "This page could not be found.", body, h1="Page not found", ads=False, noindex=True, search=False, is404=True, section="About")


# ==========================================================================
# layout
# ==========================================================================
NAV = [("deals/", "Deals"), ("calendar/", "Calendar"), ("price-pulse/", "Price Pulse"), ("rates/", "Rates"), ("tools/", "Calculators"), ("guides/", "Guides")]
MORE = [("recalls/", "Recall Radar"), ("market/", "Housing market"), ("videos/", "Videos"), ("alerts/", "Deal alerts"), ("giveaways/", "Giveaways"),
        ("support/", "Support us"), ("advertise/", "Advertise"), ("careers/", "Work with us"), ("about/", "About")]
FOOT = [
    ("Shop smarter", [("deals/", "Deal Radar"), ("calendar/", "Sale calendar"), ("price-pulse/", "Price Pulse"), ("recalls/", "Recall Radar"), ("alerts/", "Deal alerts"), ("submit/", "Submit a deal")]),
    ("Projects and money", [("quotes/", "Free project quotes"), ("rates/", "Mortgage rates"), ("market/", "Housing market meter"), ("tools/", "Calculators"), ("guides/", "Guides"), ("videos/", "Videos")]),
    ("Home.Deals", [("about/", "About"), ("editorial-policy/", "How we work"), ("advertise/", "Advertise and partner"), ("support/", "Support the site"), ("giveaways/", "Giveaways"), ("careers/", "Work with us"), ("contact/", "Contact")]),
    ("Legal", [("privacy/", "Privacy policy"), ("terms/", "Terms of use"), ("disclaimer/", "Trademark and copyright"), ("disclosure/", "Advertising disclosure"), ("cookies/", "Cookie policy"), ("accessibility/", "Accessibility"), ("sitemap/", "Sitemap")]),
]
LOGO = ('<svg class="logo-mark" viewBox="0 0 32 32" width="32" height="32" aria-hidden="true" focusable="false">'
        '<rect x="1" y="1" width="30" height="30" rx="3" fill="#17233B"/><path d="M7 17.5 16 9l9 8.5" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
        '<rect x="1" y="22" width="30" height="9" fill="#E6FB52"/><rect x="1" y="1" width="30" height="30" rx="3" fill="none" stroke="#17233B" stroke-width="2"/></svg>')


def render(p: dict, css_v: str, js_v: dict) -> str:
    path = p["path"]
    is404 = p.get("is404")
    depth = 0 if is404 else path.count("/")
    R = "../" * depth
    canonical = f'{SITE["url"]}/{path}' if not is404 else f'{SITE["url"]}/'
    title = p["title"] if path == "" else f'{p["title"]} | {SITE["name"]}'
    robots = '<meta name="robots" content="noindex, follow">' if p.get("noindex") else '<meta name="robots" content="index, follow, max-image-preview:large">'
    schemas = list(p.get("schema") or [])
    crumbs_html = ""
    if p.get("crumbs"):
        parts, items = [f'<a href="{R or "./"}">Home</a>'], [{"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["url"] + "/"}]
        for i, (name, href) in enumerate(p["crumbs"], start=2):
            if href:
                parts.append(f'<a href="{R}{href}">{E(name)}</a>')
                items.append({"@type": "ListItem", "position": i, "name": name, "item": f'{SITE["url"]}/{href}'})
            else:
                parts.append(f'<span aria-current="page">{E(name)}</span>')
                items.append({"@type": "ListItem", "position": i, "name": name, "item": canonical})
        crumbs_html = '<nav class="crumbs" aria-label="Breadcrumb">' + '<span class="crumb-sep" aria-hidden="true">/</span>'.join(parts) + "</nav>"
        schemas.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items})
    ld = "".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in schemas)
    ads = p.get("ads", True)
    adsense = (f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={SITE["adsense_client"]}" crossorigin="anonymous"></script>'
               if ads else "")
    base = ('<script>(function(){var h=location.hostname,s=location.pathname.split("/")[1]||"";'
            'document.write(\'<base href="\'+(/github\\.io$/.test(h)&&s?"/"+s+"/":"/")+\'">\');})();</script>') if is404 else ""

    def nav_link(href, label):
        cur = ' aria-current="page"' if path.startswith(href) else ""
        return f'<a href="{R}{href}"{cur}>{label}</a>'
    nav = "".join(f"<li>{nav_link(h, l)}</li>" for h, l in NAV)
    more = "".join(f"<li>{nav_link(h, l)}</li>" for h, l in MORE)
    foot = "".join(f'<div class="foot-col"><h2>{E(t)}</h2><ul>{"".join(f"<li>{nav_link(h, l)}</li>" for h, l in links)}</ul></div>' for t, links in FOOT)
    head_block = ""
    if not p.get("bare"):
        chip_html = ""
        if p.get("chip"):
            color, icon_name, code = p["chip"]
            chip_html = (f'<div class="chip chip-head" style="--chip:{color};--chip-fg:{on_color(color)}"><span class="chip-swatch">{ic(icon_name, "chip-ic")}</span>'
                         f'<span class="chip-cap"><span class="chip-code">{E(code)}</span></span></div>')
        cta = f'<p class="hero-actions"><a class="btn btn-mark" href="{p["cta"][1]}">{E(p["cta"][0])}</a></p>' if p.get("cta") else ""
        meta_line = f'<p class="meta-line">{E(p["meta_line"])}</p>' if p.get("meta_line") else ""
        lede_html = '<p class="lede">' + E(p["lede"]) + "</p>" if p.get("lede") else ""
        head_block = (f'<header class="page-head"><div class="wrap page-head-grid"><div>{crumbs_html}<h1>{E(p.get("h1") or p["title"])}</h1>'
                      f'{lede_html}{meta_line}{cta}</div>{chip_html}</div></header>')
    scripts = "".join(f'<script src="{R}assets/js/{name}.js?v={js_v[name]}" defer></script>' for name in p.get("scripts", ()))
    year = TODAY.year
    doc = f'''<!doctype html>
<html lang="en" data-root="{R or "./"}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
{base}<title>{E(title)}</title>
<meta name="description" content="{E(p["desc"])}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{"article" if path.startswith("guides/") and path != "guides/" else "website"}">
<meta property="og:site_name" content="{SITE["name"]}">
<meta property="og:title" content="{E(p["title"])}">
<meta property="og:description" content="{E(p["desc"])}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE["url"]}/assets/img/og.png">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#17233B">
<meta name="google-adsense-account" content="{SITE["adsense_client"]}">
<link rel="icon" href="{R}assets/img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{R}assets/img/icon-48.png" sizes="48x48" type="image/png">
<link rel="apple-touch-icon" href="{R}assets/img/icon-180.png">
<link rel="manifest" href="{R}manifest.webmanifest">
<link rel="alternate" type="application/rss+xml" title="{SITE["name"]} guides" href="{R}feed.xml">
<link rel="preload" href="{R}assets/fonts/archivo-var.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{R}assets/css/site.css?v={css_v}">
<script>try{{var t=localStorage.getItem("hd-theme");if(t)document.documentElement.setAttribute("data-theme",t);}}catch(e){{}}</script>
{adsense}
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<div class="strip"><a href="{CONTACT}" target="_blank" rel="noopener">{E(SITE["contact_bar"])}</a></div>
<header class="hdr"><div class="wrap hdr-in">
<a class="logo" href="{R or "./"}" aria-label="{SITE["name"]} home">{LOGO}<span class="logo-word">Home<span class="logo-dot">.</span>Deals</span></a>
<nav class="nav" aria-label="Main"><ul>{nav}
<li class="nav-more"><details><summary>More</summary><ul>{more}</ul></details></li></ul></nav>
<div class="hdr-tools">
<a class="icon-btn" href="{R}search/" aria-label="Search">{ic("search")}</a>
<button class="icon-btn" type="button" data-theme-toggle aria-label="Switch between light and dark theme">{ic("moon")}</button>
<a class="btn btn-mark btn-sm hdr-cta" href="{R}quotes/">Get free quotes</a>
<button class="icon-btn burger" type="button" aria-expanded="false" aria-controls="drawer" aria-label="Open menu">{ic("menu")}</button>
</div></div>
<div class="drawer" id="drawer" hidden><nav aria-label="Menu"><ul>{nav}{more}<li><a href="{R}quotes/">Get free quotes</a></li></ul></nav></div>
</header>
<main id="main">
{head_block}
{p["body"]}
</main>
<footer class="foot"><div class="wrap">
<div class="foot-top"><a class="logo logo-foot" href="{R or "./"}">{LOGO}<span class="logo-word">Home<span class="logo-dot">.</span>Deals</span></a>
<p>{E(SITE["tagline"])}.</p>
<p><a class="btn btn-mark btn-sm" href="{CONTACT}" target="_blank" rel="noopener">Sponsorship, advertising, partnership and domain enquiries</a></p></div>
<div class="foot-cols">{foot}</div>
<div class="foot-legal">
<p>Home.Deals is an independent website. It is not affiliated with, endorsed by or connected to any company, store or brand trading as “HomeDeals”, “Home Deals” or a similar name. All retailer, manufacturer and product names are trademarks of their respective owners and are used only to identify them. <a href="{R}disclaimer/">Trademark and copyright notice</a>.</p>
<p>This site shows advertising and may earn fees from providers and retailers. <a href="{R}disclosure/">How we are funded</a>. Content is general information, not financial, legal or professional advice. Prices, rates and offers change, so confirm them with the provider.</p>
<p>Data: U.S. Bureau of Labor Statistics, Freddie Mac via FRED, U.S. Census Bureau and HUD, FHFA, U.S. Consumer Product Safety Commission, Federal Trade Commission. <a href="{R}editorial-policy/">Sources and method</a>.</p>
<p>© {year} Home.Deals. All rights reserved.</p></div>
</div></footer>
<div class="cookie" data-cookie hidden><p>This site uses cookies for advertising and stores your preferences on your device. <a href="{R}cookies/">Cookie policy</a></p><button class="btn btn-ink btn-sm" type="button" data-cookie-ok>OK</button></div>
<script src="{R}assets/js/config.js?v={js_v["config"]}" defer></script>
<script src="{R}assets/js/site.js?v={js_v["site"]}" defer></script>
{scripts}
</body>
</html>
'''
    # bare tables inside prose get a scroll wrapper so they never widen a phone screen
    doc = re.sub(r"<table>(.*?)</table>", r'<div class="table-wrap"><table>\1</table></div>', doc, flags=re.S)
    doc = doc.replace("{{root}}", R if R else "./")
    for key, value in TOKENS.items():
        doc = doc.replace("{{" + key + "}}", value)
    return doc


# ==========================================================================
# outputs
# ==========================================================================
def write_config() -> None:
    cfg = {
        "form": {"k": SITE["form_key"], "a": SITE["form_alias"]},
        "contact": CONTACT,
        "events": [{"id": e["id"], "name": e["name"], "rule": list(e["rule"]), "lead": e["lead"], "tail": e["tail"]} for e in EVENTS],
        "months": MONTH_NAMES,
        "life": {"Refrigerator": 13, "Dishwasher": 10, "Washer": 11, "Dryer": 13, "Range or oven": 15, "Microwave": 9, "Water heater": 10,
                 "Central air conditioner": 15, "Furnace": 18, "Heat pump": 15},
    }
    (ROOT / "assets/js/config.js").write_text("window.HD = " + json.dumps(cfg, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")


def main() -> None:
    build_home()
    build_deals()
    build_calendar()
    build_pulse()
    build_quotes()
    build_rates()
    build_market()
    build_tools()
    build_recalls()
    build_videos()
    build_guides()
    build_community()
    build_standing()
    build_sitemap_page()
    build_404()

    write_config()
    css_v = asset_v("assets/css/site.css")
    js_v = {name: asset_v(f"assets/js/{name}.js") for name in ("config", "site", "wizard", "tools", "search")}

    manifest_path = ROOT / "data" / "_pages.json"
    try:
        old = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001
        old = {}
    manifest, index = {}, []
    for p in PAGES:
        doc = render(p, css_v, js_v)
        out = ROOT / (p["path"] if p["path"].endswith(".html") else p["path"] + "index.html")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(doc, encoding="utf-8")
        digest = hashlib.sha1(doc.encode("utf-8")).hexdigest()[:12]
        prev = old.get(p["path"])
        manifest[p["path"]] = [digest, prev[1] if prev and prev[0] == digest else TODAY.isoformat()]
        if p.get("search", True) and not p.get("noindex"):
            text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", p["body"], flags=re.S)
            text = re.sub(r"<[^>]+>", " ", text)
            text = re.sub(r"\{\{[a-z0-9_]+\}\}", " ", text)
            words = re.sub(r"\s+", " ", text).strip()[:900]
            index.append({"t": p.get("h1") or p["title"], "d": p["desc"], "u": p["path"], "s": p.get("section", ""), "x": words})
    manifest_path.write_text(json.dumps(manifest, indent=0, sort_keys=True) + "\n", encoding="utf-8")
    (ROOT / "search-index.json").write_text(json.dumps(index, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")

    urls = []
    for p in PAGES:
        if p.get("noindex") or p["path"].endswith(".html"):
            continue
        prio = "1.0" if p["path"] == "" else "0.8" if p["path"].count("/") == 1 else "0.6"
        urls.append(f'<url><loc>{SITE["url"]}/{p["path"]}</loc><lastmod>{manifest[p["path"]][1]}</lastmod><priority>{prio}</priority></url>')
    (ROOT / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                      + "\n".join(urls) + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text("User-agent: *\nAllow: /\nDisallow: /search/\nDisallow: /scripts/\nDisallow: /content/\n"
                                     f'Disallow: /docs/\nDisallow: /data/\n\nSitemap: {SITE["url"]}/sitemap.xml\n', encoding="utf-8")
    (ROOT / "ads.txt").write_text(f'google.com, {SITE["adsense_pub"]}, DIRECT, f08c47fec0942fa0\n', encoding="utf-8")
    items = "".join(
        f'<item><title>{E(g["title"])}</title><link>{SITE["url"]}/guides/{g["slug"]}/</link><guid>{SITE["url"]}/guides/{g["slug"]}/</guid>'
        f'<pubDate>{dt.datetime.fromisoformat(g["date"]).strftime("%a, %d %b %Y 12:00:00 +0000")}</pubDate><description>{E(g["desc"])}</description></item>'
        for g in GUIDES)
    (ROOT / "feed.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel>'
                                   f'<title>{SITE["name"]} guides</title><link>{SITE["url"]}/guides/</link>'
                                   f'<description>{E(SITE["description"])}</description><language>en-us</language>{items}</channel></rss>\n', encoding="utf-8")
    (ROOT / "manifest.webmanifest").write_text(json.dumps({
        "name": SITE["name"], "short_name": SITE["name"], "description": SITE["tagline"], "start_url": "./", "scope": "./", "display": "standalone",
        "background_color": "#F2F3EF", "theme_color": "#17233B",
        "icons": [{"src": "assets/img/icon-192.png", "sizes": "192x192", "type": "image/png"},
                  {"src": "assets/img/icon-512.png", "sizes": "512x512", "type": "image/png"}]}, indent=1) + "\n", encoding="utf-8")
    print(f"built {len(PAGES)} pages for {TODAY.isoformat()}")


if __name__ == "__main__":
    main()
