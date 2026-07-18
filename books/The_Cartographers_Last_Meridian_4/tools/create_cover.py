#!/usr/bin/env python3
"""Cover: The Cartographer's Last Meridian 4 — A disgraced cartographer maps impossible seas where longitude fractures, searching for his lost daughter."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Deep ocean night palette — no two Meridian covers share this scheme
# Top: star-chart navy. Bottom: storm-blackened indigo
CR = (10, 12, 40)    # zenith — deep space navy
CL = (5, 5, 18)      # nadir — near-black indigo

rng = random.Random()
rng.seed(2041916307)

USE_PALETTE = [
    (180, 160, 100, 200),   # aged parchment gold — for celestial markings
    (200, 100, 60, 180),    # rust-amber — for the lost island
    (120, 180, 220, 160),   # pale ice blue — for fractured longitude
    (80, 140, 200, 120),    # distant horizon blue
    (60, 180, 210, 140),    # phosphorescent teal — sea glow
]


def _add_stars(draw: ImageDraw, count: int, base_alpha: int = 160) -> None:
    """Scatter stars with varied sizes and twinkle intensities."""
    for _ in range(count):
        sx = rng.randint(10, W - 10)
        sy = rng.randint(10, H - 800)
        size = rng.choice([1, 1, 1, 2, 2, 3])
        alpha = rng.randint(base_alpha - 40, base_alpha)
        warm = rng.randint(0, 40)
        star_col = (200 + warm, 200 + warm, 220, alpha)
        draw.ellipse((sx - size, sy - size, sx + size, sy + size), fill=star_col)


def _draw_constellation(draw: ImageDraw, cx: int, cy: int, spokes: int, radius: int, col, alpha: int) -> None:
    """Draw a small constellation-like cluster radiating from a point."""
    for i in range(spokes):
        ang = (math.tau / spokes) * i + rng.uniform(-0.08, 0.08)
        dist = radius * (0.4 + rng.random() * 0.6)
        ex = cx + int(math.cos(ang) * dist)
        ey = cy + int(math.sin(ang) * dist)
        draw.line((cx, cy, ex, ey), fill=(*col[:3], alpha), width=1)
        dot_r = rng.randint(2, 4)
        draw.ellipse((ex - dot_r, ey - dot_r, ex + dot_r, ey + dot_r), fill=(*col[:3], alpha + 30))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), CR + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Deep night gradient ──────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(CR[0] + (CL[0] - CR[0]) * t)
        g = int(CR[1] + (CL[1] - CR[1]) * t)
        b = int(CR[2] + (CL[2] - CR[2]) * t)
        # Darken toward edges for a vignette feel
        vignette = 1.0 - 0.3 * abs(t - 0.5) * 2
        draw.line((0, y, W, y), fill=(int(r * vignette), int(g * vignette), int(b * vignette), 255))

    # ── Atmospheric haze band near horizon ───────────────────────────────
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for hx in range(0, W, 8):
        for hy in range(500, 1000, 4):
            dist = abs(hy - 750) / 250
            alpha = int(max(0, 1 - dist) * 25)
            if alpha > 0:
                hd.point((hx, hy), fill=(100, 140, 180, alpha))
    haze = haze.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── The celestial sphere: stars ──────────────────────────────────────
    _add_stars(draw, 320, 180)

    # ── Constellation clusters (celestial navigation motifs) ─────────────
    constel_centers = [
        (280, 220, 5, 80),   (450, 380, 6, 70),
        (1100, 180, 7, 90),  (1350, 350, 5, 75),
        (800, 300, 8, 65),   (200, 600, 4, 60),
        (1400, 650, 6, 70),  (600, 550, 5, 55),
        (1000, 520, 7, 80),
    ]
    for cx, cy, spokes, radius in constel_centers:
        pal = rng.choice(USE_PALETTE)
        _draw_constellation(draw, cx, cy, spokes, radius, pal, rng.randint(30, 70))

    # ── Celestial grid lines (astro-navigation arcs) ─────────────────────
    grid_col = (140, 170, 210, 30)
    for gi in range(3):
        y_base = 100 + gi * 200
        for wx in range(0, W, 20):
            wy = y_base + int(math.sin(wx * 0.003 + gi * 1.5) * 40)
            draw.point((wx, wy), fill=grid_col)
    # Vertical meridian-like arcs
    for gj in range(3):
        x_base = 200 + gj * 500
        for wy2 in range(100, 800, 10):
            wx2 = x_base + int(math.sin(wy2 * 0.004 + gj * 2.0) * 60)
            draw.point((wx2, wy2), fill=grid_col)

    # ── THE FRACTURED MERIDIAN — central thematic element ────────────────
    # A vertical golden line that "fractures" and becomes chaotic
    meridian_col = (180, 160, 100, 200)
    fracture_zone_y = 600  # where it starts breaking apart
    for my in range(50, 1400, 2):
        if my < fracture_zone_y:
            # Smooth golden line
            draw.line((W // 2, my, W // 2, my + 2), fill=meridian_col, width=3)
        else:
            # Fracturing — splits into offset segments
            offset = int(math.sin(my * 0.05) * (5 + (my - fracture_zone_y) * 0.03))
            offset2 = int(math.cos(my * 0.03 + 1.3) * (8 + (my - fracture_zone_y) * 0.02))
            draw.line((W // 2 + offset, my, W // 2 + offset2, my + 2), fill=meridian_col, width=2)
            # Glowing fracture sparks
            if rng.random() < 0.15:
                spark_col = (220, 200, 140, rng.randint(40, 100))
                draw.ellipse((W // 2 + offset - 3, my - 3, W // 2 + offset + 3, my + 3), fill=spark_col)

    # ── Glowing distant island (the lost daughter's isle) ────────────────
    island_x, island_y = W // 2 + 150, 680
    island_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    igd = ImageDraw.Draw(island_glow)
    igd.ellipse((island_x - 60, island_y - 20, island_x + 60, island_y + 30), fill=(200, 120, 60, 40))
    igd.ellipse((island_x - 30, island_y - 8, island_x + 30, island_y + 15), fill=(220, 160, 80, 60))
    igd.ellipse((island_x - 12, island_y - 3, island_x + 12, island_y + 6), fill=(240, 200, 120, 80))
    island_glow = island_glow.filter(ImageFilter.GaussianBlur(16))
    img = Image.alpha_composite(img, island_glow)
    draw = ImageDraw.Draw(img, "RGBA")
    # Island silhouette
    draw.ellipse((island_x - 45, island_y - 10, island_x + 45, island_y + 20), fill=(25, 18, 12, 220))
    # Peak
    draw.polygon([(island_x - 20, island_y - 6), (island_x, island_y - 35), (island_x + 20, island_y - 6)],
                 fill=(35, 25, 15, 220))
    # Tiny light on island (signal fire / beacon)
    beacon_r = 8
    beacon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beacon)
    bd.ellipse((island_x - beacon_r, island_y - beacon_r - 25, island_x + beacon_r, island_y + beacon_r - 25),
               fill=(255, 200, 100, 180))
    beacon = beacon.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, beacon)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Storm-tossed ship of the Magellan fleet ──────────────────────────
    ship_x, ship_y = W // 2 - 180, 1100
    # Hull
    draw.polygon([
        (ship_x - 90, ship_y + 30),
        (ship_x - 70, ship_y + 50),
        (ship_x + 70, ship_y + 50),
        (ship_x + 90, ship_y + 30),
    ], fill=(25, 22, 18, 230))
    # Deck line
    draw.line((ship_x - 85, ship_y + 32, ship_x + 85, ship_y + 32), fill=(45, 35, 25, 240), width=2)
    # Masts
    for mx_off in (-40, 0, 40):
        mx = ship_x + mx_off
        mast_h = 120 - abs(mx_off) // 2
        draw.line((mx, ship_y + 10, mx, ship_y - mast_h), fill=(40, 35, 30, 200), width=4)
    # Sails — billowing, tattered
    for sail_i, (sx_off, sh, sw, bulge) in enumerate([
        (-40, 60, 45, 12),   (0, 75, 55, 15),   (40, 60, 45, 12),
        (-40, 95, 40, 10),   (0, 115, 50, 14),  (40, 95, 40, 10),
    ]):
        sx = ship_x + sx_off
        sy = ship_y - sh
        # Sail as a slight curve
        sail_col = (55, 50, 42, 180)
        draw.polygon([
            (sx - sw // 2, sy),
            (sx + sw // 2, sy),
            (sx + sw // 2 + bulge, sy + sh // 2),
            (sx + sw // 2, sy + sh),
            (sx - sw // 2, sy + sh),
            (sx - sw // 2 + bulge, sy + sh // 2),
        ], fill=sail_col)
    # Flag
    draw.polygon([(ship_x + 42, ship_y - 125), (ship_x + 60, ship_y - 118), (ship_x + 42, ship_y - 111)],
                 fill=(160, 40, 30, 200))

    # ── Stormy sea / waves ───────────────────────────────────────────────
    for wi in range(8):
        amp = rng.randint(15, 45)
        freq = rng.uniform(0.005, 0.018)
        phase = rng.uniform(0, math.tau)
        y_base = ship_y + 50 + wi * 35 + rng.randint(-10, 10)
        pts = []
        for wxx in range(0, W + 4, 4):
            wyy = y_base + math.sin(wxx * freq + phase) * amp + math.sin(wxx * freq * 3 + phase * 1.4) * amp * 0.3
            pts.append((wxx, wyy))
        depth = (wi / 8)
        wave_color = (
            int(20 * (1 - depth) + 5 * depth),
            int(40 * (1 - depth) + 10 * depth),
            int(70 * (1 - depth) + 20 * depth),
        )
        draw.line(pts, fill=(*wave_color, rng.randint(60, 120)), width=rng.randint(3, 8))
        # Whitecaps
        if rng.random() < 0.3:
            crest_x = rng.randint(200, 1400)
            draw.ellipse((crest_x - 8, y_base - 5, crest_x + 8, y_base + 5),
                         fill=(150, 180, 200, rng.randint(20, 50)))

    # ── Phosphorescent sea glow beneath the surface ──────────────────────
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gld = ImageDraw.Draw(glow_layer)
    for _ in range(40):
        gx = rng.randint(0, W)
        gy = rng.randint(ship_y + 60, H - 300)
        gr = rng.randint(8, 30)
        gcol = rng.choice([(60, 180, 210, 12), (40, 140, 200, 10), (80, 160, 220, 8)])
        gld.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=gcol)
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Foreboding cloud bands across the top ────────────────────────────
    cloud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cld = ImageDraw.Draw(cloud_layer)
    for ci in range(12):
        cy_base = rng.randint(20, 400)
        cw = rng.randint(300, 800)
        cx = rng.randint(-200, W + 200 - cw)
        ch = rng.randint(30, 80)
        ca = rng.randint(10, 30)
        cld.ellipse((cx, cy_base, cx + cw, cy_base + ch), fill=(30, 25, 40, ca))
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, cloud_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Small compass rose in upper-right ─────────────────────────────────
    cr_cx, cr_cy = W - 120, 160
    cr_outer = 40
    for ang_deg in range(0, 360, 45):
        ang_rad = math.radians(ang_deg - 90)
        is_primary = ang_deg % 90 == 0
        length = cr_outer if is_primary else cr_outer * 0.6
        width_n = 3 if is_primary else 1
        ex = cr_cx + int(math.cos(ang_rad) * length)
        ey = cr_cy + int(math.sin(ang_rad) * length)
        draw.line((cr_cx, cr_cy, ex, ey), fill=(160, 140, 80, 100), width=width_n)
    # Compass circle
    draw.ellipse((cr_cx - cr_outer, cr_cy - cr_outer, cr_cx + cr_outer, cr_cy + cr_outer),
                 outline=(160, 140, 80, 60), width=1)
    draw.ellipse((cr_cx - 3, cr_cy - 3, cr_cx + 3, cr_cy + 3), fill=(180, 160, 100, 120))
    # Cardinal letters
    for label, lx_off, ly_off in [("N", 0, -50), ("S", 0, 50), ("E", 48, 6), ("W", -48, 6)]:
        draw.text((cr_cx + lx_off - 5, cr_cy + ly_off - 6), label, fill=(160, 140, 80, 80))

    # ── Draw the standard cream title/author panel ───────────────────────
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
