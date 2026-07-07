#!/usr/bin/env python3
"""Cover: The Perfumier's Cipher — marble quarry chapel at dusk, glass vial of pale gold perfume on altar, lapis-blue mosaic, cracked roof light."""

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
PANEL_Y = 1765


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m.get("title", "The Perfumier's Cipher")
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    random.seed("perfumiers-cipher")
    img = Image.new("RGBA", (W, H), (18, 16, 32, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dusk sky over quarry: indigo to amber
    for y in range(1000):
        t = y / 1000
        if t < 0.5:
            c = lerp((22, 20, 50), (70, 50, 80), t / 0.5)
        else:
            c = lerp((70, 50, 80), (190, 120, 70), (t - 0.5) / 0.5)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Marble quarry chapel silhouette
    cx = W // 2
    # Chapel walls
    draw.polygon([(cx - 300, 1000), (cx - 250, 450), (cx + 250, 450), (cx + 300, 1000)], fill=(168, 160, 148, 255))
    draw.polygon([(cx - 260, 450), (cx, 360), (cx + 260, 450)], fill=(140, 132, 120, 255))
    draw.line((cx - 260, 450, cx + 260, 450), fill=(184, 176, 164, 255), width=3)
    # Cracked roof with lapis-blue light
    draw.polygon([(cx - 80, 400), (cx - 40, 370), (cx + 40, 375), (cx + 80, 395)], fill=(60, 80, 160, 100))
    # Light beam through crack
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(cx - 20, 380), (cx + 20, 380), (cx + 120, 1200), (cx - 120, 1200)], fill=(80, 120, 220, 25))
    beam = beam.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # Altar
    draw.rectangle((cx - 100, 980, cx + 100, 1050), fill=(200, 194, 182, 255))
    draw.rectangle((cx - 90, 1050, cx + 90, 1070), fill=(180, 174, 162, 255))

    # Glass vial on altar
    vx, vy = cx, 880
    # Glow
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(g)
    gd.ellipse((vx - 60, vy - 40, vx + 60, vy + 160), fill=(230, 210, 140, 35))
    g = g.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img, g)
    draw = ImageDraw.Draw(img, "RGBA")
    # Vial body
    draw.rounded_rectangle((vx - 20, vy, vx + 20, vy + 140), radius=8, fill=(230, 228, 220, 90), outline=(190, 188, 200, 150), width=2)
    # Pale gold liquid
    draw.rounded_rectangle((vx - 15, vy + 30, vx + 15, vy + 135), radius=6, fill=(224, 198, 120, 230))
    draw.rounded_rectangle((vx - 8, vy + 60, vx + 8, vy + 120), radius=4, fill=(240, 218, 150, 180))
    # Neck and stopper
    draw.rectangle((vx - 8, vy - 30, vx + 8, vy), fill=(230, 228, 220, 90))
    draw.rectangle((vx - 10, vy - 44, vx + 10, vy - 30), fill=(162, 140, 108, 255))
    # Highlight
    draw.line((vx - 14, vy + 10, vx - 14, vy + 130), fill=(255, 255, 255, 80), width=2)

    # Lapis-blue mosaic floor
    for i in range(12):
        for j in range(6):
            mx = 200 + j * 200 + (i % 2) * 100
            my = 1180 + i * 50
            if mx < W - 100:
                draw.rectangle((mx, my, mx + 80, my + 40), fill=(
                    random.randint(30, 60), random.randint(40, 80), random.randint(120, 180), 180))

    # Foreground marble quarry walls
    draw.polygon([(0, 1000), (0, 1800), (200, 1800), (300, 1100)], fill=(148, 144, 132, 200))
    draw.polygon([(W, 1000), (W, 1800), (1400, 1800), (1300, 1100)], fill=(148, 144, 132, 200))

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
