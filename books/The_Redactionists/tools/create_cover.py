#!/usr/bin/env python3
"""Cover: The Redactionists — A metadata analyst at a defense contractor discovers her employer is systematically erasing people from all records. A cold brutalist government facade looms over a fading silhouette being redacted by black bars, while redacted documents drift through a surveillance grid of data points and scan lines."""

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
rng.seed(2143658709)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── base canvas ──────────────────────────────────────────────────────────
    img = Image.new("RGBA", (W, H), (10, 12, 18, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── vertical gradient: cold institutional steel → near-black ─────────────
    top_r, top_g, top_b = 55, 58, 65
    bot_r, bot_g, bot_b = 8, 10, 14
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(
            int(top_r + (bot_r - top_r) * t),
            int(top_g + (bot_g - top_g) * t),
            int(top_b + (bot_b - top_b) * t), 255))

    # ── brutalist government building facade ─────────────────────────────────
    bld_cx = W // 2
    bld_top, bld_bot = 60, 920
    bld_w = 1160

    # Main concrete block
    draw.rectangle((bld_cx - bld_w // 2, bld_top, bld_cx + bld_w // 2, bld_bot),
                   fill=(22, 24, 32, 240))
    draw.rectangle((bld_cx - bld_w // 2, bld_top, bld_cx + bld_w // 2, bld_bot),
                   outline=(38, 42, 52, 120), width=2)

    # Central tower rising higher
    tw = 280
    draw.rectangle((bld_cx - tw // 2, 10, bld_cx + tw // 2, bld_bot),
                   fill=(18, 20, 28, 250))
    draw.rectangle((bld_cx - tw // 2, 10, bld_cx + tw // 2, bld_bot),
                   outline=(35, 38, 48, 120), width=1)

    # Left wing windows
    for wx in range(bld_cx - bld_w // 2 + 35, bld_cx - tw // 2 - 10, 50):
        for wy in range(bld_top + 50, bld_bot - 30, 45):
            if rng.random() < 0.55:
                lit = rng.randint(140, 220)
                draw.rectangle((wx, wy, wx + 28, wy + 22),
                               fill=(lit, lit - 15, lit - 40, rng.randint(100, 190)))
    # Right wing windows
    for wx in range(bld_cx + tw // 2 + 10, bld_cx + bld_w // 2 - 35, 50):
        for wy in range(bld_top + 50, bld_bot - 30, 45):
            if rng.random() < 0.55:
                lit = rng.randint(140, 220)
                draw.rectangle((wx, wy, wx + 28, wy + 22),
                               fill=(lit, lit - 15, lit - 40, rng.randint(100, 190)))
    # Tower windows
    for wx in range(bld_cx - tw // 2 + 25, bld_cx + tw // 2 - 25, 40):
        for wy in range(30, bld_bot - 20, 40):
            if rng.random() < 0.5:
                lit = rng.randint(150, 240)
                draw.rectangle((wx, wy, wx + 20, wy + 15),
                               fill=(lit, lit - 10, lit - 30, rng.randint(90, 200)))

    # Antenna spire on roof
    draw.line((bld_cx, 10, bld_cx, 10 - 60), fill=(80, 85, 100, 180), width=3)
    draw.ellipse((bld_cx - 4, 10 - 68, bld_cx + 4, 10 - 60), fill=(200, 30, 30, 200))

    # ── ambient cold glow behind figure ──────────────────────────────────────
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 280, 1100, W // 2 + 280, 1800),
               fill=(60, 80, 110, 12))
    gd.ellipse((W // 2 - 120, 1200, W // 2 + 120, 1550),
               fill=(40, 100, 140, 8))
    glow = glow.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── human silhouette (Cate) being redacted/erased ────────────────────────
    fig_cx = W // 2
    fig_cy = 1350
    head_r = 42

    # Head
    draw.ellipse((fig_cx - head_r, fig_cy - 240 - head_r,
                  fig_cx + head_r, fig_cy - 240 + head_r),
                 fill=(12, 12, 16, 220))
    # Neck
    draw.rectangle((fig_cx - 15, fig_cy - 195, fig_cx + 15, fig_cy - 160),
                   fill=(12, 12, 16, 220))
    # Torso and legs
    body_poly = [
        (fig_cx - 90, fig_cy - 160),   # left shoulder
        (fig_cx + 90, fig_cy - 160),   # right shoulder
        (fig_cx + 60, fig_cy + 60),    # right hip
        (fig_cx + 35, fig_cy + 200),   # right foot
        (fig_cx - 35, fig_cy + 200),   # left foot
        (fig_cx - 60, fig_cy + 60),    # left hip
    ]
    draw.polygon(body_poly, fill=(12, 12, 16, 220))
    # Arms
    draw.polygon([
        (fig_cx - 90, fig_cy - 160),
        (fig_cx - 140, fig_cy - 40),
        (fig_cx - 130, fig_cy + 40),
        (fig_cx - 70, fig_cy - 20),
    ], fill=(12, 12, 16, 200))
    draw.polygon([
        (fig_cx + 90, fig_cy - 160),
        (fig_cx + 140, fig_cy - 40),
        (fig_cx + 130, fig_cy + 40),
        (fig_cx + 70, fig_cy - 20),
    ], fill=(12, 12, 16, 200))

    # ── redaction bars slicing horizontally through the figure ──────────────
    bar_slots = [
        (fig_cy - 130, 220), (fig_cy - 90, 240),
        (fig_cy - 50, 200),  (fig_cy - 10, 260),
        (fig_cy + 30, 230),  (fig_cy + 70, 200),
        (fig_cy + 110, 250), (fig_cy + 150, 210),
    ]
    for by, bw in bar_slots:
        bx = fig_cx - bw // 2 + rng.randint(-15, 15)
        shade = rng.randint(0, 20)
        draw.rectangle((bx, by, bx + bw, by + 16),
                       fill=(shade, shade, shade, 230))
        # Subtle highlight fleck on some bars (only if bar is wide enough)
        if rng.random() < 0.4 and bw > 50:
            hx1 = bx + rng.randint(8, bw - 20)
            hx2 = hx1 + rng.randint(8, 25)
            draw.rectangle((hx1, by + 4, hx2, by + 12),
                           fill=(200, 200, 205, rng.randint(30, 60)))

    # ── redacted document fragments floating ─────────────────────────────────
    for _ in range(25):
        dx = rng.randint(80, W - 80)
        dy = rng.randint(bld_bot + 80, 1950)
        dw = rng.randint(70, 180)
        dh = rng.randint(100, 150)
        angle = rng.uniform(-0.35, 0.35)

        base = rng.randint(190, 220)
        doc_col = (base, base - 5, base - 20)
        doc_alpha = rng.randint(50, 130)

        hw, hh = dw // 2, dh // 2
        c, s = math.cos(angle), math.sin(angle)
        corners = [
            (dx + (-hw) * c - (-hh) * s, dy + (-hw) * s + (-hh) * c),
            (dx +  hw * c - (-hh) * s, dy +  hw * s + (-hh) * c),
            (dx +  hw * c -  hh * s,   dy +  hw * s +  hh * c),
            (dx + (-hw) * c -  hh * s,  dy + (-hw) * s +  hh * c),
        ]
        draw.polygon(corners, fill=(*doc_col, doc_alpha))
        draw.polygon(corners, outline=(170, 160, 140, doc_alpha), width=1)

        # Simulated text lines on document
        for off in range(-hh + 20, hh - 15, 12):
            g = rng.randint(120, 180)
            tx1 = dx - hw + 12
            tx2 = dx + hw - 12
            ty = dy + off
            draw.line((tx1, ty, tx2, ty),
                      fill=(g, g, g, rng.randint(25, 70)), width=2)

        # Redaction bar on some documents
        if rng.random() < 0.5:
            rby = dy + rng.randint(-35, 35)
            rbw = rng.randint(int(dw * 0.4), int(dw * 0.85))
            rbx = dx - rbw // 2
            draw.rectangle((rbx, rby, rbx + rbw, rby + 10),
                           fill=(rng.randint(3, 18), rng.randint(3, 18),
                                 rng.randint(3, 18), rng.randint(150, 210)))

    # ── surveillance metadata grid overlay ───────────────────────────────────
    for gx in range(0, W, 40):
        draw.line((gx, bld_bot, gx, H),
                  fill=(50, 70, 100, rng.randint(3, 10)), width=1)
    for gy in range(bld_bot, H, 40):
        draw.line((0, gy, W, gy),
                  fill=(50, 70, 100, rng.randint(3, 10)), width=1)

    # ── data points (metadata traces, alerts) ────────────────────────────────
    for _ in range(120):
        px = rng.randint(30, W - 30)
        py = rng.randint(bld_bot + 60, 2000)
        pr = rng.uniform(1.5, 4.5)
        pa = rng.randint(30, 100)
        if rng.random() < 0.25:
            col = (200, 40, 40, pa)   # red alert
        else:
            col = (80, 190, 210, pa)  # cyan data
        draw.ellipse((int(px - pr), int(py - pr), int(px + pr), int(py + pr)),
                     fill=col)

    # ── metadata relationship connector lines ────────────────────────────────
    for _ in range(45):
        x1 = rng.randint(100, W - 100)
        y1 = rng.randint(bld_bot + 80, 1850)
        x2 = x1 + rng.randint(-180, 180)
        y2 = y1 + rng.randint(-180, 180)
        draw.line((x1, y1, x2, y2),
                  fill=(60, 120, 150, rng.randint(5, 25)), width=1)

    # ── vertical barcode data column (left side) ─────────────────────────────
    bc_x = 40
    for bci in range(28):
        bc_w = rng.randint(2, 7)
        bc_h = rng.randint(20, 100)
        bc_y = bld_bot + rng.randint(40, 500)
        g = rng.randint(100, 190)
        draw.rectangle((bc_x + bci * 4, bc_y, bc_x + bci * 4 + bc_w, bc_y + bc_h),
                       fill=(g, g + 5, g + 10, rng.randint(50, 110)))

    # ── radar / surveillance scan circle (right side) ────────────────────────
    scx, scy = W - 160, 1450
    for sr in range(1, 7):
        rad = sr * 25
        draw.ellipse((scx - rad, scy - rad, scx + rad, scy + rad),
                     outline=(0, 180, 200, rng.randint(20, 60)), width=1)
    # Sweeping scan line
    sa = rng.uniform(0, math.tau)
    sl = 150
    draw.line((scx, scy, scx + math.cos(sa) * sl, scy + math.sin(sa) * sl),
              fill=(0, 200, 220, rng.randint(50, 110)), width=2)
    draw.ellipse((scx - 3, scy - 3, scx + 3, scy + 3), fill=(0, 220, 240, 180))

    # ── target crosshair (surveillance focus) ────────────────────────────────
    chx, chy = W - 320, 1200
    ch_s = 20
    draw.line((chx - ch_s - 10, chy, chx - 4, chy), fill=(0, 200, 220, 90), width=1)
    draw.line((chx + 4, chy, chx + ch_s + 10, chy), fill=(0, 200, 220, 90), width=1)
    draw.line((chx, chy - ch_s - 10, chx, chy - 4), fill=(0, 200, 220, 90), width=1)
    draw.line((chx, chy + 4, chx, chy + ch_s + 10), fill=(0, 200, 220, 90), width=1)
    draw.ellipse((chx - 3, chy - 3, chx + 3, chy + 3), fill=(200, 40, 40, 150))

    # ── vignette (darkened edges) ────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ── title panel via shared utility ───────────────────────────────────────
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
