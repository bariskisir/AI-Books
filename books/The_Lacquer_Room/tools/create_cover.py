#!/usr/bin/env python3
"""Create a book-specific cover for The Lacquer Room."""

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


def draw_lacquer_room(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-lacquer-room-cover")
    for y in range(H):
        t = y / H
        r = int(34 * (1 - t) + 13 * t)
        g = int(29 * (1 - t) + 14 * t)
        b = int(31 * (1 - t) + 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Conservation-room light.
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light, "RGBA")
    ld.polygon([(1010, 0), (1335, 0), (860, 1765), (505, 1765)], fill=(234, 222, 174, 70))
    ld.polygon([(210, 0), (430, 0), (640, 1765), (360, 1765)], fill=(155, 188, 195, 28))
    draw.bitmap((0, 0), light.filter(ImageFilter.GaussianBlur(25)), fill=None)

    # Lacquer screen panels.
    screen = (210, 430, 1390, 1340)
    panel_w = (screen[2] - screen[0]) // 6
    for i in range(6):
        x0 = screen[0] + i * panel_w
        x1 = x0 + panel_w - 8
        shade = 12 + i * 3
        draw.rounded_rectangle((x0, screen[1], x1, screen[3]), radius=8, fill=(shade, shade, shade + 5, 250), outline=(105, 83, 49, 220), width=5)
        draw.line((x1, screen[1] + 12, x1, screen[3] - 12), fill=(198, 160, 74, 90), width=3)

    # Gold landscape and cranes.
    for y in (1000, 1085, 1170):
        pts = []
        for x in range(250, 1350, 75):
            pts.append((x, y + random.randint(-28, 24)))
        draw.line(pts, fill=(206, 164, 70, 190), width=7)
    for x, y, s in [(460, 735, 1.0), (785, 675, 1.2), (1120, 790, .95)]:
        gold = (226, 185, 82, 230)
        draw.ellipse((x - 16*s, y - 14*s, x + 16*s, y + 14*s), fill=gold)
        draw.line((x, y, x - 82*s, y + 60*s), fill=gold, width=int(6*s))
        draw.line((x, y, x + 96*s, y + 45*s), fill=gold, width=int(6*s))
        draw.line((x - 7*s, y + 12*s, x - 22*s, y + 82*s), fill=gold, width=int(4*s))
        draw.line((x + 8*s, y + 12*s, x + 22*s, y + 82*s), fill=gold, width=int(4*s))

    # Raking-light rectangle exposing hidden temple mark.
    mark_box = (665, 1122, 970, 1240)
    draw.rounded_rectangle(mark_box, radius=10, fill=(36, 30, 26, 245), outline=(235, 212, 134, 220), width=4)
    draw.line((520, 1040, 1040, 1230), fill=(242, 226, 154, 155), width=9)
    mark_font = font("arialbd.ttf", 42)
    draw.text((700, 1154), "KOSEN-IN", font=mark_font, fill=(226, 210, 150, 220))
    draw.text((704, 1202), "INV. 4", font=font("arial.ttf", 29), fill=(205, 188, 130, 190))

    # Microscope, swabs, sample map.
    draw.rounded_rectangle((160, 1320, 580, 1600), radius=20, fill=(222, 218, 198, 230), outline=(104, 91, 67, 180), width=4)
    draw.text((195, 1350), "LAYER MAP", font=font("arialbd.ttf", 32), fill=(57, 48, 39, 230))
    colors = [(18,18,22), (198,151,65), (115,55,42), (232,225,200), (68,83,89)]
    for i, col in enumerate(colors):
        draw.rectangle((205, 1410 + i*27, 530, 1430 + i*27), fill=col+(230,) if len(col)==3 else col)
    draw.line((1140, 1320, 1280, 1510), fill=(205, 210, 202, 230), width=20)
    draw.ellipse((1230, 1475, 1385, 1595), outline=(205, 210, 202, 230), width=18)
    draw.rectangle((1258, 1270, 1312, 1360), fill=(205, 210, 202, 230))
    for x in (710, 770, 830):
        draw.line((x, 1415, x + 240, 1560), fill=(237, 230, 208, 200), width=7)
        draw.ellipse((x + 228, 1548, x + 258, 1578), fill=(245, 236, 215, 220))

    # Dust motes.
    for _ in range(140):
        x = random.randint(130, 1470)
        y = random.randint(260, 1615)
        s = random.randint(2, 5)
        draw.ellipse((x, y, x+s, y+s), fill=(232, 206, 145, random.randint(35, 105)))

    tagline = "ART CONSERVATION  PROVENANCE  REPATRIATION"
    tag_font = font("georgia.ttf", 37)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(226, 208, 158, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Lacquer Room")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (18, 18, 21, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_lacquer_room(draw)
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
