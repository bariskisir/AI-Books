#!/usr/bin/env python3
"""Cover: The Book of Dirt — Ancient leather-bound book with soil samples pressed between pages on archaeologist's table."""

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
    title = meta.get("title", "The Book of Dirt")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("book-of-dirt")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(40 + 30 * t); g = int(30 + 20 * t); b = int(15 + 10 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    bx, by = W // 2, 1200
    draw.rectangle((bx - 150, by - 100, bx + 150, by + 120), fill=(60, 40, 30, 255), outline=(40, 25, 18, 255), width=3)
    draw.line((bx - 140, by, bx + 140, by), fill=(40, 25, 18, 200), width=1)

    for i, shade in enumerate([(80, 50, 30), (100, 70, 40), (60, 40, 20), (120, 80, 50)]):
        sx = bx - 120 + i * 65
        sy = by - 80
        draw.rectangle((sx, sy, sx + 50, sy + 60), fill=(*shade, 200), outline=(40, 30, 20, 180), width=1)

    rng = random.Random(42)
    for _ in range(30):
        dx = rng.randint(-120, 120)
        dy = rng.randint(-60, 80)
        sz = rng.randint(2, 5)
        draw.ellipse((bx + dx - sz, by + dy - sz, bx + dx + sz, by + dy + sz), fill=(rng.randint(60, 120), rng.randint(40, 80), rng.randint(20, 40), 200))

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
