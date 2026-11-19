"""Home.Deals — calculators, standing pages and legal text.

Tokens: {{root}} = relative path to the site root, {{contact}} = contact URL.
"""

# ---------------------------------------------------------------------------
# Calculators. Field tuple: (id, label, kind, default, help)
#   kind: money | pct | num | int | select:<a|b|c> | text
# The arithmetic lives in assets/js/tools.js under the same slug.
# ---------------------------------------------------------------------------
TOOLS = [
    {
        "slug": "deal-score", "name": "Deal Score checker", "icon": "tag",
        "desc": "Find the real discount after coupons, cashback, delivery and tax, measured against what the item usually sells for.",
        "action": "Check this deal",
        "groups": [
            ("The offer", [("sale", "Sale price", "money", "799", "The price on the page today"),
                           ("usual", "Usual selling price", "money", "999", "What it has actually sold for recently, not the crossed-out price"),
                           ("list", "“Was” price shown", "money", "1299", "Optional. The reference price the store displays")]),
            ("Savings you can stack", [("coupon_pct", "Coupon", "pct", "10", "Percent off the sale price"),
                                       ("coupon_amt", "Coupon, dollars off", "money", "0", ""),
                                       ("rebate", "Rebate", "money", "0", "Mail-in, instant or utility rebate"),
                                       ("cashback_pct", "Cashback", "pct", "2", "Portal or card offer")]),
            ("Costs at checkout", [("shipping", "Delivery and fees", "money", "49", ""),
                                   ("tax_pct", "Sales tax", "pct", "7", "")]),
        ],
        "how": ["Coupons come off the sale price first, percentage before dollars.",
                "Cashback is calculated on what you are charged before tax.",
                "The real discount compares your cost before tax, including delivery and after rebates and cashback, with the usual selling price.",
                "If you enter the “was” price, the checker shows how much of the advertised discount is real."],
        "faqs": [("What counts as the usual selling price?", "The price the item has sold for over most of the last two or three months. If you cannot find a history, use the lowest regular price at two other stores."),
                 ("Why is the real discount smaller than the advertised one?", "Because the advertised figure is measured from a reference price the store chose. Many items rarely sell at that price."),
                 ("Is tax included in the discount?", "No. Tax is shown in the amount you pay today and left out of the discount, because you would pay it on the usual price too.")],
    },
    {
        "slug": "unit-price", "name": "Unit price comparison", "icon": "calc",
        "desc": "Compare up to three sizes or bundles by cost per unit, square foot, sheet or load.",
        "action": "Compare unit prices",
        "groups": [
            ("Option A", [("a_price", "Price", "money", "24.99", ""), ("a_qty", "Quantity", "num", "12", "Rolls, ounces, square feet, loads")]),
            ("Option B", [("b_price", "Price", "money", "38.99", ""), ("b_qty", "Quantity", "num", "20", "")]),
            ("Option C (optional)", [("c_price", "Price", "money", "", ""), ("c_qty", "Quantity", "num", "", "")]),
        ],
        "how": ["Each price is divided by its quantity to give a cost per unit.",
                "The lowest unit price wins, and the others show how much more they cost.",
                "Use the same unit for every option: all in ounces, all in square feet or all in pieces."],
        "faqs": [("Is the bigger pack always cheaper?", "No. Promotions on mid-size packs often beat bulk sizes, which is why the unit price is worth a few seconds."),
                 ("How do I compare cookware or tool sets?", "Count only the pieces you would buy on their own. Lids, utensils and bits inflate the piece count.")],
    },
    {
        "slug": "mortgage", "name": "Mortgage payment calculator", "icon": "home",
        "desc": "Monthly payment with principal, interest, property tax, insurance and HOA, plus what a rate change does to it.",
        "action": "Calculate payment",
        "groups": [
            ("The loan", [("price", "Home price", "money", "420000", ""), ("down", "Down payment", "money", "84000", ""),
                          ("rate", "Interest rate", "pct", "{{rate30}}", "Defaults to the latest national 30-year average"),
                          ("term", "Loan term", "select:30 years|20 years|15 years|10 years", "30 years", "")]),
            ("Monthly extras", [("tax", "Property tax per year", "money", "4800", ""), ("ins", "Home insurance per year", "money", "2600", ""),
                                ("hoa", "HOA per month", "money", "0", ""), ("pmi_pct", "Mortgage insurance per year", "pct", "0", "Percent of the loan, if your down payment is under 20%")]),
        ],
        "how": ["Principal and interest use the standard amortisation formula with monthly compounding.",
                "Property tax, insurance and mortgage insurance are divided into twelve monthly amounts.",
                "The sensitivity table reprices the same loan half a point and one point either side of your rate."],
        "faqs": [("What rate should I enter?", "The calculator starts with the latest national average for a 30-year fixed loan. Your own rate depends on credit, down payment, points and lender."),
                 ("Is this the full cost of owning?", "No. Add maintenance, utilities and repairs. A common allowance is 1% to 4% of the home’s value each year.")],
    },
    {
        "slug": "refinance", "name": "Refinance break-even calculator", "icon": "percent",
        "desc": "How many months until a refinance pays for its closing costs, and the total interest on both loans.",
        "action": "Find the break-even",
        "groups": [
            ("Your current loan", [("bal", "Remaining balance", "money", "320000", ""), ("cur_rate", "Current rate", "pct", "7.5", ""),
                                   ("years_left", "Years left", "num", "27", "")]),
            ("The new loan", [("new_rate", "New rate", "pct", "{{rate30}}", "Defaults to the latest national 30-year average"),
                              ("new_term", "New term", "select:30 years|20 years|15 years|10 years", "30 years", ""),
                              ("costs", "Closing costs", "money", "6500", "Lender fees, title, appraisal and points")]),
        ],
        "how": ["Both payments are principal and interest only, so tax and insurance cancel out.",
                "Break-even months are closing costs divided by the monthly saving.",
                "Total interest is compared over the full life of each loan, which shows the effect of restarting the term."],
        "faqs": [("What is a good break-even?", "Shorter than the time you expect to keep the loan. Under three years is comfortable for most owners."),
                 ("Why can a lower payment cost more overall?", "Because a new 30-year loan spreads the balance over more years. Compare total interest, or choose a term close to the years you have left.")],
    },
    {
        "slug": "energy-cost", "name": "Energy cost calculator", "icon": "thermo",
        "desc": "What an appliance costs to run, and how long an efficient model takes to repay its higher price.",
        "action": "Calculate running cost",
        "groups": [
            ("Electricity", [("rate", "Price per kWh", "money", "{{kwh}}", "Defaults to the latest U.S. average. Your bill shows your own rate")]),
            ("One device", [("watts", "Power draw in watts", "num", "1500", "On the label or in the manual"), ("hours", "Hours used per day", "num", "4", "")]),
            ("Compare two models", [("a_kwh", "Model A, kWh per year", "num", "630", "From the yellow EnergyGuide label"), ("a_price", "Model A price", "money", "899", ""),
                                    ("b_kwh", "Model B, kWh per year", "num", "420", ""), ("b_price", "Model B price", "money", "1099", ""),
                                    ("years", "Years you expect to keep it", "num", "12", "")]),
        ],
        "how": ["Running cost is watts × hours ÷ 1,000 × your price per kWh.",
                "For the comparison, each model’s yearly kWh is multiplied by your rate and by the years you keep it.",
                "Payback is the price difference divided by the yearly saving."],
        "faqs": [("Where do I find kWh per year?", "On the yellow EnergyGuide label for most major appliances, or on the ENERGY STAR product listing."),
                 ("Does this include gas?", "No. It covers electricity. For gas appliances, use the therms per year on the label and your gas rate in place of kWh.")],
    },
    {
        "slug": "repair-or-replace", "name": "Repair or replace calculator", "icon": "hammer",
        "desc": "Apply the 50% rule and expected lifespan to a repair quote, with energy savings included.",
        "action": "Get a verdict",
        "groups": [
            ("The appliance", [("type", "Type", "select:Refrigerator|Dishwasher|Washer|Dryer|Range or oven|Microwave|Water heater|Central air conditioner|Furnace|Heat pump|Other", "Refrigerator", ""),
                               ("age", "Age in years", "num", "9", ""), ("life", "Expected life in years", "num", "13", "Fills in when you choose a type")]),
            ("The numbers", [("repair", "Repair quote", "money", "450", ""), ("replace", "Cost of a comparable new one, installed", "money", "1400", ""),
                             ("saving", "Yearly energy saving with a new one", "money", "40", "Optional")]),
        ],
        "how": ["If the repair costs half or more of a replacement, replacing usually wins.",
                "Otherwise the calculator adds the share of life already used to the repair’s share of replacement cost. A total above 1 leans towards replacing.",
                "Energy savings shorten the time a replacement takes to pay for itself."],
        "faqs": [("What is the 50% rule?", "A rule of thumb: do not spend more than half the price of a new appliance repairing an old one, particularly past the middle of its expected life."),
                 ("Where do the lifespans come from?", "They are typical service lives used across the industry. Use your own figure if the maker or your technician gives one.")],
    },
    {
        "slug": "paint", "name": "Paint calculator", "icon": "roller",
        "desc": "Gallons and cost for a room, allowing for doors, windows, coats and the ceiling.",
        "action": "Calculate paint",
        "groups": [
            ("The room", [("len", "Length in feet", "num", "14", ""), ("wid", "Width in feet", "num", "12", ""), ("hei", "Ceiling height in feet", "num", "8", ""),
                          ("doors", "Doors", "int", "1", ""), ("windows", "Windows", "int", "2", "")]),
            ("The paint", [("coats", "Coats", "int", "2", ""), ("coverage", "Coverage per gallon, sq ft", "num", "375", "On the can, usually 350 to 400"),
                           ("ceiling", "Paint the ceiling", "select:No|Yes", "No", ""), ("price", "Price per gallon", "money", "42", "")]),
        ],
        "how": ["Wall area is the room’s perimeter multiplied by its height.",
                "Each door removes about 21 square feet and each window about 15.",
                "Area × coats ÷ coverage gives gallons, rounded up to the next quart."],
        "faqs": [("Do I need primer?", "For new drywall, patched areas, stains or a strong colour change, yes. Count primer as a separate coat."),
                 ("When is paint cheapest?", "Around Memorial Day, the Fourth of July and Labor Day, when manufacturers run rebates.")],
    },
    {
        "slug": "flooring", "name": "Flooring calculator", "icon": "planks",
        "desc": "Square footage with waste, boxes to order and the installed cost.",
        "action": "Calculate flooring",
        "groups": [
            ("The room", [("len", "Length in feet", "num", "18", ""), ("wid", "Width in feet", "num", "14", ""),
                          ("waste", "Waste allowance", "select:10% straight layout|15% diagonal or herringbone|5% large simple room", "10% straight layout", "")]),
            ("The product", [("box", "Square feet per box", "num", "23.6", "Optional"), ("mat", "Material price per sq ft", "money", "3.49", ""),
                             ("lab", "Installation price per sq ft", "money", "2.50", "Optional")]),
        ],
        "how": ["Area is length multiplied by width. Add rooms together for one order.",
                "The waste allowance covers cuts, defects and a few spare planks for repairs.",
                "Boxes are rounded up, because flooring is sold by the full box."],
        "faqs": [("How much waste should I allow?", "Ten percent for a straight layout, fifteen for diagonal or herringbone, and five only for a large, simple room."),
                 ("Should I keep leftover flooring?", "Yes. Keep one unopened box. Matching a discontinued product later is difficult.")],
    },
]

