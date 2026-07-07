#!/usr/bin/env python3
"""Cover: The Half-Life of Love — Dark blue/terracotta gradient, CERN tunnel perspective, glowing particle traces, blue/terracotta/luminous cyan."""

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
    """Dark blue to terracotta gradient — science-romance."""
    for y in range(height):
        if y < height * 0.35:
            t = y / (height * 0.35)
            c = lerp_color((5, 5, 35), (15, 20, 70), t)
        elif y < height * 0.65:
            t = (y - height * 0.35) / (height * 0.30)
            c = lerp_color((15, 20, 70), (120, 65, 45), t)
        else:
            t = (y - height * 0.65) / (height * 0.35)
            c = lerp_color((120, 65, 45), (60, 30, 20), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_cern_tunnel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized LHC tunnel receding into perspective."""
    cx = width // 2
    tunnel_end = int(height * 0.35)

    # Tunnel walls
    wall_top = int(height * 0.08)
    wall_bottom = int(height * 0.55)
    wall_left = int(width * 0.05)
    wall_right = int(width * 0.95)

    # Outer tunnel walls (concrete gray-blue)
    points_left = [(0, 0), (cx, tunnel_end), (cx, tunnel_end), (wall_left, wall_top)]
    draw.polygon(points_left, fill=(25, 30, 45))

    points_right = [(width, 0), (cx, tunnel_end), (cx, tunnel_end), (wall_right, wall_top)]
    draw.polygon(points_right, fill=(25, 30, 45))

    # Floor
    floor_points = [(wall_left, wall_top), (wall_right, wall_top), (width, height), (0, height)]
    draw.polygon(floor_points, fill=(20, 25, 35))

    # Ceiling
    ceiling_points = [(0, 0), (width, 0), (wall_right, wall_top), (wall_left, wall_top)]
    draw.polygon(ceiling_points, fill=(15, 18, 28))

    # Concrete rings (horizontal bands on tunnel walls)
    for i in range(8):
        t = i / 8
        y_pos = int(wall_top + (height - wall_top) * t * 0.3)
        alpha = max(0, 60 - i * 7)
        draw.line([(int(cx - cx * (1 - t) * 0.95), y_pos), (int(cx + cx * (1 - t) * 0.95), y_pos)],
                  fill=(40 + i * 3, 45 + i * 3, 60 + i * 2), width=2)

    # Beam pipe (center line)
    for i in range(15):
        t = i / 15
        y_start = int(tunnel_end + (height * 0.45 - tunnel_end) * t)
        beam_y = y_start
        beam_width = max(1, int(12 * (1 - t)))
        alpha = max(30, int(200 * (1 - t)))
        draw.line([(cx - beam_width, beam_y), (cx + beam_width, beam_y)],
                  fill=(100, 150, 255, alpha), width=beam_width)


def draw_particle_tracks(draw: ImageDraw, width: int, height: int) -> None:
    """Draw glowing particle tracks radiating from collision point."""
    cx = width // 2
    cy = int(height * 0.25)

    rng = random.Random(42)
    colors = [
        (100, 255, 255),   # Luminous cyan
        (255, 200, 100),   # Gold
        (200, 100, 255),   # Violet
        (100, 200, 255),   # Blue
        (60, 255, 200),    # Teal
    ]

    for _ in range(60):
        angle = rng.uniform(0, 2 * math.pi)
        length = rng.randint(100, 500)
        curve = rng.uniform(-0.5, 0.5)
        color = rng.choice(colors)
        alpha = rng.randint(40, 120)
        width_variation = rng.uniform(1, 4)

        points = []
        for step in range(20):
            t = step / 19
            x = cx + math.cos(angle) * length * t + math.sin(angle * 2) * curve * 50 * t
            y = cy + math.sin(angle) * length * t + math.cos(angle * 2) * curve * 30 * t
            points.append((int(x), int(y)))

        draw.line(points, fill=color + (alpha,), width=int(width_variation))


def draw_pottery_wheel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized pottery wheel with a forming pot on it."""
    # Positioned in the lower third of the image
    base_x = width // 2
    base_y = int(height * 0.70)

    # Wheel base (rectangular table)
    table_w = 300
    table_h = 20
    draw.rectangle([base_x - table_w // 2, base_y + 60, base_x + table_w // 2, base_y + 80],
                   fill=(60, 45, 30))

    # Wheel head (circle)
    wheel_radius = 70
    draw.ellipse([base_x - wheel_radius, base_y - wheel_radius + 60,
                  base_x + wheel_radius, base_y + wheel_radius + 60],
                 fill=(80, 65, 50))
    draw.ellipse([base_x - wheel_radius + 5, base_y - wheel_radius + 65,
                  base_x + wheel_radius - 5, base_y + wheel_radius + 55],
                 fill=(90, 75, 55))

    # Pot being formed (clay cylinder on wheel)
    pot_bottom = base_y + 55
    pot_top = base_y - 40
    pot_width_bottom = 50
    pot_width_top = 35

    # Pot body
    draw.polygon([
        (base_x - pot_width_bottom, pot_bottom),
        (base_x - pot_width_top, pot_top),
        (base_x + pot_width_top, pot_top),
        (base_x + pot_width_bottom, pot_bottom)
    ], fill=(160, 100, 55))

    # Pot rim
    draw.ellipse([base_x - pot_width_top - 5, pot_top - 8,
                  base_x + pot_width_top + 5, pot_top + 8],
                 fill=(180, 120, 70))

    # Hands (simplified)
    draw.ellipse([base_x - pot_width_bottom - 25, pot_bottom - 30,
                  base_x - pot_width_bottom + 5, pot_bottom + 10],
                 fill=(200, 160, 120))
    draw.ellipse([base_x + pot_width_bottom - 5, pot_bottom - 30,
                  base_x + pot_width_bottom + 25, pot_bottom + 10],
                 fill=(200, 160, 120))


def draw_blue_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw atmospheric blue glow around the collision point and pottery wheel."""
    cx = width // 2

    # Glow at collision point
    glow_center_y = int(height * 0.25)
    for r in range(80, 0, -1):
        alpha = max(0, 200 - r * 3)
        draw.ellipse([cx - r * 4, glow_center_y - r * 4,
                      cx + r * 4, glow_center_y + r * 4],
                     fill=(30, 60, 180, alpha // 8))

    # Glow around wheel
    wheel_y = int(height * 0.70)
    for r in range(60, 0, -1):
        alpha = max(0, 150 - r * 3)
        draw.ellipse([cx - r * 3, wheel_y - r * 3,
                      cx + r * 3, wheel_y + r * 3],
                     fill=(100, 50, 30, alpha // 6))


def draw_terracotta_shards(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered terracotta shards on the ground."""
    rng = random.Random(17)
    for _ in range(15):
        x = rng.randint(50, width - 50)
        y = rng.randint(int(height * 0.65), int(height * 0.82))
        size = rng.randint(10, 30)
        angle = rng.uniform(0, 2 * math.pi)
        color = (160 + rng.randint(-20, 20), 100 + rng.randint(-20, 20), 55 + rng.randint(-15, 15))
        points = []
        for corner in range(3):
            a = angle + corner * 2 * math.pi / 3 + rng.uniform(-0.3, 0.3)
            r = size * rng.uniform(0.5, 1.0)
            points.append((int(x + math.cos(a) * r), int(y + math.sin(a) * r)))
        draw.polygon(points, fill=color)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        r = int(15 + 5 * t)
        g = int(12 + 5 * t)
        b = int(25 + 5 * t)
        alpha = 200 + int(55 * t)
        draw.line([(0, y), (width, y)], fill=(r, g, b, alpha))

    # Subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 120, 200), width=2)

    # Title text
    title = "The Half-Life\nof Love"
    title_font_size = 64
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        try:
            title_font = ImageFont.truetype(str(font_paths["title_fallback"]), title_font_size)
        except Exception:
            title_font = ImageFont.load_default()

    # Draw title centered in white
    lines = title.split("\n")
    y_offset = panel_top + 70
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 85

    # Author name
    author = "Barış Kısır"
    author_font_size = 32
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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(200, 210, 255), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Half-Life of Love")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: CERN tunnel perspective
    draw_cern_tunnel(draw, WIDTH, HEIGHT)

    # Step 3: Blue glow atmosphere
    draw_blue_glow(draw, WIDTH, HEIGHT)

    # Step 4: Particle tracks from collision point
    draw_particle_tracks(draw, WIDTH, HEIGHT)

    # Step 5: Pottery wheel with forming pot
    draw_pottery_wheel(draw, WIDTH, HEIGHT)

    # Step 6: Terracotta shards
    draw_terracotta_shards(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "title_fallback": str(FONTS_DIR / "arial.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften the image slightly
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