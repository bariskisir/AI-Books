#!/usr/bin/env python3
"""Cover: Last Exit Before the Sky — Dystopian climate fiction: a courier in a dust-choked domed city discovers the filters are deliberately throttled to control the population."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Palette: dust-choked ochre/brown grading to sooty black, with teal solarpunk accents
DUST_TOP = (140, 105, 60)
DUST_BOTTOM = (25, 18, 10)
ACCENT_TEAL = (80, 175, 170)
ACCENT_AMBER = (220, 160, 50)

rng = random.Random()
rng.seed(314159265)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (60, 45, 25, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Gradient background: dust-choked sky to sooty ground ──────────
    for y in range(H):
        t = y / H
        # Exponential fade through the dust layer
        dust_density = 1.0 - math.exp(-t * 3.5)
        r = int(DUST_TOP[0] + (DUST_BOTTOM[0] - DUST_TOP[0]) * dust_density)
        g = int(DUST_TOP[1] + (DUST_BOTTOM[1] - DUST_TOP[1]) * dust_density)
        b = int(DUST_TOP[2] + (DUST_BOTTOM[2] - DUST_TOP[2]) * dust_density)
        # Add horizontal banding — dust stratification
        band = 8 * math.sin(y * 0.003) + 4 * math.sin(y * 0.007)
        draw.line((0, y, W, y), fill=(max(0, r + int(band)), max(0, g + int(band)), max(0, b + int(band)), 255))

    # ── 2. Faint dome structure high above ────────────────────────────────
    dome_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dome_layer)
    dome_cy = int(H * 0.22)
    dome_rx, dome_ry = 900, 320
    # Dome ribs
    for angle_deg in range(5, 176, 10):
        rad = math.radians(angle_deg)
        sx = W // 2 + int(dome_rx * math.cos(rad))
        sy = dome_cy - int(dome_ry * math.sin(rad))
        ex = W // 2 + int(dome_rx * 0.15 * math.cos(rad))
        ey = dome_cy - int(dome_ry * 0.15 * math.sin(rad))
        dd.line((sx, sy, ex, ey), fill=(160, 140, 100, 25), width=2)
    # Dome arc outline
    for a in range(0, 181, 2):
        rad = math.radians(a)
        px = W // 2 + int(dome_rx * math.cos(rad))
        py = dome_cy - int(dome_ry * math.sin(rad))
        dd.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(160, 140, 100, 30))
    img = Image.alpha_composite(img, dome_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 3. Heavy dust/particulate haze layers ─────────────────────────────
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(40):
        hx = rng.randint(0, W)
        hy = rng.randint(0, H)
        hr = rng.randint(80, 400)
        h_alpha = rng.randint(3, 14)
        hd.ellipse((hx - hr, hy - hr // 3, hx + hr, hy + hr // 3),
                    fill=(140, 110, 70, h_alpha))
    haze = haze.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 4. Massive air filtration towers (central visual element) ─────────
    tower_cx = W // 2
    filters = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(filters)

    # Main central tower cluster
    tower_positions = [
        (tower_cx, int(H * 0.85), 140, int(H * 0.55)),  # (x, base_y, width, height)
        (tower_cx - 250, int(H * 0.83), 90, int(H * 0.40)),
        (tower_cx + 260, int(H * 0.84), 80, int(H * 0.38)),
        (tower_cx - 420, int(H * 0.82), 60, int(H * 0.28)),
        (tower_cx + 430, int(H * 0.83), 55, int(H * 0.25)),
    ]

    for tx, t_base, tw, th in tower_positions:
        t_top = t_base - th
        # Tower body — industrial concrete/steel
        for y in range(t_top, t_base, 4):
            t = (y - t_top) / th
            # Taper slightly upward
            local_w = int(tw * (0.7 + 0.3 * (1 - t)))
            shade = int(35 + 40 * t)
            fd.rectangle((tx - local_w // 2, y, tx + local_w // 2, y + 4),
                          fill=(shade + 10, shade + 5, shade, 230))

        # Horizontal girder bands
        for band_y in range(t_top + int(th * 0.15), t_base, int(th * 0.12)):
            bw = int(tw * 0.85)
            fd.rectangle((tx - bw // 2, band_y - 3, tx + bw // 2, band_y + 3),
                          fill=(60, 58, 50, 200))

        # Massive exhaust vents at top
        for v_count in range(3):
            vx = tx - tw // 4 + v_count * (tw // 4)
            vy = t_top + 20
            vr = tw // 8
            fd.ellipse((vx - vr, vy - vr // 2, vx + vr, vy + vr // 2),
                        fill=(20, 18, 12, 240))
            fd.ellipse((vx - vr + 3, vy - vr // 2 + 2, vx + vr - 3, vy + vr // 2 - 2),
                        fill=(50, 45, 30, 200))

        # Teal solarpunk indicator lights on each tower
        for light_y in range(t_top + int(th * 0.3), t_base - 20, int(th * 0.15)):
            if rng.random() < 0.6:
                l_alpha = rng.randint(80, 180)
                fd.ellipse((tx - 6, light_y - 3, tx + 6, light_y + 3),
                            fill=(*ACCENT_TEAL, l_alpha))
                # Glow
                fd.ellipse((tx - 14, light_y - 8, tx + 14, light_y + 8),
                            fill=(*ACCENT_TEAL, l_alpha // 4))

    # ── 5. Interconnecting pipes and ductwork ────────────────────────────
    for _ in range(20):
        x1 = rng.randint(100, W - 100)
        y1 = rng.randint(int(H * 0.55), int(H * 0.80))
        x2 = x1 + rng.randint(-300, 300)
        y2 = y1 + rng.randint(50, 300)
        p_col = (rng.randint(40, 60), rng.randint(38, 55), rng.randint(30, 45), 200)
        fd.line((x1, y1, x2, y2), fill=p_col, width=rng.randint(6, 18))
        # Pipe joint
        jx, jy = (x1 + x2) // 2, (y1 + y2) // 2
        fd.ellipse((jx - 6, jy - 6, jx + 6, jy + 6), fill=(70, 65, 55, 220))

    # Diagonal support struts
    stride = ImageDraw.Draw(filters)
    for _ in range(12):
        sx = rng.randint(100, W - 100)
        sy = rng.randint(int(H * 0.65), int(H * 0.80))
        ex = sx + rng.randint(-400, 400)
        ey = sy + rng.randint(100, 300)
        stride.line((sx, sy, ex, ey), fill=(45, 42, 35, 120), width=rng.randint(3, 8))

    img = Image.alpha_composite(img, filters)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 6. Courier silhouette (Sarin Qadir) small against the scale ──────
    cx, cy = rng.randint(600, 1000), int(H * 0.88)
    # Body
    draw.line((cx, cy, cx, cy - 50), fill=(15, 12, 8, 200), width=5)
    # Head
    draw.ellipse((cx - 7, cy - 65, cx + 7, cy - 50), fill=(15, 12, 8, 220))
    # Arms
    draw.line((cx, cy - 40, cx - 30, cy - 20), fill=(15, 12, 8, 180), width=3)
    draw.line((cx, cy - 40, cx + 30, cy - 20), fill=(15, 12, 8, 180), width=3)
    # Legs
    draw.line((cx, cy, cx - 15, cy + 30), fill=(15, 12, 8, 180), width=4)
    draw.line((cx, cy, cx + 15, cy + 30), fill=(15, 12, 8, 180), width=4)
    # Small messenger bag
    draw.line((cx - 5, cy - 30, cx + 10, cy - 25), fill=(10, 15, 20, 200), width=5)
    # Shadow beneath
    draw.ellipse((cx - 25, cy + 28, cx + 25, cy + 36), fill=(10, 8, 5, 120))

    # ── 7. Amber light shafts struggling through dust ──────────────────────
    shafts = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shafts)
    for _ in range(rng.randint(4, 7)):
        sx = rng.randint(200, 1400)
        sw = rng.randint(30, 120)
        sh = rng.randint(600, 1200)
        s_alpha = rng.randint(5, 18)
        sd.polygon([
            (sx - sw // 2, 0),
            (sx - sw // 2 - rng.randint(-40, 40), sh),
            (sx + sw // 2 + rng.randint(-40, 40), sh),
            (sx + sw // 2, 0),
        ], fill=(*ACCENT_AMBER, s_alpha))
    # One brighter shaft from a break in the dust
    sd.polygon([
        (W // 2 - 30, 0),
        (W // 2 - 80, int(H * 0.35)),
        (W // 2 + 80, int(H * 0.35)),
        (W // 2 + 30, 0),
    ], fill=(220, 200, 160, 18))
    shafts = shafts.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, shafts)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 8. Dust particles floating everywhere ─────────────────────────────
    dust_particles = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust_particles)
    for _ in range(300):
        px = rng.randint(0, W)
        py = rng.randint(0, H)
        pr = rng.uniform(0.5, 3.5)
        p_alpha = rng.randint(20, 100)
        p_col = rng.choice([
            (160, 130, 80, p_alpha),
            (120, 100, 60, p_alpha),
            (180, 150, 100, p_alpha),
            (90, 80, 50, p_alpha),
        ])
        dd.ellipse((px - pr, py - pr, px + pr, py + pr), fill=p_col)
    img = Image.alpha_composite(img, dust_particles)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. Ground-level details: cracked pavement, debris ─────────────────
    ground = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(ground)
    # Ground plane
    gd.rectangle((0, int(H * 0.92), W, H), fill=(18, 14, 8, 230))
    # Cracks
    for _ in range(25):
        cx1 = rng.randint(0, W)
        cy1 = rng.randint(int(H * 0.92), H - 20)
        cx2 = cx1 + rng.randint(-60, 60)
        cy2 = cy1 + rng.randint(5, 40)
        gd.line((cx1, cy1, cx2, cy2), fill=(30, 25, 18, 150), width=rng.randint(1, 3))
    # Debris scattered
    for _ in range(40):
        dx = rng.randint(0, W)
        dy = rng.randint(int(H * 0.92), H - 10)
        ds = rng.randint(2, 8)
        gd.ellipse((dx - ds, dy - ds // 2, dx + ds, dy + ds // 2),
                    fill=(rng.randint(20, 40), rng.randint(16, 32), rng.randint(10, 22), 200))
    # Rusted grate / manhole cover
    gd.ellipse((W // 2 - 40, int(H * 0.94) - 20, W // 2 + 40, int(H * 0.94) + 20),
                fill=(35, 28, 18, 200))
    gd.line((W // 2 - 40, int(H * 0.94), W // 2 + 40, int(H * 0.94)),
             fill=(20, 16, 10, 180), width=2)
    gd.line((W // 2, int(H * 0.94) - 20, W // 2, int(H * 0.94) + 20),
             fill=(20, 16, 10, 180), width=2)

    img = Image.alpha_composite(img, ground)

    # ── 10. Subtle overall dust-film tint ─────────────────────────────────
    tint = Image.new("RGBA", (W, H), (120, 95, 55, 12))
    img = Image.alpha_composite(img, tint)

    # ── 11. Vignette ──────────────────────────────────────────────────────
    draw = ImageDraw.Draw(img, "RGBA")
    for vy in range(H):
        vt = abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1.0 - vt * 1.2))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

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
