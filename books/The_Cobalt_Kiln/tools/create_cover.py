#!/usr/bin/env python3
"""Create a book-specific cover for The Cobalt Kiln."""

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


def draw_cobalt_kiln(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-cobalt-kiln-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(28*(1-t)+39*t), int(34*(1-t)+30*t), int(45*(1-t)+37*t), 255))

    # Museum lab and kiln chamber glow.
    draw.rectangle((0, 1065, W, 1765), fill=(52, 45, 39, 248))
    draw.rectangle((0, 1470, W, 1765), fill=(91, 65, 42, 250))
    draw.ellipse((980, 550, 1570, 1190), fill=(111, 54, 30, 80), outline=(195, 101, 47, 170), width=8)
    draw.rectangle((1090, 750, 1470, 1260), fill=(38, 34, 31, 240), outline=(195, 101, 47, 160), width=6)
    draw.arc((1125, 620, 1435, 910), 180, 360, fill=(211, 122, 58, 160), width=10)
    draw.text((1030, 1295), "PRIVATE COBALT KILN", font=font("arialbd.ttf", 28), fill=(231, 184, 116, 220))

    # Central cobalt bowl.
    cx, cy = 690, 1045
    draw.ellipse((cx - 315, cy - 130, cx + 315, cy + 130), fill=(19, 66, 142, 255), outline=(8, 30, 72, 230), width=8)
    draw.ellipse((cx - 260, cy - 88, cx + 260, cy + 88), fill=(37, 112, 198, 250), outline=(145, 193, 226, 95), width=5)
    draw.rectangle((cx - 210, cy, cx + 210, cy + 310), fill=(23, 81, 164, 255))
    draw.ellipse((cx - 210, cy + 210, cx + 210, cy + 410), fill=(15, 53, 122, 255), outline=(6, 28, 72, 220), width=7)
    for i in range(11):
        x = cx - 240 + i * 48
        draw.arc((x, cy - 35, x + 180, cy + 340), 235, 292, fill=(122, 184, 225, 70), width=5)
    draw.text((cx - 77, cy + 255), "T-44", font=font("arialbd.ttf", 50), fill=(230, 230, 195, 210))

    # Magnifier over foot mark and lacquer.
    draw.ellipse((220, 650, 575, 1005), fill=(225, 238, 231, 55), outline=(224, 236, 220, 210), width=7)
    draw.line((500, 940, 660, 1110), fill=(40, 39, 35, 230), width=24)
    draw.rounded_rectangle((300, 790, 500, 900), radius=16, fill=(26, 77, 145, 240), outline=(229, 208, 139, 180), width=4)
    draw.text((348, 818), "T-44", font=font("arialbd.ttf", 36), fill=(239, 229, 181, 235))
    draw.line((292, 880, 512, 812), fill=(80, 34, 28, 190), width=10)

    # Evidence cards.
    draw.rounded_rectangle((130, 1245, 555, 1428), radius=16, fill=(235, 226, 190, 230), outline=(85, 65, 43, 170), width=3)
    draw.text((170, 1280), "FALSE PERMIT", font=font("arialbd.ttf", 31), fill=(76, 56, 38, 230))
    draw.line((175, 1345, 510, 1345), fill=(102, 78, 55, 130), width=4)
    draw.text((172, 1372), "EXPORT BEFORE EXCAVATION", font=font("arialbd.ttf", 22), fill=(150, 57, 47, 225))
    draw.rounded_rectangle((930, 1280, 1435, 1458), radius=18, fill=(8, 24, 41, 218), outline=(73, 165, 220, 140), width=3)
    draw.text((975, 1315), "COBALT ISOTOPE TRACE", font=font("arialbd.ttf", 29), fill=(185, 221, 240, 230))
    for i, x in enumerate(range(985, 1390, 28)):
        h = 35 + int(math.sin(i * 1.2) * 25) + random.randint(-6, 6)
        draw.line((x, 1422, x, 1422 - h), fill=(76, 183, 236, 205), width=5)

    # Ash scar and shard comparison.
    draw.rounded_rectangle((640, 1375, 875, 1502), radius=18, fill=(28, 39, 43, 230), outline=(206, 143, 74, 145), width=3)
    draw.arc((675, 1408, 835, 1492), 12, 172, fill=(232, 156, 76, 230), width=8)
    draw.text((662, 1340), "ASH RING", font=font("arialbd.ttf", 27), fill=(231, 185, 127, 220))
    for _ in range(170):
        x = random.randint(140, 1480)
        y = random.randint(590, 1660)
        s = random.randint(1, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(183, 210, 236, random.randint(35, 125)))

    tagline = "CERAMIC PROVENANCE  KILN SCARS  HIDDEN MARKS"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Cobalt Kiln")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (28, 34, 45, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_cobalt_kiln(draw)
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
