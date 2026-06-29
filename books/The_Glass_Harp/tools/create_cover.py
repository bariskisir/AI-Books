#!/usr/bin/env python3
"""Create a custom cover for The Glass Harp."""

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


def draw_concert_hall(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.48:
            c = lerp((13, 18, 28), (39, 49, 67), t / 0.48)
        else:
            c = lerp((39, 49, 67), (12, 10, 15), (t - 0.48) / 0.52)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Concert hall shell and warm stage.
    draw.polygon([(150, 1500), (1450, 1500), (1250, 520), (350, 520)], fill=(44, 30, 34, 245), outline=(144, 109, 84, 150))
    draw.polygon([(280, 1510), (1320, 1510), (1130, 835), (470, 835)], fill=(171, 112, 66, 220))
    for i in range(18):
        y = 840 + i * 36
        draw.arc((240 + i * 5, y, 1360 - i * 5, y + 260), 200, 340, fill=(96, 60, 45, 95), width=4)

    # Suspended glass acoustic canopy, with one fractured section.
    canopy = [(315, 430), (1285, 380), (1390, 665), (225, 730)]
    draw.polygon(canopy, fill=(174, 208, 220, 92), outline=(225, 238, 232, 185))
    for x in range(345, 1300, 120):
        draw.line((x, 415, x + 120, 700), fill=(235, 244, 226, 120), width=5)
    broken = [(835, 405), (1010, 398), (1048, 552), (956, 623), (880, 560)]
    draw.polygon(broken, fill=(40, 50, 62, 170), outline=(240, 250, 236, 210))
    for _ in range(38):
        x = random.randint(835, 1050)
        y = random.randint(430, 675)
        draw.line((x, y, x + random.randint(-55, 55), y + random.randint(35, 120)), fill=(231, 246, 240, random.randint(75, 160)), width=random.randint(2, 5))

    # Falling glass fragments over the stage.
    for _ in range(90):
        cx = random.randint(500, 1120)
        cy = random.randint(725, 1320)
        size = random.randint(8, 32)
        pts = [(cx, cy), (cx + random.randint(-size, size), cy + random.randint(5, size * 2)), (cx + random.randint(-size, size), cy + random.randint(-size, size))]
        draw.polygon(pts, fill=(197, 232, 235, random.randint(55, 125)), outline=(240, 248, 238, random.randint(45, 120)))

    # Frequency graph across the hall, with one dangerous spike.
    graph = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(graph, "RGBA")
    base = 1185
    prev = None
    for i in range(180):
        x = 135 + i * 7
        amp = 30 * math.sin(i * 0.22) + 14 * math.sin(i * 0.61)
        if 91 <= i <= 98:
            amp -= 330 * (1 - abs(i - 94.5) / 4.5)
        y = base + amp
        if prev:
            gd.line((prev[0], prev[1], x, y), fill=(245, 218, 116, 210), width=7)
        prev = (x, y)
    graph = graph.filter(ImageFilter.GaussianBlur(0.7))
    draw.bitmap((0, 0), graph, fill=None)

    # Music stand and altered score.
    draw.rectangle((510, 1320, 1090, 1510), fill=(232, 226, 200, 238), outline=(72, 58, 48, 180), width=4)
    staff_y = 1360
    for row in range(5):
        draw.line((555, staff_y + row * 18, 1042, staff_y + row * 18), fill=(42, 42, 48, 210), width=3)
    for x in (640, 760, 860):
        draw.ellipse((x, 1405, x + 26, 1424), fill=(32, 32, 38, 225))
        draw.line((x + 24, 1413, x + 24, 1342), fill=(32, 32, 38, 225), width=4)
    draw.line((930, 1350, 930, 1460), fill=(155, 18, 30, 240), width=7)
    draw.text((948, 1368), "sustained note", font=font("arial.ttf", 31), fill=(120, 28, 34, 230))

    # Cable lines and empty seats.
    for x in range(370, 1260, 145):
        draw.line((x, 0, x + 80, 430), fill=(214, 220, 204, 80), width=3)
    for row in range(9):
        y = 1510 - row * 54
        for col in range(13 - row // 2):
            x = 205 + col * 92 + row * 22
            draw.ellipse((x, y, x + 58, y + 28), fill=(35, 20, 24, 210), outline=(116, 70, 54, 90))

    tagline = "ACOUSTICS  GLASS  HIDDEN RESONANCE"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 275), tagline, font=tag_font, fill=(231, 220, 180, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Glass Harp")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("the-glass-harp-cover")
    image = Image.new("RGBA", (W, H), (14, 14, 18, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_concert_hall(draw)
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
