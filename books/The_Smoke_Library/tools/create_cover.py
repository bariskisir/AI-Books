#!/usr/bin/env python3
"""Create a custom cover for The Smoke Library."""

from __future__ import annotations

import argparse
import json
import math
import random
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
W, H = 1600, 2560
PANEL_Y = 1765
FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_library_fire(draw: ImageDraw.ImageDraw) -> None:
    # Smoke-dark reading room with a low smoke band that mirrors the investigation clue.
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.42:
            c = lerp((12, 18, 24), (35, 43, 48), t / 0.42)
        elif t < 0.72:
            c = lerp((35, 43, 48), (70, 64, 54), (t - 0.42) / 0.30)
        else:
            c = lerp((70, 64, 54), (24, 18, 17), (t - 0.72) / 0.28)
        draw.line((0, y, W, y), fill=(*c, 255))

    for y in range(900, 1220, 8):
        alpha = int(120 * (1 - abs(y - 1060) / 190))
        draw.line((0, y, W, y), fill=(18, 22, 22, max(0, alpha)), width=9)

    # Broken skylight and pale ash light from above.
    draw.polygon([(540, 110), (1070, 70), (1170, 250), (445, 305)], fill=(154, 172, 168, 70), outline=(218, 214, 184, 120))
    for x in range(520, 1120, 90):
        draw.line((x, 95, x + 120, 285), fill=(224, 218, 190, 55), width=4)
    for i in range(18):
        x = random.randint(480, 1160)
        draw.line((x, 260, x - random.randint(120, 260), 990), fill=(235, 218, 172, random.randint(16, 32)), width=random.randint(3, 7))

    # Tall shelving bays, warped by heat.
    shelf_colors = [(64, 41, 31), (78, 50, 35), (48, 34, 29), (95, 60, 38)]
    for bay, x in enumerate(range(120, 1490, 245)):
        lean = random.randint(-18, 18)
        draw.polygon([(x, 390), (x + 180, 385 + lean), (x + 205, 1530), (x - 18, 1535)], fill=(30, 24, 22, 235), outline=(117, 82, 55, 120))
        for shelf_y in range(500, 1450, 145):
            draw.line((x - 10, shelf_y, x + 200, shelf_y + lean // 2), fill=(116, 78, 48, 190), width=10)
            for k in range(9):
                bx = x + 5 + k * 20 + random.randint(-2, 2)
                top = shelf_y - random.randint(55, 112)
                bottom = shelf_y - 8
                col = random.choice(shelf_colors)
                if random.random() < 0.28:
                    col = (18, 17, 16)
                draw.rectangle((bx, top, bx + random.randint(10, 18), bottom), fill=(*col, 230))

    # Charred central table with surviving evidence.
    draw.polygon([(330, 1390), (1275, 1365), (1450, 1585), (210, 1610)], fill=(42, 30, 24, 245), outline=(122, 84, 55, 160))
    draw.line((310, 1438, 1286, 1414), fill=(176, 122, 64, 120), width=5)
    draw.rectangle((520, 1430, 900, 1540), fill=(229, 222, 190, 230), outline=(72, 56, 45, 180), width=3)
    draw.text((548, 1455), "V-9 HOLDING", font=font("arialbd.ttf", 34), fill=(56, 45, 38, 235))
    draw.text((550, 1498), "DO NOT ERASE", font=font("arial.ttf", 28), fill=(92, 54, 43, 220))

    # Sprinkler head and red seal wax, specific to the case evidence.
    draw.ellipse((1085, 1425, 1235, 1575), fill=(52, 58, 58, 255), outline=(194, 180, 138, 170), width=5)
    for a in range(0, 360, 45):
        r = math.radians(a)
        draw.line((1160, 1500, 1160 + 92 * math.cos(r), 1500 + 92 * math.sin(r)), fill=(170, 152, 112, 160), width=5)
    draw.ellipse((1126, 1466, 1194, 1534), fill=(112, 120, 112, 255))
    draw.ellipse((960, 1505, 1038, 1578), fill=(145, 26, 28, 245), outline=(80, 15, 18, 210), width=4)
    draw.line((999, 1542, 1088, 1448), fill=(145, 26, 28, 185), width=5)

    # Smoke curls and ash flecks.
    smoke = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke, "RGBA")
    for i in range(42):
        x = random.randint(20, W - 80)
        y = random.randint(340, 1320)
        w = random.randint(220, 520)
        h = random.randint(42, 110)
        sd.arc((x - w // 2, y - h // 2, x + w // 2, y + h // 2), random.randint(160, 240), random.randint(300, 380), fill=(190, 186, 166, random.randint(18, 48)), width=random.randint(5, 13))
    smoke = smoke.filter(ImageFilter.GaussianBlur(2.2))
    draw.bitmap((0, 0), smoke, fill=None)
    for _ in range(260):
        x = random.randint(0, W)
        y = random.randint(120, PANEL_Y - 80)
        s = random.randint(1, 4)
        draw.rectangle((x, y, x + s, y + s), fill=(230, 218, 185, random.randint(35, 115)))

    tagline = "ARSON  RARE BOOKS  INSURANCE FRAUD"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 315), tagline, font=tag_font, fill=(228, 216, 180, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Smoke Library")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("the-smoke-library-cover")
    image = Image.new("RGBA", (W, H), (16, 16, 18, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_library_fire(draw)
    _draw_standard_cover_title_panel(
        image,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "PNG", optimize=True)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
