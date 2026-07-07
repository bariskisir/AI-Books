#!/usr/bin/env python3
"""Cover: The Rust Colossus — massive armored train through fog-choked wasteland under bruised chemical sky, rust-red and smoke-black."""

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

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = _standard_cover_resolve_title(m)
    author = _standard_cover_resolve_author(m)

    img = Image.new("RGBA", (W, H), (20, 15, 10, 255))
    draw = ImageDraw.Draw(img)

    # Bruised chemical sky
    for y in range(H * 2 // 3):
        t = y / (H * 2 // 3)
        r = int(35 + t * 55)
        g = int(18 + t * 28)
        b = int(8 + t * 12)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # Chemical haze
    for y in range(H * 2 // 3 - 80, H * 2 // 3 + 120):
        t = max(0, 1.0 - abs(y - (H * 2 // 3 - 40)) / 120.0)
        draw.line([(0, y), (W, y)], fill=(55, 70, 38, int(t * 90)))

    # Wasteland ground
    for y in range(H * 2 // 3, H):
        t = (y - H * 2 // 3) / (H - H * 2 // 3)
        draw.line([(0, y), (W, y)], fill=(int(95 - t * 18), int(80 - t * 12), int(55 - t * 8), 255))

    # Massive armored train
    tx = W // 2 - 360
    ty = H * 2 // 3 - 50

    # Locomotive boiler
    draw.rounded_rectangle([tx + 200, ty - 160, tx + 580, ty - 15], radius=10, fill=(42, 36, 28, 255), outline=(78, 68, 48, 255), width=3)
    for bx in [tx + 240, tx + 330, tx + 420, tx + 510]:
        draw.rectangle([bx, ty - 150, bx + 6, ty - 20], fill=(58, 50, 38, 255))

    # Smokestack with smoke
    draw.rectangle([tx + 440, ty - 250, tx + 470, ty - 160], fill=(32, 28, 22, 255))
    draw.ellipse([tx + 430, ty - 260, tx + 480, ty - 240], fill=(42, 36, 28, 255), outline=(68, 58, 42, 255), width=2)
    for _ in range(25):
        sx = tx + 455 + random.randint(-25, 25)
        sy = ty - 260 - random.randint(10, 220)
        draw.ellipse([sx, sy, sx + random.randint(15, 90), sy + random.randint(15, 90)], fill=(95, 88, 72, random.randint(8, 35)))

    # Cab
    draw.rounded_rectangle([tx + 580, ty - 200, tx + 720, ty - 15], radius=6, fill=(38, 32, 26, 255), outline=(68, 58, 42, 255), width=2)
    for wx in [tx + 600, tx + 645, tx + 685]:
        draw.rectangle([wx, ty - 170, wx + 22, ty - 145], fill=(190, 105, 40, 200))

    # Headlight
    draw.ellipse([tx + 200, ty - 110, tx + 230, ty - 80], fill=(210, 190, 105, 200))
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([tx + 215, ty - 95, -100, ty - 320, -100, ty + 160], fill=(210, 190, 105, 28))
    beam = beam.filter(ImageFilter.GaussianBlur(radius=30))
    img = Image.alpha_composite(img, beam)

    # Drive wheels
    for wx in range(6):
        cx = tx + 220 + wx * 60
        cy = ty - 8
        draw.ellipse([cx - 32, cy - 32, cx + 32, cy + 32], fill=(22, 20, 16, 255), outline=(58, 50, 38, 255), width=3)
        for a2 in range(0, 360, 60):
            rad = math.radians(a2)
            draw.line([(cx, cy), (cx + int(24 * math.cos(rad)), cy + int(24 * math.sin(rad)))], fill=(48, 40, 32, 255), width=2)
        draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(58, 50, 38, 255))

    # Armored cars behind
    for ci in range(3):
        ax = tx + 720 + ci * 150
        draw.rounded_rectangle([ax, ty - 130, ax + 140, ty - 15], radius=4, fill=(36, 32, 24, 255), outline=(62, 52, 40, 255), width=2)
        for r in range(4):
            draw.ellipse([ax + 18 + r * 32, ty - 95, ax + 22 + r * 32, ty - 91], fill=(52, 42, 32, 255))
            draw.ellipse([ax + 18 + r * 32, ty - 55, ax + 22 + r * 32, ty - 51], fill=(52, 42, 32, 255))

    # Turret on second car
    tax = tx + 790
    draw.rounded_rectangle([tax, ty - 200, tax + 45, ty - 130], radius=3, fill=(42, 36, 28, 255), outline=(68, 58, 42, 255), width=2)
    draw.rectangle([tax - 45, ty - 205, tax - 5, ty - 192], fill=(48, 42, 32, 255))

    # Fog
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(180):
        x0, y0, x1, y1 = random.randint(0, W), random.randint(0, H * 3 // 4), random.randint(30, 200), random.randint(15, 100)
        fd.ellipse([min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)], fill=(78, 88, 58, random.randint(4, 12)))
    fog = fog.filter(ImageFilter.GaussianBlur(radius=40))
    img = Image.alpha_composite(img, fog)

    _draw_standard_cover_title_panel(img, title, author, m)
    rgb = Image.new("RGB", (W, H), (20, 15, 10, 255))
    rgb.paste(img, mask=img.split()[3])
    rgb.save(op, "PNG")
    print(f"Cover saved to {op}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--metadata", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    make_cover(args.metadata, args.out)
