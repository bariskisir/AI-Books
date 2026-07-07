#!/usr/bin/env python3
"""Cover: The Simurgh Quest — obsidian Simurgh statue, thirty-colored feather glowing against cosmic stair, two tiny figures at base."""

import json
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font, _standard_cover_repair_text, _standard_cover_wrap,
    _standard_cover_center, _standard_cover_title_font,
    _standard_cover_resolve_title, _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


def make_cover(metadata: dict, out_path: str):
    """Draw The Simurgh Quest cover with a cosmic bird over mountain peaks."""
    title = _standard_cover_resolve_title(metadata)
    author = _standard_cover_resolve_author(metadata)
    model = metadata.get("model", "")

    W, H = 1600, 2560
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Cosmic gradient: deep blue-black to indigo to purple
    for y in range(H):
        t = y / H
        if t < 0.35:
            r, g, b = 5, 3, 18
        elif t < 0.55:
            s = (t - 0.35) / 0.20
            r, g, b = int(5 + 15 * s), int(3 + 10 * s), int(18 + 40 * s)
        else:
            s = (t - 0.55) / 0.45
            r, g, b = int(20 - 10 * s), int(13 - 8 * s), int(58 - 30 * s)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Stars
    rng = random.Random(212)
    for _ in range(250):
        sx = rng.randint(20, W - 20)
        sy = rng.randint(10, int(H * 0.45))
        sz = rng.randint(1, 2)
        sa = rng.randint(150, 255)
        draw.ellipse([sx - sz, sy - sz, sx + sz, sy + sz], fill=(255, 255, 255, sa))

    # Cosmic nebula glow
    nebula = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(nebula)
    nd.ellipse([200, 200, 1400, 900], fill=(100, 40, 160, 12))
    nd.ellipse([600, 100, 1000, 700], fill=(60, 100, 200, 8))
    nebula = nebula.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, nebula)
    draw = ImageDraw.Draw(img, "RGBA")

    # Cosmic stair (a stairway made of light/platforms ascending to upper right)
    stair_pts = []
    for i in range(12):
        sx = int(200 + i * 100 + rng.randint(-15, 15))
        sy = int(1800 - i * 100 + rng.randint(-10, 10))
        sw = int(120 - i * 6)
        sh = int(8 + i)
        alpha = max(30, 200 - i * 14)
        stair_color = (180, 150, 255, alpha)
        draw.rectangle([sx, sy, sx + sw, sy + sh], fill=stair_color)
        # Glow around each step
        draw.ellipse([sx - 15, sy - 6, sx + sw + 15, sy + sh + 6], fill=(120, 100, 200, max(5, alpha // 4)))
        stair_pts.append((sx, sy, sw, sh))

    # Obsidian Simurgh statue — black, angular, organic
    scx, scy = W // 2, int(H * 0.40)
    # Body (angular obsidian)
    draw.polygon([
        (scx - 40, scy + 60), (scx - 20, scy - 10), (scx - 5, scy - 40),
        (scx + 5, scy - 40), (scx + 20, scy - 10), (scx + 40, scy + 60),
        (scx + 15, scy + 80), (scx - 15, scy + 80),
    ], fill=(12, 10, 15, 240))
    # Left wing (sweeping up, jagged)
    draw.polygon([
        (scx - 15, scy + 5), (scx - 70, scy - 30), (scx - 110, scy - 60),
        (scx - 80, scy - 50), (scx - 50, scy - 25), (scx - 18, scy - 5),
    ], fill=(8, 6, 12, 240))
    # Right wing
    draw.polygon([
        (scx + 15, scy + 5), (scx + 70, scy - 30), (scx + 110, scy - 60),
        (scx + 80, scy - 50), (scx + 50, scy - 25), (scx + 18, scy - 5),
    ], fill=(8, 6, 12, 240))
    # Head
    draw.ellipse([scx - 8, scy - 55, scx + 8, scy - 35], fill=(15, 12, 18, 240))
    # Eye (small red glow)
    draw.ellipse([scx + 2, scy - 50, scx + 6, scy - 44], fill=(200, 40, 30, 220))
    # Obsidian crack lines
    for _ in range(8):
        sx2 = scx + rng.randint(-30, 30)
        sy2 = scy + rng.randint(-30, 50)
        draw.line([(sx2, sy2), (sx2 + rng.randint(-10, 10), sy2 + rng.randint(-15, 15))], fill=(25, 22, 28, 180), width=1)

    # Thirty-colored glowing feather
    feather_x, feather_y = scx + 60, scy + 30
    for i in range(30):
        hue_r = int(100 + 155 * (i / 29))
        hue_g = int(50 + 200 * (abs(0.5 - i / 29) * 2))
        hue_b = int(50 + 200 * (1 - i / 29))
        fr = i * 0.5
        draw.polygon([
            (feather_x + 2, feather_y + i * 4),
            (feather_x + 20 + fr, feather_y + i * 4 - 6),
            (feather_x + 18 + fr, feather_y + i * 4 + 2),
            (feather_x + 2, feather_y + i * 4 + 4),
        ], fill=(hue_r, hue_g, hue_b, 200))
        # Glow around each feather segment
        draw.ellipse([
            feather_x + 8 + fr - 8, feather_y + i * 4 - 6,
            feather_x + 18 + fr + 6, feather_y + i * 4 + 8
        ], fill=(hue_r, hue_g, hue_b, max(10, 80 - i * 2)))

    # Two tiny figures at base of the stair
    fig_color = (180, 160, 140, 230)
    for fi, (fx, fy) in enumerate([(650, 1750), (720, 1760)]):
        draw.ellipse([fx - 3, fy - 10, fx + 3, fy - 4], fill=fig_color)
        draw.rectangle([fx - 3, fy - 4, fx + 3, fy + 6], fill=fig_color)
        # Tiny outstretched arm toward the stair/feather
        draw.line([(fx + 3, fy - 2), (fx + 12, fy - 6)], fill=fig_color, width=1)

    _draw_standard_cover_title_panel(img, title, author, model)
    img = img.convert("RGB")
    img.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    with open(args.metadata) as f:
        metadata = json.load(f)

    make_cover(metadata, args.out)
