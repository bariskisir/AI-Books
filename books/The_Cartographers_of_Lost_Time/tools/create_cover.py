#!/usr/bin/env python3
"""Cover: The Cartographers of Lost Time — A disgraced mapmaker touches a fragment of an impossible ancient map and sees a
mountain range rising from a sea that dried up before mammals walked. Something looks back from the ancient emptiness."""

from __future__ import annotations
import argparse
import json
import math
import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Seeded RNG for reproducibility
rng = random.Random()
rng.seed(709348156)

# ── Color palette derived from the book's theme ──────────────────────────
# Aged parchment: warm sepia-to-ochre tones
PARCHMENT_LIGHT = (220, 198, 162)
PARCHMENT_DARK = (165, 130, 88)

# Ink of unknown origin: deep indigo, midnight blue
ANCIENT_INK = (18, 12, 55)
MIDNIGHT_INK = (8, 5, 35)

# Mountain/land tones: dusty slate, muted purple-grey, weathered brown
MOUNTAIN_PEAK = (125, 108, 140)
MOUNTAIN_SHADOW = (72, 58, 88)
MOUNTAIN_BASE = (95, 78, 105)
DRY_EARTH = (140, 105, 70)

# Temporal residue: phosphorescent teal, ghostly silver, amber
RESIDUE_TEAL = (80, 195, 185)
RESIDUE_SILVER = (200, 210, 215)
RESIDUE_AMBER = (225, 180, 55)

# The Ancient Presence: void crimson, gold iris
VOICE_CRIMSON = (140, 25, 35)
EYE_GOLD = (235, 185, 50)
EYE_WHITE = (225, 210, 170)
PUPIL_BLACK = (3, 1, 8)
GLOW_ORANGE = (240, 160, 40)

# ── Utility functions ────────────────────────────────────────────────────

def _noise_grid(w: int, h: int, scale: float) -> list[list[float]]:
    """Generate a simple value-noise grid for texture."""
    cells_x = max(2, int(w / scale))
    cells_y = max(2, int(h / scale))
    grid = [[rng.random() for _ in range(cells_x + 1)] for _ in range(cells_y + 1)]
    result = [[0.0 for _ in range(w)] for _ in range(h)]
    for py in range(h):
        gy = py / scale
        y0, y1 = int(gy), min(int(gy) + 1, cells_y)
        ty = gy - y0
        for px in range(w):
            gx = px / scale
            x0, x1 = int(gx), min(int(gx) + 1, cells_x)
            tx = gx - x0
            v00, v10 = grid[y0][x0], grid[y0][x1]
            v01, v11 = grid[y1][x0], grid[y1][x1]
            v0 = v00 + (v10 - v00) * tx
            v1 = v01 + (v11 - v01) * tx
            result[py][px] = v0 + (v1 - v0) * ty
    return result


def _deckle_pts(cx: int, cy: int, rx: int, ry: int, jag: int,
                num: int = 60) -> list[tuple[int, int]]:
    """Create an irregular polygon approximating a torn/deckle-edged torn map."""
    pts = []
    for i in range(num):
        a = math.tau * i / num
        jx = rng.randint(-jag, jag)
        jy = rng.randint(-jag, jag)
        px = cx + (rx + jx) * math.cos(a)
        py = cy + (ry + jy) * math.sin(a)
        pts.append((int(px), int(py)))
    return pts


def _draw_wisp(draw: ImageDraw.ImageDraw, x: int, y0: int, y1: int,
               color: tuple[int, int, int], alpha: int):
    """Draw a wispy temporal-echo shape rising from the map."""
    segments = rng.randint(6, 12)
    pts = []
    for i in range(segments + 1):
        t = i / segments
        yy = int(y0 + (y1 - y0) * t)
        sway = int(math.sin(t * math.pi * 2 + rng.uniform(0, math.tau)) * (15 + t * 25))
        xx = x + sway + rng.randint(-8, 8)
        pts.append((xx, yy))
    for i in range(len(pts) - 1):
        width = max(1, int(10 * (1 - i / len(pts))))
        draw.line((pts[i], pts[i + 1]), fill=(*color, alpha), width=width)


# ── Main cover generation ────────────────────────────────────────────────

