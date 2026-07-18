#!/usr/bin/env python3
"""Cover: The Last Clean Water Pact — drought-cracked dystopian wasteland with a looming corporate water tower, hidden aquifer glow beneath parched earth, and a lone figure dwarfed by industrial control."""

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
rng.seed(20260718)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Arid gradient: harsh bleached-yellow sky → dusty orange → deep burnt-brown ──
    for y in range(H):
        t = y / H
        if t < 0.35:
            s = t / 0.35
            r = int(225 + 15 * s)
            g = int(190 - 15 * s)
            b = int(125 - 50 * s)
        else:
            s = (t - 0.35) / 0.65
            r = int(185 - 100 * s)
            g = int(135 - 90 * s)
            b = int(55 - 40 * s)
        draw.line((0, y, W, y), fill=(min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)), 255))

    # ── Blistering sun with broad heat glow ──
    sun_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sgd = ImageDraw.Draw(sun_glow)
    scx, scy = W // 2, 130
    for rad in range(320, 30, -20):
        alpha = max(0, 55 - (320 - rad) // 6)
        sgd.ellipse((scx - rad, scy - rad, scx + rad, scy + rad),
                     fill=(255, 225, 160, alpha))
    sun_glow = sun_glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(img, sun_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Sun core
    draw.ellipse((scx - 35, scy - 35, scx + 35, scy + 35), fill=(255, 240, 210, 240))
    # White-hot center
    draw.ellipse((scx - 12, scy - 12, scx + 12, scy + 12), fill=(255, 252, 245, 200))

    # ── Distant arid horizon ridges ──
    horizon_y = 1050
    for mi in range(5):
        pts = []
        step = max(1, W // 20)
        for sx in range(-step, W + step + 1, step // 2):
            noise = rng.randint(-25, 35)
            h_off = 180 + mi * 45 + noise
            pts.append((sx, horizon_y + h_off))
        pts.append((W + step, H))
        pts.append((-step, H))
        base = max(0, 60 - mi * 10)
        col = (base + 10, base - 5, base - 10)
        draw.polygon(pts, fill=(max(0, col[0]), max(0, col[1]), max(0, col[2]), 210 - mi * 15))

    # ── Corporate water tower (AquaCorp) ──
    tw_x = W // 2
    tw_y = 920

    # Tower legs
    for leg_off in (-130, 130):
        leg_w = 10
        draw.polygon([
            (tw_x + leg_off - leg_w, tw_y),
            (tw_x + leg_off + leg_w, tw_y),
            (tw_x + leg_off + leg_w // 2, horizon_y + 130),
            (tw_x + leg_off - leg_w // 2, horizon_y + 130),
        ], fill=(72, 77, 82, 230))

    # Cross-bracing
    for b_off in range(-90, 121, 60):
        lx = tw_x + b_off
        rx = tw_x + b_off + 60
        ly = tw_y + 10
        ry = horizon_y + 60 + (b_off // 10) * 8
        draw.line((lx, ly, rx, ry), fill=(85, 90, 95, 140), width=3)
        draw.line((rx, ly, lx, ry), fill=(85, 90, 95, 120), width=2)

    # Tank body
    tank_top = tw_y - 200
    tank_bot = tw_y + 50
    tank_w = 220
    draw.rectangle((tw_x - tank_w // 2, tank_top, tw_x + tank_w // 2, tank_bot),
                    fill=(82, 87, 92, 230))
    draw.rectangle((tw_x - tank_w // 2, tank_top, tw_x + tank_w // 2, tank_bot),
                    fill=None, outline=(115, 120, 125, 160), width=2)

    # Dome roof
    draw.ellipse((tw_x - tank_w // 2, tank_top - 45, tw_x + tank_w // 2, tank_top + 45),
                  fill=(90, 95, 100, 230))

    # Water level indicator (red danger band — nearly empty)
    draw.rectangle((tw_x - tank_w // 2 + 12, tank_bot - 28, tw_x + tank_w // 2 - 12, tank_bot - 16),
                    fill=(185, 45, 40, 200))
    # Low-water warning stripe
    draw.rectangle((tw_x - tank_w // 2 + 12, tank_bot - 48, tw_x + tank_w // 2 - 12, tank_bot - 36),
                    fill=(195, 55, 45, 150))

    # Corporate logo (stylized "AQ" as geometric shapes — circle + chevron)
    logo_cx = tw_x
    logo_cy = tank_top + 45
    draw.ellipse((logo_cx - 24, logo_cy - 24, logo_cx + 24, logo_cy + 24),
                  fill=None, outline=(140, 145, 150, 140), width=3)
    # Chevron A inside circle
    draw.polygon([(logo_cx - 12, logo_cy + 10), (logo_cx, logo_cy - 14), (logo_cx + 12, logo_cy + 10)],
                  fill=None, outline=(140, 145, 150, 160), width=2)
    # Crossbar of A
    draw.line((logo_cx - 6, logo_cy - 2, logo_cx + 6, logo_cy - 2), fill=(140, 145, 150, 140), width=2)
    # Drop shape beside it (Q tail)
    draw.ellipse((logo_cx + 14, logo_cy + 2, logo_cx + 24, logo_cy + 16), fill=(140, 145, 150, 120))

    # ── Pipeline network radiating from tower ──
    # Horizontal trunk lines
    for py_off in (90, -20):
        py = tank_top + py_off
        for direction in (-1, 1):
            px_start = tw_x + direction * (tank_w // 2)
            px_end = tw_x + direction * 750
            draw.line((px_start, py, px_end, py), fill=(88, 93, 98, 170), width=8)
            # Pipe flanges/joins
            for fx in range(px_start, px_end, direction * 80):
                draw.line((fx, py - 6, fx, py + 6), fill=(110, 115, 120, 190), width=3)
            # Valve wheel at midpoint
            vx = tw_x + direction * 400
            draw.ellipse((vx - 12, py - 12, vx + 12, py + 12),
                          fill=None, outline=(120, 125, 130, 160), width=2)
            draw.line((vx - 6, py, vx + 6, py), fill=(120, 125, 130, 150), width=2)
            draw.line((vx, py - 6, vx, py + 6), fill=(120, 125, 130, 150), width=2)

    # Vertical support posts for pipes
    for post_x in (tw_x - 500, tw_x + 500, tw_x - 300, tw_x + 300):
        draw.line((post_x, 920, post_x, 1100), fill=(65, 70, 75, 160), width=5)

    # ── Cracked earth foreground ──
    crack_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(crack_layer)

    # Primary crack origins
    for _ in range(8):
        ox = rng.randint(80, W - 80)
        oy = rng.randint(1500, 2100)
        for _ in range(rng.randint(3, 6)):
            pts = [(ox, oy)]
            angle = rng.uniform(-math.pi, math.pi)
            total_len = rng.randint(100, 300)
            segments = rng.randint(5, 10)
            for seg in range(segments):
                px, py = pts[-1]
                angle += rng.uniform(-0.5, 0.5)
                seg_l = total_len / segments * rng.uniform(0.6, 1.4)
                nx = px + math.cos(angle) * seg_l
                ny = py + math.sin(angle) * seg_l * 0.55 + 8
                pts.append((int(nx), int(ny)))
            thickness = rng.randint(2, 5)
            cd.line(pts, fill=(25, 15, 8, 190), width=thickness)

    # Fine secondary cracks
    for _ in range(80):
        sx = rng.randint(0, W)
        sy = rng.randint(1400, H)
        pts = [(sx, sy)]
        for _ in range(rng.randint(2, 5)):
            px, py = pts[-1]
            pts.append((px + rng.randint(-50, 50), py + rng.randint(-20, 70)))
        cd.line(pts, fill=(35, 22, 12, 120), width=rng.randint(1, 2))

    img = Image.alpha_composite(img, crack_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Hidden aquifer glow beneath the cracks ──
    aquifer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aquifer)
    aq_cx, aq_cy = W // 2, 1750
    for rad_step in range(10):
        rad_x = 320 - rad_step * 28
        rad_y = 160 - rad_step * 14
        alpha = max(0, 45 - rad_step * 4)
        ad.ellipse((aq_cx - rad_x, aq_cy - rad_y, aq_cx + rad_x, aq_cy + rad_y),
                    fill=(20, 165, 195, alpha))
    aquifer = aquifer.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, aquifer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Aquifer water shimmer veins
    for _ in range(20):
        sx = rng.randint(350, 1250)
        sy = rng.randint(1580, 1900)
        pts = [(sx, sy)]
        for _ in range(rng.randint(2, 4)):
            px, py = pts[-1]
            pts.append((px + rng.randint(-40, 40), py + rng.randint(8, 20)))
        draw.line(pts, fill=(80, 210, 235, rng.randint(15, 50)), width=rng.randint(1, 3))

    # ── Lone figure: Dr. Sasha Okonkwo ──
    fig_x = W // 2 + 200
    fig_y = 1150
    fig_h = 150

    # Shadow on ground
    draw.ellipse((fig_x - 28, fig_y - 4, fig_x + 28, fig_y + 4), fill=(15, 10, 5, 100))

    # Legs
    draw.line((fig_x - 5, fig_y - 50, fig_x - 8, fig_y), fill=(8, 8, 12, 200), width=5)
    draw.line((fig_x + 5, fig_y - 50, fig_x + 8, fig_y), fill=(8, 8, 12, 200), width=5)
    # Torso
    draw.polygon([(fig_x - 10, fig_y - 50), (fig_x + 10, fig_y - 50),
                   (fig_x + 12, fig_y - 120), (fig_x - 12, fig_y - 120)],
                  fill=(10, 10, 15, 210))
    # Head
    draw.ellipse((fig_x - 9, fig_y - 145, fig_x + 9, fig_y - 125), fill=(12, 12, 18, 210))
    # Arms
    draw.line((fig_x - 12, fig_y - 110, fig_x - 30, fig_y - 70), fill=(10, 10, 15, 200), width=4)
    draw.line((fig_x + 12, fig_y - 110, fig_x + 28, fig_y - 75), fill=(10, 10, 15, 200), width=4)

    # ── Heat haze shimmer ──
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(12):
        hx = rng.randint(200, 1400)
        hy = rng.randint(200, 700)
        hw = rng.randint(100, 300)
        hd.ellipse((hx - hw, hy - 8, hx + hw, hy + 8), fill=(200, 180, 140, 6))
    haze = haze.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, haze)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Dust particles ──
    for _ in range(100):
        dx = rng.randint(0, W)
        dy = rng.randint(100, 1400)
        dr = rng.randint(1, 3)
        da = rng.randint(15, 55)
        col = rng.choice([(180, 155, 110), (200, 170, 120), (160, 140, 100)])
        draw.ellipse((dx - dr, dy - dr, dx + dr, dy + dr), fill=(*col, da))

    # ── Holographic corporate overlay (surveillance/credit grid) ──
    holo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(holo)
    for gy in range(350, 1050, 35):
        alpha = max(0, 12 - abs(gy - 700) // 50)
        if alpha > 0:
            hd.line((0, gy, W, gy), fill=(160, 190, 220, alpha), width=1)
    for gx in range(0, W, 35):
        hd.line((gx, 350, gx, 1050), fill=(160, 190, 220, 5), width=1)
    holo = holo.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, holo)
    draw = ImageDraw.Draw(img, "RGBA")

    # ── Faint "HYDRATION CREDIT" text overlay (illegible, just texture) ──
    for _ in range(6):
        tx = rng.randint(100, 1500)
        ty = rng.randint(450, 900)
        for ch_i in range(5):
            cx = tx + ch_i * 12
            draw.rectangle((cx, ty, cx + 8, ty + 10), fill=(150, 175, 200, rng.randint(5, 12)))

    # ── Save ──
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
