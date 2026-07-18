#!/usr/bin/env python3
"""Cover: Half Past Silence — deaf detective investigating ultrasonic arson in a coastal town; clock face dissolves into sonic rings above a midnight school."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique palette: deep marine night, ultrasonic cyan, ember fire, ghost clock
BG_TOP = (4, 6, 30)
BG_BOT = (35, 18, 40)
SONIC = (0, 220, 245)
EMBER = (245, 100, 25)
CLOCK_PALE = (200, 210, 240)
GOLD = (245, 210, 70)

rng = random.Random()
rng.seed(583947102)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*BG_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Night gradient ──
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOT[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOT[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOT[2] - BG_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Vignette ──
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 100))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 100))

    # ── Clock face (upper portion) — dissolving ghost clock ──
    clock_cx, clock_cy = W // 2, 680
    clock_r = 340

    # Soft halo behind clock
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse((clock_cx - clock_r * 1.4, clock_cy - clock_r * 1.4,
                clock_cx + clock_r * 1.4, clock_cy + clock_r * 1.4),
               fill=(*CLOCK_PALE, 6))
    halo = halo.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, halo)
    draw = ImageDraw.Draw(img, "RGBA")

    # Clock bezel — fragmented particles dissolving outward
    for ang_deg in range(0, 360):
        ang = math.radians(ang_deg)
        px = clock_cx + math.cos(ang) * clock_r
        py = clock_cy + math.sin(ang) * clock_r
        skip = rng.random()
        if skip < 0.55:
            continue  # gaps in the ring
        sz = rng.randint(2, 5)
        a = rng.randint(40, 110)
        draw.ellipse((px - sz, py - sz, px + sz, py + sz), fill=(*CLOCK_PALE, a))
        # trailing particles drifting outward
        if rng.random() < 0.35:
            tx = px + math.cos(ang) * rng.randint(5, 25)
            ty = py + math.sin(ang) * rng.randint(5, 25)
            ts = rng.randint(1, 3)
            draw.ellipse((tx - ts, ty - ts, tx + ts, ty + ts), fill=(*CLOCK_PALE, a // 2))

    # Inner ring (more intact)
    for ang_deg in range(0, 360, 2):
        ang = math.radians(ang_deg)
        px = clock_cx + math.cos(ang) * (clock_r - 18)
        py = clock_cy + math.sin(ang) * (clock_r - 18)
        if rng.random() < 0.35:
            continue
        sz = rng.randint(1, 3)
        draw.ellipse((px - sz, py - sz, px + sz, py + sz), fill=(*CLOCK_PALE, rng.randint(30, 80)))

    # Hour markers — faint dots at 12, 3, 6, 9 positions
    for marker_deg, marker_len in [(0, clock_r * 0.85), (90, clock_r * 0.85),
                                    (180, clock_r * 0.85), (270, clock_r * 0.85)]:
        ang = math.radians(marker_deg)
        mx = clock_cx + math.cos(ang) * marker_len
        my = clock_cy + math.sin(ang) * marker_len
        for _ in range(5):
            ox = rng.randint(-4, 4)
            oy = rng.randint(-4, 4)
            draw.ellipse((mx + ox - 2, my + oy - 2, mx + ox + 2, my + oy + 2),
                         fill=(*CLOCK_PALE, rng.randint(50, 100)))

    # Clock hands — half past (approximately 5:30)
    # Minute hand → 6 o'clock (straight down), angle = pi radians
    minute_ang = math.pi
    minute_len = clock_r * 0.72
    min_x = clock_cx + math.sin(minute_ang) * minute_len
    min_y = clock_cy - math.cos(minute_ang) * minute_len
    # Minute hand is dissolving — draw as line of dots
    for t in range(0, 100, 2):
        frac = t / 100
        dx = clock_cx + (min_x - clock_cx) * frac
        dy = clock_cy + (min_y - clock_cy) * frac
        if rng.random() < 0.2:
            continue
        draw.ellipse((dx - 3, dy - 3, dx + 3, dy + 3), fill=(*CLOCK_PALE, rng.randint(80, 180)))

    # Hour hand → 5:30 position (165 degrees from 12)
    hour_ang = math.radians(165)
    hour_len = clock_r * 0.48
    hour_x = clock_cx + math.sin(hour_ang) * hour_len
    hour_y = clock_cy - math.cos(hour_ang) * hour_len
    for t in range(0, 100, 2):
        frac = t / 100
        dx = clock_cx + (hour_x - clock_cx) * frac
        dy = clock_cy + (hour_y - clock_cy) * frac
        if rng.random() < 0.15:
            continue
        draw.ellipse((dx - 4, dy - 4, dx + 4, dy + 4), fill=(*CLOCK_PALE, rng.randint(80, 200)))

    # Center hub
    for r_sz in [12, 8, 4]:
        draw.ellipse((clock_cx - r_sz, clock_cy - r_sz, clock_cx + r_sz, clock_cy + r_sz),
                     fill=(*CLOCK_PALE, 200 - r_sz * 5))

    # ── COASTAL TOWN & SCHOOL SILHOUETTE ──
    sea_level = 1780

    # Rolling coastal hill line
    hill_pts = [(0, H)]
    for x in range(0, W + 1, 5):
        base_y = sea_level + math.sin(x * 0.007 + 1.2) * 25 + math.sin(x * 0.003 + 0.5) * 45
        hill_pts.append((x, int(base_y)))
    hill_pts.append((W, H))
    draw.polygon(hill_pts, fill=(7, 5, 14, 255))

    # School building (central, prominent)
    sch_cx = W // 2
    sch_w = 300
    sch_top = sea_level - 400
    # Main block
    draw.rectangle((sch_cx - sch_w // 2, sch_top, sch_cx + sch_w // 2, sea_level),
                   fill=(5, 3, 10, 250))
    # Central taller wing
    draw.rectangle((sch_cx - 80, sch_top - 80, sch_cx + 80, sch_top),
                   fill=(4, 2, 8, 250))
    # Roof peaks
    draw.polygon([(sch_cx - sch_w // 2 - 15, sch_top),
                  (sch_cx, sch_top - 55),
                  (sch_cx + sch_w // 2 + 15, sch_top)],
                 fill=(4, 2, 8, 250))
    # Bell tower / cupola (ultrasonic source)
    tower_top = sch_top - 160
    draw.rectangle((sch_cx - 20, tower_top, sch_cx + 20, sch_top - 80),
                   fill=(3, 1, 6, 250))
    draw.polygon([(sch_cx - 30, sch_top - 80),
                  (sch_cx, tower_top - 30),
                  (sch_cx + 30, sch_top - 80)],
                 fill=(3, 1, 6, 250))
    # Small spire
    draw.polygon([(sch_cx - 5, tower_top - 30),
                  (sch_cx, tower_top - 55),
                  (sch_cx + 5, tower_top - 30)],
                 fill=(2, 1, 4, 250))

    # School windows — some dark, some glowing with fire
    for row in range(3):
        for col in range(5):
            wx = sch_cx - 110 + col * 50
            wy = sch_top + 50 + row * 60
            if rng.random() < 0.35:
                # Fire-lit window
                for layer in range(3):
                    lr = EMBER[0] - layer * 40
                    lg = EMBER[1] + layer * 30
                    lb = EMBER[2] + layer * 10
                    la = rng.randint(80, 200) - layer * 30
                    draw.rectangle((wx - 10 + layer, wy - 12 + layer,
                                    wx + 10 - layer, wy + 12 - layer),
                                   fill=(max(0, lr), min(255, lg), min(255, lb), max(10, la)))
                # Bright center
                draw.rectangle((wx - 4, wy - 6, wx + 4, wy + 6), fill=(*GOLD, rng.randint(120, 200)))

    # Nearby buildings
    for bx in range(30, W, rng.randint(90, 160)):
        if abs(bx - sch_cx) < 200:
            continue
        bw = rng.randint(40, 90)
        bh = rng.randint(80, 220)
        by = sea_level - bh
        draw.rectangle((bx - bw // 2, by, bx + bw // 2, sea_level),
                       fill=(7, 5, 12, 220))
        # Roof shape
        if rng.random() < 0.5:
            draw.polygon([(bx - bw // 2 - 5, by), (bx, by - 20), (bx + bw // 2 + 5, by)],
                         fill=(5, 3, 10, 220))
        # Occasional lit window
        if rng.random() < 0.25:
            draw.rectangle((bx - 7, by + 25, bx + 7, by + 40),
                           fill=(*EMBER, rng.randint(40, 100)))

    # ── ULTRASONIC SOUND WAVES ──
    # Radiating from the bell tower spire
    wave_ox = sch_cx
    wave_oy = tower_top - 55  # spire tip

    for ri in range(12):
        radius = 50 + ri * 55
        alpha = max(8, 100 - ri * 7)
        stroke = max(1, 5 - ri // 3)
        # Draw only 60% of each ring (gives a propagating-wave feel)
        start_deg = rng.randint(0, 360)
        span = rng.randint(180, 300)
        draw.arc((wave_ox - radius, wave_oy - radius,
                  wave_ox + radius, wave_oy + radius),
                 start_deg, start_deg + span,
                 fill=(*SONIC, alpha), width=stroke)

    # Secondary arc rings (wider, more transparent)
    for ri in range(6, 18):
        radius = 300 + ri * 40
        alpha = max(3, 40 - ri * 2)
        if alpha < 3:
            break
        start_deg = rng.randint(0, 360)
        span = rng.randint(120, 200)
        draw.arc((wave_ox - radius, wave_oy - radius,
                  wave_ox + radius, wave_oy + radius),
                 start_deg, start_deg + span,
                 fill=(*SONIC, alpha), width=1)

    # ── DETECTIVE SILHOUETTE (left foreground) ──
    det_x = 160
    det_base = sea_level
    det_h = 250

    # Long coat / body
    coat_pts = [(det_x - 30, det_base),
                (det_x - 25, det_base - det_h * 0.55),
                (det_x - 15, det_base - det_h * 0.65),
                (det_x + 15, det_base - det_h * 0.65),
                (det_x + 25, det_base - det_h * 0.55),
                (det_x + 30, det_base)]
    draw.polygon(coat_pts, fill=(4, 2, 8, 230))

    # Head
    head_cx, head_cy = det_x, det_base - det_h + 30
    draw.ellipse((head_cx - 20, head_cy - 25, head_cx + 20, head_cy + 20),
                 fill=(4, 2, 8, 230))

    # Hat brim
    draw.ellipse((head_cx - 32, head_cy - 30, head_cx + 32, head_cy - 15),
                 fill=(3, 1, 6, 230))
    draw.rectangle((head_cx - 20, head_cy - 30, head_cx + 20, head_cy - 10),
                   fill=(4, 2, 8, 230))

    # ── FLOATING FIRE EMBERS & PARTICLES ──
    ember_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(ember_layer)
    for _ in range(120):
        px = rng.randint(50, W - 50)
        py = rng.randint(200, 1750)
        pr = rng.uniform(1.5, 5)
        pa = rng.randint(30, 160)
        col = rng.choice([EMBER, GOLD, (255, 180, 80), (150, 220, 255), (200, 200, 220)])
        ed.ellipse((int(px - pr), int(py - pr), int(px + pr), int(py + pr)),
                   fill=(*col, pa))
    # Blur some for a soft glow effect
    ember_layer = ember_layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, ember_layer)

    # ── AMBIENT GLOW: fire from school + ultrasonic radiance ──
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    # Fire glow around school
    gd.ellipse((sch_cx - 350, sch_top - 100, sch_cx + 350, sea_level + 150),
               fill=(*EMBER, 8))
    # Ultrasonic cyan glow around tower
    gd.ellipse((wave_ox - 200, wave_oy - 200, wave_ox + 200, wave_oy + 200),
               fill=(*SONIC, 6))
    # Moonlight from above
    gd.ellipse((clock_cx - clock_r, 0, clock_cx + clock_r, clock_cy + 100),
               fill=(*CLOCK_PALE, 4))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, glow_layer)

    # ── Title panel ──
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
