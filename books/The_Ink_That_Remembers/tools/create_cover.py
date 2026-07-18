#!/usr/bin/env python3
"""Cover: The Ink That Remembers — Fantasy tattoo magic: a memory-scarred apprentice discovers a lost ink recipe that can rewrite the past."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Warm parchment-and-ink palette — deep burgundy, aged gold, ink-black, faded crimson
PALETTE = [
    (100, 30, 45),    # deep burgundy
    (140, 100, 55),   # aged gold
    (30, 25, 40),     # ink-black
    (120, 50, 50),    # faded crimson
    (160, 130, 80),   # parchment
    (70, 40, 50),     # dark mauve
]

rng = random.Random()
rng.seed(311285793)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (18, 8, 12, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Warm vertical gradient: dark top (burgundy-ink) to warm bottom (parchment) ---
    top_r, top_g, top_b = 25, 10, 18
    bot_r, bot_g, bot_b = 65, 40, 30
    for y in range(H):
        t = y / H
        r = int(top_r + (bot_r - top_r) * t)
        g = int(top_g + (bot_g - top_g) * t)
        b = int(top_b + (bot_b - top_b) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # --- Central scribe silhouette (torso/back) made from layered polygons ---
    cx, cy = W // 2, 900
    scribe_alpha = 200

    # Shoulders and torso
    body_pts = [
        (cx - 200, 400), (cx - 100, 300), (cx + 100, 300), (cx + 200, 400),
        (cx + 180, 900), (cx - 180, 900),
    ]
    draw.polygon(body_pts, fill=(12, 5, 10, scribe_alpha))

    # Head
    draw.ellipse((cx - 45, 220, cx + 45, 310), fill=(12, 5, 10, scribe_alpha))

    # Arms extending down
    draw.polygon([
        (cx - 200, 400), (cx - 280, 600), (cx - 320, 850), (cx - 280, 900),
        (cx - 220, 900), (cx - 180, 600),
    ], fill=(12, 5, 10, scribe_alpha - 20))
    draw.polygon([
        (cx + 200, 400), (cx + 280, 600), (cx + 320, 850), (cx + 280, 900),
        (cx + 220, 900), (cx + 180, 600),
    ], fill=(12, 5, 10, scribe_alpha - 20))

    # --- Organic swirling tattoo lines emanating from the back ---
    # These look like calligraphic ink strokes spreading across the body and outward
    ink_colors = [
        (160, 120, 70, 180),   # golden ink
        (90, 50, 55, 200),     # deep crimson ink
        (170, 140, 85, 150),   # pale gold
        (60, 40, 60, 220),     # dark ink
    ]

    for _ in range(120):
        # Start point: somewhere on the torso
        angle = rng.uniform(0, math.tau)
        radius = rng.uniform(10, 120)
        sx = cx + math.cos(angle) * radius
        sy = cy - rng.uniform(20, 200) * rng.random()

        # Spiral outward in a flowing organic curve
        pts = []
        segs = rng.randint(12, 30)
        cur_angle = angle + rng.uniform(-0.5, 0.5)
        cur_radius = rng.uniform(5, 20)
        for i in range(segs):
            cur_angle += rng.uniform(-0.4, 0.4)
            cur_radius += rng.uniform(3, 14)
            nx = sx + math.cos(cur_angle) * cur_radius
            ny = sy + math.sin(cur_angle) * cur_radius * 0.7 + i * rng.uniform(-8, 12)
            pts.append((nx, ny))

        # Only draw if within the upper portion
        if any(p[1] < 1600 for p in pts):
            ink = rng.choice(ink_colors)
            width = rng.randint(1, 4)
            try:
                draw.line(pts, fill=(*ink[:3], min(255, max(20, ink[3] + rng.randint(-40, 40)))), width=width)
            except Exception:
                pass

    # --- Large decorative circular mandala behind the figure (like a scribe's wheel / ink seal) ---
    for ring in range(6):
        rr = 120 + ring * 45
        alpha = 40 - ring * 5
        col = rng.choice(PALETTE)
        draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr),
                     outline=(*col, max(8, alpha)), width=2)

    # Radial spokes from the mandala center
    for sp in range(24):
        ang = sp * (math.tau / 24) + rng.uniform(-0.05, 0.05)
        inner = 130
        outer = 360
        draw.line((
            cx + math.cos(ang) * inner, cy + math.sin(ang) * inner,
            cx + math.cos(ang) * outer, cy + math.sin(ang) * outer,
        ), fill=(100, 70, 50, 30), width=1)

    # --- Floating memory motes (glowing orbs that drift upward from the tattoos) ---
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)

    for _ in range(45):
        mx = rng.randint(200, 1400)
        my = rng.randint(100, 1600)
        mr = rng.randint(6, 18)
        # Warm glow
        glow_col = (200, 170, 110, rng.randint(15, 40))
        gd.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=glow_col)
        # Core
        core_col = (240, 220, 160, rng.randint(60, 140))
        gd.ellipse((mx - mr // 3, my - mr // 3, mx + mr // 3, my + mr // 3), fill=core_col)

    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- Additional small ink-dot particles (like splattered ink) ---
    for _ in range(80):
        px = rng.randint(50, W - 50)
        py = rng.randint(50, 1700)
        pr = rng.uniform(0.5, 3.0)
        pc = rng.choice([(60, 40, 45), (40, 30, 35), (140, 110, 70), (90, 55, 50)])
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(*pc, rng.randint(40, 120)))

    # --- Subtle horizontal divider line of "ink" above the title panel area ---
    for x in range(0, W, 2):
        wave_y = 1740 + int(math.sin(x / 80) * 4)
        draw.point((x, wave_y), fill=(100, 70, 55, 60))
    for x in range(0, W, 3):
        wave_y = 1750 + int(math.sin(x / 60 + 1) * 3)
        draw.point((x, wave_y), fill=(130, 95, 65, 40))

    # --- Calligraphic accent strokes near the top (ink-brush style) ---
    for _ in range(8):
        sx = rng.randint(100, W - 100)
        sy = rng.randint(30, 120)
        stroke_len = rng.randint(60, 200)
        stroke_pts = []
        for si in range(stroke_len):
            px = sx + si * rng.uniform(0.6, 1.2)
            py = sy + math.sin(si * 0.15) * rng.uniform(2, 8) + rng.uniform(-1, 1)
            stroke_pts.append((px, py))
        stroke_col = (120, 85, 60, rng.randint(30, 70))
        try:
            draw.line(stroke_pts, fill=stroke_col, width=rng.randint(1, 2))
        except Exception:
            pass

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()