# ---------------------------------------------------------------------------
ABOUT = """
<p>Home.Deals is an independent site about one question: when is the right time to buy something for your home, and what should it cost?</p>
<p>Most deal sites list offers. This one starts further back. It tracks the things that move home prices over a year, such as model changeovers, seasonal clearance and holiday events, and puts them next to public price data so you can see whether a category is getting cheaper or dearer before you shop.</p>
<h2>What you will find here</h2>
<ul>
<li><a href="{{root}}price-pulse/">Price Pulse</a>, a buy-or-wait signal for each home category, built from U.S. Consumer Price Index data and the sale calendar.</li>
<li><a href="{{root}}calendar/">The sale calendar</a>, month by month, with countdowns to the next events.</li>
<li><a href="{{root}}deals/">Deal Radar</a>, a guide to where real discounts are published, by category.</li>
<li><a href="{{root}}quotes/">Free quote requests</a> for twelve kinds of home project, with an instant ballpark price.</li>
<li><a href="{{root}}rates/">Mortgage rates</a> and a <a href="{{root}}market/">housing market meter</a>, updated from public sources.</li>
<li><a href="{{root}}tools/">Calculators</a> for deals, energy, repairs, paint, flooring and loans.</li>
<li><a href="{{root}}recalls/">Recall Radar</a>, recent home product recalls from the U.S. Consumer Product Safety Commission.</li>
</ul>
<h2>How the site stays current</h2>
<p>Data pages refresh automatically several times a day from public sources. Each one shows the date of the figures it uses and where they come from. The method is described in full on the <a href="{{root}}editorial-policy/">how we work</a> page.</p>
<h2>How the site is funded</h2>
<p>Home.Deals carries advertising, may earn referral fees when a reader hires a provider we introduce, and accepts voluntary support from readers. None of these change what the data says or which month we tell you to wait for. Details are in the <a href="{{root}}disclosure/">advertising disclosure</a>.</p>
<h2>Independence</h2>
<p>Home.Deals is not a retailer and sells nothing itself. It is not affiliated with any store or brand named on the site, or with any business that trades under a similar name. See the <a href="{{root}}disclaimer/">trademark and copyright notice</a>.</p>
<h2>Get in touch</h2>
<p>For corrections, partnerships, sponsorship, advertising or enquiries about this website and its domain name, use the <a href="{{contact}}" target="_blank" rel="noopener">contact page</a>.</p>
"""

