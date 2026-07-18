#!/usr/bin/env python3
"""Cover: Scream Sequence — A sound engineer capturing ambient noise in an abandoned asylum records a frequency that resonates inside her own bones; psychological body horror with sound-wave-visualized asylum descent."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Unique palette: sickly yellow-green (frequency/sickness) bleeding into
# deep bruise purple-black (asylum decay, body horror, basement darkness)
PALETTE_BG_TOP = (15, 18, 10)       # near-black with green undertone
PALETTE_BG_MID = (60, 45, 25)       # sickly brown-green
PALETTE_BG_BOT = (40, 10, 30)       # bruise purple-black
FREQ_GLOW = (180, 220, 60)          # frequency green-yellow glow
FREQ_PULSE = (255, 240, 100)        # bright pulse
BONE_GLOW = (200, 230, 150)         # bones illuminated by frequency
TEETH_GLOW = (220, 250, 180)        # teeth
BASEMENT_PULL = (60, 20, 50)        # dark purple pull from below
ASYLUM_WALL = (25, 20, 15)          # wall shadow
ASYLUM_WALL_LIT = (50, 45, 35)      # wall with frequency glow

rng = random.Random()
rng.seed(819346277)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), PALETTE_BG_TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Multi-stop gradient background ──────────────────────────────────
    # Sickly green-black at top, bruise purple at bottom
    for y in range(H):
        t = y / H
        if t < 0.4:
            # top: near-black green → sickly brown-green
            t2 = t / 0.4
            r = int(PALETTE_BG_TOP[0] + (PALETTE_BG_MID[0] - PALETTE_BG_TOP[0]) * t2)
            g = int(PALETTE_BG_TOP[1] + (PALETTE_BG_MID[1] - PALETTE_BG_TOP[1]) * t2)
            b = int(PALETTE_BG_TOP[2] + (PALETTE_BG_MID[2] - PALETTE_BG_TOP[2]) * t2)
        else:
            # bottom: sickly brown-green → bruise purple-black
            t2 = (t - 0.4) / 0.6
            r = int(PALETTE_BG_MID[0] + (PALETTE_BG_BOT[0] - PALETTE_BG_MID[0]) * t2)
            g = int(PALETTE_BG_MID[1] + (PALETTE_BG_BOT[1] - PALETTE_BG_MID[1]) * t2)
            b = int(PALETTE_BG_MID[2] + (PALETTE_BG_BOT[2] - PALETTE_BG_MID[2]) * t2)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    # ── 2. Asylum corridor — forced perspective vanishing point ────────────
    # Vanishing point: slightly below center, pulling toward basement
    vx, vy = W // 2, 1400
    # Left wall
    wall_left_pts = []
    for i in range(20):
        t = i / 19
        x1 = int(vx - 800 * (1 - t * 0.55))
        x2 = int(vx - 300 * (1 - t * 0.85))
        y1 = int(vy - 1400 * (1 - t))
        y2 = int(vy - 1400 * (1 - (t + 0.05)))
        wall_left_pts.append(((x1 + x2) // 2, (y1 + y2) // 2))
        darkness = int(20 + 30 * t)
        draw.polygon([
            (x1, y1), (x2, y1), (x2, y2), (x1, y2)
        ], fill=(darkness, darkness - 5, darkness - 8, 200))
    # Right wall
    for i in range(20):
        t = i / 19
        x1 = int(vx + 300 * (1 - t * 0.85))
        x2 = int(vx + 800 * (1 - t * 0.55))
        y1 = int(vy - 1400 * (1 - t))
        y2 = int(vy - 1400 * (1 - (t + 0.05)))
        darkness = int(20 + 30 * t)
        draw.polygon([
            (x1, y1), (x2, y1), (x2, y2), (x1, y2)
        ], fill=(darkness, darkness - 5, darkness - 8, 200))
    # Floor tiles receding to vanishing point
    for i in range(12):
        t = i / 11
        y1 = int(vy + 100 * (1 - t) * (1 - t))
        y2 = int(vy + 100 * (1 - (t + 0.08)) * (1 - (t + 0.08)))
        if y2 > H:
            break
        left_x = int(vx - 400 * (1 - t * 0.5))
        right_x = int(vx + 400 * (1 - t * 0.5))
        darkness = int(12 + 25 * t)
        draw.rectangle((left_x, min(y1, y2), right_x, max(y1, y2)),
                       fill=(darkness, darkness - 3, darkness - 5, 180))
    # Doorways along corridor walls
    for side, sign in [("left", -1), ("right", 1)]:
        for di in range(4):
            t = 0.15 + di * 0.2
            if t > 0.8:
                break
            dw = int(120 * (1 - t * 0.6))
            dh = int(220 * (1 - t * 0.6))
            dx = int(vx + sign * 350 * (1 - t * 0.7))
            dy = int(vy - 500 * (1 - t) - dh)
            # Door frame
            draw.rectangle((dx - dw // 2, dy, dx + dw // 2, dy + dh),
                           fill=None, outline=(40, 35, 25, 150), width=2)
            # Dark interior
            draw.rectangle((dx - dw // 4, dy + 5, dx + dw // 4, dy + dh - 5),
                           fill=(8, 5, 5, 180))

    # ── 3. Frequency waves — oscilloscopic waveforms cutting through image ─
    wave_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wl_draw = ImageDraw.Draw(wave_layer)

    # Multiple waveform bands at different frequencies
    for band in range(6):
        base_y = 500 + band * 200
        freq_mult = 0.01 + band * 0.008
        amp = 30 + band * 15
        alpha = int(40 + band * 15)
        pts = []
        for px in range(0, W, 4):
            t = px / W
            wave = math.sin(px * freq_mult + band) * amp
            wave += math.sin(px * freq_mult * 2.3 + band * 1.7) * amp * 0.3
            wave += math.sin(px * freq_mult * 0.5 + band * 0.8) * amp * 0.5
            # Distortion increases toward center (where the sound originates)
            center_dist = abs(px - W // 2) / (W // 2)
            wave *= (1.5 - center_dist * 0.5)
            pts.append((px, int(base_y + wave)))
        glow_color = (FREQ_GLOW[0], FREQ_GLOW[1], FREQ_GLOW[2], alpha)
        # Draw thick glowing waveform
        for thickness in range(3, 8, 2):
            for i in range(len(pts) - 1):
                wl_draw.line((pts[i], pts[i + 1]),
                             fill=(glow_color[0], glow_color[1], glow_color[2], alpha // thickness),
                             width=thickness)

    # Blur the wave layer for glowing effect
    wave_layer = wave_layer.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, wave_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Sharp waveform overlay on top
    for band in range(3):
        base_y = 600 + band * 250
        freq_mult = 0.015 + band * 0.01
        amp = 25 + band * 10
        pts = []
        for px in range(0, W, 2):
            t = px / W
            wave = math.sin(px * freq_mult + band * 2.0) * amp
            wave += math.sin(px * freq_mult * 3.0 + band * 1.2) * amp * 0.25
            pts.append((px, int(base_y + wave)))
        draw.line(pts, fill=(FREQ_PULSE[0], FREQ_PULSE[1], FREQ_PULSE[2], 120), width=2)

    # ── 4. Repeating teeth / bone vibration motif ──────────────────────────
    # Teeth/jaw silhouette at top-mid — the frequency in her mouth
    mouth_y = 480
    for tooth_x in range(W // 2 - 180, W // 2 + 181, 18):
        tooth_h = 30 + int(math.sin(tooth_x * 0.15) * 12)
        tooth_w = 10
        # Glowing tooth outline
        glow_alpha = int(100 + 80 * abs(math.sin(tooth_x * 0.05)))
        draw.rectangle(
            (tooth_x - tooth_w, mouth_y - tooth_h, tooth_x + tooth_w, mouth_y),
            fill=(TEETH_GLOW[0], TEETH_GLOW[1], TEETH_GLOW[2], glow_alpha // 2),
        )
        draw.rectangle(
            (tooth_x - tooth_w + 2, mouth_y - tooth_h + 2, tooth_x + tooth_w - 2, mouth_y - 2),
            fill=(TEETH_GLOW[0], TEETH_GLOW[1], TEETH_GLOW[2], glow_alpha // 3),
        )
    # Upper teeth (inverted)
    for tooth_x in range(W // 2 - 180, W // 2 + 181, 18):
        tooth_h = 25 + int(math.sin(tooth_x * 0.15 + 1.5) * 10)
        tooth_w = 10
        glow_alpha = int(80 + 70 * abs(math.sin(tooth_x * 0.05 + 2.0)))
        draw.rectangle(
            (tooth_x - tooth_w, mouth_y - 50, tooth_x + tooth_w, mouth_y - 50 + tooth_h),
            fill=(TEETH_GLOW[0], TEETH_GLOW[1], TEETH_GLOW[2], glow_alpha // 2),
        )

    # ── 5. Orla's silhouette — vibrating with bones visible ────────────────
    # Semi-transparent figure, torso with ribcage glowing through
    fig_cx = W // 2
    fig_top = 750
    fig_bot = 1400
    fig_w = 120

    # Body outline (ghostly)
    body_pts = [
        (fig_cx, fig_top),                                # head top
        (fig_cx - 30, fig_top + 60),                      # left cheek
        (fig_cx - 35, fig_top + 100),                     # left neck
        (fig_cx - fig_w, fig_top + 200),                  # left shoulder
        (fig_cx - fig_w - 10, fig_top + 350),             # left hip
        (fig_cx - 50, fig_bot),                           # left foot
        (fig_cx + 50, fig_bot),                           # right foot
        (fig_cx + fig_w + 10, fig_top + 350),             # right hip
        (fig_cx + fig_w, fig_top + 200),                  # right shoulder
        (fig_cx + 35, fig_top + 100),                     # right neck
        (fig_cx + 30, fig_top + 60),                      # right cheek
    ]
    # Apply vibration displacement
    vib_pts = []
    for px, py in body_pts:
        vib_x = px + int(math.sin(py * 0.1) * 3)
        vib_y = py + int(math.cos(px * 0.1) * 3)
        vib_pts.append((vib_x, vib_y))
    draw.polygon(vib_pts, fill=(30, 25, 20, 150))
    draw.polygon(vib_pts, fill=None, outline=(FREQ_GLOW[0], FREQ_GLOW[1], FREQ_GLOW[2], 80), width=2)

    # Ribcage glowing through
    for rib_y in range(fig_top + 260, fig_top + 420, 25):
        rib_alpha = int(60 + 40 * abs(math.sin(rib_y * 0.08)))
        rib_width = 70 - (rib_y - fig_top - 260) * 0.2
        draw.arc(
            (fig_cx - rib_width, rib_y - 8, fig_cx + rib_width, rib_y + 8),
            0, 180, fill=(BONE_GLOW[0], BONE_GLOW[1], BONE_GLOW[2], rib_alpha), width=3
        )
        draw.arc(
            (fig_cx - rib_width, rib_y - 8, fig_cx + rib_width, rib_y + 8),
            180, 360, fill=(BONE_GLOW[0], BONE_GLOW[1], BONE_GLOW[2], rib_alpha), width=3
        )

    # Spine centerline
    draw.line(
        (fig_cx, fig_top + 220, fig_cx, fig_top + 450),
        fill=(BONE_GLOW[0], BONE_GLOW[1], BONE_GLOW[2], 100), width=3
    )
    # Skull outline
    draw.ellipse(
        (fig_cx - 25, fig_top - 10, fig_cx + 25, fig_top + 55),
        fill=(30, 25, 20, 150), outline=(BONE_GLOW[0], BONE_GLOW[1], BONE_GLOW[2], 60), width=2
    )
    # Eye sockets (hollow, glowing)
    draw.ellipse((fig_cx - 18, fig_top + 5, fig_cx - 5, fig_top + 20),
                 fill=(FREQ_PULSE[0], FREQ_PULSE[1], FREQ_PULSE[2], 80))
    draw.ellipse((fig_cx + 5, fig_top + 5, fig_cx + 18, fig_top + 20),
                 fill=(FREQ_PULSE[0], FREQ_PULSE[1], FREQ_PULSE[2], 80))

    # ── 6. Frequency rings emanating from the basement ─────────────────────
    ring_center = (W // 2, H - 200)
    for ri in range(8):
        radius = 120 + ri * 60
        ring_alpha = int(70 - ri * 8)
        draw.ellipse(
            (ring_center[0] - radius, ring_center[1] - radius,
             ring_center[0] + radius, ring_center[1] + radius),
            outline=(FREQ_GLOW[0], FREQ_GLOW[1], FREQ_GLOW[2], max(0, ring_alpha)),
            width=3 + ri % 2,
        )

    # ── 7. Basement / stairwell descent ────────────────────────────────────
    # Dark pit at the bottom pulling downward
    pit_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(pit_layer)
    for py in range(1500, H):
        t = (py - 1500) / (H - 1500)
        pit_width = int(600 * (1 - t * 0.4))
        left = W // 2 - pit_width // 2
        right = W // 2 + pit_width // 2
        # Darker as it descends
        dark = int(5 + t * 15)
        pdraw.line((left, py, right, py), fill=(dark, dark - 2, dark + 3, min(255, 100 + int(t * 100))))
    # Stairs descending
    for si in range(20):
        t = si / 19
        sy = int(1550 + t * 700)
        sw = int(500 - t * 250)
        left = W // 2 - sw // 2
        right = W // 2 + sw // 2
        stair_alpha = int(20 + t * 60)
        pdraw.line((left, sy, right, sy), fill=(30, 25, 20, stair_alpha), width=2)
    img = Image.alpha_composite(img, pit_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 8. Spectral face in the basement darkness ──────────────────────────
    # "The Basement Voice" — subtle face emerging from the dark
    face_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(face_layer)
    fx, fy = W // 2, H - 250
    # Vague face shape
    fdraw.ellipse((fx - 80, fy - 100, fx + 80, fy + 20),
                  fill=(50, 20, 45, 40))
    # Hollow eye sockets
    fdraw.ellipse((fx - 40, fy - 60, fx - 10, fy - 25),
                  fill=(FREQ_GLOW[0], FREQ_GLOW[1], FREQ_GLOW[2], 15))
    fdraw.ellipse((fx + 10, fy - 60, fx + 40, fy - 25),
                  fill=(FREQ_GLOW[0], FREQ_GLOW[1], FREQ_GLOW[2], 15))
    # Mouth — open, silent scream
    fdraw.ellipse((fx - 20, fy - 5, fx + 20, fy + 15),
                  fill=(8, 5, 10, 100))
    face_layer = face_layer.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, face_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. Subtle text labels / markings on walls (asylum decay) ────────────
    # Door numbers barely visible on corridor walls
    for di, num in enumerate(["Ward 3", "Isolation", "Exam 2"]):
        tx = int(W // 2 - 320 + di * 250)
        ty = int(600 + di * 100)
        if 0 < tx < W:
            draw.text((tx, ty), num, fill=(100, 90, 70, 40))

    # ── 10. Sound particle debris ──────────────────────────────────────────
    for _ in range(150):
        px = rng.randint(0, W)
        py = rng.randint(0, H)
        pr = rng.uniform(0.5, 2.5)
        pa = rng.randint(20, 80)
        draw.ellipse(
            (int(px - pr), int(py - pr), int(px + pr), int(py + pr)),
            fill=(FREQ_GLOW[0], FREQ_GLOW[1], FREQ_GLOW[2], pa)
        )

    # ── 11. Vertical vignette (darker edges) ───────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 80))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 80))

    # ── Save ───────────────────────────────────────────────────────────────
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)
    print(f"Cover saved: {op}")


def main() -> None:
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
