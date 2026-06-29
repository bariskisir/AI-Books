#!/usr/bin/env python3
"""Create a book-specific cover for The Gravity Orchestra."""

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


def draw_orbit_scene(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-gravity-orchestra-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(3*(1-t)+14*t), int(13*(1-t)+26*t), int(31*(1-t)+45*t), 255))

    # Stars.
    for _ in range(220):
        x = random.randint(0, W)
        y = random.randint(40, 1510)
        s = random.randint(1, 4)
        a = random.randint(80, 210)
        draw.ellipse((x, y, x+s, y+s), fill=(220, 232, 236, a))

    # Earth limb.
    earth = Image.new("RGBA", (W, H), (0,0,0,0))
    ed = ImageDraw.Draw(earth, "RGBA")
    ed.ellipse((-340, 1110, 1940, 2770), fill=(23, 79, 104, 255), outline=(106, 191, 205, 210), width=12)
    ed.ellipse((-300, 1160, 1900, 2730), outline=(185, 229, 228, 70), width=28)
    for _ in range(30):
        x = random.randint(80, 1500)
        y = random.randint(1290, 1690)
        ed.arc((x-210, y-45, x+210, y+90), 190, 355, fill=(235, 245, 241, random.randint(45, 95)), width=random.randint(4, 10))
    draw.bitmap((0,0), earth.filter(ImageFilter.GaussianBlur(0.4)), fill=None)

    # Resonance arcs and falling debris.
    cx, cy = 800, 1180
    for r, col in [(480, (102, 184, 210, 130)), (610, (238, 191, 96, 130)), (740, (145, 216, 194, 110))]:
        draw.arc((cx-r, cy-r, cx+r, cy+r), 200, 345, fill=col, width=5)
    for _ in range(95):
        ang = random.uniform(math.radians(205), math.radians(345))
        r = random.choice([480, 610, 740]) + random.randint(-18, 18)
        x = cx + math.cos(ang)*r
        y = cy + math.sin(ang)*r
        draw.line((x, y, x+random.randint(18, 58), y+random.randint(4, 25)), fill=(230, 214, 160, random.randint(90, 190)), width=random.randint(2, 5))

    # Salvage tug.
    tx, ty = 690, 820
    draw.rounded_rectangle((tx-115, ty-45, tx+120, ty+55), radius=18, fill=(218, 224, 219, 240), outline=(93, 117, 126, 220), width=5)
    draw.rectangle((tx-55, ty-105, tx+55, ty-45), fill=(90, 130, 148, 230))
    draw.rectangle((tx-185, ty-25, tx-115, ty+25), fill=(70, 94, 112, 230))
    draw.rectangle((tx+120, ty-25, tx+205, ty+25), fill=(70, 94, 112, 230))
    draw.line((tx+125, ty+20, tx+290, ty+110), fill=(220, 222, 210, 220), width=8)
    draw.line((tx+290, ty+110, tx+365, ty+72), fill=(220, 222, 210, 220), width=8)
    draw.ellipse((tx+350, ty+55, tx+395, ty+100), outline=(220, 222, 210, 220), width=7)
    draw.polygon([(tx-170, ty-58), (tx-245, ty-160), (tx-110, ty-95)], fill=(54, 84, 108, 210))
    draw.text((tx-90, ty-12), "LITTLE", font=font("arialbd.ttf", 26), fill=(37, 51, 58, 220))

    # Satellites.
    for sx, sy, rot in [(360, 600, -12), (1170, 560, 18), (1110, 1005, -28)]:
        draw.rectangle((sx-42, sy-28, sx+42, sy+28), fill=(190, 194, 186, 230), outline=(88, 99, 108, 200), width=3)
        draw.rectangle((sx-150, sy-18, sx-50, sy+18), fill=(38, 90, 120, 220))
        draw.rectangle((sx+50, sy-18, sx+150, sy+18), fill=(38, 90, 120, 220))
        draw.line((sx-150, sy, sx+150, sy), fill=(162, 198, 204, 120), width=2)

    # Anchor platform silhouette.
    draw.rounded_rectangle((510, 1220, 1090, 1390), radius=28, fill=(48, 63, 78, 240), outline=(148, 169, 176, 190), width=5)
    draw.text((605, 1274), "ANCHOR NINE", font=font("arialbd.ttf", 40), fill=(211, 221, 213, 225))
    draw.rectangle((455, 1265, 510, 1345), fill=(91, 112, 122, 230))
    draw.rectangle((1090, 1265, 1148, 1345), fill=(91, 112, 122, 230))

    tagline = "ORBITAL DEBRIS  SALVAGE TUG  USABLE SKY"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(226, 232, 215, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Gravity Orchestra")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (4, 10, 25, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_orbit_scene(draw)
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
