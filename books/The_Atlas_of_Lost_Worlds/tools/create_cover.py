#!/usr/bin/env python3
"""Cover: The Atlas of Lost Worlds — Antique atlas open on wooden desk, glowing map coordinates, vintage brass compass."""

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
    title = meta.get("title", "The Atlas of Lost Worlds")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("atlas-lost-worlds")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(30 + 20 * (1 - t)); g = int(20 + 10 * (1 - t)); b = int(10 + 5 * (1 - t))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    draw.rectangle((100, 1100, 1500, 1600), fill=(80, 55, 35, 255))
    for x in range(100, 1500, 4):
        shade = 70 + int(20 * math.sin(x * 0.1))
        draw.line((x, 1100, x, 1600), fill=(shade, shade - 10, shade - 20, 255))

    draw.rectangle((200, 1180, 730, 1520), fill=(180, 170, 140, 200))
    draw.rectangle((870, 1180, 1400, 1520), fill=(180, 170, 140, 200))
    draw.line((740, 1200, 740, 1520), fill=(60, 40, 30, 200), width=3)

    for px, py in [(300, 1300), (500, 1400), (950, 1250), (1200, 1350)]:
        draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(220, 200, 100, 200))
        draw.line((px, py, px + random.randint(-20, 20), py - random.randint(20, 40)), fill=(220, 200, 100, 150), width=1)

    cx, cy = 1400, 1050
    draw.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=(160, 140, 80, 200), outline=(200, 180, 100, 255), width=4)
    draw.line((cx, cy - 30, cx, cy + 30), fill=(200, 180, 100, 200), width=2)
    draw.line((cx - 30, cy, cx + 30, cy), fill=(200, 180, 100, 200), width=2)
    draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(200, 180, 100, 255))

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
