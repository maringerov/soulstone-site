#!/usr/bin/env python3
"""Soulstone Open Graph card generator.

Writes the 1200x630 brand card that every page links as og:image and
twitter:image (the file named by "og_image" in generator/site.json). The card
is the dial texture from assets/c6b425b1-moser-fume-dial-clean.png, scaled to
cover the canvas and pulled down to near black under a gradient that lets the
most texture through at the bottom right, with the wordmark set in the site's
own web fonts from _ploy_static/_astro (Playfair Display for the name,
Manrope for the strapline, JetBrains Mono for the eyebrow and the URL).

The layout constants were measured off the original hand-made card so a
rebuild reproduces it; change the copy below and rerun to issue a new card.
Social networks cache the image by URL, so a new card wants a new file name:
change "og_image" in site.json, rerun this script, delete the old file and run
generator/build.py so every page, the RSS channel image and the JSON-LD point
at the new name.

Usage
  pip install -r generator/requirements-og.txt
  python3 generator/og_image.py              # writes the file named in site.json
  python3 generator/og_image.py --out PATH   # write somewhere else instead
"""
from __future__ import annotations

import argparse
import io
import json
from pathlib import Path

from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent
SITE = REPO / "generator" / "site.json"
TEXTURE = REPO / "assets" / "c6b425b1-moser-fume-dial-clean.png"
FONTS = REPO / "_ploy_static" / "_astro"

WIDTH, HEIGHT = 1200, 630

# Copy. The strapline is two fixed lines; the second line is the longest the
# column allows at this size, so a longer first line wraps by hand here.
EYEBROW = "SHOPIFY & SHOPIFY PLUS  \u00b7  AMSTERDAM"
TITLE = "Soulstone"
STRAPLINE = ("Independent Shopify Plus Developer", "and Conversion Specialist in Amsterdam")
URL = "soulstone.co"

# Palette. The card predates the green site tokens and keeps its own warm
# gold accent on near-black.
DARK = (7, 9, 6)
GOLD = (200, 172, 110)
CREAM = (243, 239, 230)
STRAP = (216, 217, 210)
MUTED = (165, 165, 157)

# How much of the texture shows through at each corner (top-left, top-right,
# bottom-left, bottom-right); bilinear in between.
TEXTURE_CORNERS = (0.02, 0.27, 0.20, 0.34)

# Type: (font file, size, variable weight). The woff2 files are variable
# fonts; Manrope's lightest instance (200) is the one on the card.
PLAYFAIR = ("playfair-display-latin-wght-normal.BOwq7MWX.woff2", 118, 400)
MANROPE = ("manrope-latin-wght-normal.DHIcAJRg.woff2", 30, 200)
MONO = ("jetbrains-mono-latin-wght-normal.B9CIFXIH.woff2", 22, 400)

# Left column and the top of each text box (Pillow's default anchor).
LEFT = 90
EYEBROW_Y = 90
RULE = (90, 140, 150, 141)  # inclusive box: 61 x 2 px
TITLE_XY = (88, 175)
STRAPLINE_Y = 345
STRAPLINE_LEADING = 42
URL_Y = 540

JPEG = dict(quality=86, progressive=True, optimize=True, subsampling="4:2:0")


def font(spec: tuple[str, int, int]) -> ImageFont.FreeTypeFont:
    name, size, weight = spec
    tt = TTFont(FONTS / name)
    tt.flavor = None  # woff2 -> plain TrueType for FreeType
    buf = io.BytesIO()
    tt.save(buf)
    buf.seek(0)
    f = ImageFont.truetype(buf, size)
    f.set_variation_by_axes([weight])
    return f


def texture() -> Image.Image:
    """The dial scaled to cover the canvas, centre cropped."""
    src = Image.open(TEXTURE).convert("RGB")
    scale = max(WIDTH / src.width, HEIGHT / src.height)
    scaled = src.resize((round(src.width * scale), round(src.height * scale)), Image.LANCZOS)
    left = (scaled.width - WIDTH) // 2
    top = (scaled.height - HEIGHT) // 2
    return scaled.crop((left, top, left + WIDTH, top + HEIGHT))


def gradient_mask() -> Image.Image:
    tl, tr, bl, br = TEXTURE_CORNERS
    small = Image.new("F", (2, 2))
    small.putdata([tl, tr, bl, br])
    mask = small.resize((WIDTH, HEIGHT), Image.BILINEAR)
    return mask.point(lambda v: v * 255).convert("L")


def background() -> Image.Image:
    base = Image.new("RGB", (WIDTH, HEIGHT), DARK)
    return Image.composite(texture(), base, gradient_mask())


def card() -> Image.Image:
    im = background()
    d = ImageDraw.Draw(im)
    mono = font(MONO)
    d.text((LEFT, EYEBROW_Y), EYEBROW, font=mono, fill=GOLD)
    d.rectangle(RULE, fill=GOLD)
    d.text(TITLE_XY, TITLE, font=font(PLAYFAIR), fill=CREAM)
    strap = font(MANROPE)
    for i, line in enumerate(STRAPLINE):
        d.text((LEFT, STRAPLINE_Y + i * STRAPLINE_LEADING), line, font=strap, fill=STRAP)
    d.text((LEFT, URL_Y), URL, font=mono, fill=MUTED)
    return im


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, help="output path (default: og_image from site.json)")
    args = ap.parse_args()
    out = args.out or REPO / json.loads(SITE.read_text(encoding="utf-8"))["og_image"].lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    card().save(out, "JPEG", **JPEG)
    print(f"wrote {out.relative_to(REPO) if out.is_relative_to(REPO) else out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
