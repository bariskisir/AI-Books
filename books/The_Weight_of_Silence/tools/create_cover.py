#!/usr/bin/env python3
"""
Cover art for The Weight of Silence.

Scene: A forensic evaluation room. Sparse table with two chairs — one
empty (from our perspective, the psychologist's), the other occupied by
a boy who sits perfectly still, hands in his lap, looking slightly past the
viewer. On the table between them: a single sheet of paper with a stick
figure drawing — a figure with no mouth. Institutional white walls, a
strip of afternoon light across the floor from a frosted window. The
boy is small in the frame, centered, very composed. Clinical white with
warm yellow light band, grey shadows, a single point of warm gold where
the light hits the table. The mood is quiet, taut, loaded with meaning
that has not yet been spoken.
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
# Room
# ---------------------------------------------------------------------------

def draw_room(draw: ImageDraw.ImageDraw) -> None:
    """Institutional evaluation room — white walls, grey floor, warm light band."""
    # Back wall — very pale institutional white
    for y in range(0, 1050):
        t = y / 1050
        r = int(235 + (215 - 235) * t)
        g = int(232 + (215 - 232) * t)
        b = int(228 + (210 - 228) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Floor — cool institutional grey linoleum
    for y in range(1050, ART_HEIGHT):
        t = (y - 1050) / (ART_HEIGHT - 1050)
        r = int(175 + (145 - 175) * t)
        g = int(172 + (142 - 172) * t)
        b = int(168 + (138 - 168) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Floor line
    draw.line([(0, 1050), (WIDTH, 1050)], fill=(155, 152, 148), width=2)

    # Floor tile grid — faint
    for tx in range(0, WIDTH, 80):
        draw.line([(tx, 1050), (tx, ART_HEIGHT)], fill=(162, 158, 154), width=1)
    for ty in range(1050, ART_HEIGHT, 80):
        draw.line([(0, ty), (WIDTH, ty)], fill=(162, 158, 154), width=1)


def draw_frosted_window(draw: ImageDraw.ImageDraw) -> None:
    """Frosted window high on right wall — source of the light band."""
    wx, wy = 1200, 60
    ww, wh = 320, 520

    # Outside light — diffused through frosted glass
    for y in range(wy, wy + wh):
        t = (y - wy) / wh
        r = int(248 + (220 - 248) * t)
        g = int(240 + (215 - 240) * t)
        b = int(210 + (185 - 210) * t)
        draw.line([(wx, y), (wx + ww, y)], fill=(r, g, b))

    # Frosted texture — very subtle horizontal streaks
    for rw in range(14):
        ry = wy + 20 + rw * 36
        if ry < wy + wh:
            draw.line([(wx + 15, ry), (wx + ww - 15, ry)],
                      fill=(255, 252, 248), width=2)

    # Window frame — institutional metal
    frame_color = (140, 135, 130)
    draw.rectangle([(wx - 6, wy - 6), (wx + ww + 6, wy + wh + 6)],
                   fill=None, outline=frame_color, width=6)
    # Mullions
    draw.line([(wx, wy + wh // 3), (wx + ww, wy + wh // 3)], fill=frame_color, width=4)
    draw.line([(wx, wy + 2 * wh // 3), (wx + ww, wy + 2 * wh // 3)], fill=frame_color, width=4)

    # Light band on floor
    light_floor_y1 = 1050
    light_floor_y2 = ART_HEIGHT
    for step in range(30):
        alpha_val = max(0, 25 - step * 0.8)
        ly = light_floor_y1 + step * 14
        draw.line([(400, ly), (WIDTH - 40, ly)],
                  fill=(255, 248, 225))


def draw_table(draw: ImageDraw.ImageDraw) -> None:
    """Sparse institutional table — pale formica, metal legs."""
    tx, ty = WIDTH // 2, 1120
    tw, th = 700, 38
    leg_h = 380
    table_color = (210, 205, 198)
    edge_color = (185, 180, 174)

    # Legs (metal, institutional)
    for lx in [tx - tw // 2 + 30, tx + tw // 2 - 30]:
        draw.rectangle([(lx - 7, ty + th), (lx + 7, ty + th + leg_h)],
                       fill=(145, 140, 135))
        # Feet
        draw.rectangle([(lx - 18, ty + th + leg_h - 10),
                        (lx + 18, ty + th + leg_h)],
                       fill=(125, 120, 115))

    # Tabletop surface
    draw.rectangle([(tx - tw // 2, ty), (tx + tw // 2, ty + th)], fill=table_color)
    # Table edge
    draw.line([(tx - tw // 2, ty), (tx + tw // 2, ty)], fill=edge_color, width=3)
    draw.line([(tx - tw // 2, ty + th), (tx + tw // 2, ty + th)], fill=edge_color, width=2)

    # Warm light reflection on table
    draw.rectangle([(tx - tw // 2 + 30, ty + 8), (tx + tw // 2 - 30, ty + 28)],
                   fill=(255, 250, 232))


def draw_light_band_on_table(draw: ImageDraw.ImageDraw) -> None:
    """The afternoon light band hitting the edge of the table."""
    for step in range(25):
        alpha_val = max(0, 30 - step * 1.2)
        ly = 1100 + step * 5
        draw.line([(420, ly), (WIDTH, ly)], fill=(255, 245, 210))


def draw_chair(draw: ImageDraw.ImageDraw, cx: int, cy: int, empty: bool = True) -> None:
    """Institutional chair — metal tubing, pale upholstery."""
    ch_w, ch_h = 120, 180
    seat_y = cy - ch_h // 2
    seat_color = (180, 175, 168)
    frame_color = (140, 135, 130)

    # Back
    draw.rectangle([(cx - ch_w // 2, seat_y),
                    (cx + ch_w // 2, seat_y + ch_h)],
                   fill=seat_color)
    draw.rectangle([(cx - ch_w // 2 - 4, seat_y - 4),
                    (cx + ch_w // 2 + 4, seat_y + ch_h + 4)],
                   fill=None, outline=frame_color, width=4)

    # Seat cushion
    draw.rectangle([(cx - ch_w // 2 + 8, seat_y + ch_h),
                    (cx + ch_w // 2 - 8, seat_y + ch_h + ch_h // 3)],
                   fill=seat_color)
    draw.rectangle([(cx - ch_w // 2 + 4, seat_y + ch_h),
                    (cx + ch_w // 2 - 4, seat_y + ch_h + ch_h // 3 + 4)],
                   fill=None, outline=frame_color, width=4)

    # Legs
    leg_y = seat_y + ch_h + ch_h // 3 + 4
    leg_len = 90
    for lx in [cx - ch_w // 2 + 10, cx + ch_w // 2 - 10]:
        draw.rectangle([(lx - 5, leg_y), (lx + 5, leg_y + leg_len)],
                       fill=frame_color)

    # Shadow on floor
    shadow_pts = [
        (cx - ch_w // 2, leg_y + leg_len),
        (cx + ch_w // 2, leg_y + leg_len),
        (cx + ch_w // 2 + 40, leg_y + leg_len + 25),
        (cx - ch_w // 2 - 40, leg_y + leg_len + 25),
    ]
    draw.polygon(shadow_pts, fill=(148, 145, 140))


def draw_jamie(draw: ImageDraw.ImageDraw) -> None:
    """Jamie sitting in the chair on the far side of the table."""
    # Chair position — far side of table
    ch_cx, ch_cy = WIDTH // 2, 960

    chair_w, chair_h = 120, 140
    seat_y = ch_cy - chair_h // 2
    seat_color = (180, 175, 168)
    frame_color = (140, 135, 130)

    # Chair back
    draw.rectangle([(ch_cx - chair_w // 2, seat_y),
                    (ch_cx + chair_w // 2, seat_y + chair_h)],
                   fill=seat_color)
    draw.rectangle([(ch_cx - chair_w // 2 - 3, seat_y - 3),
                    (ch_cx + chair_w // 2 + 3, seat_y + chair_h + 3)],
                   fill=None, outline=frame_color, width=3)

    # Chair seat
    draw.rectangle([(ch_cx - chair_w // 2 + 8, seat_y + chair_h),
                    (ch_cx + chair_w // 2 - 8, seat_y + chair_h + chair_h // 3)],
                   fill=seat_color)
    draw.rectangle([(ch_cx - chair_w // 2 + 4, seat_y + chair_h),
                    (ch_cx + chair_w // 2 - 4, seat_y + chair_h + chair_h // 3 + 3)],
                   fill=None, outline=frame_color, width=3)

    # Jamie — torso (sitting in chair)
    torso_color = (62, 68, 78)  # dark sweater
    skin_color = (195, 172, 148)
    hair_color = (48, 40, 32)

    # Body
    body_top = seat_y - 10
    body_bot = seat_y + chair_h + 10
    draw.rectangle([(ch_cx - 28, body_top), (ch_cx + 28, body_bot)], fill=torso_color)

    # Shoulders — slightly broader for a teenager
    sh_w = 36
    draw.ellipse([(ch_cx - sh_w, body_top - 8),
                  (ch_cx + sh_w, body_top + 14)],
                 fill=torso_color)

    # Head
    head_r = 20
    head_cx = ch_cx
    head_cy = body_top - 35
    draw.ellipse([(head_cx - head_r, head_cy - head_r),
                  (head_cx + head_r, head_cy + head_r)],
                 fill=skin_color)
    # Hair — dark, short
    draw.ellipse([(head_cx - head_r - 3, head_cy - head_r - 5),
                  (head_cx + head_r + 3, head_cy - 4)],
                 fill=hair_color)

    # Hands in lap
    hand_w, hand_h = 12, 6
    hands_y = body_bot - 18
    draw.ellipse([(ch_cx - 18, hands_y), (ch_cx - 6, hands_y + hand_h)],
                 fill=skin_color)
    draw.ellipse([(ch_cx + 6, hands_y), (ch_cx + 18, hands_y + hand_h)],
                 fill=skin_color)

    # Eyes — two dark dots, looking slightly past camera
    draw.ellipse([(head_cx - 8, head_cy - 5), (head_cx - 3, head_cy + 2)],
                 fill=(28, 25, 20))
    draw.ellipse([(head_cx + 3, head_cy - 5), (head_cx + 8, head_cy + 2)],
                 fill=(28, 25, 20))

    # Mouth — closed, neutral
    draw.line([(head_cx - 6, head_cy + 10), (head_cx + 6, head_cy + 10)],
              fill=(165, 142, 118), width=2)


def draw_paper(draw: ImageDraw.ImageDraw) -> None:
    """Single sheet of paper on the table — stick figure drawing with no mouth."""
    px, py = WIDTH // 2 - 290, 1130
    pw, ph = 180, 240

    # Paper
    draw.rectangle([(px, py), (px + pw, py + ph)], fill=(252, 250, 245))
    draw.rectangle([(px, py), (px + pw, py + ph)], fill=None, outline=(200, 195, 188), width=2)

    # Stick figure on the paper (drawn like a child's drawing)
    fig_cx, fig_cy = px + pw // 2, py + ph // 2 - 10
    line_color = (80, 75, 68)

    # Head — circle
    head_r = 20
    draw.ellipse([(fig_cx - head_r, fig_cy - head_r - 30),
                  (fig_cx + head_r, fig_cy - head_r + 10)],
                 fill=None, outline=line_color, width=2)

    # Eyes — two dots
    draw.ellipse([(fig_cx - 6, fig_cy - 30), (fig_cx - 2, fig_cy - 26)],
                 fill=line_color)
    draw.ellipse([(fig_cx + 2, fig_cy - 30), (fig_cx + 6, fig_cy - 26)],
                 fill=line_color)

    # NO mouth — key detail

    # Body line
    draw.line([(fig_cx, fig_cy - head_r + 10), (fig_cx, fig_cy + 45)],
              fill=line_color, width=2)
    # Arms
    draw.line([(fig_cx, fig_cy), (fig_cx - 30, fig_cy + 20)], fill=line_color, width=2)
    draw.line([(fig_cx, fig_cy), (fig_cx + 30, fig_cy + 20)], fill=line_color, width=2)
    # Legs
    draw.line([(fig_cx, fig_cy + 45), (fig_cx - 22, fig_cy + 80)], fill=line_color, width=2)
    draw.line([(fig_cx, fig_cy + 45), (fig_cx + 22, fig_cy + 80)], fill=line_color, width=2)

    # Paper shadow on table
    draw.rectangle([(px + 6, py + ph), (px + pw + 6, py + ph + 8)],
                   fill=(155, 150, 145))


def draw_observation_window_hint(draw: ImageDraw.ImageDraw) -> None:
    """Subtle one-way mirror hint on the left wall — a dark glass panel."""
    mx, my = 30, 120
    mw, mh = 220, 680

    # Glass reflection — slightly darker
    for y in range(my, my + mh):
        t = (y - my) / mh
        r = int(185 + (165 - 185) * t)
        g = int(185 + (168 - 185) * t)
        b = int(190 + (175 - 190) * t)
        draw.line([(mx, y), (mx + mw, y)], fill=(r, g, b))

    # Glass sheen
    for step in range(8):
        sy = my + 40 + step * 80
        draw.line([(mx + 10, sy), (mx + mw - 10, sy)],
                  fill=(210, 210, 215), width=2)

    # Frame
    draw.rectangle([(mx - 5, my - 5), (mx + mw + 5, my + mh + 5)],
                   fill=None, outline=(135, 130, 125), width=5)


# ---------------------------------------------------------------------------
# Atmosphere
# ---------------------------------------------------------------------------

def apply_institutional_atmosphere(image: Image.Image) -> Image.Image:
    """Very slight cool cast over everything but the light band."""
    overlay = Image.new("RGBA", (WIDTH, ART_HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Subtle cool wash on top half
    for step in range(8):
        alpha = int(8 - step * 0.9)
        if alpha > 0:
            od.rectangle([(0, step * 80), (WIDTH, step * 80 + 80)],
                         fill=(190, 192, 200, alpha))
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
    title = metadata.get("title", "The Weight of Silence")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (230, 228, 224))
    draw = ImageDraw.Draw(image)

    draw_room(draw)
    draw_frosted_window(draw)
    draw_observation_window_hint(draw)
    draw_table(draw)
    draw_chair(draw, 470, 1400)
    draw_jamie(draw)
    draw_paper(draw)
    draw_light_band_on_table(draw)
    image = apply_institutional_atmosphere(image)

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
