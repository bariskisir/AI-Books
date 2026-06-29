#!/usr/bin/env python3
"""
Cover art for The Fermentation Master.

Scene: Rows of large clay onggi fermentation jars on an outdoor stone platform
behind a traditional Korean hanok courtyard. Afternoon autumn light. Warm ochre
and deep terracotta palette. A woman's hands rest on the lid of one large jar.
Dried chili peppers hang on a rack to one side. The curved hanok roofline is
visible behind.
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
ART_HEIGHT = 1765  # upper art zone; lower panel starts here


# ---------------------------------------------------------------------------
# Sky and background
# ---------------------------------------------------------------------------

def draw_sky(draw: ImageDraw.ImageDraw) -> None:
    """Pale autumn sky — faint blue-grey gradient."""
    for y in range(0, 520):
        t = y / 520
        r = int(195 + (210 - 195) * t)
        g = int(205 + (215 - 205) * t)
        b = int(215 + (200 - 215) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


# ---------------------------------------------------------------------------
# Hanok roofline
# ---------------------------------------------------------------------------

def draw_hanok_roofline(draw: ImageDraw.ImageDraw) -> None:
    """Simplified tiled hanok eave running across upper portion of scene."""
    roof_top_y = 80
    roof_bottom_y = 420
    # Main roof trapezoid
    draw.polygon(
        [(0, roof_bottom_y), (WIDTH, roof_bottom_y),
         (WIDTH - 60, roof_top_y + 50), (60, roof_top_y + 50)],
        fill=(62, 52, 44),
    )
    # Tile rows — curved lines suggesting traditional curved tiles
    tile_color = (52, 44, 36)
    for row in range(8):
        y_base = roof_top_y + 50 + row * 42
        if y_base >= roof_bottom_y:
            break
        for col in range(22):
            x0 = col * 75 - 10
            x1 = x0 + 68
            cy = y_base + 18
            # Draw a gentle curve for each tile
            pts = []
            for px in range(x0, x1, 3):
                theta = math.pi * (px - x0) / (x1 - x0)
                py = cy - int(10 * math.sin(theta))
                pts.append((px, py))
            if len(pts) >= 2:
                draw.line(pts, fill=tile_color, width=2)
    # Eave overhang — curved upward ends
    eave_y = roof_bottom_y
    # Left end curve
    draw.arc([-80, eave_y - 60, 120, eave_y + 60], start=270, end=360, fill=(42, 36, 28), width=8)
    # Right end curve
    draw.arc([WIDTH - 120, eave_y - 60, WIDTH + 80, eave_y + 60], start=180, end=270, fill=(42, 36, 28), width=8)
    # Eave ridge line
    draw.line([(0, eave_y), (WIDTH, eave_y)], fill=(42, 36, 28), width=6)
    # Ridge decoration
    draw.rectangle([(WIDTH // 2 - 60, roof_top_y + 30), (WIDTH // 2 + 60, roof_top_y + 62)],
                   fill=(72, 60, 48))


# ---------------------------------------------------------------------------
# Courtyard ground and stone platform
# ---------------------------------------------------------------------------

def draw_ground(draw: ImageDraw.ImageDraw) -> None:
    """Earthen courtyard with fitted stone platform."""
    # Ground — pale ochre earth
    for y in range(380, ART_HEIGHT):
        t = (y - 380) / (ART_HEIGHT - 380)
        r = int(175 + (145 - 175) * t)
        g = int(158 + (130 - 158) * t)
        b = int(118 + (95 - 118) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Stone platform — darker fitted stone surface
    platform_top = 680
    platform_bottom = ART_HEIGHT - 20
    draw.rectangle([(60, platform_top), (WIDTH - 60, platform_bottom)],
                   fill=(130, 118, 100))

    # Fitted stone joints — horizontal
    stone_rows = [720, 770, 820, 870, 920, 970, 1020, 1080, 1140, 1200,
                  1260, 1320, 1380, 1440, 1500, 1560, 1620, 1680, 1720]
    for sy in stone_rows:
        if sy < platform_bottom:
            draw.line([(60, sy), (WIDTH - 60, sy)], fill=(108, 98, 82), width=2)

    # Fitted stone joints — vertical (offset by row)
    stone_cols_a = [200, 400, 600, 800, 1000, 1200, 1400]
    stone_cols_b = [120, 320, 520, 720, 920, 1120, 1320, 1480]
    for i, sy in enumerate(stone_rows):
        cols = stone_cols_a if i % 2 == 0 else stone_cols_b
        next_sy = stone_rows[i + 1] if i + 1 < len(stone_rows) else platform_bottom
        if sy < platform_bottom:
            for sx in cols:
                if 60 < sx < WIDTH - 60:
                    draw.line([(sx, sy), (sx, min(next_sy, platform_bottom))],
                              fill=(108, 98, 82), width=2)

    # Platform front edge
    draw.rectangle([(60, platform_top), (WIDTH - 60, platform_top + 18)],
                   fill=(118, 106, 88))
    draw.line([(60, platform_top), (WIDTH - 60, platform_top)], fill=(90, 80, 65), width=3)


# ---------------------------------------------------------------------------
# Autumn foliage strip
# ---------------------------------------------------------------------------

def draw_foliage(draw: ImageDraw.ImageDraw) -> None:
    """Sparse autumn leaves and branch suggestion at the back of the courtyard."""
    # Background wall suggestion behind platform
    wall_y = 400
    wall_bot = 690
    for y in range(wall_y, wall_bot):
        t = (y - wall_y) / (wall_bot - wall_y)
        r = int(185 + (170 - 185) * t)
        g = int(165 + (150 - 165) * t)
        b = int(120 + (110 - 120) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Wall top edge
    draw.line([(0, wall_y), (WIDTH, wall_y)], fill=(155, 138, 100), width=4)

    # Autumn persimmon tree branch — right side
    branch_pts = [(1420, 390), (1380, 440), (1350, 480), (1320, 520),
                  (1290, 490), (1270, 460)]
    for i in range(len(branch_pts) - 1):
        draw.line([branch_pts[i], branch_pts[i + 1]], fill=(72, 54, 38), width=5)
    # Sub-branches
    draw.line([(1350, 480), (1390, 510)], fill=(72, 54, 38), width=3)
    draw.line([(1320, 520), (1360, 545)], fill=(72, 54, 38), width=3)
    # Leaves — orange-red ovals
    leaf_positions = [(1300, 455), (1340, 475), (1360, 500), (1390, 465),
                      (1285, 478), (1370, 545), (1400, 540), (1310, 535)]
    for lx, ly in leaf_positions:
        draw.ellipse([(lx - 14, ly - 9), (lx + 14, ly + 9)],
                     fill=(195, 90, 35))
    # A few fallen leaves on the platform
    fallen = [(320, 700), (870, 712), (1250, 695), (480, 705)]
    for fx, fy in fallen:
        draw.ellipse([(fx - 10, fy - 6), (fx + 10, fy + 6)], fill=(178, 78, 28))


# ---------------------------------------------------------------------------
# Dried chili pepper rack
# ---------------------------------------------------------------------------

def draw_chili_rack(draw: ImageDraw.ImageDraw) -> None:
    """Dried red chili peppers hanging in braids on a wooden rack, left side."""
    rack_x = 55
    rack_top = 440
    rack_bot = 680
    # Rack post
    draw.rectangle([(rack_x, rack_top), (rack_x + 16, rack_bot)],
                   fill=(95, 72, 48))
    # Horizontal bar
    draw.rectangle([(rack_x - 10, rack_top + 5), (rack_x + 160, rack_top + 22)],
                   fill=(85, 65, 42))

    # Hanging braids of dried chilies
    braid_xs = [rack_x + 10, rack_x + 40, rack_x + 70, rack_x + 100, rack_x + 130]
    for bx in braid_xs:
        # String
        draw.line([(bx + 6, rack_top + 22), (bx + 6, rack_top + 220)],
                  fill=(95, 80, 55), width=2)
        # Chili peppers — elongated red teardrop shapes, 6-8 per braid
        for j in range(7):
            cy = rack_top + 40 + j * 26
            angle_offset = (j % 2) * 6 - 3
            cx = bx + angle_offset
            # Pepper body
            draw.ellipse([(cx - 4, cy - 12), (cx + 10, cy + 2)],
                         fill=(180, 40, 20))
            # Pepper tip
            draw.polygon([(cx + 3, cy + 2), (cx + 8, cy + 14), (cx - 2, cy + 2)],
                         fill=(165, 35, 18))
            # Pepper cap
            draw.ellipse([(cx - 1, cy - 14), (cx + 7, cy - 10)],
                         fill=(55, 80, 30))


# ---------------------------------------------------------------------------
# Onggi jars
# ---------------------------------------------------------------------------

def draw_onggi_jar(draw: ImageDraw.ImageDraw, cx: int, base_y: int,
                   width: int, height: int, color: tuple,
                   is_anchor: bool = False) -> None:
    """Draw a single onggi fermentation jar."""
    # Body — approximated as a polygon with rounded shoulders
    shoulder_w = int(width * 0.88)
    waist_w = int(width * 0.72)
    base_w = int(width * 0.62)
    shoulder_y = base_y - int(height * 0.80)
    neck_y = base_y - int(height * 0.92)
    base_y_bottom = base_y

    # Body polygon (simplified clay jar silhouette)
    body_pts = [
        (cx - base_w // 2, base_y_bottom),
        (cx - waist_w // 2, base_y - int(height * 0.30)),
        (cx - shoulder_w // 2, shoulder_y),
        (cx - int(width * 0.38), neck_y),
        (cx + int(width * 0.38), neck_y),
        (cx + shoulder_w // 2, shoulder_y),
        (cx + waist_w // 2, base_y - int(height * 0.30)),
        (cx + base_w // 2, base_y_bottom),
    ]
    draw.polygon(body_pts, fill=color)

    # Darker left shadow
    shadow_pts = [
        (cx - base_w // 2, base_y_bottom),
        (cx - waist_w // 2, base_y - int(height * 0.30)),
        (cx - shoulder_w // 2, shoulder_y),
        (cx - int(width * 0.38), neck_y),
        (cx - int(width * 0.20), neck_y),
        (cx - int(width * 0.18), shoulder_y),
        (cx - int(width * 0.12), base_y - int(height * 0.30)),
        (cx - int(width * 0.10), base_y_bottom),
    ]
    shadow_col = (max(0, color[0] - 28), max(0, color[1] - 22), max(0, color[2] - 18))
    draw.polygon(shadow_pts, fill=shadow_col)

    # Highlight streak
    highlight_pts = [
        (cx + int(width * 0.10), neck_y),
        (cx + int(width * 0.28), neck_y),
        (cx + int(width * 0.28), shoulder_y),
        (cx + int(width * 0.18), shoulder_y),
    ]
    hl_col = (min(255, color[0] + 22), min(255, color[1] + 18), min(255, color[2] + 14))
    draw.polygon(highlight_pts, fill=hl_col)

    # Coil texture lines
    coil_color = (max(0, color[0] - 15), max(0, color[1] - 12), max(0, color[2] - 10))
    for k in range(5):
        coil_y = shoulder_y + int((base_y_bottom - shoulder_y) * (k + 1) / 6)
        coil_w = int(shoulder_w * 0.85 - k * 8)
        draw.arc([(cx - coil_w // 2, coil_y - 6), (cx + coil_w // 2, coil_y + 6)],
                 start=5, end=175, fill=coil_color, width=2)

    # Lid
    lid_w = int(width * 0.52)
    lid_h = int(height * 0.10)
    lid_top = neck_y - lid_h
    lid_col = (max(0, color[0] - 35), max(0, color[1] - 28), max(0, color[2] - 20))
    draw.ellipse([(cx - lid_w // 2, lid_top), (cx + lid_w // 2, neck_y)],
                 fill=lid_col)
    # Lid knob
    draw.ellipse([(cx - 10, lid_top - 12), (cx + 10, lid_top + 4)],
                 fill=lid_col)

    # Anchor jar indicator: slightly different shoulder shape already handled by is_anchor
    if is_anchor:
        # Add a subtle groove mark on shoulder
        draw.arc(
            [(cx - shoulder_w // 2 + 4, shoulder_y - 8),
             (cx + shoulder_w // 2 - 4, shoulder_y + 8)],
            start=5, end=175,
            fill=(max(0, color[0] - 22), max(0, color[1] - 18), max(0, color[2] - 14)),
            width=3,
        )


def draw_onggi_rows(draw: ImageDraw.ImageDraw) -> None:
    """Draw three rows of onggi jars on the stone platform."""
    # Colors vary slightly — old fired clay in terracotta/umber tones
    jar_colors = [
        (142, 88, 58),
        (128, 76, 50),
        (155, 96, 62),
        (135, 82, 55),
        (148, 91, 60),
        (122, 74, 48),
        (160, 100, 65),
        (138, 86, 57),
    ]

    # Row 3 (back row, smaller, higher on canvas)
    back_row_y = 970
    back_w, back_h = 110, 260
    back_xs = [180, 340, 500, 660, 820, 980, 1140, 1300, 1430]
    for i, bx in enumerate(back_xs):
        jc = jar_colors[i % len(jar_colors)]
        draw_onggi_jar(draw, bx, back_row_y, back_w, back_h, jc)

    # Row 2 (middle row)
    mid_row_y = 1220
    mid_w, mid_h = 138, 330
    mid_xs = [150, 330, 510, 690, 870, 1050, 1230, 1420]
    for i, mx in enumerate(mid_xs):
        is_anc = (i == 2)  # anchor jar: 3rd from left = index 2
        jc = jar_colors[(i + 3) % len(jar_colors)]
        draw_onggi_jar(draw, mx, mid_row_y, mid_w, mid_h, jc, is_anchor=is_anc)

    # Row 1 (front row, largest, lowest on canvas)
    front_row_y = 1530
    front_w, front_h = 165, 400
    front_xs = [170, 380, 590, 800, 1010, 1220, 1430]
    for i, fx in enumerate(front_xs):
        jc = jar_colors[(i + 1) % len(jar_colors)]
        draw_onggi_jar(draw, fx, front_row_y, front_w, front_h, jc)


# ---------------------------------------------------------------------------
# Woman's hands on jar lid
# ---------------------------------------------------------------------------

def draw_hands_on_jar(draw: ImageDraw.ImageDraw) -> None:
    """Draw a pair of aged hands resting on the lid of the foreground anchor jar."""
    # The prominent foreground jar: center around x=590 in row 1, lid at approximately y=1143
    jar_cx = 590
    lid_y = 1530 - 400 + int(400 * 0.08) - 12  # lid top of front row jar index 1
    # Approximate lid top for front row jar at cx=590: base_y=1530, height=400
    # neck_y = 1530 - int(400*0.92) = 1530 - 368 = 1162
    # lid_h = int(400*0.10) = 40, lid_top = 1162 - 40 = 1122
    lid_center_y = 1122 + 20  # center of lid ellipse

    # Skin tone — aged Korean woman's hands
    skin = (195, 148, 110)
    skin_shadow = (168, 120, 85)
    skin_dark = (142, 98, 68)

    # Left hand — fingers spread slightly over lid surface
    # Palm
    draw.ellipse([(jar_cx - 90, lid_center_y - 22),
                  (jar_cx + 10, lid_center_y + 28)],
                 fill=skin)
    # Thumb
    draw.ellipse([(jar_cx - 98, lid_center_y - 12),
                  (jar_cx - 68, lid_center_y + 18)],
                 fill=skin)
    # Fingers (4)
    finger_starts = [
        (jar_cx - 72, lid_center_y - 22),
        (jar_cx - 52, lid_center_y - 28),
        (jar_cx - 32, lid_center_y - 28),
        (jar_cx - 12, lid_center_y - 22),
    ]
    for i, (fx, fy) in enumerate(finger_starts):
        flen = 52 - i * 4
        draw.ellipse([(fx - 10, fy - flen), (fx + 10, fy + 6)], fill=skin)
    # Shadow under hand
    draw.ellipse([(jar_cx - 88, lid_center_y + 14),
                  (jar_cx + 8, lid_center_y + 30)],
                 fill=skin_shadow)
    # Knuckle wrinkle lines
    for i, (fx, fy) in enumerate(finger_starts):
        flen = 52 - i * 4
        draw.line([(fx - 8, fy - flen // 2), (fx + 8, fy - flen // 2)],
                  fill=skin_dark, width=1)

    # Right hand — resting alongside
    rh_cx = jar_cx + 52
    draw.ellipse([(rh_cx - 10, lid_center_y - 22),
                  (rh_cx + 80, lid_center_y + 28)],
                 fill=skin)
    # Thumb
    draw.ellipse([(rh_cx + 70, lid_center_y - 10),
                  (rh_cx + 95, lid_center_y + 18)],
                 fill=skin)
    # Fingers
    finger_starts_r = [
        (rh_cx + 60, lid_center_y - 22),
        (rh_cx + 42, lid_center_y - 27),
        (rh_cx + 24, lid_center_y - 27),
        (rh_cx + 6, lid_center_y - 22),
    ]
    for i, (fx, fy) in enumerate(finger_starts_r):
        flen = 50 - i * 4
        draw.ellipse([(fx - 9, fy - flen), (fx + 9, fy + 6)], fill=skin)
    draw.ellipse([(rh_cx - 8, lid_center_y + 14),
                  (rh_cx + 78, lid_center_y + 30)],
                 fill=skin_shadow)


# ---------------------------------------------------------------------------
# Afternoon light overlay
# ---------------------------------------------------------------------------

def apply_afternoon_light(image: Image.Image) -> Image.Image:
    """Warm golden light wash over the art zone."""
    overlay = Image.new("RGBA", (WIDTH, ART_HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    # Warm light from upper right
    for step in range(40):
        alpha = int(18 - step * 0.4)
        if alpha <= 0:
            break
        od.ellipse(
            [(WIDTH - 300 - step * 30, -150 - step * 20),
             (WIDTH + 200 + step * 20, 600 + step * 30)],
            fill=(255, 220, 140, alpha),
        )
    art_zone = image.crop((0, 0, WIDTH, ART_HEIGHT)).convert("RGBA")
    art_zone = Image.alpha_composite(art_zone, overlay)
    result = image.copy()
    result.paste(art_zone.convert("RGB"), (0, 0))
    return result


# ---------------------------------------------------------------------------
# Main create_cover function
# ---------------------------------------------------------------------------

def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Fermentation Master")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (190, 175, 140))
    draw = ImageDraw.Draw(image)

    # Build the art scene
    draw_sky(draw)
    draw_hanok_roofline(draw)
    draw_foliage(draw)
    draw_ground(draw)
    draw_chili_rack(draw)
    draw_onggi_rows(draw)
    draw_hands_on_jar(draw)

    # Apply atmospheric light
    image = apply_afternoon_light(image)

    # Slight warm blur on background elements for depth
    bg = image.crop((0, 0, WIDTH, 440))
    bg = bg.filter(ImageFilter.GaussianBlur(radius=1.2))
    image.paste(bg, (0, 0))

    # Draw the standard title/author panel at the bottom
    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers (required by project convention)
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)

if __name__ == "__main__":
    main()
