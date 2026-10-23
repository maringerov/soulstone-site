#!/usr/bin/env python3
"""Site lint, run in CI after generator/build.py --check.

Fails on
  * em or en dashes anywhere in shipped HTML, JS and text: every *.html page,
    every bundle under _ploy_static/_astro, Markdown posts, generator files,
    workflows, llms.txt and robots.txt
  * banned words (BANNED_WORDS, case-insensitive) in the same files: the site
    describes Marin as an independent developer and never uses the usual
    label for a self-employed contractor
  * sitemap and RSS that are not well-formed XML
  * JSON-LD on any page that does not parse
  * pages missing og:image, a large twitter card, the RSS link, the favicon
    links (SVG, ICO fallback, apple-touch-icon, manifest, theme-color), the
    mobile menu (toggle button, #site-menu panel and the toggle script), the
    Win Chat link in the desktop nav and the mobile menu, the promo banner
    script, the GA4 tag with its denied consent default, the cookie consent
    script or the footer link to /privacy
  * a leftover Ploy starter favicon link (type="image/x-icon")
  * icon files referenced from the head or site.webmanifest that do not exist
  * an absolute /assets/ URL (og:image, twitter:image, JSON-LD or RSS image)
    on any page or in rss.xml whose file does not exist, so a renamed Open
    Graph card cannot leave a stale name behind
  * a blog post without exactly one in-article Win Chat promo card, or the
    card on a page that is not a post
  * leftover {{placeholders}} from the templates
  * the Google Search Console verification file changed, gained a trailing
    newline or ended up in the sitemap
  * a page URL without its trailing slash. GitHub Pages serves <dir>/index.html
    at <dir>/ and 301-redirects the slashless form, so every canonical, og:url,
    JSON-LD url/@id/item/mainEntityOfPage, sitemap <loc>, RSS <link>/<guid>,
    llms.txt link and internal href (in pages, templates and the Astro bundles)
    to an HTML page must end in "/". The canonical must also be the page's own
    URL. Files with an extension (/rss.xml, /favicon.svg) and bare fragments
    (#contact) are exempt; a fragment or query goes after the slash.
  * a date in the future: any sitemap <lastmod> or any JSON-LD datePublished
    later than today in Europe/Amsterdam (the build date). Nothing on the site
    may claim to have been published or changed on a day that has not happened.
Prints a warning for configuration values still marked PLACEHOLDER.
"""
from __future__ import annotations

import datetime as dt
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parent.parent
TODAY = dt.datetime.now(ZoneInfo("Europe/Amsterdam")).date().isoformat()
DASHES = {"\u2014": "em dash", "\u2013": "en dash"}
# Same list as build.py. The optional hyphen catches the hyphenated spelling
# and keeps the banned string itself out of this file.
BANNED_WORDS = {
    re.compile(r"free-?lanc", re.I): "say independent, or describe the work, instead",
}
TEXT_SUFFIXES = {".html", ".js", ".css", ".md", ".txt", ".xml", ".json", ".yml", ".yaml", ".py", ".svg", ".webmanifest"}
SKIP_PARTS = {".git", "__pycache__", "node_modules"}
# Google serves this back byte for byte; it is not a page and never gets a
# head block, a trailing newline or a sitemap entry.
GOOGLE_VERIFICATION = "googlef0ef0874c5fa4c80.html"
GOOGLE_VERIFICATION_BODY = b"google-site-verification: googlef0ef0874c5fa4c80.html"
ORIGIN = json.loads((REPO / "generator" / "site.json").read_text(encoding="utf-8"))["origin"].rstrip("/")
JSONLD_URL_KEYS = {"url", "@id", "item", "mainEntityOfPage"}
ARTICLE_PROMO_START = "<!-- win-chat-promo:start -->"


def pages() -> list[Path]:
    return sorted(p for p in REPO.glob("**/index.html") if "_ploy_static" not in p.parts and ".git" not in p.parts)


def templates() -> list[Path]:
    return sorted((REPO / "generator" / "templates").glob("*.html"))


def bundles() -> list[Path]:
    return sorted((REPO / "_ploy_static" / "_astro").glob("*.js"))


def internal_path(url: str) -> str | None:
    """Site-relative path for an internal URL, None for external links and bare fragments."""
    if url.startswith(ORIGIN + "/") or url == ORIGIN:
        return url[len(ORIGIN):] or "/"
    if url.startswith("/"):
        return url
    return None


