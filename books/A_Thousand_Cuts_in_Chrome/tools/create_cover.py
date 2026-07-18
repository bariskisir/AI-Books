#!/usr/bin/env python3
"""Cover: A Thousand Cuts in Chrome — Corporate espionage/bio-hacking: a microchip smuggler with a memory-splicing
implant discovers her own first memory is a brand she never bought. Fragmented chrome face, neural splice-lines,
identity barcodes, and data-shard particles against a cold steel-indigo void."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

rng = random.Random()
rng.seed(987654321)


def _make_shard_polygon(cx: float, cy: float, radius: float, points: int,
                        chaos: float) -> list[tuple[float, float]]:
    """Return a list of polygon vertices approximating a jagged shard centred at (cx, cy)."""
    verts = []
    for i in range(points):
        angle = math.tau * i / points + rng.uniform(-0.15, 0.15)
        rad = radius * rng.uniform(1.0 - chaos, 1.0 + chaos)
        verts.append((cx + math.cos(angle) * rad, cy + math.sin(angle) * rad))
    return verts


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── base canvas ──────────────────────────────────────────────────────────
    img = Image.new("RGBA", (W, H), (8, 6, 18, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── gradient: deep steel-blue at top → near-black indigo at bottom ──────
    top_col = (45, 60, 95)
    bot_col = (6, 4, 18)
    for y in range(H):
        t = y / H
        r = int(top_col[0] + (bot_col[0] - top_col[0]) * t)
        g = int(top_col[1] + (bot_col[1] - top_col[1]) * t)
        b = int(top_col[2] + (bot_col[2] - top_col[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── ambient glow behind the face ─────────────────────────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    glow_cx, glow_cy = W // 2, H // 2 - 200
    for _ in range(5):
        rad = rng.randint(250, 450)
        alpha = rng.randint(10, 25)
        gd.ellipse((glow_cx - rad, glow_cy - rad, glow_cx + rad, glow_cy + rad),
                   fill=(55, 90, 150, alpha))
    # cold cyan centre
    gd.ellipse((glow_cx - 120, glow_cy - 120, glow_cx + 120, glow_cy + 120),
               fill=(30, 160, 200, 18))
    glow = glow.filter(ImageFilter.GaussianBlur(45))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── fragmented face silhouette (geometric shards) ───────────────────────
    face_cx, face_cy = W // 2, H // 2 - 280

    # Build a set of overlapping shards that suggest a face contour
    shard_data = [
        # (offset_x, offset_y, radius, points, chaos, colour)
        # Crown / top of head
        (0, -320, 240, 7, 0.35, (65, 85, 120, 180)),
        # Left cheek
        (-150, -30, 180, 6, 0.40, (80, 100, 140, 160)),
        # Right cheek
        (160, -40, 175, 6, 0.38, (70, 90, 130, 170)),
        # Jaw / chin
        (-40, 210, 200, 8, 0.30, (55, 75, 110, 175)),
        # Forehead left
        (-100, -200, 160, 5, 0.45, (90, 110, 150, 150)),
        # Forehead right
        (110, -190, 150, 5, 0.42, (85, 105, 145, 155)),
        # Nose region
        (15, 30, 130, 6, 0.35, (75, 95, 130, 165)),
        # Left eye area (darker)
        (-90, -70, 100, 5, 0.50, (40, 50, 75, 200)),
        # Right eye area (darker)
        (90, -60, 95, 5, 0.48, (35, 45, 70, 200)),
    ]

    shard_polys = []
    for ox, oy, radius, pts, chaos, colour in shard_data:
        poly = _make_shard_polygon(face_cx + ox, face_cy + oy, radius, pts, chaos)
        draw.polygon(poly, fill=colour)
        # Chrome edge highlight on each shard
        highlight = (
            min(255, colour[0] + 80),
            min(255, colour[1] + 100),
            min(255, colour[2] + 110),
            120,
        )
        draw.polygon(poly, outline=highlight, width=2)
        shard_polys.append(poly)

    # ── the "cut" lines — thin glowing lacerations across the face ──────────
    for _ in range(12):
        x1 = rng.randint(face_cx - 300, face_cx + 300)
        y1 = rng.randint(face_cy - 300, face_cy + 250)
        angle = rng.uniform(-0.6, 0.6)
        length = rng.randint(40, 180)
        x2 = x1 + math.cos(angle) * length
        y2 = y1 + math.sin(angle) * length
        cut_bright = rng.randint(180, 255)
        cut_colour = (cut_bright, cut_bright // 2, cut_bright // 4,
                      rng.randint(90, 180))
        draw.line((x1, y1, x2, y2), fill=cut_colour, width=rng.randint(1, 3))

    # ── neural splice-lines connecting shards (thin cyan threads) ────────────
    for _ in range(40):
        sx = rng.randint(face_cx - 280, face_cx + 280)
        sy = rng.randint(face_cy - 300, face_cy + 250)
        ex = sx + rng.randint(-120, 120)
        ey = sy + rng.randint(-120, 120)
        alpha = rng.randint(30, 100)
        draw.line((sx, sy, ex, ey), fill=(40, 200, 220, alpha), width=1)

    # ── identity barcode (vertical chrome lines, right side) ────────────────
    barcode_x = W - 100
    barcode_top = 300
    barcode_bot = 1450
    bw_base = 4
    for i in range(30):
        bx = barcode_x + i * 3 + rng.randint(-1, 1)
        bw = bw_base + rng.randint(-1, 3)
        bh = rng.randint(80, barcode_bot - barcode_top)
        by = barcode_top + rng.randint(0, barcode_bot - barcode_top - bh)
        grey = rng.randint(100, 200)
        draw.rectangle((bx, by, bx + max(1, bw), by + bh),
                       fill=(grey, grey + 10, grey + 20, rng.randint(60, 140)))

    # ── corporate brand mark (subtle logo-like circle + arcs) ────────────────
    brand_cx, brand_cy = W - 160, 900
    draw.ellipse((brand_cx - 45, brand_cy - 45, brand_cx + 45, brand_cy + 45),
                 outline=(160, 55, 55, 150), width=3)
    draw.ellipse((brand_cx - 30, brand_cy - 30, brand_cx + 30, brand_cy + 30),
                 outline=(160, 55, 55, 100), width=2)
    # Crosshair inside brand
    draw.line((brand_cx - 35, brand_cy, brand_cx + 35, brand_cy),
              fill=(160, 55, 55, 120), width=2)
    draw.line((brand_cx, brand_cy - 35, brand_cx, brand_cy + 35),
              fill=(160, 55, 55, 120), width=2)
    # Arc segments radiating from brand
    for ang_deg in range(0, 360, 15):
        if rng.random() < 0.4:
            rad_outer = rng.randint(55, 100)
            rad_inner = rng.randint(40, 50)
            a = math.radians(ang_deg)
            x1 = brand_cx + math.cos(a) * rad_inner
            y1 = brand_cy + math.sin(a) * rad_inner
            x2 = brand_cx + math.cos(a) * rad_outer
            y2 = brand_cy + math.sin(a) * rad_outer
            draw.line((x1, y1, x2, y2), fill=(160, 55, 55, rng.randint(60, 130)), width=2)

    # ── data-shard particles floating upward ─────────────────────────────────
    for _ in range(120):
        px = rng.randint(0, W)
        py = rng.randint(100, 1700)
        size = rng.randint(2, 6)
        shapes = ["rect", "diamond"]
        shape = rng.choice(shapes)
        alpha = rng.randint(30, 120)
        col = rng.choice([
            (100, 180, 200, alpha),
            (180, 100, 80, alpha),
            (150, 160, 180, alpha),
            (60, 120, 160, alpha),
        ])
        if shape == "rect":
            draw.rectangle((px, py, px + size, py + size), fill=col)
        else:
            # diamond
            draw.polygon([
                (px, py - size),
                (px + size, py),
                (px, py + size),
                (px - size, py),
            ], fill=col)

    # ── fine chrome wireframe grid (distant, low-opacity) ───────────────────
    for x in range(0, W, rng.randint(60, 100)):
        draw.line((x, 0, x, 1700),
                  fill=(100, 130, 180, rng.randint(5, 15)), width=1)
    for y in range(0, 1700, rng.randint(60, 100)):
        draw.line((0, y, W, y),
                  fill=(100, 130, 180, rng.randint(5, 15)), width=1)

    # ── subtle vignette ──────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(35 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ── title panel via shared utility ───────────────────────────────────────
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
