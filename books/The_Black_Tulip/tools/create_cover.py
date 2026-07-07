#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Black Tulip."""

from __future__ import annotations

import argparse
import json
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
    """Warm Dutch sky gradient: deep tulip red to amber to dark brown."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((180, 80, 60), (210, 140, 70), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((210, 140, 70), (140, 90, 50), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((140, 90, 50), (60, 35, 20), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_sky_elements(draw: ImageDraw, width: int, height: int) -> None:
    """Draw clouds and a sun in the upper portion of the image."""
    rng = random.Random(13)

    # Sun glow
    sun_x, sun_y = width // 3, int(height * 0.12)
    for r in range(60, 10, -5):
        alpha = max(0, 180 - r * 3)
        draw.ellipse(
            [sun_x - r, sun_y - r, sun_x + r, sun_y + r],
            fill=(255, 220, 150, alpha),
        )

    # Clouds
    for _ in range(6):
        cx = rng.randint(100, width - 100)
        cy = rng.randint(50, int(height * 0.2))
        cw = rng.randint(120, 250)
        ch = rng.randint(30, 60)
        draw.ellipse([cx, cy, cx + cw, cy + ch], fill=(220, 200, 170, 80))
        draw.ellipse([cx + cw // 3, cy - 15, cx + cw * 2 // 3, cy + ch + 10], fill=(210, 190, 160, 60))


def draw_canal(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a canal with reflections in the middle distance."""
    cy = int(height * 0.55)
    ch = int(height * 0.08)

    # Water body
    draw.rectangle([(0, cy), (width, cy + ch)], fill=(70, 90, 100, 180))

    # Water shimmer lines
    rng = random.Random(17)
    for _ in range(30):
        lx = rng.randint(0, width)
        ly = cy + rng.randint(0, ch)
        lw = rng.randint(20, 80)
        draw.line([(lx, ly), (lx + lw, ly)], fill=(120, 150, 160, 60), width=1)


