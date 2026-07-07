#!/usr/bin/env python3
"""Cover for Sample Book — coastal town, library, warm tones."""

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
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


def draw_coastal_scene(draw):
    """Draw a warm coastal town with library elements."""
    rng = random.Random("sample-book-cover")

    # Sky gradient: warm sunset tones
    for y in range(1800):
        t = y / 1800
        r = int(40 + 180 * t)
        g = int(30 + 120 * t)
        b = int(60 + 100 * (1 - t))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b)))

    # Sun
    for i in range(30):
        alpha = int(100 * (1 - i / 30))
        r = 80 + i * 6
        draw.ellipse((W//2 - r, 300 - r, W//2 + r, 300 + r),
                     fill=(255, 220, 150, alpha))

    # Sea horizon
    for y in range(1100, 1800, 4):
        t = (y - 1100) / 700
        r = int(20 + 80 * t)
        g = int(40 + 100 * t)
        b = int(80 + 100 * t)
        draw.line((0, y, W, y), fill=(r, g, b))

    # Coastal town silhouette
    buildings = [
        (100, 1050, 140, 150), (260, 1080, 100, 120), (380, 1020, 150, 180),
        (550, 1050, 80, 150), (650, 1000, 120, 200), (790, 1070, 100, 130),
        (910, 990, 160, 210), (1100, 1040, 100, 160), (1250, 1010, 130, 190),
        (1400, 1060, 90, 140),
    ]
    for bx, by, bw, bh in buildings:
        draw.rectangle((bx, by, bx + bw, by + bh), fill=(30, 25, 35))
        # Windows
        for wy in range(by + 15, by + bh - 10, 30):
            for wx in range(bx + 15, bx + bw - 10, 30):
                if rng.random() > 0.4:
                    draw.rectangle((wx, wy, wx + 10, wy + 14),
                                   fill=(255, 200, 100, rng.randint(80, 200)))

    # Lighthouse
    lx = 1200
    draw.rectangle((lx - 20, 700, lx + 20, 1050), fill=(50, 45, 40))
    draw.polygon([(lx - 40, 700), (lx + 40, 700), (lx, 600)], fill=(45, 40, 35))
    draw.ellipse((lx - 15, 620, lx + 15, 650), fill=(255, 240, 200, 200))
    # Light beam
    for i in range(8):
        alpha = int(60 - i * 7)
        draw.polygon([(lx, 635), (lx + 300 + i*40, 400 - i*30), (lx + 320 + i*40, 420 - i*30)],
                     fill=(255, 250, 200, max(0, alpha)))

    # Library building (foreground)
    lib_x = W // 2 - 200
    draw.rectangle((lib_x, 900, lib_x + 400, 1200), fill=(60, 50, 40))
    draw.polygon([(lib_x - 30, 900), (lib_x + 200, 780), (lib_x + 430, 900)],
                 fill=(50, 40, 30))
    # Columns
    for cx in [lib_x + 60, lib_x + 160, lib_x + 260, lib_x + 340]:
        draw.rectangle((cx - 8, 920, cx + 8, 1200), fill=(80, 70, 60))
    # Door
    draw.rectangle((lib_x + 140, 1020, lib_x + 260, 1200), fill=(40, 30, 20))
    # Windows
    for wx in [lib_x + 50, lib_x + 290]:
        draw.rectangle((wx - 20, 950, wx + 20, 1010), fill=(200, 180, 140, 180))

    # Books/archive boxes in foreground
    for i in range(12):
        bx = rng.randint(100, W - 100)
        by = rng.randint(1700, 1800)
        bw = rng.randint(15, 40)
        bh = rng.randint(30, 60)
        shade = rng.randint(100, 160)
        draw.rectangle((bx, by - bh, bx + bw, by),
                       fill=(shade, shade - 20, shade - 40))

    # Birds
    for _ in range(15):
        bx = rng.randint(100, W - 100)
        by = rng.randint(200, 600)
        draw.arc((bx, by, bx + 20, by + 10), 0, 180,
                 fill=(30, 30, 30, 120), width=2)


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "Sample Book")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("sample-book-cover")

    img = Image.new("RGBA", (W, H), (20, 20, 30, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_coastal_scene(draw)

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
