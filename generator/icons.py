#!/usr/bin/env python3
"""Soulstone favicon and app icon generator.

Draws the S monogram as vector paths: a six segment cubic centreline swept
with a varying width, so the mark carries the diagonal stress of the Playfair
Display wordmark without referencing a font. Colours are the site tokens from
_ploy_static/_astro/Layout.TeYpMCHh.css converted from oklch to sRGB.

Outputs (repository root, committed assets; the build only links them)
  favicon.svg                 rounded square background, hairline edge
  favicon.ico                 16, 32 and 48 px
  apple-touch-icon.png        180 px, full-bleed background
  icon-192.png, icon-512.png  rounded square, transparent corners
  icon-192-maskable.png, icon-512-maskable.png
                              full-bleed background, mark inside the safe zone

Usage
  pip install -r generator/requirements-icons.txt
  python3 generator/icons.py
  python3 generator/icons.py --previews DIR   also write favicon-512.png and
                                              favicon-sizes.png (16, 32, 48 px
                                              on light and dark tabs) to DIR
"""
from __future__ import annotations

import argparse
import io
import math
from pathlib import Path

import cairosvg
from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parent.parent

BG = "#080F0C"      # --ploy-background-primary, oklch(16% .012 168)
ACCENT = "#59EC85"  # --ploy-accent-primary, oklch(84% .19 150)
BOX = 64
RADIUS = 14
MARK_SCALE = 1.06      # mark size in the rounded square
MASKABLE_SCALE = 0.86  # keeps the mark inside the 80% maskable safe zone
MONO_FONT = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Medium.ttf"

# Centreline: first anchor, then (control 1, control 2, anchor) per segment.
# Top-right terminal, over the top, down the left, across the spine, down the
# right, under the bottom, bottom-left terminal.
CENTRELINE = [
    (42.4, 21.0),
    ((41.4, 16.9), (36.4, 15.0), (31.4, 15.0)),
    ((26.2, 15.0), (22.6, 18.6), (22.6, 23.4)),
    ((22.6, 28.0), (26.8, 29.8), (32.0, 31.4)),
    ((37.6, 33.1), (42.6, 35.0), (42.6, 40.4)),
    ((42.6, 45.9), (38.2, 49.4), (32.4, 49.4)),
    ((26.6, 49.4), (22.4, 47.0), (21.0, 42.2)),
]
# Stroke width keyframes along the centreline (t in segments): thick spine,
# thin shoulders, medium terminals.
WIDTHS = [(0.0, 5.0), (0.5, 5.4), (1.0, 5.0), (1.5, 4.5), (2.0, 5.3), (3.0, 7.0),
          (4.0, 5.3), (4.5, 4.5), (5.0, 5.0), (5.5, 5.4), (6.0, 5.0)]


def bezier(p0, p1, p2, p3, t):
    u = 1 - t
    return (u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
            u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1])


def bezier_tangent(p0, p1, p2, p3, t):
    u = 1 - t
    return (3 * u * u * (p1[0] - p0[0]) + 6 * u * t * (p2[0] - p1[0]) + 3 * t * t * (p3[0] - p2[0]),
            3 * u * u * (p1[1] - p0[1]) + 6 * u * t * (p2[1] - p1[1]) + 3 * t * t * (p3[1] - p2[1]))


def width_at(t: float) -> float:
    for (t0, w0), (t1, w1) in zip(WIDTHS, WIDTHS[1:]):
        if t0 <= t <= t1:
            k = (1 - math.cos((t - t0) / (t1 - t0) * math.pi)) / 2
            return w0 + (w1 - w0) * k
    return WIDTHS[-1][1]


def outline(samples_per_segment: int = 12):
    """Offset the centreline both ways; returns the left and right edges."""
    left, right = [], []
    segments = CENTRELINE[1:]
    for i, (c1, c2, anchor) in enumerate(segments):
        p0 = CENTRELINE[0] if i == 0 else CENTRELINE[i][2]
        last = i == len(segments) - 1
        for j in range(samples_per_segment + (1 if last else 0)):
            t = j / samples_per_segment
            x, y = bezier(p0, c1, c2, anchor, t)
            dx, dy = bezier_tangent(p0, c1, c2, anchor, t)
            length = math.hypot(dx, dy)
            nx, ny = -dy / length, dx / length
            half = width_at(i + t) / 2
            left.append((x + nx * half, y + ny * half))
            right.append((x - nx * half, y - ny * half))
    return left, right


def fmt(p) -> str:
    return "%.2f %.2f" % p


def smooth_path(pts) -> str:
    """Cubic Bezier path through pts (uniform Catmull-Rom)."""
    n = len(pts)
    out = []
    for i in range(n - 1):
        p0, p1, p2, p3 = pts[max(i - 1, 0)], pts[i], pts[i + 1], pts[min(i + 2, n - 1)]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        out.append("C%s %s %s" % (fmt(c1), fmt(c2), fmt(p2)))
    return "".join(out)


