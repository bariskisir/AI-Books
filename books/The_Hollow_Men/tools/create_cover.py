#!/usr/bin/env python3
"""Cover: The Hollow Men — Ridgeline at dusk, one figure at tree line, shadow stretching impossibly toward doomed town."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= mw:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dusk sky gradient: twilight purple to deep green
    rng = __import__("random").Random(7)
    for y in range(H):
        t = y / H
        r = int(110 - 80 * t)
        g = int(70 - 40 * t)
        b = int(120 - 80 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Ridgeline silhouette
    ridge_pts = [(0, 1200)]
    for x in range(0, W + 10, 10):
        y = 1200 - int(80 * abs(__import__("math").sin(x * 0.008 + 0.3)) + 40 * abs(__import__("math").sin(x * 0.015 + 1.7)))
        ridge_pts.append((x, y))
    ridge_pts.append((W, 1200))
    ridge_pts.append((W, H))
    ridge_pts.append((0, H))
    draw.polygon(ridge_pts, fill=(25, 30, 28, 220))

    # Tree line at ridge
    for x in range(0, W, 15):
        th = 40 + int(60 * abs(__import__("math").sin(x * 0.05 + 0.8)))
        draw.line((x, 1200 - 20, x, 1200 - 20 - th), fill=(10, 12, 10, 220), width=4)

    # Single figure at tree line
    fx, fy = W // 2 - 40, 1180
    # Body
    draw.ellipse((fx - 15, fy - 50, fx + 15, fy + 10), fill=(5, 5, 5, 230))
    draw.ellipse((fx - 8, fy - 65, fx + 8, fy - 48), fill=(5, 5, 5, 230))

    # Impossibly long shadow stretching toward valley
    shadow_len = 500
    for i in range(3):
        swo = int(shadow_len * (0.85 + 0.15 * i))
        draw.line((fx, fy + 10, fx - 40 - i * 20, fy + 10 + swo), fill=(5, 5, 5, 40 - i * 10), width=8 - i * 2)
    draw.line((fx, fy + 10, fx - 80, fy + 10 + shadow_len), fill=(5, 5, 5, 60), width=10)

    # Doomed town silhouette in valley
    town_base = 1400
    for bx in range(100, W - 100, 45):
        bh = 30 + int(rng.random() * 80)
        draw.rectangle((bx, town_base - bh, bx + 30, town_base), fill=(15, 12, 10, 180))
        if rng.random() > 0.6:
            draw.rectangle((bx + 5, town_base - bh + 10, bx + 12, town_base - bh + 20), fill=(180, 100, 60, 40))

    # Church spire
    spire_x = W // 2 + 100
    draw.polygon([(spire_x - 10, town_base), (spire_x + 10, town_base), (spire_x, town_base - 120)], fill=(15, 12, 10, 180))
    draw.line((spire_x, town_base - 120, spire_x, town_base - 150), fill=(15, 12, 10, 150), width=3)

    # Fog haze in valley
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(30):
        fx2 = int(rng.random() * W)
        fy2 = int(1200 + 500 * rng.random())
        fw = int(150 + 300 * rng.random())
        fh = int(30 + 60 * rng.random())
        fd.ellipse((fx2 - fw // 2, fy2 - fh // 2, fx2 + fw // 2, fy2 + fh // 2), fill=(140, 150, 140, 15))
    fog = fog.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)



def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()