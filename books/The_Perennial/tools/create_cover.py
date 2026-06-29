#!/usr/bin/env python3
"""Generate a cover image for The Perennial."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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


def _make_gradient(draw, y1, y2, color1, color2):
    for y in range(y1, y2):
        ratio = (y - y1) / max(y2 - y1 - 1, 1)
        r = int(color1[0] + (color2[0] - color1[0]) * ratio)
        g = int(color1[1] + (color2[1] - color1[1]) * ratio)
        b = int(color1[2] + (color2[2] - color1[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_twilight_sky(draw):
    """Draw twilight sky gradient from deep blue through purple to warm orange."""
    # Upper sky - deep twilight blue
    _make_gradient(draw, 0, 400, (15, 10, 35), (40, 25, 60))
    # Mid sky - purple
    _make_gradient(draw, 400, 800, (40, 25, 60), (80, 45, 70))
    # Lower sky - warm twilight
    _make_gradient(draw, 800, 1200, (80, 45, 70), (120, 60, 60))
    # Horizon glow
    _make_gradient(draw, 1200, 1500, (120, 60, 60), (160, 100, 70))


def _draw_stars(draw):
    """Draw stars in the twilight sky."""
    for i in range(200):
        sx = int(math.sin(i * 7.3 + 13) * 700 + WIDTH // 2)
        sy = int(math.cos(i * 5.1 + 7) * 500 + 250)
        if sy > 700:
            continue
        size = 1 + int(math.sin(i * 3.7) * 1.5)
        brightness = int(math.sin(i * 2.3) * 100 + 155)
        alpha = int(math.sin(i * 4.1) * 60 + 120)
        draw.ellipse([sx - size, sy - size, sx + size, sy + size], fill=(brightness, brightness, min(255, brightness + 20), alpha))

    # Bright stars with glow
    for i in range(15):
        sx = int(math.sin(i * 11.3) * 600 + WIDTH // 2)
        sy = int(math.cos(i * 8.1) * 350 + 200)
        if sy > 650:
            continue
        for r in range(8, 0, -2):
            alpha = int((1 - r / 8) * 60)
            draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(220, 230, 255, alpha))
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 255, 200))


def _draw_garden_ground(draw):
    """Draw the garden grounds with paths and grass."""
    # Ground gradient
    _make_gradient(draw, 1500, 1765, (25, 35, 25), (20, 28, 20))

    # Garden path leading from foreground to garden
    path_points = []
    for t in range(0, 101):
        frac = t / 100.0
        x = WIDTH // 2 + int(math.sin(frac * 3) * 60 * frac)
        y = 1765 - int(frac * 350)
        path_points.append((x, y))

    for i in range(len(path_points) - 1):
        x1, y1 = path_points[i]
        x2, y2 = path_points[i + 1]
        w = max(2, int(40 * (1 - i / len(path_points))))
        draw.line([(x1, y1), (x2, y2)], fill=(60, 55, 45, 150), width=w)

    # Grass texture
    for _ in range(300):
        gx = int(math.sin(_ * 5.7) * 700 + WIDTH // 2)
        gy = 1400 + int(math.cos(_ * 3.3) * 350)
        gh = 5 + int(math.sin(_ * 7.1) * 15)
        draw.line([(gx, gy), (gx + int(math.sin(_ * 2.3) * 4), gy - gh)],
                  fill=(25 + int(math.sin(_) * 10), 45 + int(math.sin(_ * 1.3) * 10), 25 + int(math.sin(_ * 2.1) * 8)),
                  width=1)


def _draw_statues(draw):
    """Draw marble statues in the garden."""
    statue_data = [
        (WIDTH // 2 - 350, 1320, 1.0),   # Left statue
        (WIDTH // 2 - 150, 1290, 1.1),   # Center-left
        (WIDTH // 2 + 180, 1300, 1.0),   # Center-right
        (WIDTH // 2 + 400, 1330, 0.9),   # Right statue
    ]

    for sx, sy, scale in statue_data:
        # Pedestal
        pw = int(50 * scale)
        ph = int(30 * scale)
        draw.rectangle([sx - pw, sy, sx + pw, sy + ph], fill=(90, 85, 80, 180))
        # Pedestal top detail
        draw.rectangle([sx - pw - 5, sy - 3, sx + pw + 5, sy], fill=(100, 95, 90, 180))

        # Statue body
        body_w = int(18 * scale)
        body_h = int(100 * scale)
        draw.rectangle([sx - body_w, sy - body_h, sx + body_w, sy], fill=(180, 180, 175, 160))

        # Statue head
        head_r = int(12 * scale)
        draw.ellipse([sx - head_r, sy - body_h - head_r * 2, sx + head_r, sy - body_h], fill=(185, 185, 180, 160))

        # Statue arms
        arm_len = int(30 * scale)
        draw.line([(sx - body_w, sy - int(body_h * 0.7)), (sx - body_w - arm_len, sy - int(body_h * 0.5))],
                  fill=(180, 180, 175, 140), width=int(5 * scale))
        draw.line([(sx + body_w, sy - int(body_h * 0.7)), (sx + body_w + arm_len, sy - int(body_h * 0.5))],
                  fill=(180, 180, 175, 140), width=int(5 * scale))

        # Subtle glow at base of statues
        for gr in range(15, 0, -2):
            alpha = int((1 - gr / 15) * 30)
            draw.ellipse([sx - gr * 4, sy + ph - gr, sx + gr * 4, sy + ph + gr],
                         fill=(160, 140, 200, alpha))


def _draw_empty_pedestal(draw):
    """Draw the empty pedestal as the focal point."""
    ex, ey = WIDTH // 2, 1280

    # Pedestal
    pw, ph = 70, 40
    draw.rectangle([ex - pw, ey, ex + pw, ey + ph], fill=(95, 90, 85, 200))
    draw.rectangle([ex - pw - 8, ey - 5, ex + pw + 8, ey], fill=(105, 100, 95, 200))

    # Top surface visible - empty
    draw.rectangle([ex - pw - 3, ey - 8, ex + pw + 3, ey - 5], fill=(110, 105, 100, 200))

    # Engraving on pedestal
    for line_idx in range(3):
        ly = ey + 10 + line_idx * 10
        draw.line([(ex - 30, ly), (ex + 30, ly)], fill=(70, 65, 60, 150), width=1)

    # Glow around empty pedestal - ethereal light
    for gr in range(40, 0, -2):
        alpha = int((1 - gr / 40) * 40)
        draw.ellipse([ex - gr * 3, ey - gr * 4 - 30, ex + gr * 3, ey + gr * 2],
                     fill=(200, 180, 220, alpha))

    # Light beam from above onto empty pedestal
    for i in range(25):
        y = ey - 200 + i * 8
        fade = max(0, 1.0 - i / 25)
        beam_width = int(fade * 120 + 10)
        alpha = int(fade * 25)
        draw.rectangle([ex - beam_width // 2, y, ex + beam_width // 2, y + 4],
                       fill=(200, 190, 220, alpha))


def _draw_garden_details(draw):
    """Draw small bushes, flowers, and garden elements."""
    # Hedges/bushes
    for bx in range(100, WIDTH - 50, 200):
        by = 1380 + int(math.sin(bx * 0.05) * 30)
        bw = 60 + int(math.sin(bx * 0.03) * 20)
        bh = 25 + int(math.sin(bx * 0.07) * 10)
        draw.ellipse([bx - bw // 2, by - bh, bx + bw // 2, by], fill=(30, 55, 30, 150))
        draw.ellipse([bx - bw // 2 + 5, by - bh - 5, bx + bw // 2 - 5, by],
                     fill=(35, 60, 35, 100))

    # Flower accents
    for _ in range(40):
        fx = int(math.sin(_ * 9.1) * 650 + WIDTH // 2)
        fy = 1420 + int(math.cos(_ * 7.3) * 300)
        colors = [(180, 100, 120), (160, 80, 100), (200, 120, 140), (140, 60, 80)]
        c = colors[_ % len(colors)]
        draw.ellipse([fx - 3, fy - 3, fx + 3, fy + 3], fill=c + (120,))

    # Fireflies / floating lights
    for _ in range(80):
        lx = int(math.sin(_ * 11.3) * 600 + WIDTH // 2)
        ly = 1300 + int(math.cos(_ * 13.7) * 350)
        size = 1 + int(math.sin(_ * 5.1) * 1.5)
        alpha = int(math.sin(_ * 3.7) * 60 + 80)
        draw.ellipse([lx - size, ly - size, lx + size, ly + size],
                     fill=(200, 220, 180, alpha))


def _draw_moon(draw):
    """Draw a crescent moon in the sky."""
    mx, my = 1200, 180
    moon_r = 50
    # Moon glow
    for gr in range(30, 0, -3):
        alpha = int((1 - gr / 30) * 30)
        draw.ellipse([mx - moon_r - gr, my - moon_r - gr, mx + moon_r + gr, my + moon_r + gr],
                     fill=(200, 210, 220, alpha))
    # Moon body
    draw.ellipse([mx - moon_r, my - moon_r, mx + moon_r, my + moon_r], fill=(220, 225, 230, 200))
    # Crescent - dark overlay
    draw.ellipse([mx - moon_r + 15, my - moon_r - 10, mx + moon_r + 15, my + moon_r + 10],
                 fill=(15, 10, 35, 200))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Perennial")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (20, 28, 20, 255))
    draw = ImageDraw.Draw(img)

    # Build the cover elements
    _draw_twilight_sky(draw)
    _draw_moon(draw)
    _draw_stars(draw)
    _draw_garden_ground(draw)
    _draw_statues(draw)
    _draw_empty_pedestal(draw)
    _draw_garden_details(draw)

    # Title and author panel
    _draw_standard_cover_title_panel(img, title, author, model)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


# ---- Standard helper functions (do not edit below this line) ----

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    main()
