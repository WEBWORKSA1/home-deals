/* Home.Deals — site behaviour. No dependencies. */
(function () {
  "use strict";

  var HD = window.HD || {};
  var doc = document;
  var rootPath = doc.documentElement.getAttribute("data-root") || "./";

  function $(sel, ctx) { return (ctx || doc).querySelector(sel); }
  function $$(sel, ctx) { return Array.prototype.slice.call((ctx || doc).querySelectorAll(sel)); }
  function store(key, value) {
    try {
      if (value === undefined) { return window.localStorage.getItem(key); }
      if (value === null) { window.localStorage.removeItem(key); return null; }
      window.localStorage.setItem(key, value);
      return value;
    } catch (e) { return null; }
  }
  function money(n, cents) {
    if (!isFinite(n)) { return "—"; }
    return "$" + n.toLocaleString("en-US", { minimumFractionDigits: cents ? 2 : 0, maximumFractionDigits: cents ? 2 : 0 });
  }

  /* ---------- theme ---------- */
  var themeBtn = $("[data-theme-toggle]");
  if (themeBtn) {
    themeBtn.addEventListener("click", function () {
      var next = doc.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
      doc.documentElement.setAttribute("data-theme", next);
      store("hd-theme", next);
    });
  }

  /* ---------- navigation ---------- */
  var burger = $(".burger");
  var drawer = $("#drawer");
  if (burger && drawer) {
    burger.addEventListener("click", function () {
      var open = drawer.hidden;
      drawer.hidden = !open;
      burger.setAttribute("aria-expanded", String(open));
      burger.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    });
  }
  var more = $(".nav-more details");
  if (more) {
    doc.addEventListener("click", function (ev) { if (more.open && !more.contains(ev.target)) { more.open = false; } });
    doc.addEventListener("keydown", function (ev) { if (ev.key === "Escape" && more.open) { more.open = false; $("summary", more).focus(); } });
  }

  /* ---------- countdowns and the current month ---------- */
  function daysUntil(iso) {
    var p = iso.split("-");
    var target = new Date(+p[0], +p[1] - 1, +p[2]);
    var now = new Date();
    var today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    return Math.round((target - today) / 86400000);
  }
  $$("[data-count]").forEach(function (el) {
    var d = daysUntil(el.getAttribute("data-count"));
    var sentence = el.getAttribute("data-count-style") === "sentence";
    var text = "";
    if (d > 1) { text = sentence ? d + " days to go." : "in " + d + " days"; }
    else if (d === 1) { text = sentence ? "It is tomorrow." : "tomorrow"; }
    else if (d === 0) { text = sentence ? "It is today." : "today"; }
    else if (d >= -14) { text = sentence ? "" : "on now"; }
    el.textContent = text;
  });
  var months = $$(".month[data-month]");
  if (months.length) {
    var m = new Date().getMonth() + 1;
    months.forEach(function (el) { el.classList.toggle("is-now", +el.getAttribute("data-month") === m); });
  }

  /* ---------- video: load the YouTube player only on request ---------- */
  doc.addEventListener("click", function (ev) {
    var btn = ev.target.closest ? ev.target.closest("[data-yt]") : null;
    if (!btn) { return; }
    var id = btn.getAttribute("data-yt");
    if (!/^[\w-]{11}$/.test(id)) { return; }
    var frame = doc.createElement("iframe");
    frame.className = "video-frame";
    frame.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
    frame.title = (btn.getAttribute("aria-label") || "Video").replace(/^Play video: /, "");
    frame.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share";
    frame.allowFullscreen = true;
    frame.setAttribute("referrerpolicy", "strict-origin-when-cross-origin");
    btn.parentNode.replaceChild(frame, btn);
    frame.focus();
  });

  /* ---------- list filters ---------- */
  $$(".filter[data-filter]").forEach(function (bar) {
    var list = doc.getElementById(bar.getAttribute("data-filter"));
    if (!list) { return; }
    var items = Array.prototype.slice.call(list.children);
    var input = $("input[type=search]", bar);
    var count = $(".filter-count", bar);
    var kind = "all";
    function apply() {
      var q = (input && input.value || "").trim().toLowerCase();
      var shown = 0;
      items.forEach(function (el) {
        var ok = (kind === "all" || el.getAttribute("data-kind") === kind) &&
                 (!q || (el.getAttribute("data-text") || el.textContent.toLowerCase()).indexOf(q) > -1);
        el.hidden = !ok;
        if (ok) { shown += 1; }
      });
      if (count) { count.textContent = shown === items.length ? "" : (shown ? "Showing " + shown + " of " + items.length + "." : "Nothing matches. Try a shorter search or another filter."); }
    }
    $$(".pill[data-kind]", bar).forEach(function (pill) {
      pill.addEventListener("click", function () {
        kind = pill.getAttribute("data-kind");
        $$(".pill[data-kind]", bar).forEach(function (p) { var on = p === pill; p.classList.toggle("is-on", on); p.setAttribute("aria-pressed", String(on)); });
        apply();
      });
    });
    if (input) { input.addEventListener("input", apply); }
  });

  /* ---------- pane toggles (chart ranges) ---------- */
  $$("[data-toggle]").forEach(function (group) {
    var box = doc.getElementById(group.getAttribute("data-toggle"));
    if (!box) { return; }
    $$(".pill[data-show]", group).forEach(function (pill) {
      pill.addEventListener("click", function () {
        var show = pill.getAttribute("data-show");
        $$("[data-pane]", box).forEach(function (pane) { pane.hidden = pane.getAttribute("data-pane") !== show; });
        $$(".pill[data-show]", group).forEach(function (p) { var on = p === pill; p.classList.toggle("is-on", on); p.setAttribute("aria-pressed", String(on)); });
      });
    });
  });

  /* ---------- forms ---------- */
  function inbox() {
    var f = HD.form || {};
    if (f.a) { return f.a; }
    return (f.k || []).map(function (c, i) { return String.fromCharCode(c ^ (11 + (i % 7))); }).join("");
  }
  function send(payload) {
    payload._template = "table";
    payload._captcha = "false";
    payload.page = location.href.split("#")[0];
    return fetch("https://formsubmit.co/ajax/" + inbox(), {
      method: "POST",
      headers: { "Content-Type": "application/json", "Accept": "application/json" },
      body: JSON.stringify(payload)
    }).then(function (res) {
      return res.json().catch(function () { return {}; }).then(function (body) {
        return { ok: res.ok && String(body.success) !== "false", message: body.message || "" };
      });
    });
  }
  function fieldMessage(el) {
    var v = el.validity;
    if (v.valid) { return ""; }
    if (el.type === "checkbox") { return "Tick this box to continue."; }
    if (v.valueMissing) { return "This is needed."; }
    if (v.typeMismatch && el.type === "email") { return "Enter a full email address, like name@example.com."; }
    if (v.typeMismatch && el.type === "url") { return "Enter a full link starting with https://"; }
    if (v.patternMismatch && el.name === "zip") { return "Enter a 5-digit ZIP code."; }
    return "Check this entry.";
  }
  function validate(scope) {
    var firstBad = null;
    $$("input, select, textarea", scope).forEach(function (el) {
      if (el.name === "_honey" || el.disabled || el.type === "radio") { return; }
      var holder = el.closest(".field") || el.closest(".check") || el.parentNode;
      var old = holder.querySelector(".err");
      if (old) { old.parentNode.removeChild(old); }
      var msg = fieldMessage(el);
      el.classList.toggle("is-bad", !!msg);
      if (msg) {
        el.setAttribute("aria-invalid", "true");
        var note = doc.createElement("span");
        note.className = "err";
        note.textContent = msg;
        holder.appendChild(note);
        if (!firstBad) { firstBad = el; }
      } else { el.removeAttribute("aria-invalid"); }
    });
    if (firstBad) { firstBad.focus(); }
    return !firstBad;
  }
  function collect(form) {
    var out = {};
    $$("input, select, textarea", form).forEach(function (el) {
      if (!el.name || el.name === "_honey" || el.disabled) { return; }
      if ((el.type === "checkbox" || el.type === "radio") && !el.checked) { return; }
      var value = (el.value || "").trim();
      if (!value) { return; }
      out[el.name] = out[el.name] ? out[el.name] + ", " + value : value;
    });
    return out;
  }
  function failText(message) {
    if (/activat/i.test(message)) {
      return "This form is waiting for a one-time activation by the site owner, so your message was not delivered. Please use the contact page for now.";
    }
    return "That did not send. Check your connection and try again, or use the contact page.";
  }

  $$("form[data-form]").forEach(function (form) {
    if (form.classList.contains("wizard-form")) { return; }
    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var msg = $(".form-msg", form);
      var btn = $("button[type=submit]", form);
      if (!validate(form)) { return; }
      var honey = $("input[name=_honey]", form);
      var done = function () {
        var note = doc.createElement("p");
        note.className = "form-done";
        note.setAttribute("role", "status");
        note.tabIndex = -1;
        note.textContent = form.getAttribute("data-success") || "Sent.";
        form.parentNode.replaceChild(note, form);
        note.focus();
      };
      if (honey && honey.value) { done(); return; }
      var payload = collect(form);
      payload._subject = "[Home.Deals] " + (form.getAttribute("data-subject") || "Form") +
        (payload.email ? " from " + payload.email : "");
      var label = btn.textContent;
      btn.disabled = true;
      btn.textContent = "Sending…";
      msg.className = "form-msg";
      msg.textContent = "";
      send(payload).then(function (res) {
        if (res.ok) { done(); return; }
        throw new Error(res.message || "failed");
      }).catch(function (err) {
        btn.disabled = false;
        btn.textContent = label;
        msg.className = "form-msg is-bad";
        msg.textContent = failText(String(err && err.message || ""));
      });
    });
  });

  /* ---------- cookie notice ---------- */
  var cookie = $("[data-cookie]");
  if (cookie && store("hd-cookie-ok") !== "1") {
    cookie.hidden = false;
    $("[data-cookie-ok]", cookie).addEventListener("click", function () { cookie.hidden = true; store("hd-cookie-ok", "1"); });
  }

  window.HDlib = { $: $, $$: $$, store: store, money: money, send: send, validate: validate, failText: failText, root: rootPath };
})();
