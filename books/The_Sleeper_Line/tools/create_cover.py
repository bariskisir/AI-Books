#!/usr/bin/env python3
"""Cover: Phantom headlights through dark tunnel, black fungal veins on tiles, obelisk in phosphorescent cavern depths, tunnel black/fungal black/phosphor green."""

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
WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Dark underground gradient from black-green to pure black."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((30, 28, 22), (20, 18, 14), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((20, 18, 14), (10, 10, 8), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((10, 10, 8), (3, 3, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_tunnel_walls(draw: ImageDraw, width: int, height: int) -> None:
    """Draw subway tunnel walls converging in forced perspective."""
    vanish_x, vanish_y = width // 2, int(height * 0.25)
    rng = random.Random(11)

    for wall_side in [-1, 1]:
        points = []
        for y in range(int(height * 0.15), int(height * 0.85)):
            progress = (y - height * 0.15) / (height * 0.7)
            base_width = 800 * progress
            wobble = 15 * math.sin(y * 0.008 + wall_side * 2) + 10 * math.sin(y * 0.015)
            x = width // 2 + wall_side * (base_width + wobble)
            x = max(0, min(width, int(x)))
            points.append((x, y))

        # Draw wall as thick line
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=(25, 28, 30), width=6)

        # Add tunnel wall shading inside
        for offset in range(10, 80, 10):
            inner_pts = []
            for y in range(int(height * 0.15), int(height * 0.85)):
                progress = (y - height * 0.15) / (height * 0.7)
                base_width = 800 * progress
                x = width // 2 + wall_side * (base_width - offset * progress)
                x = max(0, min(width, int(x)))
                inner_pts.append((x, y))
            shade_color = (40 - offset, 42 - offset, 38 - offset)
            for i in range(len(inner_pts) - 1):
                draw.line([inner_pts[i], inner_pts[i + 1]], fill=shade_color, width=3)


def draw_tracks(draw: ImageDraw, width: int, height: int) -> None:
    """Draw train tracks converging to vanishing point."""
    vanish_x, vanish_y = width // 2, int(height * 0.25)
    rng = random.Random(7)

    for rail_side in [-1, 1]:
        pts = []
        for y in range(int(height * 0.35), int(height * 0.85)):
            progress = (y - height * 0.35) / (height * 0.50)
            spread = 300 * progress
            wobble = 5 * math.sin(y * 0.01 + rail_side)
            x = width // 2 + rail_side * (spread + wobble)
            x = max(0, min(width, int(x)))
            pts.append((x, y))

        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=(60, 62, 65), width=4)

    # Cross ties
    for y in range(int(height * 0.38), int(height * 0.82), 20):
        progress = (y - height * 0.35) / (height * 0.50)
        spread = 300 * progress
        x_l = width // 2 - spread
        x_r = width // 2 + spread
        draw.line([(x_l, y), (x_r, y)], fill=(40, 42, 45), width=2)


def draw_fungus_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw phosphorescent fungal glow from the deep."""
    cx, cy = width // 2, int(height * 0.65)
    rng = random.Random(13)

    # Central glow
    for r in range(350, 20, -15):
        alpha = max(3, 25 - r // 15)
        draw.ellipse(
            [cx - r, cy - r // 2, cx + r, cy + r // 2],
            fill=(80, 90, 60, alpha),
        )

    # Fungal tendrils reaching up
    for _ in range(25):
        tendril_x = cx + rng.randint(-200, 200)
        tendril_y = cy + rng.randint(-80, 80)
        tendril_len = rng.randint(60, 180)
        tendril_angle = -math.pi / 2 + rng.uniform(-0.3, 0.3)
        tendril_points = []
        for t in range(tendril_len):
            x = tendril_x + t * math.cos(tendril_angle) + rng.randint(-3, 3)
            y = tendril_y + t * math.sin(tendril_angle)
            tendril_points.append((x, y))

        alpha = rng.randint(15, 40)
        color = (60 + rng.randint(0, 30), 70 + rng.randint(0, 20), 50, alpha)
        for i in range(len(tendril_points) - 1):
            draw.line([tendril_points[i], tendril_points[i + 1]], fill=color, width=rng.randint(2, 6))


def draw_platform(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a subway platform edge at the bottom of the tunnel."""
    y_base = int(height * 0.78)
    rng = random.Random(19)

    # Platform edge
    draw.rectangle([(0, y_base), (width, height)], fill=(18, 20, 22))

    # Yellow safety line
    draw.line([(0, y_base), (width, y_base)], fill=(70, 65, 30), width=6)
    draw.line([(0, y_base + 3), (width, y_base + 3)], fill=(90, 85, 40), width=3)

    # Platform texture (tiles)
    for tx in range(0, width, 60):
        for ty in range(y_base + 10, height, 40):
            draw.rectangle([tx, ty, tx + 58, ty + 38], fill=(22, 24, 26), outline=(28, 30, 32), width=1)

    # Tile veining (fungus spreading)
    for _ in range(30):
        vx = rng.randint(0, width)
        vy = y_base + rng.randint(10, height - y_base - 10)
        for _ in range(rng.randint(4, 10)):
            vx += rng.randint(-5, 5)
            vy += rng.randint(1, 8)
            if vy > height or vx < 0 or vx > width:
                break
            draw.line([(vx, vy), (vx + rng.randint(-2, 2), vy + rng.randint(1, 4))],
                      fill=(35, 40, 30, rng.randint(60, 120)), width=2)


