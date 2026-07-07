#!/usr/bin/env python3
"""Cover: The Sapphire Throat — neon SAPPHIRE sign above dark alley, woman in silver dress backlit, art deco lettering."""

from __future__ import annotations
import argparse, json, math, random
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
    for c in [FONT_DIR / name, FONT_DIR / "arial.ttf", FONT_DIR / "georgia.ttf"]:
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

    # Dark alley gradient
    for y in range(H):
        t = y / H
        if t < 0.4:
            r, g, b = 8, 6, 20
        elif t < 0.7:
            r, g, b = int(8 + 40 * (t - 0.4) / 0.3), int(6 + 30 * (t - 0.4) / 0.3), int(20 - 5 * (t - 0.4) / 0.3)
        else:
            r, g, b = int(48 + 20 * (t - 0.7) / 0.3), int(36 + 15 * (t - 0.7) / 0.3), int(15 - 5 * (t - 0.7) / 0.3)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Neon SAPPHIRE sign
    nsx, nsy = W // 2, 200
    # Neon glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(120, 10, -5):
        gd.ellipse((nsx - r, nsy - r, nsx + r, nsy + r), fill=(80, 140, 255, max(0, 20 - (120 - r) // 6)))
    glow = glow.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Sapphire text - art deco style
    sf = font("arialbd.ttf", 80)
    text = "SAPPHIRE"
    bb = draw.textbbox((0, 0), text, font=sf)
    draw.text((nsx - (bb[2] - bb[0]) // 2, nsy - (bb[3] - bb[1]) // 2), text, font=sf, fill=(80, 160, 255, 230))
    draw.text((nsx - (bb[2] - bb[0]) // 2 + 2, nsy - (bb[3] - bb[1]) // 2 + 2), text, font=sf, fill=(40, 100, 220, 120))
    # Art deco lines framing sign
    draw.line((nsx - 200, nsy - 30, nsx - 120, nsy - 30), fill=(80, 160, 255, 100), width=3)
    draw.line((nsx + 120, nsy - 30, nsx + 200, nsy - 30), fill=(80, 160, 255, 100), width=3)
    draw.line((nsx - 200, nsy + 50, nsx - 120, nsy + 50), fill=(80, 160, 255, 100), width=3)
    draw.line((nsx + 120, nsy + 50, nsx + 200, nsy + 50), fill=(80, 160, 255, 100), width=3)

    # Dark alley walls
    draw.polygon([(0, 0), (0, 1800), (300, 1800), (500, 800), (400, 0)], fill=(22, 20, 25, 200))
    draw.polygon([(W, 0), (W, 1800), (1300, 1800), (1100, 800), (1200, 0)], fill=(22, 20, 25, 200))

    # Woman in silver dress (backlit, center)
    wx, wy = W // 2, 900
    # Dress silhouette
    draw.polygon([(wx - 30, wy), (wx - 80, wy + 320), (wx + 80, wy + 320), (wx + 30, wy)], fill=(8, 6, 10, 220))
    # Torso
    draw.polygon([(wx - 20, wy), (wx + 20, wy), (wx + 25, wy + 120), (wx - 25, wy + 120)], fill=(8, 6, 10, 220))
    # Head
    draw.ellipse((wx - 18, wy - 40, wx + 18, wy), fill=(8, 6, 10, 220))
    # Silver dress edge highlight (backlit)
    draw.line((wx - 80, wy + 320, wx - 30, wy), fill=(180, 190, 200, 60), width=2)
    draw.line((wx + 80, wy + 320, wx + 30, wy), fill=(180, 190, 200, 60), width=2)

    # Wet asphalt reflection (neon blue on ground)
    for y in range(1400, 1800, 2):
        alpha = int(15 * (1 - (y - 1400) / 400))
        draw.line((300, y, 1300, y), fill=(40, 120, 255, alpha + 10))

    # Rain
    rng = random.Random(42)
    for _ in range(200):
        rx = rng.randint(0, W)
        ry = rng.randint(0, 1800)
        rl = rng.randint(15, 40)
        draw.line((rx, ry, rx - 1, ry + rl), fill=(160, 165, 180, rng.randint(15, 40)), width=1)

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