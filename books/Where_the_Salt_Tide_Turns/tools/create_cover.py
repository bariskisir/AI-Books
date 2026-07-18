#!/usr/bin/env python3
"""Cover: Where the Salt Tide Turns — Rocky island shoreline at twilight, exposed tide pools reflecting a dying light, journal pages dissolving into tidal channels, a distant lighthouse, and two female silhouettes bridging memory and shore."""

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
rng.seed(720240718)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── Base canvas ──────────────────────────────────────────────────────────
    img = Image.new("RGBA", (W, H), (30, 20, 30, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Sky gradient: deep lavender-purple (top) → coral-salmon (horizon) ────
    sky_top = (45, 25, 55)
    sky_mid = (100, 55, 65)
    sky_horizon = (210, 140, 120)
    horizon_y = 850
    for y in range(horizon_y):
        t = y / horizon_y
        if t < 0.55:
            u = t / 0.55
            r = int(sky_top[0] + (sky_mid[0] - sky_top[0]) * u)
            g = int(sky_top[1] + (sky_mid[1] - sky_top[1]) * u)
            b = int(sky_top[2] + (sky_mid[2] - sky_top[2]) * u)
        else:
            u = (t - 0.55) / 0.45
            r = int(sky_mid[0] + (sky_horizon[0] - sky_mid[0]) * u)
            g = int(sky_mid[1] + (sky_horizon[1] - sky_mid[1]) * u)
            b = int(sky_mid[2] + (sky_horizon[2] - sky_mid[2]) * u)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Distant sea: smooth teal band transitioning to shoreline ─────────────
    for y in range(horizon_y, 1050):
        t = (y - horizon_y) / 200
        r = int(120 + (60 - 120) * t)
        g = int(140 + (80 - 140) * t)
        b = int(155 + (75 - 155) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Sun/glow on horizon ───────────────────────────────────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    sun_cx, sun_cy = W // 2 + 100, 820
    for rad in range(300, 30, -15):
        alpha = max(4, 28 - (300 - rad) // 12)
        gd.ellipse((sun_cx - rad, sun_cy - rad, sun_cx + rad, sun_cy + rad),
                   fill=(230, 180, 130, alpha))
    gd.ellipse((sun_cx - 30, sun_cy - 30, sun_cx + 30, sun_cy + 30),
               fill=(250, 210, 160, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Distant island silhouette ─────────────────────────────────────────────
    isle_base = 860
    draw.ellipse((W // 2 - 350, isle_base - 30, W // 2 + 80, isle_base + 60),
                 fill=(35, 25, 40, 230))
    draw.ellipse((W // 2 - 200, isle_base - 70, W // 2 - 20, isle_base + 30),
                 fill=(30, 22, 36, 240))

    # Lighthouse on the island
    lh_x = W // 2 - 130
    lh_y = 700
    draw.polygon([(lh_x - 12, lh_y + 120), (lh_x - 8, lh_y),
                  (lh_x + 8, lh_y), (lh_x + 12, lh_y + 120)],
                 fill=(25, 18, 30, 240))
    draw.polygon([(lh_x - 16, lh_y), (lh_x + 16, lh_y),
                  (lh_x, lh_y - 30)],
                 fill=(25, 18, 30, 240))
    # Lighthouse light beam
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    for ang in range(-25, 26, 5):
        a = math.radians(ang + 10)
        ex = lh_x + math.cos(a) * 400
        ey = lh_y - 20 + math.sin(a) * 200
        bd.line((lh_x, lh_y - 10, ex, ey), fill=(245, 230, 180, 8), width=18)
    bd.ellipse((lh_x - 8, lh_y - 28, lh_x + 8, lh_y - 12), fill=(250, 240, 200, 100))
    beam = beam.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, beam)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Rocky shoreline / tide pools ──────────────────────────────────────────
    shore_top = 1000
    # Base rock layer
    rock_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rock_layer)
    # Large rocks forming the shore
    rock_segments = [
        (0, shore_top, 300, H),
        (250, shore_top - 20, 550, H),
        (480, shore_top + 30, 750, H),
        (700, shore_top - 10, 1020, H),
        (950, shore_top + 40, 1250, H),
        (1180, shore_top - 15, 1420, H),
        (1380, shore_top + 20, W, H),
    ]
    for rx1, ry1, rx2, ry2 in rock_segments:
        rcol = rng.randint(35, 60)
        pts = [(rx1, ry1)]
        for x in range(rx1, rx2 + 1, 12):
            t = (x - rx1) / (rx2 - rx1)
            depth = 20 + 40 * (t * (1 - t)) + rng.randint(-15, 15)
            rock_y = ry1 + depth + (1 - t) * 30 + t * 20
            pts.append((x, rock_y))
        pts.append((rx2, H))
        pts.append((rx1, H))
        rd.polygon(pts, fill=(rcol, rcol - 5, rcol - 8, 245))

    # Rock texture overlays
    for _ in range(80):
        px = rng.randint(50, W - 50)
        py = rng.randint(shore_top, H - 100)
        shade = rng.randint(20, 45)
        rd.ellipse((px - rng.randint(3, 12), py - rng.randint(2, 6),
                     px + rng.randint(3, 12), py + rng.randint(2, 6)),
                    fill=(shade - 5, shade - 3, shade, min(180, rng.randint(60, 200))))

    img = Image.alpha_composite(img, rock_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Tide pools (water-filled depressions in the rocks) ────────────────────
    tide_pools = [
        (200, 1150, 400, 1330),
        (550, 1080, 780, 1260),
        (300, 1380, 520, 1600),
        (850, 1120, 1100, 1380),
        (1050, 1300, 1280, 1520),
        (600, 1500, 850, 1750),
        (1100, 1550, 1400, 1800),
        (130, 1480, 350, 1680),
    ]
    for px1, py1, px2, py2 in tide_pools:
        pool = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pool)
        # Pool shape (irregular ellipse)
        cpx = (px1 + px2) // 2
        cpy = (py1 + py2) // 2
        rx = (px2 - px1) // 2
        ry = (py2 - py1) // 2
        # Build irregular polygon for the pool
        pool_pts = []
        for i in range(20):
            angle = math.tau * i / 20
            wobble = 0.8 + 0.4 * rng.random()
            px = cpx + math.cos(angle) * rx * wobble
            py = cpy + math.sin(angle) * ry * wobble
            pool_pts.append((px, py))
        # Pool water color: shallow teal reflecting the sky
        pool_r = rng.randint(80, 130)
        pool_g = rng.randint(130, 180)
        pool_b = rng.randint(160, 200)
        pd.polygon(pool_pts, fill=(pool_r, pool_g, pool_b, 180))

        # Pool edge highlight (wet rock)
        pd.polygon(pool_pts, outline=(pool_r + 30, pool_g + 20, pool_b + 10, 80), width=2)

        # Life in the pool — small anemones, seaweed, shells
        for _ in range(rng.randint(4, 12)):
            sx = rng.randint(px1 + 15, px2 - 15)
            sy = rng.randint(py1 + 15, py2 - 15)
            sr = rng.randint(3, 10)
            life_col = rng.choice([
                (200, 120, 100, 160),   # coral
                (100, 80, 60, 140),      # brown seaweed
                (60, 140, 80, 150),      # green algae
                (220, 200, 180, 130),    # sand/empty shell
            ])
            pd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=life_col)

        # Bioluminescent dots in the pool (tiny glowing specks)
        for _ in range(rng.randint(5, 15)):
            bx = rng.randint(px1 + 10, px2 - 10)
            by = rng.randint(py1 + 10, py2 - 10)
            bs = rng.randint(1, 3)
            balpha = rng.randint(60, 180)
            pd.ellipse((bx - bs, by - bs, bx + bs, by + bs),
                       fill=(180, 240, 255, balpha))
            # Outer faint glow
            pd.ellipse((bx - bs * 3, by - bs * 3, bx + bs * 3, by + bs * 3),
                       fill=(180, 240, 255, balpha // 4))

        pool = pool.filter(ImageFilter.GaussianBlur(2))
        img = Image.alpha_composite(img, pool)
        draw = ImageDraw.Draw(img, "RGBA")

    # ── Journal pages drifting / dissolving into the tide ─────────────────────
    journal_positions = [
        (100, 880, 0.0),    # top-left, fresh
        (350, 920, 0.3),    # partly dissolved
        (600, 900, 0.5),    # half gone
        (900, 940, 0.7),    # mostly dissolved
        (1200, 910, 0.8),   # almost gone
        (1450, 950, 0.9),   # edge of existence
    ]
    for jx, jy, dissolve in journal_positions:
        page = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        pd = ImageDraw.Draw(page)
        pw, ph = 100, 130
        page_alpha = int(200 * (1 - dissolve))
        page_col = (240, 230, 210, page_alpha)
        # Page rectangle with slight rotation via polygon
        rot = dissolve * 0.15 + rng.uniform(-0.05, 0.05)
        cos_r = math.cos(rot)
        sin_r = math.sin(rot)
        corners = [
            (jx, jy),
            (jx + pw * cos_r, jy + pw * sin_r),
            (jx + pw * cos_r - ph * sin_r, jy + pw * sin_r + ph * cos_r),
            (jx - ph * sin_r, jy + ph * cos_r),
        ]
        pd.polygon(corners, fill=page_col)

        # Handwriting lines on the page (cursive-like strokes)
        if dissolve < 0.7:
            for line_i in range(rng.randint(4, 7)):
                ly = jy + 15 + line_i * 16
                lx_start = jx + 10
                lx_end = jx + pw - 15
                # Wavy handwriting line
                hw_pts = []
                for step in range(0, int(lx_end - lx_start) + 1, 4):
                    wx = lx_start + step
                    wy = ly + 3 * math.sin(step * 0.15 + dissolve * 2 + line_i)
                    hw_pts.append((wx, wy))
                line_alpha = int(120 * (1 - dissolve))
                pd.line(hw_pts, fill=(80, 60, 70, line_alpha), width=2)

        # Bottom corner curl (as if turning)
        curl_x = jx + pw - 10
        curl_y = jy + ph - 10
        pd.ellipse((curl_x - 15, curl_y - 15, curl_x + 15, curl_y + 15),
                   fill=(210, 195, 170, page_alpha))

        # As dissolve increases, page breaks into fragments
        if dissolve > 0.3:
            for _ in range(int(dissolve * 20)):
                fx = jx + rng.randint(-10, pw + 10)
                fy = jy + rng.randint(-10, ph + 10)
                fs = rng.randint(3, 10) * dissolve
                if rng.random() < 0.5:
                    pd.ellipse((fx, fy, fx + fs, fy + fs),
                               fill=(240, 230, 210, int(page_alpha * 0.4)))

        page = page.filter(ImageFilter.GaussianBlur(1.5))
        img = Image.alpha_composite(img, page)
        draw = ImageDraw.Draw(img, "RGBA")

    # ── Handwriting strokes that escape the pages and become tidal channels ────
    channel_starts = [
        (180, 1050),
        (420, 1100),
        (700, 1070),
        (1050, 1120),
        (1350, 1080),
    ]
    for csx, csy in channel_starts:
        channel_pts = [(csx, csy)]
        cx, cy = csx, csy
        for _ in range(rng.randint(8, 15)):
            cx += rng.randint(30, 80)
            cy += rng.randint(15, 50) + rng.randint(-15, 15)
            channel_pts.append((cx, cy))
        # Stroke transitions from ink-dark to water-teal
        for i in range(len(channel_pts) - 1):
            t = i / len(channel_pts)
            inkiness = max(0, 1 - t * 1.5)
            r = int(60 + (80 - 60) * (1 - inkiness))
            g = int(40 + (160 - 40) * (1 - inkiness))
            b = int(70 + (180 - 70) * (1 - inkiness))
            width = max(1, int(4 + t * 6))
            draw.line(channel_pts[i] + channel_pts[i + 1],
                      fill=(r, g, b, int(120 + 80 * inkiness)), width=width)

    # ── Two female silhouettes ─────────────────────────────────────────────────
    # Foreground figure: Cass (standing at water's edge, facing the sea)
    cass_x, cass_y = W // 2 - 200, 1000
    draw.polygon([
        (cass_x - 15, cass_y + 120),   # feet
        (cass_x + 15, cass_y + 120),
        (cass_x + 12, cass_y + 60),    # hips
        (cass_x + 8, cass_y + 20),     # torso
        (cass_x + 12, cass_y - 10),    # shoulders
        (cass_x - 12, cass_y - 10),
        (cass_x - 8, cass_y + 20),
        (cass_x - 12, cass_y + 60),
    ], fill=(20, 15, 25, 200))
    # Head
    draw.ellipse((cass_x - 10, cass_y - 40, cass_x + 10, cass_y - 18),
                 fill=(20, 15, 25, 200))
    # Hair (slightly longer, wind-blown)
    hair_pts = []
    for i in range(10):
        hx = cass_x - 12 + rng.randint(-2, 2)
        hy = cass_y - 38 + i * 8 + rng.randint(-2, 2)
        hx -= rng.randint(2, 5)  # sweep left
        hair_pts.append((hx, hy))
    draw.line(hair_pts, fill=(15, 10, 18, 210), width=4)
    hair_pts2 = []
    for i in range(8):
        hx = cass_x + 12 + rng.randint(-2, 2)
        hy = cass_y - 38 + i * 8 + rng.randint(-2, 2)
        hx += rng.randint(3, 6)  # sweep right
        hair_pts2.append((hx, hy))
    draw.line(hair_pts2, fill=(15, 10, 18, 210), width=4)

    # Second figure: Vivienne / memory (on the rocks, faint, turned away)
    viv_x, viv_y = W // 2 + 350, 980
    viv_alpha = 100
    draw.polygon([
        (viv_x - 12, viv_y + 90),
        (viv_x + 12, viv_y + 90),
        (viv_x + 10, viv_y + 45),
        (viv_x + 6, viv_y + 15),
        (viv_x + 10, viv_y - 8),
        (viv_x - 10, viv_y - 8),
        (viv_x - 6, viv_y + 15),
        (viv_x - 10, viv_y + 45),
    ], fill=(30, 25, 35, viv_alpha))
    draw.ellipse((viv_x - 8, viv_y - 35, viv_x + 8, viv_y - 18),
                 fill=(30, 25, 35, viv_alpha))
    # Dress suggestion (lighter, flowing)
    dress_pts = [
        (viv_x - 12, viv_y + 45),
        (viv_x - 18, viv_y + 90),
        (viv_x + 18, viv_y + 90),
        (viv_x + 12, viv_y + 45),
    ]
    draw.polygon(dress_pts, fill=(60, 50, 70, viv_alpha - 20))

    # ── Stars in the sky ───────────────────────────────────────────────────────
    for _ in range(80):
        sx = rng.randint(50, W - 50)
        sy = rng.randint(30, 700)
        ss = rng.uniform(0.5, 2.5)
        sa = rng.randint(40, 200)
        draw.ellipse((sx - ss, sy - ss, sx + ss, sy + ss),
                     fill=(220, 220, 240, sa))

    # ── Moon crescent ─────────────────────────────────────────────────────────
    moon_x, moon_y = W - 250, 200
    draw.ellipse((moon_x - 30, moon_y - 30, moon_x + 30, moon_y + 30),
                 fill=(230, 225, 215, 150))
    draw.ellipse((moon_x + 12, moon_y - 20, moon_x + 36, moon_y + 28),
                 fill=(45, 25, 55, 255))  # carve out crescent

    # ── Fine mist layer near the horizon ──────────────────────────────────────
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    for _ in range(15):
        my = rng.randint(750, 1100)
        mw = rng.randint(200, 600)
        mx = rng.randint(0, W)
        md.ellipse((mx - mw, my - 30, mx + mw, my + 30),
                   fill=(200, 180, 170, rng.randint(5, 15)))
    mist = mist.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Subtle foam line where waves meet shore ───────────────────────────────
    for x in range(0, W, 3):
        y_base = 1000 + 40 * math.sin(x * 0.02) + 20 * math.sin(x * 0.05)
        draw.line((x, y_base, x, y_base + 3),
                  fill=(240, 235, 225, rng.randint(20, 60)), width=2)

    # ── Title panel via shared utility ────────────────────────────────────────
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
