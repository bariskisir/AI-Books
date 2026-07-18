#!/usr/bin/env python3
"""Cover: The Night Market at the End of the World — a floating bazaar suspended across timelines, lantern-lit platforms against a rift-streaked twilight void."""

import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (10, 5, 35, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── TWILIGHT SKY GRADIENT ──────────────────────────────────────────────
    # Deep indigo at top, warm amber at market height, dark void at bottom
    for y in range(H):
        t = y / H
        if t < 0.30:
            p = t / 0.30
            r = int(10 + 10 * p)
            g = int(5 + 8 * p)
            b = int(35 + 20 * p)
        elif t < 0.50:
            p = (t - 0.30) / 0.20
            r = int(20 + 63 * p)
            g = int(13 + 42 * p)
            b = int(55 - 27 * p)
        elif t < 0.70:
            p = (t - 0.50) / 0.20
            r = int(83 - 55 * p)
            g = int(55 - 39 * p)
            b = int(28 - 10 * p)
        else:
            p = (t - 0.70) / 0.30
            r = int(28 - 22 * p)
            g = int(16 - 13 * p)
            b = int(18 - 15 * p)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # ── STARS ──────────────────────────────────────────────────────────────
    for _ in range(100):
        sx = random.randint(0, W)
        sy = random.randint(0, int(H * 0.28))
        sr = random.uniform(0.5, 2.5)
        sa = random.randint(60, 200)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(200, 200, 230, sa))

    # ── TIMELINE RIFTS ─────────────────────────────────────────────────────
    rift = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rift)
    rift_colors = [
        (200, 100, 50, 35),   # amber timeline
        (50, 200, 200, 30),   # cyan timeline
        (180, 60, 180, 25),   # magenta timeline
        (100, 200, 100, 20),  # green timeline
    ]
    # Wide diffuse rifts
    for _ in range(6):
        cx, cy = random.randint(80, W - 80), random.randint(100, 2000)
        rc = random.choice(rift_colors)
        pts = []
        x, y = cx, cy
        for _ in range(random.randint(6, 12)):
            x += random.randint(-35, 35)
            y += random.randint(25, 70)
            pts.append((x, y))
        rd.line(pts, fill=rc, width=random.randint(10, 30))
    # Brighter inner crack cores
    for _ in range(4):
        cx, cy = random.randint(80, W - 80), random.randint(100, 2000)
        rc = random.choice(rift_colors)
        inner = (min(255, rc[0] + 100), min(255, rc[1] + 100), min(255, rc[2] + 100), 80)
        pts = []
        x, y = cx, cy
        for _ in range(random.randint(5, 10)):
            x += random.randint(-15, 15)
            y += random.randint(20, 50)
            pts.append((x, y))
        rd.line(pts, fill=inner, width=random.randint(3, 8))
    rift = rift.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, rift)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── THE LUMEN (Zebu) ───────────────────────────────────────────────────
    lx, ly = W // 2, 280
    for r in range(80, 5, -5):
        alpha = max(0, 50 - (80 - r) * 2)
        draw.ellipse(
            (lx - r, ly - r, lx + r, ly + r),
            fill=(180, 220, 255, alpha),
        )
    # Light rays radiating from the Lumen
    for ang in range(0, 360, 20):
        rad = math.radians(ang)
        ex = lx + math.cos(rad) * 70
        ey = ly + math.sin(rad) * 70
        draw.line((lx, ly, ex, ey), fill=(180, 220, 255, 50), width=2)
    # Core
    draw.ellipse((lx - 18, ly - 18, lx + 18, ly + 18), fill=(200, 235, 255, 220))
    draw.ellipse((lx - 8, ly - 8, lx + 8, ly + 8), fill=(230, 245, 255, 255))

    # ── FLOATING MARKET PLATFORMS ──────────────────────────────────────────

    # Main platform — Mama Yemaya's stall
    mx, my = W // 2 + 10, 900
    mw = 520
    draw.ellipse((mx - mw // 2, my - 17, mx + mw // 2, my + 17), fill=(55, 38, 18, 230))

    # Red-and-gold striped canopy
    canopy_y = my - 65
    stripe_w = 30
    for i in range(mw // stripe_w):
        col = (180, 55, 35, 230) if i % 2 == 0 else (200, 160, 45, 230)
        sx = mx - mw // 2 + i * stripe_w
        draw.polygon(
            [
                (sx, canopy_y),
                (sx + stripe_w, canopy_y),
                (sx + stripe_w + 15, canopy_y + 60),
                (sx - 15, canopy_y + 60),
            ],
            fill=col,
        )
    # Scalloped canopy front edge
    for i in range(mw // 40):
        sx = mx - mw // 2 + i * 40
        draw.arc((sx - 10, canopy_y - 25, sx + 30, canopy_y + 15), 180, 360, fill=(180, 55, 35, 180), width=4)

    # Vendor table with magical artifacts
    draw.rectangle((mx - 100, my + 8, mx + 100, my + 38), fill=(75, 48, 20, 230))
    for _ in range(7):
        ax = mx + random.randint(-85, 85)
        ay = my + 5
        ac = (random.randint(100, 255), random.randint(80, 255), random.randint(100, 255), 200)
        draw.ellipse((ax - 7, ay - 7, ax + 7, ay + 7), fill=ac)
        inner = random.randint(4, 6)
        draw.ellipse((ax - inner, ay - inner, ax + inner, ay + inner), fill=(255, 255, 255, 180))

    # Upper-left platform
    draw.ellipse((180, 580, 450, 610), fill=(50, 35, 15, 220))
    draw.polygon([(210, 590), (290, 590), (300, 500), (220, 500)], fill=(55, 25, 55, 220))
    draw.ellipse((330, 570, 380, 605), fill=(80, 180, 255, 100))

    # Upper-right platform
    draw.ellipse((1150, 680, 1420, 710), fill=(50, 35, 15, 220))
    draw.polygon([(1180, 690), (1370, 690), (1350, 560), (1200, 560)], fill=(30, 55, 45, 220))

    # Lower-left platform
    draw.ellipse((100, 1250, 380, 1280), fill=(45, 30, 12, 220))

    # Lower-right platform
    draw.ellipse((1150, 1150, 1380, 1175), fill=(45, 30, 12, 220))

    # ── ROPE BRIDGES ───────────────────────────────────────────────────────
    bridge_pairs = [
        ((315, 595), (mx - 130, 882)),
        ((mx + 130, 882), (1285, 695)),
        ((240, 1265), (mx - 160, 890)),
        ((mx + 160, 890), (1265, 1162)),
    ]
    for (x1, y1), (x2, y2) in bridge_pairs:
        dx, dy = x2 - x1, y2 - y1
        dist = math.sqrt(dx * dx + dy * dy)
        if dist < 1:
            continue
        ox = -dy / dist * 8
        oy = dx / dist * 8
        # Two parallel ropes
        draw.line((x1 + ox, y1 + oy, x2 + ox, y2 + oy), fill=(100, 80, 50, 140), width=2)
        draw.line((x1 - ox, y1 - oy, x2 - ox, y2 - oy), fill=(100, 80, 50, 140), width=2)
        # Vertical slats
        for ti in range(1, 8):
            t = ti / 8
            px, py = x1 + dx * t, y1 + dy * t
            draw.line((px + ox, py + oy, px - ox, py - oy), fill=(100, 80, 50, 120), width=1)

    # ── FLOATING PAPER LANTERNS ────────────────────────────────────────────
    for _ in range(35):
        lx = random.randint(40, W - 40)
        ly = random.randint(300, 1700)
        lr = random.randint(8, 20)
        # Outer glow
        draw.ellipse(
            (lx - lr * 3, ly - lr * 3, lx + lr * 3, ly + lr * 3),
            fill=(255, 200, 80, random.randint(5, 15)),
        )
        # Lantern body
        draw.ellipse(
            (lx - lr, ly - lr, lx + lr, ly + lr),
            fill=(255, 180, 60, random.randint(100, 200)),
        )
        # Inner flame
        draw.ellipse(
            (lx - lr // 2, ly - lr // 2, lx + lr // 2, ly + lr // 2),
            fill=(255, 230, 150, random.randint(120, 200)),
        )
        # Hanging string
        draw.line((lx, ly + lr, lx, ly + lr + 12), fill=(150, 120, 80, 100), width=1)

    # ── REALITY COLLAPSE — fracture layer ──────────────────────────────────
    fracture = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fracture)

    # Jagged fracture lines
    for _ in range(25):
        fx = random.randint(0, W)
        fy = random.randint(1500, 2100)
        fpts = [(fx, fy)]
        for _ in range(random.randint(4, 8)):
            fx += random.randint(-25, 25)
            fy += random.randint(15, 40)
            fpts.append((fx, fy))
        fc = random.choice([(150, 80, 200, 50), (200, 100, 80, 40), (80, 150, 200, 35)])
        fd.line(fpts, fill=fc, width=random.randint(3, 8))

    # Energy leaking from fractures
    for _ in range(15):
        ex, ey = random.randint(0, W), random.randint(1600, 2200)
        ec = random.choice([(255, 200, 50, 70), (50, 200, 255, 70), (255, 100, 200, 50)])
        fd.ellipse((ex - 8, ey - 8, ex + 8, ey + 8), fill=ec)

    fracture = fracture.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, fracture)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── VIGNETTE — dark fade at bottom and edges ──────────────────────────
    for y in range(1800, H):
        t = (y - 1800) / 760
        a = int(180 * min(1, t))
        draw.line((0, y, W, y), fill=(0, 0, 0, a))
    for side in range(60):
        a = int(40 * (1 - side / 60))
        draw.line((side, 0, side, H), fill=(0, 0, 0, a))
        draw.line((W - side, 0, W - side, H), fill=(0, 0, 0, a))

    # ── TITLE PANEL ─────────────────────────────────────────────────────────
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
