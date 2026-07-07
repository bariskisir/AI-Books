#!/usr/bin/env python3
"""Cover: The Best Worst Eulogy — Empty church pews, single microphone at podium, warm afternoon light through stained glass."""

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
    title = meta.get("title", "The Best Worst Eulogy")
    author = meta.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = meta.get("model", "")

    random.seed("best-worst-eulogy")
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / H
        r = int(120 + 80 * (1 - t)); g = int(80 + 60 * (1 - t)); b = int(50 + 40 * (1 - t))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    for wx in range(300, 1300, 250):
        draw.rectangle((wx, 600, wx + 140, 1600), fill=(80, 55, 40, 150))
        for pl in range(600, 1600, 40):
            draw.line((wx + 10, pl, wx + 130, pl), fill=(60, 40, 30, 80), width=2)

    arch = []
    for x in range(200, W - 200, 2):
        y_arch = 500 - int(200 * math.sin((x - 200) * math.pi / (W - 400)))
        arch.append((x, y_arch))
    if arch:
        draw.arc((200, 100, W - 200, 500), 0, 180, fill=(150, 100, 60, 100), width=8)

    sg_y = 300
    for c in [(200, 80, 80), (200, 200, 80), (80, 80, 200), (200, 150, 50)]:
        for x in range(300, 1300, 50):
            draw.line((x, sg_y, x + 30, sg_y + 100), fill=(*c, 30), width=2)

    draw.rectangle((W // 2 - 30, 1020, W // 2 + 30, 1080), fill=(30, 30, 30, 200))
    draw.ellipse((W // 2 - 15, 980, W // 2 + 15, 1020), fill=(40, 40, 40, 200))
    draw.line((W // 2 + 15, 1000, W // 2 + 30, 1010), fill=(60, 60, 60, 200), width=2)

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
