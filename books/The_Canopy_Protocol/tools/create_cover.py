#!/usr/bin/env python3
"""Cover art for The Canopy Protocol — EcoThriller set in Pacific Northwest old-growth forest."""

import argparse, json, sys, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

# Import shared helpers
repo_root = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(repo_root))

from tools.cover_utils import (
    _standard_cover_font, _standard_cover_repair_text, _standard_cover_wrap,
    _standard_cover_center, _standard_cover_title_font,
    _standard_cover_resolve_title, _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)

W, H = 1600, 2560


def draw_forest_bg(draw):
    """Draw a dense old-growth forest canopy scene."""
    # Sky gradient — smoky green-gray
    for y in range(600):
        t = y / 600
        r = int(40 + t * 20)
        g = int(70 + t * 30)
        b = int(45 + t * 10)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Mid-layer gradient — deeper green
    for y in range(600, 1100):
        t = (y - 600) / 500
        r = int(20 + t * 10)
        g = int(50 + t * 15)
        b = int(25 + t * 5)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Ground — dark forest floor
    for y in range(1100, H):
        t = (y - 1100) / 500
        r = int(10 + t * 5)
        g = int(25 + t * 10)
        b = int(10 + t * 5)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Draw tree trunks — ancient Douglas firs
    trunk_positions = [
        (80, 0.9), (220, 1.0), (380, 0.85), (520, 1.0),
        (680, 0.9), (840, 1.0), (1000, 0.85), (1120, 0.95)
    ]

    for x, scale in trunk_positions:
        tw = int(45 * scale)
        th = int(1200 * scale)
        # Trunk
        for i in range(tw):
            shade = 40 + int(30 * math.sin(i * 0.3)) + int(20 * (1 - abs(i - tw/2) / (tw/2)))
            draw.line([(x - tw//2 + i, 200), (x - tw//2 + i, 200 + th)], fill=(shade, shade + 15, shade - 10))

    # Canopy branches
    for _ in range(120):
        bx = int(W * math.sin(_ * 1.7) * 0.5 + W / 2)
        by = 80 + int(120 * math.sin(_ * 0.9))
        br = 20 + int(80 * math.sin(_ * 2.3) ** 2)
        shade = 20 + int(60 * math.sin(_ * 1.1) ** 2)
        draw.ellipse([bx - br, by - br, bx + br, by + br], fill=(shade, shade + 40, shade + 10))

    # Light shafts through canopy
    for sx in [150, 400, 650, 900]:
        for sy in range(0, 800, 8):
            alpha = int(12 * (1 - sy / 800) * (1 - abs(sx - W/2) / (W/2)))
            r = 180 + alpha
            g = 200 + alpha
            b = 140 + alpha
            draw.line([(sx + int(10 * math.sin(sy * 0.05)), sy), (sx + int(10 * math.sin(sy * 0.05)) + 8, sy)], fill=(min(r, 255), min(g, 255), min(b, 255)), width=1)

    # Fallen log silhouette at bottom
    for lx in range(100, 1100):
        ly = 1300 + int(20 * math.sin(lx * 0.04))
        shade = int(30 + 20 * math.sin(lx * 0.1))
        draw.line([(lx, ly), (lx, ly + 15)], fill=(shade, shade + 10, shade - 5))


def make_cover(metadata, out_path):
    img = Image.new("RGB", (W, H), (30, 50, 25))
    draw = ImageDraw.Draw(img)

    # Background
    draw_forest_bg(draw)

    # Draw smoke/haze overlay
    for y in range(0, 500):
        for x in range(0, W, 3):
            if int(math.sin(x * 0.05 + y * 0.1) * math.cos(y * 0.02)) > 0.6:
                alpha = int(8 * (1 - y / 500))
                draw.point((x, y), fill=(180 - alpha, 180 - alpha, 150 - alpha))

    # Use the standard title panel
    title = _standard_cover_resolve_title(metadata)
    author = _standard_cover_resolve_author(metadata)

    _draw_standard_cover_title_panel(img, title, author, metadata.get("model", ""))

    img.save(str(out_path))
    print(f"Cover saved to {out_path}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True)
    p.add_argument("--out", required=True)
    args = p.parse_args()
    with open(args.metadata) as f:
        metadata = json.load(f)
    make_cover(metadata, Path(args.out))
