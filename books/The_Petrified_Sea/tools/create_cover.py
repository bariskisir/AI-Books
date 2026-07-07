#!/usr/bin/env python3
"""Cover: The Petrified Sea — chalk bluff with white quarry scar under prairie sky, lone rider below."""

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
    title = m.get("title", "The Petrified Sea")
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    random.seed("petrified-sea")
    img = Image.new("RGBA", (W, H), (20, 24, 40, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Prairie sky gradient
    for y in range(1050):
        t = y / 1050
        if t < 0.6:
            c = lerp((24, 30, 55), (90, 72, 90), t / 0.6)
        else:
            c = lerp((90, 72, 90), (220, 140, 90), (t - 0.6) / 0.4)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Prairie flats
    draw.rectangle((0, 1050, W, 1120), fill=(90, 72, 68, 255))
    draw.rectangle((0, 1050, W, 1056), fill=(200, 160, 110, 200))

    # Chalk bluff with white quarry scar
    draw.polygon([(0, 1080), (100, 1060), (300, 1070), (600, 1050), (900, 1060),
                  (1200, 1040), (W, 1050), (W, 1800), (0, 1800)], fill=(210, 200, 185, 255))
    # Quarry scar - bright white rectangle
    draw.rectangle((400, 1200, 900, 1500), fill=(240, 238, 230, 255))
    draw.rectangle((390, 1190, 910, 1510), outline=(180, 170, 155, 255), width=4)
    # Scar strata lines
    for sy in range(1220, 1500, 35):
        wob = random.randint(-4, 4)
        draw.line((410, sy + wob, 890, sy + wob), fill=(200, 196, 186, 120), width=2)

    # Lone rider on horse
    rx, ry = 750, 1580
    # Horse body
    draw.ellipse((rx - 25, ry - 15, rx + 25, ry + 10), fill=(35, 30, 28, 230))
    draw.ellipse((rx + 20, ry - 30, rx + 45, ry - 5), fill=(35, 30, 28, 230))
    draw.line((rx - 10, ry + 5, rx + 5, ry + 35), fill=(35, 30, 28, 230), width=5)
    draw.line((rx + 25, ry + 5, rx + 15, ry + 35), fill=(35, 30, 28, 230), width=5)
    # Rider
    draw.ellipse((rx + 22, ry - 55, rx + 38, ry - 35), fill=(30, 25, 22, 230))
    draw.line((rx + 30, ry - 35, rx + 28, ry - 5), fill=(30, 25, 22, 230), width=5)
    # Rider shadow
    draw.ellipse((rx - 20, ry + 35, rx + 40, ry + 42), fill=(50, 42, 36, 100))

    # Foreground grass
    for _ in range(50):
        gx = random.randint(0, W)
        gy = random.randint(1650, 1800)
        for _ in range(3):
            draw.line((gx, gy, gx + random.randint(-8, 8), gy - random.randint(6, 16)), fill=(80, 68, 48, 200), width=2)

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
