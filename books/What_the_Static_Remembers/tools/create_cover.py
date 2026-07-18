#!/usr/bin/env python3
"""Cover: What the Static Remembers — A radio engineer fixing a Cold War-era transmitter tower picks up broadcasts of his own childhood—recorded years before his birth—and the signal is changing the present to match them."""

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
rng.seed(170141823)


# ── Palettes ──────────────────────────────────────────────────────────
# Rusted industrial browns from Cold War steel, corroded copper green,
# vacuum-tube amber, and the sickly grey-green of old CRT phosphor.
RUST_A = (48, 28, 20)
RUST_B = (72, 48, 30)
RUST_C = (100, 60, 35)
TUBE_AMBER = (235, 170, 40)
TUBE_GLOW = (200, 140, 30)
PHOSPHOR_GREEN = (140, 200, 90)
PHOSPHOR_DIM = (80, 130, 50)
COPPER_STAIN = (55, 80, 70)
STATIC_GREY = (110, 110, 100)
CORROSION = (38, 50, 42)


# ── Helpers ───────────────────────────────────────────────────────────

def _gradient(draw):
    """Deep rust-brown gradient: darkest at top, lighter rusty at horizon,
    then fading to a pale sickly grey in the lower third (the static haze)."""
    for y in range(H):
        t = y / H
        if t < 0.65:
            # Rust gradient from top down
            s = t / 0.65
            r = int(RUST_A[0] + (RUST_C[0] - RUST_A[0]) * s)
            g = int(RUST_A[1] + (RUST_B[1] - RUST_A[1]) * s)
            b = int(RUST_A[2] + (RUST_B[2] - RUST_A[2]) * s)
        else:
            # Fade into pale static haze
            s = (t - 0.65) / 0.35
            r = int(RUST_C[0] + (STATIC_GREY[0] - RUST_C[0]) * s)
            g = int(RUST_B[1] + (STATIC_GREY[1] - RUST_B[1]) * s)
            b = int(RUST_B[2] + (STATIC_GREY[2] - RUST_B[2]) * s)
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _static_noise(img, density=0.006):
    """Add fine-grained analogue TV static as a translucent overlay."""
    noise = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    nd = ImageDraw.Draw(noise)
    for _ in range(int(W * H * density)):
        x = rng.randint(0, W - 1)
        y = rng.randint(0, H - 1)
        v = rng.randint(60, 200)
        a = rng.randint(3, 16)
        nd.point((x, y), fill=(v, v, v - 20, a))
    # Heavy horizontal scanlines like an analogue CRT
    for sy in range(0, H, 3):
        nd.line((0, sy, W, sy), fill=(10, 10, 8, 14))
    return Image.alpha_composite(img, noise)


