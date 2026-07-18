#!/usr/bin/env python3
"""Cover: The Hollow Protocol — geological warfare technothriller: earth cross-section with magma chamber, seismic waves, fault lines, and the Yellowstone caldera."""

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
rng.seed(908172635)

# Unique palette: molten earth / geological warfare
# Sky: smoke-choked apocalyptic orange-brown
# Crust strata: layered browns from topsoil to deep bedrock
# Magma: fiery orange, glowing yellow-red
# Alert accents: seismic red-orange, caldera glow
SKY_TOP = (18, 10, 6)
SKY_BOT = (50, 25, 12)
CRUST_TOP = (55, 40, 30)
CRUST_MID = (72, 52, 36)
CRUST_DEEP = (38, 28, 22)
MAGMA_GLOW = (220, 75, 15)
MAGMA_CORE = (255, 140, 25)
SEISMIC_RED = (255, 55, 30)
CALDERA_ORANGE = (255, 185, 40)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (18, 10, 6, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── SMOG SKY gradient ──────────────────────────────────────────────
    for y in range(600):
        t = y / 600
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── SEISMOGRAPH traces (top data readouts) ─────────────────────────
    for trace_idx in range(3):
        base_y = 70 + trace_idx * 130
        # Grid backdrop
        for gx in range(0, W, 40):
            draw.line((gx, base_y - 35, gx, base_y + 35),
                      fill=(60, 55, 50, 35), width=1)
        for gy in range(base_y - 35, base_y + 36, 14):
            draw.line((0, gy, W, gy), fill=(60, 55, 50, 25), width=1)

        # Seismic waveform — build point by point
        pts = []
        for x in range(0, W, 3):
            t = x / W
            # Background rumble
            val = (math.sin(x * 0.012 + trace_idx) * 6 +
                   math.sin(x * 0.025 + trace_idx * 2) * 3 +
                   math.sin(x * 0.004) * 4)
            # Simulated major quake events
            if 250 < x < 550:
                dist = abs(x - 400)
                val += 45 * math.exp(-dist * dist / 3000) * (
                    0.6 + 0.4 * math.sin(x * 0.12))
            if 850 < x < 1150:
                dist = abs(x - 1000)
                val += 35 * math.exp(-dist * dist / 2500) * (
                    0.5 + 0.5 * math.sin(x * 0.09))
            if 1250 < x < 1450:
                dist = abs(x - 1350)
                val += 25 * math.exp(-dist * dist / 2000)
            val += rng.gauss(0, 1.5)
            pts.append((x, base_y + int(val)))

        tcol = (SEISMIC_RED[0] - trace_idx * 40,
                SEISMIC_RED[1] + trace_idx * 15,
                SEISMIC_RED[2] + trace_idx * 10)
        if len(pts) > 1:
            draw.line(pts, fill=(*tcol, 190), width=2)

    # ── JAGGED HORIZON line with sinkhole ──────────────────────────────
    surf_y = 560
    surf_pts = [(0, surf_y)]
    for x in range(0, W + 1, 16):
        off = rng.randint(-12, 12)
        if 200 < x < 500:
            off -= 15 + int(abs(math.sin(x * 0.04)) * 25)
        elif 700 < x < 850:
            off -= 40 + int(abs(math.sin(x * 0.03)) * 30)
        elif x > 1200:
            off += int(math.sin(x * 0.015) * 18)
        surf_pts.append((x, surf_y + off))
    surf_pts.append((W, H))
    surf_pts.append((0, H))
    draw.polygon(surf_pts, fill=(42, 28, 20, 255))

    # ── EARTH CROSS-SECTION: sedimentary strata ────────────────────────
    for y in range(surf_y, 1050):
        t = (y - surf_y) / (1050 - surf_y)
        r = int(CRUST_TOP[0] + (CRUST_MID[0] - CRUST_TOP[0]) * t)
        g = int(CRUST_TOP[1] + (CRUST_MID[1] - CRUST_TOP[1]) * t)
        b = int(CRUST_TOP[2] + (CRUST_MID[2] - CRUST_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Horizontal rock strata banding
    for band_y in range(surf_y + 20, 1050, rng.randint(28, 55)):
        bh = rng.randint(3, 10)
        bc = (rng.randint(50, 85), rng.randint(38, 65), rng.randint(25, 48))
        draw.rectangle((0, band_y, W, band_y + bh),
                       fill=(*bc, rng.randint(25, 55)))

    # ── DEEP BEDROCK layer ─────────────────────────────────────────────
    for y in range(1050, 1450):
        t = (y - 1050) / (1450 - 1050)
        r = int(CRUST_MID[0] + (CRUST_DEEP[0] - CRUST_MID[0]) * t)
        g = int(CRUST_MID[1] + (CRUST_DEEP[1] - CRUST_MID[1]) * t)
        b = int(CRUST_MID[2] + (CRUST_DEEP[2] - CRUST_MID[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── FAULT LINES ────────────────────────────────────────────────────
    for _ in range(rng.randint(10, 16)):
        fx = rng.randint(80, W - 80)
        fy = rng.randint(surf_y + 30, 1350)
        fl_pts = [(fx, fy)]
        for _ in range(rng.randint(8, 22)):
            fx += rng.randint(-18, 18)
            fy += rng.randint(12, 35)
            if fy > 1700 or fx < 0 or fx > W:
                break
            fl_pts.append((int(fx), int(fy)))
        draw.line(fl_pts, fill=(rng.randint(55, 80), rng.randint(35, 55),
                                rng.randint(20, 35), rng.randint(140, 210)),
                  width=rng.randint(2, 4))

    # ── MAGMA CHAMBER with glow ────────────────────────────────────────
    mcx = W // 2 + rng.randint(-60, 60)
    mcy = 1400

    # Outer glow layers (blur will soften)
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for r in range(200, 0, -12):
        alpha = int(40 * (1 - r / 200))
        gd.ellipse((mcx - r, mcy - r, mcx + r, mcy + r),
                   fill=(MAGMA_GLOW[0], MAGMA_GLOW[1], MAGMA_GLOW[2], alpha))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Magma chamber core
    for r in range(85, 0, -5):
        alpha = int(220 * (1 - r / 85))
        t = r / 85
        cr = int(MAGMA_CORE[0] * (1 - t) + MAGMA_GLOW[0] * t)
        cg = int(MAGMA_CORE[1] * (1 - t) + MAGMA_GLOW[1] * t)
        cb = int(MAGMA_CORE[2] * (1 - t) + MAGMA_GLOW[2] * t)
        draw.ellipse((mcx - r, mcy - r, mcx + r, mcy + r),
                     fill=(cr, cg, cb, alpha))

    # Brighter hot core center
    draw.ellipse((mcx - 20, mcy - 20, mcx + 20, mcy + 20),
                 fill=(255, 200, 60, 200))

    # ── MAGMA DIKES (intrusion veins) ──────────────────────────────────
    for _ in range(rng.randint(8, 14)):
        dk_pts = [(mcx, mcy)]
        dx, dy = mcx, mcy
        angle = rng.uniform(-math.pi * 0.45, math.pi * 0.45)
        length = rng.randint(50, 220)
        for step in range(0, length, 5):
            dx += math.cos(angle) * 5 + rng.uniform(-3, 3)
            dy -= abs(math.sin(angle) * 5) + rng.uniform(2, 6)
            if dy < surf_y + 30 or dx < 0 or dx > W:
                break
            dk_pts.append((int(dx), int(dy)))
        if len(dk_pts) > 2:
            draw.line(dk_pts,
                      fill=(MAGMA_GLOW[0], MAGMA_GLOW[1], MAGMA_GLOW[2],
                            rng.randint(70, 150)),
                      width=rng.randint(3, 7))

    # ── SEISMIC RADIAL WAVES ───────────────────────────────────────────
    for wr in range(60, 1100, rng.randint(35, 70)):
        alpha = max(0, int(55 * (1 - wr / 1100)))
        draw.ellipse((mcx - wr, mcy - wr, mcx + wr, mcy + wr),
                     outline=(SEISMIC_RED[0], SEISMIC_RED[1],
                              SEISMIC_RED[2], alpha),
                     width=1)

    # ── RING OF FIRE hotspot markers ──────────────────────────────────
    for _ in range(rng.randint(6, 10)):
        hx = rng.randint(60, W - 60)
        hy = surf_y + rng.randint(15, 180)
        for mr in range(12, 0, -3):
            ma = int(90 * (1 - mr / 12))
            draw.ellipse((hx - mr, hy - mr, hx + mr, hy + mr),
                         fill=(MAGMA_GLOW[0], MAGMA_GLOW[1],
                               MAGMA_GLOW[2], ma))

    # ── YELLOWSTONE CALDERA surface indicator ─────────────────────────
    cvx = mcx + rng.randint(-30, 30)
    cvy = surf_y + 8
    # Caldera ring glow
    for rr in range(65, 8, -6):
        ca = int(110 * (1 - rr / 65))
        draw.ellipse((cvx - rr, cvy - rr // 2, cvx + rr, cvy + rr // 2),
                     outline=(CALDERA_ORANGE[0], CALDERA_ORANGE[1],
                              CALDERA_ORANGE[2], ca),
                     width=2)

    # Steam / smoke vents from caldera
    for _ in range(rng.randint(10, 18)):
        sx = cvx + rng.randint(-35, 35)
        sy = cvy - rng.randint(5, 12)
        sv_pts = [(sx, sy)]
        for _ in range(rng.randint(4, 8)):
            sx += rng.randint(-8, 8)
            sy -= rng.randint(8, 20)
            if sy < 20:
                break
            sv_pts.append((sx, sy))
        draw.line(sv_pts, fill=(rng.randint(130, 170), rng.randint(120, 150),
                                rng.randint(100, 130), rng.randint(25, 60)),
                  width=rng.randint(2, 4))

    # ── VIGNETTE ───────────────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

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