def make_cover(mp: Path, op: Path):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    # ── 1. Base: Aged parchment canvas ───────────────────────────────────
    img = Image.new("RGBA", (W, H), PARCHMENT_LIGHT + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm parchment gradient from light top to darker bottom
    for y in range(H):
        t = y / H
        r = int(PARCHMENT_LIGHT[0] + (PARCHMENT_DARK[0] - PARCHMENT_LIGHT[0]) * t)
        g = int(PARCHMENT_LIGHT[1] + (PARCHMENT_DARK[1] - PARCHMENT_LIGHT[1]) * t)
        b = int(PARCHMENT_LIGHT[2] + (PARCHMENT_DARK[2] - PARCHMENT_LIGHT[2]) * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Parchment stain texture (water damage / age spots)
    stain = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stain)
    for _ in range(40):
        sx = rng.randint(0, W)
        sy = rng.randint(0, H)
        sr = rng.randint(30, 160)
        sa = rng.randint(4, 18)
        shade = rng.choice([(180, 155, 115), (200, 180, 140), (160, 125, 80)])
        sd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(*shade, sa))
    stain = stain.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, stain)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 2. Torn map fragment (the "impossible continent" map) ────────────
    # A large deckle-edged polygon spanning the middle of the cover
    map_cx, map_cy = W // 2, 1150
    map_rx, map_ry = 680, 700
    deckle = _deckle_pts(map_cx, map_cy, map_rx, map_ry, jag=60, num=80)

    # Map background: darker aged paper
    map_bg = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    mbd = ImageDraw.Draw(map_bg)
    mbd.polygon(deckle, fill=(140, 105, 65, 240))
    # Inner highlight for the torn edge
    inner_deckle = _deckle_pts(map_cx, map_cy, map_rx - 8, map_ry - 8, jag=40, num=70)
    mbd.polygon(inner_deckle, fill=(160, 125, 80, 220))
    map_bg = map_bg.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, map_bg)
    draw = ImageDraw.Draw(img, "RGBA")

    # Torn edge line
    draw.polygon(deckle, outline=(110, 78, 48, 180), width=2)

    # ── 3. Cartographic grid lines on the map ───────────────────────────
    grid_area = (map_cx - 580, map_cy - 600, map_cx + 580, map_cy + 600)
    for step in range(6, 20):
        for direction in [(True, True), (True, False), (False, True), (False, False)]:
            # Latitude parallels (horizontal)
            ly = grid_area[1] + step * 65
            if grid_area[1] < ly < grid_area[3]:
                pts_h = []
                for lx in range(grid_area[0], grid_area[2] + 5, 8):
                    fine = math.sin(lx * 0.03 + step * 0.7) * 3
                    pts_h.append((lx, int(ly + fine)))
                draw.line(pts_h, fill=(*MIDNIGHT_INK[:3], 20), width=1)
            # Longitude meridians (vertical)
            lx = grid_area[0] + step * 65
            if grid_area[0] < lx < grid_area[2]:
                pts_v = []
                for ly2 in range(grid_area[1], grid_area[3] + 5, 8):
                    fine = math.sin(ly2 * 0.03 + step * 0.5) * 3
                    pts_v.append((int(lx + fine), ly2))
                draw.line(pts_v, fill=(*MIDNIGHT_INK[:3], 20), width=1)

    # ── 4. The impossible continent: mountain range rising from dry sea ──
    # Coastline of the lost continent
    coast_pts = []
    for cx_off in range(-520, 521, 12):
        t_norm = (cx_off + 520) / 1040
        cy_base = map_cy + 300 + math.sin(t_norm * math.pi) * 280
        cy_jag = int(cy_base + math.sin(cx_off * 0.07 + 1.3) * 20
                     + math.sin(cx_off * 0.15 + 0.7) * 8)
        coast_pts.append((map_cx + cx_off, cy_jag))

    # Coastal landmass fill
    land_poly = coast_pts[:]
    land_poly.append((coast_pts[-1][0] + 50, H))
    land_poly.append((coast_pts[0][0] - 50, H))
    draw.polygon(land_poly, fill=(*DRY_EARTH, 160))

    # Mountain range: three overlapping ridge lines
    for ridx, (peak_y, amp, spread) in enumerate([
        (map_cy - 180, 120, 380),
        (map_cy - 80, 160, 450),
        (map_cy + 40, 100, 320),
    ]):
        ridge = []
        for mx in range(-spread, spread + 1, 6):
            rel = mx / spread
            base_y = peak_y + abs(rel) * amp * 0.6
            noise = math.sin(mx * 0.04 + ridx * 2.1) * 30
            noise += math.sin(mx * 0.09 + ridx * 1.3) * 12
            ridge.append((map_cx + mx, int(base_y + noise)))
        # Fill below ridge to create solid mountain
        ridge_poly = ridge[:]
        ridge_poly.append((ridge[-1][0], ridge[-1][1] + 400))
        ridge_poly.append((ridge[0][0], ridge[0][1] + 400))
        mtn_color = (
            MOUNTAIN_PEAK[0] - ridx * 12,
            MOUNTAIN_PEAK[1] - ridx * 8,
            MOUNTAIN_PEAK[2] - ridx * 10,
        )
        draw.polygon(ridge_poly, fill=(*mtn_color, 200))

        # Ridge line (ink stroke)
        draw.line(ridge, fill=(*ANCIENT_INK, 120), width=3)
        # Snow caps on highest peaks
        if ridx == 0:
            for i in range(0, len(ridge), rng.randint(6, 14)):
                sx, sy = ridge[i]
                cap_size = rng.randint(12, 30)
                draw.ellipse((sx - cap_size, sy - 3, sx + cap_size, sy + 6),
                             fill=(220, 225, 230, rng.randint(60, 120)))

    # ── 5. Ancient ocean bed texture (ripples/dried cracks) ──────────────
    for _ in range(30):
        bx = rng.randint(map_cx - 500, map_cx + 500)
        by = rng.randint(map_cy + 200, map_cy + 600)
        br = rng.randint(30, 100)
        draw.ellipse((bx - br, by - br, bx + br, by + br),
                     outline=(*DRY_EARTH, rng.randint(30, 60)), width=1)
    # Sediment layers
    for sy in range(map_cy + 350, map_cy + 620, rng.randint(12, 30)):
        draw.line((map_cx - 500, sy, map_cx + 500, sy),
                  fill=(*DRY_EARTH, rng.randint(15, 30)), width=1)

    # ── 6. Compass rose (lower-left corner of map) ──────────────────────
    crx, cry = map_cx - 480, map_cy + 450
    cr_size = 45
    for ang_deg, label in [(0, "N"), (90, "E"), (180, "S"), (270, "W")]:
        rad = math.radians(ang_deg)
        ex = int(crx + math.cos(rad) * cr_size)
        ey = int(cry + math.sin(rad) * cr_size)
        draw.line((crx, cry, ex, ey), fill=(*ANCIENT_INK, 160), width=4)
        # Arrowhead
        a1 = math.radians(ang_deg - 25)
        a2 = math.radians(ang_deg + 25)
        draw.polygon([
            (ex, ey),
            (ex - int(math.cos(a1) * 14), ey - int(math.sin(a1) * 14)),
            (ex - int(math.cos(a2) * 14), ey - int(math.sin(a2) * 14)),
        ], fill=(*ANCIENT_INK, 200))
        # Labels
        draw.text((ex + 8, ey - 8), label, fill=(*ANCIENT_INK, 200))
    # Compass circle
    draw.ellipse((crx - cr_size, cry - cr_size, crx + cr_size, cry + cr_size),
                 outline=(*ANCIENT_INK, 100), width=1)

    # ── 7. Rhumb lines (navigation lines radiating from compass points) ─
    for _ in range(12):
        ang = rng.uniform(0, math.tau)
        sx = crx + int(math.cos(ang) * cr_size * 1.2)
        sy = cry + int(math.sin(ang) * cr_size * 1.2)
        ex = sx + int(math.cos(ang) * rng.randint(300, 600))
        ey = sy + int(math.sin(ang) * rng.randint(300, 600))
        draw.line((sx, sy, ex, ey), fill=(*ANCIENT_INK, 15), width=1)

    # ── 8. Temporal residues: ghostly echoes rising from the map ────────
    for _ in range(14):
        rx = rng.randint(map_cx - 500, map_cx + 500)
        ry_base = rng.randint(map_cy - 400, map_cy + 200)
        ry_top = rng.randint(80, ry_base - 80)
        color_choice = rng.choice([RESIDUE_TEAL, RESIDUE_SILVER, RESIDUE_AMBER])
        alpha = rng.randint(25, 70)
        _draw_wisp(draw, rx, ry_base, ry_top, color_choice, alpha)
        # Glow blob at origin point on the map
        blob_r = rng.randint(6, 18)
        draw.ellipse((rx - blob_r, ry_base - blob_r, rx + blob_r, ry_base + blob_r),
                     fill=(*color_choice, alpha))

    # Larger echo orbs floating upward
    echo_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ed = ImageDraw.Draw(echo_layer)
    for _ in range(25):
        ex = rng.randint(200, 1400)
        ey = rng.randint(80, 900)
        er = rng.randint(15, 50)
        ecol = rng.choice([RESIDUE_TEAL, RESIDUE_SILVER, RESIDUE_AMBER])
        ed.ellipse((ex - er, ey - er, ex + er, ey + er), fill=(*ecol, rng.randint(4, 16)))
    echo_layer = echo_layer.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, echo_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 9. The Ancient Presence: "Something is looking back" ─────────────
    # A dark void area at the top of the map, with a glowing eye
    void_cx, void_cy = map_cx, map_cy - 520
    void_r = 120

    # Dark void halo
    void_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(void_layer)
    for ring in range(1, 6):
        ring_r = void_r + ring * 18
        alpha = max(2, 28 - ring * 5)
        vd.ellipse((void_cx - ring_r, void_cy - ring_r,
                     void_cx + ring_r, void_cy + ring_r),
                    fill=(PUPIL_BLACK[0], PUPIL_BLACK[1], PUPIL_BLACK[2], alpha))
    void_layer = void_layer.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, void_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Void core
    draw.ellipse((void_cx - void_r, void_cy - void_r,
                  void_cx + void_r, void_cy + void_r),
                 fill=(*PUPIL_BLACK, 220))

    # Crimson glow ring around the void
    for ring_r in range(void_r + 10, void_r + 45, 5):
        a = max(5, 40 - (ring_r - void_r))
        draw.ellipse((void_cx - ring_r, void_cy - ring_r,
                      void_cx + ring_r, void_cy + ring_r),
                     outline=(*VOICE_CRIMSON, a), width=2)

    # The Eye
    eye_w, eye_h = 70, 40
    # Eye socket/shadow
    draw.ellipse((void_cx - eye_w - 5, void_cy - eye_h - 5,
                  void_cx + eye_w + 5, void_cy + eye_h + 5),
                 fill=(*PUPIL_BLACK, 240))
    # Eye white
    draw.ellipse((void_cx - eye_w, void_cy - eye_h,
                  void_cx + eye_w, void_cy + eye_h),
                 fill=(*EYE_WHITE, 200))
    # Iris
    draw.ellipse((void_cx - 25, void_cy - 22,
                  void_cx + 25, void_cy + 22),
                 fill=(*EYE_GOLD, 220))
    # Pupil - slightly off-center for an unsettling gaze
    pupil_off_x = 2
    pupil_off_y = -3
    draw.ellipse((void_cx - 10 + pupil_off_x, void_cy - 12 + pupil_off_y,
                  void_cx + 10 + pupil_off_x, void_cy + 12 + pupil_off_y),
                 fill=(*PUPIL_BLACK, 240))
    # Iris texture: radial streaks
    for ang in range(0, 360, 15):
        rad = math.radians(ang)
        for dist in [10, 18]:
            sx = int(void_cx + pupil_off_x + math.cos(rad) * dist)
            sy = int(void_cy + pupil_off_y + math.sin(rad) * dist)
            ex = int(void_cx + pupil_off_x + math.cos(rad) * (dist + 8))
            ey = int(void_cy + pupil_off_y + math.sin(rad) * (dist + 8))
            draw.line((sx, sy, ex, ey), fill=(*GLOW_ORANGE, 80), width=1)

    # Eye glow
    eye_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    egd = ImageDraw.Draw(eye_glow)
    egd.ellipse((void_cx - 50, void_cy - 40, void_cx + 50, void_cy + 40),
                fill=(*EYE_GOLD, 25))
    eye_glow = eye_glow.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, eye_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Ink drops / strange ink residue
    for _ in range(18):
        ix = rng.randint(100, 1500)
        iy = rng.randint(100, 1800)
        ir = rng.randint(2, 8)
        icol = (rng.randint(10, 25), rng.randint(5, 18), rng.randint(40, 70))
        draw.ellipse((ix - ir, iy - ir, ix + ir, iy + ir),
                     fill=(*icol, rng.randint(80, 180)))
        # Splatter trail
        for _ in range(rng.randint(2, 5)):
            sx = ix + rng.randint(-20, 20)
            sy = iy + rng.randint(-20, 20)
            sr = rng.randint(1, 3)
            draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr),
                         fill=(*icol, rng.randint(50, 100)))

    # ── 10. Title panel ──────────────────────────────────────────────────
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
