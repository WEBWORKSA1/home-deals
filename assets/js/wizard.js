/* Home.Deals — quote request wizard. */
(function () {
  "use strict";
  var L = window.HDlib;
  if (!L) { return; }
  var $ = L.$, $$ = L.$$;

  $$("[data-wizard]").forEach(function (wizard) {
    var dataEl = $("#wizard-data", wizard);
    if (!dataEl) { return; }
    var data = JSON.parse(dataEl.textContent);
    var form = $("form", wizard);
    var steps = $$(".step", form);
    var dots = $$(".steps li", wizard);
    var byslug = {};
    data.services.forEach(function (s) { byslug[s.slug] = s; });
    var state = { step: 1 };

    function picked(name) {
      var el = $('input[name="' + name + '"]:checked', form);
      return el ? el.value : "";
    }
    function service() { return byslug[picked("service")] || null; }

    function roundNice(n) {
      if (n < 1000) { return Math.round(n / 50) * 50; }
      if (n < 10000) { return Math.round(n / 100) * 100; }
      return Math.round(n / 500) * 500;
    }
    function estimate() {
      var s = service();
      if (!s) { return null; }
      var a = s.q1.options[+picked("q1")];
      var b = s.q2.options[+picked("q2")];
      if (!a || !b) { return null; }
      var lo, hi;
      if (s.mode === "area") { lo = a[1] * b[1]; hi = a[2] * b[1]; }
      else { lo = a[1] * b[1]; hi = a[2] * b[1]; }
      return L.money(roundNice(lo)) + " to " + L.money(roundNice(hi));
    }

    function tiles(target, name, options) {
      target.innerHTML = "";
      options.forEach(function (opt, i) {
        var label = document.createElement("label");
        label.className = "tile tile-row";
        var input = document.createElement("input");
        input.type = "radio"; input.name = name; input.value = String(i);
        var span = document.createElement("span");
        span.className = "tile-in"; span.textContent = opt[0];
        label.appendChild(input); label.appendChild(span);
        target.appendChild(label);
      });
    }

    function prepareDetails() {
      var s = service();
      var q1 = $('[data-q="1"]', form), q2 = $('[data-q="2"]', form), other = $('[data-q="other"]', form);
      if (!s) {
        q1.hidden = true; q2.hidden = true; other.hidden = false;
        return;
      }
      other.hidden = true; q1.hidden = false; q2.hidden = false;
      if (q1.getAttribute("data-for") !== s.slug) {
        $(".q-label", q1).textContent = s.q1.label;
        $(".q-label", q2).textContent = s.q2.label;
        tiles($("[data-q1]", q1), "q1", s.q1.options);
        tiles($("[data-q2]", q2), "q2", s.q2.options);
        q1.setAttribute("data-for", s.slug);
      }
    }

    function showEstimate() {
      var text = estimate();
      var box = $("[data-estimate]", form), done = $("[data-estimate-done]", form);
      box.hidden = !text; done.hidden = !text;
      if (text) {
        $("[data-estimate-range]", form).textContent = text;
        $("[data-estimate-range-done]", form).textContent = text;
      }
    }

    function go(step, quiet) {
      state.step = step;
      steps.forEach(function (el) { el.classList.toggle("is-on", el.getAttribute("data-step") === String(step)); });
      var n = step === "done" ? 5 : step;
      dots.forEach(function (el, i) { el.classList.toggle("is-on", i < n); if (i === n - 1) { el.setAttribute("aria-current", "step"); } else { el.removeAttribute("aria-current"); } });
      if (step === 2) { prepareDetails(); }
      if (step === 3) { showEstimate(); }
      if (!quiet) {
        var current = $('.step[data-step="' + step + '"]', form);
        var target = $("legend, h3", current) || current;
        target.tabIndex = -1;
        target.focus({ preventScroll: true });
        var top = wizard.getBoundingClientRect().top;
        if (top < 70 || top > window.innerHeight * 0.6) { window.scrollTo({ top: window.scrollY + top - 84, behavior: "smooth" }); }
      }
    }

    function check(step) {
      var err = $('.step[data-step="' + step + '"] .step-err', form);
      var msg = "";
      if (step === 1 && !picked("service")) { msg = "Choose a project to continue."; }
      if (step === 2) {
        if (service()) { if (picked("q1") === "" || picked("q2") === "") { msg = "Answer both questions to continue."; } }
        else if (!$("#f-other", form).value.trim()) { msg = "Describe the project in a sentence or two."; }
      }
      if (step === 3 && (!picked("ownership") || !picked("timing"))) { msg = "Answer both questions to continue."; }
      err.textContent = msg;
      return !msg;
    }

    form.addEventListener("click", function (ev) {
      var next = ev.target.closest("[data-next]");
      var back = ev.target.closest("[data-back]");
      if (next && check(state.step)) { go(state.step + 1); }
      if (back) { go(state.step - 1); }
    });
    form.addEventListener("change", function (ev) {
      if (ev.target.name === "service") {
        var q1 = $('[data-q="1"]', form);
        if (q1) { q1.removeAttribute("data-for"); }
      }
      var err = $('.step.is-on .step-err', form);
      if (err) { err.textContent = ""; }
    });

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      if (state.step !== 4) { return; }
      var scope = $('.step[data-step="4"]', form);
      if (!L.validate(scope)) { return; }
      var msg = $(".form-msg", scope), btn = $("button[type=submit]", scope);
      var honey = $("input[name=_honey]", form);
      if (honey && honey.value) { go("done"); return; }
      var s = service();
      var val = function (name) { var el = form.elements[name]; return el && el.value ? el.value.trim() : ""; };
      var payload = {
        project: s ? s.name : "Something else",
        ballpark_shown: estimate() || "none",
        home_ownership: picked("ownership"),
        timing: picked("timing"),
        name: val("name"), zip: val("zip"), email: val("email"), phone: val("phone") || "not given",
        contact_preference: picked("contact_pref"),
        notes: val("notes") || "none",
        consent: "yes"
      };
      if (s) {
        payload[s.q1.label] = s.q1.options[+picked("q1")][0];
        payload[s.q2.label] = s.q2.options[+picked("q2")][0];
      } else { payload.description = val("project_description"); }
      payload._subject = "[Home.Deals] Quote request: " + payload.project + ", ZIP " + payload.zip;
      var label = btn.textContent;
      btn.disabled = true; btn.textContent = "Sending…";
      msg.className = "form-msg"; msg.textContent = "";
      L.send(payload).then(function (res) {
        if (!res.ok) { throw new Error(res.message || "failed"); }
        L.store("hd-quote", null);
        go("done");
      }).catch(function (err) {
        btn.disabled = false; btn.textContent = label;
        msg.className = "form-msg is-bad";
        msg.textContent = L.failText(String(err && err.message || ""));
      });
    });

    /* start: preselect from the page or from ?service=&zip= */
    var params = new URLSearchParams(location.search);
    var want = params.get("service") || data.preselect;
    var zip = params.get("zip");
    if (zip && /^\d{5}$/.test(zip)) { form.elements.zip.value = zip; }
    if (want && (byslug[want] || want === "other")) {
      var radio = $('input[name="service"][value="' + want + '"]', form);
      if (radio) { radio.checked = true; go(2, true); }
    }
  });
})();