def draw_deep_light(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an eerie light rising from the tracks between the rails."""
    cx = width // 2
    y_start = int(height * 0.50)
    y_end = int(height * 0.75)

    for y in range(y_start, y_end, 3):
        progress = (y - y_start) / (y_end - y_start)
        glow_width = int(80 * (1 - progress * 0.7))
        alpha = int(20 * (1 - progress * 0.8))
        x = cx - glow_width // 2
        draw.line([(x, y), (x + glow_width, y)], fill=(60, 75, 50, alpha))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Tunnel gradient: pitch black toward vanishing point, faint fungal green at bottom
    for y in range(HEIGHT):
        t = y / HEIGHT
        if y < 800:
            c = (2, 2, 4)
        elif y < 1400:
            f = (y - 800) / 600
            c = tuple(int(a + (b - a) * f) for a, b in zip((2, 2, 4), (15, 18, 10)))
        else:
            f = (y - 1400) / 1160
            c = tuple(int(a + (b - a) * f) for a, b in zip((15, 18, 10), (5, 6, 4)))
        draw.line([(0, y), (WIDTH, y)], fill=c)

    # Tunnel walls converging
    vanish_x, vanish_y = WIDTH // 2, 500
    for side in (-1, 1):
        pts = []
        for y in range(400, 1800, 4):
            prog = (y - 400) / 1400
            spread = 750 * prog
            wobble = 20 * math.sin(y * 0.006 + side) + 12 * math.sin(y * 0.013 + side * 2)
            x = WIDTH // 2 + side * (spread + wobble)
            x = max(0, min(WIDTH, int(x)))
            pts.append((x, y))
        for i in range(len(pts) - 1):
            draw.line([pts[i], pts[i + 1]], fill=(20, 22, 25), width=8)

    # Black fungal veins on tiles (left wall)
    rng = random.Random(13)
    for _ in range(40):
        vx = rng.randint(50, 350)
        vy = rng.randint(500, 1700)
        for _ in range(rng.randint(6, 15)):
            vx += rng.randint(-4, 4)
            vy += rng.randint(4, 10)
            if vy > 1750 or vx < 10 or vx > 380:
                break
            draw.line([(vx, vy), (vx + rng.randint(-2, 2), vy + rng.randint(2, 5))],
                      fill=(5, 5, 5, rng.randint(120, 200)), width=3)

    # Fungal veins on right wall
    for _ in range(40):
        vx = WIDTH - rng.randint(50, 350)
        vy = rng.randint(500, 1700)
        for _ in range(rng.randint(6, 15)):
            vx += rng.randint(-4, 4)
            vy += rng.randint(4, 10)
            if vy > 1750 or vx < WIDTH - 380 or vx > WIDTH - 10:
                break
            draw.line([(vx, vy), (vx + rng.randint(-2, 2), vy + rng.randint(2, 5))],
                      fill=(5, 5, 5, rng.randint(120, 200)), width=3)

    # Phantom headlights in the distance
    hl_center_x = vanish_x
    hl_center_y = 350
    for r in range(180, 10, -8):
        alpha = max(5, 80 - r // 3)
        draw.ellipse(
            [hl_center_x - r, hl_center_y - r // 2, hl_center_x + r, hl_center_y + r // 2],
            fill=(200, 210, 220, alpha),
        )
    # Bright core
    draw.ellipse(
        [hl_center_x - 25, hl_center_y - 10, hl_center_x + 25, hl_center_y + 10],
        fill=(240, 245, 255, 180),
    )
    # Second headlight
    draw.ellipse(
        [hl_center_x - 150, hl_center_y - 8, hl_center_x - 100, hl_center_y + 8],
        fill=(220, 225, 240, 140),
    )

    # Light beams extending forward
    for y in range(hl_center_y + 20, 900, 4):
        prog = (y - hl_center_y - 20) / 580
        beam_width = int(60 + prog * 200)
        alpha = int(60 * (1 - prog * 0.7))
        if alpha < 2:
            break
        draw.line([(hl_center_x - beam_width // 2, y), (hl_center_x + beam_width // 2, y)],
                  fill=(180, 190, 200, alpha))

    # Obelisk silhouette in phosphorescent cavern depths
    ob_x = WIDTH // 2 + 200
    ob_base_y = 1400
    ob_h = 300
    ob_w = 40
    draw.polygon(
        [(ob_x, ob_base_y - ob_h), (ob_x - ob_w // 2, ob_base_y), (ob_x + ob_w // 2, ob_base_y)],
        fill=(8, 10, 8),
    )
    # Phosphorescent glow around obelisk
    for r in range(120, 10, -10):
        alpha = max(5, 40 - r // 4)
        draw.ellipse(
            [ob_x - r, ob_base_y - ob_h // 2 - r, ob_x + r, ob_base_y - ob_h // 2 + r],
            fill=(60, 80, 70, alpha),
        )
    # Second smaller obelisk
    ob2_x = WIDTH // 2 - 180
    ob2_h = 180
    draw.polygon(
        [(ob2_x, ob_base_y - ob2_h), (ob2_x - 20, ob_base_y), (ob2_x + 20, ob_base_y)],
        fill=(6, 8, 6),
    )

    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), metadata.get("model", ""))
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
