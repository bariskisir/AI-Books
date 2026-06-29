#!/usr/bin/env python3
"""Create a book-specific cover for The Cloister Algorithm."""

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


def draw_cloister_archive(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-cloister-algorithm-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(26*(1-t)+16*t), int(40*(1-t)+47*t), int(48*(1-t)+48*t), 255))

    # Abbey cloister and scanner room.
    draw.rectangle((0, 950, W, 1765), fill=(52, 64, 60, 245))
    for x in range(90, 1520, 230):
        draw.rectangle((x, 700, x + 115, 1500), fill=(43, 53, 51, 245))
        draw.arc((x - 28, 585, x + 143, 810), 180, 360, fill=(151, 162, 141, 190), width=14)
    draw.rectangle((0, 1510, W, 1765), fill=(37, 55, 48, 250))
    draw.polygon([(0, 1510), (455, 1380), (820, 1485), (1190, 1365), (1600, 1495), (1600, 1765), (0, 1765)], fill=(55, 94, 70, 220))

    # Blue scanner light and manuscript cradle.
    draw.rounded_rectangle((275, 1120, 1325, 1415), radius=28, fill=(18, 26, 28, 230), outline=(121, 168, 161, 150), width=4)
    draw.rounded_rectangle((355, 1195, 1245, 1348), radius=18, fill=(6, 17, 22, 240), outline=(52, 205, 233, 180), width=4)
    draw.rectangle((380, 1262, 1220, 1280), fill=(61, 219, 246, 220))
    for x in range(410, 1190, 70):
        draw.line((x, 1208, x + random.randint(-20, 20), 1340), fill=(83, 228, 246, 42), width=3)
    draw.text((430, 1146), "SOURCE IMAGE / MODEL OUTPUT", font=font("arialbd.ttf", 31), fill=(198, 230, 221, 220))

    # Palimpsest charter leaf with green overtext and brown undertext.
    leaf = [(505, 760), (1085, 700), (1160, 1095), (565, 1165)]
    draw.polygon(leaf, fill=(220, 207, 168, 238), outline=(83, 66, 46, 190))
    for i in range(8):
        y0 = 805 + i * 42
        draw.line((585, y0, 1040, y0 - 42), fill=(44, 108, 73, 95), width=4)
    for i in range(7):
        y0 = 875 + i * 38
        draw.line((615, y0, 1080, y0 - 48), fill=(106, 63, 37, 130), width=3)
    draw.text((635, 1018), "COMMUNIS AQUA", font=font("arialbd.ttf", 36), fill=(92, 58, 37, 215))

    # Algorithm confidence panel and cropped marginal note.
    draw.rounded_rectangle((130, 510, 540, 820), radius=22, fill=(11, 25, 28, 210), outline=(70, 204, 191, 150), width=3)
    draw.text((170, 545), "CONFIDENCE", font=font("arialbd.ttf", 32), fill=(199, 233, 220, 230))
    draw.text((205, 605), "98.2%", font=font("arialbd.ttf", 70), fill=(88, 234, 211, 235))
    draw.text((170, 705), "WRONG WHERE\nSOURCE IS DAMAGED", font=font("arialbd.ttf", 24), fill=(241, 141, 111, 225))
    draw.rounded_rectangle((1080, 515, 1455, 805), radius=18, fill=(226, 215, 177, 230), outline=(82, 65, 43, 170), width=3)
    draw.text((1115, 550), "CROPPED MARGIN", font=font("arialbd.ttf", 29), fill=(74, 54, 38, 230))
    draw.rectangle((1120, 625, 1420, 690), outline=(231, 83, 67, 210), width=6)
    draw.text((1135, 715), "meadow / millstream", font=font("arial.ttf", 27), fill=(83, 60, 42, 220))

    # File/version artifacts.
    for x, y, label in [(170, 910, "brigid_final"), (1100, 900, "meadow_final"), (1045, 1455, "POSTPROCESSOR")]:
        draw.rounded_rectangle((x, y, x + 315, y + 120), radius=15, fill=(235, 226, 192, 218), outline=(90, 74, 50, 155), width=3)
        draw.text((x + 24, y + 35), label, font=font("arialbd.ttf", 27), fill=(76, 56, 38, 225))
    for _ in range(90):
        x = random.randint(120, 1480)
        y = random.randint(710, 1600)
        draw.ellipse((x, y, x + 3, y + 3), fill=(225, 220, 178, random.randint(45, 130)))

    # Common meadow boundary and water line.
    draw.line((185, 1590, 1390, 1590), fill=(80, 168, 198, 190), width=8)
    for x in range(230, 1340, 150):
        draw.arc((x, 1560, x + 100, 1625), 0, 180, fill=(97, 197, 215, 130), width=3)
    draw.text((545, 1630), "COMMON MEADOW / WATER CLAUSE", font=font("arialbd.ttf", 30), fill=(198, 225, 205, 220))

    tagline = "DIGITAL HUMANITIES  PALIMPSEST LEAF  COMMON LAND"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Cloister Algorithm")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (26, 40, 48, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_cloister_archive(draw)
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
