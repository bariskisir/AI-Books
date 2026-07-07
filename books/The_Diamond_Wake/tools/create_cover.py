#!/usr/bin/env python3
"""Cover: The Diamond Wake — Luxury yacht at sunset, bloodstain on deck, diamond necklace catching last light."""

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
    title = meta.get("title", "The Diamond Wake")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("diamond-wake")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.4:
            c = (int(220 - 40 * t / 0.4), int(140 - 60 * t / 0.4), int(60 - 40 * t / 0.4))
        elif t < 0.6:
            c = (int(180 - 100 * (t - 0.4) / 0.2), int(80 - 50 * (t - 0.4) / 0.2), int(20 - 15 * (t - 0.4) / 0.2))
        else:
            c = (int(80 - 60 * (t - 0.6) / 0.4), int(30 - 20 * (t - 0.6) / 0.4), int(5 - 3 * (t - 0.6) / 0.4))
        draw.line((0, y, W, y), fill=(*c, 255))

    for y in range(1400, H, 2):
        t = (y - 1400) / (H - 1400)
        draw.line((0, y, W, y), fill=(20 + int(20 * (1 - t)), 30 + int(30 * (1 - t)), 60 + int(40 * (1 - t)), 180))

    draw.rectangle((W // 2 - 120, 1100, W // 2 + 120, 1400), fill=(40, 35, 50, 200))
    draw.rectangle((W // 2 - 80, 1080, W // 2 + 80, 1100), fill=(60, 50, 70, 200))

    draw.ellipse((W // 2 - 15, 1180, W // 2 + 15, 1220), fill=(120, 15, 15, 180))
    for dx in range(-20, 25, 5):
        for dy in range(-15, 20, 8):
            draw.ellipse((W // 2 + dx - 3, 1200 + dy - 3, W // 2 + dx + 3, 1200 + dy + 3), fill=(160, 20, 20, max(0, 100 - abs(dx) * 3 - abs(dy) * 3)))

    nx, ny = W // 2, 1130
    for i in range(12):
        angle = math.radians(i * 30)
        dx = int(25 * math.cos(angle))
        dy = int(5 * math.sin(angle))
        draw.ellipse((nx + dx - 3, ny + dy - 3, nx + dx + 3, ny + dy + 3), fill=(200, 220, 240, 200))

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
