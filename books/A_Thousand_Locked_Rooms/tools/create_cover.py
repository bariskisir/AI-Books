#!/usr/bin/env python3
"""Cover: A Thousand Locked Rooms — Estranged daughter Zara Quin must solve seven locked-room puzzles left by her reclusive puzzle-maker father Theo Quin, each hiding a darker family secret."""

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
rng.seed(619200847)

# ── Palette: antique mahogany, aged gold, tarnished brass, shadow ──
DOOR_WOOD = (55, 14, 18)
DOOR_SHADOW = (18, 5, 7)
GOLD = (200, 165, 80)
GOLD_DIM = (140, 100, 35)
GOLD_LIGHT = (230, 200, 100)
DARK_BG = (10, 3, 4)

# Each of the 7 puzzles gets its own color
PUZZLE_PALETTE = [
    (180, 130, 30),   # Puzzle 1: Aged gold
    (50, 140, 150),   # Puzzle 2: Verdigris teal
    (170, 55, 70),    # Puzzle 3: Oxidized crimson
    (55, 110, 180),   # Puzzle 4: Faded azure
    (150, 55, 140),   # Puzzle 5: Withered amethyst
    (100, 150, 50),   # Puzzle 6: Moss emerald
    (210, 170, 80),   # Puzzle 7: Amber
]


def _draw_lock_mechanism(draw, cx, cy, outer_r, paint_col, inner_col):
    """Draw an ornate circular lock mechanism centered at (cx, cy)."""
    # Concentric rings
    for ring_r in range(outer_r, 40, -15):
        ring_alpha = max(25, 200 - (outer_r - ring_r) * 2)
        draw.ellipse(
            (cx - ring_r, cy - ring_r, cx + ring_r, cy + ring_r),
            fill=None, outline=(160, 120, 50, min(200, ring_alpha)),
            width=2 if ring_r % 30 == 0 else 1,
        )
    # Solid lock body rings
    for radius, fill_col, outline_col, line_w in [
        (outer_r - 10, DOOR_SHADOW, paint_col, 4),
        (outer_r - 50, (30, 10, 14), paint_col, 3),
        (outer_r - 90, (22, 7, 10), inner_col, 2),
        (outer_r - 120, (15, 5, 6), GOLD_LIGHT, 2),
    ]:
        if radius > 0:
            draw.ellipse(
                (cx - radius, cy - radius, cx + radius, cy + radius),
                fill=fill_col, outline=outline_col, width=line_w,
            )


def _draw_keyhole(draw, cx, cy, size, fill_col):
    """Draw a classic keyhole symbol."""
    kh = size
    kw = kh // 3
    # Top bulb
    draw.ellipse(
        (cx - kw - 2, cy - kh - 4, cx + kw + 2, cy - kh + kw + 2),
        fill=fill_col,
    )
    # Shaft
    pts = [
        (cx - kw, cy - kh),
        (cx - kw, cy - 6),
        (cx - 3, cy + kh - 8),
        (cx + 3, cy + kh - 8),
        (cx + kw, cy - 6),
        (cx + kw, cy - kh),
    ]
    draw.polygon(pts, fill=fill_col)


