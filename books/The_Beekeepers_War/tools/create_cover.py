#!/usr/bin/env python3
"""Cover: The Beekeeper's War — Apiary at dawn, bees swarming in defensive formation, two figures facing off."""

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
    title = meta.get("title", "The Beekeeper's War")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("beekeepers-war")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.35:
            c = (int(200 - 60 * t / 0.35), int(120 - 40 * t / 0.35), int(60 - 30 * t / 0.35))
        else:
            c = (int(140 - 100 * (t - 0.35) / 0.65), int(80 - 60 * (t - 0.35) / 0.65), int(30 - 20 * (t - 0.35) / 0.65))
        draw.line((0, y, W, y), fill=(*c, 255))

    for bx in range(300, 1300, 200):
        draw.rectangle((bx, 1000, bx + 80, 1400), fill=(120, 90, 50, 200))
        for sl in range(5):
            draw.rectangle((bx + 5, 1020 + sl * 75, bx + 75, 1020 + sl * 75 + 70), fill=(160, 130, 80, 180), outline=(100, 70, 40, 200), width=1)

    rng = random.Random(42)
    for _ in range(150):
        bx = rng.randint(200, 1400)
        by = rng.randint(500, 1500)
        size = rng.randint(3, 6)
        draw.ellipse((bx - size, by - size, bx + size, by + size), fill=(220, 180, 40, rng.randint(100, 200)))

    draw.rectangle((200, 1550, 600, 1700), fill=(40, 35, 30, 200))
    draw.rectangle((1000, 1550, 1400, 1700), fill=(40, 35, 30, 200))

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