def mark_path() -> str:
    left, right = outline()
    return "M" + fmt(left[0]) + smooth_path(left) + "L" + fmt(right[-1]) + smooth_path(list(reversed(right))) + "Z"


MARK = mark_path()


def svg(rounded: bool = True, scale: float = MARK_SCALE, hairline: bool = True) -> str:
    rx = RADIUS if rounded else 0
    offset = BOX / 2 * (1 - scale)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">',
        '<rect width="64" height="64" rx="%s" fill="%s"/>' % (rx, BG),
    ]
    if hairline and rounded:
        parts.append(
            '<rect x=".25" y=".25" width="63.5" height="63.5" rx="%s" fill="none" stroke="#fff" stroke-opacity=".06" stroke-width=".5"/>'
            % (rx - 0.25)
        )
    mark = '<path fill="%s" d="%s"/>' % (ACCENT, MARK)
    if scale != 1.0:
        mark = '<g transform="translate(%.2f %.2f) scale(%.3f)">%s</g>' % (offset, offset, scale, mark)
    parts.append(mark)
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def png(svg_text: str, size: int, supersample: int = 4) -> Image.Image:
    data = cairosvg.svg2png(bytestring=svg_text.encode(), output_width=size * supersample, output_height=size * supersample)
    im = Image.open(io.BytesIO(data)).convert("RGBA")
    return im.resize((size, size), Image.LANCZOS) if supersample > 1 else im


def write_icons(root: Path) -> None:
    (root / "favicon.svg").write_text(svg(), encoding="utf-8")
    png(svg(), 512).save(root / "icon-512.png", optimize=True)
    png(svg(), 192).save(root / "icon-192.png", optimize=True)
    png(svg(rounded=False), 180).save(root / "apple-touch-icon.png", optimize=True)
    png(svg(rounded=False, scale=MASKABLE_SCALE), 512).save(root / "icon-512-maskable.png", optimize=True)
    png(svg(rounded=False, scale=MASKABLE_SCALE), 192).save(root / "icon-192-maskable.png", optimize=True)
    frames = [png(svg(), s) for s in (16, 32, 48)]
    frames[-1].save(root / "favicon.ico", format="ICO", sizes=[(16, 16), (32, 32), (48, 48)], append_images=frames[:-1])


def write_previews(root: Path, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    png(svg(), 512).save(out / "favicon-512.png", optimize=True)
    font = ImageFont.truetype(MONO_FONT, 13)
    small = ImageFont.truetype(MONO_FONT, 11)
    ico = Image.open(root / "favicon.ico")
    frames = {}
    for s in (16, 32, 48):
        ico.size = (s, s)
        ico.load()
        frames[s] = ico.convert("RGBA").copy()
    rows = [("light tab, #FFFFFF", (255, 255, 255), (60, 64, 67)),
            ("dark tab, #202124", (32, 33, 36), (232, 234, 237))]
    zoom = 4
    col_w = [16 * zoom + 16 + 90, 32 * zoom + 32 + 90, 48 * zoom + 48 + 60]
    pad = 24
    width = pad * 2 + sum(col_w)
    row_h = 48 * zoom + 56
    height = pad + 36 + row_h * len(rows) + pad
    sheet = Image.new("RGBA", (width, height), (255, 255, 255, 255))
    draw = ImageDraw.Draw(sheet)
    x, y = pad, pad
    for s, cw in zip((16, 32, 48), col_w):
        draw.text((x, y), "%dpx, 1:1 and 4x" % s, font=font, fill=(60, 64, 67))
        x += cw
    y += 36
    for label, bg, fg in rows:
        draw.rectangle([0, y, width, y + row_h], fill=bg + (255,))
        draw.text((pad, y + 10), label, font=small, fill=fg)
        x = pad
        for s, cw in zip((16, 32, 48), col_w):
            frame = frames[s]
            top = y + 36
            sheet.alpha_composite(frame, (x, top + (48 * zoom - s) // 2))
            big = frame.resize((s * zoom, s * zoom), Image.NEAREST)
            sheet.alpha_composite(big, (x + s + 16, top + (48 * zoom - s * zoom) // 2))
            x += cw
        y += row_h
    sheet.convert("RGB").save(out / "favicon-sizes.png", optimize=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default=str(REPO), help="where the icon files go (default: repository root)")
    ap.add_argument("--previews", metavar="DIR", help="also write favicon-512.png and favicon-sizes.png to DIR")
    a = ap.parse_args()
    root = Path(a.root).resolve()
    write_icons(root)
    print("wrote favicon.svg, favicon.ico, apple-touch-icon.png, icon-192.png, icon-512.png and the maskable variants to", root)
    if a.previews:
        write_previews(root, Path(a.previews).resolve())
        print("wrote favicon-512.png and favicon-sizes.png to", a.previews)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
