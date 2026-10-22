/*
 * MOCK DATA ONLY. Nothing in this file talks to a network.
 *
 * Sample answers for the "What would AI say?" tool on /win-chat/. The shape of
 * each result matches the API contract in the tool spec (POST /v1/ai-say) so
 * the real Worker can replace this file without touching tool.js: swap the
 * adapter in tool.js (window.SS_AI_SAY_ADAPTER) and delete this script tag.
 *
 * Every brand, publication and domain below is invented. None of them refers
 * to a real company or person.
 *
 * How the mock picks an answer
 *   query contains "hand soap"          -> scenario "hand-soap"
 *   query contains "collagen" or "face" -> scenario "face-cream"
 *   query contains "candle"             -> scenario "candle"
 *   anything else                       -> scenario "generic"
 *   query contains "rate limit test"    -> HTTP 429 (rate limited)
 *   query contains "paused test"        -> HTTP 503 (tool paused)
 *   query contains "fail test"          -> network failure
 *
 * Type a brand that appears in the chosen scenario (for example "Nordic Suds"
 * with the hand soap query) to see the "mentioned" state. Enter a store URL
 * whose host matches a cited domain (for example https://nordicsuds.example)
 * to see "own domain cited".
 */
(function () {
  "use strict";

  var ENGINE = "mock";

  var scenarios = {
    "hand-soap": {
      id: "r_mock_soap",
      summary:
        "An AI shopping answer would most likely open with two or three refill brands that ship within the Netherlands, then explain the trade off between concentrate tablets and bulk pouches. It would mention Nordic Suds first for its glass dispenser and tablet refills, then Pure Refill for low cost bulk pouches and Marlow Botanics for scent. It would close with a note that most refill systems only save money after the third or fourth refill and point to a buying guide and a forum thread.",
      brands: [
        { name: "Nordic Suds", rank: 1 },
        { name: "Pure Refill", rank: 2 },
        { name: "Marlow Botanics", rank: 3 },
        { name: "Hollow Oak Soap Co", rank: 4 }
      ],
      sources: [
        { url: "https://thegoodhomeguide.example/best-refillable-hand-soap", domain: "thegoodhomeguide.example" },
        { url: "https://refillreview.example/hand-soap-tablets-vs-pouches", domain: "refillreview.example" },
        { url: "https://nordicsuds.example/pages/refill-system", domain: "nordicsuds.example" },
        { url: "https://forum.lowwastehome.example/t/hand-soap-refills-nl", domain: "forum.lowwastehome.example" },
        { url: "https://purerefill.example/collections/hand-soap", domain: "purerefill.example" },
        { url: "https://duurzaamwonen.example/handzeep-navulling-test", domain: "duurzaamwonen.example" },
        { url: "https://thegoodhomeguide.example/refill-savings-calculator", domain: "thegoodhomeguide.example" }
      ],
      store_check: { jsonld_product: true, jsonld_organization: false, llms_txt: false, ai_crawlers_allowed: true }
    },

    "face-cream": {
      id: "r_mock_cream",
      summary:
        "For a collagen face cream query an AI assistant would probably explain first that topical collagen does not reach the dermis, then recommend creams that pair collagen with peptides or retinol. It would name Ferrow Skin as the most reviewed option, follow with Linden Lab for a fragrance free formula and Aurevia for a higher price point, and suggest checking ingredient lists rather than marketing claims. A dermatology magazine and two retailer review pages would carry most of the citations.",
      brands: [
        { name: "Ferrow Skin", rank: 1 },
        { name: "Linden Lab", rank: 2 },
        { name: "Aurevia", rank: 3 }
      ],
      sources: [
        { url: "https://dermnotes.example/collagen-creams-explained", domain: "dermnotes.example" },
        { url: "https://skinreviewdesk.example/best-collagen-face-cream", domain: "skinreviewdesk.example" },
        { url: "https://ferrowskin.example/products/collagen-renew", domain: "ferrowskin.example" },
        { url: "https://beautycounterpoint.example/peptides-vs-collagen", domain: "beautycounterpoint.example" },
        { url: "https://skinreviewdesk.example/linden-lab-review", domain: "skinreviewdesk.example" }
      ],
      store_check: { jsonld_product: true, jsonld_organization: true, llms_txt: false, ai_crawlers_allowed: false }
    },

    candle: {
      id: "r_mock_candle",
      summary:
        "An AI answer for a luxury candle gift would lead with presentation: a boxed candle, a known scent house and a burn time above forty hours. It would list Maison Verre first for packaging, Ember and Ash second for seasonal scents and Still Water Studio third as a smaller maker. Expect a short line on price bands from about forty to one hundred euros and links to two gift guides and one editorial list.",
      brands: [
        { name: "Maison Verre", rank: 1 },
        { name: "Ember and Ash", rank: 2 },
        { name: "Still Water Studio", rank: 3 },
        { name: "Kindle House", rank: 4 },
        { name: "Northlight Candles", rank: 5 }
      ],
      sources: [
        { url: "https://giftedit.example/luxury-candle-gifts", domain: "giftedit.example" },
        { url: "https://homeandhearth.example/best-scented-candles", domain: "homeandhearth.example" },
        { url: "https://maisonverre.example/gifting", domain: "maisonverre.example" },
        { url: "https://theinteriorsjournal.example/candles-worth-the-money", domain: "theinteriorsjournal.example" },
        { url: "https://giftedit.example/candles-under-100", domain: "giftedit.example" },
        { url: "https://emberandash.example/collections/gift-sets", domain: "emberandash.example" }
      ],
      store_check: { jsonld_product: false, jsonld_organization: false, llms_txt: false, ai_crawlers_allowed: true }
    },

    generic: {
      id: "r_mock_generic",
      summary:
        "For this query an AI shopping answer would most likely open with two or three well reviewed brands, say in one line what sets each apart, and add a caution about price or availability. It would lean on a buying guide, a comparison article and one or two retailer pages for its citations. Brands with clear product data and recent reviews tend to be named first.",
      brands: [
        { name: "Halden Goods", rank: 1 },
        { name: "Orrin and Vale", rank: 2 },
        { name: "Fieldnote Supply", rank: 3 }
      ],
      sources: [
        { url: "https://thebuyersdigest.example/guide", domain: "thebuyersdigest.example" },
        { url: "https://comparelist.example/top-picks", domain: "comparelist.example" },
        { url: "https://haldengoods.example/collections/all", domain: "haldengoods.example" },
        { url: "https://thebuyersdigest.example/what-to-look-for", domain: "thebuyersdigest.example" }
      ],
      store_check: { jsonld_product: true, jsonld_organization: false, llms_txt: true, ai_crawlers_allowed: true }
    }
  };

  function pick(query) {
    var q = String(query || "").toLowerCase();
    if (q.indexOf("hand soap") !== -1) return scenarios["hand-soap"];
    if (q.indexOf("collagen") !== -1 || q.indexOf("face") !== -1) return scenarios["face-cream"];
    if (q.indexOf("candle") !== -1) return scenarios.candle;
    return scenarios.generic;
  }

  function error(query) {
    var q = String(query || "").toLowerCase();
    if (q.indexOf("rate limit test") !== -1) return { status: 429, body: { error: "rate_limited", retry_after: 1800 } };
    if (q.indexOf("paused test") !== -1) return { status: 503, body: { error: "paused" } };
    if (q.indexOf("fail test") !== -1) return { status: 0, body: null };
    return null;
  }

  window.SS_AI_SAY_FIXTURES = {
    engine: ENGINE,
    delay_ms: 3200,
    scenarios: scenarios,
    pick: pick,
    error: error
  };
})();
