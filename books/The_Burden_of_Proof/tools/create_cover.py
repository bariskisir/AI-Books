#!/usr/bin/env python3
"""Cover: The Burden of Proof — Law library stacks at midnight, lone researcher, scattered evidence photos."""

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
    title = meta.get("title", "The Burden of Proof")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("burden-of-proof")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(15 + 10 * t); g = int(12 + 8 * t); b = int(20 + 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for sx in range(100, 1500, 180):
        draw.rectangle((sx, 300, sx + 60, 1700), fill=(40, 35, 50, 180))
        for sl in range(300, 1700, 30):
            draw.line((sx + 8, sl, sx + 52, sl), fill=(55, 50, 65, 80), width=1)

    draw.rectangle((W // 2 - 200, 900, W // 2 + 200, 1400), fill=(50, 45, 60, 200))
    draw.rectangle((W // 2 - 190, 910, W // 2 + 190, 1390), fill=(65, 60, 75, 180))

    rng = random.Random(42)
    for _ in range(12):
        px = W // 2 + rng.randint(-160, 160)
        py = 950 + rng.randint(0, 400)
        draw.rectangle((px - 25, py - 30, px + 25, py + 30), fill=(100, 90, 110, 150), outline=(140, 130, 150, 180), width=1)

    fx, fy = W // 2 - 100, 1300
    draw.ellipse((fx - 8, fy - 40, fx + 8, fy + 5), fill=(25, 22, 30, 200))
    draw.polygon([(fx - 12, fy - 5), (fx + 12, fy - 5), (fx + 14, fy + 40), (fx - 14, fy + 40)], fill=(25, 22, 30, 180))

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
