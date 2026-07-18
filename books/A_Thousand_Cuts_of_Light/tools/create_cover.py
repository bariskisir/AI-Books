#!/usr/bin/env python3
"""Cover: A Thousand Cuts of Light — neural-noir: a neural-cracked ex-advertiser sees deadly subliminals hidden in the city's ambient data-layer."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Noir-indigo palette — cold, synthetic, urban night
BG_BOTTOM = (6, 4, 16)
BG_TOP = (22, 16, 50)
NEURAL_CYAN = (0, 200, 255)
SUBLIMINAL_AMBER = (255, 180, 30)
DATA_TEAL = (35, 130, 170)

rng = random.Random()
rng.seed(719283456)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # Base canvas — deep noir
    img = Image.new("RGBA", (W, H), (*BG_BOTTOM, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient: dark at bottom, lighter at top (inverted noir)
    for y in range(H):
        t = y / H
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Heavy vignette
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(80 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 120))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 120))

    # Ambient data-layer scanlines
    scan = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(scan)
    for sy in range(0, H, 3):
        sd.line((0, sy, W, sy), fill=(255, 255, 255, 5))
    scan = scan.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, scan)
    draw = ImageDraw.Draw(img, "RGBA")

    # Cascading data columns (vertical bars like unfurling data-streams)
    for cx in range(40, W - 40, rng.randint(16, 38)):
        col_len = rng.randint(60, H // 2)
        col_start = rng.randint(80, H - col_len - 300)
        col_alpha = rng.randint(5, 20)
        col_width = rng.randint(1, 3)
        draw.line((cx, col_start, cx, col_start + col_len), fill=(*DATA_TEAL, col_alpha), width=col_width)

    # Subliminal text fragments floating invisibly in the data-layer
    fragments = [
        "BUY", "OBEY", "SLEEP", "FORGET", "CONSUME", "WATCH",
        "ZARA", "DATA", "GHOST", "PAY", "NEURAL", "CRACK",
        "DIE", "WAKE", "SEE", "HIDE", "SIGNAL", "CUT",
        "LIGHT", "DREAM", "TRUST", "FEAR", "WANT", "NEED",
        "SUBMIT", "BELIEVE", "SPEND", "WORK",
    ]
    frag_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frag_layer)
    for f in fragments:
        fx = rng.randint(40, W - 120)
        fy = rng.randint(60, H - 450)
        if rng.random() < 0.18:
            # Highlighted subliminal — the ones Zara can see
            fc = (*SUBLIMINAL_AMBER, rng.randint(160, 230))
        else:
            # Faint background noise — invisible to most people
            fc = (rng.randint(100, 180), rng.randint(180, 230), rng.randint(210, 255), rng.randint(10, 35))
        fd.text((fx, fy), f, fill=fc)
    frag_layer = frag_layer.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, frag_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Zara Nkosi's silhouette in profile (face right)
    hx, hy = W // 3 - 40, H // 2 - 120
    profile_pts = [
        (hx - 30, hy + 200),    # neck back
        (hx - 30, hy + 90),     # back of skull
        (hx - 10, hy - 30),     # upper back
        (hx + 10, hy - 90),     # crown
        (hx + 50, hy - 100),    # top of head
        (hx + 90, hy - 80),     # forehead
        (hx + 115, hy - 50),    # brow ridge
        (hx + 120, hy - 30),    # bridge
        (hx + 135, hy - 10),    # nose tip
        (hx + 120, hy + 5),     # under nose
        (hx + 115, hy + 12),    # upper lip
        (hx + 108, hy + 22),    # mouth slit
        (hx + 115, hy + 32),    # lower lip
        (hx + 108, hy + 50),    # chin point
        (hx + 95, hy + 80),     # jaw slope
        (hx + 70, hy + 170),    # neck front
    ]
    draw.polygon(profile_pts, fill=(4, 3, 14, 235))

    # Neural glow tendrils radiating from the temple (the "crack" interface)
    tx, ty = hx + 70, hy - 35
    for angle_deg in range(-75, 80, 4):
        rad = math.radians(angle_deg)
        length = rng.randint(50, 280)
        ex = tx + math.cos(rad) * length
        ey = ty + math.sin(rad) * length
        alpha = rng.randint(15, 70)
        lw = rng.randint(1, 3)
        draw.line((tx, ty, ex, ey), fill=(*NEURAL_CYAN, alpha), width=lw)

    # Neural pulse rings (concentric ripples from the interface point)
    for ri in range(2, 12):
        radius = ri * 16
        alpha = max(0, 70 - ri * 6)
        outline_alpha = max(0, alpha // 2)
        draw.ellipse((tx - radius, ty - radius, tx + radius, ty + radius),
                      outline=(*NEURAL_CYAN, outline_alpha), width=1)

    # Bright pulse at temple
    for pr in range(8, 0, -1):
        pa = 120 - pr * 14
        draw.ellipse((tx - pr * 3, ty - pr * 3, tx + pr * 3, ty + pr * 3),
                      fill=(*NEURAL_CYAN, max(0, pa)))

    # Subliminal data-ripples: circular shockwaves where subliminals break through
    ripple_centers = [
        (W // 2 + 120, H // 2 - 200),
        (W - 180, H // 2 - 60),
        (W // 2 + 200, H // 2 + 180),
        (W - 100, H // 2 + 260),
        (W // 2 + 60, H // 2 + 80),
    ]
    for rx, ry in ripple_centers:
        for ri in range(1, 5):
            rr = ri * 25
            ra = max(0, 55 - ri * 12)
            draw.ellipse((rx - rr, ry - rr, rx + rr, ry + rr),
                          outline=(*SUBLIMINAL_AMBER, ra), width=2 if ri <= 2 else 1)
        draw.ellipse((rx - 5, ry - 5, rx + 5, ry + 5), fill=(*SUBLIMINAL_AMBER, 180))

    # Additional random ripple hotspots
    for _ in range(rng.randint(3, 6)):
        rx = rng.randint(W // 2 + 30, W - 80)
        ry = rng.randint(150, H - 350)
        outer_r = rng.randint(35, 100)
        ra = rng.randint(15, 45)
        draw.ellipse((rx - outer_r, ry - outer_r, rx + outer_r, ry + outer_r),
                      outline=(*SUBLIMINAL_AMBER, ra), width=2)
        draw.ellipse((rx - outer_r // 2, ry - outer_r // 2, rx + outer_r // 2, ry + outer_r // 2),
                      outline=(*SUBLIMINAL_AMBER, ra + 15), width=1)

    # Ambient data-layer particles
    for _ in range(300):
        px = rng.randint(0, W)
        py = rng.randint(0, H - 450)
        pr = rng.randint(1, 3)
        pa = rng.randint(5, 50)
        pc = rng.choice([NEURAL_CYAN, DATA_TEAL, SUBLIMINAL_AMBER])
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(*pc, pa))

    # Noir data-rain streaks
    for _ in range(100):
        sx = rng.randint(0, W)
        sy = rng.randint(0, H - 450)
        sl = rng.randint(15, 55)
        sw = rng.randint(1, 2)
        sa = rng.randint(6, 22)
        draw.line((sx, sy, sx, sy + sl), fill=(*DATA_TEAL, sa), width=sw)

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
