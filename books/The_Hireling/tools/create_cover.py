#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Hireling — Historical Noir."""

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
    """Sand to deep shadow gradient for the Casablanca noir feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((210, 180, 140), (180, 140, 100), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((180, 140, 100), (100, 70, 50), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((100, 70, 50), (20, 15, 12), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_medina_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouette of the Casablanca medina skyline."""
    rng = random.Random(17)

    # Buildings along the horizon
    building_heights = []
    x = 0
    while x < width:
        bw = rng.randint(40, 120)
        bh = rng.randint(80, 250)
        bx = x
        building_heights.append((bx, bw, bh))
        x += bw + rng.randint(2, 10)

    for bx, bw, bh in building_heights:
        top_y = int(height * 0.28) - bh
        # Building body
        draw.rectangle([bx, top_y, bx + bw, int(height * 0.28)], fill=(30, 22, 18))
        # Rooftop detail
        if rng.random() < 0.4:
            draw.rectangle([bx + bw // 4, top_y - 10, bx + bw * 3 // 4, top_y], fill=(25, 18, 14))
        # Windows (small lit rectangles)
        for wy in range(top_y + 20, int(height * 0.26), rng.randint(20, 35)):
            for wx in range(bx + 8, bx + bw - 8, rng.randint(15, 25)):
                if rng.random() < 0.3:
                    draw.rectangle([wx, wy, wx + 6, wy + 8], fill=(220, 190, 120, 80))

    # Minaret silhouette
    minaret_x = width // 3
    minaret_h = 300
    minaret_top_y = int(height * 0.28) - minaret_h
    draw.rectangle([minaret_x - 8, minaret_top_y, minaret_x + 8, int(height * 0.28)], fill=(25, 18, 14))
    # Minaret top
    draw.polygon(
        [(minaret_x - 12, minaret_top_y), (minaret_x + 12, minaret_top_y), (minaret_x, minaret_top_y - 25)],
        fill=(25, 18, 14),
    )

    # Second minaret
    minaret2_x = width * 3 // 4
    draw.rectangle([minaret2_x - 6, minaret_top_y + 60, minaret2_x + 6, int(height * 0.28)], fill=(25, 18, 15))
    draw.polygon(
        [
            (minaret2_x - 10, minaret_top_y + 60),
            (minaret2_x + 10, minaret_top_y + 60),
            (minaret2_x, minaret_top_y + 35),
        ],
        fill=(25, 18, 15),
    )


def draw_alley(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a shadowy alley receding into the distance."""
    # Alley floor
    alley_center_x = width // 2 + 80
    alley_top_w = 60
    alley_bottom_w = 500
    alley_top_y = int(height * 0.35)
    alley_bottom_y = int(height * 0.65)

    # Left wall
    left_wall = [
        (alley_center_x - alley_bottom_w // 2, alley_bottom_y),
        (alley_center_x - alley_top_w // 2, alley_top_y),
        (alley_center_x + alley_top_w // 2, alley_top_y),
        (alley_center_x + alley_bottom_w // 2, alley_bottom_y),
    ]
    draw.polygon(left_wall, fill=(15, 10, 8))

    # Right wall
    right_wall = [
        (alley_center_x + alley_bottom_w // 2, alley_bottom_y),
        (alley_center_x + alley_top_w // 2, alley_top_y),
        (width + 200, alley_top_y),
        (width + 200, alley_bottom_y),
    ]
    draw.polygon(right_wall, fill=(20, 14, 10))

    # Archway at end
    arch_center_x = alley_center_x
    arch_center_y = alley_top_y + 60
    arch_radius = 40
    draw.arc(
        [arch_center_x - arch_radius, arch_center_y - arch_radius, arch_center_x + arch_radius, arch_center_y + arch_radius],
        0,
        180,
        fill=(60, 50, 40),
        width=4,
    )

    # Light at end of alley
    for i in range(10):
        t = i / 10
        r = int(10 + t * 30)
        glow = (180 + int(50 * (1 - t)), 160 + int(40 * (1 - t)), 80 + int(30 * (1 - t)), 40 - int(35 * t))
        draw.ellipse(
            [arch_center_x - r, arch_center_y - r, arch_center_x + r, arch_center_y + r],
            fill=glow,
        )

    # Floor detail
    for fy in range(alley_top_y + 30, alley_bottom_y, 25):
        t = (fy - alley_top_y) / (alley_bottom_y - alley_top_y)
        line_w = int(alley_top_w + (alley_bottom_w - alley_top_w) * t)
        lx = alley_center_x - line_w // 2
        draw.line([(lx, fy), (lx + line_w, fy)], fill=(25, 18, 14), width=1)


def draw_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouetted figure in a 1940s suit and fedora."""
    cx, cy = width // 2 - 60, int(height * 0.52)

    # Body (trench coat / suit silhouette)
    body_top = cy - 80
    body_bottom = cy + 60
    # Torso
    draw.polygon(
        [
            (cx - 50, body_bottom),
            (cx - 30, body_top + 20),
            (cx + 30, body_top + 20),
            (cx + 50, body_bottom),
        ],
        fill=(10, 8, 6),
    )
    # Shoulders
    draw.polygon(
        [
            (cx - 60, body_top + 30),
            (cx - 30, body_top + 10),
            (cx + 30, body_top + 10),
            (cx + 60, body_top + 30),
        ],
        fill=(12, 10, 8),
    )

    # Head
    head_radius = 18
    draw.ellipse(
        [cx - head_radius, body_top - 30, cx + head_radius, body_top + 6],
        fill=(8, 6, 5),
    )

    # Fedora
    brim_y = body_top - 32
    hat_top_y = body_top - 48
    draw.ellipse([cx - 30, brim_y - 4, cx + 30, brim_y + 6], fill=(5, 4, 3))
    draw.rectangle([cx - 18, hat_top_y, cx + 18, brim_y + 2], fill=(5, 4, 3))
    # Hat band
    draw.rectangle([cx - 18, brim_y - 4, cx + 18, brim_y], fill=(15, 12, 10))

    # Cigarette glow
    cig_x = cx + 25
    cig_y = body_top + 5
    draw.rectangle([cig_x, cig_y, cig_x + 12, cig_y + 2], fill=(180, 170, 150))
    draw.ellipse([cig_x, cig_y - 3, cig_x + 6, cig_y + 5], fill=(255, 200, 50, 200))
    # Smoke wisps
    for i in range(3):
        sx = cig_x + i * 3
        sy = cig_y - 4 - i * 12
        draw.ellipse([sx - 3, sy - 6, sx + 3, sy], fill=(200, 190, 170, 30 + i * 10))


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a pale moon in the sky."""
    mx, my = width - 200, 120
    moon_r = 45
    draw.ellipse([mx - moon_r, my - moon_r, mx + moon_r, my + moon_r], fill=(220, 210, 190, 180))
    # Glow
    for i in range(5):
        r = moon_r + 10 + i * 15
        alpha = 20 - i * 4
        draw.ellipse([mx - r, my - r, mx + r, my + r], fill=(220, 210, 190, max(0, alpha)))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        c = lerp_color((20, 15, 12), (10, 8, 6), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 50, 40), width=3)

    # Decorative line
    line_y = panel_top + 10
    draw.line([(200, line_y), (width - 200, line_y)], fill=(80, 70, 55), width=1)

    # Title text
    title = "The Hireling"
    title_font_size = 96
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
    ty = panel_top + 80

    # Shadow behind title
    shadow_offset = 3
    draw.text((tx + shadow_offset, ty + shadow_offset), title, fill=(0, 0, 0, 100), font=title_font)
    # Main title in white
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Tag line
    tagline = "A Novel of Casablanca"
    tag_font_size = 28
    try:
        tag_font = ImageFont.truetype(str(font_paths["small"]), tag_font_size)
    except Exception:
        tag_font = ImageFont.load_default()

    try:
        tbbox = draw.textbbox((0, 0), tagline, font=tag_font)
        ttw = tbbox[2] - tbbox[0]
    except Exception:
        ttw = 0
    ttx = (width - ttw) // 2
    tty = ty + 110
    draw.text((ttx, tty), tagline, fill=(180, 170, 155), font=tag_font)

    # Author name
    author = "Barış Kısır"
    author_font_size = 40
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
    ay = tty + 60
    draw.text((ax, ay), author, fill=(255, 255, 255), font=author_font)

    # Bottom decorative line
    bottom_line_y = ay + 60
    draw.line([(300, bottom_line_y), (width - 300, bottom_line_y)], fill=(80, 70, 55), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Hireling")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (sand to shadow)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Moon
    draw_moon(draw, WIDTH, HEIGHT)

    # Step 3: Medina skyline
    draw_medina_skyline(draw, WIDTH, HEIGHT)

    # Step 4: Shadowy alley
    draw_alley(draw, WIDTH, HEIGHT)

    # Step 5: Silhouetted figure in suit and fedora
    draw_figure(draw, WIDTH, HEIGHT)

    # Step 6: Title panel at bottom
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