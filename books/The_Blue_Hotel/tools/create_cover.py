#!/usr/bin/env python3
"""Cover: The Blue Hotel — Desert motel at midnight, neon blue vacancy sign, single car in parking lot."""

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
    title = meta.get("title", "The Blue Hotel")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("blue-hotel")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(5 + 3 * t); g = int(5 + 3 * t); b = int(15 + 10 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    rng = random.Random(17)
    for _ in range(40):
        x = rng.randint(0, W)
        y = rng.randint(5, 200)
        s = rng.randint(1, 2)
        draw.ellipse((x - s, y - s, x + s, y + s), fill=(180, 180, 200, rng.randint(80, 180)))

    mx, my = W // 2, 600
    draw.rectangle((mx - 200, my - 50, mx + 200, my + 100), fill=(20, 30, 60, 200))
    for rw in range(2):
        for rh in range(2):
            draw.rectangle((mx - 180 + rw * 240, my - 35 + rh * 65, mx - 180 + rw * 240 + 220, my - 35 + rh * 65 + 50), fill=(60, 80, 140, 150), outline=(40, 40, 60, 200), width=1)

    sign_x, sign_y = W // 2, 400
    draw.rectangle((sign_x - 80, sign_y - 25, sign_x + 80, sign_y + 25), fill=(0, 60, 120, 200), outline=(0, 100, 200, 255), width=3)

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((sign_x - 100, sign_y - 60, sign_x + 100, sign_y + 60), fill=(30, 100, 200, 25))
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle((mx - 30, my + 150, mx + 30, my + 200), fill=(40, 40, 60, 200))

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
