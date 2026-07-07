#!/usr/bin/env python3
"""Cover: The Ballroom of Shadows — Dark ballroom with lone dancer, moonlight through tall windows, shadowy figures."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font, _standard_cover_repair_text, _standard_cover_wrap,
    _standard_cover_center, _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title, _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

def make_cover(mp, op):
    meta = json.loads(mp.read_text(encoding="utf-8"))
    title = meta.get("title", "The Ballroom of Shadows")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("ballroom-shadows")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(10 + 5 * (1 - t)); g = int(10 + 8 * (1 - t)); b = int(18 + 15 * (1 - t))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for wx in [100, 500, 900, 1300]:
        draw.rectangle((wx, 200, wx + 60, 1700), fill=(40, 50, 80, 100))
        draw.rectangle((wx + 5, 210, wx + 55, 1690), fill=(60, 80, 140, 80))
        for bar in range(200, 1700, 60):
            draw.line((wx + 15, bar, wx + 45, bar), fill=(20, 25, 40, 80), width=2)

    moon_x, moon_y = 200, 300
    for r in range(80, 10, -10):
        draw.ellipse((moon_x - r, moon_y - r, moon_x + r, moon_y + r), fill=(150, 170, 200, max(0, 30 - r // 3)))
    draw.ellipse((moon_x - 30, moon_y - 30, moon_x + 30, moon_y + 30), fill=(200, 210, 230, 200))

    dx, dy = W // 2, 1300
    draw.ellipse((dx - 12, dy - 12, dx + 12, dy + 12), fill=(40, 35, 40, 200))
    draw.polygon([(dx - 18, dy - 12), (dx + 18, dy - 12), (dx + 25, dy + 40), (dx - 25, dy + 40)], fill=(40, 35, 40, 180))
    draw.line((dx, dy - 12, dx, dy - 40), fill=(40, 35, 40, 200), width=5)

    for fx in [400, 800, 1200]:
        draw.polygon([(fx - 15, 1500), (fx + 15, 1500), (fx + 10, 1450), (fx - 10, 1450)], fill=(15, 12, 18, 120))

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    op.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(op), "PNG", optimize=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)

if __name__ == "__main__":
    main()
