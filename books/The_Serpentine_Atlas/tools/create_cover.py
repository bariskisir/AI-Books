#!/usr/bin/env python3
"""Cover: The Serpentine Atlas — 1720s Constantinople spy drama: a mapmaker's daughter secretly completes her executed father's forbidden Ottoman survey, threading between Venetian spies and the Sultan's vizier. Features a panoramic twilight skyline of Constantinople overlaid with cartographic parchment, serpentine contour lines, compass rose, and the Golden Horn's glimmer."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# -- Unique palette: dusk over Constantinople + Ottoman gold + parchment --
# Deep twilight sky transitions from warm amber (sunset over the Golden Horn)
# through deep indigo (night over the Bosporus), with rich terracotta accents.
SKY_TOP = (28, 18, 48)       # deep indigo at top
SKY_MID = (120, 60, 55)     # warm terracotta at mid-sky
SKY_BOT = (195, 130, 75)    # amber-gold near horizon
SEA_COL = (25, 45, 65)      # dark Bosporus water
PARCHMENT = (210, 190, 155)  # aged map parchment
INK_DARK = (18, 14, 10)      # sepia ink
GOLD_ACCENT = (185, 145, 60) # Ottoman gold
WARM_LIGHT = (240, 200, 130) # lamp glow from a window


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), SKY_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # --- 1. DUSK SKY GRADIENT (indigo -> terracotta -> amber -> sea) ---
    horizon_y = 1000
    for y in range(H):
        if y < horizon_y:
            t = y / horizon_y
            if t < 0.5:
                u = t / 0.5
                r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * u)
                g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * u)
                b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * u)
            else:
                u = (t - 0.5) / 0.5
                r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * u)
                g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * u)
                b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * u)
            draw.line((0, y, W, y), fill=(r, g, b, 255))
        else:
            t = min(1.0, (y - horizon_y) / 300)
            r = int(SKY_BOT[0] + (SEA_COL[0] - SKY_BOT[0]) * t)
            g = int(SKY_BOT[1] + (SEA_COL[1] - SKY_BOT[1]) * t)
            b = int(SKY_BOT[2] + (SEA_COL[2] - SKY_BOT[2]) * t)
            draw.line((0, y, W, y), fill=(r, g, b, 255))

    # --- 2. CONSTANTINOPLE SKYLINE (domes, minarets, buildings) ---
    skyline = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(skyline)

    base_y = horizon_y + 20

    # Large central dome (Hagia Sophia inspired)
    dome_cx, dome_cy = W // 2, base_y
    sd.arc((dome_cx - 180, dome_cy - 140, dome_cx + 180, dome_cy + 40),
            0, 180, fill=INK_DARK + (220,), width=6)
    sd.arc((dome_cx - 120, dome_cy - 100, dome_cx + 120, dome_cy + 40),
            0, 180, fill=INK_DARK + (200,), width=4)
    sd.rectangle((dome_cx - 22, dome_cy + 20, dome_cx + 22, dome_cy + 80),
                  fill=INK_DARK + (220,))

    # Side semi-domes
    for side in [-1, 1]:
        sx = dome_cx + side * 150
        sd.arc((sx - 90, dome_cy - 70, sx + 90, dome_cy + 30),
                0, 180, fill=INK_DARK + (200,), width=4)
        sd.rectangle((sx - 10, dome_cy + 15, sx + 10, dome_cy + 60),
                      fill=INK_DARK + (200,))

    # Minarets (tall, thin)
    rng_skyline = random.Random(0)
    minaret_positions = [dome_cx - 300, dome_cx - 140,
                         dome_cx + 140, dome_cx + 300]
    for mx in minaret_positions:
        mh = 350 + rng_skyline.randint(-30, 30)
        sd.rectangle((mx - 5, dome_cy - mh, mx + 5, dome_cy + 60),
                      fill=INK_DARK + (200,))
        # Minaret balcony (sherefe)
        bal_y = dome_cy - mh + 60
        sd.rectangle((mx - 12, bal_y - 3, mx + 12, bal_y + 3),
                      fill=INK_DARK + (200,))
        # Cone top
        sd.polygon([(mx - 7, dome_cy - mh),
                     (mx + 7, dome_cy - mh),
                     (mx, dome_cy - mh - 30)],
                    fill=INK_DARK + (200,))

    # Secondary domes (smaller mosques)
    for offset in [-420, 420]:
        sdx = dome_cx + offset + rng_skyline.randint(-30, 30)
        sd.arc((sdx - 70, dome_cy - 60, sdx + 70, dome_cy + 20),
                0, 180, fill=INK_DARK + (180,), width=3)
        sd.rectangle((sdx - 8, dome_cy + 10, sdx + 8, dome_cy + 45),
                      fill=INK_DARK + (180,))
        sd.rectangle((sdx - 3, dome_cy - 150, sdx + 3, dome_cy + 30),
                      fill=INK_DARK + (150,))

    # City buildings along the shoreline
    for bx in range(0, W, rng_skyline.randint(18, 40)):
        bw = rng_skyline.randint(14, 35)
        bh = rng_skyline.randint(30, 90)
        bcol = rng_skyline.choice([INK_DARK, (25, 20, 18), (35, 28, 22)])
        sd.rectangle((bx, base_y + 60 - bh, bx + bw, base_y + 80),
                      fill=bcol + (180,))

    skyline = skyline.filter(ImageFilter.SMOOTH)
    img = Image.alpha_composite(img, skyline)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- 3. GOLDEN HORN (water with reflections) ---
    water = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(water)
    for wx in range(0, W, 4):
        wave_y = base_y + 80 + math.sin(wx * 0.02) * 6 + math.sin(wx * 0.07) * 3
        wd.line((wx, wave_y, wx, base_y + 180), fill=(60, 80, 100, 60))

    for _ in range(40):
        rx = random.randint(100, W - 100)
        ry = base_y + 100 + random.randint(0, 120)
        rl = random.randint(8, 30)
        ralpha = random.randint(15, 50)
        wd.ellipse((rx - rl, ry - 2, rx + rl, ry + 2),
                    fill=(220, 190, 130, ralpha))

    img = Image.alpha_composite(img, water)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- 4. PARCHMENT MAP OVERLAY (semi-transparent cartographic sheet) ---
    map_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(map_layer)

    map_margin_x = 100
    map_top = 300
    map_bot = 1500

    for row_y in range(map_top, map_bot, 2):
        edge_jitter = int(math.sin(row_y * 0.03) * 8 + random.randint(-2, 2))
        left = map_margin_x + edge_jitter
        right = W - map_margin_x + edge_jitter
        shade_var = int(math.sin(row_y * 0.015) * 10)
        pr = max(0, min(255, PARCHMENT[0] + shade_var))
        pg = max(0, min(255, PARCHMENT[1] + shade_var))
        pb = max(0, min(255, PARCHMENT[2] + shade_var))
        alpha = 70 + int(20 * math.sin(row_y * 0.02))
        md.line((left, row_y, right, row_y), fill=(pr, pg, pb, alpha))

    # --- 5. CARTOGRAPHIC DETAILS (contour lines, grid, compass rose) ---
    rng = random.Random(42)

    # Topographic contour lines
    for cx_offset in range(-100, W + 100, 80 + rng.randint(-20, 20)):
        pts = []
        for cy in range(map_top + 40, map_bot - 40, 4):
            wave = (math.sin(cy * 0.008 + cx_offset * 0.01) * 50
                    + math.sin(cy * 0.02 + cx_offset * 0.03) * 20
                    + math.cos(cy * 0.005 + cx_offset * 0.015) * 30)
            x = cx_offset + wave
            pts.append((x, cy))
        if len(pts) > 2:
            for i in range(len(pts) - 1):
                if (map_margin_x + 20 < pts[i][0] < W - map_margin_x - 20
                        and map_margin_x + 20 < pts[i + 1][0] < W - map_margin_x - 20):
                    md.line((pts[i], pts[i + 1]),
                            fill=(60, 45, 30, rng.randint(30, 60)), width=1)

    # Serpentine river/road path
    serpentine = []
    for sy in range(map_top + 30, map_bot - 30, 3):
        sx = (W // 2 + math.sin(sy * 0.012) * 200
              + math.sin(sy * 0.025) * 80 + math.cos(sy * 0.007) * 100)
        serpentine.append((sx, sy))
    for i in range(len(serpentine) - 1):
        alpha = int(120 + 60 * math.sin(i * 0.05))
        md.line((serpentine[i], serpentine[i + 1]),
                fill=GOLD_ACCENT + (alpha,), width=3)

    # Spy route markers along the serpentine
    for i in range(0, len(serpentine) - 1, 25):
        if rng.random() < 0.6:
            px, py = serpentine[i]
            md.ellipse((px - 4, py - 4, px + 4, py + 4),
                       fill=(180, 50, 50, 120))

    # Compass Rose
    cr_x, cr_y = 250, 450
    cr_size = 55
    md.ellipse((cr_x - cr_size - 5, cr_y - cr_size - 5,
                cr_x + cr_size + 5, cr_y + cr_size + 5),
               outline=GOLD_ACCENT + (150,), width=2)
    for i, angle in enumerate([0, 90, 180, 270]):
        rad = math.radians(angle)
        tip = (cr_x + math.cos(rad) * cr_size,
               cr_y + math.sin(rad) * cr_size)
        left = (cr_x + math.cos(rad + 2.6) * cr_size * 0.45,
                cr_y + math.sin(rad + 2.6) * cr_size * 0.45)
        right = (cr_x + math.cos(rad - 2.6) * cr_size * 0.45,
                 cr_y + math.sin(rad - 2.6) * cr_size * 0.45)
        if i < 2:
            md.polygon([tip, left, right], fill=INK_DARK + (180,))
        else:
            md.polygon([tip, left, right], fill=(120, 110, 90, 160))
    md.ellipse((cr_x - 5, cr_y - 5, cr_x + 5, cr_y + 5),
               fill=GOLD_ACCENT + (200,))

    # Map grid lines
    for gx in range(map_margin_x + 30, W - map_margin_x - 30, 60):
        md.line((gx, map_top + 20, gx, map_bot - 20),
                fill=(100, 85, 55, 20), width=1)
    for gy in range(map_top + 30, map_bot - 20, 60):
        md.line((map_margin_x + 20, gy, W - map_margin_x - 20, gy),
                fill=(100, 85, 55, 20), width=1)

    # City markers on the map
    markers = [
        (550, 550), (850, 700), (1050, 580), (700, 900),
        (1100, 850), (500, 1050), (900, 1100), (1200, 1000),
        (600, 700), (480, 800),
    ]
    for mx, my in markers:
        if (map_margin_x + 30 < mx < W - map_margin_x - 30
                and map_top + 30 < my < map_bot - 30):
            md.ellipse((mx - 4, my - 4, mx + 4, my + 4),
                       fill=(140, 40, 40, 180))
            md.ellipse((mx - 6, my - 6, mx + 6, my + 6),
                       outline=GOLD_ACCENT + (100,), width=1)

    # Parchment edge burn
    for wear_y in range(map_top, map_bot, 6):
        edge_t = (wear_y - map_top) / (map_bot - map_top)
        burn = int(40 * (1 - abs(edge_t - 0.5) * 2))
        if burn > 5:
            jitter_l = int(math.sin(wear_y * 0.05) * 5)
            md.line((map_margin_x - 10 + jitter_l, wear_y,
                     map_margin_x + jitter_l, wear_y),
                    fill=(40, 25, 15, min(200, burn + 50)))
            jitter_r = int(math.sin(wear_y * 0.05 + 3) * 5)
            md.line((W - map_margin_x + jitter_r, wear_y,
                     W - map_margin_x + 10 + jitter_r, wear_y),
                    fill=(40, 25, 15, min(200, burn + 50)))

    map_layer = map_layer.filter(ImageFilter.SMOOTH)
    img = Image.alpha_composite(img, map_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # --- 6. WARM LAMP GLOW (Leyla's secret workspace window) ---
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    win_cx, win_cy = 360, 850
    win_w, win_h = 70, 90
    gd.rectangle((win_cx - win_w // 2, win_cy - win_h // 2,
                  win_cx + win_w // 2, win_cy + win_h // 2),
                 fill=WARM_LIGHT + (180,))
    gd.line((win_cx, win_cy - win_h // 2, win_cx, win_cy + win_h // 2),
            fill=INK_DARK + (200,), width=3)
    gd.line((win_cx - win_w // 2, win_cy, win_cx + win_w // 2, win_cy),
            fill=INK_DARK + (200,), width=3)

    for r in range(1, 8):
        rad = r * 25
        alpha = max(0, 160 - r * 20)
        gd.ellipse((win_cx - rad, win_cy - rad,
                    win_cx + rad, win_cy + rad),
                   fill=WARM_LIGHT + (alpha,))

    glow = glow.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, glow)

    # Re-draw sharp window on top
    draw = ImageDraw.Draw(img, "RGBA")
    draw.rectangle((win_cx - win_w // 2, win_cy - win_h // 2,
                    win_cx + win_w // 2, win_cy + win_h // 2),
                   fill=WARM_LIGHT + (220,))
    draw.line((win_cx, win_cy - win_h // 2, win_cx, win_cy + win_h // 2),
              fill=INK_DARK + (220,), width=3)
    draw.line((win_cx - win_w // 2, win_cy, win_cx + win_w // 2, win_cy),
              fill=INK_DARK + (220,), width=3)

    # --- 7. STARS AND CRESCENT MOON ---
    star_rng = random.Random(17)
    for _ in range(120):
        sx = star_rng.randint(0, W)
        sy = star_rng.randint(0, horizon_y - 100)
        sr = star_rng.randint(1, 3)
        s_alpha = star_rng.randint(30, 150)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                     fill=(255, 240, 200, s_alpha))

    # Crescent moon
    moon_cx, moon_cy = W - 180, 160
    for r in range(20, 0, -1):
        alpha = 100 - r * 4
        draw.ellipse((moon_cx - r, moon_cy - r, moon_cx + r, moon_cy + r),
                     fill=(240, 225, 190, alpha))
    draw.ellipse((moon_cx + 6, moon_cy - 16, moon_cx + 24, moon_cy + 16),
                 fill=SKY_TOP + (200,))

    # --- 8. ATMOSPHERIC HAZE ---
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse((-200, horizon_y - 100, W + 200, horizon_y + 200),
               fill=(220, 170, 100, 20))
    img = Image.alpha_composite(img, haze)
    img = img.filter(ImageFilter.SMOOTH)

    # --- 9. TITLE PANEL ---
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)
    print(f"Cover saved to {op}")


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
