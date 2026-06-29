#!/usr/bin/env python3
"""Create a book-specific cover for The Quartz Witness."""

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


def draw_quartz_case(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-quartz-witness-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(38*(1-t)+18*t), int(45*(1-t)+36*t), int(50*(1-t)+44*t), 255))

    # Mountain and mine ridge.
    draw.polygon([(0, 1020), (245, 720), (485, 930), (740, 600), (1045, 950), (1285, 700), (1600, 1025), (1600, 1765), (0, 1765)], fill=(56, 70, 72, 245))
    draw.polygon([(0, 1240), (300, 1120), (620, 1245), (940, 1080), (1290, 1230), (1600, 1135), (1600, 1765), (0, 1765)], fill=(74, 86, 82, 245))
    draw.polygon([(0, 1475), (410, 1395), (800, 1488), (1180, 1375), (1600, 1450), (1600, 1765), (0, 1765)], fill=(45, 54, 54, 248))

    # White quartz vein across the ridge.
    vein = [(115, 1308), (345, 1270), (565, 1328), (780, 1260), (1010, 1306), (1240, 1254), (1490, 1305)]
    for width, alpha in [(34, 80), (22, 150), (10, 245)]:
        for a, b in zip(vein, vein[1:]):
            draw.line((a[0], a[1], b[0], b[1]), fill=(236, 238, 224, alpha), width=width)

    # Evidence table.
    draw.rounded_rectangle((130, 1175, 1470, 1705), radius=24, fill=(29, 36, 35, 235), outline=(180, 190, 171, 140), width=4)
    draw.text((185, 1215), "ARBITRATION EXHIBIT: QW-16", font=font("arialbd.ttf", 36), fill=(222, 222, 196, 220))

    # Core trays with missing meter.
    tray_y = 1320
    for i in range(7):
        x0 = 190 + i * 150
        fill = (174, 177, 160, 235) if i != 3 else (31, 36, 34, 235)
        outline = (90, 97, 88, 210)
        draw.rounded_rectangle((x0, tray_y, x0 + 118, tray_y + 72), radius=12, fill=fill, outline=outline, width=3)
        if i != 3:
            draw.line((x0 + 10, tray_y + 36, x0 + 108, tray_y + 38), fill=(242, 240, 221, 200), width=10)
    draw.text((616, 1410), "MISSING METER", font=font("arialbd.ttf", 29), fill=(230, 108, 89, 230))

    # Broken quartz prism in evidence bag.
    bag = [(930, 1370), (1320, 1305), (1395, 1600), (1000, 1660)]
    draw.polygon(bag, fill=(214, 232, 226, 72), outline=(219, 239, 232, 160))
    prism = [(1085, 1425), (1210, 1392), (1290, 1480), (1240, 1580), (1095, 1606), (1015, 1504)]
    draw.polygon(prism, fill=(234, 236, 218, 235), outline=(85, 96, 92, 185))
    draw.line((1085, 1425, 1240, 1580), fill=(172, 178, 164, 160), width=4)
    draw.line((1210, 1392, 1095, 1606), fill=(172, 178, 164, 120), width=3)
    for x in range(1035, 1300, 28):
        draw.line((x, 1430 + random.randint(-22, 20), x + 55, 1520 + random.randint(-24, 24)), fill=(70, 62, 54, 78), width=2)
    draw.text((1038, 1620), "SAWED FACE", font=font("arialbd.ttf", 26), fill=(48, 59, 56, 230))

    # Seismic trace and spring line.
    draw.rounded_rectangle((190, 1520, 820, 1640), radius=18, fill=(5, 16, 17, 170), outline=(161, 224, 205, 130), width=3)
    last = None
    for x in range(220, 790, 14):
        spike = -62 if 475 < x < 515 else 0
        y = 1592 + int(math.sin(x * 0.045) * 18) + spike
        if last:
            draw.line((last[0], last[1], x, y), fill=(113, 236, 200, 230), width=4)
        last = (x, y)
    draw.text((215, 1537), "RESTORED SEISMIC HOUR", font=font("arialbd.ttf", 25), fill=(199, 238, 224, 220))
    draw.line((205, 1685, 1410, 1685), fill=(83, 142, 164, 180), width=7)
    for x in range(220, 1390, 120):
        draw.arc((x, 1660, x + 90, 1706), 0, 180, fill=(111, 177, 196, 150), width=3)
    draw.text((570, 1712), "SPRING COVENANT LINE", font=font("arialbd.ttf", 28), fill=(190, 216, 213, 205))

    # Boundary cairn and claim line.
    for i, (x, y, s) in enumerate([(315, 1115, 42), (350, 1080, 38), (385, 1118, 45), (362, 1045, 32)]):
        draw.ellipse((x - s, y - s//2, x + s, y + s//2), fill=(145, 150, 139, 235), outline=(71, 76, 70, 180), width=3)
    for offset in range(0, 1030, 92):
        draw.line((430 + offset, 1128 - offset * 0.17, 482 + offset, 1119 - offset * 0.17), fill=(235, 193, 74, 220), width=6)
    draw.text((235, 1168), "OLD CAIRN", font=font("arialbd.ttf", 31), fill=(232, 224, 187, 210))

    # Crystal dust.
    for _ in range(210):
        x = random.randint(130, 1470)
        y = random.randint(985, 1710)
        s = random.randint(1, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(238, 239, 219, random.randint(35, 135)))

    tagline = "FORENSIC GEOLOGY  CORE SAMPLES  WATER RIGHTS"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 300), tagline, font=tag_font, fill=(227, 226, 199, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Quartz Witness")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (38, 45, 50, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_quartz_case(draw)
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
