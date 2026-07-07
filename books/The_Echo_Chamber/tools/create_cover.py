#!/usr/bin/env python3
"""Cover: The Echo Chamber — Empty radio station booth, microphone, sound wave visualizations on dark walls."""

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
    title = meta.get("title", "The Echo Chamber")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("echo-chamber")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(20 + 15 * t); g = int(18 + 12 * t); b = int(25 + 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    mx, my = W // 2, 1200
    draw.ellipse((mx - 12, my - 12, mx + 12, my + 12), fill=(50, 50, 55, 200))
    draw.ellipse((mx - 5, my - 5, mx + 5, my + 5), fill=(60, 60, 65, 200))
    draw.line((mx, my - 12, mx, my - 40), fill=(60, 60, 65, 200), width=4)
    draw.line((mx - 12, my, mx - 30, my), fill=(60, 60, 65, 200), width=2)
    draw.line((mx + 12, my, mx + 30, my), fill=(60, 60, 65, 200), width=2)

    for wave in range(3):
        base_y = 800 + wave * 200
        for x in range(0, W, 3):
            y_wave = base_y + int(40 * math.sin(x * 0.02 + wave * 2) * math.sin(x * 0.01))
            alpha = 40 + int(30 * (1 - abs(x - W / 2) / (W / 2)))
            draw.point((x, y_wave), fill=(80, 200, 220, alpha))

    for wave in range(2):
        base_y = 1400 + wave * 250
        for x in range(0, W, 2):
            y_wave = base_y + int(30 * math.sin(x * 0.015 + wave * 3) * math.cos(x * 0.008))
            alpha = 20 + int(20 * (1 - abs(x - W / 2) / (W / 2)))
            draw.point((x, y_wave), fill=(80, 200, 220, alpha))

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
