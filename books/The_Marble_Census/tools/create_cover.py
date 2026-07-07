#!/usr/bin/env python3
"""Cover: The Marble Census — Marble statue hand pointing toward tenement windows at dusk, marble white/tenement brick/dusk blue."""

from __future__ import annotations

import argparse
import json
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


def draw_marble_square(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-marble-census-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(46*(1-t)+20*t), int(50*(1-t)+34*t), int(56*(1-t)+43*t), 255))

    # Rain-lit civic square.
    draw.rectangle((0, 1215, W, 1765), fill=(42, 45, 47, 245))
    for y in range(1240, 1740, 55):
        draw.line((0, y, W, y + random.randint(-10, 10)), fill=(118, 126, 126, 70), width=2)
    for _ in range(240):
        x = random.randint(-60, W + 60)
        y = random.randint(180, 1600)
        draw.line((x, y, x - 16, y + random.randint(35, 75)), fill=(190, 202, 205, random.randint(35, 85)), width=2)

    # Courthouse and tenement silhouettes.
    draw.rectangle((90, 665, 430, 1215), fill=(28, 31, 34, 235))
    draw.rectangle((1180, 585, 1510, 1215), fill=(30, 33, 36, 235))
    for x0 in (130, 220, 310, 1220, 1310, 1400):
        for y0 in (735, 865, 995):
            draw.rectangle((x0, y0, x0 + 45, y0 + 70), fill=(217, 193, 116, 75))
    draw.polygon([(540, 645), (800, 410), (1060, 645)], fill=(82, 82, 78, 235))
    draw.rectangle((585, 645, 1015, 1215), fill=(64, 66, 65, 240))
    for x in range(630, 980, 85):
        draw.rectangle((x, 755, x + 42, 1215), fill=(37, 39, 41, 240))

    # Meridian statue.
    sx, sy = 800, 870
    marble = (217, 217, 205, 245)
    shadow = (152, 154, 148, 230)
    draw.rectangle((650, 1195, 950, 1320), fill=(186, 184, 170, 245), outline=(95, 94, 86, 200), width=5)
    draw.text((690, 1238), "MC-001", font=font("arialbd.ttf", 39), fill=(73, 72, 67, 230))
    draw.ellipse((sx - 55, sy - 250, sx + 55, sy - 140), fill=marble, outline=shadow, width=4)
    draw.polygon([(sx - 95, sy - 140), (sx + 95, sy - 140), (sx + 145, sy + 260), (sx - 145, sy + 260)], fill=marble, outline=shadow)
    draw.line((sx + 20, sy - 90, sx + 235, sy - 165), fill=marble, width=34)
    draw.ellipse((sx + 220, sy - 182, sx + 260, sy - 142), fill=marble, outline=shadow, width=3)
    draw.line((sx - 25, sy - 80, sx - 135, sy + 55), fill=shadow, width=9)
    for yy in range(sy - 80, sy + 230, 44):
        draw.arc((sx - 120, yy, sx + 120, yy + 120), 190, 345, fill=(170, 171, 162, 130), width=4)

    # Census ledger and erased-address papers.
    draw.rounded_rectangle((195, 1350, 635, 1595), radius=16, fill=(230, 225, 203, 235), outline=(91, 80, 60, 190), width=4)
    draw.text((235, 1380), "MARBLE CENSUS", font=font("arialbd.ttf", 32), fill=(55, 50, 44, 230))
    for i, txt in enumerate(["MC-001  TURNED", "MARA VALE", "ROLL RESTORED"]):
        draw.text((235, 1440 + i * 42), txt, font=font("arial.ttf", 28), fill=(60, 55, 48, 220))
    draw.rounded_rectangle((1030, 1350, 1395, 1540), radius=14, fill=(234, 228, 206, 230), outline=(120, 45, 42, 180), width=4)
    draw.text((1072, 1392), "VACANT", font=font("arialbd.ttf", 47), fill=(145, 48, 45, 220))
    draw.line((1058, 1464, 1370, 1464), fill=(145, 48, 45, 210), width=7)
    draw.text((1072, 1488), "NAME ERASED", font=font("arial.ttf", 29), fill=(80, 66, 58, 210))

    # Dust and marble chips.
    for _ in range(180):
        x = random.randint(140, 1460)
        y = random.randint(710, 1615)
        s = random.randint(2, 7)
        draw.ellipse((x, y, x + s, y + s), fill=(222, 219, 202, random.randint(45, 150)))

    tagline = "CIVIC GOTHIC  LIVING STATUES  ERASED NAMES"
    tag_font = font("georgia.ttf", 35)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(225, 218, 190, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Marble Census")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (31, 35, 40, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_marble_square(draw)
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