EDITORIAL = """
<p>This page explains where the numbers on Home.Deals come from, how the signals are calculated and what rules the editorial content follows.</p>
<h2>Data sources</h2>
<table>
<thead><tr><th>What you see</th><th>Source</th><th>Refreshed</th></tr></thead>
<tbody>
<tr><td>Price Pulse</td><td>U.S. Bureau of Labor Statistics, Consumer Price Index for All Urban Consumers, item indexes, not seasonally adjusted</td><td>Monthly, as published</td></tr>
<tr><td>Mortgage rates</td><td>Freddie Mac Primary Mortgage Market Survey weekly averages, retrieved from FRED, Federal Reserve Bank of St. Louis</td><td>Weekly</td></tr>
<tr><td>Housing market meter</td><td>U.S. Census Bureau and HUD new residential sales, and the FHFA house price index, retrieved from FRED</td><td>Monthly and quarterly</td></tr>
<tr><td>Electricity and gas prices</td><td>U.S. Bureau of Labor Statistics average price data</td><td>Monthly</td></tr>
<tr><td>Recall Radar</td><td>U.S. Consumer Product Safety Commission recall database</td><td>Several times a day</td></tr>
<tr><td>Consumer alerts</td><td>U.S. Federal Trade Commission</td><td>Several times a day</td></tr>
<tr><td>Videos</td><td>Public YouTube channel feeds, played in the official YouTube player</td><td>Several times a day</td></tr>
</tbody>
</table>
<p>An automated job collects these figures four times a day and rebuilds the pages only when something has changed. If a source is unavailable, the site keeps showing the last good figures with their date.</p>
<h2>How a Price Pulse signal is set</h2>
<ol>
<li><strong>Season.</strong> Each category has a set of months when sales are historically strongest. If the current month is one of them, the signal is “Buy window”.</li>
<li><strong>Proximity.</strong> If a stronger month is no more than two months away, the signal is “Wait”.</li>
<li><strong>Otherwise</strong> the signal is “Fair”, which means there is no seasonal reason to rush or to hold off.</li>
<li><strong>Price trend.</strong> Alongside the signal, the page shows whether the category’s price index is above or below its level a year ago and how that compares with overall inflation.</li>
</ol>
<p>The Consumer Price Index measures average prices actually paid across the country. It does not track individual products or stores, so a signal describes the conditions in a category, not the quality of a specific offer. Use the <a href="{{root}}tools/deal-score/">Deal Score checker</a> for that.</p>
<p>The October 2025 index was not published. Where a year-over-year comparison needs that month, the base is estimated from September and November 2025 and the figure is marked “about”.</p>
<h2>How the housing market meter is set</h2>
<p>The meter is a score from 0 to 100 built from three public measures: months of supply of new homes (40%), the yearly change in the FHFA house price index (35%), and where the current 30-year mortgage rate sits within its 52-week range (25%). Higher scores mean conditions lean towards buyers. It is a summary of national conditions and says nothing about a particular town or property.</p>
<h2>Cost ranges for home projects</h2>
<p>Ranges on the quote pages are typical U.S. installed prices compiled from published 2026 cost guides. They are intentionally wide. Your own quotes will depend on your region, your home and the materials you choose.</p>
<h2>Editorial rules</h2>
<ul>
<li>We do not publish invented deals, prices, reviews or testimonials.</li>
<li>Sponsored placements are labelled as sponsored.</li>
<li>Advertisers and partners do not see or influence signals, calendars or guides before publication.</li>
<li>External links go to the retailer’s or agency’s own page. Where a link earns us a commission, the page says so.</li>
<li>Corrections are made as soon as an error is confirmed. Report one through the <a href="{{contact}}" target="_blank" rel="noopener">contact page</a>.</li>
</ul>
<h2>What this site is not</h2>
<p>Home.Deals provides general information. It is not financial, legal, tax or construction advice, and it is not a lender, broker, insurer or contractor.</p>
"""

