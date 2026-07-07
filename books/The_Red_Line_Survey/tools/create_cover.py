#!/usr/bin/env python3
"""Cover: The Red Line Survey — red line through gravestones on misty ridge, old boundary stone and survey tripod in foreground."""

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
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()

def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Red Line Survey")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("the-red-line-survey-cover")
    img = Image.new("RGBA", (W, H), (18, 20, 22, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Misty ridge background
    for y in range(1800):
        t = y / 1800
        if t < 0.55:
            c = lerp((22, 30, 33), (68, 78, 68), t / 0.55)
        else:
            c = lerp((68, 78, 68), (26, 24, 22), (t - 0.55) / 0.45)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Mist
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(18):
        x0, y0, x1, y1 = random.randint(0, W), random.randint(200, 1500), random.randint(200, 600), random.randint(30, 80)
        md.ellipse((min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)), fill=(180, 190, 180, random.randint(12, 30)))
    mist = mist.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img, "RGBA")

    # Gravestones on ridge
    for i in range(8):
        gx = 180 + i * 180 + random.randint(-25, 25)
        gy = 880 + random.randint(-30, 30)
        draw.rounded_rectangle((gx, gy - 70, gx + 32, gy), radius=5, fill=(148, 145, 132, 230), outline=(78, 76, 66, 180), width=2)

    # Old boundary stone
    bsx, bsy = W // 2 - 45, 1280
    draw.polygon([(bsx, bsy), (bsx + 90, bsy), (bsx + 78, bsy - 110), (bsx + 12, bsy - 110)], fill=(158, 152, 138, 245), outline=(68, 62, 52, 180), width=3)
    for i, txt in enumerate(["S 36", "T 4N", "R 8E"]):
        draw.text((bsx + 20, bsy - 80 + i * 28), txt, font=font("arialbd.ttf", 22), fill=(58, 52, 42, 230))

    # The red line through gravestones
    pts = [(180, 1320), (420, 1100), (680, 1020), (950, 960), (1200, 860), (1420, 730)]
    for w, a in [(24, 72), (12, 235)]:
        for a2, b2 in zip(pts, pts[1:]):
            draw.line((*a2, *b2), fill=(188, 22, 34, a), width=w)
    for p in pts:
        draw.ellipse((p[0] - 10, p[1] - 10, p[0] + 10, p[1] + 10), fill=(196, 24, 34, 235))

    # Survey tripod in foreground
    tx, ty = 220, 950
    draw.line((tx, ty, tx - 45, ty + 220), fill=(38, 40, 36, 230), width=6)
    draw.line((tx, ty, tx + 45, ty + 220), fill=(38, 40, 36, 230), width=6)
    draw.line((tx, ty, tx, ty + 220), fill=(38, 40, 36, 230), width=6)
    draw.rectangle((tx - 28, ty - 28, tx + 28, ty + 28), fill=(58, 62, 58, 245), outline=(195, 185, 135, 170), width=3)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG", optimize=True)



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
