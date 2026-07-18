#!/usr/bin/env python3
"""Cover: Far Gardens We Never Reach — Three generations of Ghanaian-British women confront what was lost and what was hidden when the family matriarch's funeral unearths a love letter written in 1967 to a man none of them knew existed."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Warm Ghana earth (terracotta/amber) at bottom → cool London slate at top
CR = (160, 92, 48)
CL = (58, 72, 98)

rng = random.Random()
rng.seed(973165248)

USE_PALETTE = [
    (200, 142, 62),   # gold
    (180, 102, 42),   # amber
    (142, 62, 36),    # terracotta
    (62, 78, 102),    # slate
    (92, 72, 52),     # umber
]


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (58, 72, 98, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background: warm terracotta bottom → cool slate top
    for y in range(H):
        t = y / H
        r = int(CR[0] + (CL[0] - CR[0]) * t)
        g = int(CR[1] + (CL[1] - CR[1]) * t)
        b = int(CR[2] + (CL[2] - CR[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Vignette
    for vy in range(H):
        vt = 1 - abs(vy - H//2) / (H//2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # === THREE WOMEN SILHOUETTES (Grace, Effie, Yaa — three generations) ===
    # Each figure is a stylized female silhouette with headwrap, shoulders, and full-length dress.
    # Grace (grandmother) is tallest and farthest back; Effie (mother) is mid; Yaa (daughter) is smallest, forward.
    fig_base = 1580
    figures = [
        # (cx, scale, y_off, r, g, b)
        (W // 2 - 140, 1.0,   0,  28, 22, 34),   # Grace
        (W // 2 + 80,  0.80, 40,  36, 28, 42),   # Effie
        (W // 2 - 30,  0.62, 70,  42, 34, 50),   # Yaa
    ]

    for cx, sc, yoff, fr, fg, fb in figures:
        base_y = fig_base + yoff
        hh = int(380 * sc)          # full height from top of head
        hr = int(30 * sc)           # head radius
        nw = int(14 * sc)           # neck width
        shw = int(72 * sc)          # shoulder half-width
        hw = int(56 * sc)           # hip half-width

        head_top = base_y - hh

        # Headwrap (gele) — larger dome on top of head
        wrap_top = head_top - int(22 * sc)
        draw.ellipse((cx - hr - int(10 * sc), wrap_top, cx + hr + int(10 * sc), head_top + hr),
                     fill=(fr + 12, fg + 8, fb + 4, 220))
        # Head
        draw.ellipse((cx - hr, head_top, cx + hr, head_top + hr * 2),
                     fill=(fr, fg, fb, 210))
        # Neck
        neck_top = head_top + hr * 2
        draw.rectangle((cx - nw // 2, neck_top, cx + nw // 2, neck_top + int(18 * sc)),
                       fill=(fr - 4, fg - 4, fb - 4, 210))
        # Shoulders & torso (flowing dress silhouette)
        shoulder_y = neck_top + int(18 * sc)
        draw.polygon([
            (cx - shw, shoulder_y + int(24 * sc)),
            (cx - shw + int(10 * sc), shoulder_y),
            (cx + shw - int(10 * sc), shoulder_y),
            (cx + shw, shoulder_y + int(24 * sc)),
        ], fill=(fr, fg, fb, 200))
        # Dress — full-length flowing skirt
        dress_top = shoulder_y
        draw.polygon([
            (cx - shw + int(8 * sc), dress_top),
            (cx + shw - int(8 * sc), dress_top),
            (cx + hw + int(20 * sc), base_y + int(10 * sc)),
            (cx - hw - int(20 * sc), base_y + int(10 * sc)),
        ], fill=(fr, fg, fb, 200))
        # Subtle kente-pattern stripes on the dress
        for stripe_y in range(dress_top + int(40 * sc), base_y, int(28 * sc)):
            sl = int(sc * rng.randint(20, 50))
            draw.line((cx - sl, stripe_y, cx + sl, stripe_y),
                      fill=(fr + 30, fg + 20, fb + 10, 40), width=2)

    # === GLOWING LOVE LETTER ===
    lcx, lcy = W // 2 + 90, 780
    lw, lh = 240, 165

    # Soft golden glow behind letter
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((lcx - 200, lcy - 150, lcx + 200, lcy + 150),
               fill=(230, 190, 80, 28))
    glow = glow.filter(ImageFilter.GaussianBlur(35))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Envelope
    x1, y1 = lcx - lw // 2, lcy - lh // 2
    x2, y2 = lcx + lw // 2, lcy + lh // 2
    draw.rectangle((x1, y1, x2, y2), fill=(225, 205, 165, 210))
    draw.rectangle((x1, y1, x2, y2), outline=(175, 145, 95, 220), width=3)
    # Top flap
    draw.polygon([(x1, y1), (lcx, y1 - 35), (x2, y1)],
                 fill=(205, 180, 135, 210), outline=(175, 145, 95, 220))
    # Bottom fold
    draw.polygon([(x1, y2), (lcx, y2 + 28), (x2, y2)],
                 fill=(205, 180, 135, 210), outline=(175, 145, 95, 220))
    # Simulated handwritten lines on the envelope
    for li, llen in enumerate([120, 100, 140, 80, 60]):
        ly = y1 + 42 + li * 22
        if ly > y2 - 30:
            break
        draw.line((x1 + 22, ly, x1 + 22 + llen, ly), fill=(110, 85, 50, 140), width=2)
    # Wax seal (small heart) at bottom-center of envelope
    hx, hy = lcx, y2 - 22
    draw.ellipse((hx - 10, hy - 8, hx, hy + 4), fill=(190, 60, 50, 190))
    draw.ellipse((hx, hy - 8, hx + 10, hy + 4), fill=(190, 60, 50, 190))
    draw.polygon([(hx - 9, hy - 3), (hx + 9, hy - 3), (hx, hy + 14)],
                 fill=(190, 60, 50, 190))

    # === LONDON → ACCRA MAP ARC ===
    # A subtle dashed arc connecting two endpoints
    ldn_x, ldn_y = 280, 320
    acc_x, acc_y = 1300, 1520
    ctrl_x, ctrl_y = W // 2, 600

    steps = 80
    arc_pts = []
    for i in range(steps + 1):
        t = i / steps
        cx = (1 - t) ** 2 * ldn_x + 2 * (1 - t) * t * ctrl_x + t ** 2 * acc_x
        cy = (1 - t) ** 2 * ldn_y + 2 * (1 - t) * t * ctrl_y + t ** 2 * acc_y
        arc_pts.append((cx, cy))
    # Draw dashed
    for i in range(0, len(arc_pts) - 1, 3):
        draw.line((arc_pts[i], arc_pts[i + 1]), fill=(185, 165, 105, 45), width=2)
    # Endpoint dots
    draw.ellipse((ldn_x - 7, ldn_y - 7, ldn_x + 7, ldn_y + 7), fill=(185, 170, 130, 110))
    draw.ellipse((acc_x - 7, acc_y - 7, acc_x + 7, acc_y + 7), fill=(185, 170, 130, 110))
    # "London" small label marker (tiny cross)
    draw.line((ldn_x - 14, ldn_y, ldn_x + 14, ldn_y), fill=(185, 170, 130, 80), width=1)
    draw.line((ldn_x, ldn_y - 14, ldn_x, ldn_y + 14), fill=(185, 170, 130, 80), width=1)

    # === ADINKRA-INSPIRED BORDER MOTIFS ===
    # Subtle repeating diamond/chevron band at top
    for bx in range(0, W + 40, 50):
        by = 55
        parity = (bx // 50) % 3
        if parity == 0:
            # Diamond
            draw.polygon([
                (bx + 25, by - 12), (bx + 38, by),
                (bx + 25, by + 12), (bx + 12, by),
            ], outline=(210, 175, 105, 45), width=1)
        elif parity == 1:
            # Chevron
            draw.line((bx + 12, by + 8, bx + 25, by - 8), fill=(210, 175, 105, 45), width=1)
            draw.line((bx + 25, by - 8, bx + 38, by + 8), fill=(210, 175, 105, 45), width=1)
        else:
            # Dot
            draw.ellipse((bx + 20, by - 4, bx + 30, by + 4), fill=(210, 175, 105, 45))

    # Side ornamental lines
    for sx in (45, W - 45):
        for sy in range(120, 1680, 40):
            phase = (sy // 40) % 3
            if phase == 0:
                draw.line((sx, sy, sx + 18, sy - 6), fill=(200, 165, 100, 18), width=1)
            elif phase == 1:
                draw.line((sx + 6, sy - 4, sx + 18, sy + 4), fill=(200, 165, 100, 18), width=1)
            else:
                draw.ellipse((sx + 5, sy - 3, sx + 15, sy + 3), fill=(200, 165, 100, 22))

    # === THREE GOLDEN THREADS (invisible family bonds spanning generations) ===
    for t_idx in range(3):
        t_pts = []
        for tx in range(100, W - 100, 15):
            wave = math.sin(tx * 0.012 + t_idx * 2.3) * 35 \
                   + math.sin(tx * 0.028 + t_idx * 1.7) * 14
            ty = 1350 + wave + t_idx * 55
            t_pts.append((tx, ty))
        draw.line(t_pts, fill=(205, 175, 85, 38), width=2)

    # === WARM MEMORY PARTICLES (golden dust motes / fireflies) ===
    for _ in range(rng.randint(50, 80)):
        px = rng.randint(40, W - 40)
        py = rng.randint(80, 1650)
        pr = rng.randint(2, 7)
        pa = rng.randint(25, 110)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr),
                     fill=(225, 185, 85, pa))
        # Some get a diffuse outer halo
        if rng.random() < 0.2:
            draw.ellipse((px - pr * 4, py - pr * 4, px + pr * 4, py + pr * 4),
                         fill=(225, 185, 85, pa // 5))

    # === AGED PAPER TEXTURE PATCHES ===
    for _ in range(rng.randint(10, 18)):
        px = rng.randint(60, W - 60)
        py = rng.randint(150, 1550)
        pr = rng.randint(35, 100)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr),
                     fill=(205, 185, 135, rng.randint(4, 14)))

    # === FUNERAL WREATH / FLORAL MOTIF (subtle, low on the canvas) ===
    # A faint circular floral shape near the bottom, between the figures
    wx, wy = W // 2 - 60, 1680
    for ring in range(3):
        rr = 40 - ring * 10
        for a_deg in range(0, 360, 30):
            rad = math.radians(a_deg + ring * 15)
            fx = wx + math.cos(rad) * rr
            fy = wy + math.sin(rad) * rr * 0.7
            draw.ellipse((fx - 5, fy - 4, fx + 5, fy + 4),
                         fill=(180, 140, 90, rng.randint(20, 45)))

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
