#!/usr/bin/env python3
"""Cover: The Carnival at Midnight — Abandoned carnival at night, Ferris wheel silhouetted against full moon, single lit tent."""

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
    title = meta.get("title", "The Carnival at Midnight")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("carnival-midnight")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(5 + 3 * t); g = int(5 + 3 * t); b = int(10 + 8 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    moon_x, moon_y = W // 2, 500
    for r in range(120, 10, -10):
        draw.ellipse((moon_x - r, moon_y - r, moon_x + r, moon_y + r), fill=(180, 190, 200, max(0, 25 - r // 5)))
    draw.ellipse((moon_x - 50, moon_y - 50, moon_x + 50, moon_y + 50), fill=(220, 225, 230, 230))
    draw.ellipse((moon_x - 42, moon_y - 42, moon_x + 42, moon_y + 42), fill=(200, 210, 215, 180))

    rng = random.Random(17)
    for _ in range(50):
        x = rng.randint(0, W)
        y = rng.randint(10, 300)
        s = rng.randint(1, 2)
        draw.ellipse((x - s, y - s, x + s, y + s), fill=(200, 200, 210, rng.randint(100, 200)))

    cx, cy = W // 2, 800
    draw.ellipse((cx - 160, cy - 160, cx + 160, cy + 160), fill=(15, 12, 18, 200), outline=(30, 25, 35, 255), width=3)
    for a in range(0, 360, 30):
        rad = math.radians(a)
        x1 = cx + int(150 * math.cos(rad))
        y1 = cy + int(150 * math.sin(rad))
        draw.line((cx, cy, x1, y1), fill=(30, 25, 35, 150), width=2)
        draw.ellipse((x1 - 5, y1 - 5, x1 + 5, y1 + 5), fill=(40, 35, 45, 180))

    tx, ty = W // 2 + 200, 1200
    draw.polygon([(tx, ty), (tx - 60, ty + 80), (tx + 60, ty + 80)], fill=(40, 35, 30, 200))
    draw.ellipse((tx - 15, ty + 20, tx + 15, ty + 60), fill=(200, 180, 100, 150))

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
