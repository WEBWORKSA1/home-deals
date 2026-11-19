# Home.Deals

Know when to buy anything for your home. A static, self-updating site: buy-or-wait signals for twelve home categories, a sale calendar, calculators, mortgage and housing data, recall alerts, videos, guides and a quote-request section for home projects.

No framework, no build service, no API keys. Python standard library for the generator, plain HTML, CSS and JavaScript for the site.

## How it works

```
content/            editorial source (plain Python data)
  catalog.py        site settings, categories, calendar, sale events, deal sources
  services.py       twelve home services: costs, checklists, wizard questions
  guides.py         guides
  pages.py          calculators, about, method, legal text
scripts/
  update_data.py    pulls public data into /data (no keys)
  build.py          renders every page, sitemap, feed, search index
  check.py          pre-publish checks
  hd_core.py        shared: dates, signals, charts
data/               refreshed data, plus _status.json from the last run
assets/             css, js, fonts, images
.github/workflows/refresh.yml   scheduled refresh, rebuild and commit
docs/               research log, concept, phase-wise build prompt
```

Everything else in the repository root is generated output and is what GitHub Pages serves.

## Build locally

```
python3 scripts/update_data.py   # optional: refresh data
python3 scripts/build.py         # render the site
python3 scripts/check.py         # must report 0 errors
python3 -m http.server 8000      # preview at http://localhost:8000
```

## Automation

`.github/workflows/refresh.yml` runs four times a day, on manual run and whenever `scripts/` or `content/` change. It refreshes data, rebuilds, runs the checks and commits only when content changed. If a source is down, the last good data stays in place and the failure is written to `data/_status.json`.

| Data | Source |
|------|--------|
| Price indexes | U.S. Bureau of Labor Statistics public API |
| Mortgage rates | Freddie Mac weekly survey via FRED |
| Housing series | Census Bureau, HUD and FHFA via FRED |
| Recalls | U.S. Consumer Product Safety Commission |
| Consumer alerts | Federal Trade Commission |
| Videos | Public YouTube channel feeds |

GitHub pauses scheduled workflows after 60 days without repository activity. The refresh commits count as activity while data keeps changing. If the schedule is ever paused, re-enable it from the Actions tab.

## Publishing

1. Repository settings, Pages: deploy from branch `main`, folder `/ (root)`.
2. Custom domain: point four A records for the apex to GitHub Pages (185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153) and a CNAME for `www` to `<account>.github.io`, then enter the domain in Pages settings and enforce HTTPS.

All internal links are relative, so the site works on the project URL and on the custom domain.

## Settings you can change

All in `content/catalog.py`, under `SITE`:

| Setting | What it does |
|---------|--------------|
| `ad_slots` | Empty by default, which relies on AdSense Auto ads. Add slot ids to place manual units (`home`, `category`, `article`, `service`, `tool` and others). |
| `form_alias` | Paste the random alias the form service emails after activation. Forms then stop using the encoded inbox value. |
| `donate` | Payment links for the Support page. With none set, the page shows a pledge form. |
| `giveaway` | Set `active`, a real `prize`, `prize_value`, `start` and `end` to open a round. Until then no prize is promised. |
| `contact_url` | Where the contact bar and all commercial enquiries go. |

After any change, run the build and the checks, then commit.

## Forms

Forms post as JSON to a form service and arrive in the owner inbox. The inbox address is never written in the repository. It is stored encoded in `SITE["form_key"]`. The first submission triggers a one-time activation email to the inbox. Until that link is clicked, submissions are not delivered and the site tells the sender to use the contact page.

## Rules the checks enforce

- The contact bar is on every page with the exact text and link.
- No email address appears anywhere in the published tree.
- The contact domain never appears as visible text.
- AdSense loads on content pages and not on the 404, search or sitemap pages.
- Every internal link and anchor resolves.

## Licences

Site code and content © Home.Deals. The Archivo typeface is used under the SIL Open Font License (see `assets/fonts/OFL-Archivo.txt`). Data comes from the public sources listed above and is credited on each page.