PRIVACY = """
<p>This policy explains what information Home.Deals handles, why, and the choices you have. It applies to this website only.</p>
<h2>Summary</h2>
<ul>
<li>You can read everything on the site without creating an account or telling us who you are.</li>
<li>We receive personal details only when you send a form.</li>
<li>Advertising on the site is served by Google and its partners, who use cookies.</li>
<li>We do not sell contact lists.</li>
</ul>
<h2>Information you give us</h2>
<p>When you send a form, such as a quote request, a deal alert sign-up, a giveaway entry, a deal submission, a support pledge or an application to work with us, we receive what you typed: typically your name, email address, ZIP code, an optional phone number and the details of your request. Forms are delivered to our inbox by FormSubmit, a form-processing service, which handles the submission on our behalf.</p>
<h2>Information stored on your device</h2>
<p>The site uses your browser’s local storage for convenience: your light or dark theme, notices you have dismissed, an unfinished quote request and your last calculator inputs. This information stays on your device and is not sent to us.</p>
<h2>Advertising</h2>
<p>We use Google AdSense. Third-party vendors, including Google, use cookies to serve ads based on your prior visits to this and other websites. Google’s use of advertising cookies enables it and its partners to serve ads to you based on your visits to this site and other sites on the internet.</p>
<ul>
<li>You can opt out of personalised advertising in <a href="https://adssettings.google.com/" target="_blank" rel="noopener">Google’s Ads Settings</a>.</li>
<li>You can opt out of some other vendors’ use of cookies at <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener">aboutads.info</a>.</li>
<li>More detail: <a href="https://policies.google.com/technologies/partner-sites" target="_blank" rel="noopener">how Google uses information from sites that use its services</a>.</li>
</ul>
<p>Where the law requires consent for advertising cookies, you are asked for it before personalised ads are shown.</p>
<h2>Embedded video</h2>
<p>Videos are provided by YouTube using its privacy-enhanced mode. Nothing is loaded from YouTube until you press play. Once you do, YouTube’s own privacy policy applies.</p>
<h2>Hosting</h2>
<p>The site is hosted on GitHub Pages. GitHub may log technical information such as IP addresses for security purposes, under its own privacy statement.</p>
<h2>How we use what you send</h2>
<ul>
<li>To reply to you and carry out your request.</li>
<li>For quote requests, to introduce you to a provider for that request. We tell you who before they contact you, and we pass on only what is needed.</li>
<li>To send deal alerts or giveaway notices you asked for. Every message includes a way to stop.</li>
<li>To prevent abuse and keep basic records.</li>
</ul>
<h2>How long we keep it</h2>
<p>Requests and correspondence are kept for up to 24 months, then deleted, unless you ask us to remove them sooner or the law requires longer.</p>
<h2>Your choices and rights</h2>
<p>You can ask what we hold about you, ask us to correct or delete it, withdraw consent to contact, or object to its use. Depending on where you live, laws such as the GDPR or the CCPA give you additional rights, including the right to complain to a regulator. To make a request, use the <a href="{{contact}}" target="_blank" rel="noopener">contact page</a>. We do not sell personal information.</p>
<h2>Children</h2>
<p>The site is intended for adults. We do not knowingly collect information from children under 16.</p>
<h2>Changes</h2>
<p>If this policy changes, the new version is posted here with a new date.</p>
"""

