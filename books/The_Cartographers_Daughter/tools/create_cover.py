#!/usr/bin/env python3
"""Cover: The Cartographer's Daughter — antique map, uncharted island, sailing ship."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(n, s):
    candidates = [FONT_DIR / n, FONT_DIR / "georgiab.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()


def wrap(d, t, f, w):
    words = t.split()
    lines = []
    cur = []
    for wd in words:
        p = " ".join(cur + [wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w:
            cur.append(wd)
        else:
            lines.append(" ".join(cur))
            cur = [wd]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(d, y, lines, f, fl, g):
    for l in lines:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), l, font=f, fill=fl)
        y += bb[3] - bb[1] + g
    return y


def make_cover(mp, op):
    meta = json.loads(mp.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    # Parchment-toned base image
    img = Image.new("RGBA", (W, H), (210, 180, 140, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Parchment gradient — darker at edges, lighter center (antique map look)
    for y in range(H):
        t = y / H
        r = int(180 + 30 * (1 - abs(t - 0.5) * 1.2))
        g = int(150 + 30 * (1 - abs(t - 0.5) * 1.2))
        b = int(100 + 40 * (1 - abs(t - 0.5) * 1.2))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Aged paper texture — scattered speckles
    for _ in range(3000):
        sx, sy = random.randint(0, W), random.randint(0, H)
        sr = random.randint(1, 3)
        sd = random.randint(40, 80)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(sd, sd, sd, 30))

    # Compass rose (upper left area)
    cx, cy = 200, 300
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        length = 80 if angle % 90 == 0 else 50
        ex = cx + length * math.cos(rad)
        ey = cy + length * math.sin(rad)
        draw.line((cx, cy, ex, ey), fill=(120, 90, 50, 200), width=3)
    # Compass circle
    draw.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), outline=(120, 90, 50, 180), width=3)
    draw.ellipse((cx - 100, cy - 100, cx + 100, cy + 100), outline=(120, 90, 50, 100), width=1)
    # N label
    nf = font("arial.ttf", 36)
    draw.text((cx - 15, cy - 125), "N", font=nf, fill=(180, 60, 40, 220))

    # Rhumb lines (navigational lines crossing the map)
    for _ in range(20):
        rx1, ry1 = random.randint(0, W), random.randint(0, 1600)
        rx2, ry2 = random.randint(0, W), random.randint(0, 1600)
        draw.line((rx1, ry1, rx2, ry2), fill=(140, 110, 70, 30), width=1)

    # Uncharted island in center
    island_center = (W // 2, 750)
    # Draw island as irregular polygon
    island_points = []
    num_points = 16
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        base_radius = 180 + random.randint(-30, 30)
        # Make it irregular
        if i % 3 == 0:
            base_radius += 50
        if i % 5 == 0:
            base_radius -= 40
        px = island_center[0] + int(base_radius * math.cos(angle))
        py = island_center[1] + int(base_radius * 0.7 * math.sin(angle))
        island_points.append((px, py))
    draw.polygon(island_points, fill=(160, 140, 90, 220), outline=(100, 80, 40, 200), width=3)

    # Island interior detail — hills and shading
    for _ in range(30):
        hx = island_center[0] + random.randint(-120, 120)
        hy = island_center[1] + random.randint(-100, 100)
        hr = random.randint(10, 30)
        draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=(140, 120, 80, 100))

    # Coast soundings (depth numbers)
    sf = font("arial.ttf", 18)
    for _ in range(12):
        sx = island_center[0] + int(220 * math.cos(random.random() * 2 * math.pi))
        sy = island_center[1] + int(160 * math.sin(random.random() * 2 * math.pi))
        depth = str(random.randint(5, 40))
        draw.text((sx, sy), depth, font=sf, fill=(100, 80, 50, 120))

    # Sea monsters / mythical creatures
    # Sea serpent coil
    sx_start, sy_start = 1100, 500
    for i in range(8):
        sx = sx_start + i * 20
        sy = sy_start + int(25 * math.sin(i * 0.8))
        draw.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), fill=(100, 140, 120, 80))
    # Head
    draw.ellipse((sx_start + 160, sy_start - 20, sx_start + 190, sy_start + 10), fill=(80, 120, 100, 100))

    # Sailing ship silhouette (upper right area)
    ship_x, ship_y = 1250, 600
    # Hull
    draw.polygon(
        [(ship_x - 100, ship_y), (ship_x - 120, ship_y + 40), (ship_x + 100, ship_y + 40), (ship_x + 80, ship_y)],
        fill=(60, 50, 35, 200),
    )
    # Masts
    for mx, mh in [(ship_x - 30, -120), (ship_x, -150), (ship_x + 30, -120)]:
        draw.line((mx, ship_y, mx, ship_y + mh), fill=(50, 40, 30, 200), width=4)
    # Sails
    for mx, mh, sw, sh in [
        (ship_x - 30, -110, 30, 60),
        (ship_x, -140, 40, 70),
        (ship_x + 30, -110, 30, 60),
    ]:
        draw.ellipse((mx - sw, ship_y + mh, mx + sw, ship_y + mh + sh), fill=(80, 70, 55, 180))

    # "Uncharted" label on map area
    ul = font("arial.ttf", 24)
    draw.text((island_center[0] - 60, island_center[1] + 130), "TERRA INCOGNITA", font=ul, fill=(120, 90, 50, 150))

    # Latitude / Longitude lines on edges
    for _ in range(6):
        ly = random.randint(100, 1500)
        draw.line((0, ly, W, ly), fill=(160, 130, 90, 40), width=1)
    for _ in range(4):
        lx = random.randint(50, 1550)
        draw.line((lx, 0, lx, 1800), fill=(160, 130, 90, 40), width=1)

    # Decorative border (old map style)
    draw.rectangle((20, 20, W - 20, H - 20), outline=(120, 90, 50, 150), width=4)
    draw.rectangle((30, 30, W - 30, H - 30), outline=(120, 90, 50, 80), width=1)

    # Vignette darkening at edges
    for y in range(H):
        t = y / H
        edge_factor = 1.0 - abs(t - 0.5) * 2
        edge_factor = max(0, edge_factor)
        edge_dark = 0
        if y < 100:
            edge_dark = int((100 - y) * 0.8)
        elif y > H - 100:
            edge_dark = int((y - (H - 100)) * 0.8)
        if edge_dark > 0:
            draw.line((0, y, W, y), fill=(0, 0, 0, edge_dark))

    # Title panel at bottom
    # Gold lines
    draw.line((200, H - 120, W - 200, H - 120), fill=(200, 170, 90, 100), width=1)

    # Fonts
    tf = font("georgiab.ttf", 90)
    af = font("arialbd.ttf", 40)
    sf_small = font("arial.ttf", 28)

    # Centered title on panel
    y = 2020
    wrapped_lines = wrap(draw, title.upper(), tf, 1300)
    y = centered(draw, y, wrapped_lines, tf, (210, 190, 140), 12)
    y += 40
    # Author
    centered(draw, y, [author], af, (200, 180, 130), 6)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)



def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()

    meta_path = ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata
    out_path = ROOT / a.out if not a.out.is_absolute() else a.out
    make_cover(meta_path, out_path)


if __name__ == "__main__":
    main()