#!/usr/bin/env python3
"""Cover: The Garden of Broken Compasses — a map drawn in drought cracks, ink rivers bleeding into dry creek beds, ghost city emerging from parchment into the valley."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Palette: parched earth ochre/umber vs deep map ink indigo vs ghostly blueprint cyan
EARTH_DARK = (88, 60, 38)
EARTH_MID = (148, 108, 68)
EARTH_LIGHT = (198, 158, 108)
INK_BLUE = (28, 40, 92)
INK_LIGHT = (60, 80, 160)
GHOST_CYAN = (140, 190, 220)
DROUGHT_CRACK = (72, 46, 26)
MAP_BG = (215, 190, 150)
PARCHMENT = (230, 210, 172)

rng = random.Random()
rng.seed(890623441)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), EARTH_DARK + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Parched valley gradient ──────────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(EARTH_LIGHT[0] + (EARTH_DARK[0] - EARTH_LIGHT[0]) * t)
        g = int(EARTH_LIGHT[1] + (EARTH_DARK[1] - EARTH_LIGHT[1]) * t)
        b = int(EARTH_LIGHT[2] + (EARTH_DARK[2] - EARTH_LIGHT[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Sky glow (heat-haze pallor) ──────────────────────────────────────────
    sky_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sky_glow)
    sd.ellipse((100, -200, W - 100, 600), fill=(240, 220, 180, 20))
    sky_glow = sky_glow.filter(ImageFilter.GaussianBlur(80))
    img = Image.alpha_composite(img, sky_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Cracked earth texture (drought polygons) ────────────────────────────
    crack_polys = []
    polys_per_row = rng.randint(10, 16)
    for row in range(rng.randint(6, 10)):
        y_base = 1300 + row * 100 + rng.randint(-20, 20)
        for i in range(polys_per_row):
            cx = (i / polys_per_row) * W + rng.randint(-20, 20)
            cy = y_base + rng.randint(-30, 30)
            n_sides = rng.randint(4, 7)
            radius = rng.randint(25, 55)
            pts = []
            for a_idx in range(n_sides):
                ang = a_idx / n_sides * math.tau + rng.uniform(-0.15, 0.15)
                rr = radius * rng.uniform(0.7, 1.3)
                pts.append((cx + math.cos(ang) * rr, cy + math.sin(ang) * rr))
            crack_polys.append(pts)

    crack_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(crack_layer)
    for pts in crack_polys:
        cd.polygon(pts,
                   fill=(rng.randint(60, 90), rng.randint(40, 60), rng.randint(20, 35), rng.randint(100, 180)),
                   outline=(rng.randint(30, 55), rng.randint(18, 35), rng.randint(8, 20), 200),
                   width=rng.randint(1, 2))
    img = Image.alpha_composite(img, crack_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── The Map (tilted central parchment slab) ──────────────────────────────
    map_mask = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(map_mask)
    map_cx, map_cy = W // 2, 900
    map_w, map_h = 1200, 700
    # Slightly skewed trapezoid for perspective
    skew = rng.randint(30, 70)
    map_pts = [
        (map_cx - map_w // 2 + skew, map_cy - map_h // 2),
        (map_cx + map_w // 2 - skew, map_cy - map_h // 2 - 20),
        (map_cx + map_w // 2 + skew, map_cy + map_h // 2 + 10),
        (map_cx - map_w // 2 - skew + 20, map_cy + map_h // 2),
    ]
    md.polygon(map_pts, fill=PARCHMENT + (230,))
    md.polygon(map_pts, outline=(180, 160, 120, 200), width=4)
    # Parchment texture
    for _ in range(200):
        tx = rng.randint(map_cx - map_w // 2 + 30, map_cx + map_w // 2 - 30)
        ty = rng.randint(map_cy - map_h // 2 + 30, map_cy + map_h // 2 - 30)
        tv = rng.randint(10, 30)
        md.ellipse((tx - 2, ty - 2, tx + 2, ty + 2), fill=(200 + tv, 180 + tv, 140 + tv, rng.randint(40, 100)))
    img = Image.alpha_composite(img, map_mask)
    draw = ImageDraw.Draw(img, "RGBA")

    # Clip coordinates
    map_left = map_cx - map_w // 2
    map_right = map_cx + map_w // 2
    map_top = map_cy - map_h // 2
    map_bot = map_cy + map_h // 2

    # ── Map ink lines: contours, rivers, boundaries ──────────────────────────
    # Contour lines
    for _ in range(rng.randint(12, 20)):
        pts = []
        sx = rng.randint(map_left + 30, map_right - 30)
        sy = rng.randint(map_top + 30, map_bot - 30)
        for step in range(rng.randint(8, 18)):
            sx += rng.randint(-40, 40)
            sy += rng.randint(-20, 50)
            sx = max(map_left + 20, min(map_right - 20, sx))
            sy = max(map_top + 20, min(map_bot - 20, sy))
            pts.append((sx, sy))
        if len(pts) >= 2:
            draw.line(pts, fill=(*INK_BLUE, rng.randint(100, 160)), width=rng.randint(1, 3))

    # A map river starting on parchment and flowing OFF the map downward
    river_pts = []
    rx = rng.randint(map_left + 100, map_right - 100)
    ry = rng.randint(map_top + 50, map_top + 150)
    for step in range(rng.randint(20, 30)):
        rx += rng.randint(-15, 15)
        ry += rng.randint(18, 35)
        rx = max(50, min(W - 50, rx))
        river_pts.append((rx, ry))
    # Draw the river: thin on the map, thicker below
    for i, (rx, ry) in enumerate(river_pts):
        thickness = 2 + int((ry - river_pts[0][1]) / 25)
        alpha = min(220, 120 + int((ry - river_pts[0][1]) / 8))
        draw.line((rx, ry, rx + 1, ry + 1), fill=(*INK_LIGHT, alpha), width=thickness)
    # River glow
    for i in range(0, len(river_pts) - 1, 3):
        rx, ry = river_pts[i]
        draw.ellipse((rx - 12, ry - 8, rx + 12, ry + 8), fill=(100, 140, 200, 15))

    # ── Ink rivers bleeding into the drought valley (below the map) ──────────
    for _ in range(rng.randint(5, 8)):
        start_x = rng.randint(150, W - 150)
        start_y = rng.randint(1200, 1350)
        blood_pts = [(start_x, start_y)]
        for step in range(rng.randint(10, 18)):
            start_x += rng.randint(-25, 25)
            start_y += rng.randint(20, 50)
            blood_pts.append((start_x, min(H - 100, start_y)))
        if len(blood_pts) >= 2:
            draw.line(blood_pts, fill=(*INK_LIGHT, rng.randint(150, 220)), width=rng.randint(3, 8))
            # Blue glow around each river
            for bx, by in blood_pts:
                draw.ellipse((bx - 10, by - 6, bx + 10, by + 6), fill=(60, 100, 180, 12))

    # ── Ghost city emerging in the sky ──────────────────────────────────────
    ghost = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ghost)

    for _ in range(rng.randint(12, 20)):
        gx = rng.randint(100, W - 100)
        gy = rng.randint(200, 750)
        gh = rng.randint(120, 300)
        gw = rng.randint(40, 120)
        alpha = rng.randint(30, 80)
        # Building silhouette
        gd.rectangle((gx - gw // 2, gy, gx + gw // 2, gy + gh), fill=(*GHOST_CYAN, alpha))
        # Spire or dome
        if rng.random() < 0.4:
            gd.polygon([(gx - gw // 3, gy), (gx + gw // 3, gy), (gx, gy - rng.randint(40, 90))],
                       fill=(*GHOST_CYAN, alpha))
        # Blueprint grid lines on ghost buildings
        for ly in range(gy + 20, gy + gh - 10, rng.randint(18, 35)):
            gd.line((gx - gw // 2 + 4, ly, gx + gw // 2 - 4, ly),
                    fill=(*GHOST_CYAN, alpha // 3), width=1)

    # Ghost streets: faint grid lines descending from ghost city toward map
    for _ in range(rng.randint(6, 10)):
        sx = rng.randint(100, W - 100)
        sy = rng.randint(500, 750)
        pts = [(sx, sy)]
        for step in range(rng.randint(6, 12)):
            sx += rng.randint(-12, 12)
            sy += rng.randint(40, 70)
            pts.append((sx, sy))
        if len(pts) >= 2:
            gd.line(pts, fill=(*GHOST_CYAN, rng.randint(15, 35)), width=rng.randint(1, 2))

    ghost = ghost.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, ghost)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Compass rose (broken) ───────────────────────────────────────────────
    compass_cx = map_cx + 380
    compass_cy = map_cy - 180
    # Outer ring
    draw.ellipse((compass_cx - 60, compass_cy - 60, compass_cx + 60, compass_cy + 60),
                 outline=(*INK_BLUE, 150), width=3)
    # Cardinal points
    for angle_deg, label in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
        rad = math.radians(angle_deg)
        tip = (compass_cx + math.cos(rad) * 55, compass_cy + math.sin(rad) * 55)
        base1 = (compass_cx + math.cos(rad + 0.4) * 25, compass_cy + math.sin(rad + 0.4) * 25)
        base2 = (compass_cx + math.cos(rad - 0.4) * 25, compass_cy + math.sin(rad - 0.4) * 25)
        draw.polygon([tip, base1, base2], fill=(*INK_BLUE, rng.randint(120, 180)))
    # Broken: a crack through the compass
    draw.line((compass_cx - 40, compass_cy - 40, compass_cx + 20, compass_cy + 30),
              fill=(200, 180, 140, 200), width=4)
    draw.line((compass_cx + 20, compass_cy + 30, compass_cx + 45, compass_cy + 50),
              fill=(200, 180, 140, 200), width=3)
    # One needle detached
    rad_detach = math.radians(135)
    detached_tip = (compass_cx + math.cos(rad_detach) * 65, compass_cy + math.sin(rad_detach) * 65)
    detached_base = (compass_cx + math.cos(rad_detach - 0.3) * 30, compass_cy + math.sin(rad_detach - 0.3) * 30)
    draw.polygon([detached_tip, detached_base,
                  (compass_cx + math.cos(rad_detach + 0.3) * 30, compass_cy + math.sin(rad_detach + 0.3) * 30)],
                 fill=(*INK_LIGHT, 100))

    # ── Ink blotches / spatters near the map ────────────────────────────────
    for _ in range(rng.randint(15, 30)):
        sx = rng.randint(50, W - 50)
        sy = rng.randint(700, 1400)
        sr = rng.randint(2, 10)
        sa = rng.randint(30, 90)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                     fill=(*INK_BLUE, sa))
    # Larger ink pools
    for _ in range(rng.randint(4, 8)):
        sx = rng.randint(100, W - 100)
        sy = rng.randint(800, 1300)
        sr = rng.randint(15, 35)
        sa = rng.randint(10, 25)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                     fill=(*INK_LIGHT, sa))

    # ── Dry riverbeds in the drought valley ─────────────────────────────────
    for _ in range(rng.randint(6, 10)):
        start_x = rng.randint(100, W - 100)
        start_y = rng.randint(1300, 1500)
        bed_pts = [(start_x, start_y)]
        for step in range(rng.randint(10, 16)):
            start_x += rng.randint(-30, 30)
            start_y += rng.randint(25, 50)
            bed_pts.append((start_x, min(H - 100, start_y)))
        if len(bed_pts) >= 2:
            draw.line(bed_pts, fill=(*DROUGHT_CRACK, rng.randint(120, 200)), width=rng.randint(5, 12))

    # ── Dust motes / heat haze particles ─────────────────────────────────────
    for _ in range(rng.randint(40, 80)):
        px = rng.randint(0, W)
        py = rng.randint(0, H)
        pr = rng.randint(1, 3)
        pa = rng.randint(10, 40)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr),
                     fill=(200, 180, 140, pa))

    # ── Title panel ──────────────────────────────────────────────────────────
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
