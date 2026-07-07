#!/usr/bin/env python3
"""Cover: Silver and Bone — Mysterious silver artifact on dark background, bone fragments scattered, ethereal glow."""

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
    title = meta.get("title", "Silver and Bone")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("silver-bone")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(8 + 4 * t); g = int(8 + 4 * t); b = int(12 + 6 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((600, 800, 1000, 1400), fill=(180, 200, 220, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    cx, cy = W // 2, 1100
    draw.ellipse((cx - 50, cy - 60, cx + 50, cy + 60), fill=(160, 180, 200, 200))
    draw.ellipse((cx - 35, cy - 45, cx + 35, cy + 45), fill=(180, 200, 220, 240))
    draw.polygon([(cx, cy - 30), (cx - 15, cy + 15), (cx + 15, cy + 15)], fill=(140, 160, 180, 200))
    draw.ellipse((cx - 8, cy - 18, cx + 8, cy - 4), fill=(200, 220, 240, 255))

    rng = random.Random(17)
    for _ in range(20):
        bx = cx + rng.randint(-200, 200)
        by = cy + rng.randint(30, 200)
        angle = rng.random() * math.pi * 2
        length = rng.randint(15, 35)
        draw.line((bx, by, bx + int(length * math.cos(angle)), by + int(length * math.sin(angle))), fill=(200, 190, 180, rng.randint(80, 160)), width=3)
        draw.ellipse((bx - 4, by - 4, bx + 4, by + 4), fill=(210, 200, 190, 180))

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
