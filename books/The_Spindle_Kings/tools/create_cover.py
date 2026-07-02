#!/usr/bin/env python3
"""Cover: The Spindle Kings — laboratory interior with holographic SEM imagery of spiral molecular structures."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw

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

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

random.seed(20260702)


def make_gradient(draw):
    """Dark lab background: deep steel grey to blue-black."""
    for y in range(H):
        t = y / H
        r = int(12 + 6 * t)
        g = int(14 + 8 * t)
        b = int(28 + 18 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def draw_lab_floor(draw):
    """Draw stainless steel lab bench at the bottom of the artwork area."""
    bench_y = H * 0.58
    # Bench surface
    for y in range(int(bench_y), int(bench_y + 40)):
        t = (y - bench_y) / 40
        shine = int(80 + 120 * (1 - t) * (0.5 + 0.5 * math.sin(y * 0.05)))
        draw.line([(0, y), (W, y)], fill=(shine, shine, max(0, shine - 10)))
    # Lab bench edge reflection line
    draw.line([(0, int(bench_y)), (W, int(bench_y))], fill=(140, 145, 150), width=2)
    draw.line([(0, int(bench_y) + 1), (W, int(bench_y) + 1)], fill=(100, 105, 110), width=1)


def draw_stainless_surfaces(draw):
    """Draw reflective stainless steel panels on the sides."""
    # Left cabinet
    for y in range(100, int(H * 0.55)):
        t = y / H
        shade = int(40 + 30 * math.sin(y * 0.03) + 20 * math.cos(y * 0.07))
        r = int(shade * 0.9)
        g = shade
        b = shade
        draw.line([(30, y), (180, y)], fill=(r, g, b))
    # Right cabinet
    for y in range(100, int(H * 0.55)):
        t = y / H
        shade = int(35 + 25 * math.sin(y * 0.04 + 1) + 15 * math.cos(y * 0.06))
        r = int(shade * 0.9)
        g = shade
        b = shade
        draw.line([(W - 180, y), (W - 30, y)], fill=(r, g, b))
    # Vertical edge highlights
    draw.line([(30, 100), (30, int(H * 0.55))], fill=(100, 110, 115), width=1)
    draw.line([(180, 100), (180, int(H * 0.55))], fill=(60, 65, 70), width=1)
    draw.line([(W - 180, 100), (W - 180, int(H * 0.55))], fill=(60, 65, 70), width=1)
    draw.line([(W - 30, 100), (W - 30, int(H * 0.55))], fill=(100, 110, 115), width=1)


def draw_spiral_molecule(draw, cx, cy, radius, turns, color, alpha_start=180, alpha_end=60):
    """Draw a spiral molecular structure (SEM-style)."""
    points = []
    steps = int(turns * 60)
    for i in range(steps):
        t = i / steps
        angle = t * turns * 2 * math.pi
        r = radius * t
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        # Add slight jitter for organic look
        x += random.uniform(-0.5, 0.5)
        y += random.uniform(-0.5, 0.5)
        points.append((x, y))

    for i in range(1, len(points)):
        frac = i / len(points)
        alpha = int(alpha_start - (alpha_start - alpha_end) * frac)
        r = max(1, int(2 + frac * 3))
        try:
            draw.line(
                [points[i - 1], points[i]],
                fill=(color[0], color[1], color[2], alpha),
                width=r,
            )
        except (IndexError, TypeError):
            pass


def draw_molecular_cluster(draw):
    """Draw holographic SEM-style spiral molecular structures with cool blue-violet light."""
    # Central large spiral
    draw_spiral_molecule(draw, W * 0.5, H * 0.28, 10, 4.5, (80, 160, 255), 200, 80)
    draw_spiral_molecule(draw, W * 0.5, H * 0.28, 12, 5.0, (120, 100, 220), 160, 60)
    draw_spiral_molecule(draw, W * 0.5, H * 0.28, 8, 3.5, (60, 200, 255), 180, 70)

    # Upper-left cluster
    draw_spiral_molecule(draw, W * 0.28, H * 0.18, 6, 3.0, (100, 80, 200), 140, 40)
    draw_spiral_molecule(draw, W * 0.28, H * 0.18, 4, 2.5, (60, 180, 255), 120, 30)

    # Upper-right cluster
    draw_spiral_molecule(draw, W * 0.72, H * 0.20, 7, 3.5, (140, 100, 180), 150, 50)
    draw_spiral_molecule(draw, W * 0.72, H * 0.20, 5, 2.8, (80, 150, 255), 130, 40)

    # Lower-left cluster
    draw_spiral_molecule(draw, W * 0.22, H * 0.42, 5, 2.5, (90, 70, 210), 120, 30)
    draw_spiral_molecule(draw, W * 0.22, H * 0.42, 3, 2.0, (50, 170, 255), 100, 20)

    # Lower-right cluster
    draw_spiral_molecule(draw, W * 0.78, H * 0.40, 6, 3.0, (110, 90, 200), 130, 40)
    draw_spiral_molecule(draw, W * 0.78, H * 0.40, 4, 2.2, (70, 160, 255), 110, 25)


def draw_connecting_fibers(draw):
    """Draw carbon-nanotube fibers connecting the molecular clusters."""
    connections = [
        (W * 0.5, H * 0.28, W * 0.28, H * 0.18),
        (W * 0.5, H * 0.28, W * 0.72, H * 0.20),
        (W * 0.5, H * 0.28, W * 0.22, H * 0.42),
        (W * 0.5, H * 0.28, W * 0.78, H * 0.40),
        (W * 0.28, H * 0.18, W * 0.72, H * 0.20),
        (W * 0.22, H * 0.42, W * 0.78, H * 0.40),
    ]
    for x1, y1, x2, y2 in connections:
        segments = 40
        for i in range(segments):
            frac = i / segments
            x = x1 + (x2 - x1) * frac
            y = y1 + (y2 - y1) * frac
            # Slight sine wave deviation
            x += math.sin(frac * 8) * 8
            y += math.cos(frac * 10) * 6
            alpha = int(60 * (1 - abs(frac - 0.5) * 1.2))
            if alpha < 5:
                continue
            draw.point((int(x), int(y)), fill=(100, 180, 255, alpha))


def draw_specimen_stage(draw):
    """Draw a specimen stage/microscope column in the center."""
    stage_x = W * 0.5
    stage_y = H * 0.45
    # Column
    draw.rectangle(
        [stage_x - 30, stage_y, stage_x + 30, stage_y + 200],
        fill=(35, 40, 45),
        outline=(55, 60, 65),
        width=1,
    )
    # Stage platform
    draw.rectangle(
        [stage_x - 80, stage_y - 10, stage_x + 80, stage_y + 10],
        fill=(50, 55, 60),
        outline=(80, 85, 90),
        width=2,
    )
    # Sample glow on stage (blue-violet)
    for r in range(30, 0, -1):
        alpha = int(80 - r * 2.5)
        draw.ellipse(
            [stage_x - r, stage_y - r, stage_x + r, stage_y + r],
            fill=(80, 100, 220, alpha),
        )


def draw_red_warning_indicators(draw):
    """Draw red warning indicators and status panels."""
    # Top warning bar
    for y in range(8, 20):
        for x in range(0, W, 2):
            if random.random() < 0.1:
                r = int(255 * (0.6 + 0.4 * math.sin(x * 0.1 + y)))
                g = int(10 * (0.5 + 0.5 * math.sin(x * 0.05)))
                b = int(8 * (0.5 + 0.5 * math.sin(x * 0.05)))
                draw.point((x, y), fill=(r, g, b))

    # Warning panel upper-left
    panel_x, panel_y = 200, 60
    draw.rectangle(
        [panel_x, panel_y, panel_x + 160, panel_y + 50],
        fill=(60, 8, 8),
        outline=(200, 30, 30),
        width=2,
    )
    # Warning text simulation
    for wx in range(panel_x + 10, panel_x + 150, 6):
        for wy in range(panel_y + 15, panel_y + 40, 8):
            if random.random() < 0.7:
                draw.point((wx, wy), fill=(255, 60, 60))

    # Warning panel upper-right
    panel2_x, panel2_y = W - 360, 60
    draw.rectangle(
        [panel2_x, panel2_y, panel2_x + 160, panel2_y + 50],
        fill=(60, 8, 8),
        outline=(200, 30, 30),
        width=2,
    )
    for wx in range(panel2_x + 10, panel2_x + 150, 6):
        for wy in range(panel2_y + 15, panel2_y + 40, 8):
            if random.random() < 0.7:
                draw.point((wx, wy), fill=(255, 60, 60))

    # Small LED indicators
    led_positions = [
        (130, 55), (165, 55), (W - 130, 55), (W - 165, 55),
        (120, H * 0.55), (W - 120, H * 0.55),
    ]
    for lx, ly in led_positions:
        # Glow
        draw.ellipse(
            [lx - 6, ly - 6, lx + 6, ly + 6],
            fill=(255, 20, 20, 30),
        )
        draw.ellipse(
            [lx - 3, ly - 3, lx + 3, ly + 3],
            fill=(255, 0, 0),
        )

    # Blinking red alert text indicators on lab equipment
    for bx, by in [(300, 120), (W - 300, 120)]:
        for i in range(6):
            for j in range(3):
                if random.random() < 0.6:
                    draw.point(
                        (bx + i * 8, by + j * 10),
                        fill=(200, 20, 20),
                    )


def draw_glass_observation_window(draw):
    """Draw shadowy human figures behind a glass observation window."""
    window_x = W * 0.25
    window_y = H * 0.38
    window_w = W * 0.5
    window_h = 180

    # Glass panel
    draw.rectangle(
        [window_x, window_y, window_x + window_w, window_y + window_h],
        fill=(20, 25, 35, 120),
        outline=(60, 70, 90, 180),
        width=2,
    )

    # Glass reflection lines
    for i in range(3):
        rx = window_x + 20 + i * (window_w // 3)
        draw.line(
            [(rx, window_y + 5), (rx + 30, window_y + window_h - 5)],
            fill=(100, 120, 160, 30),
            width=1,
        )

    # Shadowy figures behind glass
    fig_data = [
        (window_x + window_w * 0.3, window_y + window_h * 0.6, 1.0),
        (window_x + window_w * 0.55, window_y + window_h * 0.55, 0.85),
        (window_x + window_w * 0.78, window_y + window_h * 0.62, 0.9),
    ]
    for fcx, fcy, scale in fig_data:
        head_r = int(10 * scale)
        body_w = int(16 * scale)
        body_h = int(45 * scale)
        # Head
        draw.ellipse(
            [fcx - head_r, fcy - body_h, fcx + head_r, fcy - body_h + head_r * 2],
            fill=(8, 10, 14, 180),
        )
        # Body
        draw.rectangle(
            [fcx - body_w, fcy - body_h + head_r * 2, fcx + body_w, fcy],
            fill=(8, 10, 14, 160),
        )

    # Glass border glow
    draw.rectangle(
        [window_x, window_y, window_x + window_w, window_y + window_h],
        outline=(60, 100, 180, 60),
        width=1,
    )


def draw_cool_violet_lighting(draw):
    """Add atmospheric cool blue-violet light effects across the scene."""
    # Central light cone from above — use gradient polygon with alpha
    for y in range(0, int(H * 0.5), 4):
        t = y / (H * 0.5)
        spread = int(300 * t)
        alpha = int(18 * (1 - t))
        if alpha < 1:
            continue
        for x_offset in range(-spread, spread, 3):
            x = W // 2 + x_offset
            if x < 0 or x >= W:
                continue
            dist_frac = abs(x_offset) / spread
            local_alpha = int(alpha * (1 - dist_frac))
            if local_alpha < 1:
                continue
            draw.point((x, y), fill=(60, 80, 160, local_alpha))


def draw_violet_ambient_glow(draw):
    """Draw violet ambient glow at the edges of the artwork."""
    for radius in range(600, 200, -30):
        alpha = int(20 - (600 - radius) / 20)
        if alpha < 2:
            continue
        draw.ellipse(
            [W // 2 - radius, H * 0.25 - radius, W // 2 + radius, H * 0.25 + radius],
            outline=(80, 60, 140, max(0, alpha)),
            width=3,
        )


def draw_holographic_grid(draw):
    """Draw a holographic projection grid overlay."""
    # Horizontal lines
    for y in range(80, int(H * 0.55), 40):
        for x in range(30, W - 30, 2):
            alpha = int(12 + 8 * math.sin(x * 0.02 + y * 0.01))
            draw.point((x, y), fill=(100, 150, 255, alpha))
    # Vertical lines
    for x in range(50, W - 50, 40):
        for y in range(80, int(H * 0.55), 2):
            alpha = int(10 + 6 * math.sin(y * 0.02 + x * 0.01))
            draw.point((x, y), fill=(100, 150, 255, alpha))


def draw_coolant_pipes(draw):
    """Draw metallic coolant pipes along the ceiling area."""
    pipe_y = 30
    draw.rectangle([(0, pipe_y), (W, pipe_y + 8)], fill=(40, 42, 45), outline=(60, 62, 65), width=1)
    draw.rectangle([(0, pipe_y + 8), (W, pipe_y + 12)], fill=(45, 48, 50), outline=(55, 58, 60), width=1)
    # Support brackets
    for bx in range(100, W - 50, 200):
        draw.rectangle([(bx, pipe_y - 6), (bx + 4, pipe_y)], fill=(50, 52, 55))


def make_cover(metadata: dict) -> Image.Image:
    """Create the full cover image for The Spindle Kings."""
    global img
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Build layers
    make_gradient(draw)
    draw_coolant_pipes(draw)
    draw_red_warning_indicators(draw)
    draw_stainless_surfaces(draw)
    draw_holographic_grid(draw)
    draw_cool_violet_lighting(draw)
    draw_violet_ambient_glow(draw)
    draw_molecular_cluster(draw)
    draw_connecting_fibers(draw)
    draw_specimen_stage(draw)
    draw_glass_observation_window(draw)
    draw_lab_floor(draw)

    return img


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    meta = {}
    if args.metadata:
        meta = json.loads(Path(args.metadata).read_text(encoding="utf-8"))

    model = meta.get("model", "")
    cover_path = ROOT / "books" / "The_Spindle_Kings" / "covers" / "The_Spindle_Kings.png"
    if args.out:
        cover_path = ROOT / Path(args.out) if not Path(args.out).is_absolute() else Path(args.out)

    img = make_cover(meta)

    cover_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(
        img,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model,
    )
    img.save(str(cover_path))
    print(f"Cover saved to: {cover_path}")


if __name__ == "__main__":
    main()