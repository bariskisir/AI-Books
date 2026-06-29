#!/usr/bin/env python3
"""
Cover art for The Dark Mirror.

Scene: A therapist's minimalist office at dusk. Two empty chairs face each
other across a low table. Between them, a large oval mirror leans against the
wall at a slight angle — its reflection shows not the room but a darker,
distorted version of it, as if a second, subtly wrong world exists just inside
the glass. The chairs cast long shadows toward each other. A narrow window
on the left shows city lights beginning to appear in the blue evening.
Cold blue-grey palette with a single warm lamp glow originating from below
the mirror. The mood is quiet, precise, and slightly wrong.
"""

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


WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765


# ---------------------------------------------------------------------------
# Background room
# ---------------------------------------------------------------------------

def draw_room(draw: ImageDraw.ImageDraw) -> None:
    """Dusk-lit office interior — walls, floor, window."""
    # Back wall — deep blue-grey
    for y in range(0, 900):
        t = y / 900
        r = int(28 + (42 - 28) * t)
        g = int(32 + (48 - 32) * t)
        b = int(44 + (62 - 44) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Side walls (perspective)
    # Left wall
    left_wall_pts = [(0, 0), (0, ART_HEIGHT), (300, ART_HEIGHT - 200), (300, 180)]
    draw.polygon(left_wall_pts, fill=(22, 28, 38))
    # Right wall
    right_wall_pts = [(WIDTH, 0), (WIDTH, ART_HEIGHT), (WIDTH - 300, ART_HEIGHT - 200), (WIDTH - 300, 180)]
    draw.polygon(right_wall_pts, fill=(18, 24, 34))

    # Floor — dark hardwood perspective
    for y in range(820, ART_HEIGHT):
        t = (y - 820) / (ART_HEIGHT - 820)
        r = int(38 + (24 - 38) * t)
        g = int(30 + (18 - 30) * t)
        b = int(22 + (14 - 22) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Floorboard lines (perspective converging)
    vanish_x = WIDTH // 2
    vanish_y = 780
    for board in range(8):
        angle_offset = (board - 4) * 95
        end_x = vanish_x + angle_offset
        draw.line([(end_x, vanish_y), (end_x + angle_offset * 3, ART_HEIGHT)],
                  fill=(30, 22, 16), width=2)


def draw_window(draw: ImageDraw.ImageDraw) -> None:
    """Narrow tall window on left — city lights at dusk."""
    wx, wy = 48, 80
    ww, wh = 180, 560
    # City sky gradient in window
    for y in range(wy, wy + wh):
        t = (y - wy) / wh
        r = int(18 + (30 - 18) * t)
        g = int(22 + (18 - 22) * t)
        b = int(55 + (28 - 55) * t)
        draw.line([(wx, y), (wx + ww, y)], fill=(r, g, b))

    # City lights — small scattered dots
    light_positions = [
        (95, 220), (140, 260), (72, 310), (188, 295), (115, 380),
        (160, 420), (88, 480), (195, 500), (130, 545), (70, 580),
        (175, 610), (108, 630), (152, 570),
    ]
    for lx, ly in light_positions:
        r_size = 3
        draw.ellipse([(lx - r_size, ly - r_size), (lx + r_size, ly + r_size)],
                     fill=(240, 220, 160))
        # Glow
        draw.ellipse([(lx - r_size - 3, ly - r_size - 3),
                      (lx + r_size + 3, ly + r_size + 3)],
                     fill=(240, 220, 160, 60) if hasattr(draw, 'alpha') else (180, 165, 110))

    # Window frame
    frame_color = (55, 50, 45)
    draw.rectangle([(wx - 8, wy - 8), (wx + ww + 8, wy + wh + 8)],
                   outline=frame_color, width=8)
    # Mullions
    draw.line([(wx + ww // 2, wy), (wx + ww // 2, wy + wh)], fill=frame_color, width=5)
    draw.line([(wx, wy + wh // 2), (wx + ww, wy + wh // 2)], fill=frame_color, width=5)

    # Warm glow from window onto left wall
    for step in range(12):
        alpha_val = max(0, 18 - step * 1.5)
        gy = wy + wh // 2
        gx = wx + ww + step * 18
        draw.ellipse([(gx - 30, gy - 80 - step * 10),
                      (gx + 30 + step * 20, gy + 80 + step * 10)],
                     fill=(60, 70, 120))


# ---------------------------------------------------------------------------
# The mirror
# ---------------------------------------------------------------------------

def draw_mirror(draw: ImageDraw.ImageDraw, image: Image.Image) -> None:
    """Oval mirror leaning against back wall — reflection shows a darker version of the room."""
    mx, my = WIDTH // 2, 240
    mw, mh = 380, 560

    # Reflection interior — darker, slightly off-color version of the background
    for y in range(my, my + mh):
        t = (y - my) / mh
        r = int(15 + (25 - 15) * t)
        g = int(10 + (18 - 10) * t)
        b = int(20 + (30 - 20) * t)
        # Clip to ellipse
        half_w = int(mw / 2 * math.sqrt(max(0, 1 - ((y - (my + mh / 2)) / (mh / 2)) ** 2)))
        if half_w > 0:
            draw.line([(mx - half_w, y), (mx + half_w, y)], fill=(r, g, b))

    # Dark distorted chair silhouettes in reflection
    # Ghost chair left
    gc_pts = [
        (mx - 130, my + 380), (mx - 90, my + 380), (mx - 90, my + 220),
        (mx - 130, my + 220)
    ]
    draw.polygon(gc_pts, fill=(8, 6, 12))
    # Ghost chair right
    gc_pts2 = [
        (mx + 90, my + 380), (mx + 130, my + 380), (mx + 130, my + 220),
        (mx + 90, my + 220)
    ]
    draw.polygon(gc_pts2, fill=(8, 6, 12))

    # Subtle warm glow from below mirror (the lamp source)
    for step in range(20):
        glow_alpha = max(0, 35 - step * 1.7)
        glow_y = my + mh + step * 14
        glow_w = mw // 2 + step * 8
        draw.ellipse([(mx - glow_w, glow_y - 15),
                      (mx + glow_w, glow_y + 15)],
                     fill=(80, 60, 20))

    # Mirror frame — thin elegant oval
    frame_pts = []
    for angle in range(361):
        theta = math.radians(angle)
        fx = mx + (mw // 2 + 12) * math.cos(theta)
        fy = (my + mh // 2) + (mh // 2 + 12) * math.sin(theta)
        frame_pts.append((fx, fy))
    draw.polygon(frame_pts, outline=(140, 120, 80), width=0)
    # Draw oval frame as thick line
    for thick in range(10):
        pts = []
        for angle in range(361):
            theta = math.radians(angle)
            fx = mx + (mw // 2 + 8 + thick) * math.cos(theta)
            fy = (my + mh // 2) + (mh // 2 + 8 + thick) * math.sin(theta)
            pts.append((fx, fy))
        if len(pts) >= 2:
            draw.line(pts + [pts[0]], fill=(130 - thick * 4, 112 - thick * 3, 75 - thick * 2), width=2)

    # Mirror sheen — thin highlight arc
    for i in range(5):
        sx = mx - mw // 2 + 30 + i * 5
        sy_top = my + 40 + i * 12
        sy_bot = my + 180 + i * 15
        draw.line([(sx, sy_top), (sx + 15, sy_bot)], fill=(180, 175, 190), width=1)


# ---------------------------------------------------------------------------
# Therapy chairs
# ---------------------------------------------------------------------------

def draw_chair(draw: ImageDraw.ImageDraw, cx: int, base_y: int, facing_right: bool) -> None:
    """Draw a simple modern therapy chair (armless, upholstered)."""
    chair_w = 190
    chair_h = 200
    seat_h = 55
    back_h = 175

    seat_color = (55, 52, 60)
    back_color = (48, 45, 54)
    leg_color = (35, 30, 28)

    # Seat
    draw.rectangle([(cx - chair_w // 2, base_y - seat_h),
                    (cx + chair_w // 2, base_y)],
                   fill=seat_color)
    # Back
    draw.rectangle([(cx - chair_w // 2, base_y - seat_h - back_h),
                    (cx + chair_w // 2, base_y - seat_h)],
                   fill=back_color)
    # Top of back — rounded suggestion
    draw.ellipse([(cx - chair_w // 2, base_y - seat_h - back_h - 20),
                  (cx + chair_w // 2, base_y - seat_h - back_h + 20)],
                 fill=back_color)

    # Legs (4)
    leg_y = base_y
    leg_length = 70
    leg_positions = [cx - chair_w // 2 + 18, cx + chair_w // 2 - 18]
    for lx in leg_positions:
        draw.rectangle([(lx - 6, leg_y), (lx + 6, leg_y + leg_length)],
                       fill=leg_color)

    # Shadow beneath chair
    shadow_pts = [
        (cx - chair_w // 2 + 10, base_y + leg_length),
        (cx + chair_w // 2 - 10, base_y + leg_length),
        (cx + chair_w // 2 + 30, base_y + leg_length + 30),
        (cx - chair_w // 2 - 30, base_y + leg_length + 30),
    ]
    draw.polygon(shadow_pts, fill=(15, 12, 10))

    # Cast shadow on floor (long at dusk)
    shadow_length = 220
    direction = 1 if facing_right else -1
    shadow_floor_pts = [
        (cx - chair_w // 2, base_y + leg_length),
        (cx + chair_w // 2, base_y + leg_length),
        (cx + chair_w // 2 + direction * shadow_length, base_y + leg_length + 180),
        (cx - chair_w // 2 + direction * shadow_length, base_y + leg_length + 180),
    ]
    draw.polygon(shadow_floor_pts, fill=(20, 15, 12))


def draw_low_table(draw: ImageDraw.ImageDraw) -> None:
    """Small low table between the chairs."""
    tx, ty = WIDTH // 2, 960
    tw, th = 160, 28
    leg_h = 55

    # Surface
    draw.rectangle([(tx - tw // 2, ty), (tx + tw // 2, ty + th)],
                   fill=(60, 50, 42))
    draw.line([(tx - tw // 2, ty), (tx + tw // 2, ty)], fill=(80, 68, 55), width=3)

    # Legs
    for lx in [tx - tw // 2 + 12, tx + tw // 2 - 12]:
        draw.rectangle([(lx - 5, ty + th), (lx + 5, ty + th + leg_h)],
                       fill=(45, 38, 30))

    # A single tissue box on the table (therapist's office motif)
    bx, by = tx - 22, ty - 36
    draw.rectangle([(bx, by), (bx + 44, by + 36)], fill=(62, 75, 80))
    draw.rectangle([(bx + 12, by - 8), (bx + 32, by + 2)], fill=(220, 215, 210))


# ---------------------------------------------------------------------------
# Atmospheric effects
# ---------------------------------------------------------------------------

def apply_dusk_atmosphere(image: Image.Image) -> Image.Image:
    """Subtle blue-cold overlay on the art zone."""
    overlay = Image.new("RGBA", (WIDTH, ART_HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Cool blue cast from top
    for step in range(25):
        alpha = int(12 - step * 0.4)
        if alpha <= 0:
            break
        od.rectangle([(0, step * 20), (WIDTH, step * 20 + 20)],
                     fill=(30, 35, 65, alpha))
    art_zone = image.crop((0, 0, WIDTH, ART_HEIGHT)).convert("RGBA")
    art_zone = Image.alpha_composite(art_zone, overlay)
    result = image.copy()
    result.paste(art_zone.convert("RGB"), (0, 0))
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Dark Mirror")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (28, 32, 44))
    draw = ImageDraw.Draw(image)

    draw_room(draw)
    draw_window(draw)

    # Chairs: left faces right, right faces left (toward each other)
    draw_chair(draw, 420, 1050, facing_right=True)
    draw_chair(draw, 1180, 1050, facing_right=False)

    draw_low_table(draw)
    draw_mirror(draw, image)

    image = apply_dusk_atmosphere(image)

    # Soft blur on distant wall for depth
    bg = image.crop((300, 0, WIDTH - 300, 400))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=1.5))
    image.paste(bg, (300, 0))

    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)

if __name__ == "__main__":
    main()
