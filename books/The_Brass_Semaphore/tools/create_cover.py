#!/usr/bin/env python3
"""Create a book-specific cover for The Brass Semaphore."""

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


def draw_brass_semaphore(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-brass-semaphore-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(30*(1-t)+42*t), int(44*(1-t)+54*t), int(57*(1-t)+61*t), 255))

    # Fog harbor and tower.
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog, "RGBA")
    for y0 in range(420, 1210, 120):
        fd.ellipse((-220, y0, W + 260, y0 + 250), fill=(210, 224, 218, 26))
    fog = fog.filter(ImageFilter.GaussianBlur(24))
    draw.bitmap((0, 0), fog)
    draw.rectangle((0, 1280, W, 1765), fill=(42, 65, 72, 245))
    for y0 in range(1360, 1710, 84):
        draw.arc((-120, y0, 520, y0 + 130), 0, 180, fill=(135, 175, 180, 80), width=4)
        draw.arc((680, y0 + 25, 1660, y0 + 165), 0, 180, fill=(135, 175, 180, 72), width=4)

    # Semaphore tower.
    draw.rectangle((690, 640, 910, 1395), fill=(45, 50, 49, 245), outline=(166, 178, 164, 145), width=5)
    draw.polygon([(655, 640), (800, 520), (945, 640)], fill=(65, 70, 66, 245), outline=(171, 182, 164, 140))
    draw.rectangle((620, 1365, 980, 1450), fill=(64, 55, 47, 245))
    pivot = (800, 610)
    brass = (214, 159, 78, 245)
    draw.ellipse((pivot[0]-34, pivot[1]-34, pivot[0]+34, pivot[1]+34), fill=brass, outline=(94, 65, 32, 220), width=4)
    draw.line((800, 610, 565, 470), fill=brass, width=24)
    draw.line((800, 610, 1035, 455), fill=brass, width=24)
    draw.polygon([(555, 448), (610, 482), (585, 535), (530, 500)], fill=(181, 39, 37, 230))
    draw.polygon([(1028, 430), (1088, 462), (1060, 520), (1000, 488)], fill=(224, 219, 175, 230))
    draw.text((714, 1480), "7-4-2", font=font("arialbd.ttf", 55), fill=(228, 193, 125, 235))

    # Gear and counterweight evidence.
    draw.rounded_rectangle((150, 885, 560, 1165), radius=22, fill=(24, 31, 31, 220), outline=(214, 159, 78, 160), width=4)
    draw.text((198, 920), "ALTERED GEAR", font=font("arialbd.ttf", 31), fill=(232, 206, 157, 230))
    for r in (80, 115):
        draw.ellipse((355-r, 1028-r, 355+r, 1028+r), outline=(214, 159, 78, 210), width=8)
    for ang in range(0, 360, 30):
        x1 = 355 + math.cos(math.radians(ang)) * 80
        y1 = 1028 + math.sin(math.radians(ang)) * 80
        x2 = 355 + math.cos(math.radians(ang)) * 128
        y2 = 1028 + math.sin(math.radians(ang)) * 128
        draw.line((x1, y1, x2, y2), fill=(214, 159, 78, 190), width=5)
    draw.rounded_rectangle((1045, 870, 1415, 1035), radius=18, fill=(231, 222, 190, 230), outline=(85, 65, 43, 170), width=3)
    draw.text((1085, 905), "PYC COUNTERWEIGHT", font=font("arialbd.ttf", 27), fill=(67, 50, 35, 230))
    draw.text((1138, 960), "PRIVATE YARD", font=font("arialbd.ttf", 34), fill=(153, 72, 52, 230))

    # Signal book and cargo ledger.
    draw.rounded_rectangle((130, 1225, 610, 1535), radius=18, fill=(232, 224, 190, 232), outline=(86, 66, 45, 160), width=3)
    draw.text((174, 1260), "MISSING SIGNAL PAGES", font=font("arialbd.ttf", 29), fill=(70, 52, 37, 230))
    for i, txt in enumerate(["7-4-2 EAST LANE", "FOG GAP", "PRIVATE TRANSFER"]):
        draw.text((180, 1328 + i * 50), txt, font=font("arial.ttf", 29), fill=(83, 61, 43, 220))
    draw.rounded_rectangle((970, 1220, 1465, 1525), radius=18, fill=(10, 23, 31, 220), outline=(122, 174, 190, 150), width=3)
    draw.text((1012, 1260), "CARGO LEDGER", font=font("arialbd.ttf", 31), fill=(203, 230, 224, 230))
    for i, cargo in enumerate(["MARIBEL TEA", "EASTWAKE COPPER", "ORISON GLASS"]):
        draw.text((1018, 1328 + i * 48), cargo, font=font("arial.ttf", 28), fill=(210, 223, 218, 220))

    # Harbor boats and signal scratches.
    draw.polygon([(250, 1580), (540, 1580), (595, 1640), (205, 1640)], fill=(28, 42, 45, 245))
    draw.rectangle((335, 1505, 470, 1580), fill=(37, 56, 60, 245))
    draw.line((255, 1678, 1370, 1678), fill=(139, 188, 190, 160), width=7)
    for x in range(300, 1320, 140):
        draw.arc((x, 1648, x + 96, 1715), 0, 180, fill=(151, 202, 202, 105), width=3)
    for _ in range(130):
        x = random.randint(90, 1510)
        y = random.randint(380, 1650)
        s = random.randint(1, 4)
        draw.ellipse((x, y, x + s, y + s), fill=(218, 232, 228, random.randint(35, 120)))

    tagline = "NAVAL SIGNALS  FOG LOGS  HARBOR CLAIMS"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Brass Semaphore")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (30, 44, 57, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_brass_semaphore(draw)
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
