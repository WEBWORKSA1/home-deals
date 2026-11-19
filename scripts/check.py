#!/usr/bin/env python3
"""Home.Deals pre-publish checks. Exits non-zero if the built site breaks a rule.

    python3 scripts/check.py

Checks: internal links and anchors resolve, every page carries the contact
bar, no email address or contact domain appears in visible text, the AdSense
tag is on content pages and off utility pages, and basic SEO tags exist.
"""
from __future__ import annotations

import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from content.catalog import SITE  # noqa: E402

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
EMAIL_OK = ("example.com", "users.noreply.github.com")
NO_ADS = {"404.html", "search/index.html", "sitemap/index.html"}
SKIP_DIRS = {".git", "node_modules", "__pycache__"}
CONTACT_HOST = re.sub(r"^https?://", "", SITE["contact_url"]).split("/")[0]


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links, self.ids, self.h1, self.text, self.imgs_no_alt = [], [], 0, [], 0
        self.title, self.desc, self.canonical, self.adsense = "", "", "", False
        self._skip, self._in_title, self.strip_ok = 0, False, False
        self._in_strip, self._strip_href, self._strip_text = False, "", []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag in ("script", "style", "noscript"):
            self._skip += 1
        if tag == "script" and "adsbygoogle.js" in (a.get("src") or ""):
            self.adsense = SITE["adsense_client"] in a["src"]
        if a.get("id"):
            self.ids.append(a["id"])
        if tag == "h1":
            self.h1 += 1
        if tag == "title":
            self._in_title = True
        if tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content") or ""
        if tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href") or ""
        if tag == "img" and a.get("alt") is None:
            self.imgs_no_alt += 1
        for key in ("href", "src", "action"):
            if a.get(key):
                self.links.append(a[key])
        if tag == "div" and a.get("class") == "strip":
            self._in_strip = True
        if tag == "a" and self._in_strip:
            self._strip_href = a.get("href") or ""

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript"):
            self._skip -= 1
        if tag == "title":
            self._in_title = False
        if tag == "div" and self._in_strip:
            self._in_strip = False
            self.strip_ok = self._strip_href == SITE["contact_url"] and "".join(self._strip_text).strip() == SITE["contact_bar"]

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_strip:
            self._strip_text.append(data)
        if not self._skip:
            self.text.append(data)


def main() -> int:
    errors, warnings = [], []
    pages = sorted(p for p in ROOT.rglob("*.html") if not (set(p.relative_to(ROOT).parts) & SKIP_DIRS))
    parsed = {}
    for path in pages:
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        parsed[path] = page
    for path, page in parsed.items():
        rel = path.relative_to(ROOT).as_posix()
        if not page.strip_ok:
            errors.append(f"{rel}: contact bar missing or altered")
        if page.h1 != 1:
            errors.append(f"{rel}: expected one h1, found {page.h1}")
        if not page.title.strip() or not page.desc.strip() or not page.canonical:
            errors.append(f"{rel}: missing title, description or canonical")
        if len(page.desc) > 170:
            warnings.append(f"{rel}: description is {len(page.desc)} characters")
        if len(set(page.ids)) != len(page.ids):
            dupes = sorted({i for i in page.ids if page.ids.count(i) > 1})
            errors.append(f"{rel}: duplicate ids {dupes}")
        if page.imgs_no_alt:
            errors.append(f"{rel}: {page.imgs_no_alt} image(s) without alt")
        if rel in NO_ADS and page.adsense:
            errors.append(f"{rel}: utility page must not load ads")
        if rel not in NO_ADS and not page.adsense:
            errors.append(f"{rel}: AdSense tag missing")
        visible = " ".join(page.text)
        if CONTACT_HOST.lower() in visible.lower():
            errors.append(f"{rel}: contact domain appears in visible text")
        if rel == "404.html":
            continue  # links resolve against a runtime <base>
        for link in page.links:
            if re.match(r"^(https?:|mailto:|tel:|data:|#$)", link) or link.startswith("//"):
                continue
            target, _, frag = link.partition("#")
            target = target.split("?")[0]
            dest = path if not target else (path.parent / target).resolve()
            if dest.is_dir():
                dest = dest / "index.html"
            if not dest.exists():
                errors.append(f"{rel}: broken link {link}")
                continue
            if frag and dest.suffix == ".html":
                other = parsed.get(dest)
                if other and frag not in other.ids:
                    errors.append(f"{rel}: missing anchor #{frag} in {dest.relative_to(ROOT).as_posix()}")
    # no email address anywhere in the published tree
    for path in ROOT.rglob("*"):
        if not path.is_file() or (set(path.relative_to(ROOT).parts) & SKIP_DIRS):
            continue
        if path.suffix.lower() in (".png", ".woff2", ".ico", ".jpg", ".webp"):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for found in EMAIL.findall(text):
            if not found.lower().endswith(EMAIL_OK):
                errors.append(f"{path.relative_to(ROOT).as_posix()}: email address in file ({found[:3]}…)")
    ads = (ROOT / "ads.txt").read_text().strip() if (ROOT / "ads.txt").exists() else ""
    if ads != f'google.com, {SITE["adsense_pub"]}, DIRECT, f08c47fec0942fa0':
        errors.append("ads.txt is missing or wrong")
    for w in warnings:
        print("warn:", w)
    for e in errors:
        print("ERROR:", e)
    print(f"checked {len(pages)} pages: {len(errors)} error(s), {len(warnings)} warning(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
