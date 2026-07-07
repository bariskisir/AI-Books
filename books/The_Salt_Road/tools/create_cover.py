#!/usr/bin/env python3
"""Cover: The Salt Road — Ancient salt caravan trail through mountains, white salt flats stretching to horizon."""

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
    title = meta.get("title", "The Salt Road")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("salt-road")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.4:
            c = (int(150 + 80 * t / 0.4), int(160 + 60 * t / 0.4), int(200 + 40 * t / 0.4))
        else:
            c = (int(230 - 60 * (t - 0.4) / 0.6), int(220 - 80 * (t - 0.4) / 0.6), int(240 - 100 * (t - 0.4) / 0.6))
        draw.line((0, y, W, y), fill=(*c, 255))

    for y in range(900, H, 2):
        t = (y - 900) / (H - 900)
        shade = int(220 - 30 * t)
        draw.line((0, y, W, y), fill=(shade, shade + 5, shade + 10, 200))

    rng = random.Random(42)
    for _ in range(30):
        cx = rng.randint(100, 1500)
        cy = rng.randint(700, 1300)
        r = rng.randint(15, 40)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(rng.randint(180, 220), rng.randint(190, 225), rng.randint(200, 230), rng.randint(40, 80)))

    for mx in [W // 2 - 100, W // 2 + 100]:
        my = 1250
        draw.polygon([(mx, my - 60), (mx + 20, my), (mx - 20, my)], fill=(100, 80, 60, 180))
        draw.line((mx, my - 60, mx, my + 60), fill=(60, 50, 40, 200), width=4)
        draw.line((mx, my + 60, mx - 20, my + 80), fill=(60, 50, 40, 200), width=3)
        draw.line((mx, my + 60, mx + 20, my + 80), fill=(60, 50, 40, 200), width=3)

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
