# Home.Deals — phase-wise build prompt

Use this prompt, one phase at a time, to rebuild or extend the site. Each phase names its inputs, the work, and the checks that must pass before the next phase starts. The site in this repository is the result of running it once.

---

## Standing rules (apply to every phase)

1. **Domain and identity.** The site is Home.Deals, read as "home deals". It is an independent site. Do not imitate or reference the look, logo or content of any business trading as "HomeDeals" or "Home Deals". Carry a trademark and copyright notice in the footer of every page and on a dedicated page.
2. **Contact bar.** The top of every page shows this exact text as a link: "Contact, if you are interested in this website/domain name/Sponsorship/Advertisement/Partnership". It links to the owner's contact page. The contact address appears only inside the link, never as visible text.
3. **One inbox, never shown.** Every form delivers to the single owner inbox. The address must not appear in any page, script, data file or document in the repository. Store it encoded, deliver through a form service, and switch to the service's random alias once the owner activates it.
4. **Google AdSense.** Publisher id `ca-pub-6620975821265271`. Put the loader in the head of every content page, publish `ads.txt`, and keep ads off pages without content (404, search, sitemap). Never ask readers to click ads. Never place ad units next to buttons or navigation.
5. **Honesty.** No invented deals, prices, reviews, testimonials, counters or partner logos. Every number shows its source and date. Estimates are labelled as estimates.
6. **Hosting.** Plain static files served by GitHub Pages on the free plan from the `main` branch, root folder. No build step on the host. All internal links are relative so the site works on a project URL and on the custom domain.
7. **Automation.** A scheduled GitHub Actions workflow refreshes data and rebuilds pages. A failed source never removes good data.
8. **Language.** Plain, direct, sentence case. Buttons say what happens. Errors say what went wrong and what to do.

---

## Phase 1 — Research

**Goal.** Know what the best sites in the niche actually do before deciding anything.

**Work.**
- Open and read at least 38 sites directly, across five groups: deal aggregators and coupon sites, retailer sale pages, home media with deal desks, home-service lead generation and cost guides, home money and public data.
- For each, record: purpose, navigation, notable features, forms and lead capture, how it earns money, trust and design elements.
- Check existing uses of the name and record what was found.
- Verify any fact that content will depend on (tax rules, current rates, program status).

**Output.** `docs/RESEARCH.md` with one row per site, the patterns across them, and the facts verified.

**Checks.** At least 38 sites were genuinely opened. Sites that failed to load are listed separately and not counted.

---

## Phase 2 — Concept and structure

**Goal.** Choose the concept with the best mix of usefulness, revenue and automation, and fix the page map.

**Work.**
- Compare options (deal feed, coupon site, property listings, timing engine plus quote desk) on what each needs and what each earns.
- Choose and justify, with numbers and with assumptions labelled.
- Define the sections: Deals (hub and one page per category), Calendar, Price Pulse, Quotes (hub and one page per service), Rates, Housing market, Calculators, Recall Radar, Videos, Guides, Giveaways, Support, Advertise, Work with us, Deal alerts, Submit a deal, Contact, About, method, and legal pages.

**Output.** `docs/CONCEPT.md` and the page map.

**Checks.** Every requirement in the brief maps to a page: AdSense, video, lead generation, donations, contests, hiring, contact bar, trademark notice.

---

## Phase 3 — Design system

**Goal.** A distinct identity that could not be mistaken for another deal site.

**Work.**
- Ground the design in the subject. The chosen idea is a paint-chip deck: each home category is a colour chip with a caption strip, and a single highlighter colour marks the action.
- One typeface used across its width axis: condensed for display, normal for reading. Self-host it.
- Tokens for colour, type and spacing as CSS custom properties, with a dark theme.
- Components: contact strip, header and drawer, chips, signal badges, hairline rows, tables, panels, forms and option tiles, wizard steps, filters, charts, meter, video cards, FAQ, bands, footer.
- One motion moment only (the chip deck on load), and none when reduced motion is requested.

**Output.** `assets/css/site.css`, `assets/fonts/`, `assets/img/` (logo, icons, social image).

**Checks.** Responsive from 360 px. Visible keyboard focus. Text contrast at AA in both themes. No horizontal scroll on mobile.

---

## Phase 4 — Data pipeline

**Goal.** Fresh, lawful data with no API keys.

**Work.** Write `scripts/update_data.py` using only the standard library:

| File | Source |
|------|--------|
| `data/pulse.json` | BLS public API, Consumer Price Index item series, with a FRED fallback |
| `data/rates.json` | Freddie Mac weekly averages from FRED, with Freddie Mac's own file as fallback |
| `data/market.json` | Census and HUD new-home series and the FHFA index from FRED |
| `data/energy.json` | BLS average electricity and gas prices |
| `data/recalls.json` | CPSC recall API, filtered to home products by keyword rules |
| `data/alerts.json` | FTC consumer feeds, filtered to homes, pricing and shopping |
| `data/videos.json` | Public YouTube channel feeds, resolved from channel handles |
| `data/_status.json` | Per-source result of the last run |

