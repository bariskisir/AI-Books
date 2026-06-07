#!/usr/bin/env python3
"""
Cover art for The Fragile Mind.

Scene: A cluster of seven or eight doors of different sizes, colours, and
styles arranged in a circle on a pale mist-grey void — each door slightly
ajar, each with a different quality of light leaking through. At the centre
of the arrangement, facing away from us, a lone female figure stands
perfectly still, looking at the doors. The doors suggest multiple inner
worlds, distinct but belonging to the same space. Pale lavender-grey
palette with warm amber leaking from the nearest door. The mood is quietly
extraordinary: eerie but not threatening, mysterious but not hostile.
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765


# ---------------------------------------------------------------------------
# Void background
# ---------------------------------------------------------------------------

def draw_void(draw: ImageDraw.ImageDraw) -> None:
    """Soft grey-lavender void — gradient from top to bottom."""
    for y in range(0, ART_HEIGHT):
        t = y / ART_HEIGHT
        r = int(185 + (155 - 185) * t)
        g = int(182 + (152 - 182) * t)
        b = int(195 + (170 - 195) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


# ---------------------------------------------------------------------------
# Ground plane (subtle)
# ---------------------------------------------------------------------------

def draw_ground(draw: ImageDraw.ImageDraw) -> None:
    """Very soft ground suggestion — grey plane extending from bottom."""
    ground_y = 1180
    for y in range(ground_y, ART_HEIGHT):
        t = (y - ground_y) / (ART_HEIGHT - ground_y)
        r = int(165 + (140 - 165) * t)
        g = int(162 + (138 - 162) * t)
        b = int(178 + (155 - 178) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Horizon line — very faint
    draw.line([(0, ground_y), (WIDTH, ground_y)], fill=(148, 144, 162), width=1)


# ---------------------------------------------------------------------------
# Door drawing utility
# ---------------------------------------------------------------------------

def draw_door(draw: ImageDraw.ImageDraw, image: Image.Image,
              cx: int, cy: int, w: int, h: int,
              frame_color: tuple, panel_color: tuple,
              light_color: tuple, ajar_angle: float = 0.12,
              has_knob: bool = True) -> None:
    """Draw a single door with its frame, panel, light leak, and optional knob."""

    # Light leak behind the door (the ajar gap)
    gap = int(w * ajar_angle)
    light_pts = [
        (cx - w // 2, cy - h // 2),
        (cx - w // 2 + gap, cy - h // 2 - int(h * 0.05)),
        (cx - w // 2 + gap, cy + h // 2),
        (cx - w // 2, cy + h // 2),
    ]
    draw.polygon(light_pts, fill=light_color)

    # Door frame
    frame_thickness = max(8, w // 12)
    draw.rectangle(
        [(cx - w // 2 - frame_thickness, cy - h // 2 - frame_thickness),
         (cx + w // 2 + frame_thickness, cy + h // 2 + frame_thickness)],
        fill=frame_color
    )

    # Door surface (slightly inset)
    door_surface_color = panel_color
    draw.rectangle(
        [(cx - w // 2, cy - h // 2),
         (cx + w // 2, cy + h // 2)],
        fill=door_surface_color
    )

    # Door panel lines (recessed panel detail)
    panel_margin = max(8, w // 8)
    panel_inner_color = (
        max(0, panel_color[0] - 20),
        max(0, panel_color[1] - 20),
        max(0, panel_color[2] - 20),
    )
    # Upper panel
    up_top = cy - h // 2 + panel_margin
    up_bot = cy - h // 2 + h // 2 - panel_margin // 2
    draw.rectangle(
        [(cx - w // 2 + panel_margin, up_top),
         (cx + w // 2 - panel_margin, up_bot)],
        fill=panel_inner_color
    )
    # Lower panel
    lo_top = cy - h // 2 + h // 2 + panel_margin // 2
    lo_bot = cy + h // 2 - panel_margin
    draw.rectangle(
        [(cx - w // 2 + panel_margin, lo_top),
         (cx + w // 2 - panel_margin, lo_bot)],
        fill=panel_inner_color
    )

    # Knob
    if has_knob:
        knob_x = cx + w // 2 - w // 6
        knob_y = cy + h // 10
        knob_r = max(5, w // 14)
        draw.ellipse(
            [(knob_x - knob_r, knob_y - knob_r),
             (knob_x + knob_r, knob_y + knob_r)],
            fill=(180, 160, 100)
        )

    # Light glow onto floor
    glow_pts = [
        (cx - w // 2, cy + h // 2),
        (cx - w // 2 + gap * 3, cy + h // 2),
        (cx - w // 2 + gap * 5, cy + h // 2 + h // 3),
        (cx - w // 2 - gap, cy + h // 2 + h // 3),
    ]
    draw.polygon(glow_pts, fill=(
        min(255, light_color[0] + 20),
        min(255, light_color[1] + 10),
        min(255, light_color[2]),
    ))


def draw_all_doors(draw: ImageDraw.ImageDraw, image: Image.Image) -> None:
    """Eight doors arranged in a rough arc surrounding the central figure."""

    # Center of the arc is where the figure stands
    fig_cx, fig_cy = WIDTH // 2, 1150

    # Door specifications: (relative angle, distance, width, height, frame_color, panel_color, light_color, ajar)
    doors = [
        # Far left — large wooden door, amber light
        (math.pi * 1.28, 580, 160, 360, (75, 55, 35), (95, 72, 48), (255, 200, 120), 0.18),
        # Left — smaller pale door, cool blue light
        (math.pi * 1.16, 420, 110, 270, (100, 100, 115), (135, 132, 148), (180, 200, 255), 0.10),
        # Upper left — narrow dark door, green light
        (math.pi * 1.05, 500, 90, 240, (42, 52, 42), (58, 72, 55), (140, 210, 140), 0.08),
        # Upper center-left — wide pale door, warm yellow
        (math.pi * 0.96, 470, 130, 290, (155, 140, 110), (175, 162, 132), (255, 240, 180), 0.14),
        # Upper center-right — narrow red-brown door, rose light
        (math.pi * 0.88, 490, 95, 260, (88, 48, 38), (112, 62, 50), (255, 180, 160), 0.09),
        # Right — medium grey door, lavender light
        (math.pi * 0.78, 430, 120, 280, (88, 82, 105), (115, 108, 135), (220, 190, 255), 0.12),
        # Far right — large dark door, white light
        (math.pi * 0.66, 560, 155, 350, (45, 42, 50), (62, 58, 70), (240, 240, 255), 0.20),
        # Background center — very small distant door
        (math.pi, 310, 70, 185, (120, 115, 125), (148, 142, 155), (200, 195, 215), 0.06),
    ]

    for angle, dist, w, h, fc, pc, lc, ajar in doors:
        dx = int(dist * math.cos(angle))
        dy = int(dist * math.sin(angle) * 0.45)  # flatten Y for perspective
        door_cx = fig_cx + dx
        door_cy = fig_cy + dy
        draw_door(draw, image, door_cx, door_cy, w, h, fc, pc, lc, ajar)


# ---------------------------------------------------------------------------
# Central figure
# ---------------------------------------------------------------------------

def draw_figure(draw: ImageDraw.ImageDraw) -> None:
    """Small female silhouette, back to viewer, facing the circle of doors."""
    fig_cx, fig_cy = WIDTH // 2, 1150

    fig_color = (55, 50, 65)

    # Body
    body_w, body_h = 42, 110
    draw.ellipse(
        [(fig_cx - body_w // 2, fig_cy - body_h),
         (fig_cx + body_w // 2, fig_cy)],
        fill=fig_color
    )
    # Head
    head_r = 22
    draw.ellipse(
        [(fig_cx - head_r, fig_cy - body_h - head_r * 2),
         (fig_cx + head_r, fig_cy - body_h)],
        fill=fig_color
    )
    # Arms
    draw.line([(fig_cx - body_w // 2, fig_cy - body_h + 30),
               (fig_cx - body_w // 2 - 28, fig_cy - body_h + 80)],
              fill=fig_color, width=10)
    draw.line([(fig_cx + body_w // 2, fig_cy - body_h + 30),
               (fig_cx + body_w // 2 + 28, fig_cy - body_h + 80)],
              fill=fig_color, width=10)
    # Legs
    draw.line([(fig_cx - 12, fig_cy), (fig_cx - 18, fig_cy + 85)],
              fill=fig_color, width=12)
    draw.line([(fig_cx + 12, fig_cy), (fig_cx + 18, fig_cy + 85)],
              fill=fig_color, width=12)

    # Shadow on ground
    shadow_pts = [
        (fig_cx - 45, fig_cy + 85),
        (fig_cx + 45, fig_cy + 85),
        (fig_cx + 80, fig_cy + 115),
        (fig_cx - 80, fig_cy + 115),
    ]
    draw.polygon(shadow_pts, fill=(145, 140, 158))


# ---------------------------------------------------------------------------
# Atmospheric mist
# ---------------------------------------------------------------------------

def apply_mist(image: Image.Image) -> Image.Image:
    """Layered soft mist — Gaussian blur on background region."""
    bg = image.crop((0, 0, WIDTH, 700))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=2.5))
    result = image.copy()
    result.paste(bg, (0, 0))
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Fragile Mind")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (185, 182, 195))
    draw = ImageDraw.Draw(image)

    draw_void(draw)
    draw_ground(draw)
    draw_all_doors(draw, image)
    draw_figure(draw)
    image = apply_mist(image)

    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers
# ---------------------------------------------------------------------------

def _standard_cover_font(name, size):
    candidates = [name, "arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]
    if "bd" in name.lower() or "bold" in name.lower():
        candidates = [name, "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()

def _standard_cover_repair_text(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text

def _standard_cover_wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        trial = " ".join(current + [word])
        box = draw.textbbox((0, 0), trial, font=font)
        if current and box[2] - box[0] > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines or [text]

def _standard_cover_center(draw, y, lines, font, fill, gap, width):
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font)
        draw.text(((width - (box[2] - box[0])) // 2, y), line, font=font, fill=fill)
        y += box[3] - box[1] + gap
    return y

def _standard_cover_title_font(draw, title, max_width):
    for size in (116, 104, 96, 88, 80, 72, 66, 60):
        font = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), font, max_width)
        heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]
        if len(lines) <= 4 and sum(heights) + max(0, len(lines) - 1) * 18 <= 430:
            return font, lines, 18
    font = _standard_cover_font("arialbd.ttf", 58)
    return font, _standard_cover_wrap(draw, title.upper(), font, max_width), 14

def _standard_cover_resolve_title(local_vars):
    for key in ("title", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value
    return ""

def _standard_cover_resolve_author(local_vars):
    for key in ("author", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value
    return "Barış Kısır"

def _draw_standard_cover_title_panel(image, title="", author="", model=""):
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    py = 1765
    draw.rectangle((0, py, 1600, 2560), fill=(22, 18, 28, 255))
    draw.line((180, py + 17, 1420, py + 17), fill=(150, 130, 190, 125), width=3)
    title_font, lines, gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 52)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in lines) + max(0, len(lines) - 1) * gap
    author_height = draw.textbbox((0, 0), author, font=author_font)[3] - draw.textbbox((0, 0), author, font=author_font)[1]
    y = py + 120 + max(0, (2560 - py - 230 - (title_height + 118 + author_height)) // 2)
    y = _standard_cover_center(draw, y, lines, title_font, (210, 200, 225), gap, 1600) + 118
    _standard_cover_center(draw, y, [author], author_font, (175, 165, 195), 12, 1600)
    if model:
        model_font = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, 2560 - 110, [model], model_font, (130, 115, 155), 12, 1600)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cover for The Fragile Mind")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    create_cover(args.metadata, args.out)
