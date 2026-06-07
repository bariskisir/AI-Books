#!/usr/bin/env python3
"""
Cover art for The Glass Self.

Scene: A psychiatrist's figure standing at the end of a long hospital corridor
at night. The corridor is institutional — cold blue-white fluorescent light,
polished vinyl floor, rows of closed doors. The figure is fully present and
solid. But his reflection in the polished floor is absent — a perfect black
void where the reflection should be, as though the floor has swallowed the
image. A single warm yellow light burns at the far end of the corridor, the
only warmth in the scene. The palette is cold institutional blue-white with
that single warm point of promise. The mood is clinical and deeply unsettling.
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
# Background: corridor walls and ceiling
# ---------------------------------------------------------------------------

def draw_corridor_background(draw: ImageDraw.ImageDraw) -> None:
    """Cold blue-white institutional corridor with perspective."""
    # Sky/ceiling gradient — deep blue-black at top
    for y in range(0, ART_HEIGHT):
        t = y / ART_HEIGHT
        r = int(8 + (38 - 8) * t)
        g = int(12 + (52 - 12) * t)
        b = int(22 + (78 - 22) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


# ---------------------------------------------------------------------------
# Corridor floor — polished vinyl with perspective lines
# ---------------------------------------------------------------------------

def draw_floor(draw: ImageDraw.ImageDraw) -> None:
    """Polished institutional floor with perspective vanishing point."""
    floor_y = 900  # Where floor begins in the image
    vp_x = WIDTH // 2  # Vanishing point x (center)
    vp_y = 640  # Vanishing point y (horizon)

    # Floor surface gradient — dark grey going lighter toward horizon
    for y in range(floor_y, ART_HEIGHT):
        t = (y - floor_y) / (ART_HEIGHT - floor_y)
        r = int(28 + (15 - 28) * (1 - t))
        g = int(34 + (18 - 34) * (1 - t))
        b = int(45 + (24 - 45) * (1 - t))
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Perspective lines on floor (tile joints)
    num_lines = 16
    for i in range(num_lines + 1):
        # Bottom edge spread
        x_bottom = int(WIDTH * i / num_lines)
        # Lines converge toward vanishing point
        draw.line([(x_bottom, ART_HEIGHT), (vp_x, vp_y)],
                  fill=(40, 50, 65, 180), width=1)

    # Horizontal floor tile lines
    num_h_lines = 14
    for i in range(1, num_h_lines + 1):
        t = i / num_h_lines
        # Perspective: lines cluster near horizon
        y = int(vp_y + (ART_HEIGHT - vp_y) * (t ** 1.8))
        if y > floor_y:
            # Width narrows toward vanishing point
            half_w = int(WIDTH * 0.5 * (1 - (1 - t) ** 0.7))
            draw.line([(vp_x - half_w, y), (vp_x + half_w, y)],
                      fill=(38, 48, 62), width=1)


# ---------------------------------------------------------------------------
# Corridor walls — left and right with perspective
# ---------------------------------------------------------------------------

def draw_walls(draw: ImageDraw.ImageDraw) -> None:
    """Corridor side walls with closed doors, perspective receding."""
    vp_x = WIDTH // 2
    vp_y = 640
    floor_y = 900

    # Wall panels — left side
    left_wall_bottom = [(0, floor_y), (0, ART_HEIGHT - 300)]
    left_wall_top = [(0, 0), (0, floor_y)]
    # Left wall face
    left_pts = [
        (0, 120),
        (vp_x - 40, vp_y - 20),
        (vp_x - 40, floor_y + 20),
        (0, floor_y),
    ]
    draw.polygon(left_pts, fill=(22, 28, 42))

    # Right wall face
    right_pts = [
        (WIDTH, 120),
        (vp_x + 40, vp_y - 20),
        (vp_x + 40, floor_y + 20),
        (WIDTH, floor_y),
    ]
    draw.polygon(right_pts, fill=(18, 24, 38))

    # Ceiling polygon
    ceiling_pts = [
        (0, 0),
        (WIDTH, 0),
        (WIDTH, 120),
        (vp_x + 40, vp_y - 20),
        (vp_x - 40, vp_y - 20),
        (0, 120),
    ]
    draw.polygon(ceiling_pts, fill=(12, 16, 28))

    # Draw doors on left wall
    _draw_corridor_doors(draw, side='left')
    # Draw doors on right wall
    _draw_corridor_doors(draw, side='right')


def _draw_corridor_doors(draw: ImageDraw.ImageDraw, side: str) -> None:
    """Draw a series of receding closed doors on one side of the corridor."""
    vp_x = WIDTH // 2
    vp_y = 640
    floor_y = 900

    num_doors = 6
    for i in range(num_doors):
        t = (i + 0.5) / num_doors
        # Perspective scale — doors shrink toward vanishing point
        scale = 1.0 - t * 0.72

        if side == 'left':
            # Left wall: doors on the left side
            base_x = int(WIDTH * 0.05 + t * (vp_x * 0.7 - WIDTH * 0.05))
            door_w = int(85 * scale)
            door_h = int(220 * scale)
            door_y_bottom = int(floor_y - 20 * (1 - t))
            door_y_top = door_y_bottom - door_h
            # Door is on the left wall panel — skewed slightly
            pts = [
                (base_x, door_y_top),
                (base_x + door_w, door_y_top),
                (base_x + door_w, door_y_bottom),
                (base_x, door_y_bottom),
            ]
        else:
            base_x = int(WIDTH * 0.95 - t * (vp_x * 0.7 - WIDTH * 0.05))
            door_w = int(85 * scale)
            door_h = int(220 * scale)
            door_y_bottom = int(floor_y - 20 * (1 - t))
            door_y_top = door_y_bottom - door_h
            pts = [
                (base_x - door_w, door_y_top),
                (base_x, door_y_top),
                (base_x, door_y_bottom),
                (base_x - door_w, door_y_bottom),
            ]

        # Door frame
        frame_col = (30, 38, 55)
        draw.polygon(pts, fill=frame_col)
        # Door surface (slightly lighter)
        inset = max(2, int(6 * scale))
        if side == 'left':
            inner_pts = [
                (pts[0][0] + inset, pts[0][1] + inset),
                (pts[1][0] - inset, pts[1][1] + inset),
                (pts[2][0] - inset, pts[2][1] - inset),
                (pts[3][0] + inset, pts[3][1] - inset),
            ]
        else:
            inner_pts = [
                (pts[0][0] + inset, pts[0][1] + inset),
                (pts[1][0] - inset, pts[1][1] + inset),
                (pts[2][0] - inset, pts[2][1] - inset),
                (pts[3][0] + inset, pts[3][1] - inset),
            ]
        draw.polygon(inner_pts, fill=(35, 44, 62))


# ---------------------------------------------------------------------------
# Fluorescent lights on ceiling
# ---------------------------------------------------------------------------

def draw_ceiling_lights(draw: ImageDraw.ImageDraw) -> None:
    """Fluorescent strip lights running down the corridor center."""
    vp_x = WIDTH // 2
    vp_y = 640

    num_lights = 8
    for i in range(num_lights):
        t = i / num_lights
        # Position along ceiling strip
        y = int(vp_y - 30 + (120 - vp_y + 30) * (1 - t))
        half_w = int(90 * (1 - t * 0.75))
        # Light fixture rectangle
        draw.rectangle(
            [(vp_x - half_w, y - max(2, int(6 * (1 - t)))),
             (vp_x + half_w, y + max(2, int(6 * (1 - t))))],
            fill=(200, 215, 230)
        )
        # Glow effect around light
        glow_color = (90, 110, 140)
        draw.ellipse(
            [(vp_x - half_w - 10, y - 15),
             (vp_x + half_w + 10, y + 15)],
            fill=glow_color
        )

    # Cast light pools downward from each fixture
    for i in range(num_lights):
        t = i / num_lights
        y_ceiling = int(vp_y - 30 + (120 - vp_y + 30) * (1 - t))
        pool_w = int(120 * (1 - t * 0.7))
        pool_y = int(900 - 300 * t)
        if pool_y > y_ceiling:
            # Light cone
            pts = [
                (vp_x - 8, y_ceiling),
                (vp_x + 8, y_ceiling),
                (vp_x + pool_w, pool_y),
                (vp_x - pool_w, pool_y),
            ]
            draw.polygon(pts, fill=(45, 58, 80))


# ---------------------------------------------------------------------------
# The warm yellow light at the far end
# ---------------------------------------------------------------------------

def draw_far_light(draw: ImageDraw.ImageDraw, image: Image.Image) -> None:
    """A single warm yellow-amber glow at the vanishing point end."""
    vp_x = WIDTH // 2
    vp_y = 640

    # Radiate warm glow from the vanishing point
    layers = [
        (60, (255, 230, 140, 18)),
        (42, (255, 215, 100, 28)),
        (28, (255, 200, 80, 45)),
        (18, (255, 190, 60, 70)),
        (10, (255, 210, 120, 100)),
        (5, (255, 240, 180, 160)),
    ]
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    for radius, color in layers:
        overlay_draw.ellipse(
            [(vp_x - radius, vp_y - radius),
             (vp_x + radius, vp_y + radius)],
            fill=color
        )
    # Composite
    image_rgba = image.convert("RGBA")
    image_rgba.alpha_composite(overlay)
    final = image_rgba.convert("RGB")
    image.paste(final)


# ---------------------------------------------------------------------------
# The figure — solid, present, standing at the near end of corridor
# ---------------------------------------------------------------------------

def draw_figure(draw: ImageDraw.ImageDraw) -> None:
    """A standing figure in a long coat, fully present, near the front."""
    fig_cx = WIDTH // 2
    fig_base = 1580  # Standing on the floor near the bottom of the art area

    # Figure dimensions
    leg_h = 220
    body_h = 210
    head_r = 38
    coat_w = 88

    fig_color = (55, 65, 85)
    coat_color = (48, 58, 78)
    highlight = (75, 90, 115)

    # Legs
    draw.rectangle(
        [(fig_cx - 28, fig_base - leg_h),
         (fig_cx + 28, fig_base)],
        fill=fig_color
    )
    # Coat / body — slightly wider
    draw.rectangle(
        [(fig_cx - coat_w // 2, fig_base - leg_h - body_h),
         (fig_cx + coat_w // 2, fig_base - leg_h + 30)],
        fill=coat_color
    )
    # Coat lapels / slight highlight
    draw.rectangle(
        [(fig_cx - coat_w // 2 + 5, fig_base - leg_h - body_h + 10),
         (fig_cx - coat_w // 4, fig_base - leg_h - 20)],
        fill=highlight
    )
    # Arms at sides
    draw.rectangle(
        [(fig_cx - coat_w // 2 - 16, fig_base - leg_h - body_h + 40),
         (fig_cx - coat_w // 2, fig_base - leg_h + 70)],
        fill=coat_color
    )
    draw.rectangle(
        [(fig_cx + coat_w // 2, fig_base - leg_h - body_h + 40),
         (fig_cx + coat_w // 2 + 16, fig_base - leg_h + 70)],
        fill=coat_color
    )
    # Head
    head_cy = fig_base - leg_h - body_h - head_r
    draw.ellipse(
        [(fig_cx - head_r, head_cy - head_r),
         (fig_cx + head_r, head_cy + head_r)],
        fill=(72, 82, 98)
    )
    # Subtle highlight on head/face
    draw.ellipse(
        [(fig_cx - 14, head_cy - 16),
         (fig_cx + 14, head_cy + 6)],
        fill=(88, 100, 118)
    )


# ---------------------------------------------------------------------------
# The absent reflection — black void in floor where reflection should be
# ---------------------------------------------------------------------------

def draw_absent_reflection(draw: ImageDraw.ImageDraw) -> None:
    """Where the figure's reflection should appear in the polished floor,
    there is only a deep black void — the defining horror of the image."""
    fig_cx = WIDTH // 2
    fig_base = 1580

    # Reflection zone: mirror image position below fig_base
    ref_top = fig_base + 10
    ref_height = 420
    ref_w_top = 75
    ref_w_bottom = 110

    # The void — absolute black, slightly wider than the figure
    void_pts = [
        (fig_cx - ref_w_top, ref_top),
        (fig_cx + ref_w_top, ref_top),
        (fig_cx + ref_w_bottom, ref_top + ref_height),
        (fig_cx - ref_w_bottom, ref_top + ref_height),
    ]
    draw.polygon(void_pts, fill=(0, 0, 0))

    # Subtle dark halo around the void to make it more uncanny
    halo_pts = [
        (fig_cx - ref_w_top - 14, ref_top - 5),
        (fig_cx + ref_w_top + 14, ref_top - 5),
        (fig_cx + ref_w_bottom + 20, ref_top + ref_height + 15),
        (fig_cx - ref_w_bottom - 20, ref_top + ref_height + 15),
    ]
    # Draw as semi-transparent by layering dark tones
    for inset in range(15, 0, -3):
        fade = 255 - inset * 8
        pts = [
            (fig_cx - ref_w_top - inset, ref_top - inset // 2),
            (fig_cx + ref_w_top + inset, ref_top - inset // 2),
            (fig_cx + ref_w_bottom + inset + 5, ref_top + ref_height + inset),
            (fig_cx - ref_w_bottom - inset - 5, ref_top + ref_height + inset),
        ]
        draw.polygon(pts, fill=(max(0, 15 - inset), max(0, 18 - inset), max(0, 28 - inset)))


# ---------------------------------------------------------------------------
# Floor reflection of corridor lights (present — only the PERSON is absent)
# ---------------------------------------------------------------------------

def draw_floor_reflections(draw: ImageDraw.ImageDraw) -> None:
    """Corridor lights DO reflect — emphasizing the absence of the figure's reflection."""
    vp_x = WIDTH // 2
    floor_y = 900

    # Subtle corridor-light reflections in floor
    num_pools = 7
    for i in range(num_pools):
        t = i / num_pools
        y = int(floor_y + (ART_HEIGHT - floor_y) * (0.05 + t * 0.85))
        half_w = int(55 * (1 - t * 0.55))
        brightness = int(30 + (1 - t) * 25)
        draw.ellipse(
            [(vp_x - half_w, y - 8),
             (vp_x + half_w, y + 8)],
            fill=(brightness, brightness + 10, brightness + 22)
        )


