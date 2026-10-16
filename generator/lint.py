#!/usr/bin/env python3
"""Site lint, run in CI after generator/build.py --check.

Fails on
  * em or en dashes in Markdown posts, generator files, llms.txt, robots.txt,
    the hand-maintained landing page, and in the <title> and meta description
    of every page (legacy post bodies predate the rule and are not scanned)
  * sitemap and RSS that are not well-formed XML
  * JSON-LD on any page that does not parse
  * pages missing og:image, a large twitter card or the RSS link
  * leftover {{placeholders}} from the templates
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
DASH_SCAN = ["posts", "generator", "llms.txt", "robots.txt", "shopify-plus-developer-amsterdam", ".github"]


def pages() -> list[Path]:
    return sorted(p for p in REPO.glob("**/index.html") if "_ploy_static" not in p.parts and ".git" not in p.parts)


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    placeholders: dict[str, set[str]] = {}

    def dashes(text: str, where: str) -> None:
        for n, line in enumerate(text.splitlines(), 1):
            for ch, name in DASHES.items():
                if ch in line:
                    errors.append(f"{where}:{n}: {name}")

    for entry in DASH_SCAN:
        path = REPO / entry
        files = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
        for f in files:
            if f.suffix in {".jpg", ".png", ".webp", ".ico", ".woff2"}:
                continue
            dashes(f.read_text(encoding="utf-8"), str(f.relative_to(REPO)))

    for page in pages():
        rel = str(page.relative_to(REPO))
        h = page.read_text(encoding="utf-8")
        title = re.search(r"<title>(.*?)</title>", h, re.S)
        desc = re.search(r'<meta name="description" content="([^"]*)"', h)
        if not title:
            errors.append(f"{rel}: no <title>")
        else:
            dashes(title.group(1), f"{rel} <title>")
            if title.group(1).count("| Soulstone") > 1:
                errors.append(f"{rel}: doubled brand in title: {title.group(1)!r}")
        if not desc:
            errors.append(f"{rel}: no meta description")
        else:
            dashes(desc.group(1), f"{rel} meta description")
        for attr, label in [('property="og:image"', "og:image"), ('name="twitter:card" content="summary_large_image"', "twitter large card"),
                            ('type="application/rss+xml"', "RSS link")]:
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
    print(f"lint ok: {len(pages())} pages checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
