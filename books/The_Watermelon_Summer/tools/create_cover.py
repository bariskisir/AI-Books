#!/usr/bin/env python3
"""Cover: The Watermelon Summer — Three sisters silhouetted against golden sunset over watermelon field, green Buick on dirt road."""

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
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((255, 180, 60), (255, 140, 40), t)
        elif y < height * 0.55:
            t = (y - height * 0.3) / (height * 0.25)
            c = lerp_color((255, 140, 40), (200, 80, 30), t)
        elif y < height * 0.75:
            t = (y - height * 0.55) / (height * 0.2)
            c = lerp_color((200, 80, 30), (80, 40, 60), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((80, 40, 60), (20, 15, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_sun(draw: ImageDraw, width: int, height: int) -> None:
    cx, cy = width // 2, int(height * 0.32)
    r = 180
    for i in range(12, 0, -1):
        alpha = max(5, 120 - i * 10)
        r2 = r + i * 20
        draw.ellipse([cx - r2, cy - r2, cx + r2, cy + r2], fill=(255, 200, 80, alpha))
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 220, 100))
    draw.ellipse([cx - r + 30, cy - r + 30, cx + r - 30, cy + r - 30], fill=(255, 240, 160))


def draw_watermelon_field(draw: ImageDraw, width: int, height: int) -> None:
    rng = random.Random("watermelon-field")
    for _ in range(60):
        x = rng.randint(0, width)
        y = rng.randint(int(height * 0.55), int(height * 0.85))
        r = rng.randint(30, 60)
        draw.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(30, 100, 40, 200))
        draw.ellipse([x - r + 5, y - r // 2 + 3, x + r - 5, y + r // 2 - 3], fill=(40, 120, 50, 180))
        if rng.random() < 0.3:
            draw.ellipse([x - 8, y - 4, x + 8, y + 4], fill=(20, 60, 30))
    vine_color = (40, 110, 50, 120)
    for _ in range(30):
        x = rng.randint(0, width)
        y = rng.randint(int(height * 0.6), int(height * 0.8))
        draw.line([(x, y), (x + rng.randint(-60, 60), y + rng.randint(10, 40))], fill=vine_color, width=2)


def draw_dirt_road(draw: ImageDraw, width: int, height: int) -> None:
    points = []
    for y in range(int(height * 0.6), HEIGHT):
        t = (y - height * 0.6) / (HEIGHT - height * 0.6)
        road_w = 80 + t * 300
        cx = width // 2 + int(20 * math.sin(y / 200))
        points.append((cx - road_w // 2, y))
    for y in range(int(height * 0.6), HEIGHT):
        t = (y - height * 0.6) / (HEIGHT - height * 0.6)
        road_w = 80 + t * 300
        cx = width // 2 + int(20 * math.sin(y / 200))
        draw.line([(cx - road_w // 2, y), (cx + road_w // 2, y)], fill=(120, 90, 60, 180 + int(50 * t)))
    for y in range(int(height * 0.6), HEIGHT, 15):
        cx = width // 2 + int(20 * math.sin(y / 200))
        t = (y - height * 0.6) / (HEIGHT - height * 0.6)
        road_w = 80 + t * 300
        for s in range(-1, 2):
            sx = cx + s * random.randint(10, 40)
            sy = y + random.randint(-5, 5)
            draw.ellipse([sx - 5, sy - 3, sx + 5, sy + 3], fill=(100, 75, 50, 100))


def draw_green_buick(draw: ImageDraw, width: int, height: int) -> None:
    cx = width // 2 + 60
    cy = int(height * 0.58)
    car_w, car_h = 140, 50
    draw.rectangle([cx - car_w // 2, cy - car_h // 2, cx + car_w // 2, cy + car_h // 2], fill=(40, 100, 60))
    draw.rectangle([cx - car_w // 2, cy - car_h // 2, cx + car_w // 2, cy + car_h // 2], outline=(30, 80, 50), width=2)
    draw.rectangle([cx - car_w // 2 + 10, cy - car_h // 2 - 5, cx + car_w // 2 - 10, cy - car_h // 2], fill=(40, 100, 60))
    draw.rectangle([cx - car_w // 2 + 10, cy - car_h // 2 - 5, cx + car_w // 2 - 10, cy - car_h // 2], outline=(30, 80, 50), width=1)
    for wx in [cx - 35, cx + 15]:
        draw.rectangle([wx, cy - car_h // 2 - 3, wx + 18, cy - car_h // 2 + 12], fill=(150, 180, 200, 150))
    draw.ellipse([cx - 40, cy + car_h // 2 - 8, cx - 20, cy + car_h // 2 + 8], fill=(30, 30, 30))
    draw.ellipse([cx + 20, cy + car_h // 2 - 8, cx + 40, cy + car_h // 2 + 8], fill=(30, 30, 30))


def draw_three_sisters(draw: ImageDraw, width: int, height: int) -> None:
    silhouettes = [
        (width // 2 - 100, int(height * 0.47), 1.0),
        (width // 2, int(height * 0.45), 1.15),
        (width // 2 + 100, int(height * 0.48), 0.95),
    ]
    for sx, sy, sc in silhouettes:
        h = int(160 * sc)
        draw.ellipse([sx - 10 * sc, sy - h, sx + 10 * sc, sy - h + 20 * sc], fill=(10, 8, 15, 200))
        draw.polygon([(sx - 18 * sc, sy - h + 20 * sc), (sx + 18 * sc, sy - h + 20 * sc), (sx + 20 * sc, sy), (sx - 20 * sc, sy)], fill=(10, 8, 15, 200))
        draw.line([(sx - 20 * sc, sy - 30 * sc), (sx - 40 * sc, sy - 10 * sc)], fill=(10, 8, 15, 200), width=int(5 * sc))
        draw.line([(sx + 20 * sc, sy - 30 * sc), (sx + 40 * sc, sy - 10 * sc)], fill=(10, 8, 15, 200), width=int(5 * sc))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Watermelon Summer")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw, WIDTH, HEIGHT)
    draw_sun(draw, WIDTH, HEIGHT)
    draw_watermelon_field(draw, WIDTH, HEIGHT)
    draw_dirt_road(draw, WIDTH, HEIGHT)
    draw_green_buick(draw, WIDTH, HEIGHT)
    draw_three_sisters(draw, WIDTH, HEIGHT)

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
