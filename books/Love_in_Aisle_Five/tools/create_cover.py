#!/usr/bin/env python3
"""Cover: Love in Aisle Five — Romantic grocery store aisle at dusk, soft warm lighting, two people reaching for same item."""

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
    title = meta.get("title", "Love in Aisle Five")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("love-aisle-five")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(120 + 80 * (1 - t)); g = int(60 + 40 * (1 - t)); b = int(40 + 30 * (1 - t))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for sx in [100, 400, 700, 1000, 1300]:
        draw.rectangle((sx, 200, sx + 10, 1800), fill=(60, 45, 35, 180))
        for sh in range(6):
            draw.rectangle((sx + 15, 300 + sh * 240, sx + 180, 300 + sh * 240 + 200), fill=(140, 110, 80, 60), outline=(80, 60, 45, 100), width=1)

    for ly in range(200, 1800, 240):
        draw.line((0, ly, W, ly), fill=(180, 160, 120, 30))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((500, 800, 1100, 1800), fill=(255, 200, 120, 30))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    for arm in [-50, 50]:
        x1, y1 = W // 2 + arm, 1400
        x2, y2 = W // 2, 1200
        draw.line((x1, y1, x2, y2), fill=(25, 20, 18, 200), width=8)
        draw.ellipse((x2 - 8, y2 - 6, x2 + 8, y2 + 6), fill=(30, 25, 22, 200))

    draw.rectangle((W // 2 - 12, 1160, W // 2 + 12, 1180), fill=(200, 120, 40, 220))

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
