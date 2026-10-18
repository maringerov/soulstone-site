#!/usr/bin/env python3
"""Site lint, run in CI after generator/build.py --check.

Fails on
  * em or en dashes anywhere in shipped HTML, JS and text: every *.html page,
    every bundle under _ploy_static/_astro, Markdown posts, generator files,
    workflows, llms.txt and robots.txt
  * sitemap and RSS that are not well-formed XML
  * JSON-LD on any page that does not parse
  * pages missing og:image, a large twitter card, the RSS link, the mobile
    menu (toggle button, #site-menu panel and the toggle script), the GA4 tag
    with its denied consent default, the cookie consent script or the footer
    link to /privacy
  * leftover {{placeholders}} from the templates
  * the Google Search Console verification file changed, gained a trailing
    newline or ended up in the sitemap
Prints a warning for configuration values still marked PLACEHOLDER.
"""
from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DASHES = {"\u2014": "em dash", "\u2013": "en dash"}
TEXT_SUFFIXES = {".html", ".js", ".css", ".md", ".txt", ".xml", ".json", ".yml", ".yaml", ".py"}
SKIP_PARTS = {".git", "__pycache__", "node_modules"}
# Google serves this back byte for byte; it is not a page and never gets a
# head block, a trailing newline or a sitemap entry.
GOOGLE_VERIFICATION = "googlef0ef0874c5fa4c80.html"
GOOGLE_VERIFICATION_BODY = b"google-site-verification: googlef0ef0874c5fa4c80.html"


def pages() -> list[Path]:
    return sorted(p for p in REPO.glob("**/index.html") if "_ploy_static" not in p.parts and ".git" not in p.parts)


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

    scanned = shipped_text_files()
    for f in scanned:
        dashes(f.read_text(encoding="utf-8"), str(f.relative_to(REPO)))

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
                            ('<button type="button" class="ss-nav-toggle" aria-expanded="false" aria-controls="site-menu">', "mobile menu toggle"),
                            ('<nav id="site-menu" class="ss-nav-panel" data-state="closed"', "mobile menu panel"),
                            ("window.__ssNav", "mobile menu script"),
                            ('<script async src="https://www.googletagmanager.com/gtag/js?id=G-', "GA4 tag"),
                            ("gtag('consent','default',{analytics_storage:'denied',ad_storage:'denied',ad_user_data:'denied',ad_personalization:'denied'})", "GA4 consent default"),
                            ("window.__ssConsent", "cookie consent script"),
                            ('<a href="/privacy" class="text-ploy-text-primary/85 transition-colors hover:text-ploy-accent-primary">Privacy</a>', "footer privacy link")]:
            if attr not in h:
                errors.append(f"{rel}: missing {label}")
        for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, re.S):
            try:
                json.loads(raw)
            except json.JSONDecodeError as e:
                errors.append(f"{rel}: JSON-LD does not parse: {e}")
        if re.search(r"\{\{[a-z_]+\}\}", h):
            errors.append(f"{rel}: unfilled template placeholder")
        for m in re.finditer(r"PLACEHOLDER[^<\"]*", h):
            placeholders.setdefault(m.group(0).strip(), set()).add(rel)

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
    print(f"lint ok: {len(pages())} pages checked, {len(scanned)} files scanned for dashes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
