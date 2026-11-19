/* Home.Deals — calculators. Everything runs in the browser. */
(function () {
  "use strict";
  var L = window.HDlib;
  if (!L) { return; }
  var HD = window.HD || {};
  var money = L.money;

  function pct(n, d) { return isFinite(n) ? n.toFixed(d === undefined ? 1 : d) + "%" : "—"; }
  function pmt(principal, ratePct, years) {
    var r = ratePct / 100 / 12, n = years * 12;
    if (n <= 0) { return 0; }
    return r ? principal * r / (1 - Math.pow(1 + r, -n)) : principal / n;
  }
  function rows(list) {
    return "<dl>" + list.map(function (r) { return "<div><dt>" + r[0] + "</dt><dd>" + r[1] + "</dd></div>"; }).join("") + "</dl>";
  }
  function verdict(kind, text) { return '<p><span class="verdict verdict-' + kind + '">' + text + "</span></p>"; }
  function firstNumber(text) { var m = /[\d.]+/.exec(text || ""); return m ? parseFloat(m[0]) : 0; }

  var calc = {
    "deal-score": function (v) {
      if (!(v.sale > 0)) { return null; }
      var afterCoupon = Math.max(0, v.sale * (1 - v.coupon_pct / 100) - v.coupon_amt);
      var tax = afterCoupon * v.tax_pct / 100;
      var payToday = afterCoupon + v.shipping + tax;
      var cashback = afterCoupon * v.cashback_pct / 100;
      var effective = afterCoupon + v.shipping - v.rebate - cashback;
      var out = "";
      var list = [["Price after coupons", money(afterCoupon, true)], ["Delivery and fees", money(v.shipping, true)],
                  ["Sales tax", money(tax, true)], ["You pay today", money(payToday, true)],
                  ["Rebate and cashback you get back", money(v.rebate + cashback, true)],
                  ["Your cost before tax, delivered", money(effective, true)]];
      if (v.usual > 0) {
        var real = (1 - effective / v.usual) * 100;
        var kind = real >= 30 ? "good" : real >= 15 ? "good" : real >= 5 ? "ok" : real >= 0 ? "warn" : "bad";
        var label = real >= 30 ? "Strong deal" : real >= 15 ? "Good deal" : real >= 5 ? "Modest saving" : real >= 0 ? "Barely a discount" : "You would pay more than usual";
        out += "<h3>Real discount</h3><p class=\"big\">" + pct(real) + "</p>" + verdict(kind, label);
        list.push(["Real discount against the usual price", pct(real)]);
        if (v.list > 0) {
          var advertised = (1 - v.sale / v.list) * 100;
          list.push(["Discount the store advertises", pct(advertised)]);
          if (advertised - real > 3) {
            out += "<p>About " + Math.round(advertised - real) + " points of the advertised discount come from the reference price, not from what the item usually sells for.</p>";
          }
        }
      } else {
        out += "<h3>What you pay</h3><p class=\"big\">" + money(payToday, true) + "</p><p>Add the usual selling price to see the real discount.</p>";
      }
      return out + rows(list);
    },

    "unit-price": function (v) {
      var opts = [["A", v.a_price, v.a_qty], ["B", v.b_price, v.b_qty], ["C", v.c_price, v.c_qty]]
        .filter(function (o) { return o[1] > 0 && o[2] > 0; })
        .map(function (o) { return { name: o[0], unit: o[1] / o[2] }; });
      if (opts.length < 2) { return null; }
      var best = opts.reduce(function (a, b) { return b.unit < a.unit ? b : a; });
      var list = opts.map(function (o) {
        var extra = o === best ? "lowest" : "+" + pct((o.unit / best.unit - 1) * 100) + " more";
        return ["Option " + o.name, money(o.unit, true) + " per unit, " + extra];
      });
      return "<h3>Best value</h3><p class=\"big\">Option " + best.name + "</p>" +
        verdict("good", money(best.unit, true) + " per unit") + rows(list);
    },

    "mortgage": function (v) {
      var loan = v.price - v.down, years = firstNumber(v.term);
      if (!(loan > 0) || !(years > 0)) { return null; }
      var pi = pmt(loan, v.rate, years);
      var tax = v.tax / 12, ins = v.ins / 12, pmi = loan * v.pmi_pct / 100 / 12;
      var total = pi + tax + ins + v.hoa + pmi;
      var table = "<table><thead><tr><th>Rate</th><th>Principal and interest</th><th>Difference</th></tr></thead><tbody>" +
        [-1, -0.5, 0, 0.5, 1].map(function (d) {
          var p = pmt(loan, v.rate + d, years), diff = p - pi;
          return "<tr><td>" + pct(v.rate + d, 2) + "</td><td>" + money(p) + "</td><td>" + (d === 0 ? "—" : (diff > 0 ? "+" : "−") + money(Math.abs(diff))) + "</td></tr>";
        }).join("") + "</tbody></table>";
      return "<h3>Monthly payment</h3><p class=\"big\">" + money(total) + "</p>" +
        rows([["Loan amount", money(loan)], ["Down payment", pct(v.price > 0 ? v.down / v.price * 100 : 0)],
              ["Principal and interest", money(pi)], ["Property tax", money(tax)], ["Home insurance", money(ins)],
              ["HOA", money(v.hoa)], ["Mortgage insurance", money(pmi)],
              ["Total interest over " + years + " years", money(pi * years * 12 - loan)]]) + table;
    },

    "refinance": function (v) {
      var years = firstNumber(v.new_term);
      if (!(v.bal > 0) || !(v.years_left > 0) || !(years > 0)) { return null; }
      var cur = pmt(v.bal, v.cur_rate, v.years_left), neu = pmt(v.bal, v.new_rate, years);
      var saving = cur - neu;
      var curInterest = cur * v.years_left * 12 - v.bal, newInterest = neu * years * 12 - v.bal;
      var net = curInterest - newInterest - v.costs;
      var out;
      if (saving <= 0) {
        out = "<h3>Break-even</h3><p class=\"big\">None</p>" + verdict("bad", "The new loan raises your payment");
      } else {
        var months = v.costs / saving;
        var kind = months <= 36 ? "good" : months <= 60 ? "warn" : "bad";
        var label = months <= 36 ? "Pays for itself quickly" : months <= 60 ? "Slow payback" : "Hard to justify";
        out = "<h3>Break-even</h3><p class=\"big\">" + Math.ceil(months) + " months</p>" + verdict(kind, label);
        if (net < 0) { out += "<p>The payment falls, but total interest rises because the term restarts. Consider a shorter new term.</p>"; }
      }
      return out + rows([["Current payment", money(cur)], ["New payment", money(neu)],
                         ["Monthly saving", (saving >= 0 ? "" : "−") + money(Math.abs(saving))], ["Closing costs", money(v.costs)],
                         ["Interest left on the current loan", money(curInterest)], ["Interest on the new loan", money(newInterest)],
                         ["Lifetime result after costs", (net >= 0 ? "Save " : "Pay ") + money(Math.abs(net)) + (net >= 0 ? "" : " more")]]);
    },

    "energy-cost": function (v) {
      if (!(v.rate > 0)) { return null; }
      var out = "", list = [];
      if (v.watts > 0 && v.hours > 0) {
        var kwhDay = v.watts * v.hours / 1000;
        out += "<h3>Running cost of one device</h3><p class=\"big\">" + money(kwhDay * v.rate * 365) + "<span class=\"big-unit\"> a year</span></p>";
        list.push(["Energy used per day", kwhDay.toFixed(2) + " kWh"], ["Cost per day", money(kwhDay * v.rate, true)],
                  ["Cost per month", money(kwhDay * v.rate * 30.4, true)]);
      }
      if (v.a_kwh > 0 && v.b_kwh > 0) {
        var a = v.a_kwh * v.rate, b = v.b_kwh * v.rate, years = v.years || 10;
        var aTotal = v.a_price + a * years, bTotal = v.b_price + b * years;
        list.push(["Model A, yearly running cost", money(a)], ["Model B, yearly running cost", money(b)],
                  ["Model A over " + years + " years, with price", money(aTotal)], ["Model B over " + years + " years, with price", money(bTotal)]);
        var cheapRun = a < b ? "A" : "B";
        var premium = cheapRun === "A" ? v.a_price - v.b_price : v.b_price - v.a_price;
        var yearly = Math.abs(a - b);
        if (premium > 0 && yearly > 0) {
          var pay = premium / yearly;
          list.push(["Payback on the efficient model", pay.toFixed(1) + " years"]);
          out += verdict(pay <= years ? "good" : "warn", pay <= years ? "Model " + cheapRun + " pays back its higher price in " + pay.toFixed(1) + " years"
            : "Model " + cheapRun + " does not pay back within " + years + " years");
        } else if (yearly > 0) {
          out += verdict("good", "Model " + cheapRun + " costs less to buy and to run");
        }
      }
      return list.length ? out + rows(list) : null;
    },

    "repair-or-replace": function (v) {
      if (!(v.repair > 0) || !(v.replace > 0) || !(v.life > 0)) { return null; }
      var ratio = v.repair / v.replace, used = Math.min(1.5, v.age / v.life), score = ratio + used;
      var kind, label;
      if (ratio >= 0.5) { kind = "bad"; label = "Replace: the repair costs half or more of a new one"; }
      else if (score >= 1) { kind = "warn"; label = "Lean towards replacing"; }
      else if (score >= 0.75) { kind = "ok"; label = "Close call: repair if it is otherwise reliable"; }
      else { kind = "good"; label = "Repair"; }
      var list = [["Repair as a share of replacement", pct(ratio * 100, 0)], ["Expected life already used", pct(used * 100, 0)],
                  ["Combined score (1.00 or more leans to replace)", score.toFixed(2)]];
      if (v.saving > 0) { list.push(["Years for energy savings to cover the extra cost of replacing", ((v.replace - v.repair) / v.saving).toFixed(1)]); }
      return "<h3>Verdict</h3>" + verdict(kind, label) + rows(list);
    },

    "paint": function (v) {
      if (!(v.len > 0) || !(v.wid > 0) || !(v.hei > 0) || !(v.coverage > 0)) { return null; }
      var walls = Math.max(0, 2 * (v.len + v.wid) * v.hei - v.doors * 21 - v.windows * 15);
      var ceiling = /^y/i.test(v.ceiling) ? v.len * v.wid : 0;
      var coats = v.coats || 1;
      var gallons = Math.ceil((walls + ceiling) * coats / v.coverage * 4) / 4;
      var whole = Math.floor(gallons), quarts = Math.round((gallons - whole) * 4);
      var buy = quarts >= 3 ? (whole + 1) + " gallons" : whole + " gallon" + (whole === 1 ? "" : "s") + (quarts ? " and " + quarts + " quart" + (quarts === 1 ? "" : "s") : "");
      if (whole === 0 && quarts < 3) { buy = quarts + " quart" + (quarts === 1 ? "" : "s"); }
      return "<h3>Paint needed</h3><p class=\"big\">" + gallons.toFixed(2) + "<span class=\"big-unit\"> gallons</span></p>" +
        rows([["Buy", buy], ["Wall area to paint", Math.round(walls) + " sq ft"], ["Ceiling area", Math.round(ceiling) + " sq ft"],
              ["Coats", String(coats)], ["Estimated paint cost", money(Math.ceil(gallons) * v.price)]]);
    },

    "flooring": function (v) {
      if (!(v.len > 0) || !(v.wid > 0)) { return null; }
      var area = v.len * v.wid, waste = firstNumber(v.waste) / 100, total = area * (1 + waste);
      var list = [["Room area", area.toFixed(0) + " sq ft"], ["With waste allowance", total.toFixed(0) + " sq ft"]];
      var ordered = total;
      if (v.box > 0) {
        var boxes = Math.ceil(total / v.box);
        ordered = boxes * v.box;
        list.push(["Boxes to order", boxes + " (" + ordered.toFixed(1) + " sq ft)"]);
      }
      var material = ordered * v.mat, labour = area * v.lab;
      list.push(["Material", money(material)], ["Installation", money(labour)]);
      return "<h3>Total cost</h3><p class=\"big\">" + money(material + labour) + "</p>" + rows(list);
    }
  };

  L.$$("form[data-tool]").forEach(function (form) {
    var slug = form.getAttribute("data-tool");
    var result = form.parentNode.querySelector("[data-result]");
    var fields = L.$$("[data-f]", form);
    var key = "hd-tool-" + slug;

    try {
      var saved = JSON.parse(L.store(key) || "null");
      if (saved) { fields.forEach(function (el) { var k = el.getAttribute("data-f"); if (saved[k] !== undefined) { el.value = saved[k]; } }); }
    } catch (e) { /* ignore unreadable saved inputs */ }

    function values() {
      var v = {}, raw = {};
      fields.forEach(function (el) {
        var k = el.getAttribute("data-f");
        raw[k] = el.value;
        v[k] = el.tagName === "SELECT" ? el.value : (parseFloat(el.value) || 0);
      });
      L.store(key, JSON.stringify(raw));
      return v;
    }
    function run() {
      var html = calc[slug] ? calc[slug](values()) : null;
      result.innerHTML = html || '<p class="result-empty">Enter the figures above to see a result.</p>';
    }
    if (slug === "repair-or-replace") {
      var type = form.querySelector('[data-f="type"]'), life = form.querySelector('[data-f="life"]');
      type.addEventListener("change", function () { var n = (HD.life || {})[type.value]; if (n) { life.value = n; } });
    }
    form.addEventListener("input", run);
    form.addEventListener("change", run);
    form.addEventListener("submit", function (ev) { ev.preventDefault(); run(); result.scrollIntoView({ block: "nearest", behavior: "smooth" }); });
    form.addEventListener("reset", function () { L.store(key, null); setTimeout(run, 0); });
    run();
  });
})();
