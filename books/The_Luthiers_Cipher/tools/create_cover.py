#!/usr/bin/env python3
"""Cover: The Luthiers Cipher — Dark background, amber-lake varnished violin, magnifying glass and secret notation, amber/wood brown/magnifying blue."""

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


def draw_violin_cipher(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-luthiers-cipher-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(40*(1-t)+22*t), int(28*(1-t)+36*t), int(26*(1-t)+44*t), 255))

    # Workshop wall and bench.
    draw.rectangle((0, 1050, W, 1765), fill=(56, 44, 38, 245))
    for y in range(1080, 1740, 76):
        draw.line((0, y, W, y + random.randint(-8, 8)), fill=(101, 76, 58, 85), width=3)
    draw.rectangle((0, 1515, W, 1765), fill=(92, 64, 42, 248))
    draw.line((0, 1515, W, 1515), fill=(169, 125, 78, 150), width=5)

    # Hanging archive papers and court order.
    for x, y, rot, label in [(145, 335, -8, "EVACUATION"), (1120, 315, 6, "INJUNCTION"), (1010, 875, -5, "BELLER")]:
        paper = Image.new("RGBA", (330, 430), (0, 0, 0, 0))
        pd = ImageDraw.Draw(paper, "RGBA")
        pd.rounded_rectangle((0, 0, 330, 430), radius=14, fill=(231, 219, 183, 235), outline=(91, 69, 47, 170), width=3)
        pd.text((34, 35), label, font=font("arialbd.ttf", 32), fill=(75, 54, 39, 230))
        for i in range(7):
            pd.line((35, 105 + i*38, 290, 105 + i*38), fill=(101, 81, 61, 115), width=3)
        paper = paper.rotate(rot, expand=True, resample=Image.Resampling.BICUBIC)
        draw.bitmap((x, y), paper)

    # Violin body on bench.
    cx, cy = 760, 1110
    varnish = (139, 68, 34, 255)
    glow = (217, 132, 59, 190)
    draw.ellipse((cx - 255, cy - 455, cx + 35, cy - 45), fill=varnish, outline=(63, 34, 25, 230), width=7)
    draw.ellipse((cx - 20, cy - 455, cx + 270, cy - 45), fill=varnish, outline=(63, 34, 25, 230), width=7)
    draw.ellipse((cx - 310, cy - 95, cx - 15, cy + 425), fill=varnish, outline=(63, 34, 25, 230), width=7)
    draw.ellipse((cx + 5, cy - 95, cx + 300, cy + 425), fill=varnish, outline=(63, 34, 25, 230), width=7)
    draw.rectangle((cx - 120, cy - 430, cx + 120, cy + 390), fill=varnish)
    for off in (-95, 95):
        draw.arc((cx + off - 45, cy - 220, cx + off + 55, cy + 40), 82, 278, fill=(48, 26, 20, 235), width=13)
    draw.rounded_rectangle((cx - 42, cy - 560, cx + 42, cy - 255), radius=28, fill=(68, 37, 27, 255))
    draw.rectangle((cx - 98, cy - 575, cx + 98, cy - 515), fill=(55, 31, 23, 255))
    draw.rounded_rectangle((cx - 80, cy + 250, cx + 80, cy + 335), radius=20, fill=(48, 28, 24, 255))
    for x in (cx - 54, cx - 18, cx + 18, cx + 54):
        draw.line((x, cy - 565, x, cy + 320), fill=(226, 211, 174, 210), width=4)
    draw.polygon([(cx - 105, cy + 25), (cx + 105, cy + 25), (cx + 76, cy + 95), (cx - 76, cy + 95)], fill=(228, 198, 132, 245), outline=(80, 48, 31, 210))
    for i in range(18):
        x = cx - 180 + i * 22
        draw.arc((x, cy - 300, x + 360, cy + 420), 255, 287, fill=(glow[0], glow[1], glow[2], 35), width=4)

    # Inner rib cipher magnifier.
    draw.ellipse((1035, 1030, 1390, 1385), fill=(221, 231, 218, 54), outline=(224, 232, 211, 210), width=7)
    draw.line((1305, 1325, 1465, 1495), fill=(62, 47, 38, 230), width=24)
    draw.rounded_rectangle((1085, 1160, 1340, 1268), radius=18, fill=(82, 48, 34, 235), outline=(211, 172, 111, 175), width=4)
    draw.text((1112, 1188), "17 4 9 / B", font=font("arialbd.ttf", 38), fill=(234, 207, 149, 235))

    # Dendrochronology ring chart and varnish sample.
    draw.rounded_rectangle((150, 1225, 545, 1435), radius=18, fill=(22, 28, 27, 210), outline=(218, 184, 124, 120), width=3)
    draw.text((185, 1250), "SPRUCE RING MATCH", font=font("arialbd.ttf", 27), fill=(224, 203, 158, 220))
    for i, x in enumerate(range(185, 510, 16)):
        h = 55 + int(math.sin(i * 1.7) * 32) + random.randint(-8, 8)
        draw.line((x, 1395, x, 1395 - h), fill=(202, 184, 142, 185), width=4)
    draw.rounded_rectangle((1025, 1460, 1370, 1588), radius=14, fill=(235, 224, 190, 230), outline=(85, 58, 38, 190), width=4)
    draw.text((1060, 1490), "VARNISH: AMBER / MADDER", font=font("arialbd.ttf", 24), fill=(77, 55, 39, 230))
    draw.ellipse((1295, 1525, 1332, 1562), fill=(185, 82, 35, 230))

    # Rosin and shavings.
    for _ in range(130):
        x = random.randint(95, 1500)
        y = random.randint(1180, 1660)
        s = random.randint(1, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(228, 193, 126, random.randint(45, 140)))
    for _ in range(36):
        x = random.randint(180, 1420)
        y = random.randint(1470, 1695)
        draw.arc((x, y, x + random.randint(60, 150), y + random.randint(15, 45)), 185, 350, fill=(187, 129, 69, 130), width=3)

    tagline = "VIOLIN PROVENANCE  VARNISH LAYERS  HIDDEN MARK"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Luthiers Cipher")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (40, 28, 26, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_violin_cipher(draw)
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