def draw_tulip_fields(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rows of colorful tulips in the foreground fields."""
    rng = random.Random(5)
    field_top = int(height * 0.50)
    field_bottom = int(height * 0.75)

    colors = [
        (180, 40, 40),    # Red
        (200, 60, 50),    # Tulip red
        (160, 30, 80),    # Dark pink
        (220, 180, 40),   # Yellow
        (200, 100, 30),   # Orange
        (140, 40, 120),   # Purple
        (40, 40, 40),     # Near-black (the goal)
    ]

    # Draw rows of tulips
    for row in range(12):
        ry = field_top + row * 18 + rng.randint(0, 5)
        rx = rng.randint(0, 20)
        while rx < width:
            # Tulip flower
            flower_color = rng.choice(colors)
            flower_h = rng.randint(12, 20)
            flower_w = rng.randint(8, 14)

            # Petals (three overlapping ellipses)
            draw.ellipse([rx, ry - flower_h, rx + flower_w, ry], fill=flower_color)
            draw.ellipse([rx - 3, ry - flower_h + 3, rx + flower_w + 3, ry + 2], fill=flower_color)

            # Stem
            stem_h = rng.randint(15, 25)
            draw.line([(rx + flower_w // 2, ry), (rx + flower_w // 2, ry + stem_h)], fill=(60, 80, 40), width=2)

            rx += rng.randint(25, 45)


def draw_windmill(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a Dutch windmill on the horizon."""
    mx = int(width * 0.75)
    my = int(height * 0.42)

    # Base tower (trapezoidal)
    tower_w_top = 40
    tower_w_bot = 55
    tower_h = 120
    draw.polygon(
        [
            (mx - tower_w_top // 2, my - tower_h),
            (mx + tower_w_top // 2, my - tower_h),
            (mx + tower_w_bot // 2, my),
            (mx - tower_w_bot // 2, my),
        ],
        fill=(120, 80, 50),
    )

    # Tower cap (conical roof)
    draw.polygon(
        [
            (mx - tower_w_top // 2 - 5, my - tower_h),
            (mx + tower_w_top // 2 + 5, my - tower_h),
            (mx, my - tower_h - 30),
        ],
        fill=(100, 60, 35),
    )

    # Blades
    blade_length = 70
    blade_width = 8
    for angle in [0, 45, 90, 135]:
        rad = angle * 3.14159 / 180
        ex = mx + int(blade_length * __import__("math").cos(rad))
        ey = (my - tower_h) + int(blade_length * __import__("math").sin(rad))
        draw.line([(mx, my - tower_h), (ex, ey)], fill=(80, 55, 35), width=blade_width)

    # Blade cross-bars
    for angle in [22.5, 67.5, 112.5, 157.5]:
        rad = angle * 3.14159 / 180
        mid_x = mx + int(blade_length * 0.5 * __import__("math").cos(rad))
        mid_y = (my - tower_h) + int(blade_length * 0.5 * __import__("math").sin(rad))
        perp_rad = rad + 1.5708
        px1 = mid_x + int(15 * __import__("math").cos(perp_rad))
        py1 = mid_y + int(15 * __import__("math").sin(perp_rad))
        px2 = mid_x - int(15 * __import__("math").cos(perp_rad))
        py2 = mid_y - int(15 * __import__("math").sin(perp_rad))
        draw.line([(px1, py1), (px2, py2)], fill=(80, 55, 35), width=3)

    # Door
    draw.rectangle([mx - 10, my - 30, mx + 10, my], fill=(60, 35, 20))


def draw_canal_house(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a traditional Amsterdam canal house silhouette on the horizon."""
    hx = int(width * 0.25)
    hy = int(height * 0.42)

    # Building body
    bw, bh = 70, 100
    draw.rectangle([hx - bw // 2, hy - bh, hx + bw // 2, hy], fill=(90, 65, 45))

    # Gable
    gable_w = bw + 20
    draw.polygon(
        [
            (hx - gable_w // 2, hy - bh),
            (hx + gable_w // 2, hy - bh),
            (hx + bw // 2, hy - bh - 30),
            (hx - bw // 2, hy - bh - 30),
        ],
        fill=(100, 75, 55),
    )

    # Windows
    for wx in range(-20, 25, 20):
        wy = hy - bh + 15
        draw.rectangle([hx + wx - 6, wy, hx + wx + 6, wy + 20], fill=(200, 180, 130, 150))
        draw.rectangle([hx + wx - 6, wy, hx + wx + 6, wy + 20], outline=(60, 40, 25), width=1)

    # Door
    draw.rectangle([hx - 8, hy - 25, hx + 8, hy], fill=(60, 35, 20))


def draw_canal_bridge(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small arched bridge over the canal."""
    bx = int(width * 0.5)
    by = int(height * 0.53)

    # Arch
    arch_r = 60
    for y_offset in range(arch_r):
        line_width = max(1, 8 - y_offset // 4)
        # Left side of arch
        draw.arc(
            [bx - arch_r, by - arch_r + y_offset, bx + arch_r, by + arch_r],
            start=0,
            end=180,
            fill=(100, 75, 55),
            width=line_width,
        )

    # Bridge surface
    draw.line([(bx - arch_r - 20, by), (bx + arch_r + 20, by)], fill=(120, 90, 65), width=6)

    # Railings
    draw.line([(bx - arch_r - 20, by - 12), (bx + arch_r + 20, by - 12)], fill=(80, 55, 35), width=3)
    for px in range(bx - arch_r, bx + arch_r + 1, 15):
        draw.line([(px, by - 12), (px, by)], fill=(80, 55, 35), width=2)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(30, 20, 15, 220))

    # Subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 100, 50), width=3)

    # Subtle inner glow line
    draw.line([(0, panel_top + 4), (width, panel_top + 4)], fill=(80, 50, 30, 100), width=1)

    # Title text
    title = "The Black Tulip"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 90
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Decorative line under title
    line_y = ty + 85
    line_w = 200
    draw.line([(width // 2 - line_w // 2, line_y), (width // 2 + line_w // 2, line_y)], fill=(180, 100, 50), width=2)

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = line_y + 40
    draw.text((ax, ay), author, fill=(220, 200, 180), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (warm Dutch sky)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Sky elements (clouds, sun)
    draw_sky_elements(draw, WIDTH, HEIGHT)

    # Step 3: Canal in middle distance
    draw_canal(draw, WIDTH, HEIGHT)

    # Step 4: Canal house silhouette
    draw_canal_house(draw, WIDTH, HEIGHT)

    # Step 5: Windmill on horizon
    draw_windmill(draw, WIDTH, HEIGHT)

    # Step 6: Small arched bridge
    draw_canal_bridge(draw, WIDTH, HEIGHT)

    # Step 7: Tulip fields in foreground
    draw_tulip_fields(draw, WIDTH, HEIGHT)

    # Step 8: Title panel (dark background, white text)
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
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