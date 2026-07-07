#!/usr/bin/env python3
"""Cover: Woman in trench coat before shimmering doorway in dim brick corridor, gauge in hand, amber light bleeding from seam, brick brown/doorway amber/coat dark."""

from __future__ import annotations

import argparse
import json
import math
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
ART_HEIGHT = 1765


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    """Dim brick corridor gradient: warm brown at top to dark brown at bottom."""
    for y in range(ART_HEIGHT):
        t = y / ART_HEIGHT
        r = int(60 + (40 - 60) * t)
        g = int(35 + (22 - 35) * t)
        b = int(20 + (12 - 20) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_brick_walls(draw: ImageDraw.ImageDraw) -> None:
    """Brick texture on the corridor walls."""
    # Left wall
    for by in range(0, ART_HEIGHT, 20):
        for bx in range(0, 250, 40):
            offset = 20 if (by // 20) % 2 == 1 else 0
            shade = 55 + int(10 * math.sin(bx * 0.1 + by * 0.05))
            draw.rectangle([bx + offset, by, bx + offset + 36, by + 18],
                           fill=(shade, shade - 10, shade - 15), outline=(45, 28, 15), width=1)
    # Right wall
    for by in range(0, ART_HEIGHT, 20):
        for bx in range(WIDTH - 250, WIDTH, 40):
            offset = 20 if (by // 20) % 2 == 1 else 0
            shade = 55 + int(10 * math.sin(bx * 0.1 + by * 0.05))
            draw.rectangle([bx + offset, by, bx + offset + 36, by + 18],
                           fill=(shade, shade - 10, shade - 15), outline=(45, 28, 15), width=1)
    # Floor
    draw.rectangle([(0, ART_HEIGHT - 100), (WIDTH, ART_HEIGHT)], fill=(30, 18, 10))
    for fx in range(0, WIDTH, 50):
        draw.line([(fx, ART_HEIGHT - 100), (fx, ART_HEIGHT)], fill=(22, 14, 8), width=2)


def draw_seam(image: Image.Image) -> None:
    """A shimmering doorway of amber light at the center — the open seam."""
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx = WIDTH // 2
    door_w, door_h = 150, 500
    top = 600
    # Halo
    for r in range(250, 0, -6):
        a = int(80 * (1 - r / 250))
        gd.ellipse([(cx - door_w // 2 - r, top - r), (cx + door_w // 2 + r, top + door_h + r)],
                   fill=(255, 200, 100, max(0, a // 4)))
    # Bright slit
    for i in range(door_w // 2, 0, -1):
        t = i / (door_w / 2)
        a = int(255 * (1 - t) ** 1.5)
        gd.rectangle([(cx - i, top), (cx + i, top + door_h)], fill=(255, 220, 150, a))
    gd.rectangle([(cx - 12, top), (cx + 12, top + door_h)], fill=(255, 240, 200, 255))
    # Light bleeding onto walls
    for angle in range(-40, 40, 3):
        rad = math.radians(angle)
        for d in range(0, 200, 10):
            lx = cx + int(d * math.sin(rad) * 0.6)
            ly = top + door_h // 2 + int(d * math.cos(rad) * 0.3)
            if ly > ART_HEIGHT or lx < 0 or lx > WIDTH:
                break
            a = max(2, 40 - d // 8)
            gd.point((lx, ly), fill=(255, 200, 100, a))
    glow = glow.filter(ImageFilter.GaussianBlur(4))
    image.paste(Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB"), (0, 0))


def draw_figure(draw: ImageDraw.ImageDraw) -> None:
    """Woman in trench coat before the shimmering doorway, gauge in hand."""
    cx = WIDTH // 2
    base = 1200
    col = (18, 16, 22)
    # Legs
    draw.line([(cx - 12, base), (cx - 8, base - 80)], fill=col, width=12)
    draw.line([(cx + 12, base), (cx + 8, base - 80)], fill=col, width=12)
    # Torso (trench coat)
    draw.polygon([(cx - 22, base - 70), (cx + 22, base - 70), (cx + 18, base), (cx - 18, base)], fill=col)
    # Coat collar
    draw.polygon([(cx - 22, base - 70), (cx, base - 90), (cx + 22, base - 70)], fill=(25, 22, 28))
    # Head
    draw.ellipse([(cx - 16, base - 120), (cx + 16, base - 88)], fill=col)
    # Hair
    draw.ellipse([(cx - 18, base - 124), (cx + 18, base - 105)], fill=(12, 10, 15))
    # Arm holding gauge (right arm, extended)
    draw.line([(cx + 20, base - 60), (cx + 60, base - 80)], fill=col, width=8)
    # Gauge in hand
    gauge_cx, gauge_cy = cx + 65, base - 85
    draw.ellipse([gauge_cx - 15, gauge_cy - 15, gauge_cx + 15, gauge_cy + 15], fill=(40, 45, 50))
    draw.ellipse([gauge_cx - 12, gauge_cy - 12, gauge_cx + 12, gauge_cy + 12], fill=(55, 60, 65))
    # Gauge face
    draw.ellipse([gauge_cx - 8, gauge_cy - 8, gauge_cx + 8, gauge_cy + 8], fill=(80, 85, 90))
    # Gauge needle
    draw.line([(gauge_cx, gauge_cy), (gauge_cx + 5, gauge_cy - 6)], fill=(255, 200, 80), width=2)
    # Gauge glow (amber)
    for r in range(20, 0, -3):
        a = max(2, 30 - (20 - r) * 3)
        draw.ellipse([gauge_cx - r, gauge_cy - r, gauge_cx + r, gauge_cy + r], fill=(255, 200, 80, a))
    # Left arm
    draw.line([(cx - 20, base - 55), (cx - 40, base - 40)], fill=col, width=8)
    # Shadow on floor
    draw.ellipse([cx - 30, base - 2, cx + 30, base + 6], fill=(15, 10, 8, 100))
    # Long shadow toward viewer from the light
    for i in range(3):
        a = max(5, 40 - i * 12)
        draw.polygon([(cx - 25 + i * 5, base), (cx + 25 - i * 5, base),
                      (cx + 80 - i * 10, base + 120), (cx - 80 + i * 10, base + 120)],
                     fill=(12, 10, 8, a))


def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tessera Bureau")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (40, 48, 66))
    # overlays are full-height so alpha_composite matches the base image size
    draw = ImageDraw.Draw(image)

    draw_background(draw)
    draw_brick_walls(draw)
    draw_seam(image)
    draw_figure(ImageDraw.Draw(image))

    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)

if __name__ == "__main__":
    main()
