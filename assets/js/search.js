/* Home.Deals — on-site search over the generated index. */
(function () {
  "use strict";
  var L = window.HDlib;
  var input = document.getElementById("search-q");
  var out = document.getElementById("search-results");
  if (!L || !input || !out) { return; }
  var index = null;

  function esc(text) { var d = document.createElement("div"); d.textContent = text; return d.innerHTML; }

  function render(q) {
    var terms = q.toLowerCase().split(/\s+/).filter(function (t) { return t.length > 1; });
    if (!terms.length) { out.innerHTML = '<p class="search-count">Type a word or two to search every page.</p>'; return; }
    var hits = [];
    index.forEach(function (p) {
      var t = p.t.toLowerCase(), d = p.d.toLowerCase(), x = (p.x || "").toLowerCase(), score = 0;
      for (var i = 0; i < terms.length; i += 1) {
        var term = terms[i], s = 0;
        if (t.indexOf(term) > -1) { s += 6; }
        if (d.indexOf(term) > -1) { s += 3; }
        if (x.indexOf(term) > -1) { s += 1; }
        if (!s) { return; }
        score += s;
      }
      hits.push({ p: p, score: score });
    });
    hits.sort(function (a, b) { return b.score - a.score; });
    if (!hits.length) {
      out.innerHTML = '<p class="search-count">Nothing found for “' + esc(q) + '”. Try a single word, such as a product or a project.</p>';
      return;
    }
    out.innerHTML = '<p class="search-count">' + hits.length + (hits.length === 1 ? " page" : " pages") + " found.</p><ul class=\"rows\">" +
      hits.slice(0, 30).map(function (h) {
        return '<li class="row"><div class="row-main"><h3><a href="' + L.root + h.p.u + '">' + esc(h.p.t) + "</a></h3><p>" + esc(h.p.d) +
          '</p></div><span class="tagline">' + esc(h.p.s) + "</span></li>";
      }).join("") + "</ul>";
  }

  var q = new URLSearchParams(location.search).get("q") || "";
  input.value = q;
  fetch(L.root + "search-index.json").then(function (r) { return r.json(); }).then(function (data) {
    index = data;
    render(input.value);
    input.addEventListener("input", function () { render(input.value); });
  }).catch(function () {
    out.innerHTML = '<p class="search-count">Search could not load. Use the sitemap to browse every page.</p>';
  });
  var form = input.form;
  if (form) { form.addEventListener("submit", function (ev) { ev.preventDefault(); if (index) { render(input.value); } }); }
})();