def missing_slash(url: str) -> bool:
    """True when an internal URL points at an HTML page without its trailing slash."""
    path = internal_path(url)
    if path is None:
        return False
    base = re.split(r"[#?]", path, 1)[0]
    if base.endswith("/"):
        return False
    return "." not in base.rsplit("/", 1)[-1]


def page_url(page: Path) -> str:
    rel = page.relative_to(REPO).parent.as_posix()
    return ORIGIN + "/" + ("" if rel == "." else rel + "/")


def href_errors(h: str, rel: str) -> list[str]:
    """Internal hrefs (attributes and serialized astro-island props) that lack the trailing slash."""
    hrefs = re.findall(r'\bhref="([^"]*)"', h) + re.findall(r"&quot;href&quot;:\[0,&quot;([^&]*)&quot;\]", h)
    bad = sorted({u for u in hrefs if missing_slash(u)})
    return [f"{rel}: href without trailing slash: {bad}"] if bad else []


def asset_errors(text: str, rel: str) -> list[str]:
    """Absolute /assets/ URLs (og:image, twitter:image, JSON-LD and RSS images) whose file is missing.

    The Open Graph card is renamed when its artwork changes, so a stale name
    in a legacy post or a bundle would ship a broken preview image.
    """
    names = sorted(set(re.findall(re.escape(ORIGIN) + r"/assets/([A-Za-z0-9._-]+)", text)))
    missing = [n for n in names if not (REPO / "assets" / n).is_file()]
    return [f"{rel}: /assets/{n} is referenced but does not exist" for n in missing]


def jsonld_urls(node) -> list[str]:
    found: list[str] = []
    if isinstance(node, list):
        for n in node:
            found += jsonld_urls(n)
    elif isinstance(node, dict):
        for k, v in node.items():
            if k in JSONLD_URL_KEYS and isinstance(v, str):
                found.append(v)
            else:
                found += jsonld_urls(v)
    return found


def published_dates(node) -> list[str]:
    """Every datePublished value in a JSON-LD graph, as YYYY-MM-DD."""
    found: list[str] = []
    if isinstance(node, list):
        for n in node:
            found += published_dates(n)
    elif isinstance(node, dict):
        for k, v in node.items():
            if k == "datePublished" and isinstance(v, str):
                found.append(v[:10])
            else:
                found += published_dates(v)
    return found


