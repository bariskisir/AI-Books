#!/usr/bin/env python3
"""Cover: Where Thistles Drink the Sun — A disgraced herbalist returns to thorn-woven groves to break a curse where moon-touched children speak in tongues and drive parents mad."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique palette: blood-crimson moon, murky grove browns, sickly herbal amber
# Top = deep bruise purple (night sky), mid = blood-rust red (moon's curse),
# Bottom = black-thorn brown (the grove)
SKY_TOP = (18, 8, 22)       # bruise-purple night
SKY_MID = (80, 18, 22)      # blood-rust red
SKY_BOT = (12, 8, 5)        # black-thorn bottom
THORN_COL = (35, 18, 12)    # dark thorn wood
BLOOD_COL = (140, 28, 30)   # blood red
AMBER_COL = (200, 150, 60)  # sickly amber/herbal glow
PALE_COL = (220, 200, 180)  # pale moon skin


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random(hash(title + "thistle-drink-moon-curse"))

    img = Image.new("RGBA", (W, H), (*SKY_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Three-zone gradient background ──────────────────────────────
    for y in range(H):
        t = y / H
        if t < 0.35:
            u = t / 0.35
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * u + 4 * math.sin(u * 3.7))
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * u + 2 * math.sin(u * 2.9))
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * u - 3 * math.sin(u * 2.1))
        elif t < 0.65:
            u = (t - 0.35) / 0.30
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * u)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * u)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * u)
        else:
            u = (t - 0.65) / 0.35
            r = int(SKY_BOT[0] + 4 * u)
            g = int(SKY_BOT[1] + 3 * u)
            b = int(SKY_BOT[2] + 2 * u)
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # ── Blood-Red Moon ──────────────────────────────────────────────
    moon_cx, moon_cy = W // 2, 320
    moon_r = 180

    # Outer blood-red glow rings
    for gi in range(6, 0, -1):
        gr = moon_r + gi * 30
        ga = max(0, 60 - gi * 10)
        draw.ellipse((moon_cx - gr, moon_cy - gr, moon_cx + gr, moon_cy + gr),
                     fill=(BLOOD_COL[0], BLOOD_COL[1], BLOOD_COL[2], ga))

    # Moon body — pale with blood-rust tint
    draw.ellipse((moon_cx - moon_r, moon_cy - moon_r, moon_cx + moon_r, moon_cy + moon_r),
                 fill=(*PALE_COL, 240))

    # Moon surface markings — like veins of blood
    for _ in range(rng.randint(40, 70)):
        mx = moon_cx + int(rng.gauss(0, moon_r * 0.5))
        my = moon_cy + int(rng.gauss(0, moon_r * 0.5))
        dist = math.hypot(mx - moon_cx, my - moon_cy)
        if dist > moon_r * 0.85:
            continue
        mr = rng.uniform(1.5, 5.0)
        draw.ellipse((mx - mr, my - mr, mx + mr, my + mr),
                     fill=(BLOOD_COL[0], BLOOD_COL[1], BLOOD_COL[2], rng.randint(30, 100)))

    # Blood-red corona glow (blur pass)
    corona = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(corona)
    cd.ellipse((moon_cx - moon_r - 40, moon_cy - moon_r - 40,
                moon_cx + moon_r + 40, moon_cy + moon_r + 40),
               fill=(*BLOOD_COL, 50))
    cd.ellipse((moon_cx - moon_r - 80, moon_cy - moon_r - 80,
                moon_cx + moon_r + 80, moon_cy + moon_r + 80),
               fill=(BLOOD_COL[0] // 2, BLOOD_COL[1] // 2, BLOOD_COL[2] // 2, 25))
    corona = corona.filter(ImageFilter.GaussianBlur(24))
    img = Image.alpha_composite(img, corona)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Thorn-Woven Grove (left and right framing thorns) ───────────
    def draw_thorn_branch(d, x0, y0, angle, length, depth, col, max_depth=5):
        """Recursive thorn branch drawing — gnarled, crooked thorns."""
        if depth > max_depth or length < 12:
            return
        ex = int(x0 + math.cos(angle) * length)
        ey = int(y0 + math.sin(angle) * length)
        w = max(1, 7 - depth)
        d.line((x0, y0, ex, ey), fill=(*col, 180 - depth * 25), width=w)

        # Draw thorns along the branch
        num_thorns = rng.randint(1, 3)
        for _ in range(num_thorns):
            t_frac = rng.uniform(0.2, 0.9)
            tx = int(x0 + (ex - x0) * t_frac + rng.randint(-5, 5))
            ty = int(y0 + (ey - y0) * t_frac + rng.randint(-5, 5))
            t_ang = angle + rng.choice([-1.2, 1.2, -0.8, 0.8])
            t_len = rng.randint(6, 18)
            t_ex = int(tx + math.cos(t_ang) * t_len)
            t_ey = int(ty + math.sin(t_ang) * t_len)
            d.line((tx, ty, t_ex, t_ey), fill=(*col, 180 - depth * 25), width=max(1, w - 1))

            # Thorn tip (small sharp triangle)
            tip_ang = t_ang + rng.choice([-0.6, 0.6])
            tip_x = int(t_ex + math.cos(tip_ang) * int(t_len * 0.3))
            tip_y = int(t_ey + math.sin(tip_ang) * int(t_len * 0.3))
            d.line((t_ex, t_ey, tip_x, tip_y), fill=(40, 22, 14, 200), width=1)

        # Recurse
        new_angle = angle + rng.uniform(-0.5, 0.5)
        new_len = int(length * rng.uniform(0.55, 0.75))
        draw_thorn_branch(d, ex, ey, new_angle, new_len, depth + 1, col, max_depth)

    # Left grove — thorn branches from left edge
    for _ in range(rng.randint(8, 12)):
        base_x = rng.randint(-30, 60)
        base_y = rng.randint(200, 1800)
        ang = rng.uniform(-0.6, 0.6)
        ln = rng.randint(80, 220)
        col_var = (THORN_COL[0] + rng.randint(-8, 8),
                   THORN_COL[1] + rng.randint(-5, 5),
                   THORN_COL[2] + rng.randint(-4, 4))
        draw_thorn_branch(draw, base_x, base_y, ang, ln, 0, col_var, 4)

    # Right grove — thorn branches from right edge
    for _ in range(rng.randint(8, 12)):
        base_x = W + rng.randint(-60, 30)
        base_y = rng.randint(200, 1800)
        ang = math.pi + rng.uniform(-0.6, 0.6)
        ln = rng.randint(80, 220)
        col_var = (THORN_COL[0] + rng.randint(-8, 8),
                   THORN_COL[1] + rng.randint(-5, 5),
                   THORN_COL[2] + rng.randint(-4, 4))
        draw_thorn_branch(draw, base_x, base_y, ang, ln, 0, col_var, 4)

    # ── The Thorn Path (perspective path receding into the grove) ──
    path_top_y = 800
    path_bot_y = 1700
    path_top_w = 120
    path_bot_w = 600

    path_col = (30, 20, 15)
    for py in range(path_top_y, path_bot_y, 4):
        t = (py - path_top_y) / (path_bot_y - path_top_y)
        hw = int(path_top_w + (path_bot_w - path_top_w) * t)
        cx = W // 2
        draw.line((cx - hw, py, cx + hw, py), fill=(path_col[0] + int(8 * t),
                                                     path_col[1] + int(5 * t),
                                                     path_col[2] + int(3 * t), 200))

    # Path edge lines (thorn roots along path)
    for side in (-1, 1):
        for _ in range(rng.randint(15, 25)):
            t_frac = rng.uniform(0.1, 0.95)
            py = int(path_top_y + (path_bot_y - path_top_y) * t_frac)
            hw = int(path_top_w + (path_bot_w - path_top_w) * t_frac)
            px = W // 2 + side * hw + rng.randint(0, 20)
            root_len = rng.randint(15, 60)
            root_angle = math.pi * (0.5 + side * 0.3) + rng.uniform(-0.5, 0.5)
            rx = int(px + math.cos(root_angle) * root_len)
            ry = int(py + math.sin(root_angle) * root_len)
            draw.line((px, py, rx, ry), fill=(THORN_COL[0] + 10, THORN_COL[1] + 5, THORN_COL[2] + 3, 180), width=rng.randint(1, 3))

    # ── Bramble Kest silhouette (small figure on the path) ─────────
    fig_x = W // 2 + rng.randint(-15, 15)
    fig_y = 1250

    # Body
    draw.ellipse((fig_x - 14, fig_y - 55, fig_x + 14, fig_y), fill=(8, 6, 4, 230))
    # Head
    draw.ellipse((fig_x - 10, fig_y - 78, fig_x + 10, fig_y - 55), fill=(8, 6, 4, 230))
    # Shoulders / cloak
    draw.polygon([(fig_x - 18, fig_y - 48), (fig_x + 18, fig_y - 48),
                  (fig_x + 28, fig_y - 20), (fig_x + 22, fig_y + 5),
                  (fig_x - 22, fig_y + 5), (fig_x - 28, fig_y - 20)],
                 fill=(8, 6, 4, 230))
    # Herbalist's staff
    staff_x = fig_x + 20
    draw.line((staff_x, fig_y - 55, staff_x, fig_y + 30), fill=(45, 25, 10, 220), width=3)
    # Staff top — a small amber glow (herbal remedy)
    draw.ellipse((staff_x - 6, fig_y - 65, staff_x + 6, fig_y - 53),
                 fill=(AMBER_COL[0], AMBER_COL[1], AMBER_COL[2], 100))

    # ── Marrow the Wyrd-Woman (smaller, more stooped, near bottom) ─
    marrow_x = W // 2 - rng.randint(120, 180)
    marrow_y = 1480
    # Stooped figure
    draw.ellipse((marrow_x - 10, marrow_y - 38, marrow_x + 10, marrow_y), fill=(10, 7, 5, 220))
    draw.ellipse((marrow_x - 7, marrow_y - 52, marrow_x + 7, marrow_y - 38), fill=(10, 7, 5, 220))
    # Wyrd-woman's shawl
    draw.polygon([(marrow_x - 16, marrow_y - 35), (marrow_x + 16, marrow_y - 35),
                  (marrow_x + 22, marrow_y + 5), (marrow_x - 22, marrow_y + 5)],
                 fill=(12, 8, 6, 220))
    # Her gnarled walking stick
    draw.line((marrow_x + 12, marrow_y - 35, marrow_x + 18, marrow_y + 15),
              fill=(35, 18, 8, 210), width=3)

    # ── Sorrow (mute daughter, small, trailing behind) ─────────────
    sorrow_x = W // 2 + rng.randint(100, 150)
    sorrow_y = 1400
    draw.ellipse((sorrow_x - 8, sorrow_y - 32, sorrow_x + 8, sorrow_y), fill=(8, 6, 5, 210))
    draw.ellipse((sorrow_x - 6, sorrow_y - 44, sorrow_x + 6, sorrow_y - 32), fill=(8, 6, 5, 210))

    # ── Whispering Tongues (floating glyph-like motes) ─────────────
    # These represent the children's tongues — floating, twisted symbols
    for _ in range(rng.randint(60, 90)):
        tx = rng.randint(100, W - 100)
        ty = rng.randint(50, 1100)
        # Avoid the moon
        if math.hypot(tx - moon_cx, ty - moon_cy) < moon_r + 30:
            continue
        size = rng.uniform(3, 9)
        shape = rng.randint(0, 3)
        alpha = rng.randint(40, 120)
        col = (rng.randint(180, 230), rng.randint(140, 200), rng.randint(80, 140), alpha)
        if shape == 0:
            # floating dot
            draw.ellipse((tx - size, ty - size, tx + size, ty + size), fill=col)
        elif shape == 1:
            # twisted arc (like a tongue glyph)
            draw.arc((tx - size, ty - size, tx + size, ty + size),
                     0 + rng.randint(0, 180), 180 + rng.randint(0, 180),
                     fill=(*col[:3], alpha), width=max(1, int(size) // 2))
        elif shape == 2:
            # wispy line node
            draw.line((tx - size, ty, tx + size, ty + rng.randint(-int(size), int(size))),
                      fill=(*col[:3], alpha), width=max(1, int(size) // 2))
        else:
            # small cross or rune mark
            draw.line((tx - size, ty - size, tx + size, ty + size),
                      fill=(*col[:3], alpha // 2), width=1)
            draw.line((tx + size, ty - size * 0.5, tx - size, ty + size * 0.5),
                      fill=(*col[:3], alpha // 2), width=1)

    # ── Herbal wisps (curative green-amber threads winding through) ─
    for _ in range(rng.randint(12, 20)):
        wx = rng.randint(200, W - 200)
        wy = rng.randint(300, 1400)
        pts = []
        for step in range(rng.randint(6, 12)):
            px = wx + int(step * rng.uniform(12, 25))
            py = wy + int(math.sin(step * 0.7 + rng.random()) * rng.uniform(10, 30))
            if px > W:
                break
            pts.append((px, py))
        if len(pts) > 1:
            draw.line(pts, fill=(AMBER_COL[0], AMBER_COL[1], AMBER_COL[2], rng.randint(25, 60)),
                      width=rng.randint(1, 3))

    # ── Black-thorn arch overhead (upper frame) ────────────────────
    arch_pts = []
    for ax in range(0, W + 10, 10):
        t = ax / W
        # Arch shape bending from left edge to right edge across top
        arch_y = 40 + 240 * (1 - math.sin(t * math.pi)) + rng.randint(-8, 8)
        arch_pts.append((ax, int(arch_y)))
    draw.line(arch_pts, fill=(*THORN_COL, 180), width=6)
    # Thorns on arch
    for _ in range(rng.randint(12, 20)):
        ax = rng.randint(0, W)
        t = ax / W
        ay = 40 + 240 * (1 - math.sin(t * math.pi))
        ang = rng.uniform(0.5, 2.5)
        tl = rng.randint(10, 30)
        draw.line((ax, int(ay), ax + int(math.cos(ang) * tl), int(ay + math.sin(ang) * tl)),
                  fill=(*THORN_COL, 160), width=2)

    # ── Ground thistle / bramble at the bottom ─────────────────────
    for x in range(0, W, rng.randint(15, 40)):
        h = rng.randint(10, 35)
        col = (THORN_COL[0] + rng.randint(0, 10),
               THORN_COL[1] + rng.randint(0, 8),
               THORN_COL[2] + rng.randint(0, 5), 180)
        draw.line((x, 1760, x, 1760 - h), fill=col, width=rng.randint(1, 3))
        # Thistle leaves
        draw.line((x, 1760 - h, x - rng.randint(4, 10), 1760 - h + rng.randint(2, 6)),
                  fill=col, width=1)
        draw.line((x, 1760 - h, x + rng.randint(4, 10), 1760 - h + rng.randint(2, 6)),
                  fill=col, width=1)

    # ── Vignette (darken edges) ────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 100))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 100))

    # ── Blood droplets / curse motes (falling from moon) ──────────
    for _ in range(rng.randint(30, 45)):
        dx = moon_cx + rng.randint(-moon_r - 20, moon_r + 20)
        dy = moon_cy + rng.randint(moon_r + 10, moon_r + 250)
        dr = rng.uniform(1.5, 4.0)
        da = rng.randint(40, 110)
        dcol = (BLOOD_COL[0], BLOOD_COL[1] + rng.randint(-5, 5),
                BLOOD_COL[2] + rng.randint(-5, 5), da)
        draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=dcol)
        # Streak
        if rng.random() < 0.4:
            draw.line((dx, dy, dx, dy + rng.randint(8, 25)),
                      fill=(*dcol[:3], da // 2), width=1)

    # ── Save ───────────────────────────────────────────────────────
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
