#!/usr/bin/env python3
"""Cover: The Consequence of Forgotten Doors — Oslo demolition crew finds impossible doorframes to rooms full of regret. Perspective scene: broken wall, warm portal glow, Man in Grey Coat silhouette, floating letters, debris."""

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
rng.seed(1947283615)

# Cold demolition-site palette: slate, steel, ash
# Portal glow: warm amber, gold, ochre
COLD_SKY = (45, 52, 62)
WARM_GLOW = (220, 175, 90)
DOOR_COLOR = (65, 55, 45)
MAN_COLOR = (25, 25, 30)
PAPER_COLOR = (225, 215, 190)
DEBRIS_COLOR = (70, 62, 52)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # Base: cold grey-blue gradient
    img = Image.new("RGBA", (W, H), (45, 52, 62, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Gradient: cold demolition sky ──
    for y in range(H):
        t = y / H
        r = int(45 + (55 - 45) * t)
        g = int(52 + (48 - 52) * t)
        b = int(62 + (50 - 62) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Vignette ──
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 90))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 90))

    # ── Demolished building interior: jagged broken walls ──
    # Left broken wall
    wall_pts_left = [
        (0, 200),
        (rng.randint(50, 180), rng.randint(180, 280)),
        (rng.randint(200, 350), rng.randint(220, 320)),
        (rng.randint(250, 400), rng.randint(500, 700)),
        (rng.randint(200, 360), rng.randint(900, 1100)),
        (rng.randint(180, 320), rng.randint(1200, 1400)),
        (rng.randint(150, 280), rng.randint(1500, 1700)),
        (0, 1765),
    ]
    draw.polygon(wall_pts_left, fill=(55, 48, 42, 240))
    # Texture lines on left wall
    for _ in range(20):
        x_base = rng.randint(10, 250)
        y1 = rng.randint(250, 1700)
        y2 = min(y1 + rng.randint(20, 80), 1760)
        draw.line((x_base, y1, x_base + rng.randint(-10, 10), y2),
                  fill=(48, 42, 36, rng.randint(40, 90)), width=rng.randint(1, 3))

    # Right broken wall
    wall_pts_right = [
        (W, 300),
        (W - rng.randint(50, 150), rng.randint(250, 350)),
        (W - rng.randint(180, 300), rng.randint(280, 400)),
        (W - rng.randint(220, 350), rng.randint(600, 800)),
        (W - rng.randint(180, 300), rng.randint(1000, 1200)),
        (W - rng.randint(120, 250), rng.randint(1300, 1500)),
        (W - rng.randint(80, 180), rng.randint(1600, 1750)),
        (W, 1765),
    ]
    draw.polygon(wall_pts_right, fill=(50, 44, 38, 240))
    for _ in range(15):
        x_base = W - rng.randint(30, 200)
        y1 = rng.randint(300, 1700)
        y2 = min(y1 + rng.randint(20, 60), 1760)
        draw.line((x_base, y1, x_base + rng.randint(-8, 8), y2),
                  fill=(42, 38, 32, rng.randint(30, 80)), width=rng.randint(1, 2))

    # ── Floor / rubble pile ──
    for x in range(0, W, rng.randint(15, 40)):
        pile_h = rng.randint(20, 60)
        pile_col = (rng.randint(55, 75), rng.randint(48, 65), rng.randint(40, 55))
        draw.ellipse((x - 30, 1700 - pile_h, x + 30, 1765),
                     fill=(*pile_col, 200))

    # ── Doorframe (the portal) — central, slightly right of center ──
    df_x0, df_y0 = 520, 580
    df_w, df_h = 340, 620
    df_x1, df_y1 = df_x0 + df_w, df_y0 + df_h

    # Doorframe wood/dark structure
    draw.rectangle((df_x0, df_y0, df_x1, df_y1), fill=(45, 38, 32, 230))
    # Inner opening (the portal)
    margin = 18
    portal_x0 = df_x0 + margin
    portal_y0 = df_y0 + margin
    portal_x1 = df_x1 - margin
    portal_y1 = df_y1 - margin

    # ── Portal glow layer behind everything in the door ──
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    # Intense center glow
    for radius in range(180, 20, -10):
        alpha = max(5, 60 - radius // 3)
        gd.rectangle((portal_x0 + radius // 4, portal_y0 + radius // 4,
                       portal_x1 - radius // 4, portal_y1 - radius // 4),
                     fill=(WARM_GLOW[0], WARM_GLOW[1], WARM_GLOW[2], alpha))
    # Outer light spill on floor
    gd.ellipse((df_x0 - 80, df_y1 - 40, df_x1 + 80, df_y1 + 120),
               fill=(WARM_GLOW[0], WARM_GLOW[1], WARM_GLOW[2], 20))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Impossible room contents visible through portal ──
    # (furniture silhouettes that shouldn't exist)
    # A chair
    draw.rectangle((portal_x0 + 60, portal_y1 - 140, portal_x0 + 100, portal_y1 - 40),
                   fill=(55, 45, 35, 180))
    draw.rectangle((portal_x0 + 40, portal_y1 - 170, portal_x0 + 120, portal_y1 - 150),
                   fill=(55, 45, 35, 180))
    # A table
    draw.rectangle((portal_x1 - 160, portal_y1 - 100, portal_x1 - 40, portal_y1 - 85),
                   fill=(50, 40, 30, 180))
    draw.line((portal_x1 - 150, portal_y1 - 85, portal_x1 - 150, portal_y1),
              fill=(50, 40, 30, 180), width=4)
    draw.line((portal_x1 - 60, portal_y1 - 85, portal_x1 - 60, portal_y1),
              fill=(50, 40, 30, 180), width=4)
    # Warm ambient light inside portal
    for _ in range(40):
        px = rng.randint(portal_x0 + 20, portal_x1 - 20)
        py = rng.randint(portal_y0 + 20, portal_y1 - 20)
        pr = rng.randint(3, 12)
        pa = rng.randint(20, 60)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr),
                     fill=(WARM_GLOW[0], WARM_GLOW[1], WARM_GLOW[2], pa))

    # ── Doorframe trim ──
    draw.rectangle((df_x0, df_y0, df_x1, df_y0 + 8), fill=(35, 30, 26, 255))
    draw.rectangle((df_x0, df_y1 - 8, df_x1, df_y1), fill=(35, 30, 26, 255))
    draw.rectangle((df_x0, df_y0, df_x0 + 8, df_y1), fill=(35, 30, 26, 255))
    draw.rectangle((df_x1 - 8, df_y0, df_x1, df_y1), fill=(35, 30, 26, 255))

    # ── Second doorframe behind (receding perspective, liminal depth) ──
    df2_x0 = df_x0 + 190
    df2_y0 = df_y0 + 160
    df2_w = 80
    df2_h = 160
    draw.rectangle((df2_x0, df2_y0, df2_x0 + df2_w, df2_y0 + df2_h),
                   fill=(40, 35, 30, 200))
    draw.rectangle((df2_x0 + 5, df2_y0 + 5, df2_x0 + df2_w - 5, df2_y0 + df2_h - 5),
                   fill=(WARM_GLOW[0], WARM_GLOW[1], WARM_GLOW[2], 30))

    # ── Third faint doorframe further back ──
    df3_x0 = df2_x0 + 30
    df3_y0 = df2_y0 + 40
    draw.rectangle((df3_x0, df3_y0, df3_x0 + 20, df3_y0 + 40),
                   outline=(80, 72, 60, 120), width=2)

    # ── The Man in the Grey Coat — silhouette in the main portal ──
    man_x = portal_x0 + 70
    man_top = portal_y0 + 100
    man_bot = portal_y1 - 40
    # Coat body
    draw.polygon([
        (man_x - 28, man_bot),
        (man_x - 22, man_top + 80),
        (man_x - 15, man_top + 60),
        (man_x - 8, man_top + 20),
        (man_x, man_top),
        (man_x + 8, man_top + 20),
        (man_x + 15, man_top + 60),
        (man_x + 22, man_top + 80),
        (man_x + 28, man_bot),
    ], fill=(18, 18, 22, 220))
    # Grey coat faint outline glow (rim light from portal)
    draw.polygon([
        (man_x - 28, man_bot),
        (man_x - 22, man_top + 80),
        (man_x - 15, man_top + 60),
        (man_x - 8, man_top + 20),
        (man_x, man_top),
    ], fill=(WARM_GLOW[0], WARM_GLOW[1], WARM_GLOW[2], 12))

    # ── Floating letters / papers ──
    for _ in range(rng.randint(12, 22)):
        lx = rng.randint(150, 1450)
        ly = rng.randint(300, 1500)
        lw = rng.randint(30, 55)
        lh = rng.randint(40, 65)
        angle = rng.uniform(-0.4, 0.4)
        lp = rng.randint(160, 220)
        # Letter body
        draw.rectangle((lx, ly, lx + lw, ly + lh),
                       fill=(PAPER_COLOR[0], PAPER_COLOR[1], PAPER_COLOR[2], lp))
        # Faint text lines on letter
        for li in range(rng.randint(3, 6)):
            tx = lx + 5
            ty = ly + 8 + li * 8
            tw = rng.randint(12, lw - 14)
            draw.line((tx, ty, tx + tw, ty),
                      fill=(100, 90, 80, rng.randint(30, 70)), width=1)
        # Fold/fray effect
        if rng.random() < 0.4:
            draw.line((lx + lw, ly, lx + lw - 8, ly + 8),
                      fill=(160, 150, 130, lp), width=1)

    # ── Photograph (square, polaroid-style) ──
    for _ in range(rng.randint(2, 4)):
        px = rng.randint(250, 1350)
        py = rng.randint(400, 1400)
        ps = rng.randint(35, 55)
        pa = rng.randint(140, 200)
        draw.rectangle((px, py, px + ps, py + ps), fill=(210, 200, 180, pa))
        # Faint image inside photo
        for _ in range(8):
            sx = px + rng.randint(4, ps - 8)
            sy = py + rng.randint(4, ps - 8)
            draw.line((sx, sy, sx + rng.randint(3, 12), sy + rng.randint(3, 10)),
                      fill=(130, 110, 90, rng.randint(20, 50)), width=1)

    # ── Demolition debris / dust particles ──
    for _ in range(rng.randint(80, 150)):
        dx = rng.randint(0, W)
        dy = rng.randint(100, 1700)
        dr = rng.uniform(1.0, 4.5)
        da = rng.randint(15, 60)
        dc = rng.choice([
            (130, 120, 100, da),
            (100, 95, 85, da),
            (150, 140, 120, da),
            (DEBRIS_COLOR[0] + 20, DEBRIS_COLOR[1] + 15, DEBRIS_COLOR[2] + 10, da),
        ])
        draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=dc)

    # ── Overhead broken beams / rebar ──
    for _ in range(rng.randint(3, 6)):
        x1 = rng.randint(50, W - 50)
        y1 = rng.randint(100, 350)
        x2 = x1 + rng.randint(-120, 120)
        y2 = rng.randint(350, 600)
        draw.line((x1, y1, x2, y2), fill=(35, 30, 25, rng.randint(150, 220)),
                  width=rng.randint(5, 12))
        # Rebar detail
        if rng.random() < 0.5:
            draw.line((x1, y1, x2 + rng.randint(-20, 20), y2 + rng.randint(-10, 10)),
                      fill=(60, 55, 45, rng.randint(40, 80)), width=2)

    # ── Oslo skyline silhouette through a hole in the right wall ──
    skyline_y = 1100
    for sx in range(W - 350, W - 50, rng.randint(20, 50)):
        bh = rng.randint(40, 160)
        bw = rng.randint(15, 35)
        draw.rectangle((sx - bw // 2, skyline_y - bh, sx + bw // 2, skyline_y),
                       fill=(30, 35, 40, 180))

    # ── Subtle light rays from portal ──
    for _ in range(rng.randint(6, 12)):
        rx = rng.randint(df_x0 + 20, df_x1 - 20)
        angle = math.radians(rng.randint(-25, 25))
        length = rng.randint(300, 600)
        for step in range(0, length, 4):
            sx = rx + int(math.sin(angle) * step)
            sy = df_y1 + step
            if sx < 0 or sx > W or sy > H:
                break
            alpha_dist = max(0, 20 - step // 30)
            draw.line((sx, sy, sx + int(math.sin(angle) * 6), sy + 6),
                      fill=(WARM_GLOW[0], WARM_GLOW[1], WARM_GLOW[2], alpha_dist),
                      width=rng.randint(2, 4))

    # ── Dust motes glowing in portal light ──
    for _ in range(rng.randint(40, 70)):
        dx = rng.randint(df_x0 - 60, df_x1 + 60)
        dy = rng.randint(df_y0, df_y1 + 150)
        dr = rng.uniform(1, 3)
        da = rng.randint(30, 90)
        draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr),
                     fill=(WARM_GLOW[0], WARM_GLOW[1], WARM_GLOW[2], da))

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
