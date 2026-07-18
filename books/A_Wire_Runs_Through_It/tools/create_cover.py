#!/usr/bin/env python3
"""Cover: A Wire Runs Through It — post-collapse Detroit with neural data wire, ruined skyline, and memory fragments"""

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
rng.seed(1873995139)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Smog sky with Detroit rust horizon glow ──
    horizon_y = 1450
    for y in range(H):
        if y < horizon_y:
            t = 1 - y / horizon_y
            r = int(25 + 150 * (1 - t) * (1 - t))
            g = int(10 + 50 * (1 - t) * (1 - t))
            b = int(3 + 12 * (1 - t) * (1 - t))
            r += rng.randint(-5, 5)
            g += rng.randint(-3, 3)
            b += rng.randint(-2, 2)
            draw.line(
                (0, y, W, y),
                fill=(
                    max(0, min(255, r)),
                    max(0, min(255, g)),
                    max(0, min(255, b)),
                    255,
                ),
            )
        else:
            t = (y - horizon_y) / (H - horizon_y)
            r = int(15 + 20 * t)
            g = int(8 + 10 * t)
            b = int(4 + 5 * t)
            draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── 2. Ruined Detroit skyline (collapsed buildings with jagged tops) ──
    ruins = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ruins)
    for _ in range(rng.randint(18, 28)):
        bx = rng.randint(10, W - 10)
        bw = rng.randint(25, 140)
        bh = rng.randint(150, 600)
        base_y = horizon_y + rng.randint(-30, 80)
        top_y = base_y - bh
        col = (rng.randint(12, 28), rng.randint(6, 16), rng.randint(3, 10))
        if rng.random() < 0.7:
            pts = [(bx - bw // 2, base_y)]
            segments = rng.randint(3, 7)
            for seg in range(segments):
                sx = bx - bw // 2 + (bw * seg) // segments
                sy = top_y + rng.randint(-30, 80)
                pts.append((sx, sy))
            pts.append((bx + bw // 2, base_y))
            rd.polygon(pts, fill=(*col, 240))
        else:
            rd.rectangle(
                (bx - bw // 2, top_y, bx + bw // 2, base_y), fill=(*col, 240)
            )
    img = Image.alpha_composite(img, ruins)

    # ── 3. Neural wire (the "wire" — organic data stream through the sky) ──
    wire_pts = []
    for i in range(25):
        t = i / 24
        wx = int(
            50
            + t * (W - 100)
            + math.sin(t * math.pi * 3) * 200
            + math.sin(t * math.pi * 7) * 60
        )
        wy = int(
            horizon_y
            - t * (horizon_y - 80)
            + math.cos(t * math.pi * 2) * 100
        )
        wire_pts.append((wx, wy))

    for thickness, blur_r, alpha, col in [
        (20, 12, 25, (0, 180, 200)),
        (12, 6, 40, (0, 220, 240)),
        (5, 0, 120, (50, 255, 255)),
    ]:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(layer)
        for i in range(len(wire_pts) - 1):
            ld.line(
                (wire_pts[i], wire_pts[i + 1]),
                fill=(*col, alpha),
                width=thickness,
            )
        if blur_r > 0:
            layer = layer.filter(ImageFilter.GaussianBlur(blur_r))
        img = Image.alpha_composite(img, layer)

    # ── 4. Branching data tendrils (neural threads reaching into the city) ──
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(rng.randint(25, 45)):
        idx = rng.randint(0, len(wire_pts) - 2)
        sx, sy = wire_pts[idx]
        angle = rng.uniform(0, math.tau)
        length = rng.randint(30, 160)
        ex = sx + math.cos(angle) * length
        ey = sy + math.sin(angle) * length
        tcol = (
            rng.randint(0, 60),
            rng.randint(160, 255),
            rng.randint(180, 255),
        )
        draw.line(
            (sx, sy, ex, ey),
            fill=(*tcol, rng.randint(30, 100)),
            width=rng.randint(1, 2),
        )

    # ── 5. Memory fragments (data particles rising from dead implants) ──
    for _ in range(rng.randint(100, 180)):
        px = rng.randint(0, W)
        py = rng.randint(horizon_y - 600, horizon_y - 50)
        pr = rng.randint(1, 5)
        col_type = rng.random()
        if col_type < 0.4:
            pcol = (200, 220, 255, rng.randint(60, 180))  # pale blue memory
        elif col_type < 0.7:
            pcol = (255, 200, 150, rng.randint(40, 140))  # warm amber memory
        elif col_type < 0.9:
            pcol = (200, 150, 255, rng.randint(40, 120))  # corrupted memory
        else:
            pcol = (255, 60, 60, rng.randint(80, 200))  # warning signal
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr), fill=pcol
        )

    # ── 6. Rin Weaver silhouette (data archaeologist on rubble) ──
    fig_x = W // 2 + 180
    fig_y = horizon_y + 60

    # Rubble platform beneath the figure
    rubble = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rbd = ImageDraw.Draw(rubble)
    for _ in range(12):
        rx = fig_x + rng.randint(-60, 60)
        ry = fig_y + rng.randint(-10, 20)
        rs = rng.randint(10, 35)
        rbd.ellipse(
            (rx - rs, ry - rs, rx + rs, ry + rs),
            fill=(
                rng.randint(20, 40),
                rng.randint(10, 25),
                rng.randint(5, 15),
                200,
            ),
        )
    img = Image.alpha_composite(img, rubble)

    # Figure silhouette
    fig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fig)
    # Body
    fd.polygon(
        [
            (fig_x - 8, fig_y),
            (fig_x + 8, fig_y),
            (fig_x + 5, fig_y - 55),
            (fig_x - 5, fig_y - 55),
        ],
        fill=(0, 0, 0, 220),
    )
    # Head
    fd.ellipse(
        (fig_x - 9, fig_y - 68, fig_x + 9, fig_y - 54),
        fill=(0, 0, 0, 220),
    )
    # Right arm reaching toward the wire
    fd.line(
        (fig_x + 6, fig_y - 35, fig_x + 30, fig_y - 75),
        fill=(0, 0, 0, 220),
        width=5,
    )
    # Left arm at side
    fd.line(
        (fig_x - 6, fig_y - 35, fig_x - 20, fig_y - 25),
        fill=(0, 0, 0, 220),
        width=4,
    )
    # Data stream from hand toward the neural wire
    closest = min(
        wire_pts,
        key=lambda p: math.hypot(
            p[0] - (fig_x + 30), p[1] - (fig_y - 75)
        ),
    )
    fd.line(
        (fig_x + 30, fig_y - 75, closest[0], closest[1]),
        fill=(
            rng.randint(50, 150),
            rng.randint(200, 255),
            rng.randint(200, 255),
            rng.randint(40, 90),
        ),
        width=2,
    )
    img = Image.alpha_composite(img, fig)

    # ── 7. Countdown timer ring (the assassination weapon trigger) ──
    draw = ImageDraw.Draw(img, "RGBA")
    cx, cy = W // 2 - 100, 350
    ring_r = 130
    # Partial outer ring — only 3/4 complete (countdown nearly done)
    for deg in range(0, 275, 2):
        ang = math.radians(deg - 90)
        rx = cx + ring_r * math.cos(ang)
        ry = cy + ring_r * math.sin(ang)
        progress = deg / 270
        alpha = int(200 * (1 - progress * 0.7))
        gcol = max(30, int(80 - progress * 60))
        draw.ellipse(
            (rx - 4, ry - 4, rx + 4, ry + 4),
            fill=(255, gcol, gcol, alpha),
        )
    # Timer ticks around the ring
    for tick in range(24):
        ang = math.radians(tick * 15 - 90)
        if tick * 15 < 275:
            inner = ring_r - 18
            outer = ring_r + 8
            tx1 = cx + inner * math.cos(ang)
            ty1 = cy + inner * math.sin(ang)
            tx2 = cx + outer * math.cos(ang)
            ty2 = cy + outer * math.sin(ang)
            draw.line(
                (tx1, ty1, tx2, ty2),
                fill=(255, 50, 50, 140),
                width=2,
            )
    # Pulsing center of the ring
    for ri, ra in [(20, 40), (10, 80), (4, 160)]:
        draw.ellipse(
            (cx - ri, cy - ri, cx + ri, cy + ri),
            fill=(0, 200, 220, ra),
        )

    # ── 8. Atmospheric haze / pollution ──
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(40):
        hx = rng.randint(0, W)
        hy = rng.randint(0, horizon_y)
        hr = rng.randint(40, 160)
        hd.ellipse(
            (hx - hr, hy - hr, hx + hr, hy + hr),
            fill=(60, 25, 5, rng.randint(2, 8)),
        )
    haze = haze.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, haze)

    # ── 9. Ground debris / rubble field ──
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(rng.randint(30, 60)):
        dx = rng.randint(0, W)
        dy = rng.randint(horizon_y + 20, H)
        dr = rng.randint(2, 8)
        dcol = (
            rng.randint(10, 30),
            rng.randint(5, 18),
            rng.randint(3, 10),
        )
        draw.ellipse(
            (dx - dr, dy - dr, dx + dr, dy + dr),
            fill=(*dcol, rng.randint(100, 200)),
        )

    # Low ground fog layer
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fgd = ImageDraw.Draw(fog)
    for _ in range(10):
        fx = rng.randint(-100, W + 100)
        fy = rng.randint(horizon_y, H)
        fgd.ellipse(
            (fx - 300, fy - 30, fx + 300, fy + 30),
            fill=(40, 15, 5, rng.randint(5, 15)),
        )
    fog = fog.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, fog)

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
