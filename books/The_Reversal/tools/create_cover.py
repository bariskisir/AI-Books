#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Reversal."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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


WIDTH = 1600
HEIGHT = 2560


def _gradient(draw, w, h, top_color, bottom_color):
    for y in range(h):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / h)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / h)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_chair(draw, cx, cy_base, scale, color, shadow_color, highlight_color):
    """Draw a simple therapy chair facing the viewer."""
    s = scale
    seat_w = int(280 * s)
    seat_h = int(50 * s)
    backrest_h = int(420 * s)
    backrest_w = int(260 * s)
    leg_h = int(120 * s)
    leg_w = int(18 * s)

    backrest_x0 = cx - backrest_w // 2
    backrest_y0 = cy_base - leg_h - seat_h - backrest_h
    backrest_x1 = backrest_x0 + backrest_w
    backrest_y1 = backrest_y0 + backrest_h

    # Backrest
    draw.rectangle(
        [backrest_x0, backrest_y0, backrest_x1, backrest_y1],
        fill=color,
        outline=highlight_color,
        width=2,
    )
    # Tufted buttons
    button_r = 4
    for r in range(3):
        for c in range(3):
            bx = backrest_x0 + int(backrest_w * (0.25 + r * 0.25))
            by = backrest_y0 + int(backrest_h * (0.2 + c * 0.3))
            draw.ellipse(
                [bx - button_r, by - button_r, bx + button_r, by + button_r],
                fill=shadow_color,
            )

    # Seat
    seat_x0 = cx - seat_w // 2
    seat_y0 = cy_base - leg_h - seat_h
    seat_x1 = seat_x0 + seat_w
    seat_y1 = seat_y0 + seat_h
    draw.rectangle(
        [seat_x0, seat_y0, seat_x1, seat_y1],
        fill=color,
        outline=highlight_color,
        width=2,
    )

    # Front legs
    draw.rectangle(
        [seat_x0 + 20, seat_y1, seat_x0 + 20 + leg_w, seat_y1 + leg_h],
        fill=shadow_color,
    )
    draw.rectangle(
        [seat_x1 - 20 - leg_w, seat_y1, seat_x1 - 20, seat_y1 + leg_h],
        fill=shadow_color,
    )

    # Shadow on floor
    shadow_ellipse_w = int(seat_w * 1.1)
    shadow_ellipse_h = int(40 * s)
    for r in range(6):
        alpha = 18 - r * 3
        if alpha < 0:
            alpha = 0
        draw.ellipse(
            [
                cx - shadow_ellipse_w // 2 - r * 4,
                cy_base - shadow_ellipse_h // 2 + r,
                cx + shadow_ellipse_w // 2 + r * 4,
                cy_base + shadow_ellipse_h // 2 + r,
            ],
            fill=(0, 0, 0, alpha),
        )


def _draw_figure_silhouette(draw, cx, cy_base, height, color, head_color):
    """Draw a tall, featureless human silhouette in shadow."""
    head_r = int(height * 0.09)
    torso_h = int(height * 0.45)
    torso_w = int(height * 0.28)
    arm_len = int(height * 0.32)
    leg_h = int(height * 0.42)
    leg_w = int(height * 0.10)

    # Head
    head_cy = cy_base - leg_h - torso_h - head_r
    draw.ellipse(
        [cx - head_r, head_cy - head_r, cx + head_r, head_cy + head_r],
        fill=head_color,
    )

    # Torso
    torso_y0 = head_cy + head_r
    torso_y1 = torso_y0 + torso_h
    torso_x0 = cx - torso_w // 2
    torso_x1 = cx + torso_w // 2
    draw.polygon(
        [
            (torso_x0, torso_y0),
            (torso_x1, torso_y0),
            (torso_x1 - 8, torso_y1),
            (torso_x0 + 8, torso_y1),
        ],
        fill=color,
    )

    # Arms hanging at sides
    arm_w = int(height * 0.045)
    draw.rectangle(
        [torso_x0 - arm_w, torso_y0 + 10, torso_x0, torso_y0 + 10 + arm_len],
        fill=color,
    )
    draw.rectangle(
        [torso_x1, torso_y0 + 10, torso_x1 + arm_w, torso_y0 + 10 + arm_len],
        fill=color,
    )

    # Legs
    leg_y0 = torso_y1
    leg_y1 = leg_y0 + leg_h
    draw.rectangle(
        [cx - leg_w, leg_y0, cx, leg_y1],
        fill=color,
    )
    draw.rectangle(
        [cx, leg_y0, cx + leg_w, leg_y1],
        fill=color,
    )


