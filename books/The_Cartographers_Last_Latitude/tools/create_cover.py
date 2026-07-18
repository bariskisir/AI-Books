#!/usr/bin/env python3
"""Cover: The Cartographer's Last Latitude — A disgraced 18th-century cartographer, hired to chart an uncharted Arctic passage, discovers his maps are being used not for science but to strand a rival colonial fleet in permanent ice."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Arctic palette: deep Prussian blue sky, icy teal midground, frozen white foreground
SKY_TOP = (18, 22, 48)
SKY_BOT = (50, 80, 90)
ICE_LIGHT = (200, 225, 235)
ICE_SHADOW = (140, 175, 195)
AURORA_COLORS = [(80, 200, 140, 45), (60, 180, 200, 35), (120, 200, 100, 30), (160, 220, 180, 25)]
LANTERN_WARM = (220, 180, 100)
HULL_DARK = (22, 18, 16)


def _sine_wave(x: float, amp: float, freq: float, phase: float) -> float:
    return amp * (math.sin(x * freq + phase) + math.sin(x * freq * 2.7 + phase * 0.6) * 0.3)


def _draw_ship(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float, rng: random.Random) -> None:
    """Draw a three-masted 18th-century ship listing in ice at position (cx, cy)."""
    s = scale
    hull_pts = [
        (cx - 160 * s, cy + 20 * s),
        (cx - 120 * s, cy - 10 * s),
        (cx + 100 * s, cy - 12 * s),
        (cx + 150 * s, cy + 15 * s),
        (cx + 170 * s, cy + 25 * s),
        (cx + 140 * s, cy + 30 * s),
        (cx - 140 * s, cy + 28 * s),
    ]
    draw.polygon(hull_pts, fill=(*HULL_DARK, 240))
    # Hull stripe
    draw.polygon([
        (cx - 135 * s, cy + 12 * s),
        (cx - 105 * s, cy - 3 * s),
        (cx + 95 * s, cy - 5 * s),
        (cx + 135 * s, cy + 8 * s),
        (cx + 140 * s, cy + 18 * s),
        (cx - 130 * s, cy + 18 * s),
    ], fill=(55, 38, 30, 235))

    # Bowsprit
    draw.line((cx + 150 * s, cy - 8 * s, cx + 210 * s, cy - 40 * s), fill=(40, 35, 30, 220), width=max(2, int(5 * s)))

    # Three masts
    mast_positions = [
        (cx - 80 * s, cy - 10 * s, -200 * s),  # foremast
        (cx + 0 * s, cy - 11 * s, -270 * s),   # mainmast
        (cx + 80 * s, cy - 11 * s, -210 * s),  # mizzenmast
    ]
    for mx, my, mh in mast_positions:
        draw.line((mx, my, mx, my + mh), fill=(35, 32, 28, 240), width=max(2, int(4 * s)))

    # Sails (furled — ship is trapped, not sailing) — bundled canvas
    furled_sails = [
        (cx - 80 * s, cy - 130 * s, 25 * s, 55 * s),
        (cx + 0 * s, cy - 180 * s, 32 * s, 65 * s),
        (cx + 80 * s, cy - 130 * s, 25 * s, 55 * s),
    ]
    for fx, fy, fw, fh in furled_sails:
        draw.ellipse((fx - fw, fy, fx + fw, fy + fh), fill=(60, 55, 48, 230))
        draw.ellipse((fx - fw * 0.7, fy + 5, fx + fw * 0.7, fy + fh * 0.7), fill=(72, 66, 58, 210))

    # Cross yards (bare spars)
    for mx, my, mh in mast_positions:
        for yi in range(int(my + mh * 0.4), int(my + mh * 0.85), int(-mh * 0.18)):
            y_spar = my + yi
            y_spar = max(y_spar, int(my + mh * 0.2))
            spar_len = int(50 * s + (-yi / mh) * 50 * s)
            draw.line((mx - spar_len, y_spar, mx + spar_len, y_spar), fill=(40, 38, 34, 200), width=2)

    # Lantern on stern
    draw.ellipse((cx - 155 * s, cy - 12 * s, cx - 142 * s, cy), fill=(*LANTERN_WARM, 200))
    draw.ellipse((cx - 152 * s, cy - 10 * s, cx - 145 * s, cy - 2 * s), fill=(255, 220, 160, 220))

    # Warm lantern glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    gd.ellipse((cx - 180 * s, cy - 40 * s, cx - 120 * s, cy + 25 * s), fill=(*LANTERN_WARM, 18))
    for _ in range(5):
        gx = cx - 165 * s + rng.randint(-15, 15)
        gy = cy + rng.randint(-15, 8) * s
        gr = rng.randint(40, 120)
        gd.ellipse((gx - gr, gy - gr, gx + gr, gy + gr), fill=(255, 220, 160, rng.randint(3, 10)))
    return glow_layer


def _draw_ice_floe(draw: ImageDraw.ImageDraw, x: float, y: float, w: float, h: float, shade: tuple) -> None:
    """Draw a single ice floe as an irregular polygon."""
    pts = []
    steps = max(6, int(w // 15))
    for i in range(steps + 1):
        px = x + w * i / steps
        offset = random.uniform(-h * 0.2, h * 0.15)
        py = y + offset
        pts.append((px, py))
    # bottom edge (underwater — jagged)
    for i in range(steps, -1, -1):
        px = x + w * i / steps
        offset = h + random.uniform(-h * 0.1, h * 0.05)
        py = y + offset
        pts.append((px, py))
    draw.polygon(pts, fill=(*shade, 235))


def _draw_aurora(draw: ImageDraw.ImageDraw, width: int, height: int, rng: random.Random) -> Image.Image:
    """Draw aurora borealis curtain as a separate layer."""
    aurora_layer = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora_layer)

    for ci in range(rng.randint(3, 6)):
        base_y = rng.randint(80, 280)
        amp = rng.randint(20, 60)
        freq = rng.uniform(0.003, 0.008)
        phase = rng.uniform(0, math.tau * 2)
        col = rng.choice(AURORA_COLORS)
        alpha_mult = rng.uniform(0.5, 1.0)

        pts = []
        for wx in range(0, width + 4, 4):
            wy = base_y + math.sin(wx * freq + phase) * amp + math.sin(wx * freq * 2.3 + phase * 0.8) * amp * 0.3
            pts.append((wx, wy + rng.randint(-5, 5)))

        # Vertical taper — aurora is brighter at the base
        for taper in range(3):
            taper_alpha = int(col[3] * alpha_mult * (1 - taper * 0.3))
            if taper_alpha < 5:
                continue
            offset = taper * 18
            line_pts = [(px, py + offset + rng.randint(-2, 2)) for px, py in pts]
            ad.line(line_pts, fill=(col[0], col[1], col[2], taper_alpha), width=12 - taper * 3)

    aurora_layer = aurora_layer.filter(ImageFilter.GaussianBlur(12))
    return aurora_layer


def _draw_compass_rose(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int, rng: random.Random) -> None:
    """Draw a broken compass rose half-buried in ice — symbol of betrayal."""
    # Outer ring (cracked)
    draw.ellipse((cx - size, cy - size, cx + size, cy + size), outline=(70, 60, 45, 160), width=2)
    draw.arc((cx - size, cy - size, cx + size, cy + size), 30, 140, fill=(70, 60, 45, 120), width=1)
    draw.arc((cx - size, cy - size, cx + size, cy + size), 210, 320, fill=(70, 60, 45, 120), width=1)

    # Cardinal points (three visible, one broken off)
    for angle, label in [(0, 'N'), (90, 'E'), (180, 'S'), (270, 'W')]:
        rad = math.radians(angle)
        tip_x = cx + math.sin(rad) * size * 0.75
        tip_y = cy - math.cos(rad) * size * 0.75
        base_x = cx + math.sin(rad) * size * 0.3
        base_y = cy - math.cos(rad) * size * 0.3
        if label == 'W':
            # Broken — just a stub
            draw.line((cx, cy, tip_x * 0.5 + cx * 0.5, tip_y * 0.5 + cy * 0.5), fill=(60, 50, 38, 180), width=3)
        else:
            draw.polygon([
                (tip_x, tip_y),
                (base_x - math.cos(rad) * 8, base_y - math.sin(rad) * 8),
                (base_x + math.cos(rad) * 8, base_y + math.sin(rad) * 8),
            ], fill=(70 + rng.randint(-10, 10), 60 + rng.randint(-10, 10), 45 + rng.randint(-10, 10), 180))

    # Center dot
    draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=(90, 78, 60, 200))


def _draw_torn_map(draw: ImageDraw.ImageDraw, cx: int, cy: int, rng: random.Random) -> None:
    """Draw a torn map fragment on the ice — the cartographer's betrayed work."""
    paper_col = (210, 195, 170)
    pts = [(cx, cy)]
    for i in range(1, 6):
        px = cx + rng.randint(-40, 40)
        py = cy + rng.randint(-30, 20) + i * 14
        pts.append((px, py))
    draw.polygon(pts + [(cx + rng.randint(-20, 20), cy + 85)], fill=(*paper_col, 200))

    # Map lines (coastlines)
    map_lines = [
        [(cx - 15, cy + 12), (cx + 10, cy + 18), (cx + 20, cy + 35), (cx + 8, cy + 50)],
        [(cx + 5, cy + 20), (cx - 10, cy + 40), (cx - 15, cy + 60)],
        [(cx - 8, cy + 30), (cx + 15, cy + 45), (cx + 22, cy + 65), (cx + 10, cy + 78)],
    ]
    for line in map_lines:
        draw.line(line, fill=(80, 70, 55, 120), width=1)

    # Torn edge indicator
    stroke_pts = []
    for i in range(7):
        px = cx + rng.randint(-42, 42)
        py = cy + i * 15
        stroke_pts.append((px, py))
    draw.line(stroke_pts, fill=(190, 180, 160, 180), width=1)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    rng = random.Random()
    rng.seed(abs(hash(title + "cartographer-last-latitude-1742")))

    # ── Base canvas ───────────────────────────────────────────────
    img = Image.new("RGBA", (W, H), (*SKY_TOP, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Arctic sky gradient ───────────────────────────────────────
    for y in range(H):
        t = y / H
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * min(1, t * 2.5))
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * min(1, t * 2.5))
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * min(1, t * 2.5))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # ── Aurora borealis ──────────────────────────────────────────
    aurora = _draw_aurora(draw, W, H, rng)
    img = Image.alpha_composite(img, aurora)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Distant ice horizon (low, jagged line) ───────────────────
    horizon_y = 580
    horizon_pts = []
    for hx in range(0, W + 10, 10):
        hy = horizon_y + math.sin(hx * 0.008 + rng.uniform(0, 2)) * 12 + math.sin(hx * 0.02) * 6
        horizon_pts.append((hx, hy))
    INT_SHADE = (160, 190, 205)
    draw.polygon(horizon_pts + [(W, H), (0, H)],
                 fill=(INT_SHADE[0], INT_SHADE[1], INT_SHADE[2], 150))
    draw.line(horizon_pts, fill=(180, 210, 225, 100), width=2)

    # ── Background icebergs ──────────────────────────────────────
    for bi in range(rng.randint(4, 6)):
        bx = rng.randint(100, W - 100)
        bw = rng.randint(80, 220)
        bh = rng.randint(60, 180)
        by = horizon_y + 40 + rng.randint(-20, 30)
        # Above-water
        draw.polygon([
            (bx - bw // 2, by),
            (bx - bw // 3, by - bh),
            (bx + bw // 4, by - bh * rng.uniform(0.6, 0.9)),
            (bx + bw // 2, by),
        ], fill=(150 + rng.randint(-20, 20), 175 + rng.randint(-10, 15), 195 + rng.randint(-10, 15), 200))
        # Under-water haze (lighter blue)
        draw.polygon([
            (bx - bw // 2, by),
            (bx + bw // 2, by),
            (bx + bw // 3, by + bh * 0.6),
            (bx - bw // 3, by + bh * 0.5),
        ], fill=(80, 120, 140, 80))

    # ── Pack ice (midground — broken ice sheet) ─────────────────
    ice_line_y = int(H * 0.50)
    for ix in range(0, W, rng.randint(40, 90)):
        fw = rng.randint(80, 200)
        fh = rng.randint(15, 35)
        fy = ice_line_y + rng.randint(-30, 50) + math.sin(ix * 0.015) * 20
        shade = (ICE_SHADOW[0] + rng.randint(-20, 20), ICE_SHADOW[1] + rng.randint(-15, 15), ICE_SHADOW[2] + rng.randint(-10, 10))
        _draw_ice_floe(draw, ix - fw // 2, fy, fw, fh, shade)

    # ── The trapped ship (tilted, listing to port) ──────────────
    ship_cx = W // 2 - 60
    ship_cy = int(H * 0.43)
    glow_layer = _draw_ship(draw, ship_cx, ship_cy, 1.0, rng)
    img = Image.alpha_composite(img, glow_layer)

    # ── Foreground ice (large floes pressing against the ship) ──
    foreground_y = int(H * 0.58)
    for fi in range(8):
        fw = rng.randint(140, 300)
        fh = rng.randint(25, 50)
        fx = (fi - 3) * 220 + rng.randint(-30, 30)
        fy = foreground_y + rng.randint(-15, 25) + math.sin(fi * 1.7) * 18
        shade = (ICE_LIGHT[0] - rng.randint(0, 30), ICE_LIGHT[1] - rng.randint(0, 20), ICE_LIGHT[2] - rng.randint(0, 10))
        _draw_ice_floe(draw, fx, fy, fw, fh, shade)
        # Ice highlight edges
        draw.line((fx + 10, fy + 5, fx + fw - 10, fy + rng.randint(3, 10)),
                  fill=(230, 240, 245, rng.randint(30, 70)), width=1)

    # ── Foreground detail: broken compass on the ice ────────────
    _draw_compass_rose(draw, W // 2 + 280, int(H * 0.67), 55, rng)

    # ── Foreground detail: torn map fragment ────────────────────
    _draw_torn_map(draw, W // 2 - 350, int(H * 0.66), rng)

    # ── Ice cracks (fracture lines in foreground ice) ───────────
    for ci in range(rng.randint(5, 9)):
        cx1 = rng.randint(0, W)
        cy1 = int(H * 0.60) + rng.randint(0, int(H * 0.15))
        cpts = [(cx1, cy1)]
        segs = rng.randint(3, 6)
        for si in range(segs):
            nx = cpts[-1][0] + rng.randint(-50, 50)
            ny = cpts[-1][1] + rng.randint(10, 30)
            cpts.append((nx, ny))
        draw.line(cpts, fill=(180, 210, 225, rng.randint(30, 70)), width=1)

    # ── Scattered ice crystals (small bright dots) ──────────────
    for _ in range(rng.randint(60, 120)):
        px = rng.randint(0, W)
        py = rng.randint(int(H * 0.55), int(H * 0.80))
        pr = rng.uniform(1.0, 3.5)
        pa = rng.randint(50, 180)
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(230, 245, 255, pa))

    # ── Falling snow particles (upper area) ─────────────────────
    snow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(snow_layer)
    for _ in range(rng.randint(100, 200)):
        sx = rng.randint(0, W)
        sy = rng.randint(0, int(H * 0.55))
        sr = rng.uniform(1.0, 4.0)
        sa = rng.randint(60, 200)
        sd.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(255, 255, 255, sa))
    img = Image.alpha_composite(img, snow_layer)

    # ── Vignette (subtle darkening at edges) ────────────────────
    for vy in range(H):
        vt = abs(vy - H // 2) / (H // 2)
        vl = 1 - abs(vy - H // 2) / (H // 2)
        vv_h = int(35 * max(0, 1 - vt * 1.5))
        vv_v = int(50 * max(0, 1 - vl * 2))
        if vv_h > 0:
            draw.line((0, vy, vv_h, vy), fill=(0, 0, 0, 60))
            draw.line((W - vv_h, vy, W, vy), fill=(0, 0, 0, 60))
        if vy < vv_v:
            draw.line((0, vy, W, vy), fill=(0, 0, 0, max(0, 30 - vy // 10)))

    # ── Polar night glow at top ─────────────────────────────────
    for ty in range(40):
        t_alpha = int(40 * (1 - ty / 40))
        if t_alpha > 0:
            draw.line((0, ty, W, ty), fill=(10, 15, 35, t_alpha))

    # ── Save ─────────────────────────────────────────────────────
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
