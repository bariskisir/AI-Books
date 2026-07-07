#!/usr/bin/env python3
"""Cover: The Frequency of Truth — Abandoned lighthouse in fog, red warning lights, radio tower against gray sky, fog gray/red signal/black."""

from __future__ import annotations

import argparse
import json
import math
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
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


def draw_fog_and_radio(draw):
    """Draw a foggy coastal scene with a radio tower and lighthouse."""
    rng = random.Random("frequency-of-truth-cover")

    # Gray sky gradient: dark gray at top, lighter fog gray at bottom
    for y in range(2000):
        t = y / 2000
        r = int(40 + 80 * t)
        g = int(40 + 80 * t)
        b = int(45 + 82 * t)
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b))))

    # Distant lighthouse with red warning light beam
    beam_center_x = 400
    beam_center_y = 500
    for angle_offset in range(-2, 3):
        angle = math.radians(-30 + angle_offset * 8)
        for length in range(50, 600, 10):
            alpha = max(0, 50 - length // 15)
            x = beam_center_x + math.cos(angle) * length
            y = beam_center_y + math.sin(angle) * length
            draw.point((x, y), fill=(255, 60, 40, alpha))

    # Radio tower (main focal point)
    tower_x = W // 2 + 100
    tower_base_y = 1100
    # Tower legs
    for leg_offset in [-12, 12]:
        draw.line((tower_x + leg_offset, tower_base_y, tower_x, 250),
                  fill=(120, 120, 130), width=3)
    # Cross-bracing
    for y_pos in range(300, 1100, 60):
        brace_width = max(5, int(12 * (1 - (y_pos - 250) / 850)))
        draw.line((tower_x - brace_width, y_pos, tower_x + brace_width, y_pos + 30),
                  fill=(100, 100, 110), width=2)
        draw.line((tower_x + brace_width, y_pos, tower_x - brace_width, y_pos + 30),
                  fill=(100, 100, 110), width=2)

    # Antenna array at top of tower
    draw.rectangle((tower_x - 25, 230, tower_x + 25, 260), fill=(80, 80, 90))
    for ant_offset in [-30, -15, 0, 15, 30]:
        draw.line((tower_x + ant_offset, 230, tower_x + ant_offset * 3, 150),
                  fill=(150, 150, 160), width=1)
        draw.line((tower_x + ant_offset, 230, tower_x + ant_offset * 3, 310),
                  fill=(150, 150, 160), width=1)

    # Lighthouse silhouette (left side)
    lx = 300
    draw.rectangle((lx - 25, 500, lx + 25, 1100), fill=(60, 55, 50))
    draw.polygon([(lx - 45, 500), (lx + 45, 500), (lx, 400)], fill=(55, 50, 45))
    # Light room — red warning
    draw.rectangle((lx - 30, 400, lx + 30, 450), fill=(255, 60, 40, 180))
    draw.ellipse((lx - 20, 420, lx + 20, 450), fill=(255, 100, 80, 220))
    # Red glow around lighthouse
    for r in range(100, 10, -10):
        alpha = max(0, 30 - (100 - r) // 3)
        draw.ellipse((lx - r, 400 - r, lx + r, 450 + r), fill=(255, 40, 20, alpha))

    # Radio waves emanating from tower (concentric arcs)
    for wave_radius in [100, 180, 280, 400, 540]:
        alpha = max(0, 80 - wave_radius // 10)
        draw.arc((tower_x - wave_radius, 1250 - wave_radius,
                  tower_x + wave_radius, 1250 + wave_radius),
                 -30, 30, fill=(100, 220, 255, alpha), width=2)

    # Fog layers (horizontal bands of white/gray)
    for fog_y in range(200, 1300, 40):
        fog_alpha = rng.randint(10, 40)
        fog_variation = rng.randint(0, 50)
        draw.line((0, fog_y + fog_variation, W, fog_y + fog_variation),
                  fill=(200, 200, 210, fog_alpha), width=rng.randint(5, 20))

    # Number sequences floating in the fog (decorative)
    numbers_text = "69142 77388 92110 73880"
    for i, char in enumerate(numbers_text):
        if char == " ":
            continue
        nx = 200 + i * 50 + rng.randint(-10, 10)
        ny = 1450 + rng.randint(-100, 100)
        n_alpha = rng.randint(30, 80)
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except Exception:
            font = ImageFont.load_default()
        draw.text((nx, ny), char, fill=(180, 220, 255, n_alpha), font=font)

    # Ground / rocky shore
    for y in range(1100, 1600, 2):
        t = (y - 1100) / 500
        r = int(40 + 50 * t)
        g = int(35 + 45 * t)
        b = int(30 + 40 * t)
        draw.line((0, y, W, y), fill=(r, g, b))

    # City lights in the distance
    for _ in range(60):
        lx_pos = rng.randint(50, W - 50)
        ly_pos = rng.randint(900, 1050)
        l_alpha = rng.randint(30, 120)
        draw.point((lx_pos, ly_pos), fill=(255, 200, 100, l_alpha))

    # Static/snow effect
    for _ in range(200):
        sx = rng.randint(0, W)
        sy = rng.randint(1400, 1700)
        s_alpha = rng.randint(5, 25)
        draw.point((sx, sy), fill=(150, 150, 200, s_alpha))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Frequency of Truth")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("frequency-of-truth-cover")

    img = Image.new("RGBA", (W, H), (10, 10, 25, 255))
    draw = ImageDraw.Draw(img, "RGBA")
    draw_fog_and_radio(draw)

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