def _draw_window(draw, x, y, w, h, frame_color, glow_color):
    """Draw a tall window with a faint glow."""
    # Frame
    draw.rectangle([x, y, x + w, y + h], outline=frame_color, width=6)
    # Mullion
    draw.line([(x + w // 2, y), (x + w // 2, y + h)], fill=frame_color, width=4)
    draw.line([(x, y + h // 2), (x + w, y + h // 2)], fill=frame_color, width=4)
    # Glow (soft radial)
    for r in range(int(min(w, h) * 0.45), 0, -8):
        alpha = max(0, int(10 * (1 - r / (min(w, h) * 0.45))))
        cx = x + w // 2
        cy = y + h // 2
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(glow_color[0], glow_color[1], glow_color[2], alpha),
        )


def _draw_floor(draw, y_floor, w, h, color):
    """Draw a simple floor plane below y_floor."""
    draw.rectangle([0, y_floor, w, h], fill=color)


def _draw_wall(draw, w, h_floor, color_top, color_bottom):
    """Draw the back wall with a soft vertical gradient."""
    for y in range(h_floor):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / h_floor)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / h_floor)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / h_floor)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def create_cover(metadata_path: str, output_path: str) -> None:
    """Create the cover image."""
    meta = {}
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = meta.get("title", "The Reversal")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT), (8, 12, 22))
    draw = ImageDraw.Draw(img)

    # Back wall (vertical gradient: deep teal to near-black)
    _draw_wall(draw, WIDTH, int(HEIGHT * 0.78), (12, 24, 38), (4, 8, 18))

    # Floor (slightly lighter, cool gray)
    floor_y = int(HEIGHT * 0.78)
    _draw_floor(draw, floor_y, WIDTH, HEIGHT, (22, 28, 38))

    # Subtle floor line
    draw.line([(0, floor_y), (WIDTH, floor_y)], fill=(60, 70, 88, 255), width=2)

    # Tall window on the left (faint amber light)
    win_x, win_y, win_w, win_h = 180, 320, 360, 980
    _draw_window(
        draw,
        win_x,
        win_y,
        win_w,
        win_h,
        frame_color=(45, 50, 62),
        glow_color=(220, 170, 110),
    )

    # Window light spilling onto floor
    for r in range(220, 0, -10):
        alpha = max(0, int(6 * (1 - r / 220)))
        cx = win_x + win_w // 2
        cy = floor_y
        draw.polygon(
            [
                (cx - 80, cy),
                (cx + 80, cy),
                (cx + 80 + r * 3, floor_y + r),
                (cx - 80 - r * 3, floor_y + r),
            ],
            fill=(220, 170, 110, alpha),
        )

    # Therapy chair in the center
    chair_color = (50, 60, 80)
    chair_shadow = (20, 24, 36)
    chair_highlight = (110, 130, 160)
    _draw_chair(
        draw,
        WIDTH // 2 + 80,
        floor_y - 30,
        scale=1.5,
        color=chair_color,
        shadow_color=chair_shadow,
        highlight_color=chair_highlight,
    )

    # Second chair, smaller and dimmer, on the right (the doctor's chair, reversed)
    _draw_chair(
        draw,
        WIDTH // 2 - 360,
        floor_y - 20,
        scale=1.1,
        color=(35, 42, 58),
        shadow_color=(15, 18, 28),
        highlight_color=(70, 85, 110),
    )

    # A small standing figure between the chairs (the patient, faceless, in shadow)
    _draw_figure_silhouette(
        draw,
        WIDTH // 2 - 80,
        floor_y - 30,
        height=520,
        color=(28, 32, 44),
        head_color=(40, 46, 60),
    )

    # Mirror on the back wall, slightly to the right
    mirror_x, mirror_y = WIDTH - 460, 480
    mirror_w, mirror_h = 280, 480
    # Mirror frame
    draw.rectangle(
        [mirror_x - 8, mirror_y - 8, mirror_x + mirror_w + 8, mirror_y + mirror_h + 8],
        fill=(28, 32, 40),
    )
    # Mirror surface (subtle gradient, slightly cooler than the wall)
    for y in range(mirror_h):
        ry = mirror_y + y
        for x in range(mirror_w):
            rx = mirror_x + x
            r = 30 + int(10 * (x / mirror_w))
            g = 38 + int(10 * (y / mirror_h))
            b = 50 + int(12 * (y / mirror_h))
            draw.point((rx, ry), fill=(r, g, b))
    # Faint reflection of a figure inside the mirror
    reflect_cx = mirror_x + mirror_w // 2 - 6
    reflect_cy = mirror_y + mirror_h // 2 + 20
    # reflection silhouette (slightly offset)
    draw.ellipse(
        [reflect_cx - 22, reflect_cy - 90, reflect_cx + 22, reflect_cy - 50],
        fill=(45, 52, 68),
    )
    draw.polygon(
        [
            (reflect_cx - 38, reflect_cy - 45),
            (reflect_cx + 38, reflect_cy - 45),
            (reflect_cx + 30, reflect_cy + 95),
            (reflect_cx - 30, reflect_cy + 95),
        ],
        fill=(40, 46, 60),
    )
    # Mirror inner frame
    draw.rectangle(
        [mirror_x, mirror_y, mirror_x + mirror_w, mirror_y + mirror_h],
        outline=(60, 70, 88),
        width=2,
    )

    # Small overhead pendant lamp (warm light pool)
    lamp_cx = WIDTH // 2 + 60
    lamp_y = 200
    # Cord
    draw.line([(lamp_cx, 0), (lamp_cx, lamp_y)], fill=(80, 70, 60), width=3)
    # Shade
    draw.polygon(
        [
            (lamp_cx - 80, lamp_y),
            (lamp_cx + 80, lamp_y),
            (lamp_cx + 50, lamp_y + 90),
            (lamp_cx - 50, lamp_y + 90),
        ],
        fill=(45, 38, 30),
    )
    # Glow
    for r in range(360, 0, -12):
        alpha = max(0, int(8 * (1 - r / 360)))
        draw.ellipse(
            [lamp_cx - r, lamp_y + 80, lamp_cx + r, lamp_y + 80 + r * 2],
            fill=(220, 170, 100, alpha),
        )

    # Faint dust motes / specks
    rng = random.Random(7)
    for _ in range(80):
        x = rng.randint(100, WIDTH - 100)
        y = rng.randint(200, int(HEIGHT * 0.78))
        size = rng.choice([1, 1, 1, 2])
        alpha = rng.randint(20, 80)
        draw.ellipse(
            [x, y, x + size, y + size],
            fill=(200, 190, 170, alpha),
        )

    # Standard title panel
    _draw_standard_cover_title_panel(img, title, author, model)

    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


# ---- Standard helper functions (required by AGENTS.md) ----



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
