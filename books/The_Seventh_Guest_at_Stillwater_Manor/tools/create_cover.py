#!/usr/bin/env python3
"""Cover: The Seventh Guest at Stillwater Manor — Six strangers approach a remote Scottish manor through a stormy moor; a manuscript page pinned by a dagger dominates the foreground."""

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
rng.seed("seventh-guest-stillwater")

# ── Palette: stormy highland moor, aged parchment, blood, steel ──
SKY_TOP = (12, 14, 32)
SKY_MID = (28, 24, 38)
SKY_BOT = (42, 36, 40)
MOOR = (28, 26, 20)
HILL_FAR = (22, 20, 16)
MANOR_BODY = (8, 6, 10)
PARCHMENT = (215, 198, 170)
PARCHMENT_SHADOW = (155, 140, 115)
WAX = (155, 25, 20)
WAX_HIGH = (175, 35, 30)
BLOOD = (140, 18, 15)
STEEL = (185, 185, 190)
STEEL_DARK = (100, 100, 108)
HILT = (55, 38, 18)
MOON = (228, 220, 202)
MOON_GLOW = (200, 195, 180)
WINDOW_LIGHT = (215, 190, 125)
MIST = (165, 170, 180)
INK = (22, 18, 24)
GOLD = (170, 145, 85)
CLOUD = (40, 38, 46)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Stormy sky gradient ──
    for y in range(H):
        t = y / H
        if t < 0.35:
            u = t / 0.35
            r = int(SKY_TOP[0] + (SKY_MID[0] - SKY_TOP[0]) * u)
            g = int(SKY_TOP[1] + (SKY_MID[1] - SKY_TOP[1]) * u)
            b = int(SKY_TOP[2] + (SKY_MID[2] - SKY_TOP[2]) * u)
        elif t < 0.55:
            u = (t - 0.35) / 0.20
            r = int(SKY_MID[0] + (SKY_BOT[0] - SKY_MID[0]) * u)
            g = int(SKY_MID[1] + (SKY_BOT[1] - SKY_MID[1]) * u)
            b = int(SKY_MID[2] + (SKY_BOT[2] - SKY_MID[2]) * u)
        else:
            u = min(1.0, (t - 0.55) / 0.15)
            r = int(SKY_BOT[0] + (MOOR[0] - SKY_BOT[0]) * u)
            g = int(SKY_BOT[1] + (MOOR[1] - SKY_BOT[1]) * u)
            b = int(SKY_BOT[2] + (MOOR[2] - SKY_BOT[2]) * u)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Moon behind storm clouds ──
    moon_cx, moon_cy = 1100, 220
    for r in range(280, 70, -10):
        a = max(2, 28 - (280 - r) // 10)
        draw.ellipse((moon_cx - r, moon_cy - r, moon_cx + r, moon_cy + r), fill=(*MOON_GLOW, a))
    draw.ellipse((moon_cx - 70, moon_cy - 70, moon_cx + 70, moon_cy + 70), fill=MOON)
    # Storm clouds drifting across moon
    for _ in range(10):
        cx = rng.randint(moon_cx - 200, moon_cx + 200)
        cy = rng.randint(moon_cy - 80, moon_cy + 80)
        cw = rng.randint(60, 240)
        ch = rng.randint(12, 40)
        draw.ellipse((cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2), fill=(*CLOUD, rng.randint(40, 90)))

    # ── 3. Distant hills (two layers) ──
    for layer_idx, (base_y, amp, freq, blur_r) in enumerate([
        (int(H * 0.52), 55, 0.018, 4),
        (int(H * 0.56), 40, 0.030, 2),
    ]):
        hl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        hd = ImageDraw.Draw(hl)
        col = HILL_FAR if layer_idx == 0 else MOOR
        for x in range(0, W, 2):
            h = int(amp * (0.6 + 0.4 * math.sin(x * freq * 0.7))
                    * (0.5 + 0.5 * math.sin(x * freq * 3.1 + 0.5)))
            hd.line((x, base_y - h, x, base_y), fill=(*col, 220))
        hl = hl.filter(ImageFilter.GaussianBlur(blur_r))
        img = Image.alpha_composite(img, hl)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 4. Manor silhouette ──
    mc, mg = W // 2, int(H * 0.58)
    mt = mg - 220
    ml = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(ml)
    # Main building
    md.rectangle((mc - 130, mt + 50, mc + 130, mg), fill=MANOR_BODY)
    md.polygon([(mc - 145, mt + 50), (mc, mt - 8), (mc + 145, mt + 50)], fill=(6, 4, 8))
    # Left tower
    md.rectangle((mc - 190, mt + 10, mc - 140, mg), fill=MANOR_BODY)
    md.polygon([(mc - 200, mt + 10), (mc - 165, mt - 35), (mc - 130, mt + 10)], fill=(6, 4, 8))
    # Right tower
    md.rectangle((mc + 140, mt + 10, mc + 190, mg), fill=MANOR_BODY)
    md.polygon([(mc + 130, mt + 10), (mc + 165, mt - 35), (mc + 200, mt + 10)], fill=(6, 4, 8))
    # Center turret
    md.rectangle((mc - 25, mt - 35, mc + 25, mt), fill=MANOR_BODY)
    md.polygon([(mc - 35, mt - 35), (mc, mt - 65), (mc + 35, mt - 35)], fill=(6, 4, 8))
    # Lit windows
    for wx, wy in [(mc - 85, mt + 80), (mc + 45, mt + 80),
                   (mc - 85, mt + 160), (mc + 45, mt + 160),
                   (mc - 170, mt + 80), (mc + 155, mt + 80),
                   (mc - 170, mt + 150), (mc + 155, mt + 150)]:
        wa = rng.randint(100, 160)
        md.rectangle((wx, wy, wx + 18, wy + 26), fill=(*WINDOW_LIGHT, wa))
        md.rectangle((wx + 2, wy + 2, wx + 16, wy + 24), fill=(*WINDOW_LIGHT, wa + 30))
    img = Image.alpha_composite(img, ml)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 5. Moorland ground texture ──
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gl)
    for _ in range(250):
        gx = rng.randint(0, W)
        gy = rng.randint(int(H * 0.50), int(H * 0.82))
        glen = rng.randint(4, 16)
        gc = (rng.randint(18, 42), rng.randint(16, 34), rng.randint(12, 26))
        gd.line((gx, gy, gx + glen, gy - rng.randint(0, 4)), fill=(*gc, rng.randint(30, 80)), width=1)
    img = Image.alpha_composite(img, gl)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 6. Six guest silhouettes on winding path ──
    figures = [
        (mc - 30, int(H * 0.63), 14),
        (mc - 10, int(H * 0.66), 16),
        (mc + 20, int(H * 0.69), 15),
        (mc - 25, int(H * 0.72), 18),
        (mc + 35, int(H * 0.75), 17),
        (mc + 60, int(H * 0.78), 13),
    ]
    for fx, fy, fh in figures:
        fc = (rng.randint(4, 14), rng.randint(3, 12), rng.randint(5, 16))
        # Head
        draw.ellipse((fx - 3, fy - fh, fx + 3, fy - fh + 7), fill=(*fc, 220))
        # Body
        draw.rectangle((fx - 4, fy - fh + 7, fx + 4, fy - 1), fill=(*fc, 220))
        # Coat/skirt
        draw.polygon([
            (fx - 6, fy - 6), (fx + 6, fy - 6),
            (fx + 8, fy), (fx - 8, fy),
        ], fill=(*fc, 200))

    # ── 7. Atmospheric fog ──
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    fd.ellipse((-200, int(H * 0.42), W + 200, int(H * 0.50)), fill=(*MIST, 18))
    fd.ellipse((mc - 400, int(H * 0.50), mc + 400, int(H * 0.56)), fill=(*MIST, 14))
    fog = fog.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, fog)

    # ── 8. Foreground manuscript page (torn edges, aged) ──
    pl, pr = 200, 1400
    pt, pb = 1240, 1740

    pg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(pg)

    # Build torn-edge polygon
    pts = [(pl + rng.randint(-10, 15), pt + rng.randint(-5, 15))]
    for x in range(pl + 30, pr - 20, 10):
        pts.append((x, pt + rng.randint(-8, 12)))
    pts.append((pr + rng.randint(-15, 10), pt + rng.randint(-5, 15)))
    for y in range(pt + 30, pb - 20, 10):
        pts.append((pr + rng.randint(-8, 8), y))
    pts.append((pr + rng.randint(-10, 15), pb + rng.randint(-8, 8)))
    for x in range(pr - 30, pl + 20, -10):
        pts.append((x, pb + rng.randint(-8, 12)))
    pts.append((pl + rng.randint(-15, 10), pb + rng.randint(-8, 8)))
    for y in range(pb - 30, pt + 20, -10):
        pts.append((pl + rng.randint(-8, 8), y))

    # Shadow offset
    sdw = [(p[0] + 6, p[1] + 6) for p in pts]
    pd.polygon(sdw, fill=(*PARCHMENT_SHADOW, 150))
    pd.polygon(pts, fill=PARCHMENT)
    img = Image.alpha_composite(img, pg)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. Handwriting lines (simulated scribbled text) ──
    lx, rx = pl + 45, pr - 45
    ty, by_text = pt + 35, pb - 35
    ypos = ty
    while ypos < by_text:
        indent = 15 if (ypos - ty > 40 and rng.random() < 0.22) else 0
        x = lx + indent
        maxw = rx - x - rng.randint(15, 40)
        sx = x
        while sx < x + maxw:
            seg = rng.randint(8, 22)
            if sx + seg > x + maxw:
                seg = x + maxw - sx
            sy = ypos + rng.randint(-2, 3)
            ey = ypos + rng.randint(-2, 3)
            ink_d = rng.randint(18, 38)
            draw.line((sx, sy, sx + seg, ey),
                      fill=(ink_d, ink_d - 4, ink_d + 3, rng.randint(180, 240)),
                      width=rng.randint(1, 2))
            sx += seg
        # Occasional ink blot
        if rng.random() < 0.06:
            bx = lx + rng.randint(20, rx - lx - 20)
            by_blot = ypos + rng.randint(-3, 3)
            for br in range(5, 1, -1):
                draw.ellipse((bx - br, by_blot - br, bx + br, by_blot + br),
                             fill=(35, 30, 32, rng.randint(80, 160)))
        ypos += rng.randint(15, 22)
        if rng.random() < 0.12:
            ypos += rng.randint(6, 12)

    # ── 10. Dagger pinning the page ──
    dx0, dy0 = W // 2, pt - 25
    db = pt + 55
    # Blade shadow
    draw.polygon([(dx0 - 9, db + 3), (dx0, dy0 - 17), (dx0 + 9, db + 3)],
                 fill=(80, 80, 85, 100))
    # Blade
    draw.polygon([(dx0 - 6, db), (dx0, dy0), (dx0 + 6, db)], fill=STEEL)
    draw.line((dx0 - 2, dy0 + 10, dx0 - 2, db - 5), fill=(215, 215, 220, 160), width=1)
    draw.polygon([(dx0 - 2, dy0 + 5), (dx0, dy0 - 3), (dx0 + 2, dy0 + 5)], fill=STEEL)
    # Hilt / handle
    draw.rectangle((dx0 - 8, dy0 - 28, dx0 + 8, dy0 + 3), fill=HILT)
    # Crossguard
    draw.rectangle((dx0 - 20, dy0 - 4, dx0 + 20, dy0 + 2), fill=STEEL_DARK)
    draw.rectangle((dx0 - 18, dy0 - 2, dx0 + 18, dy0), fill=(*GOLD, 180))
    # Pommel
    draw.ellipse((dx0 - 6, dy0 - 36, dx0 + 6, dy0 - 28), fill=(*GOLD, 220))
    # Grip wrap lines
    for wy in range(dy0 - 24, dy0, 5):
        draw.line((dx0 - 7, wy, dx0 + 7, wy + 2), fill=(40, 25, 10, 150), width=1)

    # ── 11. Wax seal ──
    sc, sy = W // 2 + 200, pb - 45
    sr = 26
    draw.ellipse((sc - sr + 3, sy - sr + 3, sc + sr + 3, sy + sr + 3),
                 fill=(70, 12, 8, 90))
    draw.ellipse((sc - sr, sy - sr, sc + sr, sy + sr), fill=WAX)
    draw.ellipse((sc - sr + 3, sy - sr + 3, sc + sr - 3, sy + sr - 3), fill=WAX_HIGH)
    # Pressed emblem (radial lines)
    for a in range(0, 360, 20):
        ra = math.radians(a)
        draw.line((
            sc + math.cos(ra) * (sr - 5), sy + math.sin(ra) * (sr - 5),
            sc + math.cos(ra) * (sr - 12), sy + math.sin(ra) * (sr - 12),
        ), fill=(130, 15, 12, 160), width=2)
    draw.ellipse((sc - 4, sy - 4, sc + 4, sy + 4), fill=(140, 18, 15, 220))

    # ── 12. Blood-red accents (drips and spatter) ──
    for _ in range(4):
        bx0 = dx0 + rng.randint(-5, 5)
        by0 = db + rng.randint(3, 10)
        br0 = rng.randint(2, 5)
        draw.ellipse((bx0 - br0, by0 - br0, bx0 + br0, by0 + br0),
                     fill=(*BLOOD, rng.randint(160, 220)))
        if rng.random() < 0.4:
            draw.line((bx0, by0, bx0 + rng.randint(-2, 2), by0 + rng.randint(10, 20)),
                      fill=(*BLOOD, rng.randint(100, 160)), width=2)
    for _ in range(8):
        sx0 = dx0 + rng.randint(-25, 25)
        sy0 = pt + rng.randint(8, 35)
        sr0 = rng.randint(1, 3)
        draw.ellipse((sx0 - sr0, sy0 - sr0, sx0 + sr0, sy0 + sr0),
                     fill=(*BLOOD, rng.randint(140, 200)))

    # ── 13. Subtle vignette ──
    vg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vg)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vw = int(70 * max(0, 1 - vt))
        if vw > 0:
            vd.line((0, vy, vw, vy), fill=(0, 0, 0, 110))
            vd.line((W - vw, vy, W, vy), fill=(0, 0, 0, 110))
    img = Image.alpha_composite(img, vg)

    # ── 14. Rain streaks (upper portion) ──
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(120):
        rx = rng.randint(0, W)
        ry = rng.randint(0, int(H * 0.55))
        rlen = rng.randint(8, 25)
        draw.line((rx, ry, rx - 2, ry + rlen),
                  fill=(180, 185, 195, rng.randint(12, 30)), width=1)

    # ── 15. Save ──
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
