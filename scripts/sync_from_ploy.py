#!/usr/bin/env python3
"""Fetch Ploy preview HTML, rewrite URLs for soulstone.co, write GitHub Pages layout."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLOY_ORIGIN = "https://my-site-376b3de7.ploy.build"
SITE_ORIGIN = "https://soulstone.co"

# path on Ploy -> output path in repo (relative to ROOT)
PAGES: list[tuple[str, str]] = [
    ("", "index.html"),
    ("faq", "faq/index.html"),
    ("results", "results/index.html"),
    ("shopify-plus-architecture", "shopify-plus-architecture/index.html"),
    ("blog", "blog/index.html"),
    (
        "blog/conversion-not-traffic-problem",
        "blog/conversion-not-traffic-problem/index.html",
    ),
    (
        "blog/hidden-cost-shopify-plus-app-sprawl",
        "blog/hidden-cost-shopify-plus-app-sprawl/index.html",
    ),
    (
        "blog/mobile-speed-conversion-premium-shopify",
        "blog/mobile-speed-conversion-premium-shopify/index.html",
    ),
    (
        "blog/premium-product-page-anatomy",
        "blog/premium-product-page-anatomy/index.html",
    ),
    (
        "blog/replatforming-usually-wrong-answer",
        "blog/replatforming-usually-wrong-answer/index.html",
    ),
    ("tag/conversion", "tag/conversion/index.html"),
    ("tag/shopify-plus", "tag/shopify-plus/index.html"),
    ("tag/architecture", "tag/architecture/index.html"),
    ("tag/performance", "tag/performance/index.html"),
    ("tag/premium-brands", "tag/premium-brands/index.html"),
]

STATIC_ASSETS = [
    "/_ploy_static/_astro/Layout.TeYpMCHh.css",
    "/_ploy_static/_astro/site-header.b9Kqj_FD.js",
]

LEGACY_ROOT_FILES = [
    "faq.html",
    "results.html",
    "shopify-plus-architecture.html",
]


def fetch(url: str) -> str:
    result = subprocess.run(
        ["curl", "-sL", url],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def transform_html(html: str) -> str:
    html = html.replace(PLOY_ORIGIN, SITE_ORIGIN)
    html = html.replace("http://soulstone.co", SITE_ORIGIN)

    # Legacy export used *.html paths and pointed blog at Ploy.
    replacements = {
        'href="index.html"': 'href="/"',
        'href="faq.html"': 'href="/faq"',
        'href="results.html"': 'href="/results"',
        'href="shopify-plus-architecture.html"': 'href="/shopify-plus-architecture"',
        'href="index.html#': 'href="/#',
    }
    for old, new in replacements.items():
        html = html.replace(old, new)

    html = re.sub(
        r'<link rel="canonical" href="[^"]*\.html"',
        lambda m: m.group(0).split('"')[0] + '"',
        html,
    )
    # Fix any remaining relative canonicals like faq.html
    html = re.sub(
        r'(<link rel="canonical" href=")(?!https?://)[^"]+\.html(")',
        r"\1" + SITE_ORIGIN + r"\2",
        html,
    )

    if PLOY_ORIGIN in html or "my-site-376b3de7" in html:
        raise RuntimeError("Ploy origin still present after transform")

    return html


def download_static_asset(asset_path: str) -> None:
    dest = ROOT / asset_path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        return
    url = PLOY_ORIGIN + asset_path
    content = fetch(url)
    dest.write_text(content, encoding="utf-8")
    print(f"  downloaded {asset_path}")


def main() -> int:
    print("Downloading static assets...")
    for asset in STATIC_ASSETS:
        download_static_asset(asset)

    print("Fetching and writing pages...")
    for ploy_path, out_path in PAGES:
        url = f"{PLOY_ORIGIN}/{ploy_path}" if ploy_path else f"{PLOY_ORIGIN}/"
        print(f"  {url} -> {out_path}")
        html = transform_html(fetch(url))
        dest = ROOT / out_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(html, encoding="utf-8")

    print("Removing legacy root *.html pages...")
    for legacy in LEGACY_ROOT_FILES:
        path = ROOT / legacy
        if path.exists():
            path.unlink()
            print(f"  removed {legacy}")

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