def _vignette(draw):
    """Darken edges to focus attention on the tower."""
    for vy in range(H):
        vt = abs(vy - H // 2) / (H // 2)
        vv = int(60 * max(0, 1 - vt * 0.5))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 50))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 50))
    for vx in range(W):
        vt = abs(vx - W // 2) / (W // 2)
        vv = int(50 * max(0, 1 - vt * 0.5))
        if vv > 0:
            draw.line((vx, 0, vx, vv), fill=(0, 0, 0, 35))
            draw.line((vx, H - vv, vx, H), fill=(0, 0, 0, 55))


# ── Scene elements ────────────────────────────────────────────────────

def _radio_tower(draw):
    """The Cold War transmitter tower — rusted steel lattice dominating
    the left-centre of the composition. A massive vertical structure with
    cross-bracing, a dish array, and warning lights."""
    cx, cy = W // 2 - 120, 900  # tower base centre

    # ── Main lattice legs (four tapering verticals) ──
    leg_positions = [-160, -50, 50, 160]
    leg_x = [cx + p for p in leg_positions]
    top_x = [cx + int(p * 0.25) for p in leg_positions]  # taper at top
    tower_top_y = cy - 780

    for i in range(4):
        draw.line(
            (leg_x[i], cy, top_x[i], tower_top_y),
            fill=(32, 20, 14, 230), width=6,
        )

    # ── Horizontal cross-beams every 60 px ──
    for step in range(0, 800, 60):
        beam_y = cy - step
        wider = step / 780  # 0 at top, 1 at base
        left_a = top_x[0] + int((leg_x[0] - top_x[0]) * wider)
        left_b = top_x[1] + int((leg_x[1] - top_x[1]) * wider)
        right_a = top_x[2] + int((leg_x[2] - top_x[2]) * wider)
        right_b = top_x[3] + int((leg_x[3] - top_x[3]) * wider)

        # Left half of beam
        draw.line((left_a, beam_y, left_b, beam_y), fill=(40, 28, 18, 180), width=3)
        # Right half
        draw.line((right_a, beam_y, right_b, beam_y), fill=(40, 28, 18, 180), width=3)

        # Diagonal cross-bracing (X pattern on left pair and right pair)
        if step > 60:
            prev_y = beam_y + 60
            for j in range(2):
                prev_la = top_x[j] + int((leg_x[j] - top_x[j]) * ((step - 60) / 780))
                prev_lb = top_x[j + 1] + int((leg_x[j + 1] - top_x[j + 1]) * ((step - 60) / 780))
                la = top_x[j] + int((leg_x[j] - top_x[j]) * wider)
                lb = top_x[j + 1] + int((leg_x[j + 1] - top_x[j + 1]) * wider)
                draw.line((prev_la, prev_y, la, beam_y), fill=(30, 20, 12, 120), width=2)
                draw.line((prev_lb, prev_y, lb, beam_y), fill=(30, 20, 12, 120), width=2)
                # X-brace within each bay
                draw.line((prev_la, prev_y, lb, beam_y), fill=(25, 18, 10, 100), width=1)
                draw.line((prev_lb, prev_y, la, beam_y), fill=(25, 18, 10, 100), width=1)

    # ── Guy wires (diagonal tension cables) ──
    for side in [-1, 1]:
        for depth in [180, 320]:
            gw_x = cx + side * depth
            gw_base = (gw_x, cy)
            # Three cable anchor points
            for anchor_y in [tower_top_y + 100, tower_top_y + 250, tower_top_y + 400]:
                a = int(40 + 30 * (1 - (anchor_y - tower_top_y) / 500))
                draw.line(
                    (cx, anchor_y, gw_base[0], gw_base[1]),
                    fill=(60, 48, 35, a), width=1,
                )

    # ── Dish antenna array near the top ──
    dish_y = tower_top_y + 120
    draw.line((top_x[3], dish_y - 20, top_x[3] + 140, dish_y - 40), fill=(50, 38, 25, 200), width=3)
    # Dish bowl (parabolic shape)
    dish_pts = []
    for ang_deg in range(-70, 71, 5):
        rad = math.radians(ang_deg)
        dx = 100 * math.cos(rad)
        dy = 60 * math.sin(rad)
        dish_pts.append((top_x[3] + 140 + dx, dish_y - 40 + dy))
    draw.polygon(dish_pts, fill=(28, 18, 12, 180), outline=(60, 42, 28, 220), width=2)
    # Dish feed horn
    draw.line((top_x[3] + 140, dish_y - 40, top_x[3] + 235, dish_y - 40), fill=(70, 50, 35, 200), width=3)
    # Red aviation warning light at top
    draw.ellipse((top_x[1] - 8, tower_top_y - 12, top_x[1] + 8, tower_top_y + 4), fill=(220, 30, 20, 200))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((top_x[1] - 25, tower_top_y - 30, top_x[1] + 25, tower_top_y + 12), fill=(220, 40, 20, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    draw.ellipse((top_x[1] - 8, tower_top_y - 12, top_x[1] + 8, tower_top_y + 4), fill=(220, 30, 20, 200))

    # ── Second smaller dish ──
    dish2_y = tower_top_y + 280
    draw.line((top_x[0], dish2_y, top_x[0] - 110, dish2_y), fill=(50, 38, 25, 180), width=2)
    draw.ellipse((top_x[0] - 110 - 40, dish2_y - 30, top_x[0] - 110 + 40, dish2_y + 30),
                 fill=(28, 18, 12, 160), outline=(60, 42, 28, 200), width=2)

    # ── Equipment shed at base ──
    shed_w, shed_h = 140, 60
    shed_x, shed_y = cx - 70, cy
    draw.rectangle((shed_x, shed_y, shed_x + shed_w, shed_y + shed_h), fill=(25, 18, 10, 230))
    draw.line((shed_x, shed_y, shed_x + shed_w, shed_y), fill=(48, 35, 22, 200), width=2)
    # Door
    draw.rectangle((shed_x + 55, shed_y + 15, shed_x + 85, shed_y + shed_h), fill=(12, 8, 5, 240))
    # Corroded panel marks
    for _ in range(4):
        px = shed_x + rng.randint(5, shed_w - 5)
        py = shed_y + rng.randint(5, shed_h - 5)
        draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=(35, 28, 18, 80))

    return cx, cy, top_x, tower_top_y


def _concentric_waves(draw, cx, cy):
    """Radio broadcast waves — concentric ellipses emanating from the
    tower's midpoint, visibly warping/tearing the space behind them."""
    base_waves = [30, 80, 150, 230, 320, 430, 560, 700, 860, 1040]

    for radius in base_waves:
        # Elliptical waves (taller than wide — signal propagates vertically too)
        rx = int(radius * 1.3)
        ry = int(radius * 2.2)
        alpha = max(8, int(60 - radius * 0.05))
        width = max(1, int(5 - radius * 0.004))

        # Slightly offset vertical centre — waves drift upward like heat
        voice_cy = cy - 100
        draw.ellipse(
            (cx - rx, voice_cy - ry, cx + rx, voice_cy + ry),
            outline=(TUBE_AMBER[0], TUBE_AMBER[1], TUBE_AMBER[2], alpha),
            width=width,
        )

        # Second, fainter concentric slightly offset (interference pattern)
        draw.ellipse(
            (cx - rx + 8, voice_cy - ry - 4, cx + rx + 8, voice_cy + ry - 4),
            outline=(PHOSPHOR_GREEN[0], PHOSPHOR_GREEN[1], PHOSPHOR_GREEN[2], max(4, alpha // 3)),
            width=max(1, width - 1),
        )


def _static_memory_holes(draw):
    """Glitched rectangular regions where the static 'remembers' — ghostly
    broadcast fragments that look like corrupted video frames from a 1970s
    surveillance feed. These are the story's 'broadcasts of his own childhood'
    bleeding into the present."""
    hole_data = [
        (140, 620, 300, 780),     # top-left fragment
        (760, 480, 1080, 650),    # wide landscape memory
        (1100, 720, 1380, 880),   # right-side fragment
        (200, 820, 480, 1020),    # mid-left memory
        (920, 850, 1260, 1050),   # large central memory
        (180, 1100, 400, 1260),   # lower fragment
        (1100, 1000, 1320, 1170), # right lower
    ]

    for (x1, y1, x2, y2) in hole_data:
        # Faint white/grey rectangle - like a glitching video overlay
        alpha = rng.randint(18, 40)

        # Draw the hole
        draw.rectangle((x1, y1, x2, y2), fill=(STATIC_GREY[0], STATIC_GREY[1], STATIC_GREY[2], alpha))

        # Horizontal glitch bands inside each hole
        for gy in range(y1 + 4, y2 - 4, rng.randint(6, 18)):
            gh = rng.randint(2, 5)
            if rng.random() < 0.6:
                c = (TUBE_AMBER[0], TUBE_AMBER[1], TUBE_AMBER[2], rng.randint(15, 40))
            else:
                c = (PHOSPHOR_GREEN[0], PHOSPHOR_GREEN[1], PHOSPHOR_GREEN[2], rng.randint(10, 30))
            draw.rectangle((x1 + 2, gy, x2 - 2, gy + gh), fill=c)

        # Bright scan-line at top of hole (like a CRT raster line)
        draw.line((x1, y1 + 2, x2, y1 + 2), fill=(200, 190, 170, 50), width=1)

        # VHS-style tracking noise at bottom
        for _ in range(rng.randint(3, 6)):
            nx = x1 + rng.randint(0, x2 - x1 - 20)
            ny = y2 - rng.randint(1, 12)
            draw.line((nx, ny, nx + 20 + rng.randint(0, 30), ny), fill=(180, 180, 170, 30), width=1)


def _static_horizon_glow(draw):
    """A sickly amber/green horizon glow — the 'signal' bending the
    visual space as it changes the present to match the past."""
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)

    # Horizon band of amber light
    for y in range(500, 1100):
        t = 1 - abs(y - 800) / 300
        if t > 0:
            alpha = int(12 * t)
            gd.line((0, y, W, y), fill=(TUBE_AMBER[0], TUBE_AMBER[1], TUBE_AMBER[2], alpha))

    # Broader green phosphor bloom above
    for y in range(300, 700):
        t = 1 - abs(y - 500) / 200
        if t > 0:
            alpha = int(6 * t)
            gd.line((0, y, W, y), fill=(PHOSPHOR_DIM[0], PHOSPHOR_DIM[1], PHOSPHOR_DIM[2], alpha))

    glow = glow.filter(ImageFilter.GaussianBlur(20))
    return glow


def _voice_in_the_static(draw):
    """A faint, almost-subconscious face in the static — 'The Voice on the
    Air'.  Built from sparse dots and lines at the threshold of perception,
    centred in the upper-right quadrant where the interference is strongest."""
    vx, vy = 1100, 420

    # Eye sockets — two dark hollows
    for ex, ey in [(vx - 35, vy - 12), (vx + 35, vy - 12)]:
        draw.ellipse((ex - 18, ey - 12, ex + 18, ey + 12), fill=(20, 14, 8, 50))
        draw.ellipse((ex - 10, ey - 6, ex + 10, ey + 6), fill=(8, 5, 3, 80))
        # Pinprick of light in each eye
        draw.ellipse((ex - 3, ey - 3, ex + 3, ey + 3), fill=(TUBE_AMBER[0], TUBE_AMBER[1], TUBE_AMBER[2], 40))

    # Bridge of nose (subtle)
    draw.line((vx - 6, vy - 6, vx + 6, vy - 6), fill=(30, 22, 14, 40), width=2)
    draw.line((vx, vy - 6, vx, vy + 18), fill=(25, 18, 10, 40), width=2)

    # Mouth — a faint, static-fractured line
    mx, my = vx, vy + 40
    for i in range(3):
        off = i * 12 - 12
        a = rng.randint(20, 50)
        draw.line((mx - 20 + off, my + i * 3, mx + 20 + off * 0.5, my + i * 3),
                  fill=(80, 72, 60, a), width=1)

    # Jaw outline (barely visible)
    jaw_pts = []
    for ang_deg in range(0, 181, 10):
        rad = math.radians(ang_deg - 90)
        jx = vx + 55 * math.cos(rad)
        jy = vy + 65 * math.sin(rad)
        jaw_pts.append((jx, jy))
    draw.line(jaw_pts, fill=(40, 32, 24, 25), width=1)

    # Surrounding static dots that cluster around the face
    for _ in range(60):
        ang = rng.uniform(0, math.tau)
        dist = rng.gauss(80, 30)
        px = vx + math.cos(ang) * dist
        py = vy + math.sin(ang) * dist
        if 0 <= px < W and 0 <= py < H:
            draw.point((int(px), int(py)), fill=(STATIC_GREY[0] + rng.randint(-20, 20),
                                                  STATIC_GREY[1] + rng.randint(-20, 20),
                                                  STATIC_GREY[2] + rng.randint(-20, 20),
                                                  rng.randint(15, 45)))


def _vu_meter_needle(draw):
    """A broken analogue VU meter at the bottom-left — the needle pinned
    into the red, representing the signal that should not exist."""
    vx, vy = 100, 1500

    # Meter face
    draw.arc((vx - 60, vy - 60, vx + 60, vy + 60), -135, 135,
             fill=(50, 40, 28, 180), width=3)

    # Scale markings
    for deg in range(-120, 121, 10):
        rad = math.radians(deg - 90)
        inner_r, outer_r = (40, 48) if deg % 30 == 0 else (44, 48)
        x1 = vx + inner_r * math.cos(rad)
        y1 = vy + inner_r * math.sin(rad)
        x2 = vx + outer_r * math.cos(rad)
        y2 = vy + outer_r * math.sin(rad)
        draw.line((x1, y1, x2, y2), fill=(TUBE_AMBER[0] - 40, TUBE_AMBER[1] - 40, TUBE_AMBER[2] - 20, 120), width=2)

    # Red danger zone (right side)
    for deg in range(60, 121, 2):
        rad = math.radians(deg - 90)
        inner_r, outer_r = 0, 52
        x1 = vx + inner_r * math.cos(rad)
        y1 = vy + inner_r * math.sin(rad)
        x2 = vx + outer_r * math.cos(rad)
        y2 = vy + outer_r * math.sin(rad)
        draw.line((x1, y1, x2, y2), fill=(180, 25, 25, 40), width=2)

    # Needle (pinned into red)
    needle_deg = 85  # Pinned into red zone
    rad = math.radians(needle_deg - 90)
    n_len = 42
    nx = vx + n_len * math.cos(rad)
    ny = vy + n_len * math.sin(rad)
    draw.line((vx, vy, nx, ny), fill=(220, 35, 25, 200), width=3)
    # Needle tip dot
    draw.ellipse((nx - 3, ny - 3, nx + 3, ny + 3), fill=(230, 40, 30, 220))

    # Centre pivot
    draw.ellipse((vx - 5, vy - 5, vx + 5, vy + 5), fill=(TUBE_AMBER[0], TUBE_AMBER[1], TUBE_AMBER[2], 180))


def _frequency_dial(draw):
    """A vintage radio frequency dial showing a ghost frequency — the
    station that should not exist, broadcasting on the wrong band."""
    dx, dy = 1200, 1480
    dial_w, dial_h = 300, 90

    # Dial face panel
    draw.rectangle((dx, dy, dx + dial_w, dy + dial_h), fill=(22, 16, 10, 210))
    draw.rectangle((dx, dy, dx + dial_w, dy + dial_h), outline=(55, 42, 28, 180), width=2)

    # Frequency markings
    for i in range(11):
        fx = dx + 15 + i * (dial_w - 30) // 10
        draw.line((fx, dy + 10, fx, dy + 10 + ((dial_h - 20) if i % 5 == 0 else (dial_h - 35))),
                  fill=(TUBE_AMBER[0] - 30, TUBE_AMBER[1] - 30, TUBE_AMBER[2] - 20, 100), width=1)

    # Ghost frequency marker (off-scale — a red needle pointing past the end)
    needle_x = dx + dial_w - 10
    draw.line((needle_x, dy + 8, needle_x, dy + dial_h - 8),
              fill=(200, 30, 20, 200), width=3)
    # Small label
    draw.polygon([(needle_x - 5, dy + 6), (needle_x + 5, dy + 6), (needle_x, dy - 2)],
                 fill=(200, 30, 20, 200))

    # "GHOST FREQ" in dots
    gf_x = dx + 15
    gf_y = dy + 20
    for i, row in enumerate([
        [0,1,1,0,1,1,1,0,1,1,1,0,0,1,1,1,0,1,0,1,1,1,0,1,1,1],
    ]):
        for j, bit in enumerate(row):
            if bit:
                draw.point((gf_x + j * 8, gf_y + i * 10), fill=(TUBE_AMBER[0] - 20, TUBE_AMBER[1] - 20, TUBE_AMBER[2] - 20, 70))


def _corroded_ground(draw):
    """The ground beneath the tower — cracked earth with rusty stains and
    dead grass, suggesting the signal has been poisoning the soil."""
    for x in range(0, W, 20):
        ground_y = 900 + int(20 * math.sin(x * 0.05) + 10 * math.sin(x * 0.12))
        draw.line((x, ground_y, x + 20, ground_y + 5),
                  fill=(CORROSION[0] + rng.randint(-10, 10),
                        CORROSION[1] + rng.randint(-10, 10),
                        CORROSION[2] + rng.randint(-10, 10), 200),
                  width=4)

    # Crack patterns in the earth
    for _ in range(20):
        cx = rng.randint(0, W)
        cy = rng.randint(920, 1100)
        for seg in range(3):
            ang = rng.uniform(-0.8, 0.8) + (-1 if seg > 1 else 0) * 0.5
            dx = cx + int(math.cos(ang) * rng.randint(20, 60))
            dy = cy + int(10 + seg * 15 + rng.randint(-5, 5))
            draw.line((cx, cy, dx, dy), fill=(25, 18, 10, rng.randint(40, 100)), width=1)
            cx, cy = dx, dy


def _rabbit_ears(draw):
    """A pair of rabbit-ear antennas growing out of the ground like
    skeletal fingers — domestic objects made ominous by the signal."""
    for side, flip in [(-1, 1), (1, -1)]:
        base_x = W // 2 + side * 380
        base_y = 980
        tip_x = base_x + flip * rng.randint(80, 140)
        tip_y = base_y - rng.randint(150, 220)
        draw.line((base_x, base_y, tip_x, tip_y), fill=(48, 35, 22, 180), width=3)
        draw.line((tip_x, tip_y, tip_x - flip * 10, tip_y - 5), fill=(60, 45, 28, 160), width=3)
        draw.line((tip_x, tip_y, tip_x + flip * 10, tip_y - 5), fill=(60, 45, 28, 160), width=3)


# ── Main ──────────────────────────────────────────────────────────────

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── 1. Base image with rust gradient ──────────────────────────────
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    _gradient(draw)

    # ── 2. Horizon glow (signal bending reality) ──────────────────────
    horizon_glow = _static_horizon_glow(draw)
    img = Image.alpha_composite(img, horizon_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 3. Corroded, cracked ground ──────────────────────────────────
    _corroded_ground(draw)

    # ── 4. Rabbit-ear antennas (ominous domestic objects) ────────────
    _rabbit_ears(draw)

    # ── 5. The radio transmitter tower ───────────────────────────────
    cx, cy, top_x, tower_top_y = _radio_tower(draw)

    # ── 6. Concentric broadcast waves (warping space) ────────────────
    _concentric_waves(draw, cx, tower_top_y + 200)

    # ── 7. Static memory holes (the broadcasts of his childhood) ─────
    _static_memory_holes(draw)

    # ── 8. The Voice in the Static (ghost face) ──────────────────────
    _voice_in_the_static(draw)

    # ── 9. Broken VU meter ───────────────────────────────────────────
    _vu_meter_needle(draw)

    # ── 10. Ghost frequency dial ─────────────────────────────────────
    _frequency_dial(draw)

    # ── 11. Static overlay ───────────────────────────────────────────
    img = _static_noise(img, density=0.008)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 12. Vignette ─────────────────────────────────────────────────
    _vignette(draw)

    # ── 13. Title panel ──────────────────────────────────────────────
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
