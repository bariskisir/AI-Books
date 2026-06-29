#!/usr/bin/env python3
"""Create a book-specific cover for The Tidal Pharmacy."""

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


def draw_tidal_pharmacy(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-tidal-pharmacy-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(18*(1-t)+9*t), int(52*(1-t)+71*t), int(72*(1-t)+92*t), 255))

    # Harbor and islands.
    draw.rectangle((0, 1060, W, 1765), fill=(30, 86, 101, 245))
    for y0 in range(1120, 1700, 90):
        draw.arc((-80, y0, 360, y0 + 130), 0, 180, fill=(117, 187, 195, 85), width=4)
        draw.arc((420, y0 + 30, 920, y0 + 160), 0, 180, fill=(117, 187, 195, 70), width=4)
        draw.arc((1000, y0 - 15, 1660, y0 + 145), 0, 180, fill=(117, 187, 195, 78), width=4)
    draw.polygon([(0, 990), (300, 870), (640, 965), (1040, 850), (1600, 1015), (1600, 1180), (0, 1180)], fill=(36, 71, 66, 235))
    draw.rectangle((150, 1200, 1445, 1282), fill=(78, 62, 48, 245))
    for x in range(180, 1420, 120):
        draw.rectangle((x, 1265, x + 28, 1595), fill=(55, 47, 40, 245))

    # Pharmacy cold crate and public seal.
    draw.rounded_rectangle((235, 760, 860, 1210), radius=34, fill=(219, 236, 236, 240), outline=(55, 95, 103, 210), width=6)
    draw.rectangle((235, 930, 860, 995), fill=(57, 196, 218, 210))
    draw.text((290, 815), "PUBLIC MEDICINE", font=font("arialbd.ttf", 38), fill=(37, 72, 78, 230))
    draw.text((305, 1035), "SEAL 8813", font=font("arialbd.ttf", 46), fill=(210, 73, 56, 235))
    for x in range(285, 820, 85):
        draw.line((x, 1125, x + 45, 1125), fill=(44, 88, 96, 130), width=5)

    # Clouded insulin vial under magnifier.
    draw.ellipse((990, 690, 1395, 1095), fill=(220, 239, 234, 58), outline=(220, 240, 231, 210), width=7)
    draw.line((1305, 1015, 1485, 1195), fill=(35, 54, 55, 230), width=24)
    draw.rounded_rectangle((1110, 785, 1275, 1010), radius=32, fill=(221, 238, 244, 220), outline=(40, 77, 89, 190), width=4)
    draw.rectangle((1138, 740, 1248, 800), fill=(75, 117, 130, 230))
    for _ in range(46):
        x = random.randint(1135, 1258)
        y = random.randint(830, 985)
        s = random.randint(2, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(240, 255, 255, random.randint(75, 160)))
    draw.text((1028, 1032), "CLOUDED INSULIN", font=font("arialbd.ttf", 27), fill=(31, 69, 76, 225))

    # Temperature graph and tide window.
    draw.rounded_rectangle((210, 1360, 835, 1575), radius=20, fill=(6, 24, 31, 205), outline=(101, 221, 232, 135), width=3)
    draw.text((250, 1392), "COPIED TEMPERATURE CURVE", font=font("arialbd.ttf", 26), fill=(193, 238, 233, 225))
    last = None
    for x in range(250, 800, 18):
        y = 1510 + int(math.sin(x * 0.035) * 24)
        if last:
            draw.line((last[0], last[1], x, y), fill=(88, 231, 220, 220), width=4)
        last = (x, y)
    draw.rounded_rectangle((940, 1345, 1388, 1588), radius=18, fill=(230, 222, 188, 228), outline=(91, 74, 51, 170), width=3)
    draw.text((980, 1380), "TIDE WINDOW", font=font("arialbd.ttf", 31), fill=(63, 50, 37, 230))
    draw.text((1008, 1445), "00:34 - 01:12", font=font("arialbd.ttf", 42), fill=(30, 90, 103, 235))
    draw.text((988, 1510), "MERIDIAN SKIFF", font=font("arial.ttf", 28), fill=(68, 58, 44, 220))

    # Ferry and skiff silhouettes.
    draw.polygon([(980, 1170), (1290, 1170), (1355, 1235), (920, 1235)], fill=(31, 47, 50, 245))
    draw.rectangle((1040, 1080, 1220, 1170), fill=(38, 62, 66, 245))
    draw.line((180, 1660, 1460, 1660), fill=(118, 199, 207, 185), width=7)
    for x in range(220, 1410, 155):
        draw.arc((x, 1630, x + 110, 1695), 0, 180, fill=(135, 214, 218, 120), width=3)
    draw.text((515, 1692), "COLD CHAIN MUST FOLLOW THE TIDE", font=font("arialbd.ttf", 30), fill=(202, 233, 226, 220))

    # Salt crystals and ledger tags.
    for _ in range(150):
        x = random.randint(130, 1490)
        y = random.randint(700, 1650)
        s = random.randint(1, 5)
        draw.rectangle((x, y, x + s, y + s), fill=(224, 246, 244, random.randint(40, 130)))
    draw.rounded_rectangle((965, 520, 1425, 630), radius=14, fill=(239, 231, 196, 225), outline=(80, 62, 42, 150), width=3)
    draw.text((995, 555), "HARBOR BOOK != MANIFEST", font=font("arialbd.ttf", 23), fill=(68, 53, 38, 225))

    tagline = "COLD CHAIN  TIDE LOGS  PUBLIC MEDICINE"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tidal Pharmacy")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (18, 52, 72, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_tidal_pharmacy(draw)
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
