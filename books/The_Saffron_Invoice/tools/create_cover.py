#!/usr/bin/env python3
"""Create a custom cover for The Saffron Invoice."""

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


def draw_restaurant_scene(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.48:
            c = lerp((22, 18, 20), (82, 48, 36), t / 0.48)
        else:
            c = lerp((82, 48, 36), (24, 18, 17), (t - 0.48) / 0.52)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Stainless pass and warm kitchen tile.
    draw.rectangle((0, 1230, W, PANEL_Y), fill=(76, 78, 76, 245))
    draw.rectangle((150, 560, 1450, 1265), fill=(214, 198, 166, 232), outline=(78, 58, 42, 170), width=5)
    for x in range(170, 1440, 125):
        draw.line((x, 570, x + random.randint(-20, 20), 1255), fill=(128, 100, 70, 75), width=2)
    for y in range(640, 1230, 95):
        draw.line((165, y, 1435, y + random.randint(-8, 8)), fill=(128, 100, 70, 68), width=2)

    # Saffron tin and adulterated oil bottle.
    draw.rounded_rectangle((245, 765, 620, 1135), radius=28, fill=(154, 28, 36, 245), outline=(230, 190, 88, 200), width=7)
    draw.rectangle((285, 835, 580, 1030), fill=(238, 218, 150, 235), outline=(80, 48, 34, 180), width=4)
    draw.text((320, 875), "NOOR", font=font("arialbd.ttf", 54), fill=(92, 38, 32, 235))
    draw.text((320, 938), "IMPERIAL", font=font("arialbd.ttf", 36), fill=(92, 38, 32, 230))
    draw.text((320, 982), "LOT IN-772", font=font("arial.ttf", 28), fill=(136, 46, 42, 230))
    draw.rectangle((365, 1070, 560, 1110), fill=(238, 226, 186, 230))
    draw.text((378, 1078), "MX-SF-14B", font=font("arialbd.ttf", 25), fill=(160, 28, 36, 235))

    draw.rounded_rectangle((990, 735, 1170, 1180), radius=45, fill=(222, 154, 42, 205), outline=(246, 218, 122, 190), width=5)
    draw.rectangle((1030, 655, 1130, 760), fill=(68, 58, 52, 235))
    draw.text((1018, 1195), "ALMOND", font=font("arialbd.ttf", 33), fill=(235, 214, 154, 230))
    draw.text((1027, 1234), "CARRIER", font=font("arial.ttf", 28), fill=(235, 214, 154, 220))

    # Invoice sheet with forged stamp.
    draw.polygon([(640, 650), (950, 620), (990, 1118), (675, 1160)], fill=(242, 233, 205, 240), outline=(82, 66, 46, 160))
    draw.text((690, 700), "INVOICE", font=font("arialbd.ttf", 42), fill=(52, 46, 38, 235))
    for i in range(8):
        y = 780 + i * 42
        draw.line((690, y, 930, y - 20), fill=(80, 68, 52, 130), width=3)
    draw.ellipse((765, 950, 940, 1085), outline=(180, 32, 40, 210), width=8)
    draw.text((795, 994), "FORGED", font=font("arialbd.ttf", 29), fill=(180, 32, 40, 220))

    # Plate at pass with saffron rice and red/yellow adulterated threads.
    draw.ellipse((430, 1260, 1170, 1605), fill=(232, 228, 214, 245), outline=(102, 96, 86, 160), width=8)
    draw.ellipse((515, 1318, 1085, 1548), fill=(218, 168, 54, 235))
    for _ in range(170):
        x = random.randint(545, 1060)
        y = random.randint(1340, 1530)
        if ((x - 800) / 285) ** 2 + ((y - 1435) / 115) ** 2 <= 1:
            col = random.choice([(190, 28, 30, 220), (238, 190, 50, 200), (138, 64, 26, 190)])
            draw.line((x, y, x + random.randint(-12, 12), y + random.randint(-5, 8)), fill=col, width=random.randint(2, 4))

    # Allergy alert card and chain arrows.
    draw.rectangle((1185, 1275, 1415, 1455), fill=(244, 232, 194, 235), outline=(130, 42, 42, 170), width=4)
    draw.text((1212, 1310), "ALLERGEN", font=font("arialbd.ttf", 33), fill=(138, 28, 34, 235))
    draw.text((1212, 1355), "ALMOND", font=font("arialbd.ttf", 39), fill=(138, 28, 34, 235))
    draw.line((620, 945, 690, 900), fill=(220, 176, 68, 180), width=6)
    draw.line((950, 900, 1015, 945), fill=(220, 176, 68, 180), width=6)
    draw.line((1070, 1180, 930, 1330), fill=(220, 176, 68, 180), width=6)

    # Steam and spice dust.
    cloud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud, "RGBA")
    for _ in range(32):
        x = random.randint(400, 1120)
        y = random.randint(1120, 1400)
        cd.arc((x - 160, y - 70, x + 160, y + 100), 190, 360, fill=(236, 220, 180, random.randint(28, 70)), width=random.randint(5, 13))
    cloud = cloud.filter(ImageFilter.GaussianBlur(1.7))
    draw.bitmap((0, 0), cloud, fill=None)
    for _ in range(210):
        x = random.randint(210, 1390)
        y = random.randint(560, 1570)
        s = random.randint(2, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(240, 178, 45, random.randint(45, 140)))

    tagline = "FOOD FRAUD  SAFFRON  SUPPLY CHAIN"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(238, 220, 176, 232))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Saffron Invoice")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("the-saffron-invoice-cover")
    image = Image.new("RGBA", (W, H), (18, 16, 16, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_restaurant_scene(draw)
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