def _draw_puzzle_panel(draw, img, x1, y1, x2, y2, pcol, panel_idx):
    """Draw one puzzle compartment with border, glow, and a unique symbol."""
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    sr = min(x2 - x1, y2 - y1) // 3

    # Outer frame
    draw.rectangle((x1, y1, x2, y2), fill=(38, 12, 15, 240), outline=pcol, width=2)
    draw.rectangle((x1 + 5, y1 + 5, x2 - 5, y2 - 5), fill=None,
                   outline=(pcol[0] // 2, pcol[1] // 2, pcol[2] // 2, 80), width=1)

    # Inner glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.ellipse((cx - 30, cy - 30, cx + 30, cy + 30), fill=(*pcol, 14))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Unique geometric symbol per puzzle
    sym_col = (pcol[0], pcol[1], pcol[2], 180)
    if panel_idx == 0:
        # Diamond
        draw.polygon([
            (cx, cy - sr), (cx + sr, cy), (cx, cy + sr), (cx - sr, cy),
        ], fill=None, outline=sym_col, width=2)
    elif panel_idx == 1:
        # Triangle
        draw.polygon([
            (cx, cy - sr), (cx + sr, cy + sr), (cx - sr, cy + sr),
        ], fill=None, outline=sym_col, width=2)
    elif panel_idx == 2:
        # Square
        draw.rectangle(
            (cx - sr // 2, cy - sr // 2, cx + sr // 2, cy + sr // 2),
            fill=None, outline=sym_col, width=2,
        )
    elif panel_idx == 3:
        # Star (crossed axes + circle)
        for ang_deg in (0, 90, 180, 270):
            ang = math.radians(ang_deg)
            draw.line((cx, cy, cx + math.cos(ang) * sr, cy + math.sin(ang) * sr),
                      fill=sym_col, width=2)
        draw.ellipse((cx - sr // 2, cy - sr // 2, cx + sr // 2, cy + sr // 2),
                     fill=None, outline=sym_col, width=1)
    elif panel_idx == 4:
        # Hexagon
        pts = []
        for ang_deg in range(0, 360, 60):
            ang = math.radians(ang_deg)
            pts.append((cx + math.cos(ang) * sr, cy + math.sin(ang) * sr))
        draw.polygon(pts, fill=None, outline=sym_col, width=2)
    elif panel_idx == 5:
        # Cross
        draw.line((cx - sr, cy, cx + sr, cy), fill=sym_col, width=2)
        draw.line((cx, cy - sr, cx, cy + sr), fill=sym_col, width=2)
        draw.ellipse((cx - sr // 3, cy - sr // 3, cx + sr // 3, cy + sr // 3),
                     fill=None, outline=(*pcol, 120), width=1)
    else:
        # Concentric circles (puzzle 7)
        for rr in range(sr, sr // 4 - 1, -(sr // 3)):
            draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr),
                         fill=None, outline=sym_col, width=1)

    # Small keyhole icon inside each panel
    _draw_keyhole(draw, cx, cy, 6, (pcol[0], pcol[1], pcol[2], 200))

    return img, draw


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), DARK_BG)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Rich gradient background (black → deep mahogany → dark) ──
    for y in range(H):
        t = y / H
        phase = math.sin(t * math.pi * 0.85)
        r = int(18 + 52 * phase * (1 - t * 0.25))
        g = int(4 + 12 * phase * (1 - t * 0.25))
        b = int(6 + 18 * phase * (1 - t * 0.25))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # ── 2. Vignette ──
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(70 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 130))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 130))

    # ── 3. Main door frame ──
    df_l, df_r = 180, 1420
    df_t, df_b = 130, 1940

    # Multi-layered frame border
    for bw in range(20):
        alpha = 180 - bw * 7
        if alpha < 15:
            alpha = 15
        c = max(10, 60 - bw * 2)
        draw.rectangle(
            (df_l - bw, df_t - bw, df_r + bw, df_b + bw),
            fill=None, outline=(c, c // 3, c // 3, alpha), width=1,
        )

    # Door body
    door_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(door_layer)
    dd.rectangle((df_l, df_t, df_r, df_b), fill=DOOR_WOOD, outline=GOLD_DIM, width=4)
    img = Image.alpha_composite(img, door_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 4. Wood grain / aged texture ──
    for _ in range(60):
        gx = rng.randint(df_l + 15, df_r - 15)
        gy = rng.randint(df_t + 15, df_b - 15)
        offset = rng.randint(-8, 8)
        grey = DOOR_WOOD[0] + offset
        galpha = rng.randint(20, 50)
        if rng.random() < 0.65:
            draw.line((gx, gy, gx + rng.randint(30, 140), gy + rng.randint(-6, 6)),
                      fill=(max(0, grey), max(0, DOOR_WOOD[1] + offset // 2),
                            max(0, DOOR_WOOD[2] + offset // 2), galpha), width=1)
        else:
            draw.line((gx, gy, gx + rng.randint(-5, 5), gy + rng.randint(30, 80)),
                      fill=(max(0, grey), max(0, DOOR_WOOD[1] + offset // 2),
                            max(0, DOOR_WOOD[2] + offset // 2), galpha), width=1)

    # Inner door panel border
    draw.rectangle((df_l + 22, df_t + 22, df_r - 22, df_b - 22),
                   fill=None, outline=(70, 24, 14, 140), width=2)

    # ── 5. Door arch ──
    draw.arc((df_l - 15, df_t - 130, df_r + 15, df_t + 40),
             0, 180, fill=GOLD_DIM, width=8)
    draw.arc((df_l + 25, df_t - 95, df_r - 25, df_t + 10),
             0, 180, fill=GOLD, width=3)

    # ── 6. Central lock mechanism ──
    lx, ly = W // 2, 1050
    _draw_lock_mechanism(draw, lx, ly, 260, GOLD_DIM, GOLD_LIGHT)
    _draw_keyhole(draw, lx, ly, 28, GOLD_LIGHT)

    # Keyhole glow
    kh_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    kg = ImageDraw.Draw(kh_glow)
    kg.ellipse((lx - 40, ly - 40, lx + 40, ly + 40), fill=(255, 220, 120, 35))
    kh_glow = kh_glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, kh_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 7. Radiating spokes from lock ──
    for ang_deg in range(0, 360, 10):
        ang = math.radians(ang_deg)
        sr = rng.randint(50, 90)
        ex = lx + math.cos(ang) * rng.randint(200, 340)
        ey = ly + math.sin(ang) * rng.randint(200, 340)
        ex = max(df_l + 15, min(df_r - 15, ex))
        ey = max(df_t + 15, min(df_b - 15, ey))
        draw.line((lx + math.cos(ang) * sr, ly + math.sin(ang) * sr, ex, ey),
                  fill=(90, 55, 15, 50), width=1)

    # ── 8. Seven puzzle panels ──
    panel_positions = [
        (lx - 200, ly - 385, lx - 40, ly - 280),    # Upper-left
        (lx + 40, ly - 385, lx + 200, ly - 280),    # Upper-right
        (lx - 400, ly - 185, lx - 230, ly - 70),    # Mid-left
        (lx + 230, ly - 185, lx + 400, ly - 70),    # Mid-right
        (lx - 400, ly + 70, lx - 230, ly + 185),    # Lower mid-left
        (lx + 230, ly + 70, lx + 400, ly + 185),    # Lower mid-right
        (lx - 200, ly + 240, lx + 200, ly + 410),   # Bottom center (large)
    ]

    for i, ((x1, y1, x2, y2), pcol) in enumerate(zip(panel_positions, PUZZLE_PALETTE)):
        img, draw = _draw_puzzle_panel(draw, img, x1, y1, x2, y2, pcol, i)

    # ── 9. Ornamental diamond fretwork (puzzle-box texture) ──
    for dx in range(df_l + 80, df_r - 60, 36):
        for dy in range(df_t + 80, df_b - 60, 36):
            # Skip lock area
            if abs(dx - lx) < 290 and abs(dy - ly) < 290:
                continue
            # Skip panel areas
            skip_panel = False
            for (px1, py1, px2, py2) in [(p[0][0], p[0][1], p[0][2], p[0][3]) for p in
                                          [(pos,) for pos in panel_positions]]:
                pass
            for pp in panel_positions:
                if pp[0] - 8 < dx < pp[2] + 8 and pp[1] - 8 < dy < pp[3] + 8:
                    skip_panel = True
                    break
            if skip_panel:
                continue

            dr = rng.randint(3, 6)
            da = rng.randint(12, 35)
            draw.polygon([
                (dx, dy - dr), (dx + dr, dy), (dx, dy + dr), (dx - dr, dy),
            ], fill=None, outline=(130, 90, 30, da), width=1)

    # ── 10. Corner rosettes ──
    for (cx_, cy_) in [
        (df_l + 18, df_t + 18),
        (df_r - 18, df_t + 18),
        (df_l + 18, df_b - 18),
        (df_r - 18, df_b - 18),
    ]:
        for rr in range(8, 45, 8):
            draw.arc((cx_ - rr, cy_ - rr, cx_ + rr, cy_ + rr),
                     0, 90 if cx_ < W // 2 else 180 if cx_ > W // 2 else 270,
                     fill=GOLD_DIM, width=1)

    # ── 11. Light beam from keyhole ──
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    for ang_deg in range(-25, 26, 5):
        ang = math.radians(ang_deg)
        for dist in range(80, 650, 60):
            bx = lx + math.sin(ang) * dist
            by = ly + 40 + math.cos(ang) * dist * 0.45
            br = 1.5 + dist * 0.006
            ba = max(1, 18 - dist // 40)
            bd.ellipse((bx - br, by - br, bx + br, by + br), fill=(230, 200, 100, ba))
    beam = beam.filter(ImageFilter.GaussianBlur(7))
    img = Image.alpha_composite(img, beam)

    # ── 12. Dust / particles ──
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(dust)
    for _ in range(120):
        dx = rng.randint(40, W - 40)
        dy = rng.randint(40, H - 180)
        dr = rng.randint(1, 3)
        db = rng.randint(170, 230)
        ds.ellipse((dx - dr, dy - dr, dx + dr, dy + dr),
                   fill=(db, db - 20, db - 60, rng.randint(15, 50)))
    dust = dust.filter(ImageFilter.GaussianBlur(1))
    img = Image.alpha_composite(img, dust)

    # ── 13. Warm light pool at door base ──
    base_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bgd = ImageDraw.Draw(base_glow)
    bgd.ellipse((lx - 500, df_b - 80, lx + 500, df_b + 100), fill=(200, 160, 60, 10))
    base_glow = base_glow.filter(ImageFilter.GaussianBlur(45))
    img = Image.alpha_composite(img, base_glow)

    # ── 14. Gold separator line ──
    draw = ImageDraw.Draw(img, "RGBA")
    draw.line((180, H - 155, W - 180, H - 155), fill=GOLD_DIM, width=1)

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
