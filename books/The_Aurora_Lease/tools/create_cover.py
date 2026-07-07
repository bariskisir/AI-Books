#!/usr/bin/env python3
"""Create a book-specific cover for The Aurora Lease."""

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
FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    for candidate in (FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_aurora_field(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-aurora-lease-cover")
    for y in range(H):
        t = y / H
        r = int(7 * (1 - t) + 17 * t)
        g = int(18 * (1 - t) + 34 * t)
        b = int(43 * (1 - t) + 52 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Star field and polar haze.
    for _ in range(290):
        x = random.randint(0, W)
        y = random.randint(50, 1010)
        a = random.randint(45, 190)
        s = random.choice([1, 1, 2, 2, 3])
        draw.ellipse((x, y, x + s, y + s), fill=(220, 241, 236, a))

    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora, "RGBA")
    bands = [
        ((72, 246, 169, 84), 205, 34, 0.010, 0.8),
        ((114, 201, 248, 70), 330, 42, 0.012, 2.4),
        ((205, 118, 239, 42), 475, 58, 0.009, 4.7),
    ]
    for color, base, amp, freq, phase in bands:
        points = []
        for x in range(-80, W + 120, 20):
            y = base + math.sin(x * freq + phase) * amp + math.sin(x * 0.003 + phase) * 50
            points.append((x, y))
        lower = [(x, y + 460 + math.sin(x * 0.015) * 42) for x, y in reversed(points)]
        ad.polygon(points + lower, fill=color)
        for x, y in points[::2]:
            ad.line((x, y - 18, x + random.randint(-35, 35), y + random.randint(260, 520)), fill=color, width=random.randint(8, 22))
    aurora = aurora.filter(ImageFilter.GaussianBlur(11))
    draw.bitmap((0, 0), aurora)

    # Snow ridge and protected valley.
    ridge = [(0, 1325), (180, 1262), (360, 1300), (535, 1190), (720, 1265), (910, 1135), (1120, 1238), (1300, 1168), (1600, 1275), (1600, 1765), (0, 1765)]
    draw.polygon(ridge, fill=(194, 213, 220, 245))
    draw.polygon([(0, 1430), (235, 1380), (560, 1440), (850, 1345), (1165, 1400), (1600, 1360), (1600, 1765), (0, 1765)], fill=(123, 151, 164, 238))
    draw.polygon([(0, 1575), (290, 1535), (630, 1592), (1040, 1505), (1600, 1588), (1600, 1765), (0, 1765)], fill=(70, 92, 106, 245))

    # Station domes, mast, and magnetometer hut on Lease Ridge.
    draw.rectangle((242, 1110, 705, 1328), fill=(38, 54, 62, 240))
    draw.pieslice((242, 955, 705, 1265), 180, 360, fill=(57, 80, 88, 242), outline=(176, 208, 211, 180), width=4)
    draw.rectangle((352, 1048, 432, 1122), fill=(232, 221, 147, 135))
    draw.rectangle((520, 1070, 600, 1148), fill=(232, 221, 147, 105))
    draw.line((788, 710, 788, 1285), fill=(206, 227, 228, 220), width=7)
    for yy in range(820, 1230, 95):
        draw.line((736, yy, 840, yy + 38), fill=(152, 186, 190, 180), width=4)
    draw.rectangle((855, 1185, 1118, 1348), fill=(42, 63, 70, 245), outline=(170, 205, 205, 140), width=4)
    draw.text((890, 1222), "MAG", font=font("arialbd.ttf", 46), fill=(202, 236, 225, 210))
    draw.text((889, 1277), "ARRAY", font=font("arial.ttf", 34), fill=(202, 236, 225, 180))

    # Lease line, buried cairn, and illegal pulse wells.
    lease_color = (242, 198, 78, 215)
    for offset in range(0, 1010, 92):
        draw.line((165 + offset, 1506 - offset * 0.16, 218 + offset, 1496 - offset * 0.16), fill=lease_color, width=6)
    for x, y in [(1025, 1430), (1110, 1412), (1198, 1398)]:
        draw.ellipse((x - 22, y - 22, x + 22, y + 22), fill=(255, 111, 89, 220))
        for r in (42, 76, 118):
            draw.ellipse((x - r, y - r, x + r, y + r), outline=(255, 111, 89, max(35, 150 - r)), width=4)
    for i, (x, y) in enumerate([(602, 1362), (625, 1328), (655, 1374), (681, 1339), (710, 1383)]):
        draw.ellipse((x - 22, y - 13, x + 22, y + 13), fill=(96, 104, 103, 240), outline=(214, 225, 218, 100), width=2)
    draw.text((565, 1410), "OLD CAIRN", font=font("arialbd.ttf", 31), fill=(221, 230, 221, 175))

    # Migrating herd marks and collar silence.
    for x in range(165, 570, 72):
        y = 1535 + int(math.sin(x * 0.04) * 18)
        draw.ellipse((x, y, x + 13, y + 26), fill=(29, 45, 48, 190))
        draw.ellipse((x + 22, y + 8, x + 35, y + 34), fill=(29, 45, 48, 190))
    draw.rounded_rectangle((1235, 1510, 1442, 1606), radius=18, fill=(26, 40, 44, 215), outline=(115, 225, 191, 130), width=3)
    draw.text((1263, 1530), "COLLAR", font=font("arialbd.ttf", 28), fill=(168, 231, 214, 205))
    draw.text((1278, 1570), "NO SIGNAL", font=font("arial.ttf", 24), fill=(240, 127, 108, 210))

    # Data trace overlay.
    trace_y = 1648
    draw.rounded_rectangle((165, 1588, 1435, 1710), radius=20, fill=(6, 20, 26, 150), outline=(92, 224, 184, 110), width=3)
    last = None
    for x in range(195, 1405, 16):
        spike = 0
        if 840 < x < 1010 or 1105 < x < 1220:
            spike = random.randint(-70, 42)
        y = trace_y + int(math.sin(x * 0.035) * 18) + spike
        if last:
            draw.line((last[0], last[1], x, y), fill=(107, 247, 188, 220), width=4)
        last = (x, y)
    draw.text((200, 1605), "MAGNETOMETER PULSE / LEASE RIDGE", font=font("arialbd.ttf", 28), fill=(198, 242, 224, 205))

    tagline = "POLAR RESEARCH  SHIFTED BOUNDARY  GREEN SKY"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 300), tagline, font=tag_font, fill=(221, 246, 229, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Aurora Lease")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (7, 18, 43, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_aurora_field(draw)
    _draw_standard_cover_title_panel(image, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
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
