#!/usr/bin/env python3
"""Cover: Neon Requiem — A data-courier with a cortical implant that lets her taste encrypted files must traffick a dead CEO's final 47 seconds of consciousness across a city where every memory is a weapon."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ----- Synaptic palette -----
# Toxic green for neural data, corrupted amber for taste synesthesia,
# neural pink for implant nodes, data cyan for memory fragments, glitch magenta for corruption
BG_A = (10, 6, 22)
BG_B = (38, 24, 58)
NEON_GREEN = (57, 255, 20)
TASTE_AMBER = (255, 190, 0)
NEURAL_PINK = (255, 80, 180)
DATA_CYAN = (0, 222, 255)
GLITCH_MAGENTA = (255, 0, 200)
CORRUPT_RED = (255, 40, 60)


def _gradient(draw):
    """Deep dark-to-purple gradient for the cyberpunk night."""
    for y in range(H):
        t = y / H
        r = int(BG_A[0] + (BG_B[0] - BG_A[0]) * t)
        g = int(BG_A[1] + (BG_B[1] - BG_A[1]) * t)
        b = int(BG_A[2] + (BG_B[2] - BG_A[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _neural_glow(img, rng):
    """Ambient bio-luminescent glow behind the neural cortex."""
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx, cy = W // 2 - 30, H // 3 - 50
    for _ in range(25):
        ang = rng.uniform(0, math.tau)
        dist = abs(rng.gauss(0, 200))
        nx = cx + int(math.cos(ang) * dist)
        ny = cy + int(math.sin(ang) * dist * 0.75)
        if nx < 0 or nx > W or ny < 0 or ny > H * 0.65:
            continue
        r = rng.randint(10, 25)
        col = rng.choice([NEON_GREEN, DATA_CYAN, NEURAL_PINK])
        gd.ellipse((nx - r, ny - r, nx + r, ny + r), fill=(*col, 12))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    return Image.alpha_composite(img, glow)


def _neural_cortex(draw, rng):
    """Dense synaptic web depicting Nix's cortical implant — interconnected
    nodes radiating from the implant site like a conscious constellation."""
    cx, cy = W // 2 - 30, H // 3 - 50
    nodes = []
    for _ in range(70):
        angle = rng.uniform(0, math.tau)
        dist = abs(rng.gauss(0, 260))
        nx = cx + int(math.cos(angle) * dist)
        ny = cy + int(math.sin(angle) * dist * 0.75)
        if nx < 0 or nx > W or ny < 60 or ny > H * 0.65:
            continue
        r = rng.randint(2, 6)
        t = rng.random()
        if t < 0.45:
            col = (60 + rng.randint(0, 100), 200 + rng.randint(0, 55), 20 + rng.randint(0, 40))
        elif t < 0.75:
            col = (20 + rng.randint(0, 40), 180 + rng.randint(0, 75), 220 + rng.randint(0, 35))
        else:
            col = (200 + rng.randint(0, 55), 40 + rng.randint(0, 60), 160 + rng.randint(0, 80))
        draw.ellipse((nx - r, ny - r, nx + r, ny + r), fill=(*col, rng.randint(120, 230)))
        nodes.append((nx, ny))

    # Connect nearby nodes into a web — the implant's synaptic mesh
    thresh = 130
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            dx = nodes[i][0] - nodes[j][0]
            dy = nodes[i][1] - nodes[j][1]
            d = math.sqrt(dx * dx + dy * dy)
            if d < thresh:
                a = int(45 * (1 - d / thresh))
                if a < 8:
                    continue
                c = NEON_GREEN if rng.random() < 0.55 else NEURAL_PINK
                draw.line((nodes[i][0], nodes[i][1], nodes[j][0], nodes[j][1]), fill=(*c, a), width=1)

    # Impulse burst — synaptic firing radiating from the implant's core
    bx, by = cx + 40, cy + 20
    for _ in range(35):
        ang = rng.uniform(-math.pi * 0.6, math.pi * 0.6) - math.pi * 0.15
        ln = rng.randint(120, 500)
        ex = bx + int(math.cos(ang) * ln)
        ey = by + int(math.sin(ang) * ln)
        a = rng.randint(12, 40)
        c = NEON_GREEN if rng.random() < 0.7 else DATA_CYAN
        draw.line((bx, by, ex, ey), fill=(*c, a), width=rng.randint(1, 3))


def _taste_currents(draw, rng):
    """Amber/gold undulating sine waves — the synesthetic 'taste' of
    encrypted data flowing through Nix's cortical implant. Each wave
    is a different encryption layer she must parse through her tongue-implant."""
    ox, oy = W // 2 - 120, 1350
    for wi in range(6):
        amp = 16 + wi * 15
        freq = 0.022 - wi * 0.002
        phase = wi * 1.1
        pts = []
        a = 70 - wi * 10
        for x in range(0, 701, 4):
            wy = oy + wi * 22 + math.sin(x * freq + phase) * amp + math.sin(x * freq * 2.1 + phase * 0.6) * amp * 0.3
            pts.append((ox + x, wy))
        draw.line(pts, fill=(*TASTE_AMBER, max(8, a)), width=3)


def _memory_fragment(draw, rng):
    """A glitched, partially corrupted data block — the dead CEO Imogen Voss's
    final 47 seconds of consciousness. Surrounded by encryption pulse rings
    and data-frame brackets. The timer bar shows 47% progress."""
    mx, my = W // 2 + 130, H // 2 - 60
    mw, mh = 260, 180

    # Dark panel with cyan data-border
    draw.rectangle((mx, my, mx + mw, my + mh), fill=(6, 3, 18, 220), outline=(*DATA_CYAN, 80), width=2)

    # Encrypted data bits (hex-like rectangles inside the fragment)
    for _ in range(50):
        bx = mx + 12 + rng.randint(0, mw - 24)
        by = my + 12 + rng.randint(0, mh - 24)
        bw = rng.randint(4, 10)
        bh = rng.randint(4, 10)
        c = NEON_GREEN if rng.random() < 0.5 else DATA_CYAN
        draw.rectangle((bx, by, bx + bw, by + bh), fill=(*c, rng.randint(80, 200)))

    # Memory corruption glitch bands
    for _ in range(rng.randint(5, 10)):
        gy = my + rng.randint(4, mh - 6)
        gh = rng.randint(2, 8)
        c = rng.choice([GLITCH_MAGENTA, CORRUPT_RED, DATA_CYAN])
        draw.rectangle((mx + 4, gy, mx + mw - 4, gy + gh), fill=(*c, rng.randint(35, 90)))

    # Data-frame corner brackets (encoding visual language)
    for (cxx, cyy, dxx, dyy) in [
        (mx, my, 20, 0), (mx, my, 0, 20),
        (mx + mw, my, -20, 0), (mx + mw, my, 0, 20),
        (mx, my + mh, 20, 0), (mx, my + mh, 0, -20),
        (mx + mw, my + mh, -20, 0), (mx + mw, my + mh, 0, -20)
    ]:
        draw.line((cxx, cyy, cxx + dxx, cyy + dyy), fill=(*DATA_CYAN, 100), width=2)

    # Expanding pulse rings — the fragment trying to decompress
    for r in range(3):
        off = r * 8
        draw.rectangle(
            (mx - 8 - off, my - 8 - off, mx + mw + 8 + off, my + mh + 8 + off),
            outline=(*NEON_GREEN, 20 - r * 6), width=1
        )

    # 47-second timer bar at the bottom of the fragment
    bar_y = my + mh + 12
    draw.line((mx, bar_y, mx + mw, bar_y), fill=(*TASTE_AMBER, 60), width=2)
    draw.line((mx, bar_y, mx + int(mw * 0.47), bar_y), fill=(*TASTE_AMBER, 180), width=2)


def _data_motes(draw, rng):
    """Floating encrypted data particles — the ambient detritus of corporate
    data warfare drifting across Nix's cortical field of vision."""
    for _ in range(120):
        x = rng.randint(0, W)
        y = rng.randint(60, int(H * 0.7))
        r = rng.randint(1, 4)
        t = rng.random()
        if t < 0.5:
            col = (*NEON_GREEN, rng.randint(40, 140))
        elif t < 0.8:
            col = (*DATA_CYAN, rng.randint(30, 110))
        else:
            col = (*NEURAL_PINK, rng.randint(20, 80))
        draw.ellipse((x - r, y - r, x + r, y + r), fill=col)


