#!/usr/bin/env python3
"""Cover: The Cartographer's Tongue — A disgraced cartographer maps a building that changes size depending on who looks at it, in a city that rearranges its streets each dawn."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Palette: spectral violet-to-bone horizon, phosphorescent green contours, amber windows ──
SKY_TOP = (25, 8, 35)         # deep indigo-violet night
SKY_BOT = (55, 40, 50)        # dusty bone-purple at horizon
BUILDING_BASE = (35, 20, 40)  # muted violet-gray
BUILDING_HIGH = (60, 50, 55)  # paler violet for shifted scale view
WINDOW_LIT = (240, 190, 80)   # warm amber glow
WINDOW_DIM = (180, 130, 50)   # dim amber
CONTOUR_LINE = (120, 200, 140)  # phosphorescent green
GRID_LINE = (180, 160, 120)    # faded parchment
STREET_COL = (50, 35, 40)      # street fragment fill
GOLD_ACCENT = (200, 160, 80)   # compass rose gold

rng = random.Random()
rng.seed(2911847562)


def _draw_contour_lines(draw, cx, cy, count):
    """Draw topographic contour lines warping around the impossible space."""
    for ci in range(count):
        base_r = 80 + ci * 28 + rng.randint(-5, 5)
        pts = []
        for ang_deg in range(0, 370, 5):
            ang = math.radians(ang_deg)
            wobble = math.sin(ang * 4 + ci) * 12 + math.sin(ang * 7 + ci * 2) * 6
            push = 25 * math.exp(-abs(math.sin(ang)) * 2) * (1 + math.sin(ang * 3 + ci) * 0.3)
            r = base_r + wobble + push
            px = cx + math.cos(ang) * r
            py = cy + math.sin(ang) * r * 0.7
            pts.append((px, py))
        alpha = max(15, 55 - ci * 3)
        draw.line(pts, fill=(*CONTOUR_LINE, alpha), width=1)


def _draw_building_face(draw, x, y, w, h, scale_id):
    """Draw one perspective view of the mutable building at a given scale."""
    col_bright = 10 + scale_id * 8
    col = (
        BUILDING_BASE[0] + col_bright,
        BUILDING_BASE[1] + col_bright // 2,
        BUILDING_BASE[2] + col_bright,
    )
    # Distorted rectilinear body with skewed sides
    draw.polygon([
        (x - w // 2, y - h),
        (x + w // 2, y - h),
        (x + w // 2 + scale_id * 15, y - h // 2),
        (x + w // 2, y),
        (x - w // 2, y),
        (x - w // 2 - scale_id * 10, y - h // 2),
    ], fill=(*col, 230), outline=(120, 100, 110, 80), width=1)

    # Windows at varying sizes per scale
    win_size = 8 + scale_id * 3
    for wy in range(y - h + 25, y - 15, 30 + scale_id * 5):
        for wx in range(x - w // 2 + 15, x + w // 2 - 10, 25 + scale_id * 4):
            if rng.random() < 0.6:
                lit = rng.random() < 0.5
                wcol = WINDOW_LIT if lit else WINDOW_DIM
                w_off = int(math.sin(wx * 0.05 + wy * 0.03) * 4)
                draw.rectangle(
                    (wx + w_off, wy, wx + win_size + w_off, wy + win_size),
                    fill=(*wcol, rng.randint(120, 220)),
                )


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*SKY_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Sky gradient: deep violet fading to dusty bone at the horizon ──
    for y in range(H):
        t = y / H
        phase = math.sin(t * math.pi * 0.7) if t < 0.7 else 1.0
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t + 15 * phase * (1 - t))
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t + 10 * phase * (1 - t))
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t + 20 * phase * (1 - t))
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    # ── 2. Perspective projection grid (cartographic vanishing-point lines) ──
    vx, vy = W // 2, 800  # vanishing point
    for gi in range(-20, 21):
        x = W // 2 + gi * 45
        gcol = (*GRID_LINE, rng.randint(10, 22))
        draw.line((x, 0, vx + gi * 3, vy), fill=gcol, width=1)
    for gy in range(0, vy + 80, 30):
        spread = 1 - (gy / vy) * 0.7 if vy > 0 else 0
        gcol = (*GRID_LINE, rng.randint(6, 16))
        draw.line(
            (vx - int(W * spread), gy, vx + int(W * spread), gy),
            fill=gcol, width=1,
        )

    # ── 3. Topographic contour lines mapping the impossible space ──
    _draw_contour_lines(draw, W // 2, 950, 14)

    # ── 4. The mutable building — three overlapping views at different scales ──
    # View 1: Tomas Liev's perspective — tall and narrow
    _draw_building_face(draw, W // 2 - 60, 1000, 220, 520, 0)

    # View 2: The Patron's perspective — wide and squat
    _draw_building_face(draw, W // 2 + 80, 1020, 360, 320, 2)

    # View 3: Inspector Moroz's perspective — medium, warped
    _draw_building_face(draw, W // 2 - 20, 980, 300, 420, 1)

    # Ghostly building outlines shimmering between states
    for gi in range(6):
        gx_off = rng.randint(-40, 40)
        gy_off = rng.randint(-20, 20)
        gw = rng.randint(250, 400)
        gh = rng.randint(350, 550)
        gcol = (
            100 + rng.randint(-20, 20),
            80 + rng.randint(-20, 20),
            110 + rng.randint(-20, 20),
            15,
        )
        draw.polygon([
            (W // 2 + gx_off - gw // 2, 1000 + gy_off - gh),
            (W // 2 + gx_off + gw // 2, 1000 + gy_off - gh),
            (W // 2 + gx_off + gw // 2 + 20, 1000 + gy_off),
            (W // 2 + gx_off + gw // 2, 1000 + gy_off),
            (W // 2 + gx_off - gw // 2, 1000 + gy_off),
            (W // 2 + gx_off - gw // 2 - 20, 1000 + gy_off - gh // 2),
        ], fill=gcol, outline=(140, 120, 150, 8), width=1)

    # ── 5. Floating street fragments (city rearranging its streets at dawn) ──
    for _ in range(8):
        sx = rng.randint(50, W - 50)
        sy = rng.randint(400, 1700)
        sw = rng.randint(60, 180)
        sh = rng.randint(8, 20)
        rot_deg = rng.uniform(-9, 9)

        frag = Image.new("RGBA", (sw + 20, sh + 10), (0, 0, 0, 0))
        fd = ImageDraw.Draw(frag)
        fd.rectangle((10, 0, 10 + sw, sh), fill=(*STREET_COL, 200), outline=(*GOLD_ACCENT, 60), width=1)
        # Cobblestone lines
        for cx_ in range(10, 10 + sw, rng.randint(8, 16)):
            fd.line((cx_, 0, cx_, sh), fill=(60, 45, 50, 60), width=1)
        for cy_ in range(0, sh, 4):
            fd.line((10, cy_, 10 + sw, cy_), fill=(60, 45, 50, 40), width=1)

        frag = frag.rotate(rot_deg, expand=True, center=(sw // 2 + 10, sh // 2), resample=Image.BICUBIC)
        frag = frag.filter(ImageFilter.GaussianBlur(0.5))

        # Drop shadow
        shadow = Image.new("RGBA", frag.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.rectangle((2, 3, frag.width - 2, frag.height - 2), fill=(0, 0, 0, 80))
        shadow = shadow.filter(ImageFilter.GaussianBlur(3))
        img.paste(shadow, (sx - frag.width // 2 + 3, sy - frag.height // 2 + 3), shadow)
        img.paste(frag, (sx - frag.width // 2, sy - frag.height // 2), frag)

    # ── 6. Broken compass rose ──
    crx, cry = W - 200, 350
    # Outer ring (fragmented)
    for ang_deg in range(0, 360, 5):
        ang = math.radians(ang_deg)
        sr = 70 + 10 * math.sin(ang * 3)
        if rng.random() < 0.15:
            continue
        px = crx + math.cos(ang) * sr
        py = cry + math.sin(ang) * sr
        draw.ellipse((px - 2, py - 2, px + 2, py + 2), fill=(*GOLD_ACCENT, rng.randint(30, 70)))
    # Cardinal pointers
    for i, ang_deg in enumerate([0, 180, 90, 270]):
        if i == 3 or rng.random() < 0.3:
            continue
        ang = math.radians(ang_deg)
        tip_x = crx + math.cos(ang) * 90
        tip_y = cry + math.sin(ang) * 90
        bx1 = crx + math.cos(ang + 0.15) * 40
        by1 = cry + math.sin(ang + 0.15) * 40
        bx2 = crx + math.cos(ang - 0.15) * 40
        by2 = cry + math.sin(ang - 0.15) * 40
        draw.polygon([(tip_x, tip_y), (bx1, by1), (bx2, by2)],
                     fill=(*GOLD_ACCENT, 120), outline=(*GOLD_ACCENT, 60), width=1)

    # ── 7. Scattered parchment map fragments drifting upward ──
    for _ in range(12):
        fx = rng.randint(100, W - 100)
        fy = rng.randint(150, 1700)
        fw = rng.randint(30, 80)
        fh = rng.randint(20, 50)
        fcol = (
            180 + rng.randint(-20, 20),
            160 + rng.randint(-20, 20),
            120 + rng.randint(-20, 20),
            rng.randint(30, 70),
        )
        pts = [
            (fx, fy),
            (fx + fw, fy - rng.randint(5, 15)),
            (fx + fw + 5, fy + fh),
            (fx - rng.randint(3, 10), fy + fh + 5),
        ]
        draw.polygon(pts, fill=fcol, outline=(200, 180, 140, 40), width=1)
        # Tiny cartographic marks
        for _ in range(2):
            mx = fx + rng.randint(5, fw - 5)
            my = fy + rng.randint(5, fh - 5)
            draw.line((mx, my, mx + rng.randint(10, 25), my + rng.randint(-3, 3)),
                      fill=(100, 120, 80, rng.randint(30, 60)), width=1)
        if rng.random() < 0.5:
            ex1 = fx + rng.randint(5, fw - 5)
            ey1 = fy + rng.randint(5, fh - 5)
            ex2 = ex1 + rng.randint(3, 8)
            ey2 = ey1 + rng.randint(3, 8)
            draw.ellipse((ex1, ey1, ex2, ey2), fill=(200, 80, 60, rng.randint(40, 80)))

    # ── 8. Atmospheric haze layer ──
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(5):
        hx = rng.randint(0, W)
        hy = rng.randint(600, 1400)
        hr = rng.randint(200, 500)
        hd.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=(160, 140, 180, rng.randint(4, 12)))
    haze = haze.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. Dust motes / floating particles ──
    for _ in range(200):
        px = rng.randint(0, W)
        py = rng.randint(0, H - 200)
        pr = rng.uniform(0.5, 2.5)
        pa = rng.randint(10, 45)
        pb = rng.randint(180, 240)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(pb, pb - 20, pb - 40, pa))

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
