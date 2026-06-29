#!/usr/bin/env python3
"""Cover for The Bookbinder of Prague — warm workshop, leather, gold tooling."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


def draw_workshop_scene(draw):
    """Draw a warm bookbinding workshop."""
    rng = random.Random("bookbinder-prague-42")

    # Warm workshop gradient background
    for y in range(H):
        t = y / H
        r = int(60 + 100 * t)
        g = int(35 + 55 * t)
        b = int(20 + 30 * t)
        draw.line((0, y, W, y), fill=(min(r, 255), min(g, 255), min(b, 255)))

    # Warm light glow from upper right
    for i in range(40):
        alpha = int(25 * (1 - i / 40))
        r = 300 + i * 20
        draw.ellipse((W - 300 - r, 200 - r, W - 300 + r, 200 + r),
                     fill=(255, 220, 160, alpha))

    # Workshop window (arched, with Prague skyline view)
    win_x, win_y = W // 2 - 200, 150
    draw.arc((win_x, win_y, win_x + 400, win_y + 300), 0, 180,
             fill=(180, 140, 90), width=12)
    draw.rectangle((win_x, win_y + 150, win_x + 400, win_y + 480),
                   fill=(60, 75, 100))
    draw.rectangle((win_x + 10, win_y + 160, win_x + 390, win_y + 470),
                   fill=(140, 180, 210))
    # Window mullions
    draw.line((W // 2, win_y + 150, W // 2, win_y + 480), fill=(80, 70, 55), width=8)
    draw.line((win_x, win_y + 300, win_x + 400, win_y + 300), fill=(80, 70, 55), width=6)
    # Distant spires through window
    for sx in [W//2 - 100, W//2, W//2 + 80]:
        sh = rng.randint(40, 80)
        draw.polygon([(sx - 6, 450), (sx + 6, 450), (sx, 450 - sh)],
                     fill=(50, 55, 65))

    # Workbench
    bench_y = 1450
    draw.rectangle((80, bench_y, W - 80, bench_y + 30), fill=(120, 80, 50))
    draw.rectangle((80, bench_y - 8, W - 80, bench_y + 2), fill=(160, 110, 70))
    # Wood grain
    for _ in range(30):
        gx = rng.randint(100, W - 100)
        draw.line((gx, bench_y - 6, gx + rng.randint(-40, 40), bench_y + 25),
                  fill=(140, 95, 60, 80), width=1)

    # Books being bound (on bench)
    book_colors = [(180, 40, 30), (30, 60, 120), (40, 110, 50), (150, 100, 30), (100, 30, 80)]
    for i in range(5):
        bx = 250 + i * 220
        by = bench_y - rng.randint(80, 150)
        bw = rng.randint(60, 100)
        bh = rng.randint(100, 160)
        bc = book_colors[i]
        draw.rectangle((bx, by, bx + bw, by + bh), fill=bc)
        # Spine detail
        draw.rectangle((bx - 8, by, bx + 4, by + bh), fill=tuple(c // 3 for c in bc))
        # Gold tooling lines
        for gy in [by + 20, by + bh - 30]:
            draw.line((bx + 4, gy, bx + bw - 4, gy), fill=(200, 170, 90), width=2)
        draw.rectangle((bx + bw // 2 - 10, by + bh // 2, bx + bw // 2 + 10, by + bh // 2 + 15),
                       fill=(210, 180, 100))

    # Open book on bench
    obx, oby = W // 2 - 80, bench_y - 200
    draw.polygon([(obx, oby + 180), (obx + 160, oby + 180), (obx + 140, oby + 20), (obx + 20, oby + 20)],
                 fill=(230, 215, 180))
    draw.line((obx + 80, oby + 20, obx + 80, oby + 180), fill=(180, 160, 120), width=3)
    # Text lines on pages
    for ly in range(oby + 40, oby + 160, 18):
        draw.line((obx + 20, ly, obx + 70, ly), fill=(160, 140, 100), width=1)
        draw.line((obx + 90, ly, obx + 140, ly), fill=(160, 140, 100), width=1)

    # Thread and needle
    tx, ty = 950, bench_y - 100
    draw.line((tx, ty, tx + 120, ty - 80), fill=(200, 180, 150), width=2)
    draw.line((tx + 120, ty - 80, tx + 100, ty - 120), fill=(200, 180, 150), width=2)
    # Needle
    draw.line((tx + 80, ty - 40, tx + 140, ty - 100), fill=(180, 175, 170), width=3)
    draw.ellipse((tx + 135, ty - 105, tx + 145, ty - 95), fill=(220, 215, 210))

    # Bone folder
    draw.rounded_rectangle((1150, bench_y - 140, 1210, bench_y - 10), radius=10,
                           fill=(200, 185, 160), outline=(160, 140, 110), width=2)

    # Shelves with books behind bench
    shelf_y = 850
    for shelf in range(3):
        sy = shelf_y + shelf * 180
        draw.rectangle((40, sy, W - 40, sy + 10), fill=(100, 70, 40))
        for bx in range(60, W - 60, rng.randint(30, 70)):
            bh = rng.randint(80, 160)
            bw = rng.randint(25, 55)
            shade = rng.randint(40, 180)
            color = (shade, shade // 2, shade // 3)
            if rng.random() > 0.5:
                color = (shade // 2, shade // 3, shade)
            draw.rectangle((bx, sy - bh, bx + bw, sy), fill=color)
            draw.rectangle((bx, sy - bh, bx + 4, sy), fill=tuple(c // 3 for c in color))

    # Warm dust motes / atmosphere
    for _ in range(80):
        dx = rng.randint(0, W)
        dy = rng.randint(0, H)
        ds = rng.randint(1, 3)
        draw.rectangle((dx, dy, dx + ds, dy + ds),
                       fill=(255, 220, 150, rng.randint(15, 50)))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Bookbinder of Prague")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("bookbinder-prague-42")

    img = Image.new("RGBA", (W, H), (30, 25, 18, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_workshop_scene(draw)

    _draw_standard_cover_title_panel(
        img,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG", optimize=True)
    print(f"Cover saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
