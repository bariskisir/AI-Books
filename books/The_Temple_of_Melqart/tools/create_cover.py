#!/usr/bin/env python3
"""Cover: The Temple of Melqart — Ancient Phoenician temple ruins at sunset, massive stone columns, Mediterranean sea."""

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
    title = meta.get("title", "The Temple of Melqart")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("temple-melqart")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.3:
            c = (int(220 - 30 * t / 0.3), int(140 - 40 * t / 0.3), int(60 - 30 * t / 0.3))
        elif t < 0.5:
            c = (int(190 - 70 * (t - 0.3) / 0.2), int(100 - 50 * (t - 0.3) / 0.2), int(30 - 20 * (t - 0.3) / 0.2))
        elif t < 0.7:
            c = (int(120 - 60 * (t - 0.5) / 0.2), int(50 - 25 * (t - 0.5) / 0.2), int(10 - 5 * (t - 0.5) / 0.2))
        else:
            c = (int(60 - 40 * (t - 0.7) / 0.3), int(25 - 15 * (t - 0.7) / 0.3), int(5 - 3 * (t - 0.7) / 0.3))
        draw.line((0, y, W, y), fill=(*c, 255))

    for y in range(900, H, 2):
        t = (y - 900) / (H - 900)
        shade = int(40 + 20 * (1 - t))
        draw.line((0, y, W, y), fill=(shade, shade + 10, shade + 30, 180))

    cols = [(300, 0.6), (500, 1.0), (800, 1.2), (1100, 1.0), (1300, 0.6)]
    for cx, sc in cols:
        w = int(60 * sc)
        h = int(500 * sc)
        draw.rectangle((cx - w // 2, 600, cx + w // 2, 600 + h), fill=(120, 80, 50, 180))
        draw.rectangle((cx - w // 2 + 5, 600 + 10, cx + w // 2 - 5, 600 + h - 10), fill=(140, 100, 60, 150))

    for cx, sc in cols:
        w = int(60 * sc)
        h = int(500 * sc)
        draw.rectangle((cx - w // 2 - 10, 590, cx + w // 2 + 10, 610), fill=(100, 65, 40, 200))
        draw.rectangle((cx - w // 2 - 5, 590 + h - 5, cx + w // 2 + 5, 590 + h + 5), fill=(100, 65, 40, 200))

    sun_x, sun_y = W // 2, 400
    for r in range(100, 10, -10):
        draw.ellipse((sun_x - r, sun_y - r, sun_x + r, sun_y + r), fill=(255, 200, 80, max(0, 60 - r // 2)))
    draw.ellipse((sun_x - 40, sun_y - 40, sun_x + 40, sun_y + 40), fill=(255, 220, 100, 200))

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
