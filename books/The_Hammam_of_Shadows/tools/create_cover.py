#!/usr/bin/env python3
"""Cover: The Hammam of Shadows — Marble hammam interior with star-shaped skylights, pool with prone figure, marble white/water blue/shadow indigo."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path


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

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH, HEIGHT = 1600, 2560
ARTWORK_BOTTOM = int(HEIGHT * 0.69)


# ---------------------------------------------------------------------------
# Scene drawing helpers
# ---------------------------------------------------------------------------


def _lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(len(c1)))


def _draw_background_gradient(draw, width, artwork_bottom):
    """Deep background: overhead dome, dark upper area brightening downward."""
    for y in range(artwork_bottom):
        t = y / artwork_bottom
        # Deep indigo at top, warm marble lower
        c = _lerp_color((10, 8, 25), (45, 38, 35), t)
        draw.line([(0, y), (width, y)], fill=c)


def _draw_dome(image, draw, width, artwork_bottom):
    """Domed ceiling with star-shaped skylights and warm amber glow from below."""
    cx = width // 2
    dome_cy = -60
    dome_rx = width // 2 + 40
    dome_ry = artwork_bottom // 2 + 80

    # Draw the dome interior as a pale stone arch
    dome_img = Image.new("RGBA", (width, artwork_bottom), (0, 0, 0, 0))
    dome_draw = ImageDraw.Draw(dome_img)
    dome_draw.ellipse(
        [cx - dome_rx, dome_cy - dome_ry, cx + dome_rx, dome_cy + dome_ry],
        fill=(210, 200, 185, 60),
        outline=(180, 170, 150, 80),
        width=3,
    )
    image.alpha_composite(dome_img)

    # Star-shaped skylights punched through the dome
    star_positions = [
        (cx, 40),
        (cx - 260, 110),
        (cx + 260, 110),
        (cx - 140, 60),
        (cx + 140, 60),
        (cx - 380, 200),
        (cx + 380, 200),
    ]
    for sx, sy in star_positions:
        _draw_star_skylight(draw, sx, sy, radius=22)


def _draw_star_skylight(draw, cx, cy, radius=22):
    """Eight-pointed star skylight with pale sky-blue glow."""
    points = []
    inner_r = radius * 0.42
    for i in range(16):
        angle = math.radians(i * 22.5 - 90)
        r = radius if i % 2 == 0 else inner_r
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))

    # Outer glow halo
    for expand in range(14, 0, -2):
        alpha = int(15 * (14 - expand) / 14)
        draw.ellipse(
            [cx - radius - expand, cy - radius - expand,
             cx + radius + expand, cy + radius + expand],
            fill=(160, 200, 230, alpha),
        )

    # The star shape itself
    draw.polygon(points, fill=(200, 230, 255, 220))
    draw.polygon(points, outline=(240, 250, 255, 180), width=1)


def _draw_columns(image, draw, width, artwork_bottom):
    """Marble columns framing the scene, with amber oil lamp glow."""
    column_specs = [
        # (x_center, width_col, shadow_side)
        (80, 58, "right"),
        (width - 80, 58, "left"),
        (220, 42, "right"),
        (width - 220, 42, "left"),
    ]

    for cx, cw, shadow in column_specs:
        # Column body gradient
        col_img = Image.new("RGBA", (width, artwork_bottom), (0, 0, 0, 0))
        col_draw = ImageDraw.Draw(col_img)
        for row in range(artwork_bottom):
            t = row / artwork_bottom
            base = _lerp_color((190, 178, 158), (160, 148, 130), t)
            col_draw.line([(cx - cw // 2, row), (cx + cw // 2, row)], fill=base + (210,))
        # Shadow strip
        shadow_x = (cx + cw // 2 - 8) if shadow == "right" else (cx - cw // 2)
        col_draw.rectangle(
            [shadow_x, 0, shadow_x + 10, artwork_bottom],
            fill=(20, 15, 10, 80),
        )
        image.alpha_composite(col_img)

        # Oil lamp bracket on inner-facing columns
        if cx in (220, width - 220):
            lamp_y = artwork_bottom // 3
            lamp_x = cx + (cw // 2 + 18) if shadow == "right" else cx - (cw // 2 + 18)
            _draw_oil_lamp(draw, lamp_x, lamp_y)


def _draw_oil_lamp(draw, cx, cy):
    """Small oil lamp with amber glow radiating outward."""
    # Glow halo
    for radius in range(55, 4, -4):
        alpha = int(45 * (55 - radius) / 55)
        color = (200, 140, 40, alpha)
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=color)

    # Lamp body
    draw.ellipse([cx - 10, cy - 5, cx + 10, cy + 12], fill=(100, 70, 20, 240))
    # Flame
    flame_pts = [(cx, cy - 18), (cx - 5, cy - 5), (cx + 5, cy - 5)]
    draw.polygon(flame_pts, fill=(255, 200, 80, 220))
    draw.polygon(
        [(cx, cy - 13), (cx - 3, cy - 5), (cx + 3, cy - 5)],
        fill=(255, 240, 160, 200),
    )


def _draw_marble_floor(image, draw, width, artwork_bottom):
    """Marble floor with perspective lines converging at center."""
    floor_top = int(artwork_bottom * 0.58)
    cx = width // 2

    # Floor base gradient: pale marble to shadow at edges
    floor_img = Image.new("RGBA", (width, artwork_bottom - floor_top), (0, 0, 0, 0))
    floor_draw = ImageDraw.Draw(floor_img)
    for y in range(artwork_bottom - floor_top):
        t = y / max(artwork_bottom - floor_top - 1, 1)
        c = _lerp_color((210, 205, 195), (175, 168, 155), t)
        floor_draw.line([(0, y), (width, y)], fill=c + (230,))

    image.alpha_composite(floor_img, dest=(0, floor_top))

    # Perspective grid lines
    vanish_y = int(artwork_bottom * 0.52)
    num_lines = 9
    for i in range(num_lines + 1):
        t = i / num_lines
        fx = int(t * width)
        draw.line([(cx, vanish_y), (fx, artwork_bottom)], fill=(160, 152, 140, 60), width=1)

    # Horizontal floor lines (closer together near vanish point)
    for step in range(1, 8):
        fy = vanish_y + int((artwork_bottom - vanish_y) * (step / 7) ** 1.4)
        x_span = int((width / 2) * (step / 7) ** 0.7)
        draw.line([(cx - x_span, fy), (cx + x_span, fy)], fill=(155, 148, 136, 55), width=1)


def _draw_pool(image, draw, width, artwork_bottom):
    """Steaming marble pool at center, pale water glowing faintly."""
    pool_cx = width // 2
    pool_cy = int(artwork_bottom * 0.72)
    pool_w = int(width * 0.48)
    pool_h = int(artwork_bottom * 0.11)

    # Pool surround (stone lip)
    lip_thickness = 14
    lip_rect = [
        pool_cx - pool_w // 2 - lip_thickness,
        pool_cy - pool_h // 2 - lip_thickness,
        pool_cx + pool_w // 2 + lip_thickness,
        pool_cy + pool_h // 2 + lip_thickness,
    ]
    draw.ellipse(lip_rect, fill=(195, 188, 175, 240), outline=(155, 145, 132, 200), width=3)

    # Water surface
    pool_rect = [
        pool_cx - pool_w // 2,
        pool_cy - pool_h // 2,
        pool_cx + pool_w // 2,
        pool_cy + pool_h // 2,
    ]
    pool_img = Image.new("RGBA", (width, artwork_bottom), (0, 0, 0, 0))
    pool_draw = ImageDraw.Draw(pool_img)
    pool_draw.ellipse(pool_rect, fill=(140, 175, 195, 180))

    # Water shimmer lines
    for _ in range(8):
        sx = random.randint(pool_cx - pool_w // 2 + 20, pool_cx + pool_w // 2 - 20)
        sy = random.randint(pool_cy - pool_h // 2 + 6, pool_cy + pool_h // 2 - 6)
        pool_draw.line([(sx, sy), (sx + random.randint(18, 45), sy)], fill=(200, 225, 235, 80), width=1)

    image.alpha_composite(pool_img)

    # Floating figure: body face-down at pool's edge (left side of pool)
    body_x = pool_cx - pool_w // 2 + 30
    body_y = pool_cy - 8
    _draw_prone_figure(draw, body_x, body_y)


def _draw_prone_figure(draw, x, y):
    """Simplified silhouette of a man face-down at the pool edge."""
    # Body elongated horizontally
    body_color = (40, 30, 22, 200)
    draw.ellipse([x, y - 12, x + 90, y + 12], fill=body_color)
    # Head
    draw.ellipse([x + 80, y - 10, x + 108, y + 10], fill=body_color)
    # Arms trailing
    draw.line([(x + 20, y + 8), (x - 20, y + 24)], fill=body_color, width=8)
    draw.line([(x + 50, y + 10), (x + 60, y + 28)], fill=body_color, width=7)


def _draw_fatma_silhouette(image, draw, width, artwork_bottom):
    """Silhouette of Fatma standing in the shadow of a column, watching."""
    # Position: right side, partially obscured by column shadow
    fig_x = width - 280
    fig_bottom = int(artwork_bottom * 0.88)
    fig_height = 155
    fig_top = fig_bottom - fig_height

    shadow_img = Image.new("RGBA", (width, artwork_bottom), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_img)

    # Figure silhouette — standing, slightly turned
    # Torso
    shadow_draw.polygon(
        [
            (fig_x - 18, fig_top + 38),
            (fig_x + 18, fig_top + 38),
            (fig_x + 22, fig_bottom - 12),
            (fig_x - 22, fig_bottom - 12),
        ],
        fill=(18, 12, 8, 240),
    )
    # Head
    shadow_draw.ellipse(
        [fig_x - 14, fig_top, fig_x + 14, fig_top + 30],
        fill=(18, 12, 8, 240),
    )
    # Head covering (tellak's cloth)
    shadow_draw.ellipse(
        [fig_x - 18, fig_top - 6, fig_x + 18, fig_top + 20],
        fill=(18, 12, 8, 240),
    )
    # Arm reaching slightly forward
    shadow_draw.polygon(
        [
            (fig_x + 18, fig_top + 55),
            (fig_x + 42, fig_top + 90),
            (fig_x + 36, fig_top + 96),
            (fig_x + 12, fig_top + 62),
        ],
        fill=(18, 12, 8, 220),
    )
    # Skirt/garment spreading at base
    shadow_draw.polygon(
        [
            (fig_x - 22, fig_bottom - 12),
            (fig_x + 22, fig_bottom - 12),
            (fig_x + 32, fig_bottom),
            (fig_x - 32, fig_bottom),
        ],
        fill=(18, 12, 8, 240),
    )

    # Column shadow behind her
    shadow_draw.rectangle(
        [fig_x - 60, fig_top - 30, fig_x - 20, artwork_bottom],
        fill=(8, 6, 4, 120),
    )

    image.alpha_composite(shadow_img)


def _draw_steam(image, width, artwork_bottom):
    """Translucent steam wisps rising from pool and floor."""
    steam_img = Image.new("RGBA", (width, artwork_bottom), (0, 0, 0, 0))
    steam_draw = ImageDraw.Draw(steam_img)

    random.seed(42)
    pool_cx = width // 2
    pool_cy = int(artwork_bottom * 0.72)

    for _ in range(18):
        sx = random.randint(pool_cx - 200, pool_cx + 200)
        sy_bottom = random.randint(pool_cy - 40, pool_cy + 20)
        wisp_height = random.randint(80, 220)
        wisp_width = random.randint(25, 65)
        for seg in range(8):
            alpha = int(28 * (1 - seg / 8))
            drift = random.randint(-8, 8)
            steam_draw.ellipse(
                [
                    sx + drift - wisp_width // 2,
                    sy_bottom - seg * wisp_height // 7 - wisp_height // 5,
                    sx + drift + wisp_width // 2,
                    sy_bottom - seg * wisp_height // 7 + wisp_height // 5,
                ],
                fill=(220, 230, 235, alpha),
            )

    blurred = steam_img.filter(ImageFilter.GaussianBlur(radius=5))
    image.alpha_composite(blurred)


def _draw_geometric_tile_border(draw, width, artwork_bottom):
    """Ottoman geometric tile border at the base of the walls on each side."""
    tile_y_top = int(artwork_bottom * 0.52)
    tile_height = int(artwork_bottom * 0.07)
    tile_size = 28

    # Left border strip
    for wall_x in [0, width - tile_size * 4]:
        for ty in range(tile_y_top, tile_y_top + tile_height, tile_size):
            for tx in range(wall_x, wall_x + tile_size * 4, tile_size):
                # Alternating pattern
                col = (tx - wall_x) // tile_size
                row = (ty - tile_y_top) // tile_size
                if (col + row) % 2 == 0:
                    fill = (140, 110, 80, 170)
                    accent = (180, 150, 100, 200)
                else:
                    fill = (90, 80, 65, 170)
                    accent = (120, 100, 75, 200)

                draw.rectangle([tx, ty, tx + tile_size - 2, ty + tile_size - 2], fill=fill)
                # Inner diamond accent
                cx_t, cy_t = tx + tile_size // 2, ty + tile_size // 2
                r = tile_size // 4
                pts = [(cx_t, cy_t - r), (cx_t + r, cy_t), (cx_t, cy_t + r), (cx_t - r, cy_t)]
                draw.polygon(pts, fill=accent)


def _draw_amber_wash(image, width, artwork_bottom):
    """Warm amber glow emanating from oil lamps, overlaid on scene."""
    wash_img = Image.new("RGBA", (width, artwork_bottom), (0, 0, 0, 0))
    wash_draw = ImageDraw.Draw(wash_img)

    lamp_positions = [(220, artwork_bottom // 3), (width - 220, artwork_bottom // 3)]
    for lx, ly in lamp_positions:
        for radius in range(200, 10, -15):
            alpha = int(22 * (200 - radius) / 200)
            wash_draw.ellipse(
                [lx - radius, ly - radius, lx + radius, ly + radius],
                fill=(200, 130, 30, alpha),
            )

    blurred = wash_img.filter(ImageFilter.GaussianBlur(radius=30))
    image.alpha_composite(blurred)


def draw_hammam_scene(image):
    """Draw the full Ottoman hammam scene on an RGBA image."""
    draw = ImageDraw.Draw(image, "RGBA")
    random.seed(17)

    _draw_background_gradient(draw, WIDTH, ARTWORK_BOTTOM)
    _draw_dome(image, draw, WIDTH, ARTWORK_BOTTOM)
    _draw_columns(image, draw, WIDTH, ARTWORK_BOTTOM)
    _draw_marble_floor(image, draw, WIDTH, ARTWORK_BOTTOM)
    _draw_pool(image, draw, WIDTH, ARTWORK_BOTTOM)
    _draw_geometric_tile_border(draw, WIDTH, ARTWORK_BOTTOM)
    _draw_amber_wash(image, WIDTH, ARTWORK_BOTTOM)
    _draw_steam(image, WIDTH, ARTWORK_BOTTOM)
    _draw_fatma_silhouette(image, draw, WIDTH, ARTWORK_BOTTOM)


# ---------------------------------------------------------------------------
# Standard title-panel helpers (required by project convention)
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



def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Hammam of Shadows")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw_hammam_scene(image)
    _draw_standard_cover_title_panel(image, title, author, model)

    out = image.convert("RGB")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    out.save(out_path, "PNG")
    print(f"Cover saved to {out_path}")


def main():
    parser = argparse.ArgumentParser(description="Generate cover for The Hammam of Shadows")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
