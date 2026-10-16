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
# Blog posts, the blog index and tag pages are NOT listed: they are owned by
# generator/build.py and must never be fetched from Ploy again.
PAGES: list[tuple[str, str]] = [
    ("", "index.html"),
    ("faq", "faq/index.html"),
    ("results", "results/index.html"),
    ("shopify-plus-architecture", "shopify-plus-architecture/index.html"),
]

# Paths written by generator/build.py. Anything under these prefixes is
# refused by write_output(), whatever the PAGES/ROOT_FILES lists say.
GENERATOR_OWNED: tuple[str, ...] = (
    "blog/",
    "tag/",
    "sitemap-index.xml",
    "sitemap-0.xml",
    "rss.xml",
)

# Hand-maintained in this repo, not on Ploy. Also refused by write_output().
HAND_MAINTAINED: tuple[str, ...] = (
    "robots.txt",
    "llms.txt",
    "shopify-plus-developer-amsterdam/",
    "assets/",
    "generator/",
    "posts/",
)

# Root-level static files fetched from Ploy and rewritten for soulstone.co.
# robots.txt and the sitemaps used to be here; robots.txt is hand-maintained
# and the sitemaps come from the generator.
ROOT_FILES: list[tuple[str, str]] = []

# Safe to fetch/refresh from Ploy
STATIC_ASSETS = [
    "/_ploy_static/_astro/Layout.TeYpMCHh.css",
    "/_ploy_static/_astro/site-header.b9Kqj_FD.js",
]

# Never overwrite: local remaps or GitHub Pages-specific fixes
# (WebP dial with PNG fallback, hero visible without JS, footer links).
PROTECTED_STATIC_ASSETS = [
    "/_ploy_static/_astro/dial-canvas.CyRCYrVZ.js",
    "/_ploy_static/_astro/closing-cta.B27vAxRK.js",
    "/_ploy_static/_astro/site-footer.DULiVXzC.js",
]

LEGACY_ROOT_FILES = [
    "faq.html",
    "results.html",
    "shopify-plus-architecture.html",
]


def is_protected(rel_path: str) -> str | None:
    """Return the matching protected prefix for a repo-relative path, if any."""
    rel = rel_path.lstrip("/")
    for prefix in GENERATOR_OWNED + HAND_MAINTAINED:
        if rel == prefix or rel.startswith(prefix):
            return prefix
    return None


def write_output(rel_path: str, content: str) -> None:
    prefix = is_protected(rel_path)
    if prefix:
        raise RuntimeError(
            f"refusing to write {rel_path}: '{prefix}' is generator-owned or hand-maintained"
        )
    dest = ROOT / rel_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(content, encoding="utf-8")


def fetch(url: str) -> str:
    result = subprocess.run(
        ["curl", "-sL", url],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def transform_content(content: str) -> str:
    content = content.replace(PLOY_ORIGIN, SITE_ORIGIN)
    content = content.replace("http://soulstone.co", SITE_ORIGIN)
    return content


def transform_html(html: str) -> str:
    html = transform_content(html)

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

    if PLOY_ORIGIN in html or "my-site-376b3de7" in html:
        raise RuntimeError("Ploy origin still present after transform")

    return html


def download_static_asset(asset_path: str, *, protected: bool = False) -> None:
    dest = ROOT / asset_path.lstrip("/")
    dest.parent.mkdir(parents=True, exist_ok=True)
    if protected and dest.exists():
        print(f"  kept protected {asset_path}")
        return
    url = PLOY_ORIGIN + asset_path
    content = fetch(url)
    dest.write_text(content, encoding="utf-8")
    print(f"  downloaded {asset_path}")


def main() -> int:
    for ploy_path, out_path in PAGES + ROOT_FILES:
        prefix = is_protected(out_path)
        if prefix:
            raise RuntimeError(f"{out_path} is listed for sync but '{prefix}' is protected")

    print("Downloading static assets...")
    for asset in STATIC_ASSETS:
        download_static_asset(asset)
    for asset in PROTECTED_STATIC_ASSETS:
        download_static_asset(asset, protected=True)

    print("Fetching and writing pages...")
    for ploy_path, out_path in PAGES:
        url = f"{PLOY_ORIGIN}/{ploy_path}" if ploy_path else f"{PLOY_ORIGIN}/"
        print(f"  {url} -> {out_path}")
        write_output(out_path, transform_html(fetch(url)))

    print("Fetching root files (robots, sitemaps)...")
    for ploy_path, out_path in ROOT_FILES:
        url = f"{PLOY_ORIGIN}/{ploy_path}"
        print(f"  {url} -> {out_path}")
        content = transform_content(fetch(url))
        if PLOY_ORIGIN in content or "my-site-376b3de7" in content:
            raise RuntimeError(f"Ploy origin still present in {out_path}")
        write_output(out_path, content)

    print("Removing legacy root *.html pages...")
    for legacy in LEGACY_ROOT_FILES:
        path = ROOT / legacy
        if path.exists():
            path.unlink()
            print(f"  removed {legacy}")

    print("Re-applying the shared head block and rebuilding the blog...")
    subprocess.run([sys.executable, str(ROOT / "generator" / "build.py")], check=True)

    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