def _hex_packets(draw, rng):
    """Small hexagon glyphs — encrypted data packets traversing the
    city's networks, each one a potential weapon in corporate hands."""
    for _ in range(18):
        x = rng.randint(0, W)
        y = rng.randint(0, int(H * 0.7))
        s = rng.randint(6, 14)
        a = rng.randint(30, 80)
        c = NEON_GREEN if rng.random() < 0.5 else DATA_CYAN
        pts = []
        for i in range(6):
            ang = math.pi / 3 * i - math.pi / 6
            pts.append((x + math.cos(ang) * s, y + math.sin(ang) * s))
        draw.polygon(pts, outline=(*c, a), width=1)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random()
    rng.seed(873291045)

    img = Image.new("RGBA", (W, H), BG_A)
    draw = ImageDraw.Draw(img, "RGBA")
    _gradient(draw)

    # Ambient glow behind the neural cortex
    img = _neural_glow(img, rng)
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Neural cortex — Nix's cortical implant visualization
    _neural_cortex(draw, rng)

    # 2. Taste currents — encrypted data tasted as synesthetic amber waves
    _taste_currents(draw, rng)

    # 3. Memory fragment — the CEO's corrupted 47-second consciousness
    _memory_fragment(draw, rng)

    # 4. Data motes — floating encrypted particles
    _data_motes(draw, rng)

    # 5. Hex packets — data packets in transit
    _hex_packets(draw, rng)

    # 6. Vignette — darken edges for focus
    for vy in range(H):
        vt = abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt * 0.6))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 60))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 60))

    # 7. Subtle CRT scan lines for cyberpunk display texture
    for y in range(0, int(H * 0.75), 4):
        draw.line((0, y, W, y), fill=(0, 0, 0, 5))

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