Rules: keep the previous file when a source fails, strip any email address from third-party text, write no timestamps into data files so unchanged data makes no diff.

**Checks.** Unit-test each parser with sample payloads. Run the workflow once and read `_status.json`: every source should report ok.

---

## Phase 5 — Generator

**Goal.** One command builds every page.

**Work.**
- `content/` holds editorial data as plain Python: site settings, categories, calendar, events, deal sources, services, guides, calculators, legal text.
- `scripts/build.py` renders every page with a shared layout, relative links, canonical tags, Open Graph tags and JSON-LD (WebSite, Organization, BreadcrumbList, FAQPage, Article).
- It also writes `sitemap.xml` with real last-modified dates, `robots.txt`, `ads.txt`, `feed.xml`, `manifest.webmanifest`, `search-index.json` and `assets/js/config.js`.
- Signals: buy window if the month is one of the category's strongest, wait if a stronger month is within two months, otherwise fair. Show the price index trend beside it.
- Sale events are computed from rules (for example the third Monday of February), never typed in.
- Charts are inline SVG rendered at build time.

**Checks.** The build is deterministic: the same inputs give byte-identical pages.

---

## Phase 6 — Lead generation and forms

**Goal.** A quote flow people finish, and forms that reach the inbox.

**Work.**
- A four-step wizard: project, two project questions, home and timing, contact. Show progress. Show an instant ballpark range before asking for contact details. Phone number optional.
- Entry points: home page mini-form (project and ZIP), header button, twelve service pages that open the wizard with the service chosen.
- Consent text at the submit step that says who may contact the person and how. State that the site is an introduction service, not a contractor, and may be paid by providers.
- Other forms: deal alerts, submit a deal, giveaway entry or notification, support pledge, work-with-us application, contact.
- Inline validation with specific messages, a honeypot field, a clear success state, and a failure message that offers the contact page.

**Checks.** Browser test the whole wizard, a plain form, validation and the failure path with the form service mocked. Confirm the payload fields.

---

## Phase 7 — Content

**Goal.** Enough original, useful content to deserve traffic and pass an AdSense review.

**Work.**
- Twelve category pages: how pricing works, when prices drop, what a good deal looks like, what to watch for, where to look, FAQ.
- Twelve service pages: cost table, what moves the price, how to compare quotes, questions to ask, FAQ.
- A twelve-month calendar with buy and hold lists that agree with the category signals.
- At least twelve guides of 400 to 700 words.
- Eight calculators, each with an explanation of its method.
- About, method, privacy, terms, trademark and copyright, advertising disclosure, cookies, accessibility.

**Checks.** Calendar and signals never contradict each other. Every cost is a range with a source note. Tax and program statements match current law.

---

## Phase 8 — Monetisation and compliance

**Work.**
- AdSense loader and `ads.txt`. Optional manual ad units appear only when slot ids are set in `content/catalog.py`.
- Advertising disclosure, privacy policy with Google's advertising cookie wording and opt-out links, cookie notice.
- Giveaways: standing rules (no purchase necessary, eligibility, random draw, no ad interaction). A round opens only when a real prize, value and dates are set.
- Support: payment buttons when links are set, otherwise a pledge form. State that contributions are not tax-deductible.
- Advertise page with sponsorship formats, all routed to the contact page.

---

## Phase 9 — Quality checks

**Work.** `scripts/check.py` must pass: internal links and anchors resolve, the contact bar is on every page with the exact text and link, no email address anywhere in the published tree, the contact domain never appears as visible text, AdSense on content pages and not on utility pages, one `h1`, title, description and canonical on every page, no duplicate ids, images have alt text. Then test in a browser at desktop and mobile widths in both themes.

---

## Phase 10 — Publish

1. Commit and push to `main` on GitHub.
2. Add `.github/workflows/refresh.yml`: on a schedule four times a day, on manual run and on pushes to scripts or content. It runs the data refresh, the build and the checks, then commits only if content changed.
3. In the repository settings, set Pages to deploy from branch `main`, folder `/ (root)`.
4. Point the domain: four A records for the apex to GitHub Pages, a CNAME for `www`, then set the custom domain in Pages settings and enforce HTTPS.
5. Send one test form and click the activation link the form service emails to the inbox. Paste the alias it returns into `form_alias`.
6. Add the site in AdSense, confirm `ads.txt`, switch on Google's consent message for regions that require it, and request review once the site is live on the domain.
7. Submit `sitemap.xml` in Google Search Console.

---

## Phase 11 — Growth

- Sign quote partners or connect a lead network for roofing, solar, HVAC and windows first.
- Add affiliate programs per retailer and label the links.
- Add regional pages (state rebates, sales-tax holidays) and more services.
- Move alerts to an email provider with double opt-in.
- Set payment links on the Support page and open the first giveaway round.
- Add structured product feeds once affiliate accounts exist, feeding a real deals list.