def shipped_text_files() -> list[Path]:
    return sorted(
        p for p in REPO.rglob("*")
        if p.is_file() and p.suffix in TEXT_SUFFIXES and not SKIP_PARTS & set(p.parts)
    )


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    placeholders: dict[str, set[str]] = {}

    def dashes(text: str, where: str) -> None:
        for n, line in enumerate(text.splitlines(), 1):
            for ch, name in DASHES.items():
                if ch in line:
                    errors.append(f"{where}:{n}: {name}")

    def banned_words(text: str, where: str) -> None:
        for n, line in enumerate(text.splitlines(), 1):
            for pat, hint in BANNED_WORDS.items():
                for m in pat.finditer(line):
                    errors.append(f"{where}:{n}:{m.start() + 1}: banned word {m.group(0)!r}, {hint}")

    scanned = shipped_text_files()
    for f in scanned:
        text = f.read_text(encoding="utf-8")
        where = str(f.relative_to(REPO))
        dashes(text, where)
        banned_words(text, where)

    for page in pages():
        rel = str(page.relative_to(REPO))
        h = page.read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", h, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', h)
        if not title:
            errors.append(f"{rel}: no <title>")
        else:
            if title.group(1).count("| Soulstone") > 1:
                errors.append(f"{rel}: doubled brand in title: {title.group(1)!r}")
        if not desc:
            errors.append(f"{rel}: no meta description")
        for attr, label in [('property="og:image"', "og:image"), ('name="twitter:card" content="summary_large_image"', "twitter large card"),
                            ('type="application/rss+xml"', "RSS link"),
                            ('<link rel="icon" href="/favicon.svg" type="image/svg+xml"/>', "SVG favicon"),
                            ('<link rel="icon" href="/favicon.ico" sizes="48x48"/>', "ICO favicon fallback"),
                            ('<link rel="apple-touch-icon" href="/apple-touch-icon.png"', "apple-touch-icon"),
                            ('<link rel="manifest" href="/site.webmanifest"/>', "web app manifest"),
                            ('<meta name="theme-color" content="', "theme-color"),
                            ('<button type="button" class="ss-nav-toggle" aria-expanded="false" aria-controls="site-menu">', "mobile menu toggle"),
                            ('<nav id="site-menu" class="ss-nav-panel" data-state="closed"', "mobile menu panel"),
                            ("window.__ssNav", "mobile menu script"),
                            ('<a href="/win-chat/" class="font-mono text-[0.7rem] uppercase tracking-[0.18em] text-ploy-text-secondary transition-colors hover:text-ploy-text-primary">Win Chat</a></nav>', "Win Chat link in the desktop nav"),
                            ('<li><a href="/win-chat/" class="ss-nav-link font-mono uppercase tracking-[0.18em] text-ploy-text-secondary transition-colors hover:text-ploy-text-primary">Win Chat</a></li></ul>', "Win Chat link in the mobile menu"),
                            ("window.__ssPromo", "promo banner script"),
                            ('<script async src="https://www.googletagmanager.com/gtag/js?id=G-', "GA4 tag"),
                            ("gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'})", "GA4 consent default"),
                            ("window.__ssConsent", "cookie consent script"),
                            ('<a href="/privacy/" class="text-ploy-text-primary/85 transition-colors hover:text-ploy-accent-primary">Privacy</a>', "footer privacy link")]:
            if attr not in h:
                errors.append(f"{rel}: missing {label}")
        own = page_url(page)
        canonical = re.search(r'<link rel="canonical" href="([^"]*)"', h)
        if not canonical:
            errors.append(f"{rel}: no canonical link")
        elif canonical.group(1) != own:
            errors.append(f"{rel}: canonical {canonical.group(1)!r} is not the page's own URL {own!r}")
        og_url = re.search(r'<meta property="og:url" content="([^"]*)"', h)
        if not og_url:
            errors.append(f"{rel}: no og:url")
        elif og_url.group(1) != own:
            errors.append(f"{rel}: og:url {og_url.group(1)!r} is not the page's own URL {own!r}")
        hreflang = [u for u in re.findall(r'<link rel="alternate" hreflang="[^"]*" href="([^"]*)"', h) if missing_slash(u)]
        if hreflang:
            errors.append(f"{rel}: hreflang without trailing slash: {sorted(set(hreflang))}")
        errors += href_errors(h, rel)
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                errors.append(f"{rel}: JSON-LD does not parse: {e}")
                continue
            bad = sorted({u for u in jsonld_urls(data) if missing_slash(u)})
            if bad:
                errors.append(f"{rel}: JSON-LD URL without trailing slash: {bad}")
            future = sorted({d for d in published_dates(data) if d > TODAY})
            if future:
                errors.append(f"{rel}: datePublished {future} is after today ({TODAY})")
        errors += asset_errors(h, rel)
        if 'type="image/x-icon"' in h:
            errors.append(f"{rel}: old Ploy favicon link still present")
        is_post = page.parent.parent == REPO / "blog"
        promos = h.count(ARTICLE_PROMO_START)
        asides = h.count('<aside class="not-prose ss-article-promo" aria-label="Win Chat">')
        if is_post and (promos != 1 or asides != 1):
            errors.append(f"{rel}: every post needs exactly one Win Chat promo card, found {promos} marker(s) and {asides} aside(s)")
        if not is_post and (promos or asides):
            errors.append(f"{rel}: Win Chat promo card belongs in posts only")
        if re.search(r"\{\{[a-z_]+\}\}", h):
            errors.append(f"{rel}: unfilled template placeholder")
        for m in re.finditer(r"PLACEHOLDER[^<\"]*", h):
            placeholders.setdefault(m.group(0).strip(), set()).add(rel)

    for tpl in templates():
        rel = str(tpl.relative_to(REPO))
        t = tpl.read_text(encoding="utf-8")
        errors += href_errors(t, rel)
        for attr, label in [(r'<link rel="canonical" href="([^"]*)"', "canonical"), (r'<meta property="og:url" content="([^"]*)"', "og:url")]:
            m = re.search(attr, t)
            if m and m.group(1) != "{{url}}" and not m.group(1).endswith("/"):
                errors.append(f"{rel}: {label} {m.group(1)!r} lacks the trailing slash")

    for js in bundles():
        rel = str(js.relative_to(REPO))
        bad = sorted({u for u in re.findall(r'\bhref:"([^"]*)"', js.read_text(encoding="utf-8")) if missing_slash(u) or u.endswith(".html") or "index.html#" in u})
        if bad:
            errors.append(f"{rel}: href without trailing slash: {bad}")

    for xml in ["sitemap-0.xml", "sitemap-index.xml", "rss.xml"]:
        try:
            ET.fromstring((REPO / xml).read_bytes())
        except (ET.ParseError, FileNotFoundError) as e:
            errors.append(f"{xml}: {e}")

    sitemap = (REPO / "sitemap-0.xml").read_text(encoding="utf-8")
    locs = re.findall(r"<loc>([^<]+)</loc>", sitemap)
    if len(locs) != len(set(locs)):
        errors.append("sitemap-0.xml: duplicate <loc> entries")
    if sitemap.count("<url>") != sitemap.count("<lastmod>"):
        errors.append("sitemap-0.xml: every <url> needs a <lastmod>")
    if any(GOOGLE_VERIFICATION in loc for loc in locs):
        errors.append(f"sitemap-0.xml: {GOOGLE_VERIFICATION} must not be listed")
    for loc in locs:
        if missing_slash(loc) or not loc.startswith(ORIGIN + "/"):
            errors.append(f"sitemap-0.xml: <loc>{loc}</loc> is not a trailing-slash page URL on {ORIGIN}")
    for loc, lastmod in re.findall(r"<loc>([^<]+)</loc><lastmod>([^<]+)</lastmod>", sitemap):
        if lastmod[:10] > TODAY:
            errors.append(f"sitemap-0.xml: {loc} lastmod {lastmod} is after today ({TODAY})")

    rss = (REPO / "rss.xml").read_text(encoding="utf-8")
    for u in re.findall(r"<(?:link|guid[^>]*)>([^<]+)</(?:link|guid)>", rss):
        if missing_slash(u):
            errors.append(f"rss.xml: {u} lacks the trailing slash")
    errors += asset_errors(rss, "rss.xml")

    llms = (REPO / "llms.txt").read_text(encoding="utf-8")
    for u in re.findall(r"https?://[^\s)\]>]+", llms):
        if missing_slash(u):
            errors.append(f"llms.txt: {u} lacks the trailing slash")

    icon_files = {"favicon.svg", "favicon.ico", "apple-touch-icon.png"}
    try:
        manifest = json.loads((REPO / "site.webmanifest").read_text(encoding="utf-8"))
        for key in ("name", "short_name", "theme_color", "background_color", "icons"):
            if not manifest.get(key):
                errors.append(f"site.webmanifest: missing {key}")
        for icon in manifest.get("icons", []):
            icon_files.add(icon["src"].lstrip("/"))
        if not any(i.get("purpose") == "maskable" for i in manifest.get("icons", [])):
            errors.append("site.webmanifest: no maskable icon")
    except (json.JSONDecodeError, FileNotFoundError, KeyError, TypeError) as e:
        errors.append(f"site.webmanifest: {e}")
    for name in sorted(icon_files):
        if not (REPO / name).is_file():
            errors.append(f"{name}: icon file missing")

    verification = REPO / GOOGLE_VERIFICATION
    if not verification.is_file():
        errors.append(f"{GOOGLE_VERIFICATION}: missing")
    elif verification.read_bytes() != GOOGLE_VERIFICATION_BODY:
        errors.append(f"{GOOGLE_VERIFICATION}: content changed (expected the exact token, no trailing newline)")

    cfg = json.loads((REPO / "generator" / "site.json").read_text(encoding="utf-8"))
    for k, v in cfg.get("profiles", {}).items():
        if str(v).upper().startswith("PLACEHOLDER"):
            warnings.append(f"generator/site.json profiles.{k} is still a placeholder")

    for text, where in sorted(placeholders.items()):
        warnings.append(f"{text!r} on {len(where)} page(s), e.g. {sorted(where)[0]}")
    for w in sorted(set(warnings)):
        print(f"warning: {w}")
    if errors:
        for e in errors:
            print(f"error: {e}", file=sys.stderr)
        print(f"\n{len(errors)} lint error(s)", file=sys.stderr)
        return 1
    print(f"lint ok: {len(pages())} pages checked, {len(scanned)} files scanned for dashes and banned words")
    return 0


if __name__ == "__main__":
    sys.exit(main())
