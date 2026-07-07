#!/usr/bin/env python3
"""Cover: The Botanist's Daughter — Victorian greenhouse, rare orchid blooming, woman's silhouette among exotic plants."""

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
    title = meta.get("title", "The Botanist's Daughter")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("botanists-daughter")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.4:
            c = (int(100 + 80 * (1 - t / 0.4)), int(150 + 60 * (1 - t / 0.4)), int(80 + 40 * (1 - t / 0.4)))
        else:
            c = (int(40 + 20 * t), int(70 + 30 * t), int(30 + 15 * t))
        draw.line((0, y, W, y), fill=(*c, 255))

    for x in range(0, W, 40):
        draw.line((x, 200, x + 20, 1800), fill=(120, 160, 100, 30), width=2)
        draw.line((x + 20, 200, x + 40, 1800), fill=(80, 120, 60, 20), width=2)

    ox, oy = W // 2 + 100, 1100
    draw.line((ox, oy + 40, ox, oy - 20), fill=(60, 100, 50, 200), width=4)
    draw.ellipse((ox - 25, oy - 30, ox + 25, oy + 5), fill=(160, 80, 120, 200))
    for petal in range(5):
        px = ox + int(30 * math.cos(petal * 2 * math.pi / 5))
        py = oy - 30 + int(30 * math.sin(petal * 2 * math.pi / 5))
        draw.ellipse((px - 15, py - 15, px + 15, py + 15), fill=(200, 100, 140, 180))
    draw.ellipse((ox - 8, oy - 35, ox + 8, oy - 20), fill=(220, 180, 60, 200))

    sx, sy = W // 2 - 120, 1000
    draw.ellipse((sx - 8, sy - 100, sx + 8, sy + 20), fill=(20, 25, 30, 180))
    draw.polygon([(sx - 15, sy - 80), (sx + 15, sy - 80), (sx + 18, sy), (sx - 18, sy)], fill=(20, 25, 30, 160))
    draw.line((sx, sy, sx, sy + 60), fill=(20, 25, 30, 180), width=5)
    draw.line((sx - 12, sy - 30, sx - 25, sy - 10), fill=(20, 25, 30, 160), width=4)
    draw.line((sx + 12, sy - 30, sx + 25, sy - 10), fill=(20, 25, 30, 160), width=4)

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
