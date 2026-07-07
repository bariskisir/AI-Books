#!/usr/bin/env python3
"""Cover: Titan's Heart — massive sphere of interlocking brass rings, furnace-orange glow, steam rising around scaffolding, dark foundry/brass-gold/furnace-orange."""

from __future__ import annotations

import argparse
import json
import math
import random
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



WIDTH = 1600
HEIGHT = 2560

FONT_DIR = Path("C:/Windows/Fonts")
TITLE_FONT = str(FONT_DIR / "georgiab.ttf")
AUTHOR_FONT = str(FONT_DIR / "arialbd.ttf")
SMALL_FONT = str(FONT_DIR / "arial.ttf")

random.seed(42)


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def generate_cover(output_path: Path) -> None:
    """Generate the full cover image — Titan's Heart."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (25, 15, 10, 255))
    draw = ImageDraw.Draw(img)

    # Dark foundry gradient: black-brown to deep bronze
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.5:
            c = lerp_color((15, 8, 4), (50, 25, 12), t / 0.5)
        else:
            c = lerp_color((50, 25, 12), (25, 12, 6), (t - 0.5) / 0.5)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    # Steam/haze layer in background
    haze = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(40):
        sx = random.randint(0, WIDTH)
        sy = random.randint(300, 1400)
        sr = random.randint(40, 120)
        hd.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                   fill=(180, 160, 120, random.randint(8, 25)))
    haze = haze.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, haze)

    # Titan's Heart — massive sphere of interlocking brass rings
    cx, cy = WIDTH // 2, 700
    sphere_r = 420

    # Outer glow
    for r in range(sphere_r + 100, 0, -15):
        a = max(3, 80 - (sphere_r + 100 - r) // 5)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=(200, 120, 30, max(0, a // 4)))

    # Multiple interlocking brass rings (latitudinal)
    for i in range(12):
        angle = math.radians(i * 15)
        ring_r = sphere_r * math.sin(angle)
        ring_y_offset = sphere_r * (1 - math.cos(angle))
        if ring_r < 10:
            continue
        rx = int(ring_r)
        ry = int(ring_r * 0.35)
        ry_off = int(ring_y_offset)
        # Brass ring
        r_bright = 150 + random.randint(-20, 20)
        r_color = (r_bright, r_bright - 40, r_bright - 80)
        if i % 2 == 0:
            r_color = (r_bright - 20, r_bright - 30, r_bright - 60)
        draw.ellipse(
            [cx - rx, cy - ry + ry_off, cx + rx, cy + ry + ry_off],
            outline=r_color, width=8 + i % 3,
        )
        # Rivet details on rings
        for j in range(0, 360, 45):
            rad = math.radians(j)
            rvx = cx + int(rx * math.cos(rad))
            rvy = cy + int(ry * math.sin(rad)) + ry_off
            draw.ellipse([rvx - 3, rvy - 3, rvx + 3, rvy + 3], fill=(180, 150, 80))

    # Longitudinal rings
    for i in range(6):
        rad = math.radians(i * 30)
        draw.arc(
            [cx - sphere_r, cy - sphere_r, cx + sphere_r, cy + sphere_r],
            int(math.degrees(rad)), int(math.degrees(rad) + 180),
            fill=(160, 120, 50, 150), width=6,
        )

    # Central core — furnace-orange glow
    for r in range(200, 0, -8):
        a = max(5, 150 - (200 - r) * 2)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=(255, 140, 30, a))
    for r in range(100, 0, -5):
        a = max(8, 200 - (100 - r) * 4)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r],
                     fill=(255, 200, 80, a))
    # White-hot core center
    draw.ellipse([cx - 30, cy - 30, cx + 30, cy + 30], fill=(255, 240, 200, 220))

    # Scaffolding around the sphere
    scaffold_color = (60, 40, 25)
    for angle in range(0, 360, 60):
        rad = math.radians(angle)
        sx = cx + int((sphere_r + 30) * math.cos(rad))
        sy = cy + int((sphere_r + 30) * math.sin(rad) * 0.5)
        # Scaffold post
        draw.line([(sx, sy), (sx, sy + 200)], fill=scaffold_color, width=6)
        # Cross-brace
        draw.line([(sx - 20, sy + 50), (sx + 20, sy + 100)], fill=scaffold_color, width=4)
        draw.line([(sx + 20, sy + 50), (sx - 20, sy + 100)], fill=scaffold_color, width=4)
    # Bottom scaffold platform
    draw.ellipse([cx - 500, cy + 350, cx + 500, cy + 420], fill=(40, 25, 15))
    draw.ellipse([cx - 480, cy + 360, cx + 480, cy + 410], fill=(50, 32, 18))
    # Scaffold vertical beams
    for bx in range(cx - 400, cx + 450, 80):
        draw.line([(bx, cy + 380), (bx, HEIGHT)], fill=(45, 28, 15), width=6)

    # Steam rising from below
    for _ in range(30):
        sx = cx + random.randint(-400, 400)
        sy = random.randint(1000, 1400)
        sr = random.randint(20, 70)
        a = random.randint(15, 45)
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr],
                     fill=(180, 160, 130, a))

    # Light rays emanating from the core
    for angle in range(0, 360, 15):
        rad = math.radians(angle)
        for d in range(0, 600, 20):
            lx = cx + int(d * math.cos(rad))
            ly = cy + int(d * math.sin(rad) * 0.5)
            if lx < 0 or lx > WIDTH or ly < 0 or ly > HEIGHT:
                break
            a = max(2, 60 - d // 15)
            draw.point((lx, ly), fill=(255, 180, 60, a))

    # Soft vignette
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for r in range(WIDTH // 2, 0, -1):
        alpha = int(100 * (1 - r / (WIDTH // 2)))
        vdraw.ellipse(
            [WIDTH // 2 - r, HEIGHT // 2 - r, WIDTH // 2 + r, HEIGHT // 2 + r],
            outline=(0, 0, 0, alpha),
        )
    img = Image.alpha_composite(img, vignette)

    # Convert to RGB for output
    rgb_img = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    rgb_img.paste(img, mask=img.split()[3])
    _draw_standard_cover_title_panel(rgb_img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), _standard_cover_metadata_from_locals(locals()).get("model", ""))
    rgb_img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    # Read metadata (for validation, but we use hardcoded design)
    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    model = _standard_cover_metadata_from_locals(locals()).get("model", "")
    print(f"Generating cover for: {metadata['title']}")

    args.out.parent.mkdir(parents=True, exist_ok=True)
    generate_cover(args.out)


if __name__ == "__main__":
    main()