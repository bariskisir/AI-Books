#!/usr/bin/env python3
"""Cover: Programmer's Lament — A blind coder's neural sonification interface reveals her employer's AI rewriting human memory through data-stream backdoors."""

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
rng.seed(902471365)

# Sonified cyberpunk palette — deep indigo/warm purple background,
# teal for clean data, signal-orange for sonification, red for corruption
PALETTE_BG_TOP = (5, 2, 18)
PALETTE_BG_BOT = (55, 18, 70)
PALETTE_TEAL = (0, 200, 180)
PALETTE_ORANGE = (255, 120, 40)
PALETTE_ICE = (100, 200, 255)
PALETTE_RED = (255, 40, 60)
PALETTE_MINT = (50, 255, 180)
PALETTE_PURPLE = (180, 100, 255)
PALETTE_WARM = (255, 80, 40)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (*PALETTE_BG_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Spectral gradient background ─────────────────────────────────────
    # Deep indigo at top, bleeding into warm dark purple at the bottom,
    # simulating the visible spectrum of a sonograph
    for y in range(H):
        t = y / H
        r = int(PALETTE_BG_TOP[0] + (PALETTE_BG_BOT[0] - PALETTE_BG_TOP[0]) * t
                + 15 * max(0, t - 0.5))
        g = int(PALETTE_BG_TOP[1] + (PALETTE_BG_BOT[1] - PALETTE_BG_TOP[1]) * t
                - 5 * max(0, t - 0.6) * 10)
        b = int(PALETTE_BG_TOP[2] + (PALETTE_BG_BOT[2] - PALETTE_BG_TOP[2]) * t
                - 10 * max(0, t - 0.65) * 8)
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)),
                                       max(0, min(255, b)), 255))

    # Vignette edge
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 100))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 100))

    # ── Spectrogram frequency bands ──────────────────────────────────────
    # Horizontal translucent bars at varying heights, representing audio
    # frequencies that Kira "hears" as she navigates code
    SPEC_COLORS = [
        PALETTE_TEAL, PALETTE_ORANGE, PALETTE_ICE,
        PALETTE_RED, PALETTE_PURPLE, PALETTE_MINT,
    ]
    for _ in range(45):
        y_pos = rng.randint(80, 1650)
        bar_h = rng.randint(3, 35)
        col = rng.choice(SPEC_COLORS)
        alpha = rng.randint(8, 35)
        draw.rectangle((0, y_pos, W, y_pos + bar_h),
                       fill=(col[0], col[1], col[2], alpha))

    # Denser thin lines for a fine spectrogram texture
    for _ in range(90):
        y_pos = rng.randint(80, 1650)
        col = rng.choice(SPEC_COLORS)
        alpha = rng.randint(4, 15)
        draw.rectangle((0, y_pos, W, y_pos + 1),
                       fill=(col[0], col[1], col[2], alpha))

    # ── Cochlea-inspired spiral arcs ────────────────────────────────────
    # Concentric partial arcs in the upper-mid area, evoking the inner-ear
    # spiral that translates vibration into neural signal — Kira's
    # sonification interface
    spiral_cx = W // 2 + 80
    spiral_cy = 620
    for ring in range(14):
        radius = 80 + ring * 31
        start_deg = 100 + ring * 12
        end_deg = 440 - ring * 6
        bbox = (spiral_cx - radius, spiral_cy - radius,
                spiral_cx + radius, spiral_cy + radius)
        fade = max(8, 60 - ring * 4)
        # Alternate teal and orange arcs for a spectral sweep
        if ring % 3 == 0:
            arc_col = (*PALETTE_TEAL, fade)
        elif ring % 3 == 1:
            arc_col = (*PALETTE_ORANGE, fade)
        else:
            arc_col = (*PALETTE_PURPLE, fade)
        draw.arc(bbox, start_deg, end_deg, fill=arc_col,
                 width=max(1, 5 - ring // 3))

    # ── Cascading sine waves (sonified code) ────────────────────────────
    # Each wave represents a code module Kira "reads" through sound
    for wave_idx in range(10):
        y_base = 400 + wave_idx * 120 + rng.randint(-30, 30)
        amplitude = 25 + rng.randint(10, 70)
        frequency = 0.004 + rng.uniform(0, 0.018)
        phase = rng.uniform(0, math.tau)
        wcol = rng.choice([PALETTE_TEAL, PALETTE_ORANGE, PALETTE_ICE, PALETTE_PURPLE, PALETTE_MINT])
        pts = []
        for wx in range(0, W + 3, 3):
            wy = y_base + math.sin(wx * frequency + phase) * amplitude
            pts.append((wx, wy))
        alpha = rng.randint(35, 100)
        draw.line(pts, fill=(wcol[0], wcol[1], wcol[2], alpha),
                  width=rng.randint(1, 4))

    # ── Profile silhouette — Kira Solovyova ─────────────────────────────
    # Left-facing bust, with data streams flowing into the ear region
    # representing her neural sonification interface
    sx, sy = 260, 720
    SIL = (12, 8, 20, 235)

    # Head (ellipse)
    draw.ellipse((sx - 45, sy - 70, sx + 45, sy + 50), fill=SIL)
    # Neck
    draw.rectangle((sx - 18, sy + 45, sx + 22, sy + 95), fill=SIL)
    # Shoulders and upper torso
    draw.ellipse((sx - 90, sy + 75, sx + 75, sy + 280), fill=SIL)
    # Hair suggestion — longer at the back
    draw.ellipse((sx - 55, sy - 75, sx - 10, sy + 30), fill=(8, 5, 16, 240))
    draw.ellipse((sx + 35, sy - 60, sx + 60, sy + 60), fill=(8, 5, 16, 240))

    # Ear area highlight — a small glowing dot at the ear position
    draw.ellipse((sx + 28, sy - 5, sx + 38, sy + 8),
                 fill=(*PALETTE_TEAL, 180))

    # ── Data streams flowing into the ear ────────────────────────────────
    # Thin curved lines converging toward the ear area, representing
    # sonified code entering Kira's perception
    for dl in range(16):
        start_x = rng.randint(sx + 60, sx + 320)
        start_y = rng.randint(sy - 40, sy + 20)
        mid_x = (start_x + sx + 30) // 2
        mid_y = start_y - rng.randint(30, 80)
        col = rng.choice([
            (*PALETTE_TEAL, rng.randint(80, 150)),
            (*PALETTE_ORANGE, rng.randint(60, 120)),
            (*PALETTE_ICE, rng.randint(50, 100)),
        ])
        w = rng.randint(1, 2)
        draw.line((start_x, start_y, mid_x, mid_y), fill=col, width=w)
        draw.line((mid_x, mid_y, sx + 30, sy + 2 + rng.randint(-8, 8)),
                  fill=col, width=w)

    # ── Code rain — vertical falling data columns ────────────────────────
    # Suggesting the codebase scrolling through Kira's interface
    for _ in range(70):
        x = rng.randint(0, W)
        y = rng.randint(80, 1600)
        length = rng.randint(15, 140)
        col = rng.choice([
            (*PALETTE_TEAL, rng.randint(10, 50)),
            (*PALETTE_ICE, rng.randint(8, 35)),
            (*PALETTE_ORANGE, rng.randint(8, 30)),
        ])
        draw.line((x, y, x, y + length), fill=col, width=rng.randint(1, 3))

    # ── Glitch memory blocks ────────────────────────────────────────────
    # Scattered rects representing corrupted short-term memory fragments
    # that the AI is rewriting
    GLITCH_COLORS = [
        (*PALETTE_RED, 45),
        (255, 100, 0, 35),
        (200, 0, 200, 30),
        (*PALETTE_ORANGE, 30),
    ]
    for _ in range(rng.randint(10, 18)):
        bx = rng.randint(100, W - 100)
        by = rng.randint(250, 1620)
        bw = rng.randint(18, 90)
        bh = rng.randint(8, 32)
        base_col = rng.choice(GLITCH_COLORS)
        draw.rectangle((bx, by, bx + bw, by + bh), fill=base_col)
        # Offset clone — the glitch "echo"
        if rng.random() < 0.55:
            ox = bx + rng.randint(4, 18)
            echo_col = (*PALETTE_TEAL, base_col[3] - 10)
            draw.rectangle((ox, by, ox + bw, by + bh), fill=echo_col)
        # Bright pixel fragment within the block
        if rng.random() < 0.5:
            px = bx + rng.randint(2, max(2, bw - 10))
            py = by + rng.randint(2, max(2, bh - 6))
            draw.rectangle((px, py, px + rng.randint(4, 12), py + rng.randint(2, 6)),
                           fill=(250, 250, 250, rng.randint(15, 40)))

    # ── The "backdoor" — diagonal glitch tear ──────────────────────────
    # A jagged crack slicing diagonally across the upper half, representing
    # the AI's secret backdoor corrupting the data stream
    cx, cy = W // 2 - 120, 350
    crack_pts = []
    for step in range(22):
        jx = cx + step * 30 + rng.randint(-12, 12)
        jy = cy + step * 18 + rng.randint(-10, 10)
        crack_pts.append((jx, jy))

    # Outer glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_layer)
    for gs in range(6):
        gx = cx + 330 + rng.randint(-60, 60)
        gy = cy + 200 + rng.randint(-60, 60)
        gr = rng.randint(40, 100)
        glow_draw.ellipse((gx - gr, gy - gr, gx + gr, gy + gr),
                          fill=(*PALETTE_RED, 6))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Crack line — thick warm red
    draw.line(crack_pts, fill=(*PALETTE_RED, 140), width=6)
    draw.line(crack_pts, fill=(*PALETTE_WARM, 50), width=14)

    # Tiny spark fragments along the crack
    for _ in range(rng.randint(8, 15)):
        spx = cx + 330 + rng.randint(-30, 30)
        spy = cy + 200 + rng.randint(-30, 30)
        spr = rng.randint(1, 4)
        spcol = rng.choice([PALETTE_RED, PALETTE_ORANGE, (255, 200, 100)])
        draw.ellipse((spx - spr, spy - spr, spx + spr, spy + spr),
                     fill=(*spcol, rng.randint(100, 220)))

    # ── Floating binary/data dots ──────────────────────────────────────
    # Tiny circles suggesting active neural data transmission
    for _ in range(80):
        dx = rng.randint(0, W)
        dy = rng.randint(100, 1650)
        dr = rng.uniform(1.0, 3.5)
        dcol = rng.choice([PALETTE_TEAL, PALETTE_ICE, PALETTE_MINT])
        da = rng.randint(15, 60)
        draw.ellipse((int(dx - dr), int(dy - dr), int(dx + dr), int(dy + dr)),
                     fill=(dcol[0], dcol[1], dcol[2], da))

    # ── Save ─────────────────────────────────────────────────────────
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