TERMS = """
<p>By using Home.Deals you agree to these terms. If you do not agree, please do not use the site.</p>
<h2>What the site provides</h2>
<p>Home.Deals publishes general information about prices, sale timing, home projects and home finance, together with calculators and links to third-party websites. It is provided for information only. It is not financial, legal, tax, insurance, engineering or construction advice.</p>
<h2>Prices, deals and data</h2>
<p>Prices, offers, rates and availability change constantly and are controlled by the retailers and institutions concerned. Always confirm details with the seller before you buy. Data pages show the date of the figures they use. We work to keep everything accurate and do not guarantee that it is complete or current.</p>
<h2>Calculators</h2>
<p>Results are estimates based on what you enter and on simplified assumptions. Do not rely on them as the sole basis for a decision.</p>
<h2>Quote requests</h2>
<p>Home.Deals is an introduction service. We are not a contractor, lender, insurer or broker and are not a party to any agreement between you and a provider. We do not guarantee the availability, quality, pricing or licensing of any provider. Check credentials yourself before hiring. We may receive a fee from providers.</p>
<h2>Giveaways</h2>
<p>Giveaways are governed by the rules published on the <a href="{{root}}giveaways/">giveaways page</a> for each round.</p>
<h2>Things you send us</h2>
<p>If you submit a deal, a tip or other content, you confirm that it is accurate to the best of your knowledge and that you have the right to share it, and you allow us to publish, edit or decline it.</p>
<h2>External links and advertising</h2>
<p>The site links to websites we do not control and displays third-party advertising. We are not responsible for their content, products or practices.</p>
<h2>Intellectual property</h2>
<p>Original text, design, graphics and code on Home.Deals are protected by copyright. You may link to any page and quote short passages with attribution. Trademarks belong to their owners. See the <a href="{{root}}disclaimer/">trademark and copyright notice</a>.</p>
<h2>Acceptable use</h2>
<p>Do not misuse the site, attempt to disrupt it, submit false information or use automated means to send forms.</p>
<h2>Disclaimer and limitation of liability</h2>
<p>The site is provided “as is”, without warranties of any kind. To the fullest extent permitted by law, Home.Deals and its operator are not liable for any loss arising from use of the site, reliance on its content, or dealings with third parties reached through it.</p>
<h2>Changes and governing law</h2>
<p>We may update these terms by posting a new version here. These terms are governed by the laws of the jurisdiction in which the operator is established, without regard to conflict-of-law rules.</p>
<h2>Contact</h2>
<p>Questions about these terms can be sent through the <a href="{{contact}}" target="_blank" rel="noopener">contact page</a>.</p>
"""

