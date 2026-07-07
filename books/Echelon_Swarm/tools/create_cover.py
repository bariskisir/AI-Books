#!/usr/bin/env python3
"""Cover for Echelon Swarm — drone swarm silhouettes over Arctic tundra."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


def draw_arctic_swarm_scene(draw):
    """Draw Arctic tundra with drone swarm silhouettes against dark sky."""
    rng = random.Random("echelon-swarm-cover")

    # Night sky gradient: deep blue-black to dark purple
    for y in range(1800):
        t = y / 1800
        r = int(5 + 20 * t)
        g = int(5 + 15 * t)
        b = int(25 + 30 * (1 - t))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b)))

    # Aurora borealis effect
    for i in range(40):
        ax = rng.randint(0, W)
        ay = rng.randint(100, 700)
        aw = rng.randint(100, 400)
        ah = rng.randint(20, 80)
        green = int(60 + rng.randint(0, 100))
        alpha = rng.randint(20, 50)
        draw.ellipse((ax - aw // 2, ay - ah // 2, ax + aw // 2, ay + ah // 2),
                     fill=(0, green, 80, alpha))

    # Distant mountains (snow-covered peaks in darkness)
    mountain_color = (25, 30, 50)
    peaks = [(0, 1400), (200, 1200), (400, 1300), (600, 1100), (800, 1250),
             (1000, 1150), (1200, 1200), (1400, 1280), (W, 1350)]
    draw.polygon(peaks, fill=mountain_color)
    # Snow caps
    snow_color = (60, 65, 80, 100)
    draw.polygon([(560, 1120), (600, 1100), (640, 1120)], fill=snow_color)
    draw.polygon([(960, 1170), (1000, 1150), (1040, 1170)], fill=snow_color)

    # Arctic tundra ground
    for y in range(1400, 1800, 2):
        t = (y - 1400) / 400
        r = int(15 + 25 * t)
        g = int(15 + 20 * t)
        b = int(20 + 25 * t)
        draw.line((0, y, W, y), fill=(r, g, b))

    # Abandoned radar station silhouette
    station_x = W // 2 - 100
    # Main building
    draw.rectangle((station_x, 1300, station_x + 200, 1480), fill=(10, 10, 15))
    # Radar dish tower
    draw.rectangle((station_x + 80, 1150, station_x + 120, 1300), fill=(12, 12, 18))
    # Dish
    draw.ellipse((station_x + 30, 1100, station_x + 170, 1200), fill=(8, 8, 12))
    # Support legs
    draw.line((station_x + 40, 1200, station_x + 60, 1300), fill=(10, 10, 15), width=4)
    draw.line((station_x + 160, 1200, station_x + 140, 1300), fill=(10, 10, 15), width=4)

    # Drone swarm silhouettes in sky
    drone_positions = []
    for _ in range(60):
        dx = rng.randint(50, W - 50)
        dy = rng.randint(200, 900)
        drone_positions.append((dx, dy))

    # Draw drones as small angular shapes
    for dx, dy in drone_positions:
        size = rng.randint(6, 14)
        # Wing body
        draw.polygon([
            (dx - size, dy),
            (dx + size, dy),
            (dx + size // 3, dy + size // 2),
            (dx - size // 3, dy + size // 2),
        ], fill=(180, 50, 50, rng.randint(100, 200)))
        # Rotor glow
        rotor_color = (200, 60, 60, rng.randint(30, 80))
        draw.ellipse((dx - size - 2, dy - 3, dx - size + 4, dy + 3), fill=rotor_color)
        draw.ellipse((dx + size - 4, dy - 3, dx + size + 2, dy + 3), fill=rotor_color)

    # Connection lines between nearby drones (swarm network visualization)
    for i, (x1, y1) in enumerate(drone_positions):
        for x2, y2 in drone_positions[i + 1:i + 5]:
            dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            if dist < 150:
                draw.line((x1, y1, x2, y2), fill=(180, 50, 50, 30), width=1)

    # Data stream lines (vertical glowing lines suggesting signals)
    for _ in range(15):
        sx = rng.randint(100, W - 100)
        sy_start = rng.randint(200, 800)
        sy_end = sy_start + rng.randint(50, 150)
        for y in range(sy_start, sy_end, 2):
            t = (y - sy_start) / (sy_end - sy_start)
            alpha = int(80 * (1 - t))
            draw.line((sx, y, sx + rng.randint(-2, 2), y + 2),
                      fill=(100, 200, 255, max(0, alpha)), width=1)

    # Small glowing data nodes
    for _ in range(8):
        nx = rng.randint(100, W - 100)
        ny = rng.randint(400, 900)
        for r in range(6, 0, -1):
            alpha = int(40 / (6 - r + 1))
            draw.ellipse((nx - r, ny - r, nx + r, ny + r),
                         fill=(100, 200, 255, alpha))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "Echelon Swarm")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("echelon-swarm-cover")

    img = Image.new("RGBA", (W, H), (5, 5, 20, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_arctic_swarm_scene(draw)

    _draw_standard_cover_title_panel(
        img,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model,
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(output_path, "PNG", optimize=True)
    print(f"Cover saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
