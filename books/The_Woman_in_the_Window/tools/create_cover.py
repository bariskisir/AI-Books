#!/usr/bin/env python3
"""Cover: The Woman in the Window — Woman in red dress presses palm against rain-streaked window at night, viewed from across courtyard through camera crosshairs."""

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

ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    for y in range(height):
        t = y / height
        if t < 0.4:
            t2 = t / 0.4
            c = lerp_color((10, 10, 25), (20, 15, 35), t2)
        elif t < 0.7:
            t2 = (t - 0.4) / 0.3
            c = lerp_color((20, 15, 35), (5, 5, 15), t2)
        else:
            t2 = (t - 0.7) / 0.3
            c = lerp_color((5, 5, 15), (2, 2, 8), t2)
        draw.line([(0, y), (width, y)], fill=c)


def draw_building_facade(draw: ImageDraw, width: int, height: int) -> None:
    rng = random.Random("building-facade")
    building_left = 200
    building_right = 1400
    building_top = 100
    building_bot = 1700
    draw.rectangle([building_left, building_top, building_right, building_bot], fill=(15, 12, 18))
    for row in range(6):
        for col in range(4):
            wx = building_left + 100 + col * 260
            wy = building_top + 80 + row * 200
            draw.rectangle([wx, wy, wx + 160, wy + 140], fill=(8, 6, 12))
            draw.rectangle([wx, wy, wx + 160, wy + 140], outline=(20, 18, 25), width=1)
            draw.line([wx + 80, wy, wx + 80, wy + 140], fill=(15, 13, 20), width=2)
            draw.line([wx, wy + 70, wx + 160, wy + 70], fill=(15, 13, 20), width=2)
            if rng.random() < 0.15:
                draw.rectangle([wx + 4, wy + 4, wx + 156, wy + 136], fill=(40, 50, 80, 60))


def draw_courtyard(draw: ImageDraw, width: int, height: int) -> None:
    for y in range(1700, HEIGHT):
        t = (y - 1700) / (HEIGHT - 1700)
        r = int(5 + 10 * t)
        g = int(5 + 8 * t)
        b = int(10 + 15 * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_window(draw: ImageDraw, width: int, height: int) -> None:
    win_cx = width // 2
    win_cy = int(height * 0.40)
    win_w, win_h = 300, 400
    draw.rectangle([win_cx - win_w // 2, win_cy - win_h // 2, win_cx + win_w // 2, win_cy + win_h // 2], fill=(10, 8, 15))
    draw.rectangle([win_cx - win_w // 2, win_cy - win_h // 2, win_cx + win_w // 2, win_cy + win_h // 2], outline=(40, 35, 50), width=6)
    draw.line([win_cx - win_w // 2, win_cy, win_cx + win_w // 2, win_cy], fill=(40, 35, 50), width=4)
    draw.line([win_cx, win_cy - win_h // 2, win_cx, win_cy + win_h // 2], fill=(40, 35, 50), width=4)
    room_color = (15, 12, 20)
    draw.rectangle([win_cx - win_w // 2 + 6, win_cy - win_h // 2 + 6, win_cx - 4, win_cy - 2], fill=room_color)
    draw.rectangle([win_cx + 4, win_cy - win_h // 2 + 6, win_cx + win_w // 2 - 6, win_cy - 2], fill=room_color)
    draw.rectangle([win_cx - win_w // 2 + 6, win_cy + 4, win_cx - 4, win_cy + win_h // 2 - 6], fill=room_color)
    draw.rectangle([win_cx + 4, win_cy + 4, win_cx + win_w // 2 - 6, win_cy + win_h // 2 - 6], fill=room_color)


def draw_woman_in_window(draw: ImageDraw, width: int, height: int) -> None:
    win_cx = width // 2
    win_cy = int(height * 0.40)
    cx, cy = win_cx, win_cy
    dress_color = (180, 30, 40)
    skin_color = (200, 170, 150)
    head_r = 20
    draw.ellipse([cx - head_r, cy - 50 - head_r, cx + head_r, cy - 50 + head_r], fill=skin_color)
    body_w, body_h = 25, 90
    draw.polygon([(cx - body_w, cy - 30), (cx + body_w, cy - 30), (cx + body_w + 10, cy + 60), (cx - body_w - 10, cy + 60)], fill=dress_color)
    draw.arc([cx - 70, cy + 40, cx + 70, cy + 120], 0, 180, fill=dress_color, width=30)
    palm_cx = cx + 55
    palm_cy = cy - 10
    draw.ellipse([palm_cx - 12, palm_cy - 8, palm_cx + 12, palm_cy + 8], fill=skin_color)
    for f in range(5):
        fx = palm_cx - 8 + f * 4
        draw.line([(fx, palm_cy + 6), (fx, palm_cy + 14)], fill=skin_color, width=2)


def draw_rain(draw: ImageDraw, width: int, height: int) -> None:
    rng = random.Random("night-rain")
    for _ in range(300):
        x = rng.randint(0, width)
        y = rng.randint(0, 1800)
        length = rng.randint(15, 40)
        alpha = rng.randint(30, 80)
        draw.line([(x, y), (x + 3, y + length)], fill=(180, 190, 210, alpha), width=1)


def draw_crosshairs(draw: ImageDraw, width: int, height: int) -> None:
    cx, cy = width // 2, int(height * 0.40)
    r = 250
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(0, 255, 0, 120), width=2)
    r2 = 200
    draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], outline=(0, 255, 0, 60), width=1)
    draw.line([(cx - r - 30, cy), (cx - 30, cy)], fill=(0, 255, 0, 100), width=2)
    draw.line([(cx + 30, cy), (cx + r + 30, cy)], fill=(0, 255, 0, 100), width=2)
    draw.line([(cx, cy - r - 30), (cx, cy - 30)], fill=(0, 255, 0, 100), width=2)
    draw.line([(cx, cy + 30), (cx, cy + r + 30)], fill=(0, 255, 0, 100), width=2)
    draw.line([(cx - r - 30, cy), (cx + r + 30, cy)], fill=(0, 255, 0, 30), width=1)
    draw.line([(cx, cy - r - 30), (cx, cy + r + 30)], fill=(0, 255, 0, 30), width=1)
    draw.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=(0, 255, 0, 150))
    for a in range(0, 360, 45):
        rad = math.radians(a)
        x1 = cx + int(r * math.cos(rad))
        y1 = cy + int(r * math.sin(rad))
        x2 = cx + int((r + 15) * math.cos(rad))
        y2 = cy + int((r + 15) * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=(0, 255, 0, 100), width=2)


def draw_ambient_glow(draw: ImageDraw, width: int, height: int) -> None:
    glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse([width // 2 - 180, int(height * 0.27), width // 2 + 180, int(height * 0.53)], fill=(200, 100, 80, 15))
    glow = glow.filter(ImageFilter.GaussianBlur(30))
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    img.paste(glow, (0, 0))
    return img


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Woman in the Window")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_building_facade(draw, WIDTH, HEIGHT)
    draw_courtyard(draw, WIDTH, HEIGHT)
    draw_window(draw, WIDTH, HEIGHT)
    draw_woman_in_window(draw, WIDTH, HEIGHT)
    glow_img = draw_ambient_glow(draw, WIDTH, HEIGHT)
    img = Image.alpha_composite(img, glow_img)
    draw = ImageDraw.Draw(img, "RGBA")
    draw_rain(draw, WIDTH, HEIGHT)
    draw_crosshairs(draw, WIDTH, HEIGHT)

    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