DISCLAIMER = """
<h2>Independent website</h2>
<p>Home.Deals is the domain name of this independent website. The words “home” and “deals” are used here in their ordinary, descriptive sense: deals for the home. This website is not affiliated with, endorsed by, sponsored by or connected to any company, store, marketplace, app or brand that trades as “HomeDeals”, “Home Deals” or any similar name, anywhere in the world. It does not use their logos, trade dress, designs or content, and nothing here is intended to suggest a connection with them.</p>
<h2>Trademarks</h2>
<p>All retailer, manufacturer, product, program and service names mentioned on this site are trademarks or registered trademarks of their respective owners. They are used only to identify those companies and their own offers, pages and products. Their use does not imply any affiliation with or endorsement by the owner. No third-party logos are reproduced on this site.</p>
<ul>
<li>ENERGY STAR is a registered mark owned by the U.S. Environmental Protection Agency.</li>
<li>Primary Mortgage Market Survey and PMMS are marks of Freddie Mac.</li>
<li>FRED is a mark of the Federal Reserve Bank of St. Louis.</li>
<li>YouTube is a trademark of Google LLC.</li>
</ul>
<h2>Copyright</h2>
<p>The original text, layout, graphics, icons and code on this site are © Home.Deals. Figures drawn from U.S. government sources are public information and are credited on the pages that use them. Video is shown through the official embedded player and remains the property of its creators. Short factual titles of recalls and alerts are reproduced from the agencies’ public notices with a link to the original.</p>
<h2>Reporting a concern</h2>
<p>If you believe something on this site infringes your copyright or misuses your trademark, tell us through the <a href="{{contact}}" target="_blank" rel="noopener">contact page</a>. Please include the page address, the work or mark concerned, proof of ownership or authority to act, and your contact details. We review every notice and will remove or correct material where the concern is valid.</p>
<h2>No professional advice</h2>
<p>Content on this site is general information. It is not financial, legal, tax, insurance or construction advice. Prices, rates and offers change. Confirm them with the provider before acting.</p>
<h2>Domain and website enquiries</h2>
<p>Enquiries about this website, its domain name, sponsorship, advertising or partnership are welcome through the <a href="{{contact}}" target="_blank" rel="noopener">contact page</a>.</p>
"""

