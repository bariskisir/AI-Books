#!/usr/bin/env python3
"""Cover: The Reversal — psychiatrist's office chair from patient's side, slightly askew, gray light through venetian blinds."""

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

    # Wall gradient: gray-green to dark
    _draw_wall(draw, WIDTH, int(HEIGHT * 0.78), (18, 30, 42), (6, 10, 20))

    # Floor
    floor_y = int(HEIGHT * 0.78)
    _draw_floor(draw, floor_y, WIDTH, HEIGHT, (20, 26, 36))
    draw.line([(0, floor_y), (WIDTH, floor_y)], fill=(55, 65, 82, 255), width=2)

    # Venetian blinds on window (left)
    win_x, win_y, win_w, win_h = 120, 280, 400, 1000
    # Window frame
    draw.rectangle([win_x - 8, win_y - 8, win_x + win_w + 8, win_y + win_h + 8], fill=(35, 38, 48))
    # Window opening - gray light
    draw.rectangle([win_x, win_y, win_x + win_w, win_y + win_h], fill=(120, 130, 145, 180))
    # Venetian blind slats
    for sy in range(win_y + 20, win_y + win_h - 20, 30):
        draw.line([(win_x + 4, sy), (win_x + win_w - 4, sy)], fill=(60, 65, 75), width=4)
    # Blind cords
    draw.line([(win_x + win_w // 3, win_y), (win_x + win_w // 3, win_y + win_h)], fill=(40, 42, 48), width=2)
    draw.line([(win_x + win_w * 2 // 3, win_y), (win_x + win_w * 2 // 3, win_y + win_h)], fill=(40, 42, 48), width=2)
    # Gray light through blinds
    for r in range(180, 0, -10):
        alpha = max(0, int(8 * (1 - r / 180)))
        cx = win_x + win_w // 2
        draw.ellipse(
            [cx - r, floor_y - r // 2, cx + r, floor_y + r],
            fill=(150, 160, 175, alpha),
        )

    # Therapy chair in center (patient's side view, slightly askew)
    chair_color = (55, 65, 85)
    chair_shadow = (22, 26, 38)
    chair_highlight = (115, 135, 165)
    _draw_chair(
        draw,
        WIDTH // 2,
        floor_y - 30,
        scale=1.5,
        color=chair_color,
        shadow_color=chair_shadow,
        highlight_color=chair_highlight,
    )
    # Rotate chair slightly (askew) by adjusting shadow
    shadow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.ellipse([WIDTH // 2 - 150, floor_y + 60, WIDTH // 2 + 80, floor_y + 95], fill=(0, 0, 0, 50))
    shadow = shadow.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Second chair (doctor's chair, dimmer, right side)
    _draw_chair(
        draw,
        WIDTH // 2 + 380,
        floor_y - 20,
        scale=1.0,
        color=(32, 38, 52),
        shadow_color=(14, 16, 26),
        highlight_color=(65, 78, 100),
    )

    # Small figure silhouette (patient, faceless) in front of chair, slightly offset
    _draw_figure_silhouette(
        draw,
        WIDTH // 2 - 140,
        floor_y - 30,
        height=500,
        color=(26, 30, 42),
        head_color=(38, 44, 58),
    )

    # Overhead pendant light
    lamp_cx = WIDTH // 2
    lamp_y = 160
    draw.line([(lamp_cx, 0), (lamp_cx, lamp_y)], fill=(72, 62, 52), width=3)
    draw.polygon(
        [(lamp_cx - 70, lamp_y), (lamp_cx + 70, lamp_y), (lamp_cx + 45, lamp_y + 80), (lamp_cx - 45, lamp_y + 80)],
        fill=(40, 34, 28),
    )
    for r in range(320, 0, -12):
        alpha = max(0, int(6 * (1 - r / 320)))
        draw.ellipse([lamp_cx - r, lamp_y + 70, lamp_cx + r, lamp_y + 70 + r * 2], fill=(220, 170, 100, alpha))

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
