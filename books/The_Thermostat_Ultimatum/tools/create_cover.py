#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Thermostat Ultimatum (Climate Thriller)."""

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


def draw_stratosphere_sky(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark upper-atmosphere sky gradient."""
    for y in range(height):
        if y < height * 0.2:
            t = y / (height * 0.2)
            c = lerp_color((5, 5, 25), (15, 10, 40), t)
        elif y < height * 0.45:
            t = (y - height * 0.2) / (height * 0.25)
            c = lerp_color((15, 10, 40), (60, 50, 100), t)
        elif y < height * 0.65:
            t = (y - height * 0.45) / (height * 0.2)
            c = lerp_color((60, 50, 100), (150, 120, 100), t)
        else:
            t = (y - height * 0.65) / (height * 0.35)
            c = lerp_color((150, 120, 100), (20, 15, 10), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_stratus_sheen(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a thin reflective aerosol sheen across the upper atmosphere."""
    sheen_y = int(height * 0.2)
    for x in range(0, width, 4):
        shimmer = int(math.sin(x * 0.02) * 40 + math.sin(x * 0.05) * 15)
        sheen_color = (180, 200, 255, max(0, min(60, 40 + shimmer)))
        for dy in range(-30, 30):
            draw.point((x, sheen_y + dy + int(math.sin(x * 0.01 + dy * 0.1) * 5)), fill=sheen_color)


def draw_mountain_range(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the Atlas Mountains silhouette."""
    mt_height = int(height * 0.5)
    peak_data = []
    for x in range(0, width + 10, 8):
        peak = mt_height + int(math.sin(x * 0.003) * 80 + math.sin(x * 0.008) * 40 + math.sin(x * 0.015) * 20)
        peak_data.append((x, peak))

    # Shadow mountains (background)
    for i in range(len(peak_data) - 1):
        x1, y1 = peak_data[i]
        x2, y2 = peak_data[i+1]
        draw.polygon([(x1, y1), (x2, y2), (x2, HEIGHT), (x1, HEIGHT)], fill=(25, 20, 30))

    # Lighter foreground peaks
    fg_peaks = []
    for x in range(0, width + 10, 5):
        peak = mt_height + 30 + int(math.sin(x * 0.004 + 1) * 60 + math.sin(x * 0.012) * 30)
        fg_peaks.append((x, peak))

    for i in range(len(fg_peaks) - 1):
        x1, y1 = fg_peaks[i]
        x2, y2 = fg_peaks[i+1]
        draw.polygon([(x1, y1), (x2, y2), (x2, HEIGHT), (x1, HEIGHT)], fill=(35, 30, 40))


def draw_stratus_domes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the silver domes of the geoengineering facility."""
    base_y = int(height * 0.62)
    centers = [
        (width // 2 - 200, base_y, 80),
        (width // 2 - 80, base_y - 20, 100),
        (width // 2 + 60, base_y - 10, 90),
        (width // 2 + 180, base_y + 10, 70),
        (width // 2 - 30, base_y - 70, 45),
    ]

    for cx, cy, radius in centers:
        # Dome shadow
        draw.ellipse([cx - radius - 5, cy - 5, cx + radius + 5, cy + int(radius * 0.4) + 5], fill=(10, 8, 15))
        # Dome body
        draw.ellipse([cx - radius, cy - int(radius * 0.6), cx + radius, cy + int(radius * 0.3)], fill=(160, 170, 180))
        # Dome highlight
        draw.ellipse([cx - int(radius * 0.6), cy - int(radius * 0.5), cx + int(radius * 0.1), cy - int(radius * 0.1)], fill=(200, 210, 220, 120))
        # Dome outline
        draw.arc([cx - radius, cy - int(radius * 0.6), cx + radius, cy + int(radius * 0.3)], 0, 180, fill=(100, 110, 120), width=2)


def draw_injection_tower(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an aerosol injection tower rising from the domes."""
    base_x = width // 2 - 30
    base_y = int(height * 0.55)
    tower_height = 300

    # Main tower structure
    draw.rectangle([base_x - 8, base_y - tower_height, base_x + 8, base_y], fill=(120, 130, 140))

    # Truss details
    for i in range(8):
        y = base_y - i * (tower_height // 8)
        draw.line([(base_x - 15, y), (base_x + 15, y)], fill=(80, 90, 100), width=1)
        draw.line([(base_x - 15, y), (base_x - 8, y - tower_height // 16)], fill=(80, 90, 100), width=1)
        draw.line([(base_x + 15, y), (base_x + 8, y - tower_height // 16)], fill=(80, 90, 100), width=1)

    # Injection nozzle at top
    nozzle_y = base_y - tower_height
    draw.ellipse([base_x - 12, nozzle_y - 8, base_x + 12, nozzle_y + 8], fill=(80, 90, 100))

    # Spray effect - aerosol particles being released
    for angle_step in range(20):
        angle = math.radians(200 + angle_step * 10 + math.sin(angle_step) * 20)
        length = 40 + angle_step * 5
        ex = base_x + int(math.cos(angle) * length)
        ey = nozzle_y + int(math.sin(angle) * length)
        particle_size = 3 + angle_step % 4
        alpha = max(20, 100 - angle_step * 4)
        draw.ellipse([ex - particle_size, ey - particle_size, ex + particle_size, ey + particle_size],
                     fill=(200, 220, 255, alpha))


def draw_global_grid(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a subtle global latitude/longitude grid in the sky."""
    grid_color = (100, 120, 180, 20)
    center_x = width // 2
    center_y = int(height * 0.3)

    # Latitude lines (curved)
    for lat in range(-60, 70, 30):
        points = []
        for x in range(0, width, 20):
            y_offset = int(math.sin((x - center_x) * 0.005) * (90 - abs(lat)) * 0.5)
            y = center_y + lat * 3 + y_offset
            if 0 <= y < height * 0.5:
                points.append((x, y))
        if len(points) > 1:
            draw.line(points, fill=(80, 100, 160, 30), width=1)

    # Longitude lines
    for lon in range(-90, 100, 30):
        x = center_x + int(math.sin(math.radians(lon * 2)) * 400)
        draw.line([(x, 0), (x, int(height * 0.45))], fill=(80, 100, 160, 20), width=1)


def draw_thermostat_gauge(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a subtle circular gauge/thermostat motif in the sky."""
    cx = width // 2
    cy = int(height * 0.28)
    outer_r = 180
    inner_r = 150

    # Outer ring
    draw.arc([cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r], 0, 360, fill=(100, 140, 200, 40), width=3)
    draw.arc([cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r], 0, 360, fill=(100, 140, 200, 30), width=2)

    # Tick marks
    for i in range(12):
        angle = math.radians(i * 30 - 120)
        r1 = inner_r + 5
        r2 = outer_r - 5
        x1 = cx + int(math.cos(angle) * r1)
        y1 = cy + int(math.sin(angle) * r1)
        x2 = cx + int(math.cos(angle) * r2)
        y2 = cy + int(math.sin(angle) * r2)
        draw.line([(x1, y1), (x2, y2)], fill=(120, 160, 220, 50), width=2)

    # Needle (pointing to red zone / danger)
    needle_angle = math.radians(65)
    nx = cx + int(math.cos(needle_angle) * (inner_r - 10))
    ny = cy + int(math.sin(needle_angle) * (inner_r - 10))
    draw.line([(cx, cy), (nx, ny)], fill=(220, 50, 50, 120), width=4)

    # Center dot
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(180, 50, 50, 150))


def draw_node_lights(draw: ImageDraw, width: int, height: int) -> None:
    """Draw small glowing points representing the seven Stratus nodes on the globe."""
    node_positions = [
        (width // 2 - 180, int(height * 0.32)),  # North America
        (width // 2 - 120, int(height * 0.40)),  # South America
        (width // 2 + 40, int(height * 0.33)),   # Europe
        (width // 2 - 60, int(height * 0.38)),   # Africa
        (width // 2 + 120, int(height * 0.35)),  # Asia
        (width // 2 + 160, int(height * 0.43)),  # Australia
        (width // 2 - 100, int(height * 0.22)),  # Arctic
    ]

    for nx, ny in node_positions:
        # Outer glow
        draw.ellipse([nx - 12, ny - 12, nx + 12, ny + 12], fill=(100, 200, 255, 30))
        draw.ellipse([nx - 6, ny - 6, nx + 6, ny + 6], fill=(150, 230, 255, 60))
        # Center
        draw.ellipse([nx - 3, ny - 3, nx + 3, ny + 3], fill=(200, 240, 255, 200))


def draw_lightning_strike(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a faint lightning bolt breaking through the clouds - danger symbol."""
    cx = width // 2 + 60
    start_y = int(height * 0.08)
    end_y = int(height * 0.18)

    points = [(cx, start_y), (cx - 20, start_y + 20), (cx + 10, start_y + 35),
              (cx - 15, start_y + 55), (cx + 5, end_y)]

    for i in range(len(points) - 1):
        draw.line([points[i], points[i+1]], fill=(220, 220, 150, 80), width=3)

    # Glow around the bolt
    for i in range(len(points) - 1):
        x1, y1 = points[i]
        x2, y2 = points[i+1]
        draw.line([(x1, y1), (x2, y2)], fill=(255, 255, 200, 30), width=8)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Stratosphere sky gradient
    draw_stratosphere_sky(draw, WIDTH, HEIGHT)

    # Step 2: Aerosol sheen
    draw_stratus_sheen(draw, WIDTH, HEIGHT)

    # Step 3: Global grid
    draw_global_grid(draw, WIDTH, HEIGHT)

    # Step 4: Thermostat gauge
    draw_thermostat_gauge(draw, WIDTH, HEIGHT)

    # Step 5: Lightning strike
    draw_lightning_strike(draw, WIDTH, HEIGHT)

    # Step 6: Node lights
    draw_node_lights(draw, WIDTH, HEIGHT)

    # Step 7: Mountain range
    draw_mountain_range(draw, WIDTH, HEIGHT)

    # Step 8: Stratus domes
    draw_stratus_domes(draw, WIDTH, HEIGHT)

    # Step 9: Injection tower
    draw_injection_tower(draw, WIDTH, HEIGHT)

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