DISCLOSURE = """
<p>Home.Deals is free to use. This page explains how it earns money, so you can judge what you read with that in mind.</p>
<h2>Display advertising</h2>
<p>The site shows ads served by Google AdSense. We do not choose individual ads and we do not endorse the advertisers. Ads are kept separate from navigation and buttons. We never ask readers to click on ads.</p>
<h2>Quote requests</h2>
<p>When you ask for quotes and we introduce you to a provider, that provider may pay us a referral fee. You pay nothing to us. Fees do not change the cost ranges, checklists or advice on the page.</p>
<h2>Affiliate links</h2>
<p>Some links to retailers may be affiliate links, which means we may earn a commission if you buy after following them, at no extra cost to you. Pages that carry such links say so. Whether a link earns a commission has no bearing on the signals, the calendar or the order in which sources are listed.</p>
<h2>Sponsorship</h2>
<p>Companies can sponsor a category, a calculator, the alerts email or a giveaway prize. Sponsored placements are clearly labelled. Sponsors do not review editorial content before it is published.</p>
<h2>Reader support</h2>
<p>Readers can choose to <a href="{{root}}support/">support the site</a>. Supporters receive our thanks and nothing that affects editorial content. Home.Deals is not a charity and contributions are not tax-deductible.</p>
<h2>Questions</h2>
<p>Ask anything about how the site is funded through the <a href="{{contact}}" target="_blank" rel="noopener">contact page</a>.</p>
"""

COOKIES = """
<p>This page lists the cookies and similar storage used on Home.Deals.</p>
<table>
<thead><tr><th>Type</th><th>Set by</th><th>Purpose</th><th>Your control</th></tr></thead>
<tbody>
<tr><td>Preferences in local storage</td><td>Home.Deals</td><td>Remembers your theme, dismissed notices, an unfinished quote request and calculator inputs. Stays on your device.</td><td>Clear your browser’s site data at any time</td></tr>
<tr><td>Advertising cookies</td><td>Google and its advertising partners</td><td>Serve and measure ads, limit how often you see an ad and, where permitted, personalise ads</td><td><a href="https://adssettings.google.com/" target="_blank" rel="noopener">Google Ads Settings</a>, <a href="https://www.aboutads.info/choices/" target="_blank" rel="noopener">aboutads.info</a>, or the consent prompt where shown</td></tr>
<tr><td>Video cookies</td><td>YouTube</td><td>Set only after you press play on a video</td><td>Do not play embedded videos, or adjust settings in your Google account</td></tr>
</tbody>
</table>
<p>The site does not set its own tracking or analytics cookies. You can block cookies in your browser settings. The site will still work, and ads may be less relevant.</p>
<p>See the <a href="{{root}}privacy/">privacy policy</a> for how personal information is handled.</p>
"""

