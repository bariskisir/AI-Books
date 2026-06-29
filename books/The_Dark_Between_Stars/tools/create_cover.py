#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Dark Between Stars — Lovecraftian."""

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
    """Abyssal black to deep green gradient for the seafloor trench feel."""
    # Top: near-black abyss -> middle: dark green -> bottom: black again
    mid = height * 0.45
    for y in range(height):
        if y < mid:
            t = y / mid
            c = lerp_color((2, 2, 5), (5, 20, 10), t)
        elif y < height * 0.8:
            t = (y - mid) / (height * 0.35)
            c = lerp_color((5, 20, 10), (10, 35, 15), t)
        else:
            t = (y - height * 0.8) / (height * 0.2)
            c = lerp_color((10, 35, 15), (1, 3, 1), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_abyss_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Faint green bioluminescent glow emanating from the trench depths."""
    cx, cy = width // 2, height // 2 - 100
    for r in range(600, 100, -20):
        alpha = max(0, 20 - (600 - r) // 30)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(0, 60, 30, max(0, alpha)),
        )


def draw_cyclopean_pillars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw massive cyclopean pillars rising from the abyss — non-Euclidean geometry."""
    import random

    rng = random.Random(13)

    pillar_data = [
        # (x_center, top_y, bottom_y, width, lean_offset)
        (int(width * 0.15), int(height * 0.25), int(height * 0.78), 55, -8),
        (int(width * 0.30), int(height * 0.20), int(height * 0.82), 70, 5),
        (int(width * 0.50), int(height * 0.10), int(height * 0.85), 90, 0),
        (int(width * 0.70), int(height * 0.22), int(height * 0.80), 65, -6),
        (int(width * 0.85), int(height * 0.28), int(height * 0.75), 50, 4),
    ]

    for cx, top_y, bottom_y, pw, lean in pillar_data:
        # Main column body with lean
        steps = 30
        points = []
        for s in range(steps + 1):
            t = s / steps
            y = top_y + (bottom_y - top_y) * t
            x_off = lean * math.sin(t * math.pi * 1.5)
            wobble = rng.randint(-3, 3)
            x = cx + int(x_off) + wobble
            w = pw + int(8 * math.sin(t * math.pi * 2))
            points.append((x - w // 2, y, x + w // 2, y))

        # Draw column as stacked rectangles (pillar body)
        for i in range(len(points) - 1):
            x1, y1, x2, _ = points[i]
            _, y_top, _, y_bot = points[i + 1]
            draw.rectangle([x1, y1, x2, y_bot], fill=(8, 12, 8))
            # Edge highlight
            draw.line([(x1, y1), (x1, y_bot)], fill=(15, 25, 15), width=1)
            draw.line([(x2, y1), (x2, y_bot)], fill=(15, 25, 15), width=1)

        # Top capital (non-Euclidean shape)
        cap_w = pw + 30
        cap_h = 30
        draw.polygon(
            [
                (cx - cap_w // 2, top_y),
                (cx - cap_w // 2 - 10, top_y + cap_h),
                (cx + cap_w // 2 + 10, top_y + cap_h),
                (cx + cap_w // 2, top_y),
            ],
            fill=(10, 20, 12),
        )
        # Glowing symbol on capital
        symbol_color = (0, 80, 40, 60)
        draw.ellipse(
            [cx - 12, top_y + 5, cx + 12, top_y + cap_h - 5],
            fill=symbol_color,
        )

    # Additional background pillars (darker, smaller)
    for i in range(6):
        cx_bg = rng.randint(50, width - 50)
        bg_pw = rng.randint(25, 40)
        bg_top = rng.randint(int(height * 0.35), int(height * 0.55))
        bg_bot = int(height * 0.85)
        draw.rectangle(
            [cx_bg - bg_pw // 2, bg_top, cx_bg + bg_pw // 2, bg_bot],
            fill=(4, 6, 4),
        )


def draw_trench_floor(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the trench floor with ancient stonework and symbols."""
    # Base floor
    floor_y = int(height * 0.78)
    draw.rectangle([(0, floor_y), (width, int(height * 0.85))], fill=(5, 10, 5))

    # Stone tiles
    for tx in range(0, width, 60):
        draw.line([(tx, floor_y), (tx, int(height * 0.85))], fill=(8, 15, 8), width=1)

    # Horizontal lines
    for ty in range(floor_y, int(height * 0.85), 20):
        draw.line([(0, ty), (width, ty)], fill=(8, 15, 8), width=1)

    # Glowing symbols on floor
    import random
    rng = random.Random(17)
    for _ in range(15):
        sx = rng.randint(20, width - 20)
        sy = rng.randint(floor_y + 5, int(height * 0.83))
        size = rng.randint(6, 14)
        draw.ellipse(
            [sx - size // 2, sy - size // 2, sx + size // 2, sy + size // 2],
            fill=(0, 60, 30, 80),
        )


def draw_ancient_ruins(draw: ImageDraw, width: int, height: int) -> None:
    """Draw cyclopean ruin arches in the midground."""
    import random

    rng = random.Random(31)
    # Arches
    arch_positions = [
        (int(width * 0.08), int(height * 0.50), 40, 120),
        (int(width * 0.22), int(height * 0.45), 50, 140),
        (int(width * 0.78), int(height * 0.47), 45, 130),
        (int(width * 0.92), int(height * 0.52), 35, 110),
    ]

    for ax, ay, aw, ah in arch_positions:
        # Arch pillars
        draw.rectangle([ax - aw // 2, ay, ax - aw // 4, ay + ah], fill=(6, 10, 6))
        draw.rectangle([ax + aw // 4, ay, ax + aw // 2, ay + ah], fill=(6, 10, 6))
        # Arch top
        draw.arc([ax - aw // 2, ay - aw // 2, ax + aw // 2, ay + aw // 2], 0, 180, fill=(8, 14, 8), width=4)


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark rectangular title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(5, 8, 5, 220))

    # Subtle border at top of panel
    draw.line([(40, panel_top), (width - 40, panel_top)], fill=(0, 80, 40), width=2)

    # Green glow line beneath border
    draw.line([(60, panel_top + 4), (width - 60, panel_top + 4)], fill=(0, 40, 20, 100), width=1)

    # Title text — use arialbd.ttf as instructed (NOT georgiab.ttf)
    title = "The Dark\nBetween Stars"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 70
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # Drop shadow for readability
        draw.text((tx + 2, y_offset + 2), line, fill=(0, 30, 15), font=title_font)
        draw.text((tx, y_offset), line, fill=(220, 230, 220), font=title_font)
        y_offset += 95

    # Author name
    author = "Barış Kısır"
    author_font_size = 38
    try:
        author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = y_offset + 30
    # Drop shadow
    draw.text((ax + 2, ay + 2), author, fill=(0, 30, 15), font=author_font)
    draw.text((ax, ay), author, fill=(180, 200, 180), font=author_font)


def draw_bioluminescent_particles(draw: ImageDraw, width: int, height: int) -> None:
    """Draw floating green bioluminescent particles throughout the scene."""
    import random

    rng = random.Random(23)
    for _ in range(80):
        x = rng.randint(50, width - 50)
        y = rng.randint(int(height * 0.15), int(height * 0.75))
        size = rng.randint(2, 6)
        alpha = rng.randint(40, 120)
        r_val = rng.randint(0, 20)
        g_val = rng.randint(80, 200)
        b_val = rng.randint(10, 60)
        # Outer glow
        draw.ellipse(
            [x - size * 3, y - size * 3, x + size * 3, y + size * 3],
            fill=(r_val, g_val, b_val, alpha // 3),
        )
        # Inner glow
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(r_val, g_val, b_val, alpha),
        )
        # Bright center
        draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(150, 255, 150, 180))


def draw_submerged_ship(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small silhouette of a trawler (the Rodbroke) on the surface."""
    sx, sy = int(width * 0.72), int(height * 0.18)
    # Hull
    draw.polygon(
        [(sx - 30, sy), (sx + 30, sy), (sx + 35, sy + 12), (sx - 35, sy + 12)],
        fill=(3, 5, 3),
    )
    # Cabin
    draw.rectangle([sx - 10, sy - 15, sx + 10, sy], fill=(4, 6, 4))
    # Mast
    draw.line([(sx, sy - 15), (sx, sy - 30)], fill=(3, 5, 3), width=2)
    # Ripples
    for i in range(3):
        ry = sy + 12 + i * 4
        draw.arc(
            [sx - 40 - i * 10, ry - 2, sx + 40 + i * 10, ry + 2],
            0, 180, fill=(0, 30, 15, 60 - i * 15), width=1,
        )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (abyssal black to deep green)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Abyss glow
    draw_abyss_glow(draw, WIDTH, HEIGHT)

    # Step 3: Ancient ruins (midground)
    draw_ancient_ruins(draw, WIDTH, HEIGHT)

    # Step 4: Cyclopean pillars (foreground)
    draw_cyclopean_pillars(draw, WIDTH, HEIGHT)

    # Step 5: Trench floor with symbols
    draw_trench_floor(draw, WIDTH, HEIGHT)

    # Step 6: Submerged ship silhouette
    draw_submerged_ship(draw, WIDTH, HEIGHT)

    # Step 7: Bioluminescent particles
    draw_bioluminescent_particles(draw, WIDTH, HEIGHT)

    # Step 8: Title panel (dark, white text using arialbd.ttf)
    draw_title_panel(draw, WIDTH, HEIGHT)

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