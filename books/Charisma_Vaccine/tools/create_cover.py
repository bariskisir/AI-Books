#!/usr/bin/env python3
"""Cover: Charisma Vaccine — Dystopian social satire: a failed influencer discovers an underground clinic selling a vaccine to permanently reduce charisma, escaping the social credit system."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

# Clinical-sterile top fading into cold city-night bottom
# Palette: sterile white/ice-blue → charcoal, with piercing clinical green and rating red accents
CR = (210, 220, 225)   # top: clinical white
CM = (140, 155, 165)   # mid: steel grey
CL = (25, 30, 40)      # bottom: night city

ACCENT_GREEN = (50, 220, 140)    # social credit positive
ACCENT_RED = (230, 50, 60)       # social credit negative
ACCENT_BLUE = (60, 180, 255)     # clinical / digital
ACCENT_YELLOW = (240, 200, 40)   # warning

rng = random.Random()
rng.seed(9137402561)


def _gaussian(center, spread):
    """Return a random gaussian-ish integer around center."""
    return int(center + sum(rng.uniform(-1, 1) for _ in range(6)) * spread)


def _draw_gradient(draw):
    """Three-segment vertical gradient: clinical white top → steel mid → night bottom."""
    for y in range(H):
        t = y / H
        if t < 0.4:
            # top segment: CR → CM
            lt = t / 0.4
            r = int(CR[0] + (CM[0] - CR[0]) * lt)
            g = int(CR[1] + (CM[1] - CR[1]) * lt)
            b = int(CR[2] + (CM[2] - CR[2]) * lt)
        elif t < 0.7:
            # middle segment: CM → CL
            lt = (t - 0.4) / 0.3
            r = int(CM[0] + (CL[0] - CM[0]) * lt)
            g = int(CM[1] + (CL[1] - CM[1]) * lt)
            b = int(CM[2] + (CL[2] - CM[2]) * lt)
        else:
            # bottom: hold CL
            r, g, b = CL
        draw.line((0, y, W, y), fill=(r, g, b, 255))


def _draw_social_credit_ui(draw):
    """Floating UI panels showing social credit scores, ratings, bar charts."""
    ui_alpha = 160

    # --- Large animated credit-score badge (upper-right area) ---
    score = 943  # looks high but is ominous
    bx, by = 1150, 380
    # Glow behind badge
    for rad in range(30, 10, -5):
        alpha = max(10, 30 - rad)
        draw.ellipse((bx - rad, by - rad, bx + rad, by + rad),
                     fill=(*ACCENT_GREEN, alpha))
    # Badge background
    draw.rounded_rectangle((bx - 90, by - 45, bx + 90, by + 45),
                           radius=12, fill=(15, 18, 25, 200), outline=(*ACCENT_GREEN, 120), width=2)
    # Score number
    draw.text((bx - 65, by - 30), "SOCIAL", fill=(160, 170, 180, 200), font=None)
    draw.text((bx - 65, by - 10), "CREDIT", fill=(160, 170, 180, 200), font=None)
    draw.text((bx - 65, by + 8), str(score), fill=(*ACCENT_GREEN, 220), font=None)

    # --- Rating bar charts (left side) ---
    bar_x0 = 80
    bar_y0 = 250
    categories = [
        ("CONFORMITY", 0.92, ACCENT_GREEN),
        ("LOYALTY", 0.88, ACCENT_GREEN),
        ("CONSUMPTION", 0.78, ACCENT_YELLOW),
        ("NETWORKING", 0.65, ACCENT_YELLOW),
        ("AUTHENTICITY", 0.31, ACCENT_RED),
        ("INDEPENDENCE", 0.12, ACCENT_RED),
    ]
    for i, (label, pct, color) in enumerate(categories):
        yp = bar_y0 + i * 52
        # label
        draw.text((bar_x0, yp), label, fill=(160, 170, 180, ui_alpha), font=None)
        # bar background
        draw.rectangle((bar_x0 + 220, yp + 2, bar_x0 + 420, yp + 18),
                       fill=(40, 45, 55, 150), outline=(60, 65, 75, 100), width=1)
        # bar fill
        fill_w = int(200 * pct)
        draw.rectangle((bar_x0 + 220, yp + 2, bar_x0 + 220 + fill_w, yp + 18),
                       fill=(*color, 180))
        # percentage
        draw.text((bar_x0 + 430, yp), f"{int(pct * 100)}%", fill=(*color, 200), font=None)

    # --- Warning overlay: CHARISMA DETECTED ---
    warn_x, warn_y = W // 2 - 100, 650
    draw.rounded_rectangle((warn_x, warn_y, warn_x + 200, warn_y + 40),
                           radius=6, fill=(*ACCENT_RED, 160), outline=(*ACCENT_RED, 220), width=2)
    draw.text((warn_x + 12, warn_y + 8), "! CHARISMA DETECTED", fill=(255, 255, 255, 230), font=None)

    # --- Small floating data points ---
    for _ in range(8):
        dx = rng.randint(100, 1500)
        dy = rng.randint(150, 600)
        val = rng.choice(["+2.4", "-1.7", "+0.8", "-3.2", "+5.1", "-0.3"])
        is_pos = val.startswith("+")
        col = ACCENT_GREEN if is_pos else ACCENT_RED
        draw.text((dx, dy), val, fill=(*col, rng.randint(80, 160)), font=None)

    # --- Grid lines (clinical data overlay) ---
    for gx in range(0, W, 80):
        draw.line((gx, 0, gx, 1700), fill=(80, 90, 110, 12), width=1)
    for gy in range(0, 1700, 80):
        draw.line((0, gy, W, gy), fill=(80, 90, 110, 12), width=1)

    # --- QR-like data matrix in corner ---
    qx, qy = 60, 100
    for row in range(9):
        for col in range(9):
            if rng.random() < 0.55:
                sz = 4
                draw.rectangle((qx + col * 8, qy + row * 8, qx + col * 8 + sz, qy + row * 8 + sz),
                               fill=(*ACCENT_GREEN, rng.randint(30, 80)))


def _draw_syringe(img, draw):
    """Central giant glass/clinical syringe — the vaccine itself."""
    cx, cy = W // 2, 1050
    # Syringe body (cylinder)
    body_w, body_h = 70, 420
    bx0, bx1 = cx - body_w // 2, cx + body_w // 2
    by0, by1 = cy - body_h // 2, cy + body_h // 2

    # Glass body gradient
    glass = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glass)
    for y in range(by0, by1):
        t = (y - by0) / body_h
        alpha = int(30 + 50 * (1 - abs(t - 0.5) * 2))
        gd.line((bx0 + 4, y, bx1 - 4, y), fill=(180, 210, 230, alpha))

    # Fluid inside (translucent green serum)
    fluid_top = by0 + 80
    fluid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fluid)
    for x in range(bx0 + 8, bx1 - 8, 2):
        for y in range(fluid_top, by1 - 20):
            t = (y - fluid_top) / (by1 - 20 - fluid_top)
            alpha = int(30 + 60 * (1 - t))
            fd.point((x, y), fill=(*ACCENT_GREEN, alpha))

    # Bubbles inside fluid
    for _ in range(rng.randint(8, 15)):
        bb_x = rng.randint(bx0 + 12, bx1 - 12)
        bb_y = rng.randint(fluid_top + 10, by1 - 30)
        bb_r = rng.randint(2, 8)
        fd.ellipse((bb_x - bb_r, bb_y - bb_r, bb_x + bb_r, bb_y + bb_r),
                   fill=(255, 255, 255, rng.randint(30, 80)))

    composite_combo = Image.alpha_composite(glass, fluid)
    img.alpha_composite(composite_combo)

    # Glass highlights
    draw.line((bx0 + 10, by0 + 4, bx0 + 10, by1 - 4), fill=(255, 255, 255, 60), width=3)
    draw.line((bx1 - 10, by0 + 4, bx1 - 10, by1 - 4), fill=(200, 220, 240, 30), width=2)

    # Syringe neck
    neck_w, neck_h = 20, 60
    nx0, nx1 = cx - neck_w // 2, cx + neck_w // 2
    ny0, ny1 = by1, by1 + neck_h
    draw.rectangle((nx0, ny0, nx1, ny1), fill=(160, 190, 210, 200))
    draw.rectangle((nx0 + 2, ny0, nx0 + 6, ny1), fill=(255, 255, 255, 50))
    draw.rectangle((nx1 - 6, ny0, nx1 - 2, ny1), fill=(200, 220, 240, 30))

    # Needle
    needle_len = 160
    draw.polygon([
        (cx - 5, ny1),
        (cx + 5, ny1),
        (cx + 1, ny1 + needle_len),
        (cx - 1, ny1 + needle_len),
    ], fill=(140, 150, 165, 220))
    # Needle highlight
    draw.line((cx - 2, ny1, cx - 1, ny1 + needle_len), fill=(255, 255, 255, 40), width=1)

    # Needle tip droplet
    droplet_x, droplet_y = cx, ny1 + needle_len + 6
    draw.ellipse((droplet_x - 5, droplet_y - 5, droplet_x + 5, droplet_y + 5),
                 fill=(*ACCENT_GREEN, 200))

    # Plunger rod
    plunger_top = by0 - 100
    draw.rectangle((cx - 6, plunger_top, cx + 6, by0), fill=(100, 110, 125, 220))

    # Plunger handle
    handle_h = 35
    draw.rectangle((cx - 40, plunger_top - handle_h, cx + 40, plunger_top),
                   fill=(80, 90, 105, 230), outline=(120, 130, 145, 180), width=2)
    draw.rectangle((cx - 30, plunger_top - handle_h + 6, cx + 30, plunger_top - 6),
                   fill=(60, 70, 85, 200))

    # Syringe body outline
    draw.rounded_rectangle((bx0, by0, bx1, by1), radius=8,
                           outline=(160, 190, 210, 150), width=2)

    # Volume markings on the syringe
    for mark_i in range(7):
        my = by0 + 35 + mark_i * 50
        if my > by1 - 20:
            break
        ml = bx0 + 4
        draw.line((ml, my, ml + 15, my), fill=(200, 210, 230, 120), width=1)
        draw.text((ml - 28, my - 6), f"{6 - mark_i}", fill=(180, 190, 210, 100), font=None)

    # Glow emanating from the needle tip
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((droplet_x - 60, droplet_y - 60, droplet_x + 60, droplet_y + 60),
               fill=(*ACCENT_GREEN, 15))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    img.alpha_composite(glow)


def _draw_crowd_silhouette(draw):
    """Faceless identical silhouettes at the bottom — conformity."""
    base_y = 1650
    spacing = 52
    total = W // spacing + 2
    for i in range(total):
        x = i * spacing + rng.randint(-8, 8)
        # Slight height variation but eerily similar
        h = 180 + rng.randint(-15, 15)
        # Head
        draw.ellipse((x - 18, base_y - h, x + 18, base_y - h + 40),
                     fill=(15, 18, 25, 210))
        # Body
        body_pts = [
            (x - 22, base_y - h + 36),
            (x + 22, base_y - h + 36),
            (x + 28, base_y),
            (x - 28, base_y),
        ]
        draw.polygon(body_pts, fill=(15, 18, 25, 210))
        # Every 4th person has a red "rating" dot on their head
        if i % 4 == 0:
            draw.ellipse((x - 5, base_y - h - 6, x + 5, base_y - h + 4),
                         fill=(*ACCENT_RED, rng.randint(80, 160)))
        elif i % 7 == 0:
            draw.ellipse((x - 4, base_y - h - 5, x + 4, base_y - h + 3),
                         fill=(*ACCENT_GREEN, rng.randint(60, 120)))


def _draw_scan_lines(draw):
    """Subtle horizontal scan lines like a CRT monitor — surveillance theme."""
    for y in range(0, 1700, 4):
        draw.line((0, y, W, y), fill=(0, 0, 0, 6), width=1)


def _draw_city_silhouette_background(draw):
    """Faint city skyline behind the syringe — the surveillance state."""
    for _ in range(rng.randint(18, 30)):
        bx = rng.randint(0, W)
        bw = rng.randint(30, 80)
        bh = rng.randint(80, 300)
        col = rng.randint(10, 20)
        draw.rectangle((bx, 1500 - bh, bx + bw, 1500),
                       fill=(col, col + 2, col + 5, 100))
        # Occasional lit window
        if rng.random() < 0.25:
            wx = bx + rng.randint(4, bw - 10)
            wy = 1500 - bh + rng.randint(4, bh - 10)
            draw.rectangle((wx, wy, wx + 6, wy + 6),
                           fill=(*ACCENT_YELLOW, rng.randint(20, 60)))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (30, 35, 45, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # 1. Background gradient
    _draw_gradient(draw)

    # 2. City silhouette behind everything
    _draw_city_silhouette_background(draw)

    # 3. Social credit UI overlays (data panels, scores, bar charts)
    _draw_social_credit_ui(draw)

    # 4. Scan lines (surveillance)
    _draw_scan_lines(draw)

    # 5. Central syringe — the vaccine
    _draw_syringe(img, draw)

    # 6. Faceless crowd silhouette at bottom
    _draw_crowd_silhouette(draw)

    # 7. Vignette
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(30 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 100))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 100))

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
