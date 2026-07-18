#!/usr/bin/env python3
"""Cover: Ninth Orbit — A generation ship with a decaying orbit, its decaying orbital path glowing rust-orange as the maintenance crew uncovers the true purpose of exile."""

from __future__ import annotations
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

    rng = random.Random()
    rng.seed(892403716)

    img = Image.new("RGBA", (W, H), (5, 3, 8, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Deep-space gradient ─────────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(5 + 20 * t)
        g = int(3 + 8 * t)
        b = int(8 + 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Stars ───────────────────────────────────────────────────────
    for _ in range(rng.randint(140, 220)):
        sx = rng.randint(0, W)
        sy = rng.randint(0, 1800)
        sr = rng.uniform(0.5, 2.5)
        sa = rng.randint(40, 200)
        draw.ellipse(
            (int(sx - sr), int(sy - sr), int(sx + sr), int(sy + sr)),
            fill=(180, 200, 230, sa),
        )

    # ── Orbit Decay Ring ────────────────────────────────────────────
    # A broken elliptical orbital path crossing the composition diagonally.
    # Drawn in two passes: a blurred glow layer, then sharper debris segments.
    ring_cx, ring_cy = W // 2, 950
    ring_a, ring_b = 720, 300  # semi-axes

    # Pass 1: soft glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for deg in range(0, 360, 2):
        rad = math.radians(deg)
        ex = ring_cx + ring_a * math.cos(rad) * 0.95 - ring_b * math.sin(rad) * 0.31
        ey = ring_cy + ring_a * math.cos(rad) * 0.31 + ring_b * math.sin(rad) * 0.95
        if rng.random() < 0.35:
            continue
        brightness = 0.4 + 0.6 * (1 - abs(math.sin(rad)))
        rw = max(1, int(2 + 12 * brightness))
        rr = int(140 + 100 * brightness)
        rg_ = int(60 + 70 * brightness)
        rb = int(15 + 30 * brightness)
        gd.ellipse(
            (ex - rw, ey - rw, ex + rw, ey + rw),
            fill=(rr, rg_, rb, int(60 + 100 * brightness)),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Pass 2: sharper ring fragments
    for deg in range(0, 360, 3):
        rad = math.radians(deg)
        ex = ring_cx + ring_a * math.cos(rad) * 0.95 - ring_b * math.sin(rad) * 0.31
        ey = ring_cy + ring_a * math.cos(rad) * 0.31 + ring_b * math.sin(rad) * 0.95
        if rng.random() < 0.42:
            continue
        brightness = 0.4 + 0.6 * (1 - abs(math.sin(rad)))
        rw = max(1, int(1 + 5 * brightness))
        rr = int(200 + 55 * brightness)
        rg_ = int(90 + 60 * brightness)
        rb = int(25 + 40 * brightness)
        draw.ellipse(
            (ex - rw, ey - rw, ex + rw, ey + rw),
            fill=(rr, rg_, rb, int(100 + 155 * brightness)),
        )
        # Occasional spark
        if rng.random() < 0.12:
            px = ex + rng.randint(-12, 12)
            py = ey + rng.randint(-12, 12)
            draw.ellipse((px - 1, py - 1, px + 1, py + 1), fill=(255, 200, 100, rng.randint(150, 255)))

    # ── Generation Ship (extreme low-angle perspective) ─────────────
    scx = W // 2 + 40    # ship center, slightly off-center
    top_y = 320
    bot_y = 1650

    top_hw = 60    # top half-width (distant)
    bot_hw = 360   # bottom half-width (close to viewer)

    # Main hull body
    hull = [
        (scx - top_hw, top_y),
        (scx - bot_hw, bot_y),
        (scx + bot_hw, bot_y),
        (scx + top_hw, top_y),
    ]
    draw.polygon(hull, fill=(16, 14, 18, 240))

    # Longitudinal panel seams
    for col in range(-3, 4):
        if col == 0:
            continue
        ratio = col / 4
        x1 = scx + ratio * top_hw
        x2 = scx + ratio * bot_hw
        draw.line((int(x1), top_y, int(x2), bot_y), fill=(28, 25, 30, 100), width=1)

    # Transverse structural bands
    for i in range(1, 14):
        t = i / 14
        y_pos = int(top_y + (bot_y - top_y) * t)
        cw = top_hw + (bot_hw - top_hw) * t
        draw.line((scx - cw, y_pos, scx + cw, y_pos), fill=(35, 32, 38, 90), width=1)

    # Central spine ridge
    draw.line((scx, top_y, scx, bot_y), fill=(42, 38, 45, 160), width=3)

    # ── Habitat Ring Pairs ──────────────────────────────────────────
    ring_ys = [top_y + 150, top_y + 300, top_y + 470, top_y + 660, top_y + 870]
    for ry in ring_ys:
        t = (ry - top_y) / (bot_y - top_y)
        cw = top_hw + (bot_hw - top_hw) * t
        rr_a = int(22 + t * 50)
        rr_b = int(10 + t * 25)

        for sign in (-1, 1):
            rx = scx + sign * (cw + 18)

            # Outer ring
            draw.ellipse(
                (rx - rr_a, ry - rr_b, rx + rr_a, ry + rr_b),
                outline=(22, 20, 25, 210), width=2,
            )
            # Inner ring detail
            draw.ellipse(
                (rx - rr_a + 6, ry - rr_b + 4, rx + rr_a - 6, ry + rr_b - 4),
                outline=(35, 32, 40, 80), width=1,
            )
            # Spokes
            for sp in range(0, 360, 45):
                srad = math.radians(sp)
                sx_ = rx + (rr_a - 2) * math.cos(srad)
                sy_ = ry + (rr_b - 2) * math.sin(srad)
                ix_ = rx + rr_a * 0.3 * math.cos(srad)
                iy_ = ry + rr_b * 0.3 * math.sin(srad)
                draw.line((int(ix_), int(iy_), int(sx_), int(sy_)), fill=(30, 28, 35, 70), width=1)
            # Structural arm
            draw.line(
                (int(scx + sign * cw), ry, int(rx - sign * rr_a), ry),
                fill=(28, 25, 32, 160), width=2,
            )

    # ── Radiator fins ───────────────────────────────────────────────
    for col_ratio in (-0.4, -0.2, 0.2, 0.4):
        for j in range(3, 9):
            t = j / 10
            y_pos = int(top_y + (bot_y - top_y) * t)
            cw = top_hw + (bot_hw - top_hw) * t
            fx = int(scx + col_ratio * cw)
            fh = int(35 + t * 35)
            draw.line((fx, y_pos - fh, fx, y_pos + fh), fill=(20, 18, 22, 160), width=2)
            draw.line(
                (fx, y_pos, int(scx + col_ratio * (cw - 5)), y_pos),
                fill=(25, 22, 28, 100), width=1,
            )

    # ── Corrosion / decay patches on hull ───────────────────────────
    for _ in range(rng.randint(15, 30)):
        t = rng.uniform(0.1, 0.9)
        y_pos = int(top_y + (bot_y - top_y) * t)
        cw = top_hw + (bot_hw - top_hw) * t
        px = int(scx + rng.uniform(-cw + 15, cw - 15))
        pr = rng.randint(5, 25)
        pcol = (rng.randint(70, 140), rng.randint(25, 55), rng.randint(8, 28), rng.randint(60, 150))
        draw.ellipse((px - pr, y_pos - pr, px + pr, y_pos + pr), fill=pcol)

    # ── Maintenance crew work lights ────────────────────────────────
    for _ in range(rng.randint(18, 30)):
        t = rng.uniform(0.05, 0.85)
        y_pos = int(top_y + (bot_y - top_y) * t)
        cw = top_hw + (bot_hw - top_hw) * t
        lx = int(scx + rng.uniform(-cw * 0.35, cw * 0.35))
        lr = rng.randint(3, 7)
        la = rng.randint(100, 220)
        draw.ellipse((lx - lr, y_pos - lr, lx + lr, y_pos + lr), fill=(255, 200, 80, la))
        draw.ellipse(
            (lx - lr * 3, y_pos - lr * 3, lx + lr * 3, y_pos + lr * 3),
            fill=(255, 200, 80, la // 5),
        )

    # ── Engine exhaust glow ─────────────────────────────────────────
    exhaust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    xd = ImageDraw.Draw(exhaust)
    for _ in range(rng.randint(10, 18)):
        ex = scx + rng.randint(-60, 60)
        ey = bot_y + rng.randint(0, 80)
        er = rng.randint(15, 40)
        xd.ellipse(
            (ex - er, ey - er, ex + er, ey + er),
            fill=(rng.randint(100, 200), rng.randint(30, 70), rng.randint(5, 25), rng.randint(30, 80)),
        )
    exhaust = exhaust.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, exhaust)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Vignette ────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 90))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 90))

    # ── Atmospheric haze around ship (rusty-brown) ──────────────────
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    hd.ellipse(
        (scx - 500, top_y - 80, scx + 500, bot_y + 150),
        fill=(50, 20, 8, 12),
    )
    haze = haze.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, haze)

    # ── Save ────────────────────────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)
    print(f"Cover saved: {op}")


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
