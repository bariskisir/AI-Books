#!/usr/bin/env python3
"""Cover: Repetition Artist — FBI forensic timeline-analyst finds the same 3-second micro-expression tell in every serial killer's confession footage."""

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

    # ═══════════════════════════════════════════════════════════════
    # Cold evidence-room palette: steel gray, chilled blue, blood red
    # ═══════════════════════════════════════════════════════════════
    BG_TOP = (12, 18, 32)
    BG_BOTTOM = (36, 44, 58)
    ACCENT_RED = (180, 40, 40)
    EVIDENCE_YELLOW = (210, 190, 120)
    FLESH_TONE = (200, 180, 165)
    COLD_BLUE = (100, 140, 200)

    img = Image.new("RGBA", (W, H), (*BG_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Gradient background (chilled concrete) ──
    for y in range(255, H):
        t = (y - 255) / (H - 255)
        r = int(BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t)
        g = int(BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t)
        b = int(BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Darker vignette ──
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(50 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 90))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 90))

    # ── Forensic timeline tick marks (left edge) ──
    for i in range(60):
        ty = 200 + i * 24
        tick_len = 20 if i % 5 == 0 else 10
        draw.line((30, ty, 30 + tick_len, ty), fill=(*COLD_BLUE, 80 + int(80 * math.sin(i * 0.5))), width=2 if i % 5 == 0 else 1)
        if i % 10 == 0:
            draw.text((60, ty - 8), f"{i * 3:02d}:00", fill=(*COLD_BLUE, 140))

    # ── Case-file / evidence tape lines (horizontal strings across the cover) ──
    for row in range(5):
        ry = 400 + row * 260
        draw.line((80, ry, W - 80, ry), fill=(*EVIDENCE_YELLOW, 20 + row * 8), width=1)
        # Red evidence marker dots
        for col in range(4):
            mx = 200 + col * 400
            draw.ellipse((mx - 4, ry - 4, mx + 4, ry + 4), fill=(*ACCENT_RED, 60 + row * 20))

    # ── The REPEATING FACE PROFILE motif ──
    # Six ghostly portrait silhouettes side by side, subtly different
    # Each represents a different killer's face — same tell
    rng = random.Random()
    rng.seed(890134527)

    face_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(face_layer, "RGBA")

    face_centers = [
        (180, 850),
        (460, 830),
        (740, 860),
        (1020, 840),
        (1300, 850),
        (1580, 830),
    ]

    for idx, (fcx, fcy) in enumerate(face_centers):
        # Each face is a stylized profile silhouette facing inward
        direction = 1 if idx < 3 else -1  # first 3 face right, last 3 face left
        face_alpha = 40 + idx * 12

        # Build face profile as polygon points
        fw, fh = 120, 160
        pts = []
        # Start at chin
        cx = fcx
        cy = fcy
        # Chin
        pts.append((cx, cy + fh // 2))
        # Jaw line
        pts.append((cx + direction * fw // 4, cy + fh // 3))
        # Mouth area
        pts.append((cx + direction * fw // 3, cy + fh // 6))
        # Nose bridge bump
        pts.append((cx + direction * fw // 2, cy - fh // 8))
        pts.append((cx + direction * fw // 3, cy - fh // 4))
        # Eye indent
        pts.append((cx + direction * fw // 5, cy - fh // 3))
        # Forehead
        pts.append((cx + direction * fw // 3, cy - fh // 2))
        # Top of head
        pts.append((cx + direction * fw // 6, cy - fh * 3 // 5))
        pts.append((cx, cy - fh * 3 // 5 + fh // 6))
        pts.append((cx - direction * fw // 6, cy - fh // 3))
        pts.append((cx - direction * fw // 8, cy))
        pts.append((cx - direction * fw // 12, cy + fh // 3))
        pts.append((cx, cy + fh // 2))

        face_color = (160 + idx * 10, 140 + idx * 8, 130 + idx * 6)
        fd.polygon(pts, fill=(*face_color, face_alpha))

        # Add a single red dot at the same relative position on each face
        # (the recurring micro-expression — same spot on each face)
        spot_x = cx + direction * fw // 5
        spot_y = cy - fh // 6
        fd.ellipse((spot_x - 6, spot_y - 6, spot_x + 6, spot_y + 6), fill=(*ACCENT_RED, 100 + idx * 20))

    img = Image.alpha_composite(img, face_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Connection lines between the red spots (showing the same tell linking them) ──
    for i in range(len(face_centers) - 1):
        fx1, fy1 = face_centers[i]
        fx2, fy2 = face_centers[i + 1]
        d = 1 if i < 3 else -1
        x1 = fx1 + d * fw // 5
        y1 = (fy1) - fh // 6
        d2 = 1 if (i + 1) < 3 else -1
        x2 = fx2 + d2 * fw // 5
        y2 = (fy2) - fh // 6
        draw.line((x1, y1, x2, y2), fill=(*ACCENT_RED, 120), width=2)

    # ── Waveform / audio-visual trace (the 3-second micro-expression pattern) ──
    wave = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wd = ImageDraw.Draw(wave, "RGBA")
    wave_pts = []
    for x in range(60, W - 60, 6):
        t = x / W
        # Composite waveform with repeated burst every ~1/4 of width (the "tell" repeating)
        base = math.sin(x * 0.04) * 20
        burst1 = math.exp(-((x - W * 0.2) ** 2) / (W * 0.01)) * 45
        burst2 = math.exp(-((x - W * 0.47) ** 2) / (W * 0.01)) * 45
        burst3 = math.exp(-((x - W * 0.74) ** 2) / (W * 0.01)) * 45
        y_offset = base + burst1 + burst2 + burst3 + math.sin(x * 0.08) * 8
        wy = 1150 + int(y_offset)
        wave_pts.append((x, wy))

    if len(wave_pts) > 1:
        wd.line(wave_pts, fill=(*COLD_BLUE, 160), width=3)
        # Glow layer for waveform
        for offset in range(6, 18, 4):
            glow_pts = []
            for x, wy in wave_pts:
                glow_pts.append((x, wy + offset))
            wd.line(glow_pts, fill=(*COLD_BLUE, 20), width=2)
            glow_pts2 = []
            for x, wy in wave_pts:
                glow_pts2.append((x, wy - offset))
            wd.line(glow_pts2, fill=(*COLD_BLUE, 20), width=2)

    img = Image.alpha_composite(img, wave)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Lens / surveillance camera overlay (confession footage motif) ──
    # Crosshairs
    cx, cy = W // 2, 1450
    draw.line((cx - 120, cy, cx - 20, cy), fill=(*ACCENT_RED, 100), width=2)
    draw.line((cx + 20, cy, cx + 120, cy), fill=(*ACCENT_RED, 100), width=2)
    draw.line((cx, cy - 120, cx, cy - 20), fill=(*ACCENT_RED, 100), width=2)
    draw.line((cx, cy + 20, cx, cy + 120), fill=(*ACCENT_RED, 100), width=2)
    # REC indicator
    draw.ellipse((cx + 140, cy - 10, cx + 160, cy + 10), fill=(*ACCENT_RED, 200))
    draw.text((cx + 170, cy - 12), "REC", fill=(*ACCENT_RED, 200))
    # Lens ring
    draw.ellipse((cx - 60, cy - 60, cx + 60, cy + 60), outline=(*COLD_BLUE, 60), width=2)
    draw.ellipse((cx - 50, cy - 50, cx + 50, cy + 50), outline=(*COLD_BLUE, 40), width=1)

    # ── Fingerprint / loop patterns (forensic motif) ──
    for fi in range(3):
        fcx = 300 + fi * 500
        fcy = 1650
        for ring in range(3, 10):
            r = ring * 6 + fi * 3
            draw.arc((fcx - r, fcy - r, fcx + r, fcy + r), -30 + fi * 10, 200 + fi * 10,
                     fill=(*COLD_BLUE, 30 + ring * 8), width=1)
        # Whorl center
        draw.ellipse((fcx - 3, fcy - 3, fcx + 3, fcy + 3), fill=(*COLD_BLUE, 60))

    # ── Red evidence-room string lines ──
    for si in range(6):
        sx = 80 + si * 280
        sy = 200
        ex = 100 + si * 240
        ey = 600 + si * 40
        draw.line((sx, sy, ex, ey), fill=(*ACCENT_RED, 30 + si * 10), width=1)

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
