#!/usr/bin/env python3
"""Cover: The Jaguar Codex — Maya pyramid silhouette at dawn, descending golden serpent shadow, jade glyph spirals, jaguar silhouette."""

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Shared helpers from repo-root tools
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


W = 1600
H = 2560


def make_cover(draw: ImageDraw.ImageDraw, meta: dict) -> Image.Image:
    # Dawn gradient: dark indigo to gold
    for y in range(H):
        t = y / (H * 0.6) if y < H * 0.6 else 1.0
        if y < H * 0.6:
            r = int(15 + 200 * t)
            g = int(25 + 150 * t)
            b = int(40 + 80 * t)
        else:
            r, g, b = 10, 20, 15
        draw.rectangle([(0, y), (W, y)], fill=(r, g, b))

    # Dawn sun rising behind pyramid
    sun_x, sun_y = W // 2, int(H * 0.30)
    for rr in range(120, 0, -3):
        draw.ellipse([sun_x - rr, sun_y - rr, sun_x + rr, sun_y + rr], fill=(255, 200 + int(55 * (1 - rr / 120)), 80, max(0, 80 - rr)))
    draw.ellipse([sun_x - 60, sun_y - 60, sun_x + 60, sun_y + 60], fill=(255, 230, 120))

    # Maya pyramid silhouette (stepped)
    pyr_base = 720
    pyr_h = 480
    pyr_x = (W - pyr_base) // 2
    pyr_y = int(H * 0.52)
    steps = 9
    step_h = pyr_h // steps
    for i in range(steps):
        top_w = pyr_base - (i * (pyr_base // steps))
        x_off = (pyr_base - top_w) // 2
        y_top = pyr_y - (i * step_h)
        draw.polygon([
            (pyr_x + x_off, y_top + step_h),
            (pyr_x + x_off + top_w, y_top + step_h),
            (pyr_x + x_off + top_w - top_w // 3, y_top),
            (pyr_x + x_off + top_w // 3, y_top),
        ], fill=(20, 16, 12))

    # Temple at summit
    tw, th = 70, 50
    tx = (W - tw) // 2
    ty = pyr_y - pyr_h - th
    draw.rectangle([tx, ty, tx + tw, ty + th], fill=(30, 25, 20))

    # Descending golden serpent shadow
    for i in range(steps):
        y_pos = pyr_y - (i * step_h) - step_h // 2
        x_pos = W // 2 + i * 14 - 10
        draw.line([(x_pos - 4, y_pos), (x_pos + 4, y_pos)], fill=(220, 190, 80), width=5)
    # Serpent head at base
    sx, sy = W // 2 + steps * 14 - 10, pyr_y - step_h // 2
    draw.ellipse([sx - 25, sy - 15, sx + 25, sy + 15], fill=(30, 80, 45))
    draw.ellipse([sx - 10, sy - 6, sx - 4, sy], fill=(5, 5, 5))
    draw.ellipse([sx + 4, sy - 6, sx + 10, sy], fill=(5, 5, 5))

    # Jungle tree silhouettes at base
    for ti in range(14):
        tx2 = 20 + ti * 110
        ty2 = pyr_y + 60
        th2 = 60 + (ti % 5) * 30
        draw.rectangle([tx2, ty2, tx2 + 5, ty2 + th2], fill=(12, 25, 15))
        cr = 20 + (ti % 4) * 10
        draw.ellipse([tx2 - cr, ty2 - 8, tx2 + 5 + cr, ty2 + 15], fill=(12, 25, 15))

    # Jaguar silhouette prowling
    jx, jy = W - 180, pyr_y + 50
    draw.ellipse([jx - 18, jy - 6, jx + 18, jy + 6], fill=(4, 2, 0))
    draw.ellipse([jx + 18, jy - 10, jx + 55, jy + 5], fill=(4, 2, 0))
    draw.line([jx - 18, jy - 2, jx - 30, jy - 10], fill=(4, 2, 0), width=3)

    # Jade glyph fragments in sky
    for gx, gy in [(100, 280), (W - 130, 340), (180, 430), (W - 180, 480)]:
        draw.ellipse([gx - 14, gy - 14, gx + 14, gy + 14], outline=(50, 140, 70), width=2)
        for ri in range(1, 4):
            draw.ellipse([gx - ri * 3, gy - ri * 3, gx + ri * 3, gy + ri * 3], outline=(200, 170, 80), width=1)

    return draw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.metadata, "r", encoding="utf-8") as f:
        meta = json.load(f)

    img = Image.new("RGB", (W, H), color=(10, 20, 12))
    draw = ImageDraw.Draw(img)

    make_cover(draw, meta)
    _draw_standard_cover_title_panel(img, draw, meta)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG")
    print(f"Cover saved: {out}")


if __name__ == "__main__":
    main()
