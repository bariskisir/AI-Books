#!/usr/bin/env python3
"""Cover: The Brine Communion — Salt flats at twilight, crystalline formations, mysterious figures in white robes."""

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
    title = meta.get("title", "The Brine Communion")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("brine-communion")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.3:
            c = (int(80 + 100 * t / 0.3), int(60 + 80 * t / 0.3), int(100 + 120 * t / 0.3))
        elif t < 0.6:
            c = (int(180 - 60 * (t - 0.3) / 0.3), int(140 - 40 * (t - 0.3) / 0.3), int(220 - 80 * (t - 0.3) / 0.3))
        else:
            c = (int(120 - 80 * (t - 0.6) / 0.4), int(100 - 60 * (t - 0.6) / 0.4), int(140 - 90 * (t - 0.6) / 0.4))
        draw.line((0, y, W, y), fill=(*c, 255))

    for y in range(800, H, 2):
        t = (y - 800) / (H - 800)
        shade = int(180 + 40 * t)
        draw.line((0, y, W, y), fill=(shade, shade + 5, shade + 10, 200))

    rng = random.Random(17)
    for _ in range(25):
        cx = rng.randint(100, 1500)
        cy = rng.randint(600, 1400)
        r = rng.randint(20, 50)
        draw.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=(200, 220, 230, rng.randint(40, 100)), outline=(220, 240, 250, 120), width=1)

    for fx in [W // 2 - 150, W // 2, W // 2 + 150]:
        fy = 1400
        draw.ellipse((fx - 15, fy - 50, fx + 15, fy + 10), fill=(200, 220, 230, 100))
        draw.polygon([(fx - 20, fy), (fx + 20, fy), (fx + 15, fy + 80), (fx - 15, fy + 80)], fill=(180, 200, 210, 80))

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
