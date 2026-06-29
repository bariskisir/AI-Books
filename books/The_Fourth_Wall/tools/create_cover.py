#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Fourth Wall (metafiction)."""

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
    """Cream-to-ink-black gradient — page to void."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((245, 240, 230), (200, 190, 175), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((200, 190, 175), (80, 70, 65), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((80, 70, 65), (15, 10, 10), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_typewriter(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized typewriter silhouette."""
    cx, cy = width // 2, int(height * 0.35)
    base_w, base_h = 280, 40
    roller_w, roller_h = 260, 30
    keys_w, keys_h = 200, 60

    # Base
    draw.rectangle([cx - base_w // 2, cy, cx + base_w // 2, cy + base_h], fill=(30, 25, 20))
    # Roller / carriage
    draw.rectangle([cx - roller_w // 2, cy - roller_h, cx + roller_w // 2, cy], fill=(40, 35, 30))
    draw.rectangle([cx - roller_w // 2 - 10, cy - roller_h - 5, cx + roller_w // 2 + 10, cy - roller_h], fill=(50, 45, 40))
    # Keys area
    draw.rectangle([cx - keys_w // 2, cy + base_h, cx + keys_w // 2, cy + base_h + keys_h], fill=(35, 30, 25))
    # Key rows
    rng = random.Random(8)
    for row in range(4):
        for col in range(8):
            kx = cx - keys_w // 2 + 15 + col * 24 + rng.randint(-2, 2)
            ky = cy + base_h + 10 + row * 14 + rng.randint(-1, 1)
            draw.ellipse([kx - 5, ky - 5, kx + 5, ky + 5], fill=(60, 55, 50))

    # Paper coming out of typewriter
    draw.rectangle(
        [cx - roller_w // 2 + 20, cy - roller_h - 120, cx + roller_w // 2 - 20, cy - roller_h],
        fill=(240, 235, 225),
    )
    # Lines of text on the paper
    for line_idx in range(5):
        ly = cy - roller_h - 100 + line_idx * 18
        lx = cx - roller_w // 2 + 40
        for _ in range(rng.randint(4, 10)):
            lx += rng.randint(12, 20)
            draw.line([(lx, ly), (lx + 8, ly)], fill=(80, 75, 70), width=2)


def draw_manuscript_pages(draw: ImageDraw, width: int, height: int) -> None:
    """Scattered manuscript pages floating/drifting."""
    rng = random.Random(14)
    for _ in range(12):
        px = rng.randint(100, width - 100)
        py = rng.randint(int(height * 0.1), int(height * 0.75))
        angle = rng.uniform(-0.3, 0.3)
        pw, ph = 140, 180

        # Page shadow
        page_img = Image.new("RGBA", (int(pw + 20), int(ph + 20)), (0, 0, 0, 0))
        page_draw = ImageDraw.Draw(page_img)
        page_draw.rectangle([10, 10, 10 + pw, 10 + ph], fill=(235, 230, 220, 200))
        # Text lines on page
        for l in range(5):
            lx = 30
            ly = 40 + l * 28
            for _ in range(rng.randint(3, 7)):
                lx += rng.randint(15, 25)
                page_draw.line([(lx, ly), (lx + rng.randint(20, 50), ly)], fill=(100, 95, 90, 150), width=2)
        rotated = page_img.rotate(angle * 180 / math.pi, expand=True, resample=Image.BICUBIC)
        ox = int(px - rotated.width // 2)
        oy = int(py - rotated.height // 2)
        draw._image.paste(rotated, (ox, oy), rotated)


def draw_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a blurred human figure — Nora/Marcus bleeding through."""
    cx = width // 2
    cy = int(height * 0.58)

    # Create a figure layer
    fig = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fig_draw = ImageDraw.Draw(fig)

    # Head
    head_r = 30
    fig_draw.ellipse([cx - head_r, cy - 120 - head_r, cx + head_r, cy - 120 + head_r], fill=(60, 55, 50, 160))
    # Body
    body_pts = [
        (cx - 50, cy - 90),
        (cx + 50, cy - 90),
        (cx + 60, cy + 40),
        (cx + 70, cy + 100),
        (cx - 70, cy + 100),
        (cx - 60, cy + 40),
    ]
    fig_draw.polygon(body_pts, fill=(60, 55, 50, 150))

    # Apply blur
    fig = fig.filter(ImageFilter.GaussianBlur(radius=12))
    draw._image.paste(fig, (0, 0), fig)


def draw_crack(draw: ImageDraw, width: int, height: int) -> None:
    """A crack/shatter across the center — the fourth wall breaking."""
    rng = random.Random(3)
    start_x = width // 2 + rng.randint(-100, 100)
    start_y = int(height * 0.25)

    for _ in range(3):
        x, y = start_x, start_y
        points = []
        steps = 30
        for s in range(steps + 1):
            t = s / steps
            x += rng.randint(-8, 8)
            y += int(height * 0.5 / steps) + rng.randint(-3, 3)
            points.append((x, y))
        draw.line(points, fill=(200, 195, 185, 180), width=rng.randint(1, 3))

    # Small shatter fragments near the crack
    for _ in range(20):
        fx = start_x + rng.randint(-100, 100)
        fy = start_y + rng.randint(50, 400)
        draw.polygon(
            [(fx, fy), (fx + rng.randint(-10, 10), fy + rng.randint(-10, 10)), (fx + rng.randint(-10, 10), fy + rng.randint(-10, 10))],
            fill=(200, 195, 185, 120),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Dark panel at bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 15, 15, 230))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 75, 70), width=2)

    # Title text
    title = "The Fourth Wall"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 100
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

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
    ay = ty + 120
    draw.text((ax, ay), author, fill=(200, 195, 185), font=author_font)

    # Subtitle line: genre descriptor
    genre_text = "METAFICTION"
    genre_font_size = 20
    try:
        genre_font = ImageFont.truetype(str(font_paths["small"]), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()

    try:
        gbbox = draw.textbbox((0, 0), genre_text, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    gy = ay + 50
    draw.text((gx, gy), genre_text, fill=(150, 145, 135), font=genre_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Fourth Wall")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Crack across the image (fourth wall breaking)
    draw_crack(draw, WIDTH, HEIGHT)

    # Step 3: Scattered manuscript pages
    draw_manuscript_pages(draw, WIDTH, HEIGHT)

    # Step 4: Typewriter silhouette
    draw_typewriter(draw, WIDTH, HEIGHT)

    # Step 5: Blurred figure
    draw_figure(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
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