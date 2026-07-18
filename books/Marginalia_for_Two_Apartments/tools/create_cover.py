#!/usr/bin/env python3
"""Cover: Marginalia for Two Apartments — A NASA orbital dynamicist and a Brooklyn baker swap apartments for a year through a house-exchange site, leaving each other increasingly personal notes and recipes hidden in the margins of books around the flat."""
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
rng.seed(1053126526)

# Colour palettes derived from the story
# Warm side (Leo the baker — amber, honey, flour)
# Cool side (Dr. Maya Chen — orbital navy, twilight indigo)
PALETTE_WARM_TOP = (210, 145, 65)
PALETTE_WARM_BOT = (110, 55, 22)
PALETTE_COOL_TOP = (25, 40, 80)
PALETTE_COOL_BOT = (8, 15, 38)
NOTE_COLORS = [
    (255, 245, 220, 205),   # cream
    (255, 232, 210, 200),   # warm parchment
    (222, 238, 255, 200),   # cool paper
    (242, 252, 237, 200),   # faint green
    (255, 220, 222, 200),   # blush
]


def _rotated_rect(cx, cy, w, h, deg):
    """Return the 4 corners of a rectangle centred at (cx,cy) rotated by *deg* degrees."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    hw, hh = w / 2, h / 2
    return [
        (cx - hw * c + hh * s, cy - hw * s - hh * c),
        (cx + hw * c + hh * s, cy + hw * s - hh * c),
        (cx + hw * c - hh * s, cy + hw * s + hh * c),
        (cx - hw * c - hh * s, cy - hw * s + hh * c),
    ]


def _rotated_line(draw, cx, cy, deg, lx, ly, length, fill, width):
    """Draw a short horizontal line at local offset (lx,ly) rotated by *deg*."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    x1 = cx + lx * c - ly * s
    y1 = cy + lx * s + ly * c
    x2 = cx + (lx + length) * c - ly * s
    y2 = cy + (lx + length) * s + ly * c
    draw.line((x1, y1, x2, y2), fill=fill, width=width)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ---- BACKGROUND: split gradient (warm left / cool right) ----
    warm_side = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(warm_side)
    for y in range(H):
        t = y / H
        r = int(PALETTE_WARM_TOP[0] + (PALETTE_WARM_BOT[0] - PALETTE_WARM_TOP[0]) * t)
        g = int(PALETTE_WARM_TOP[1] + (PALETTE_WARM_BOT[1] - PALETTE_WARM_TOP[1]) * t)
        b = int(PALETTE_WARM_TOP[2] + (PALETTE_WARM_BOT[2] - PALETTE_WARM_TOP[2]) * t)
        wd.line((0, y, W, y), fill=(r, g, b, 255))

    cool_side = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cool_side)
    for y in range(H):
        t = y / H
        r = int(PALETTE_COOL_TOP[0] + (PALETTE_COOL_BOT[0] - PALETTE_COOL_TOP[0]) * t)
        g = int(PALETTE_COOL_TOP[1] + (PALETTE_COOL_BOT[1] - PALETTE_COOL_TOP[1]) * t)
        b = int(PALETTE_COOL_TOP[2] + (PALETTE_COOL_BOT[2] - PALETTE_COOL_TOP[2]) * t)
        cd.line((0, y, W, y), fill=(r, g, b, 255))

    sigmoid_mask = Image.new("L", (W, H), 0)
    smd = ImageDraw.Draw(sigmoid_mask)
    for x in range(W):
        xf = x / W
        v = int(255 / (1 + math.exp(-12 * (xf - 0.5))))
        smd.line((x, 0, x, H), fill=v)

    img = Image.alpha_composite(
        warm_side,
        Image.composite(cool_side, Image.new("RGBA", (W, H), (0, 0, 0, 0)), sigmoid_mask),
    )
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- RIGHT THIRD: star field ----
    for _ in range(rng.randint(130, 210)):
        sx = rng.randint(W // 2, W - 15)
        sy = rng.randint(25, 900)
        sr = rng.uniform(0.4, 2.8)
        fade = (sx - W // 2) / (W // 2)
        sa = int(rng.randint(40, 200) * fade)
        draw.ellipse(
            [int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr)],
            fill=(200, 220, 255, sa),
        )

    # ---- RIGHT THIRD: orbital arcs (Dr. Maya's world) ----
    arc_palette = [
        (120, 185, 225),
        (100, 160, 215),
        (160, 210, 245),
        (80, 200, 255),
        (60, 140, 200),
    ]
    for _ in range(rng.randint(6, 10)):
        ax = rng.randint(W // 2 + 30, W - 80)
        ay = rng.randint(180, 800)
        rx = rng.randint(50, 240)
        ry = rng.randint(25, 170)
        start_a = rng.randint(0, 300)
        end_a = start_a + rng.randint(50, 200)
        col = rng.choice(arc_palette)
        draw.arc(
            [ax - rx, ay - ry, ax + rx, ay + ry],
            start_a,
            end_a,
            fill=(*col, rng.randint(25, 75)),
            width=rng.randint(1, 3),
        )

    # ---- LEFT THIRD: warm glow patches ----
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gld = ImageDraw.Draw(glow_layer)
    for _ in range(rng.randint(7, 13)):
        gx = rng.randint(30, W // 2 + 60)
        gy = rng.randint(80, 1350)
        gr = rng.randint(70, 300)
        gc = (rng.randint(200, 255), rng.randint(145, 200), rng.randint(55, 120))
        gld.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=(*gc, rng.randint(10, 32)))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(rng.randint(18, 42)))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- LEFT THIRD: flour / baking dust particles ----
    for _ in range(rng.randint(110, 190)):
        px = rng.randint(15, W // 2 + 120)
        py = rng.randint(60, 1650)
        pr = rng.uniform(1, 5)
        pa = rng.randint(22, 105)
        draw.ellipse(
            [int(px - pr), int(py - pr), int(px + pr), int(py + pr)],
            fill=(255, 248, 235, pa),
        )

    # ---- CENTRE: open book with marginalia ----
    bcx, bcy = W // 2, 985
    bw, bh = 360, 230
    hbw, hbh = bw // 2, bh // 2

    # left page — sinusoidal outer edge
    lt = []
    for i in range(hbw + 1):
        lt.append((bcx - hbw + i, bcy - hbh + int(14 * math.sin(i * math.pi / hbw))))
    lb = []
    for i in range(hbw, -1, -1):
        lb.append((bcx - hbw + i, bcy + hbh + int(14 * math.sin(i * math.pi / hbw))))
    draw.polygon(lt + lb, fill=(240, 225, 195, 235), outline=(165, 145, 105, 155), width=1)

    # right page
    rt = []
    for i in range(hbw + 1):
        rt.append((bcx + i, bcy - hbh + int(14 * math.sin((hbw - i) * math.pi / hbw))))
    rb = []
    for i in range(hbw, -1, -1):
        rb.append((bcx + i, bcy + hbh + int(14 * math.sin((hbw - i) * math.pi / hbw))))
    draw.polygon(rt + rb, fill=(248, 232, 200, 235), outline=(165, 145, 105, 155), width=1)

    # spine
    draw.rectangle(
        (bcx - 5, bcy - hbh - 6, bcx + 5, bcy + hbh + 6),
        fill=(145, 115, 75, 235),
    )
    draw.rectangle(
        (bcx - 1, bcy - hbh - 4, bcx + 1, bcy + hbh + 4),
        fill=(175, 145, 105, 200),
    )

    # printed body text (grey horizontal lines on pages)
    for side, xoff in ((-1, -hbw // 2), (1, hbw // 2)):
        for li in range(rng.randint(5, 8)):
            ly = bcy - hbh + 22 + li * 24
            lw = rng.randint(55, 135)
            draw.line(
                (bcx + xoff - lw // 2, ly, bcx + xoff + lw // 2, ly),
                fill=(125, 105, 75, rng.randint(80, 160)),
                width=rng.randint(1, 2),
            )

    # marginalia scribbles in the margins of the book
    for side, xoff in ((-1, -hbw // 2 - 28), (1, hbw // 2 + 10)):
        for si in range(rng.randint(2, 4)):
            sy = bcy - hbh + 18 + si * 32 + rng.randint(-4, 4)
            scx = bcx + xoff
            for seg in range(3):
                draw.line(
                    (
                        scx + seg * 14,
                        sy,
                        scx + seg * 14 + rng.randint(6, 16),
                        sy + rng.randint(-2, 2),
                    ),
                    fill=(175, 95, 75, rng.randint(90, 180)),
                    width=1,
                )

    # ---- FLOATING MARGINALIA NOTES (drifting between the two worlds) ----
    for _ in range(rng.randint(14, 22)):
        nx = rng.randint(180, 1420)
        ny = rng.randint(480, 1550)
        nw = rng.randint(44, 82)
        nh = rng.randint(52, 88)
        angle = rng.uniform(-32, 32)
        col = rng.choice(NOTE_COLORS)
        outline = (140, 130, 110, 110)

        pts = _rotated_rect(nx, ny, nw, nh, angle)
        draw.polygon(pts, fill=col, outline=outline)

        hcol = (80, 70, 60, rng.randint(55, 130))
        for hl in range(rng.randint(2, 4)):
            y_off = -nh // 2 + 12 + hl * 16 + rng.randint(-2, 2)
            x_start = -nw // 2 + 8
            h_len = rng.randint(14, nw - 22)
            _rotated_line(draw, nx, ny, angle, x_start, y_off, h_len, hcol, 1)

    # ---- CONNECTION THREADS (handwriting bridging the apartment divide) ----
    for _ in range(rng.randint(5, 9)):
        x1 = rng.randint(180, W // 2 - 40)
        y1 = rng.randint(550, 1450)
        x2 = rng.randint(W // 2 + 40, 1420)
        y2 = rng.randint(550, 1450)
        cpx = (x1 + x2) * 0.5 + rng.randint(-60, 60)
        cpy = min(y1, y2) - rng.randint(40, 120)
        tcol = (
            rng.randint(180, 220),
            rng.randint(160, 200),
            rng.randint(120, 160),
            rng.randint(25, 55),
        )
        # quadratic bezier approximation
        for si in range(28):
            t0 = si / 28
            t1 = (si + 1) / 28
            xa = (1 - t0) ** 2 * x1 + 2 * (1 - t0) * t0 * cpx + t0 ** 2 * x2
            ya = (1 - t0) ** 2 * y1 + 2 * (1 - t0) * t0 * cpy + t0 ** 2 * y2
            xb = (1 - t1) ** 2 * x1 + 2 * (1 - t1) * t1 * cpx + t1 ** 2 * x2
            yb = (1 - t1) ** 2 * y1 + 2 * (1 - t1) * t1 * cpy + t1 ** 2 * y2
            draw.line((int(xa), int(ya), int(xb), int(yb)), fill=tcol, width=1)

    # ---- SUBTLE VIGNETTE ----
    vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(vig)
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            vd.line((0, vy, vv, vy), fill=(0, 0, 0, 55))
            vd.line((W - vv, vy, W, vy), fill=(0, 0, 0, 55))
    img = Image.alpha_composite(img, vig)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- TITLE PANEL ----
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
