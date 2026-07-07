#!/usr/bin/env python3
"""Cover: Dark séance parlor with velvet-draped spirit cabinet, blue-white luminescence glowing from within, dark parlor/violet velvet/ghost-light blue."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Spirit Cabinet")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Dark séance parlor gradient: deep violet-black to warm brown-black
    for y in range(H):
        t = y / H
        c = lerp_color((10, 5, 18), (25, 12, 8), t)
        draw.line([(0, y), (W, y)], fill=c)

    # Wainscoting / wall panel lines
    for y in range(400, 1600, 60):
        a = max(5, 20 - y // 100)
        draw.line([(0, y), (W, y)], fill=(20, 10, 20, a))

    # Velvet curtains framing the cabinet area
    curtain_color = (60, 15, 40)
    for side in (-1, 1):
        for i in range(8):
            cx = W // 2 + side * (200 + i * 35)
            top_w = 60 - i * 3
            pts = [
                (cx, 0),
                (cx + side * top_w, 0),
                (cx + side * 130, int(H * 0.85)),
                (cx - side * 30, int(H * 0.85)),
            ]
            shade = max(20, curtain_color[0] - i * 4)
            draw.polygon(pts, fill=(shade, max(10, shade // 3), max(15, shade // 2)))
            for fy in range(0, int(H * 0.75), 50):
                wave = int(10 * math.sin(fy / 35 + side * 2))
                draw.line([(cx + side * (20 + wave), fy), (cx + side * 50, fy + 30)],
                          fill=(40, 8, 25), width=3)

    # Spirit cabinet (dark wooden cabinet with velvet drape)
    cab_x, cab_y = W // 2 - 150, 400
    cab_w, cab_h = 300, 800
    # Cabinet frame
    draw.rectangle([cab_x, cab_y, cab_x + cab_w, cab_y + cab_h], fill=(30, 16, 12))
    draw.rectangle([cab_x - 8, cab_y - 8, cab_x + cab_w + 8, cab_y + cab_h + 8],
                   outline=(50, 30, 20), width=4)
    # Velvet drape over cabinet opening
    for i in range(10):
        dx = cab_x + i * (cab_w // 10)
        for y in range(cab_y + 50, cab_y + cab_h - 50, 6):
            wave = int(8 * math.sin(y / 40 + i * 1.2))
            draw.line([(dx + wave, y), (dx + wave + 1, y + 1)],
                      fill=(80 + random.randint(-10, 10), 20, 50 + random.randint(-10, 10), 200))

    # Blue-white luminescence glowing from within the cabinet
    glow_cx = W // 2
    glow_cy = cab_y + cab_h // 2
    for r in range(350, 10, -10):
        a = max(3, 60 - r // 6)
        draw.ellipse(
            [glow_cx - r, glow_cy - r, glow_cx + r, glow_cy + r],
            fill=(150, 200, 255, a),
        )
    for r in range(180, 10, -8):
        a = max(5, 80 - r // 3)
        draw.ellipse(
            [glow_cx - r, glow_cy - r, glow_cx + r, glow_cy + r],
            fill=(200, 230, 255, a),
        )
    # Bright core
    draw.ellipse(
        [glow_cx - 30, glow_cy - 60, glow_cx + 30, glow_cy + 60],
        fill=(220, 240, 255, 200),
    )

    # Light rays streaming from cabinet cracks
    for angle in range(-30, 30, 5):
        rad = math.radians(angle)
        for d in range(0, 300, 15):
            x = glow_cx + int(d * math.sin(rad) * 0.3)
            y = glow_cy + int(d * math.cos(rad) * 0.5)
            if y > H or x < 0 or x > W:
                break
            a = max(2, 40 - d // 10)
            draw.point((x, y), fill=(180, 220, 255, a))

    # Séance table in foreground
    table_top = 1350
    draw.ellipse([(W // 2 - 200, table_top), (W // 2 + 200, table_top + 50)], fill=(40, 25, 18))
    draw.ellipse([(W // 2 - 180, table_top + 5), (W // 2 + 180, table_top + 45)], fill=(50, 32, 22))
    # Table legs
    for lx in [W // 2 - 150, W // 2 + 150]:
        draw.line([(lx, table_top + 40), (lx - 20, table_top + 200)], fill=(30, 18, 12), width=8)

    # Candles on table
    for candle_x in [W // 2 - 80, W // 2 + 80]:
        draw.rectangle([candle_x - 6, table_top - 60, candle_x + 6, table_top], fill=(200, 190, 170))
        draw.ellipse([candle_x - 4, table_top - 68, candle_x + 4, table_top - 60], fill=(255, 200, 50))
        for r in range(20, 0, -3):
            a = int(30 - r * 1.5)
            draw.ellipse([candle_x - r, table_top - 70 - r, candle_x + r, table_top - 70 + r],
                         fill=(255, 200, 80, max(0, a)))

    # Ouija planchette on table
    draw.ellipse([(W // 2 - 50, table_top - 15), (W // 2 + 50, table_top + 10)], fill=(180, 160, 120))
    draw.polygon([(W // 2, table_top - 25), (W // 2 - 10, table_top - 15), (W // 2 + 10, table_top - 15)],
                 fill=(50, 45, 40))

    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