ACCESSIBILITY = """
<p>Home.Deals is built to be usable by as many people as possible, and aims to meet the Web Content Accessibility Guidelines 2.2 at level AA.</p>
<h2>What we do</h2>
<ul>
<li>Pages use semantic headings, landmarks and labelled form fields.</li>
<li>Everything can be reached and operated with a keyboard, with a visible focus indicator.</li>
<li>Text and controls meet contrast requirements in both light and dark themes.</li>
<li>Charts are accompanied by the figures in text or a table.</li>
<li>Motion is minimal and is switched off when your device asks for reduced motion.</li>
<li>Videos play only when you choose, in the YouTube player, which offers captions where the creator has provided them.</li>
</ul>
<h2>Known limits</h2>
<p>Advertising and embedded video are supplied by third parties and may not meet the same standard. External websites we link to are outside our control.</p>
<h2>Tell us about a problem</h2>
<p>If something does not work with your browser or assistive technology, tell us through the <a href="{{contact}}" target="_blank" rel="noopener">contact page</a> with the page address and what happened, and we will fix what we can.</p>
"""

GIVEAWAY_STANDING_RULES = [
    ("No purchase necessary", "Entry is free. A purchase, a donation or a quote request does not improve your chances."),
    ("Who can enter", "Legal residents of the 50 United States and the District of Columbia who are 18 or older at the time of entry. Void where prohibited or restricted by law. The operator, its contractors and their households are not eligible."),
    ("How to enter", "Complete the entry form during the entry period. One entry per person per round. Automated or bulk entries are disqualified."),
    ("No ad interaction", "You are never required or encouraged to click on, view or interact with advertising to enter or to win."),
    ("Selecting winners", "Winners are drawn at random from all eligible entries within seven days of the closing date. Odds of winning depend on the number of eligible entries received."),
    ("Notifying winners", "Winners are contacted at the email address on the entry. A winner who does not reply within ten days forfeits the prize and another entry is drawn."),
    ("Prizes", "The prize and its approximate retail value are stated for each round before entries open. Prizes are not transferable and have no cash alternative unless stated. Taxes on a prize are the winner’s responsibility."),
    ("Your information", "Entry details are used to run the giveaway and, only if you tick the box, to send you deal alerts. See the privacy policy."),
    ("General", "The sponsor may cancel or change a round if it cannot run as planned. By entering you accept these rules and the sponsor’s decisions, which are final. Giveaways are not sponsored, endorsed or administered by any retailer or brand named on the site unless stated."),
]

SUPPORT_USES = [
    ("Keeping the lights on", "Hosting, the data pipeline that refreshes prices, rates and recalls four times a day, and the tools behind it."),
    ("More and better guides", "Research and writing time for buying guides, cost guides and new calculators."),
    ("Promotion and reach", "Getting the calendar and Price Pulse in front of more households."),
    ("People", "Paying contributors: deal scouts, writers, video makers and developers."),
    ("Giveaways and prizes", "Funding prize rounds for readers."),
]

ADVERTISE_FORMATS = [
    ("Category sponsorship", "Your brand alongside one of twelve home categories, labelled as sponsor, for a month or a season."),
    ("Calculator sponsorship", "Presenting sponsor of a calculator that matches your product, such as flooring, paint, energy or mortgage."),
    ("Deal alerts sponsorship", "A labelled placement in the deal alerts email."),
    ("Giveaway prize partner", "Supply a prize and be credited throughout the round."),
    ("Quote partner", "Licensed, insured service providers can apply to receive project introductions in their service area."),
    ("Website and domain", "Enquiries about acquiring or partnering on this website and its domain name."),
]

CAREER_ROLES = [
    ("Deal scout", "Finds and checks home deals against price history and sends them in with the evidence."),
    ("Guide writer", "Writes clear, sourced buying and cost guides for a home category you know well."),
    ("Video maker", "Short explainers on timing purchases, reading quotes and using the calculators."),
    ("Data and code contributor", "Improves the data pipeline, adds public data sources and builds calculators."),
    ("Regional partner", "Helps connect readers with reputable, licensed providers in your area."),
]
