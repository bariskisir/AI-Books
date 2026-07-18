#!/usr/bin/env python3
"""Cover: The Clockwork Covenant — A disgraced toymaker in a clockpunk city must build a device to rewind time before a celestial alignment cracks the realm apart. Giant celestial orrery, cracked reality, brass gear-scattered skyline, golden magic threads, time-particle constellation."""

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
rng.seed(1883719335)

# Unique palette: midnight brass and celestial gold — clockpunk fantasy
CR = (10, 8, 40)      # deep celestial navy at top
CL = (65, 50, 30)     # warm bronze at bottom (city glow)
GOLD = (220, 175, 50)
BRASS = (180, 140, 40)
COPPER = (160, 80, 40)
RIFT_COL = (200, 40, 180)


def _gear_teeth(draw, cx, cy, inner_r, outer_r, num_teeth, fill, outline=None, width=1):
    """Draw a gear ring with teeth around it."""
    # Main ring
    draw.ellipse((cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r),
                 outline=fill, width=width + 1)
    draw.ellipse((cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r),
                 outline=fill, width=width)
    # Teeth
    for i in range(num_teeth):
        angle = math.tau * i / num_teeth
        mid_a = angle
        mid_ax = cx + math.cos(mid_a) * (inner_r + (outer_r - inner_r) * 0.5)
        mid_ay = cy + math.sin(mid_a) * (inner_r + (outer_r - inner_r) * 0.5)
        t_inner = cx + math.cos(mid_a) * outer_r
        t_outer = cx + math.cos(mid_a) * (outer_r + 12)
        t_inner_y = cy + math.sin(mid_a) * outer_r
        t_outer_y = cy + math.sin(mid_a) * (outer_r + 12)
        # Tooth as short line
        draw.line((t_inner, t_inner_y, t_outer, t_outer_y), fill=fill, width=width + 2)
    # Inner hub
    hub_r = inner_r // 3
    draw.ellipse((cx - hub_r, cy - hub_r, cx + hub_r, cy + hub_r),
                 outline=fill, width=width + 1)
    # Spokes
    for i in range(4):
        a = math.tau * i / 4
        sx = cx + math.cos(a) * hub_r
        sy = cy + math.sin(a) * hub_r
        ex = cx + math.cos(a) * inner_r
        ey = cy + math.sin(a) * inner_r
        draw.line((sx, sy, ex, ey), fill=fill, width=width)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Base canvas ──────────────────────────────────────────────────────────
    img = Image.new("RGBA", (W, H), (10, 8, 40, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Vertical gradient: deep celestial navy → warm bronze ─────────────────
    for y in range(H):
        t = y / H
        r = int(CR[0] + (CL[0] - CR[0]) * t)
        g = int(CR[1] + (CL[1] - CR[1]) * t)
        b = int(CR[2] + (CL[2] - CR[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Background starfield (dim, scattered) ────────────────────────────────
    for _ in range(180):
        sx = rng.randint(0, W)
        sy = rng.randint(0, 1400)
        sr = rng.uniform(0.5, 2.0)
        sa = rng.randint(20, 90)
        draw.ellipse((int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr)),
                     fill=(200, 210, 230, sa))

    # ── Celestial Rift — a jagged crack in reality across the upper sky ──────
    rift_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rift_layer)

    rift_y_center = 300
    rift_pts = []
    rx = -50
    while rx < W + 50:
        ry = rift_y_center + rng.randint(-120, 120) + 20 * math.sin(rx / 80)
        rift_pts.append((rx, ry))
        rx += rng.randint(20, 50)

    # Glowing rift core
    for thickness in range(8, 2, -1):
        alpha = 40 + thickness * 15
        col = (
            min(255, RIFT_COL[0] + thickness * 10),
            min(255, 40 + (8 - thickness) * 20),
            min(255, RIFT_COL[2] - thickness * 15),
        )
        rd.line(rift_pts, fill=(*col, alpha), width=thickness * 2 + 6)

    # Outer glow on rift
    rd.line(rift_pts, fill=(RIFT_COL[0], 80, RIFT_COL[2], 30), width=40)
    rd.line(rift_pts, fill=(120, 60, 200, 20), width=70)

    # Energy tendrils from the rift
    for _ in range(16):
        seg_start = rng.choice(rift_pts)
        tendril = [seg_start]
        tx, ty = seg_start
        for _ in range(rng.randint(3, 6)):
            tx += rng.randint(-30, 30)
            ty += rng.randint(20, 60)
            tendril.append((tx, ty))
        ep = (rng.randint(180, 240), rng.randint(40, 80), rng.randint(180, 220))
        rd.line(tendril, fill=(*ep, rng.randint(50, 120)), width=rng.randint(2, 5))

    rift_layer = rift_layer.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, rift_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Giant Celestial Orrery / Clockwork Mechanism ─────────────────────────
    # A massive compound gear structure in the upper-mid sky
    orrery_cx, orrery_cy = W // 2, 550

    # Glow behind the orrery
    orrery_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ogd = ImageDraw.Draw(orrery_glow)
    for rad in [300, 200, 100]:
        ogd.ellipse((orrery_cx - rad, orrery_cy - rad, orrery_cx + rad, orrery_cy + rad),
                    fill=(GOLD[0], GOLD[1], GOLD[2], max(3, 18 - rad // 20)))
    orrery_glow = orrery_glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, orrery_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Outer gear ring 1 (largest)
    _gear_teeth(draw, orrery_cx, orrery_cy, 180, 210, 24,
                 fill=BRASS + (160,), width=3)
    # Gear ring 2 (medium, rotated offset)
    _gear_teeth(draw, orrery_cx + 40, orrery_cy + 30, 130, 155, 18,
                 fill=GOLD + (140,), width=2)
    # Gear ring 3 (small, inner)
    _gear_teeth(draw, orrery_cx - 30, orrery_cy - 40, 85, 105, 12,
                 fill=COPPER + (150,), width=2)
    # Small orbiting gears
    for orbit_idx in range(5):
        oa = math.tau * orbit_idx / 5 + 0.3
        ox = orrery_cx + math.cos(oa) * 250
        oy = orrery_cy + math.sin(oa) * 200
        _gear_teeth(draw, ox, oy, 25, 35, 8,
                     fill=GOLD + (120,), width=2)

    # Orrery arms (connecting rings)
    for arm_idx in range(3):
        aa = math.tau * arm_idx / 3
        inner_x = orrery_cx + math.cos(aa) * 40
        inner_y = orrery_cy + math.sin(aa) * 40
        outer_x = orrery_cx + math.cos(aa) * 190
        outer_y = orrery_cy + math.sin(aa) * 190
        draw.line((inner_x, inner_y, outer_x, outer_y),
                  fill=BRASS + (100,), width=3)

    # ── Roman numeral fragments floating near the orrery ─────────────────────
    numerals_coords = [
        (orrery_cx - 280, orrery_cy - 180), (orrery_cx + 200, orrery_cy - 150),
        (orrery_cx + 300, orrery_cy), (orrery_cx - 200, orrery_cy + 150),
        (orrery_cx + 150, orrery_cy + 200), (orrery_cx - 300, orrery_cy + 50),
    ]
    numerals = ["I", "V", "X", "L", "C", "M"]
    for (nx, ny), num in zip(numerals_coords, numerals):
        for char_offset, char in enumerate(num):
            draw.text((nx + char_offset * 18, ny), char,
                      fill=GOLD + (rng.randint(80, 140),))

    # ── Clock hands sweeping across the sky ──────────────────────────────────
    hand_center = (orrery_cx + 20, orrery_cy - 10)
    for hand_angle, hand_len, hand_col in [
        (0.8, 260, GOLD + (100,)),
        (2.2, 200, BRASS + (80,)),
        (4.5, 180, COPPER + (90,)),
    ]:
        hx = hand_center[0] + math.cos(hand_angle) * hand_len
        hy = hand_center[1] + math.sin(hand_angle) * hand_len
        draw.line((hand_center[0], hand_center[1], hx, hy),
                  fill=hand_col, width=4)

    # ── Golden magic threads (clockwork-powered magic weaving through gears) ─
    for _ in range(25):
        start_x = rng.randint(0, W)
        start_y = rng.randint(300, 1100)
        thread_pts = [(start_x, start_y)]
        cx, cy = start_x, start_y
        for _ in range(rng.randint(4, 10)):
            cx += rng.randint(-60, 60)
            cy += rng.randint(20, 50)
            thread_pts.append((cx, cy))
        thread_alpha = rng.randint(40, 130)
        thread_width = rng.randint(1, 3)
        draw.line(thread_pts, fill=GOLD + (thread_alpha,), width=thread_width)

    # ── City skyline: clockwork spires, towers, visible gear mechanisms ──────
    city_base_y = 1550
    num_towers = rng.randint(14, 20)
    towers = sorted([rng.randint(60, W - 60) for _ in range(num_towers)])

    for tx in towers:
        tw = rng.randint(30, 90)
        th = rng.randint(200, 550)

        # Tower body
        tcol = (rng.randint(10, 25), rng.randint(8, 18), rng.randint(10, 20))
        draw.rectangle((tx - tw // 2, city_base_y - th, tx + tw // 2, city_base_y),
                       fill=(*tcol, 230))

        # Spire or clock tower top
        if rng.random() < 0.4:
            spire_h = rng.randint(30, 80)
            draw.polygon([
                (tx - 8, city_base_y - th),
                (tx + 8, city_base_y - th),
                (tx, city_base_y - th - spire_h),
            ], fill=(*tcol, 230))

        # Exposed gear mechanism on the tower (clockwork aesthetic)
        if rng.random() < 0.5:
            gear_y = city_base_y - th + rng.randint(15, th - 40)
            gear_r = rng.randint(8, 18)
            gcol = BRASS + (rng.randint(120, 180),)
            _gear_teeth(draw, tx, gear_y, gear_r - 4, gear_r, 6,
                         fill=gcol, width=1)

        # Tiny glowing windows
        for wy in range(city_base_y - th + 10, city_base_y - 10, rng.randint(20, 40)):
            for wx in range(tx - tw // 2 + 4, tx + tw // 2 - 4, rng.randint(12, 25)):
                if rng.random() < 0.35:
                    wcol = (255, 220, 140) if rng.random() < 0.6 else (GOLD[0], GOLD[1], GOLD[2])
                    draw.rectangle((wx, wy, wx + 5, wy + 5), fill=(*wcol, rng.randint(80, 180)))

        # Smoke/steam plume from some towers
        if rng.random() < 0.3:
            plume_pts = [(tx, city_base_y - th)]
            px, py = tx, city_base_y - th
            for _ in range(rng.randint(3, 5)):
                px += rng.randint(-15, 15)
                py -= rng.randint(10, 25)
                plume_pts.append((px, py))
            draw.line(plume_pts, fill=(100, 95, 85, rng.randint(20, 50)), width=rng.randint(3, 6))

    # ── The Grand Escapement — a monumental clock tower (centerpiece) ────────
    escapement_x = W // 2
    escapement_w = 120
    escapement_h = 650
    ec_y = city_base_y - escapement_h
    draw.rectangle((escapement_x - escapement_w // 2, ec_y,
                    escapement_x + escapement_w // 2, city_base_y),
                   fill=(12, 10, 8, 240))
    # Escapement peak
    draw.polygon([
        (escapement_x - 40, ec_y),
        (escapement_x + 40, ec_y),
        (escapement_x, ec_y - 50),
    ], fill=(12, 10, 8, 240))
    # Escapement face (large gear)
    _gear_teeth(draw, escapement_x, ec_y + 100, 30, 40, 8,
                 fill=GOLD + (200,), width=3)
    # Pendulum
    draw.line((escapement_x, ec_y + 140, escapement_x, ec_y + 280),
              fill=GOLD + (180,), width=3)
    draw.ellipse((escapement_x - 15, ec_y + 280, escapement_x + 15, ec_y + 310),
                 fill=GOLD + (200,))

    # ── Silhouette of Theo Brasswick on the escapement tower ─────────────────
    fig_x = escapement_x + 50
    fig_y = ec_y + 100
    # Body
    draw.line((fig_x, fig_y + 30, fig_x, fig_y + 60), fill=(5, 5, 5, 200), width=4)
    # Head
    draw.ellipse((fig_x - 6, fig_y + 20, fig_x + 6, fig_y + 32), fill=(5, 5, 5, 200))
    # Arms raised (looking up at the sky)
    draw.line((fig_x, fig_y + 35, fig_x - 15, fig_y + 20), fill=(5, 5, 5, 200), width=3)
    draw.line((fig_x, fig_y + 35, fig_x + 15, fig_y + 20), fill=(5, 5, 5, 200), width=3)
    # Tool (a wrench/staff) in right hand
    draw.line((fig_x + 15, fig_y + 20, fig_x + 30, fig_y - 10), fill=(80, 70, 50, 200), width=2)

    # ── Gear particles / time fragments floating upward ──────────────────────
    for _ in range(80):
        px = rng.randint(0, W)
        py = rng.randint(200, 1500)
        size = rng.randint(2, 5)
        alpha = rng.randint(30, 100)
        choices = [
            GOLD + (alpha,),
            BRASS + (alpha,),
            (180, 220, 255, alpha),
            (255, 200, 100, alpha),
        ]
        col = rng.choice(choices)
        if rng.random() < 0.5:
            # Gear tooth shape (tiny L)
            draw.line((px, py, px + size, py), fill=col, width=1)
            draw.line((px + size, py, px + size, py + size), fill=col, width=1)
        else:
            # Dot
            draw.ellipse((px, py, px + size, py + size), fill=col)

    # ── Constellation lines connecting stars (suggesting the celestial alignment) ──
    stars = [(rng.randint(100, W - 100), rng.randint(50, 400)) for _ in range(30)]
    for i, (sx, sy) in enumerate(stars):
        for j in range(i + 1, len(stars)):
            dx = stars[j][0] - sx
            dy = stars[j][1] - sy
            dist = math.sqrt(dx * dx + dy * dy)
            if dist < 150 and rng.random() < 0.3:
                alpha = int(max(0, 25 - dist // 10))
                draw.line((sx, sy, stars[j][0], stars[j][1]),
                          fill=GOLD + (alpha,), width=1)

    # ── Subtle vignette ──────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(35 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ── Lower fog/mist layer ─────────────────────────────────────────────────
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse((-300, 1400, W + 300, 1850), fill=(BRASS[0], BRASS[1], BRASS[2], 15))
    fog = fog.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, fog)

    # ── Title panel via shared utility ───────────────────────────────────────
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
