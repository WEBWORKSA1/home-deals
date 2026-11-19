"""Home.Deals — guides. Original editorial content.

Tokens such as {{rate30}} are replaced at build time with the latest figures
from /data, so the numbers in these guides stay current without editing.
"""

GUIDES = [
    {
        "slug": "real-deal-or-fake-discount",
        "title": "How to tell a real deal from a fake discount",
        "desc": "Five checks that separate a genuine price drop from an inflated “was” price, with a calculator that does the arithmetic.",
        "topic": "Smart shopping", "minutes": 5, "date": "2026-11-19",
        "points": ["A discount only means something against the price people actually paid.",
                   "Unit price, delivery and required add-ons decide the real cost.",
                   "If a product is always on sale, the sale price is the price."],
        "body": """
<p>A red tag tells you what a retailer wants you to compare. It does not tell you whether the price is good. The percentage on a sale sign is calculated from a reference price the seller chose, and that reference price is the weakest number on the page.</p>
<h2>Start with the price that was actually charged</h2>
<p>U.S. advertising rules say a former price used in a comparison should be one at which the product was genuinely offered for a reasonable period. In practice many home products spend most of the year “on sale”. A sofa listed at $1,999 and sold at $1,199 every week is a $1,199 sofa.</p>
<p>So check the history. Look at what the same item sold for over the past two or three months, at the same store and at two competitors. A real deal sits clearly below that band. Deal communities and price-tracking tools make this quick, and so does a screenshot habit when you are planning a large purchase.</p>
<h2>Compare the unit, not the box</h2>
<p>Pack sizes, piece counts and bundle contents change between stores. A 12-piece cookware set may contain five pans and seven lids and utensils. A “value pack” may cost more per unit than the regular size. Divide the price by the thing you care about: per pan, per sheet, per square foot, per load.</p>
<h2>Add what the checkout adds</h2>
<ul>
<li><strong>Delivery and haul-away.</strong> Freight on furniture and appliances can erase a 15% discount.</li>
<li><strong>Required parts.</strong> Hoses, cords, mounting kits and installation.</li>
<li><strong>Memberships.</strong> A member price is only a saving if you would join anyway.</li>
<li><strong>Financing.</strong> Deferred-interest plans charge interest back to day one if the balance is not cleared in time.</li>
</ul>
<h2>Check the model number</h2>
<p>Some products are made in a version for one retailer or one sale event. The model number differs by a letter and so does the specification: a smaller battery, a brushed motor, a thinner mattress layer. If you cannot find the exact model number anywhere else, compare by specification instead.</p>
<h2>Ask what waiting would cost</h2>
<p>Most home categories have a predictable low season. If the next one is a few weeks away and the item is not urgent, the best deal may be the one you have not seen yet. The <a href="{{root}}calendar/">sale calendar</a> shows the pattern month by month, and <a href="{{root}}price-pulse/">Price Pulse</a> shows whether a category is getting cheaper or dearer compared with last year.</p>
<h2>Run the numbers</h2>
<p>The <a href="{{root}}tools/deal-score/">Deal Score checker</a> takes the sale price, the usual selling price, delivery, tax and any coupon or cashback, and returns the real discount and a plain verdict. It takes under a minute, which is less time than most returns.</p>
""",
        "related": ["tools/deal-score", "tools/unit-price", "calendar"],
    },
    {
        "slug": "home-sale-calendar-explained",
        "title": "Why home prices follow a calendar, and how to use it",
        "desc": "Model years, floor space and weather set the price of furniture, appliances and outdoor goods. Here is the logic behind the best months to buy.",
        "topic": "Smart shopping", "minutes": 5, "date": "2026-11-19",
        "points": ["Retailers discount when they need space, not when you need the product.",
                   "Buy against the season: cooling in fall, heating in spring, patio at summer’s end.",
                   "Holiday weekends are strongest for mattresses and major appliances."],
        "body": """
<p>Sale calendars look like folklore until you see what drives them. Three forces set the timing of almost every home discount, and once you know them you can predict the low point for a product nobody has written a calendar for.</p>
<h2>Force one: the model year</h2>
<p>Manufacturers refresh product lines on a schedule. Most major appliances are renewed in September and October, refrigerators in May, furniture collections in February and August, and vacuums in early summer. The weeks before a refresh are when retailers cut prices on the outgoing version, which is usually the same product with last year’s handle.</p>
<h2>Force two: floor space</h2>
<p>A store can only display so much. Patio sets must leave before holiday stock arrives, and holiday decor must leave before January storage and fitness displays. Bulky seasonal goods are discounted on the retailer’s deadline, in steps, until they are gone. That is why patio furniture is cheapest in September and October and artificial trees on December 26.</p>
<h2>Force three: the weather</h2>
<p>Demand for air conditioners, heaters, snow blowers and mowers follows the forecast. Prices peak in the first hot or cold week, when stock is short and buyers are urgent. The same products are cheapest when nobody needs them.</p>
<h2>Where holidays fit</h2>
<p>Presidents’ Day, Memorial Day, the Fourth of July, Labor Day and Black Friday are marketing events laid on top of those cycles. They matter most in categories with wide margins and negotiable extras: mattresses, major appliances and furniture. For small goods, Black Friday week and the big online sale events set the lows.</p>
<h2>How to use it</h2>
<ol>
<li>Decide what you need in the next twelve months.</li>
<li>Look up each item’s low season on the <a href="{{root}}calendar/">calendar</a>.</li>
<li>Note the price now, so you can judge the sale when it comes.</li>
<li>Buy at the low point, and use the waiting time to collect quotes for anything that needs installing.</li>
</ol>
<p>Timing is not everything. A broken refrigerator cannot wait for May. For urgent purchases, switch from timing to tactics: open-box stock, price matching and bundle offers narrow the gap quickly.</p>
""",
        "related": ["calendar", "price-pulse", "guides/appliance-buying-timing"],
    },
    {
        "slug": "black-friday-home-playbook",
        "title": "Black Friday for the home: what to buy and what to skip",
        "desc": "Which home categories genuinely hit their yearly lows in Black Friday week, which do not, and how to prepare a short list.",
        "topic": "Sale events", "minutes": 5, "date": "2026-11-19",
        "points": ["Best: small kitchen appliances, vacuums, smart home devices, tool kits and bedding-in-a-box mattresses.",
                   "Wait: holiday decor, linens, furniture clearance and flooring installation.",
                   "Sales now start in late October, so the price on the Friday itself is rarely special."],
        "body": """
<p>Black Friday is no longer a day. Large home retailers now open “early” sales in late October and keep them running into December, which changes the job from queuing to comparing. The questions are which categories reach a true low in this window and how to recognise it.</p>
<h2>Categories that usually hit their lows</h2>
<ul>
<li><strong>Small kitchen appliances and cookware.</strong> Gift demand makes this the most competitive category of the season.</li>
<li><strong>Vacuums and robot vacuums.</strong> Previous-generation models fall furthest.</li>
<li><strong>Smart home devices.</strong> Platform makers discount their own hardware heavily.</li>
<li><strong>Tool combo kits.</strong> Look for free-tool offers with a battery starter kit.</li>
<li><strong>Online mattress brands.</strong> The lowest advertised prices of the year, often with bundles.</li>
<li><strong>Major appliances.</strong> Good, with bundle savings, though fall clearance of outgoing models is comparable.</li>
</ul>
<h2>Categories worth waiting on</h2>
<ul>
<li><strong>Holiday decor and artificial trees.</strong> Half price or better from December 26.</li>
<li><strong>Sheets and towels.</strong> January white sales.</li>
<li><strong>Furniture.</strong> January clearance is deeper on specific pieces.</li>
<li><strong>Flooring and carpet installation.</strong> Installers discount in the December and January lull.</li>
<li><strong>Patio and grills.</strong> Whatever was left sold in October.</li>
</ul>
<h2>Prepare a short list</h2>
<p>Doorbusters work because they catch shoppers without a plan. Write down the three to five things you would buy anyway, with the exact model and today’s price. During the sale, compare against that note instead of the crossed-out number on the page.</p>
<h2>Watch for event-only models</h2>
<p>Some televisions, tools and small appliances are built for the season with a slightly different model number and a thinner specification. If the model appears nowhere else and has no reviews before November, compare the specification line by line.</p>
<h2>Use the return calendar</h2>
<p>Many retailers extend holiday returns into January. Buy early when a price is good, keep the receipt, and ask for a price adjustment if the same store drops the price further within its adjustment window.</p>
<p>Before you buy from an unfamiliar brand, search the <a href="{{root}}recalls/">Recall Radar</a>, and run any headline discount through the <a href="{{root}}tools/deal-score/">Deal Score checker</a>.</p>
""",
        "related": ["calendar", "tools/deal-score", "recalls"],
    },
    {
        "slug": "appliance-buying-timing",
        "title": "How to buy a major appliance for less",
        "desc": "Model changeovers, bundle rebates, open-box stock and delivery terms: the levers that set the real price of a refrigerator, range or washer.",
        "topic": "Buying guides", "minutes": 6, "date": "2026-11-19",
        "points": ["Outgoing models are cleared in September and October, refrigerators in May.",
                   "Bundle offers, price matching and utility rebates stack.",
                   "Delivery, installation parts and haul-away belong in the comparison."],
        "body": """
<p>Appliance prices move more than most people expect. The same dishwasher can sell for 30% less in October than in March, and the gap between the advertised price and the delivered, connected price can be several hundred dollars. Here is how to control both.</p>
<h2>Buy the outgoing model</h2>
<p>New ranges, dishwashers, washers and dryers reach stores in September and October, and new refrigerators in May. Retailers discount the previous model to clear it. The differences are often cosmetic, so the outgoing model at 25% to 40% under its launch price is the standard good deal in this category.</p>
<p>Price Pulse currently shows major appliance prices {{pulse_major_appliances_dir}} compared with a year ago, based on the Consumer Price Index. Check the <a href="{{root}}price-pulse/">latest reading</a> before you decide whether to wait.</p>
<h2>Stack the savings</h2>
<ol>
<li><strong>Holiday bundle offers.</strong> Buying two or more pieces from one brand often adds a tiered rebate.</li>
<li><strong>Price matching.</strong> Large appliance retailers generally match each other on identical model numbers. Bring a link.</li>
<li><strong>Utility rebates.</strong> Search your ZIP code in the ENERGY STAR rebate finder. The federal tax credits ended after December 31, 2025, but utility and state programs continue.</li>
<li><strong>Card and portal offers.</strong> Activate them before you check out.</li>
</ol>
<h2>Consider open-box and scratch-and-dent</h2>
<p>A dent on the side of a refrigerator that will sit between cabinets costs nothing in use. Ask whether the full manufacturer warranty applies, inspect the unit in person and confirm the return policy. Discounts of 20% to 50% are common.</p>
<h2>Compare the delivered price</h2>
<ul>
<li>Delivery and whether it includes bringing the unit inside</li>
<li>Installation and required parts: hoses, cords, gas connectors, brackets</li>
<li>Haul-away of the old appliance</li>
<li>Whether doors need removing to get it through yours</li>
</ul>
<h2>Decide on the warranty at home</h2>
<p>Extended warranties are sold at the moment you are least able to evaluate them. Check what your credit card adds, read the manufacturer warranty and decide beforehand. If you want cover, you can usually buy it within 30 days.</p>
<h2>Repair or replace?</h2>
<p>If a repair costs more than half the price of a comparable new appliance and the unit is past the middle of its expected life, replacement usually makes sense. The <a href="{{root}}tools/repair-or-replace/">Repair or replace calculator</a> applies that rule to your numbers and adds the energy savings of a newer model.</p>
""",
        "related": ["deals/appliances", "tools/repair-or-replace", "tools/energy-cost"],
    },
    {
        "slug": "mattress-shopping",
        "title": "How to shop a mattress sale without getting lost in model names",
        "desc": "Why mattresses are hard to compare, what the four holiday sales really offer, and the terms that matter more than the discount.",
        "topic": "Buying guides", "minutes": 5, "date": "2026-11-19",
        "points": ["The same mattress is sold under different names at different stores.",
                   "Compare construction, trial period, return cost and warranty.",
                   "Presidents’ Day, Memorial Day, Labor Day and Black Friday are the four real sales."],
        "body": """
<p>Mattresses are one of the few products designed to resist comparison. Manufacturers sell near-identical models under exclusive names to each retailer, which makes price matching almost impossible and leaves the shopper comparing adjectives.</p>
<h2>Compare the build, not the name</h2>
<p>Ask for, or look up, four facts about any mattress: its height, its type (innerspring, hybrid, foam or latex), the coil count and gauge if it has coils, and the thickness and density of its foam layers. Two mattresses that match on those are close relatives whatever they are called.</p>
<h2>Know the four sales</h2>
<p>Presidents’ Day in February, Memorial Day in May, Labor Day in September and Black Friday in November carry the year’s strongest offers. Outside those weeks most sellers still run a promotion, and the difference is usually in the extras: a free adjustable base, pillows, sheets or a longer trial.</p>
<h2>Read the trial and return terms</h2>
<ul>
<li><strong>Trial length.</strong> Ninety nights or more is common online. Some require you to keep the mattress 30 nights before returning it.</li>
<li><strong>Return cost.</strong> Free pickup, a flat fee or a restocking percentage.</li>
<li><strong>Exchange or refund.</strong> Store trials are often exchange-only.</li>
</ul>
<h2>Check the warranty wording</h2>
<p>A ten-year warranty is standard. What matters is the sag depth it covers, usually between three-quarters of an inch and an inch and a half, and whether a stain or an unsupportive base voids it. Use a protector from day one.</p>
<h2>Negotiate in stores</h2>
<p>Showroom margins are wide. Ask for the holiday price outside the holiday, free delivery, removal of the old mattress and a base upgrade. Having a competing written price for a similar build helps even when the model names differ.</p>
<h2>Check safety on unfamiliar brands</h2>
<p>Mattresses sold in the U.S. must meet a federal flammability standard, and low-priced brands sold through online marketplaces are recalled regularly for failing it. Search the brand in the <a href="{{root}}recalls/">Recall Radar</a> before you order.</p>
""",
        "related": ["deals/mattresses", "recalls", "calendar"],
    },
    {
        "slug": "open-box-refurbished",
        "title": "Open-box, refurbished and scratch-and-dent: what to check",
        "desc": "The discounted conditions explained, with a checklist for warranty, returns and inspection before you buy.",
        "topic": "Smart shopping", "minutes": 4, "date": "2026-11-19",
        "points": ["Open-box is a return, refurbished is repaired and tested, scratch-and-dent is cosmetically damaged.",
                   "Who refurbished it and who backs the warranty matter more than the label.",
                   "Inspect before delivery leaves, and check for recalls."],
        "body": """
<p>Three labels cover most discounted non-new stock, and each means something different about what happened to the product before it reached you.</p>
<h2>What the labels mean</h2>
<ul>
<li><strong>Open-box.</strong> Bought, opened and returned, or used as a display. Often unused. Usually sold with the retailer’s normal return policy.</li>
<li><strong>Refurbished or renewed.</strong> Returned or faulty stock that has been inspected, repaired where needed and tested. Quality depends on who did the work.</li>
<li><strong>Scratch-and-dent.</strong> New and working, with cosmetic damage from shipping or the warehouse floor.</li>
<li><strong>Floor model.</strong> Displayed in a store. Expect wear on touch points.</li>
</ul>
<h2>The checklist</h2>
<ol>
<li><strong>Who stands behind it?</strong> Manufacturer-refurbished stock with a manufacturer warranty is the safest. Third-party “renewed” listings vary.</li>
<li><strong>How long is the warranty?</strong> One year matches new. Ninety days is thin for a major appliance.</li>
<li><strong>What is the return window?</strong> Clearance and outlet stock is sometimes final sale.</li>
<li><strong>Is everything in the box?</strong> Racks, shelves, remotes, mounting hardware and manuals.</li>
<li><strong>Where is the damage?</strong> A dent on a hidden side is free money. A dent near a door seal or a control panel is not.</li>
<li><strong>Is the model recalled?</strong> Older stock is more likely to be affected. Search the <a href="{{root}}recalls/">Recall Radar</a>.</li>
</ol>
<h2>Where it works best</h2>
<p>Major appliances, furniture, tools and vacuums carry the largest open-box savings, commonly 20% to 50%. Mattresses are different: many states restrict resale of used bedding, so “open-box” mattresses are usually comfort returns that have been sanitised. Read the terms carefully.</p>
<h2>Inspect on arrival</h2>
<p>Check the item while the delivery team is still there. Note any damage that was not disclosed on the delivery receipt and photograph it. For appliances, run a full cycle within the return window.</p>
""",
        "related": ["tools/deal-score", "recalls", "deals/appliances"],
    },
    {
        "slug": "stacking-savings",
        "title": "Stacking savings: the order that gets the lowest price",
        "desc": "Sale price, coupon, rebate, cashback, card offer and price adjustment: how they combine, and the order to apply them.",
        "topic": "Smart shopping", "minutes": 5, "date": "2026-11-19",
        "points": ["Discounts multiply in sequence, so 20% then 10% is 28%, not 30%.",
                   "Portals and card offers pay on the amount you are charged.",
                   "A price adjustment after purchase is the most overlooked saving."],
        "body": """
<p>The lowest price on a home purchase rarely comes from one discount. It comes from five or six small ones applied in the right order. Each layer is modest, and together they regularly add 10% to 20% on top of the sale price.</p>
<h2>The stack, in order</h2>
<ol>
<li><strong>Sale price.</strong> Start from a price that is good against its own history. Stacking cannot rescue a bad base price.</li>
<li><strong>Store coupon or promo code.</strong> Email sign-up codes, loyalty offers and mover’s coupons from home improvement stores. Most stores accept one code per order.</li>
<li><strong>Manufacturer or utility rebate.</strong> Common on appliances, paint, water heaters and thermostats. Submit the same day and keep copies.</li>
<li><strong>Cashback portal.</strong> Click through before adding items to the basket. The portal is paid a commission by the retailer and shares part of it with you.</li>
<li><strong>Card-linked offer or category bonus.</strong> Activate in your card app first.</li>
<li><strong>Discounted gift cards.</strong> Buying a retailer’s gift card below face value, then paying with it.</li>
<li><strong>Price adjustment.</strong> If the price falls after you buy, ask for the difference within the retailer’s window.</li>
</ol>
<h2>Why the arithmetic disappoints</h2>
<p>Percentages apply one after another. Twenty percent off followed by a 10% coupon is 28% off, because the coupon applies to the reduced price. Cashback is paid on the amount charged before tax, so it shrinks as the other layers grow. The <a href="{{root}}tools/deal-score/">Deal Score checker</a> applies each layer in the right sequence.</p>
<h2>What does not stack</h2>
<ul>
<li>Two promo codes on one order, at most stores</li>
<li>A portal payout with a coupon code that did not come from the portal, in some cases</li>
<li>Price matching with a coupon, which many retailers treat as either-or</li>
</ul>
<h2>Keep it proportionate</h2>
<p>An hour of stacking is worth it on a $2,000 appliance order and not on a $20 lamp. Use the full stack for the big purchases and a single code for the rest.</p>
""",
        "related": ["tools/deal-score", "deals", "guides/real-deal-or-fake-discount"],
    },
    {
        "slug": "compare-contractor-quotes",
        "title": "How to compare contractor quotes line by line",
        "desc": "A method for getting three comparable quotes, reading what is missing from each, and choosing on value instead of the bottom line.",
        "topic": "Home projects", "minutes": 6, "date": "2026-11-19",
        "points": ["Write one scope and give it to every contractor.",
                   "The cheapest quote is often the one that left something out.",
                   "Tie payments to finished stages, and keep the deposit small."],
        "body": """
<p>Three quotes for the same job can differ by 50%. Usually nobody is cheating. Each contractor priced a different job, because each was given a different description of it. The fix is to control the description.</p>
<h2>Write the scope first</h2>
<p>One page is enough. State what is being done, where, with which materials or grade of material, what is being removed, and who handles permits and disposal. Send the same page to every contractor and ask them to price exactly that, with alternatives listed separately.</p>
<h2>Line the quotes up</h2>
<p>Put the quotes side by side and compare these lines:</p>
<ul>
<li><strong>Materials.</strong> Brand, product line, grade and quantity</li>
<li><strong>Labour.</strong> What is included, and what counts as an extra</li>
<li><strong>Preparation and demolition.</strong> Tear-off, removal and disposal</li>
<li><strong>Allowances.</strong> The budget assumed for items you have not chosen yet</li>
<li><strong>Permits and inspections.</strong> Who obtains and pays for them</li>
<li><strong>Timeline.</strong> Start date, duration and what happens if it slips</li>
<li><strong>Warranty.</strong> On materials and on workmanship, in writing</li>
</ul>
<p>When one quote is far lower, find the line that explains it. A missing tear-off, a low tile allowance or no permit is a different job, not a better price.</p>
<h2>Check the business</h2>
<ol>
<li>Verify the licence with your state or local licensing board.</li>
<li>Ask for a certificate of liability insurance and, where required, workers’ compensation.</li>
<li>Call two recent customers with a similar project.</li>
<li>Search the business name with your state attorney general or consumer protection office.</li>
</ol>
<h2>Agree how money moves</h2>
<p>A fair schedule ties payments to completed stages. Keep the deposit small. Some states cap it: California, for example, limits home improvement deposits to 10% of the contract price or $1,000, whichever is less. Hold back a final payment until the punch list is done, and ask for lien waivers from the contractor and major suppliers as you pay.</p>
<h2>Put changes in writing</h2>
<p>Changes are where budgets go. Agree before work starts that every change is priced and signed before it is carried out.</p>
<h2>Get a ballpark first</h2>
<p>Knowing the typical range makes outliers obvious. The <a href="{{root}}quotes/">quote request</a> page shows an instant ballpark for twelve project types before you talk to anyone.</p>
""",
        "related": ["quotes", "guides/avoid-home-service-scams", "tools/repair-or-replace"],
    },
    {
        "slug": "home-energy-savings-2026",
        "title": "Home energy savings after the federal tax credits ended",
        "desc": "The 25C and 25D credits stopped at the end of 2025. Here is what still pays: utility and state rebates, and the upgrades with the fastest payback.",
        "topic": "Home projects", "minutes": 6, "date": "2026-11-19",
        "points": ["Federal credits for home efficiency and residential clean energy ended for work done after December 31, 2025.",
                   "Utility rebates and state-run programs still exist and vary by ZIP code.",
                   "Air sealing, insulation and controls usually pay back before equipment does."],
        "body": """
<p>For three years, federal tax credits covered 30% of many home energy upgrades. That changed with legislation signed in July 2025. According to the IRS, the Energy Efficient Home Improvement Credit is not allowed for property placed in service after December 31, 2025, and the Residential Clean Energy Credit is not allowed for expenditures made after that date.</p>
<h2>What that means in practice</h2>
<ul>
<li>Upgrades completed in 2025 or earlier could be claimed on that year’s return using Form 5695.</li>
<li>Unused residential clean energy credit from earlier years can still be carried forward.</li>
<li>For work done now, do not build a federal credit into the payback. Some government web pages still describe the old rules, so check the date on anything you read.</li>
</ul>
<h2>What still exists</h2>
<ul>
<li><strong>Utility rebates.</strong> Many electric and gas utilities pay rebates on heat pumps, heat pump water heaters, smart thermostats, insulation and efficient appliances. Some apply the rebate at checkout through a utility marketplace.</li>
<li><strong>State programs.</strong> Home energy rebate programs are run state by state, with eligibility often tied to income. Availability differs widely, so check your state energy office.</li>
<li><strong>Weatherization assistance.</strong> Income-qualified households can receive free efficiency work through state and local agencies.</li>
</ul>
<p>The quickest way to see what applies to you is a ZIP code search in the ENERGY STAR rebate finder, followed by your utility’s own rebate page.</p>
<h2>What pays back fastest</h2>
<p>With electricity averaging about {{kwh}} per kilowatt-hour nationally ({{kwh_date}}, Bureau of Labor Statistics), the order of operations matters more than ever.</p>
<ol>
<li><strong>Air sealing and attic insulation.</strong> Low cost, and it reduces the size of any heating or cooling system you buy later.</li>
<li><strong>Smart or programmable thermostat.</strong> Often rebated to near zero.</li>
<li><strong>LED lighting and controls.</strong> Small, immediate, permanent.</li>
<li><strong>Heat pump water heater.</strong> Uses a fraction of the electricity of a standard electric tank.</li>
<li><strong>Heating and cooling replacement.</strong> Best timed for when the old system is near the end of its life.</li>
<li><strong>Solar.</strong> Now depends on your electricity rate and your utility’s export rules. Compare several quotes by price per watt.</li>
</ol>
<h2>Run your own numbers</h2>
<p>The <a href="{{root}}tools/energy-cost/">Energy cost calculator</a> compares the running cost of two appliances at your electricity rate and shows how many years an efficient model takes to repay its premium.</p>
""",
        "related": ["tools/energy-cost", "quotes/solar", "quotes/hvac"],
    },
    {
        "slug": "refinance-math",
        "title": "Refinance math when rates are high",
        "desc": "The break-even calculation, what points really cost, and the options for owners whose existing rate is lower than today’s.",
        "topic": "Home money", "minutes": 6, "date": "2026-11-19",
        "points": ["Break-even months equal closing costs divided by monthly savings.",
                   "If your current rate is below today’s average, a rate-and-term refinance cannot help.",
                   "Compare at least three lenders on the same day, using the Loan Estimate."],
        "body": """
<p>The average 30-year fixed mortgage rate was {{rate30}}% in the week of {{rate30_date}}, according to Freddie Mac’s weekly survey, compared with {{rate30_year_ago}}% a year earlier. Whether refinancing makes sense depends entirely on which side of that number your current loan sits.</p>
<h2>The break-even calculation</h2>
<p>Refinancing replaces your loan with a new one and costs money up front, commonly a few percent of the loan amount in lender fees, title, appraisal and prepaid items. The decision comes down to one division:</p>
<p><strong>Break-even months = total closing costs ÷ monthly payment savings</strong></p>
<p>If closing costs are $6,000 and the new payment is $200 lower, you break even in 30 months. Stay longer than that and you gain. Sell or refinance again sooner and you lose. The <a href="{{root}}tools/refinance/">Refinance break-even calculator</a> does this with your figures and also shows the total interest on both loans.</p>
<h2>Watch the term reset</h2>
<p>A lower payment is not the same as a lower cost. Moving a loan with 24 years left into a new 30-year loan can reduce the payment while increasing the total interest. Compare total cost over the period you expect to keep the home, or match the new term to the years you have left.</p>
<h2>What points cost</h2>
<p>A point is 1% of the loan paid up front to lower the rate. Points have their own break-even, calculated the same way. They suit owners who will keep the loan for many years and rarely suit anyone who may move or refinance within five.</p>
<h2>If your rate is lower than today’s</h2>
<p>Millions of owners hold loans well below current rates. For them, replacing the first mortgage is expensive, and these are the usual alternatives:</p>
<ul>
<li><strong>Home equity loan or line of credit</strong> to borrow against the home while keeping the first mortgage untouched</li>
<li><strong>Recasting</strong> after a lump-sum payment, which lowers the payment for a small fee without changing the rate</li>
<li><strong>Extra principal payments</strong>, which shorten the loan with no fees at all</li>
</ul>
<h2>Shop on one day</h2>
<p>Rates change daily, so collect Loan Estimates from at least three lenders on the same day and compare the rate, the points and the lender fees in section A. Multiple mortgage credit checks within a short window are generally treated as a single inquiry for scoring purposes.</p>
<p>See the current averages and the last five years on the <a href="{{root}}rates/">mortgage rates</a> page. This guide is general information, not financial advice for your situation.</p>
""",
        "related": ["rates", "tools/refinance", "tools/mortgage"],
    },
    {
        "slug": "recalls-before-you-buy",
        "title": "Check recalls before you buy clearance or secondhand",
        "desc": "How product recalls work, where they are published, and a two-minute check for furniture, appliances and heaters.",
        "topic": "Safety", "minutes": 4, "date": "2026-11-19",
        "points": ["It is illegal to sell a recalled consumer product in the U.S., including secondhand.",
                   "Dressers, mattresses, heaters and battery-powered tools account for many home recalls.",
                   "Recalled products usually qualify for a refund, repair or replacement."],
        "body": """
<p>The U.S. Consumer Product Safety Commission announces several hundred recalls a year, and a large share involve things found in every home: dressers that tip, mattresses that fail the flammability standard, heaters and fire pits that burn, and battery packs that overheat.</p>
<h2>Why clearance and secondhand need a check</h2>
<p>Selling a recalled product is against federal law, and that includes resale. In practice recalled items still circulate through marketplaces, garage sales and liquidation lots, because sellers often do not know. Low-priced brands sold only online appear in recall notices regularly, sometimes within months of going on sale.</p>
<h2>The two-minute check</h2>
<ol>
<li>Find the brand and model number on the product label or listing.</li>
<li>Search the brand in the <a href="{{root}}recalls/">Recall Radar</a>, which lists recent home-related recalls from the official database.</li>
<li>For older products, search the full database at CPSC.gov.</li>
<li>If the seller cannot provide a model number, treat that as an answer.</li>
</ol>
<h2>What a recall gives you</h2>
<p>Each notice names a remedy: a refund, a free repair or a replacement. You do not need a receipt in most cases. The notice explains how to register, and what to do with the product in the meantime, which is usually to stop using it straight away.</p>
<h2>Products worth registering</h2>
<p>Return the registration card or register online for major appliances, heaters, nursery furniture and anything with a large battery. Registration is how a manufacturer finds you when a recall is issued.</p>
<h2>Report a problem</h2>
<p>If a product injures someone or fails dangerously, report it at SaferProducts.gov. Reports from consumers are one of the ways recalls begin.</p>
<p>Recall information on Home.Deals comes from the CPSC’s public data and is refreshed several times a day. Always confirm details in the official notice linked from each entry.</p>
""",
        "related": ["recalls", "guides/open-box-refurbished", "deals/furniture"],
    },
    {
        "slug": "first-year-homeowner-budget",
        "title": "A first-year budget for a new homeowner",
        "desc": "What to set aside for maintenance, which big-ticket items to plan for, and a seasonal checklist that prevents the expensive repairs.",
        "topic": "Home money", "minutes": 5, "date": "2026-11-19",
        "points": ["Set aside 1% to 4% of the home’s value each year for maintenance and repairs.",
                   "Know the age of the roof, water heater and HVAC, because they fail on a schedule.",
                   "Small seasonal jobs prevent most large bills."],
        "body": """
<p>The mortgage payment is the predictable part of owning a home. The unpredictable part is everything attached to it, and the first year is when most new owners discover what the previous owner postponed.</p>
<h2>How much to set aside</h2>
<p>A long-standing rule of thumb is 1% to 4% of the home’s value per year for maintenance and repairs, with newer homes at the low end and older homes at the high end. On a $400,000 house that is roughly $330 to $1,330 a month. You will not spend it evenly. Some years cost little and one year replaces a roof.</p>
<h2>Find the ages that matter</h2>
<p>Your inspection report or the equipment labels will give you install dates. Typical service lives:</p>
<table>
<thead><tr><th>Item</th><th>Typical life</th><th>Typical replacement cost</th></tr></thead>
<tbody>
<tr><td>Tank water heater</td><td>8 to 12 years</td><td>$1,300 to $3,200</td></tr>
<tr><td>Central air conditioner</td><td>12 to 17 years</td><td>$4,500 to $9,500</td></tr>
<tr><td>Furnace</td><td>15 to 20 years</td><td>$3,200 to $7,800</td></tr>
<tr><td>Asphalt shingle roof</td><td>20 to 30 years</td><td>$5,500 to $16,000</td></tr>
<tr><td>Refrigerator</td><td>10 to 15 years</td><td>$900 to $3,000</td></tr>
<tr><td>Dishwasher</td><td>9 to 12 years</td><td>$500 to $1,400</td></tr>
<tr><td>Washer or dryer</td><td>10 to 13 years</td><td>$600 to $1,500 each</td></tr>
</tbody>
</table>
<p>Anything within three years of the end of its range belongs in your plan. Collecting quotes before it fails is the single best way to avoid emergency pricing.</p>
<h2>Do the cheap jobs on schedule</h2>
<ul>
<li><strong>Spring.</strong> Clean gutters, check the roof from the ground, service the air conditioner, test the sump pump.</li>
<li><strong>Summer.</strong> Seal gaps around windows and doors, check the deck and exterior paint.</li>
<li><strong>Fall.</strong> Service the furnace, drain outdoor taps, clean the dryer vent, sweep the chimney.</li>
<li><strong>Winter.</strong> Flush the water heater, test smoke and carbon monoxide alarms, check for ice dams.</li>
<li><strong>Monthly.</strong> Change or check the HVAC filter.</li>
</ul>
<h2>Buy the first-year list at the right time</h2>
<p>New owners buy more furniture, appliances and tools in twelve months than in the following ten years. Spread those purchases across the <a href="{{root}}calendar/">sale calendar</a> and the saving is typically larger than any single negotiation.</p>
""",
        "related": ["calendar", "quotes", "tools/mortgage"],
    },
    {
        "slug": "avoid-home-service-scams",
        "title": "Home repair scams and high-pressure sales: how to say no",
        "desc": "The common patterns, your cancellation rights for sales made at your door, and what to do if something has already gone wrong.",
        "topic": "Safety", "minutes": 5, "date": "2026-11-19",
        "points": ["A price that expires today is a sales tactic.",
                   "Most sales of $25 or more made at your home can be cancelled within three business days.",
                   "Never pay in full up front, and never sign over an insurance claim under pressure."],
        "body": """
<p>Most contractors are honest. The dishonest ones are easy to recognise, because they use the same handful of approaches and they all depend on speed. Slowing the conversation down defeats nearly every one.</p>
<h2>The patterns</h2>
<ul>
<li><strong>The storm chaser.</strong> Arrives after hail or wind, offers a free inspection, finds damage and asks you to sign immediately.</li>
<li><strong>Leftover materials.</strong> A crew “just finished a job nearby” and can do your driveway or roof cheaply today, for cash.</li>
<li><strong>The today-only price.</strong> A large list price, a dramatic discount and a call to a manager. Common with windows, solar, siding and water treatment.</li>
<li><strong>The big deposit.</strong> Most or all of the money up front, followed by delays or disappearance.</li>
<li><strong>The claim handler.</strong> Offers to “deal with the insurance” and asks you to sign over your benefits.</li>
<li><strong>The free energy audit.</strong> A sales visit presented as a utility or government program.</li>
</ul>
<h2>Your right to cancel</h2>
<p>The Federal Trade Commission’s Cooling-Off Rule gives you three business days to cancel most sales of $25 or more made at your home, and sales of $130 or more made at temporary locations such as hotel rooms and fairs. The seller must tell you about the right and give you two copies of a cancellation form. Many states add their own protections for home improvement contracts.</p>
<h2>Five habits that protect you</h2>
<ol>
<li>Never sign on the first visit. A real price is still there next week.</li>
<li>Get three written quotes for the same scope.</li>
<li>Verify the licence and insurance yourself, using the state board, not a number the salesperson provides.</li>
<li>Pay by card or cheque, in stages, with a small deposit.</li>
<li>Call your insurer yourself before agreeing to any insurance-funded repair.</li>
</ol>
<h2>If it has already happened</h2>
<p>Cancel in writing within the cooling-off period and keep proof of delivery. Dispute card payments quickly. Report the business to the FTC at ReportFraud.ftc.gov and to your state attorney general, and to your local building department if unlicensed work was done.</p>
<p>The <a href="{{root}}recalls/">Recall Radar</a> page also lists current consumer alerts from the FTC that relate to homes and shopping.</p>
""",
        "related": ["guides/compare-contractor-quotes", "quotes", "recalls"],
    },
]
