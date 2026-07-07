#!/usr/bin/env python3
"""Cover: Dandelion Wine Summer — Small-town summer scene, dandelion fields, vintage jar of golden wine."""

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
    title = meta.get("title", "Dandelion Wine Summer")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("dandelion-wine")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        if t < 0.4:
            c = (int(100 + 130 * t / 0.4), int(160 + 80 * t / 0.4), int(200 - 50 * t / 0.4))
        elif t < 0.65:
            c = (int(230 - 60 * (t - 0.4) / 0.25), int(240 - 80 * (t - 0.4) / 0.25), int(150 - 50 * (t - 0.4) / 0.25))
        else:
            c = (int(170 - 100 * (t - 0.65) / 0.35), int(160 - 100 * (t - 0.65) / 0.35), int(100 - 60 * (t - 0.65) / 0.35))
        draw.line((0, y, W, y), fill=(*c, 255))

    rng = random.Random(42)
    for _ in range(300):
        x = rng.randint(0, W)
        y = rng.randint(800, 1800)
        s = rng.randint(4, 12)
        draw.ellipse((x - s, y - s, x + s, y + s), fill=(200, 220, 50, rng.randint(40, 100)))
        draw.line((x, y, x + rng.randint(-4, 4), y + 20), fill=(80, 120, 40, 100), width=2)

    jx, jy = W // 2, 1300
    draw.rectangle((jx - 40, jy - 80, jx + 40, jy + 20), fill=(180, 160, 100, 200), outline=(120, 100, 60, 220), width=3)
    draw.rectangle((jx - 28, jy - 95, jx + 28, jy - 80), fill=(140, 120, 70, 200))
    draw.ellipse((jx - 18, jy - 65, jx + 18, jy - 20), fill=(220, 200, 80, 150))

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
