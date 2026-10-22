/*
 * "What would AI say?" tool for /win-chat/.
 *
 * Plain JS, no dependencies, no build step. Mounts into #ss-ai-say.
 *
 * Data access goes through ONE adapter object so the mocked fixture can be
 * swapped for the real Worker later:
 *
 *   window.SS_AI_SAY_ADAPTER = {
 *     mode: "live",                       // "mock" shows the preview badge
 *     provider: "the answer engine",      // named in the privacy line
 *     ask: function (payload) {...},      // -> Promise<result>, rejects with {status, retry_after}
 *     get: function (id, params) {...}    // -> Promise<result> for a share link
 *   };
 *
 * `payload` is {query, brand, store_url}. `result` follows the API contract in
 * the tool spec (id, share_url, engine, checked_at, summary, brands, sources,
 * stats, store_check, disclaimer). When no adapter is defined before this
 * script runs, the mock adapter below is used. It reads window.SS_AI_SAY_FIXTURES
 * from tool-fixtures.js and never touches the network.
 */
(function () {
  "use strict";

  var mount = document.getElementById("ss-ai-say");
  if (!mount || mount.dataset.ready) return;
  mount.dataset.ready = "1";

  var AUDIT_HREF = "mailto:marin@soulstone.co?subject=AI%20visibility%20audit";
  var DISCLAIMER = "This is one AI answer from one engine at one moment. Real assistants vary by user, location and time.";
  var CHIPS = ["refillable hand soap", "collagen face cream", "luxury candle gift"];
  var LIMITS = { queryMin: 3, queryMax: 200, brandMax: 60 };
  var PROGRESS = [
    "Asking the engine your question",
    "Reading the pages it cites",
    "Counting the brands it names",
    "Checking your store",
    "Nearly there"
  ];

  /* ------------------------------------------------------------------ */
  /* Mock adapter (MOCKED DATA ONLY, replaced by the Worker later)       */
  /* ------------------------------------------------------------------ */

  function mockAdapter() {
    var fx = window.SS_AI_SAY_FIXTURES;

    function wait(ms) {
      return new Promise(function (resolve) { setTimeout(resolve, ms); });
    }

    function hostOf(url) {
      try { return new URL(url).hostname.replace(/^www\./, "").toLowerCase(); } catch (e) { return ""; }
    }

    function build(scenario, payload) {
      var brand = (payload.brand || "").trim();
      var brands = scenario.brands.map(function (b) { return { name: b.name, rank: b.rank }; });
      var match = null;
      brands.forEach(function (b) {
        if (brand && b.name.toLowerCase() === brand.toLowerCase()) match = b;
      });
      var own = hostOf(payload.store_url || "");
      var counts = {};
      var order = [];
      scenario.sources.forEach(function (s) {
        if (!counts[s.domain]) { counts[s.domain] = 0; order.push(s.domain); }
        counts[s.domain] += 1;
      });
      var top = order.slice().sort(function (a, b) {
        return counts[b] - counts[a] || order.indexOf(a) - order.indexOf(b);
      }).slice(0, 3);
      var ownCited = !!own && scenario.sources.some(function (s) {
        return s.domain === own || s.domain.slice(-(own.length + 1)) === "." + own;
      });
      var page = location.origin + location.pathname;
      var share = page + "?result=" + encodeURIComponent(scenario.id);
      if (brand) share += "&brand=" + encodeURIComponent(brand);
      if (payload.store_url) share += "&store=" + encodeURIComponent(payload.store_url);
      return {
        id: scenario.id,
        share_url: share,
        engine: fx.engine,
        checked_at: new Date().toISOString(),
        cached: false,
        query: payload.query,
        brand: brand || null,
        store_url: payload.store_url || null,
        summary: scenario.summary,
        brands: brands,
        sources: scenario.sources.map(function (s) { return { url: s.url, domain: s.domain }; }),
        stats: {
          brand_mentioned: !!match,
          brand_rank: match ? match.rank : null,
          source_count: scenario.sources.length,
          top_domains: top,
          own_domain_cited: ownCited
        },
        store_check: payload.store_url ? scenario.store_check : null,
        disclaimer: "Estimate. One AI answer from one engine at one moment."
      };
    }

    return {
      mode: "mock",
      provider: "the answer engine",
      ask: function (payload) {
        if (!fx) return Promise.reject({ status: 0 });
        var err = fx.error(payload.query);
        return wait(fx.delay_ms).then(function () {
          if (err) throw { status: err.status, retry_after: err.body && err.body.retry_after };
          return build(fx.pick(payload.query), payload);
        });
      },
      get: function (id, params) {
        if (!fx) return Promise.reject({ status: 0 });
        var found = null;
        Object.keys(fx.scenarios).forEach(function (k) {
          if (fx.scenarios[k].id === id) found = fx.scenarios[k];
        });
        return wait(600).then(function () {
          if (!found) throw { status: 404 };
          var query = { "r_mock_soap": "best refillable hand soap Netherlands", "r_mock_cream": "collagen face cream", "r_mock_candle": "luxury candle gift" }[id] || "your shopping question";
          return build(found, { query: query, brand: params.brand || "", store_url: params.store_url || "" });
        });
      }
    };
  }

  var adapter = window.SS_AI_SAY_ADAPTER || mockAdapter();

  /* ------------------------------------------------------------------ */
  /* Helpers                                                              */
  /* ------------------------------------------------------------------ */

  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function el(tag, attrs, html) {
    var n = document.createElement(tag);
    if (attrs) Object.keys(attrs).forEach(function (k) { n.setAttribute(k, attrs[k]); });
    if (html != null) n.innerHTML = html;
    return n;
  }

  function fmtDate(iso) {
    var d = new Date(iso);
    if (isNaN(d.getTime())) return "";
    return d.toLocaleDateString("en-GB", { day: "numeric", month: "short", year: "numeric" });
  }

  function reducedMotion() {
    return window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function isPublicHost(host) {
    host = host.toLowerCase();
    if (!host || host === "localhost" || host.slice(-6) === ".local" || host.indexOf(".") === -1) return false;
    if (/^\d{1,3}(\.\d{1,3}){3}$/.test(host) || host.indexOf(":") !== -1 || host.charAt(0) === "[") return false;
    return true;
  }

  function validate(values) {
    var errors = {};
    var q = values.query.trim();
    if (q.length < LIMITS.queryMin) errors.query = "Type at least three characters.";
    else if (q.length > LIMITS.queryMax) errors.query = "Keep it under 200 characters.";
    if (values.brand.trim().length > LIMITS.brandMax) errors.brand = "Keep the brand name under 60 characters.";
    var u = values.store_url.trim();
    if (u) {
      var parsed = null;
      try { parsed = new URL(u.indexOf("://") === -1 ? "https://" + u : u); } catch (e) { parsed = null; }
      if (!parsed || parsed.protocol !== "https:") errors.store_url = "Use a full https address, for example https://yourstore.com.";
      else if (!isPublicHost(parsed.hostname)) errors.store_url = "Use a public store address.";
      else values.store_url = parsed.origin + (parsed.pathname === "/" ? "" : parsed.pathname);
    } else {
      values.store_url = "";
    }
    values.query = q;
    values.brand = values.brand.trim();
    return errors;
  }

  function colorVar(name, fallback) {
    var raw = getComputedStyle(mount).getPropertyValue(name).trim();
    if (!raw) return fallback;
    var probe = document.createElement("canvas").getContext("2d");
    probe.fillStyle = "#010203";
    probe.fillStyle = raw;
    return probe.fillStyle === "#010203" ? fallback : probe.fillStyle;
  }

  /* ------------------------------------------------------------------ */
  /* Markup                                                              */
  /* ------------------------------------------------------------------ */

  var isMock = adapter.mode === "mock";
  var privacyLive = "We store your query and result for 90 days so share links work. We keep a hashed version of your IP address for 24 hours to stop abuse. We send your query to " + esc(adapter.provider || "the answer engine") + " to generate the answer. We do not store names or emails unless you book an audit.";
  var privacyMock = "Preview build. Answers come from a small set of sample results stored in this page. Nothing you type is sent or stored anywhere.";

  mount.className = "ss-ais";
  mount.innerHTML =
    '<div class="ss-ais-inner">' +
      '<div class="ss-ais-head">' +
        '<div>' +
          '<p class="ss-ais-eyebrow">Try it</p>' +
          '<h2 class="ss-ais-title" id="ss-ais-title">What would AI say?</h2>' +
          '<p class="ss-ais-lede">Type a question a shopper might ask an AI assistant. We show what the answer would most likely say, which brands it names and which sites it leans on. Add your brand to see whether you are in it.</p>' +
          (isMock ? '<p class="ss-ais-badge">Preview · sample answers</p>' : "") +
        '</div>' +
        '<div>' +
          '<form class="ss-ais-card" id="ss-ais-form" novalidate aria-labelledby="ss-ais-title">' +
            '<span class="ss-ais-rule" aria-hidden="true"></span>' +
            '<div class="ss-ais-form">' +
              '<div class="ss-ais-field">' +
                '<label class="ss-ais-label" for="ss-ais-query"><b>Shopping question</b><span class="ss-ais-count" id="ss-ais-count" aria-hidden="true">0 / 200</span></label>' +
                '<input class="ss-ais-input" id="ss-ais-query" name="query" type="text" maxlength="200" autocomplete="off" spellcheck="true" placeholder="best refillable hand soap Netherlands" aria-describedby="ss-ais-query-hint ss-ais-query-error" required>' +
                '<p class="ss-ais-hint" id="ss-ais-query-hint">Three to 200 characters. Try one of these:</p>' +
                '<ul class="ss-ais-chips" aria-label="Example questions">' +
                  CHIPS.map(function (c) { return '<li><button type="button" class="ss-ais-chip" data-chip="' + esc(c) + '">' + esc(c) + '</button></li>'; }).join("") +
                '</ul>' +
                '<p class="ss-ais-error-text" id="ss-ais-query-error" aria-live="polite"></p>' +
              '</div>' +
              '<div class="ss-ais-row">' +
                '<div class="ss-ais-field">' +
                  '<label class="ss-ais-label" for="ss-ais-brand"><b>Your brand</b><span class="ss-ais-opt">optional</span></label>' +
                  '<input class="ss-ais-input" id="ss-ais-brand" name="brand" type="text" maxlength="60" autocomplete="organization" placeholder="Brand name" aria-describedby="ss-ais-brand-error">' +
                  '<p class="ss-ais-error-text" id="ss-ais-brand-error" aria-live="polite"></p>' +
                '</div>' +
                '<div class="ss-ais-field">' +
                  '<label class="ss-ais-label" for="ss-ais-store"><b>Store URL</b><span class="ss-ais-opt">optional</span></label>' +
                  '<input class="ss-ais-input" id="ss-ais-store" name="store_url" type="url" inputmode="url" autocomplete="url" placeholder="https://yourstore.com" aria-describedby="ss-ais-store-hint ss-ais-store-error">' +
                  '<p class="ss-ais-hint" id="ss-ais-store-hint">Adds a quick check of your product data and AI crawler access.</p>' +
                  '<p class="ss-ais-error-text" id="ss-ais-store-error" aria-live="polite"></p>' +
                '</div>' +
              '</div>' +
              '<div class="ss-ais-actions">' +
                '<button type="submit" class="ss-ais-btn" id="ss-ais-submit">See what AI would say</button>' +
                '<span class="ss-ais-hint" id="ss-ais-time">Takes about ten seconds.</span>' +
              '</div>' +
            '</div>' +
            '<p class="ss-ais-privacy">' + (isMock ? privacyMock : privacyLive) + ' <a href="/privacy/">Privacy</a></p>' +
          '</form>' +
          '<div class="ss-ais-loading" id="ss-ais-loading" hidden>' +
            '<div class="ss-ais-progress" aria-hidden="true"><span></span></div>' +
            '<p class="ss-ais-status" id="ss-ais-status" role="status" aria-live="polite"></p>' +
          '</div>' +
          '<div class="ss-ais-notice" id="ss-ais-notice" role="alert" hidden></div>' +
        '</div>' +
      '</div>' +
      '<div class="ss-ais-result" id="ss-ais-result" aria-live="polite" aria-labelledby="ss-ais-result-title" role="region" hidden></div>' +
    '</div>';

  var form = mount.querySelector("#ss-ais-form");
  var queryInput = mount.querySelector("#ss-ais-query");
  var brandInput = mount.querySelector("#ss-ais-brand");
  var storeInput = mount.querySelector("#ss-ais-store");
  var count = mount.querySelector("#ss-ais-count");
  var submit = mount.querySelector("#ss-ais-submit");
  var loading = mount.querySelector("#ss-ais-loading");
  var status = mount.querySelector("#ss-ais-status");
  var notice = mount.querySelector("#ss-ais-notice");
  var result = mount.querySelector("#ss-ais-result");
  var progressTimer = null;
  var imageUrl = null;

  function updateCount() {
    count.textContent = queryInput.value.length + " / " + LIMITS.queryMax;
  }
  queryInput.addEventListener("input", updateCount);
  updateCount();

  mount.addEventListener("click", function (e) {
    var chip = e.target.closest("[data-chip]");
    if (chip) {
      queryInput.value = chip.getAttribute("data-chip");
      updateCount();
      setError(queryInput, "");
      queryInput.focus();
    }
  });

  function setError(input, msg) {
    var p = mount.querySelector("#" + input.id + "-error");
    p.textContent = msg;
    if (msg) input.setAttribute("aria-invalid", "true"); else input.removeAttribute("aria-invalid");
  }

  /* ------------------------------------------------------------------ */
  /* States                                                              */
  /* ------------------------------------------------------------------ */

  function showLoading() {
    notice.hidden = true;
    result.hidden = true;
    submit.disabled = true;
    submit.textContent = "Asking";
    loading.hidden = false;
    var i = 0;
    status.innerHTML = esc(PROGRESS[0]) + "<small>Usually about ten seconds. Stay on this page.</small>";
    clearInterval(progressTimer);
    progressTimer = setInterval(function () {
      i = Math.min(i + 1, PROGRESS.length - 1);
      status.firstChild.nodeValue = PROGRESS[i];
    }, 2200);
  }

  function stopLoading() {
    clearInterval(progressTimer);
    loading.hidden = true;
    submit.disabled = false;
    submit.textContent = "See what AI would say";
  }

  function showNotice(err) {
    var title, body;
    var s = err && err.status;
    if (s === 429) {
      var mins = err.retry_after ? Math.max(1, Math.round(err.retry_after / 60)) : null;
      title = "You have asked a few times already.";
      body = "The tool allows five checks an hour and fifteen a day so it stays free for everyone. " + (mins ? "Try again in about " + mins + " minute" + (mins === 1 ? "" : "s") + "." : "Try again a little later.") + " If you want the full set of questions for your category, book an audit and we will run them for you.";
    } else if (s === 503) {
      title = "The tool is resting for today.";
      body = "We cap how many checks run each day. It is back tomorrow. If you want to know where you stand now, book an audit instead.";
    } else if (s === 404) {
      title = "That result has expired.";
      body = "Share links are kept for 90 days. Ask the question again to get a fresh answer.";
    } else {
      title = "We could not get an answer.";
      body = "Something went wrong on our side and nothing was stored. Try again in a moment, or book an audit and we will run the check for you.";
    }
    notice.innerHTML =
      '<h3>' + esc(title) + '</h3><p>' + esc(body) + '</p>' +
      '<div class="ss-ais-actions"><a class="ss-ais-btn" href="' + AUDIT_HREF + '">Book an AI visibility audit</a>' +
      (s === 503 ? "" : '<button type="button" class="ss-ais-btn ss-ais-btn-ghost" data-retry>Try again</button>') + '</div>';
    notice.hidden = false;
    notice.querySelector("h3").setAttribute("tabindex", "-1");
    notice.querySelector("h3").focus({ preventScroll: true });
  }

  notice.addEventListener("click", function (e) {
    if (e.target.closest("[data-retry]")) {
      notice.hidden = true;
      queryInput.focus();
    }
  });

  /* ------------------------------------------------------------------ */
  /* Result card                                                         */
  /* ------------------------------------------------------------------ */

  function favicon(domain) {
    var letter = domain.replace(/^www\./, "").charAt(0) || "?";
    return '<span class="ss-ais-favicon" aria-hidden="true">' + esc(letter) + '</span>';
  }

  function pathOf(url) {
    try { var u = new URL(url); return u.pathname.length > 1 ? u.pathname : ""; } catch (e) { return ""; }
  }

  function hostOf(url) {
    try { return new URL(url).hostname.replace(/^www\./, "").toLowerCase(); } catch (e) { return ""; }
  }

  function stat(label, value, sub, good) {
    return '<div class="ss-ais-stat' + (good ? " is-good" : "") + '"><dt>' + esc(label) + '</dt><dd>' + esc(value) + (sub ? '<small>' + esc(sub) + '</small>' : "") + '</dd></div>';
  }

  function renderResult(r) {
    var st = r.stats || {};
    var brand = r.brand || "";
    var own = hostOf(r.store_url || "");
    var total = r.brands.length;

    var tiles =
      brand
        ? stat("Your brand", st.brand_mentioned ? "Named" : "Not named", st.brand_mentioned ? brand + " is in the answer" : brand + " is missing", st.brand_mentioned)
        : stat("Your brand", "Not given", "Add a brand name to check");
    tiles += brand && st.brand_mentioned
      ? stat("Rank", st.brand_rank + " of " + total, "Among brands named", st.brand_rank === 1)
      : stat("Brands named", String(total), total ? "First is " + r.brands[0].name : "");
    tiles += stat("Sources cited", String(st.source_count), (st.top_domains || []).length ? "Most from " + st.top_domains[0] : "");
    tiles += r.store_url
      ? stat("Your domain", st.own_domain_cited ? "Cited" : "Not cited", own, st.own_domain_cited)
      : stat("Your domain", "Not given", "Add a store URL to check");

    var brands = r.brands.map(function (b) {
      var you = brand && b.name.toLowerCase() === brand.toLowerCase();
      return '<li class="ss-ais-brand' + (you ? " is-you" : "") + '"><span class="ss-ais-rank" aria-hidden="true">' + b.rank + '</span><span class="ss-ais-brand-name">' + esc(b.name) + '</span>' + (you ? '<span class="ss-ais-you">You</span>' : "") + '</li>';
    }).join("");

    var sources = r.sources.map(function (s) {
      var you = own && (s.domain === own || s.domain.slice(-(own.length + 1)) === "." + own);
      var p = pathOf(s.url);
      return '<li><a class="ss-ais-source' + (you ? " is-you" : "") + '" href="' + esc(s.url) + '" target="_blank" rel="noopener nofollow">' + favicon(s.domain) + '<span class="ss-ais-source-domain">' + esc(s.domain) + (p ? '<span class="ss-ais-source-path">' + esc(p) + '</span>' : "") + '</span>' + (you ? '<span class="ss-ais-you">You</span>' : "") + '</a></li>';
    }).join("");

    var domains = (st.top_domains || []).map(function (d) { return '<li>' + esc(d) + '</li>'; }).join("");

    var checks = "";
    if (r.store_check) {
      var items = [
        ["jsonld_product", "Product data AI can read", "JSON-LD Product with price and availability"],
        ["jsonld_organization", "Brand data AI can read", "JSON-LD Organization"],
        ["llms_txt", "llms.txt file", "A short guide to your store for AI crawlers"],
        ["ai_crawlers_allowed", "AI crawlers allowed", "robots.txt lets GPTBot, PerplexityBot, Google-Extended and ClaudeBot in"]
      ];
      checks = '<ul class="ss-ais-checks">' + items.map(function (it) {
        var ok = !!r.store_check[it[0]];
        return '<li class="ss-ais-check ' + (ok ? "is-ok" : "is-missing") + '"><span class="ss-ais-check-mark" aria-hidden="true">' + (ok ? "&#10003;" : "&#10005;") + '</span><span><span class="ss-ais-sr">' + (ok ? "Present: " : "Missing: ") + '</span>' + esc(it[1]) + '<small>' + esc(it[2]) + '</small></span></li>';
      }).join("") + '</ul>';
    } else {
      checks = '<p class="ss-ais-hint" style="margin-top:1rem">Add your store URL above and ask again to check your product data, llms.txt and AI crawler access.</p>';
    }

    result.innerHTML =
      '<div class="ss-ais-result-head">' +
        '<div><h3 id="ss-ais-result-title">What AI would likely say about <q>' + esc(r.query) + '</q></h3></div>' +
        '<p class="ss-ais-meta">Engine: ' + esc(r.engine) + ' · Checked ' + esc(fmtDate(r.checked_at)) + ' · Estimate</p>' +
      '</div>' +
      '<div class="ss-ais-block ss-ais-span"><h4>At a glance</h4><dl class="ss-ais-stats">' + tiles + '</dl></div>' +
      '<div class="ss-ais-grid">' +
        '<div class="ss-ais-block ss-ais-span"><h4>Likely answer</h4><p class="ss-ais-summary">' + esc(r.summary) + '</p></div>' +
        '<div class="ss-ais-block ss-ais-left"><h4>Brands named, in order</h4><ol class="ss-ais-list">' + brands + '</ol></div>' +
        '<div class="ss-ais-block"><h4>Sources cited</h4><ul class="ss-ais-list">' + sources + '</ul>' + (domains ? '<h4 style="margin-top:1.5rem">Most cited domains</h4><ul class="ss-ais-domains">' + domains + '</ul>' : "") + '</div>' +
        '<div class="ss-ais-block ss-ais-span"><h4>Store check' + (own ? " · " + esc(own) : "") + '</h4>' + checks + '</div>' +
      '</div>' +
      '<div class="ss-ais-share" id="ss-ais-share">' +
        '<h4>Share this result</h4>' +
        '<div class="ss-ais-share-row">' +
          '<button type="button" class="ss-ais-share-btn" data-share="copy">' + icon("link") + 'Copy link</button>' +
          '<a class="ss-ais-share-btn" href="https://www.linkedin.com/sharing/share-offsite/?url=' + encodeURIComponent(r.share_url) + '" target="_blank" rel="noopener">' + icon("linkedin") + 'LinkedIn</a>' +
          '<a class="ss-ais-share-btn" href="https://x.com/intent/post?text=' + encodeURIComponent(shareText(r)) + '&url=' + encodeURIComponent(r.share_url) + '" target="_blank" rel="noopener">' + icon("x") + 'X</a>' +
          (navigator.share ? '<button type="button" class="ss-ais-share-btn" data-share="native">' + icon("share") + 'Share</button>' : "") +
          '<a class="ss-ais-share-btn" data-share="download" href="#" download="what-would-ai-say-' + esc(r.id) + '.png" aria-disabled="true">' + icon("image") + 'Download image</a>' +
        '</div>' +
        '<p class="ss-ais-share-link"><a href="' + esc(r.share_url) + '">' + esc(r.share_url) + '</a></p>' +
        '<p class="ss-ais-sr" role="status" aria-live="polite" id="ss-ais-share-status"></p>' +
        '<img class="ss-ais-share-img" id="ss-ais-share-img" alt="Share card: what AI would say about ' + esc(r.query) + '" width="1200" height="630" hidden>' +
        '<p class="ss-ais-share-note">The image is drawn in your browser from this result, 1200 by 630 pixels, ready for LinkedIn or X.</p>' +
      '</div>' +
      '<p class="ss-ais-disclaimer"><b>Estimate.</b> ' + esc(DISCLAIMER) + '</p>' +
      '<div class="ss-ais-cta"><p>Want the full picture across the questions your buyers ask?</p><a class="ss-ais-btn" href="' + AUDIT_HREF + '">Book an AI visibility audit</a></div>';

    result.hidden = false;
    result.scrollIntoView({ behavior: reducedMotion() ? "auto" : "smooth", block: "start" });

    drawShareImage(r).then(function (blob) {
      if (imageUrl) URL.revokeObjectURL(imageUrl);
      imageUrl = URL.createObjectURL(blob);
      var img = result.querySelector("#ss-ais-share-img");
      var dl = result.querySelector('[data-share="download"]');
      img.src = imageUrl;
      img.hidden = false;
      dl.href = imageUrl;
      dl.removeAttribute("aria-disabled");
      dl.dataset.blobReady = "1";
      result.__shareBlob = blob;
    }).catch(function () {
      var dl = result.querySelector('[data-share="download"]');
      if (dl) dl.remove();
    });
  }

  function shareText(r) {
    var t = "What would AI say about \"" + r.query + "\"? ";
    if (r.brand) t += r.stats.brand_mentioned ? r.brand + " is named at number " + r.stats.brand_rank + ". " : r.brand + " is not in the answer. ";
    t += r.brands.length + " brands and " + r.stats.source_count + " sources. Check your own on soulstone.co.";
    return t;
  }

  function icon(name) {
    var paths = {
      link: '<path d="M10 14a3.5 3.5 0 0 0 5 0l4-4a3.5 3.5 0 0 0-5-5l-1 1"/><path d="M14 10a3.5 3.5 0 0 0-5 0l-4 4a3.5 3.5 0 0 0 5 5l1-1"/>',
      linkedin: '<path d="M6 9v12M6 5v.01M11 21v-7a3 3 0 0 1 6 0v7M11 9v12"/>',
      x: '<path d="M4 4l16 16M20 4L4 20"/>',
      share: '<path d="M12 3v12M8 7l4-4 4 4M5 13v6a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-6"/>',
      image: '<rect x="3" y="5" width="18" height="14" rx="1.5"/><path d="M3 16l5-5 4 4 3-3 6 6"/><circle cx="16" cy="9" r="1.5"/>'
    };
    return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">' + paths[name] + '</svg>';
  }

  result.addEventListener("click", function (e) {
    var btn = e.target.closest("[data-share]");
    if (!btn) return;
    var kind = btn.getAttribute("data-share");
    var say = result.querySelector("#ss-ais-share-status");
    var link = result.querySelector(".ss-ais-share-link a");
    if (kind === "copy") {
      var url = link ? link.getAttribute("href") : location.href;
      var done = function () { say.textContent = "Link copied."; btn.lastChild.nodeValue = "Copied"; setTimeout(function () { btn.lastChild.nodeValue = "Copy link"; }, 2000); };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(url).then(done, function () { fallbackCopy(url); done(); });
      } else { fallbackCopy(url); done(); }
    } else if (kind === "native") {
      var data = { title: "What would AI say?", text: shareText(result.__current), url: result.__current.share_url };
      if (result.__shareBlob && navigator.canShare) {
        var file = new File([result.__shareBlob], "what-would-ai-say.png", { type: "image/png" });
        if (navigator.canShare({ files: [file] })) data.files = [file];
      }
      navigator.share(data).catch(function () {});
    } else if (kind === "download" && !btn.dataset.blobReady) {
      e.preventDefault();
      say.textContent = "The image is still being drawn. Try again in a moment.";
    }
  });

  function fallbackCopy(text) {
    var ta = document.createElement("textarea");
    ta.value = text;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.opacity = "0";
    document.body.appendChild(ta);
    ta.select();
    try { document.execCommand("copy"); } catch (e) {}
    document.body.removeChild(ta);
  }

  /* ------------------------------------------------------------------ */
  /* Share image, drawn client side on a canvas                         */
  /* ------------------------------------------------------------------ */

  function wrapText(ctx, text, maxWidth, maxLines) {
    var words = text.split(/\s+/);
    var lines = [];
    var line = "";
    for (var i = 0; i < words.length; i++) {
      var test = line ? line + " " + words[i] : words[i];
      if (ctx.measureText(test).width > maxWidth && line) {
        lines.push(line);
        line = words[i];
        if (lines.length === maxLines) break;
      } else {
        line = test;
      }
    }
    if (lines.length < maxLines && line) lines.push(line);
    else if (lines.length === maxLines && (line || i < words.length)) {
      var last = lines[maxLines - 1];
      while (ctx.measureText(last + "...").width > maxWidth && last.length > 1) last = last.slice(0, -1).replace(/\s+$/, "");
      lines[maxLines - 1] = last + "...";
    }
    return lines;
  }

  function drawShareImage(r) {
    var W = 1200, H = 630;
    var bg = colorVar("--ploy-background-primary", "#080f0c");
    var panel = colorVar("--ploy-neutral-primary-s2", "#111916");
    var text = colorVar("--ploy-text-primary", "#eef3ef");
    var muted = colorVar("--ploy-text-secondary", "#a0afa6");
    var accent = colorVar("--ploy-accent-primary", "#59ec85");
    var heading = '"Playfair Display Variable", "Playfair Display", Georgia, serif';
    var body = '"Manrope Variable", Manrope, system-ui, sans-serif';
    var mono = '"JetBrains Mono Variable", "JetBrains Mono", ui-monospace, monospace';

    var ready = document.fonts && document.fonts.load
      ? Promise.all([document.fonts.load("400 56px " + heading), document.fonts.load("500 20px " + body), document.fonts.load("500 20px " + mono)]).catch(function () {})
      : Promise.resolve();

    return ready.then(function () {
      var canvas = document.createElement("canvas");
      canvas.width = W;
      canvas.height = H;
      var ctx = canvas.getContext("2d");

      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, W, H);
      var glow = ctx.createRadialGradient(W - 160, 120, 0, W - 160, 120, 520);
      glow.addColorStop(0, "rgba(80,220,140,0.22)");
      glow.addColorStop(1, "rgba(80,220,140,0)");
      ctx.fillStyle = glow;
      ctx.fillRect(0, 0, W, H);
      ctx.strokeStyle = "rgba(255,255,255,0.12)";
      ctx.lineWidth = 2;
      ctx.strokeRect(1, 1, W - 2, H - 2);

      ctx.fillStyle = accent;
      ctx.fillRect(72, 72, 56, 2);
      ctx.font = "500 18px " + mono;
      ctx.textBaseline = "alphabetic";
      ctx.fillText(("What would AI say?  ·  soulstone.co/win-chat").toUpperCase(), 72, 116);

      ctx.fillStyle = text;
      ctx.font = "400 54px " + heading;
      var lines = wrapText(ctx, "\u201C" + r.query + "\u201D", W - 144, 2);
      var y = 190;
      lines.forEach(function (l) { ctx.fillText(l, 72, y); y += 64; });

      var st = r.stats || {};
      var tiles = [];
      if (r.brand) tiles.push([r.brand.length > 18 ? "Your brand" : r.brand, st.brand_mentioned ? "Named" : "Not named", !!st.brand_mentioned]);
      else tiles.push(["Brands named", String(r.brands.length), false]);
      if (r.brand && st.brand_mentioned) tiles.push(["Rank", st.brand_rank + " of " + r.brands.length, st.brand_rank === 1]);
      else tiles.push(["First named", r.brands.length ? r.brands[0].name : "None", false]);
      tiles.push(["Sources cited", String(st.source_count), false]);
      tiles.push(["Most cited", (st.top_domains || [])[0] || "None", false]);

      var footerLine = H - 86;
      var brandsY = footerLine - 34;
      var top = y + 40;
      var gap = 20, tw = (W - 144 - gap * 3) / 4, th = Math.min(168, brandsY - 56 - top);
      tiles.forEach(function (t, i) {
        var x = 72 + i * (tw + gap);
        ctx.fillStyle = panel;
        ctx.fillRect(x, top, tw, th);
        ctx.strokeStyle = t[2] ? accent : "rgba(255,255,255,0.14)";
        ctx.lineWidth = 1.5;
        ctx.strokeRect(x + 0.75, top + 0.75, tw - 1.5, th - 1.5);
        ctx.fillStyle = muted;
        ctx.font = "500 15px " + mono;
        ctx.fillText(t[0].toUpperCase(), x + 24, top + 32);
        ctx.fillStyle = t[2] ? accent : text;
        var size = Math.min(40, Math.round(th * 0.34));
        var family = heading;
        ctx.font = "400 " + size + "px " + family;
        if (ctx.measureText(t[1]).width > tw - 48) {
          family = mono;
          size = 20;
          ctx.font = "500 " + size + "px " + family;
          while (ctx.measureText(t[1]).width > tw - 48 && size > 13) { size -= 1; ctx.font = "500 " + size + "px " + family; }
        }
        ctx.fillText(t[1], x + 24, top + th - 30);
      });

      ctx.fillStyle = muted;
      ctx.font = "500 20px " + body;
      var named = "Brands named: " + r.brands.map(function (b) { return b.name; }).join(", ");
      ctx.fillText(wrapText(ctx, named, W - 144, 1)[0], 72, brandsY);

      ctx.fillStyle = "rgba(255,255,255,0.12)";
      ctx.fillRect(72, footerLine, W - 144, 1);
      ctx.fillStyle = muted;
      ctx.font = "500 15px " + mono;
      ctx.fillText(("Estimate. One AI answer from one engine at one moment. " + fmtDate(r.checked_at)).toUpperCase(), 72, H - 46);
      ctx.fillStyle = text;
      ctx.font = "400 26px " + heading;
      ctx.textAlign = "right";
      ctx.fillText("Soulstone", W - 72, H - 42);
      ctx.textAlign = "left";

      return new Promise(function (resolve, reject) {
        canvas.toBlob(function (blob) { blob ? resolve(blob) : reject(new Error("toBlob failed")); }, "image/png");
      });
    });
  }

  /* ------------------------------------------------------------------ */
  /* Submit and deep links                                               */
  /* ------------------------------------------------------------------ */

  function run(promise) {
    showLoading();
    return promise.then(function (r) {
      stopLoading();
      result.__current = r;
      renderResult(r);
    }, function (err) {
      stopLoading();
      showNotice(err || {});
    });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    var values = { query: queryInput.value, brand: brandInput.value, store_url: storeInput.value };
    var errors = validate(values);
    setError(queryInput, errors.query || "");
    setError(brandInput, errors.brand || "");
    setError(storeInput, errors.store_url || "");
    var first = [queryInput, brandInput, storeInput].filter(function (i) { return i.getAttribute("aria-invalid"); })[0];
    if (first) { first.focus(); return; }
    run(adapter.ask(values));
  });

  var params = new URLSearchParams(location.search);
  if (params.get("result")) {
    if (params.get("brand")) brandInput.value = params.get("brand");
    if (params.get("store")) storeInput.value = params.get("store");
    run(adapter.get(params.get("result"), { brand: params.get("brand") || "", store_url: params.get("store") || "" })).then(function () {
      if (result.__current) { queryInput.value = result.__current.query; updateCount(); }
    });
  }
})();