# ---------------------------------------------------------------------------
# Atmospheric: subtle blue flicker at ceiling edges
# ---------------------------------------------------------------------------

def draw_ceiling_flicker(draw: ImageDraw.ImageDraw) -> None:
    """Subtle blue-white flicker lines at ceiling, suggesting fluorescent buzz."""
    for i in range(18):
        x = int(WIDTH * i / 18) + 12
        y_top = int(22 + i % 3 * 8)
        y_bot = int(y_top + 30 + (i % 5) * 12)
        alpha = int(30 + (i % 4) * 12)
        draw.line(
            [(x, y_top), (x, y_bot)],
            fill=(140, 165, 200),
            width=1
        )


# ---------------------------------------------------------------------------
# Apply atmospheric blur
# ---------------------------------------------------------------------------

def apply_atmosphere(image: Image.Image) -> Image.Image:
    """Very light blur on background for depth."""
    bg = image.crop((0, 0, WIDTH, 700))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=1.5))
    result = image.copy()
    result.paste(bg, (0, 0))
    return result


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Glass Self")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (8, 12, 22))
    draw = ImageDraw.Draw(image)

    draw_corridor_background(draw)
    draw_walls(draw)
    draw_floor(draw)
    draw_ceiling_lights(draw)
    draw_far_light(draw, image)
    draw_floor_reflections(draw)
    draw_absent_reflection(draw)
    draw_figure(draw)
    draw_ceiling_flicker(draw)
    image = apply_atmosphere(image)

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
    draw.rectangle((0, py, 1600, 2560), fill=(8, 10, 18, 255))
    draw.line((180, py + 17, 1420, py + 17), fill=(80, 100, 145, 125), width=3)
    title_font, lines, gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 52)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in lines) + max(0, len(lines) - 1) * gap
    author_height = draw.textbbox((0, 0), author, font=author_font)[3] - draw.textbbox((0, 0), author, font=author_font)[1]
    y = py + 120 + max(0, (2560 - py - 230 - (title_height + 118 + author_height)) // 2)
    y = _standard_cover_center(draw, y, lines, title_font, (185, 205, 235), gap, 1600) + 118
    _standard_cover_center(draw, y, [author], author_font, (140, 165, 205), 12, 1600)
    if model:
        model_font = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, 2560 - 110, [model], model_font, (90, 115, 155), 12, 1600)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cover for The Glass Self")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    create_cover(args.metadata, args.out)
