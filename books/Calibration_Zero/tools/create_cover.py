#!/usr/bin/env python3
"""Cover: Calibration Zero — Neural cyberpunk: a black-market calibrator's consciousness-scanner reveals her own memory partitions were never born. Circular calibration ring, sweeping diagnostic beam, dissolving Tokyo skyline, and ghost-corporation watermarks."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# ── Unique palette: deep void indigo, electric cyan, hot magenta, ghost white ──
VOID = (6, 4, 22)
INDIGO_DEEP = (10, 8, 40)
CYAN_NEON = (0, 230, 255)
MAGENTA = (255, 0, 128)
GHOST = (180, 200, 220)
CORP_RED = (180, 30, 40)


def _scanner_ring_poly(cx: float, cy: float, r: float, segments: int = 64) -> list[tuple[float, float]]:
    """Return polygon vertices for a smooth circle approximation."""
    pts = []
    for i in range(segments):
        a = math.tau * i / segments
        pts.append((cx + math.cos(a) * r, cy + math.sin(a) * r))
    return pts


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    rng = random.Random()
    rng.seed(302199410)  # fixed seed for reproducibility

    img = Image.new("RGBA", (W, H), VOID + (255,))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 1. Deep indigo-to-void vertical gradient ─────────────────────────────
    for y in range(H):
        t = y / H
        r = int(VOID[0] + (INDIGO_DEEP[0] - VOID[0]) * (1 - abs(t - 0.3) * 0.8))
        g = int(VOID[1] + (INDIGO_DEEP[1] - VOID[1]) * (1 - abs(t - 0.3) * 0.8))
        b = int(VOID[2] + (INDIGO_DEEP[2] - VOID[2]) * (1 - abs(t - 0.3) * 0.8))
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # ── 2. Perspective grid vanishing to center (neural calibration grid) ────
    vx, vy = W // 2, 950  # vanishing point
    for ring in range(1, 14):
        spread = ring * 120
        alpha = max(3, 25 - ring * 2)
        # Horizontal perspective lines
        for h_line in range(4):
            t_h = (h_line + 0.5) / 4
            y_off = int(vy + math.copysign(spread * t_h * t_h, 1 if h_line >= 2 else -1))
            if 0 < y_off < 1800:
                draw.line((0, y_off, W, y_off), fill=(50, 180, 255, alpha), width=1)
        # Radial lines from vanishing point
        for rad in range(12):
            a = math.tau * rad / 12
            ex = vx + math.cos(a) * spread * 2
            ey = vy + math.sin(a) * spread * 2
            draw.line((vx, vy, int(ex), int(ey)), fill=(50, 180, 255, max(1, alpha - 5)), width=1)

    # ── 3. Large circular neural scanner ring (the dominant focal point) ────
    cx, cy = vx, vy  # scanner centre = vanishing point
    scanner_r = 520

    # Outer ring glow
    glow_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow_layer)
    for gr in range(scanner_r - 20, scanner_r + 30, 5):
        alpha = max(1, 12 - abs(gr - scanner_r) // 3)
        gd.polygon(_scanner_ring_poly(cx, cy, gr), fill=(0, 200, 255, alpha))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, glow_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Main scanner ring (cyan neon)
    draw.polygon(_scanner_ring_poly(cx, cy, scanner_r), outline=(0, 220, 255, 160), width=3)
    # Inner ring (thinner, lighter)
    draw.polygon(_scanner_ring_poly(cx, cy, scanner_r - 35), outline=(0, 240, 255, 90), width=1)
    # Outer thin ring
    draw.polygon(_scanner_ring_poly(cx, cy, scanner_r + 20), outline=(0, 200, 255, 50), width=1)

    # ── 4. Calibration crosshairs at cardinal/ordinal points ────────────────
    for angle_deg in range(0, 360, 45):
        a = math.radians(angle_deg)
        for radius_offset in [scanner_r + 45, scanner_r + 75]:
            tx = cx + math.cos(a) * radius_offset
            ty = cy + math.sin(a) * radius_offset
            tick_len = 12
            dx = math.cos(a) * tick_len
            dy = math.sin(a) * tick_len
            draw.line((tx - dx, ty - dy, tx + dx, ty + dy), fill=(255, 0, 128, 180), width=2)
            # Small dot at each tick
            draw.ellipse((tx - 2, ty - 2, tx + 2, ty + 2), fill=(255, 0, 128, 220))

    # ── 5. The sweeping calibration beam (rotating radar sweep) ────────────
    # Create a radial gradient sweep via layered triangles
    sweep_angle = rng.uniform(0, math.tau)  # fixed position for static image
    sweep_width = math.radians(35)  # beam width

    beam_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam_layer)
    # Build the sweep as a thick triangle fan
    beam_steps = 20
    for i in range(beam_steps):
        t_a = sweep_angle - sweep_width / 2 + sweep_width * i / beam_steps
        r_inner = 30
        r_outer = scanner_r + 30
        pts = [
            (cx + math.cos(t_a) * r_inner, cy + math.sin(t_a) * r_inner),
            (cx + math.cos(t_a) * r_outer, cy + math.sin(t_a) * r_outer),
            (cx + math.cos(t_a + sweep_width / beam_steps) * r_outer,
             cy + math.sin(t_a + sweep_width / beam_steps) * r_outer),
            (cx + math.cos(t_a + sweep_width / beam_steps) * r_inner,
             cy + math.sin(t_a + sweep_width / beam_steps) * r_inner),
        ]
        alpha_sweep = int(40 * (1 - i / beam_steps))
        bd.polygon(pts, fill=(0, 255, 220, alpha_sweep))
    beam_layer = beam_layer.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, beam_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Sweep leading edge (bright line)
    for edge in [sweep_angle - sweep_width / 2, sweep_angle + sweep_width / 2]:
        ex = cx + math.cos(edge) * (scanner_r + 40)
        ey = cy + math.sin(edge) * (scanner_r + 40)
        draw.line((cx, cy, int(ex), int(ey)), fill=(0, 255, 240, 80), width=2)

    # ── 6. Diagnostic readout tick marks around the ring ────────────────────
    for tick_i in range(48):
        tick_angle = math.radians(tick_i * 7.5)
        t_inner = scanner_r - 12 if tick_i % 4 == 0 else scanner_r - 6
        t_outer = scanner_r + 12 if tick_i % 4 == 0 else scanner_r + 6
        tx1 = cx + math.cos(tick_angle) * t_inner
        ty1 = cy + math.sin(tick_angle) * t_inner
        tx2 = cx + math.cos(tick_angle) * t_outer
        ty2 = cy + math.sin(tick_angle) * t_outer
        col = MAGENTA if tick_i % 8 == 0 else (0, 180, 255, 120)
        draw.line((tx1, ty1, tx2, ty2), fill=col, width=2 if tick_i % 4 == 0 else 1)

    # ── 7. Ghostly Tokyo Skyline (partially dissolved, within lower ring) ──
    skyline_y = cy + 200
    tokyo_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tokyo_layer)

    # Tokyo Tower (vague silhouette)
    tt_cx = cx + 80
    tt_base = skyline_y
    tt_h = 250
    # Tower body
    td.polygon([
        (tt_cx - 15, tt_base), (tt_cx + 15, tt_base),
        (tt_cx + 10, tt_base - tt_h + 60),
        (tt_cx + 6, tt_base - tt_h + 60),
        (tt_cx + 6, tt_base - tt_h),
        (tt_cx - 6, tt_base - tt_h),
        (tt_cx - 6, tt_base - tt_h + 60),
        (tt_cx - 10, tt_base - tt_h + 60),
    ], fill=(100, 180, 220, 50), outline=(80, 160, 200, 80))

    # Tokyo Skytree silhouette
    st_cx = cx - 120
    st_base = skyline_y - 40
    st_h = 320
    td.polygon([
        (st_cx - 8, st_base), (st_cx + 8, st_base),
        (st_cx + 5, st_base - st_h + 80),
        (st_cx + 3, st_base - st_h + 80),
        (st_cx + 3, st_base - st_h),
        (st_cx - 3, st_base - st_h),
        (st_cx - 3, st_base - st_h + 80),
        (st_cx - 5, st_base - st_h + 80),
    ], fill=(80, 160, 200, 40), outline=(60, 140, 180, 60))

    # Smaller buildings
    for b_i in range(20):
        bx = cx - 250 + b_i * 25 + rng.randint(-5, 5)
        bw = rng.randint(15, 30)
        bh = rng.randint(60, 180)
        by = skyline_y - bh
        alpha_b = rng.randint(15, 35)
        bcol = (40 + rng.randint(0, 30), 80 + rng.randint(0, 40), 140 + rng.randint(0, 40), alpha_b)
        td.rectangle((bx, by, bx + bw, skyline_y), fill=bcol)
        # A few lit windows
        if rng.random() < 0.3:
            for wy in range(by + 4, skyline_y - 4, rng.randint(8, 14)):
                for wx in range(bx + 3, bx + bw - 3, rng.randint(6, 12)):
                    if rng.random() < 0.4:
                        td.rectangle((wx, wy, wx + 3, wy + 3), fill=(255, 220, 150, rng.randint(20, 60)))

    # Gradually dissolve the right side of the skyline into particles
    dissolve_mask = Image.new("L", (W, H), 0)
    dm_draw = ImageDraw.Draw(dissolve_mask)
    for y_px in range(skyline_y - 400, skyline_y + 10):
        for x_px in range(cx + 80, W):
            dist = (x_px - (cx + 80)) / (W - cx - 80)
            if dist > 0.3 and rng.random() < dist * 0.6:
                continue  # skip many pixels → dissolve effect
            dm_draw.point((x_px, y_px), fill=255)
    tokyo_layer = Image.composite(tokyo_layer, Image.new("RGBA", (W, H), (0, 0, 0, 0)), dissolve_mask)
    img = Image.alpha_composite(img, tokyo_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── 8. Ghost-corporation watermark (faded logo: double circle + crosshair) ──
    logo_cx, logo_cy = W - 200, 550
    # Outer ring (degraded)
    for lr in range(55, 65, 5):
        draw.polygon(_scanner_ring_poly(logo_cx, logo_cy, lr), outline=(150, 25, 35, max(1, 40 - lr)), width=1)
    # Inner ring
    draw.polygon(_scanner_ring_poly(logo_cx, logo_cy, 30), outline=(150, 25, 35, 50), width=1)
    # Crosshair
    draw.line((logo_cx - 70, logo_cy, logo_cx + 70, logo_cy), fill=(150, 25, 35, 35), width=1)
    draw.line((logo_cx, logo_cy - 70, logo_cx, logo_cy + 70), fill=(150, 25, 35, 35), width=1)
    # Central dot
    draw.ellipse((logo_cx - 3, logo_cy - 3, logo_cx + 3, logo_cy + 3), fill=(160, 30, 40, 60))

    # Faded "ARCHIVE" text (just geometric suggestion — no real text rendering dependency)
    # represented as horizontal line segments suggesting text
    archive_y = logo_cy + 80
    for seg_i in range(18):
        sx = logo_cx - 50 + seg_i * 5
        draw.line((sx, archive_y, sx + 3, archive_y), fill=(150, 30, 40, max(1, 35 - seg_i)), width=1)

    # ── 9. Memory fragment particles (floating data shards) ─────────────────
    for _ in range(150):
        px = rng.randint(0, W)
        py = rng.randint(200, 1700)
        size = rng.randint(2, 7)
        alpha_p = rng.randint(30, 130)
        # Choose fragment style
        style = rng.random()
        if style < 0.4:
            # Cyan data dot
            col = (0, 200 + rng.randint(0, 55), 255, alpha_p)
            draw.ellipse((px - size, py - size, px + size, py + size), fill=col)
        elif style < 0.7:
            # Magenta shard (diamond)
            col = (255, rng.randint(0, 50), 128 + rng.randint(0, 50), alpha_p)
            draw.polygon([
                (px, py - size),
                (px + size, py),
                (px, py + size),
                (px - size, py),
            ], fill=col)
        else:
            # Ghost-white hex fragment
            col = (180 + rng.randint(0, 40), 200 + rng.randint(0, 30), 220, alpha_p)
            hex_pts = []
            for hi in range(6):
                ha = math.radians(hi * 60 + 30)
                hex_pts.append((px + math.cos(ha) * size, py + math.sin(ha) * size))
            draw.polygon(hex_pts, fill=col)

    # ── 10. Vertical data-stream lines (like Tokyo neon + diagnostic feed) ──
    for _ in range(25):
        dx = rng.randint(30, W - 30)
        dy_start = rng.randint(50, 1200)
        dy_len = rng.randint(100, 500)
        col_type = rng.random()
        if col_type < 0.5:
            dcol = (0, 180 + rng.randint(0, 75), 255, rng.randint(5, 20))
        else:
            dcol = (255, rng.randint(0, 40), 128 + rng.randint(0, 50), rng.randint(5, 18))
        draw.line((dx, dy_start, dx, dy_start + dy_len), fill=dcol, width=1)

    # ── 11. Horizontal diagnostic waveform (EEG-style) across the ring ──────
    wave_y = cy + 320
    wave_pts = []
    for wx in range(0, W, 3):
        t_w = wx / W
        amplitude = 25 * (1 - abs(t_w - 0.5) * 0.6)
        wave = math.sin(t_w * math.tau * 4 + 1.3) * 0.6 \
             + math.sin(t_w * math.tau * 11 + 2.7) * 0.3 \
             + math.sin(t_w * math.tau * 27 + 0.5) * 0.1
        wy = wave_y + wave * amplitude
        wave_pts.append((wx, wy))
    for wi in range(len(wave_pts) - 1):
        alpha_w = int(60 + 40 * abs(math.sin(wi * 0.3)))
        draw.line((wave_pts[wi], wave_pts[wi + 1]), fill=(0, 200, 255, max(1, alpha_w)), width=2)

    # ── 12. Vignette (subtle) ──────────────────────────────────────────────
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(40 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 70))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 70))

    # ── 13. A few bright "ping" dots on the scanner ring (detections) ──────
    for _ in range(8):
        angle_p = rng.uniform(0, math.tau)
        pr = scanner_r + rng.randint(-10, 10)
        px = cx + math.cos(angle_p) * pr
        py = cy + math.sin(angle_p) * pr
        glow_r = rng.randint(6, 14)
        # Outer glow
        g_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd2 = ImageDraw.Draw(g_layer)
        gd2.ellipse((px - glow_r, py - glow_r, px + glow_r, py + glow_r),
                     fill=(0, 255, 240, 40))
        # Inner bright dot
        gd2.ellipse((px - 3, py - 3, px + 3, py + 3),
                     fill=(200, 255, 255, 180))
        g_layer = g_layer.filter(ImageFilter.GaussianBlur(5))
        img = Image.alpha_composite(img, g_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Save ────────────────────────────────────────────────────────────────
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
