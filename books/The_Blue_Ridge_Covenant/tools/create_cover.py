#!/usr/bin/env python3
"""
Create the cover image for The Blue Ridge Covenant.

Scene: A forested Appalachian mountain hollow at twilight. A dirt road leads
into dark woods; a farmhouse amber light is barely visible deep in the trees.
At the treeline, a lone figure silhouette stands looking outward. The sky is
deep blue-gray with low clouds. Bare ridge-line trees are dark against the
fading sky. Fog gathers in the valley below.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 1600
HEIGHT = 2560
ARTWORK_HEIGHT = 1765  # upper 65% approx


def draw_sky(draw: ImageDraw.ImageDraw) -> None:
    """Gradient sky: deep twilight blue-gray at top, warm dark amber at horizon."""
    sky_bottom = int(ARTWORK_HEIGHT * 0.45)
    for y in range(sky_bottom):
        t = y / sky_bottom
        # Top: deep blue-gray (25,30,45) -> horizon: warm steel-gray (65,60,70)
        r = int(25 + (65 - 25) * t)
        g = int(30 + (60 - 30) * t)
        b = int(45 + (70 - 45) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_fog_valley(draw: ImageDraw.ImageDraw) -> None:
    """Low fog filling the valley floor — pale blue-white wisps."""
    fog_top = int(ARTWORK_HEIGHT * 0.72)
    fog_bottom = int(ARTWORK_HEIGHT * 0.88)
    rng = random.Random(42)
    for _ in range(180):
        x = rng.randint(-80, WIDTH + 80)
        y = rng.randint(fog_top, fog_bottom)
        rx = rng.randint(120, 380)
        ry = rng.randint(20, 55)
        alpha = rng.randint(28, 68)
        # Draw ellipses as fog wisps
        draw.ellipse(
            [(x - rx, y - ry), (x + rx, y + ry)],
            fill=(200, 210, 220, alpha),
        )


def draw_background_mountains(draw: ImageDraw.ImageDraw) -> None:
    """Distant Blue Ridge ridgelines — dark blue-gray silhouettes layered."""
    horizon_y = int(ARTWORK_HEIGHT * 0.44)

    # Far ridge (lighter, more blue)
    far_ridge = []
    rng = random.Random(7)
    x = 0
    while x <= WIDTH:
        y = horizon_y + rng.randint(-55, 20)
        far_ridge.append((x, y))
        x += rng.randint(30, 80)
    far_ridge.append((WIDTH, horizon_y + 10))
    far_ridge.append((WIDTH, ARTWORK_HEIGHT))
    far_ridge.append((0, ARTWORK_HEIGHT))
    draw.polygon(far_ridge, fill=(48, 55, 72))

    # Mid ridge (darker, more gray)
    mid_ridge = []
    rng2 = random.Random(13)
    x = 0
    while x <= WIDTH:
        y = horizon_y + rng2.randint(25, 110)
        mid_ridge.append((x, y))
        x += rng2.randint(20, 60)
    mid_ridge.append((WIDTH, horizon_y + 60))
    mid_ridge.append((WIDTH, ARTWORK_HEIGHT))
    mid_ridge.append((0, ARTWORK_HEIGHT))
    draw.polygon(mid_ridge, fill=(38, 44, 55))


def draw_ridge_bare_trees(draw: ImageDraw.ImageDraw) -> None:
    """Bare deciduous trees along the upper ridge line — dark silhouettes."""
    horizon_y = int(ARTWORK_HEIGHT * 0.44)
    rng = random.Random(99)

    def draw_bare_tree(cx: int, base_y: int, height: int, spread: float) -> None:
        trunk_top = base_y - height
        # Trunk
        tw = max(2, height // 28)
        draw.line([(cx, base_y), (cx, trunk_top)], fill=(18, 18, 22), width=tw)
        # Branches — recursive-ish with a fixed depth
        branches = [(cx, trunk_top, 0, -1, height * 0.42)]
        for _ in range(3):
            new_branches = []
            for bx, by, dx, dy, length in branches:
                if length < 6:
                    continue
                for angle_offset in (-0.4, 0.0, 0.4):
                    angle = math.atan2(dy, dx) + angle_offset + rng.uniform(-0.12, 0.12)
                    nl = length * rng.uniform(0.55, 0.7)
                    ex = int(bx + math.cos(angle) * nl * spread)
                    ey = int(by + math.sin(angle) * nl)
                    w = max(1, int(nl // 14))
                    draw.line([(bx, by), (ex, ey)], fill=(18, 18, 22), width=w)
                    new_branches.append((ex, ey, math.cos(angle), math.sin(angle), nl))
            branches = new_branches

    # Place trees along the ridge line
    x_positions = [50, 130, 240, 340, 480, 600, 730, 870, 990, 1120, 1260, 1380, 1500, 1580]
    for x in x_positions:
        h = rng.randint(90, 190)
        base_y = horizon_y + rng.randint(10, 55)
        draw_bare_tree(x, base_y, h, rng.uniform(0.85, 1.1))


def draw_dark_forest(draw: ImageDraw.ImageDraw) -> None:
    """Dense dark forest filling the lower two-thirds of the artwork area."""
    forest_top = int(ARTWORK_HEIGHT * 0.44)
    # Base forest fill — very dark green-black
    draw.rectangle([(0, forest_top), (WIDTH, ARTWORK_HEIGHT)], fill=(14, 22, 18))

    rng = random.Random(55)

    # Draw layered tree silhouettes: conifers (hemlocks) and deciduous
    def draw_hemlock(cx: int, base_y: int, height: int) -> None:
        """Triangular hemlock shape."""
        layers = 6
        for i in range(layers):
            t = i / layers
            layer_y = base_y - int(height * t)
            half_w = int(height * 0.28 * (1 - t * 0.75))
            pts = [
                (cx - half_w, layer_y),
                (cx + half_w, layer_y),
                (cx, layer_y - int(height * 0.18)),
            ]
            shade = rng.randint(8, 22)
            draw.polygon(pts, fill=(shade, shade + 10, shade + 6))

    def draw_oak_mass(cx: int, base_y: int, height: int) -> None:
        """Rounded deciduous tree mass."""
        cr = int(height * 0.38)
        cy = base_y - int(height * 0.68)
        shade = rng.randint(10, 24)
        draw.ellipse(
            [(cx - cr, cy - cr // 2), (cx + cr, cy + cr // 2)],
            fill=(shade, shade + 8, shade + 4),
        )
        # Trunk
        draw.rectangle(
            [(cx - 5, base_y - int(height * 0.35)), (cx + 5, base_y)],
            fill=(12, 14, 12),
        )

    # Background tree layer
    for i in range(60):
        x = rng.randint(0, WIDTH)
        base_y = rng.randint(int(ARTWORK_HEIGHT * 0.50), int(ARTWORK_HEIGHT * 0.68))
        h = rng.randint(120, 260)
        if rng.random() < 0.55:
            draw_hemlock(x, base_y, h)
        else:
            draw_oak_mass(x, base_y, h)

    # Midground tree layer — darker, larger
    for i in range(40):
        x = rng.randint(-40, WIDTH + 40)
        base_y = rng.randint(int(ARTWORK_HEIGHT * 0.60), int(ARTWORK_HEIGHT * 0.80))
        h = rng.randint(200, 400)
        if rng.random() < 0.5:
            draw_hemlock(x, base_y, h)
        else:
            draw_oak_mass(x, base_y, h)

    # Foreground tree trunks — massive, close
    fg_trees = [(-60, 50), (120, 80), (320, 60), (700, 90), (1050, 70), (1350, 80), (1620, 55)]
    for cx, trunk_w in fg_trees:
        base_y = ARTWORK_HEIGHT
        top_y = rng.randint(int(ARTWORK_HEIGHT * 0.22), int(ARTWORK_HEIGHT * 0.42))
        draw.rectangle([(cx - trunk_w // 2, top_y), (cx + trunk_w // 2, base_y)], fill=(8, 10, 8))
        # Canopy suggestion at top
        cr = rng.randint(80, 160)
        shade = rng.randint(10, 20)
        draw.ellipse(
            [(cx - cr, top_y - cr // 2), (cx + cr, top_y + cr // 2)],
            fill=(shade, shade + 6, shade + 3),
        )


def draw_dirt_road(draw: ImageDraw.ImageDraw) -> None:
    """A dirt road receding into the dark forest — perspective converging to center."""
    # Road vanishing point: center-left of artwork, about 55% down
    vp_x = WIDTH // 2 - 60
    vp_y = int(ARTWORK_HEIGHT * 0.55)

    # Road edges — perspective lines from bottom corners to vanishing point
    road_left_bottom = (int(WIDTH * 0.28), ARTWORK_HEIGHT)
    road_right_bottom = (int(WIDTH * 0.72), ARTWORK_HEIGHT)

    # Build road polygon
    road_pts = [
        road_left_bottom,
        road_right_bottom,
        (vp_x + 18, vp_y),
        (vp_x - 18, vp_y),
    ]
    draw.polygon(road_pts, fill=(52, 42, 34))

    # Road texture: ruts and shadows
    rng = random.Random(77)
    for _ in range(22):
        t = rng.uniform(0.1, 0.95)
        lx = int(road_left_bottom[0] + (vp_x - 18 - road_left_bottom[0]) * t)
        rx = int(road_right_bottom[0] + (vp_x + 18 - road_right_bottom[0]) * t)
        y = int(ARTWORK_HEIGHT + (vp_y - ARTWORK_HEIGHT) * t)
        shade = rng.randint(35, 58)
        draw.line([(lx, y), (rx, y)], fill=(shade, shade - 8, shade - 14), width=1)

    # Central grass strip between ruts
    strip_pts = [
        (int((road_left_bottom[0] + road_right_bottom[0]) / 2 - 55), ARTWORK_HEIGHT),
        (int((road_left_bottom[0] + road_right_bottom[0]) / 2 + 55), ARTWORK_HEIGHT),
        (vp_x + 4, vp_y + 10),
        (vp_x - 4, vp_y + 10),
    ]
    draw.polygon(strip_pts, fill=(22, 34, 20))


def draw_farmhouse_light(draw: ImageDraw.ImageDraw) -> None:
    """A faint amber farmhouse light barely visible deep in the dark forest."""
    # The light is subtle — a warm glow deep in the trees, center-right
    lx = int(WIDTH * 0.62)
    ly = int(ARTWORK_HEIGHT * 0.60)

    # Glow layers — large to small, very transparent
    for radius, alpha in [(90, 18), (55, 30), (30, 50), (14, 80), (6, 130)]:
        draw.ellipse(
            [(lx - radius, ly - radius), (lx + radius, ly + radius)],
            fill=(200, 150, 60, alpha),
        )

    # Window shape — tiny rectangle of warm amber
    draw.rectangle([(lx - 5, ly - 7), (lx + 5, ly + 7)], fill=(230, 180, 80))


def draw_figure_silhouette(draw: ImageDraw.ImageDraw) -> None:
    """A lone figure standing at the treeline, looking outward."""
    # Figure stands at the edge of the road where it meets the forest
    fx = int(WIDTH * 0.47)
    fy = int(ARTWORK_HEIGHT * 0.665)
    fig_h = 52  # figure height in pixels
    fig_w = 14

    # Body
    draw.rectangle(
        [(fx - fig_w // 2, fy - fig_h), (fx + fig_w // 2, fy)],
        fill=(8, 8, 10),
    )
    # Head
    head_r = 9
    draw.ellipse(
        [(fx - head_r, fy - fig_h - head_r * 2), (fx + head_r, fy - fig_h)],
        fill=(8, 8, 10),
    )
    # Suggestion of duffel bag or pack on one shoulder
    draw.ellipse(
        [(fx + fig_w // 2 - 2, fy - fig_h + 8), (fx + fig_w // 2 + 14, fy - fig_h + 24)],
        fill=(10, 10, 12),
    )


def draw_low_clouds(draw: ImageDraw.ImageDraw) -> None:
    """Low storm clouds across the upper sky."""
    rng = random.Random(33)
    cloud_y_center = int(ARTWORK_HEIGHT * 0.18)
    for _ in range(12):
        cx = rng.randint(0, WIDTH)
        cy = rng.randint(cloud_y_center - 80, cloud_y_center + 60)
        rx = rng.randint(200, 500)
        ry = rng.randint(40, 100)
        alpha = rng.randint(20, 50)
        draw.ellipse(
            [(cx - rx, cy - ry), (cx + rx, cy + ry)],
            fill=(55, 58, 72, alpha),
        )


def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Blue Ridge Covenant")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    # Use RGBA for compositing fog and glow layers
    image = Image.new("RGBA", (WIDTH, HEIGHT), (20, 25, 30, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    # Build scene from back to front
    draw_sky(draw)
    draw_low_clouds(draw)
    draw_background_mountains(draw)
    draw_ridge_bare_trees(draw)
    draw_dark_forest(draw)
    draw_dirt_road(draw)
    draw_farmhouse_light(draw)
    draw_fog_valley(draw)
    draw_figure_silhouette(draw)

    # Slight blur on the overall artwork to soften edges and unify the scene
    art_crop = image.crop((0, 0, WIDTH, ARTWORK_HEIGHT))
    art_crop = art_crop.filter(ImageFilter.GaussianBlur(radius=1.2))
    image.paste(art_crop, (0, 0))

    # Convert to RGB for the title panel (which uses solid colors)
    image = image.convert("RGB")

    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    image.save(out_path, "PNG")
    print(f"Cover saved to {out_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers (required by project convention)
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
    draw.rectangle((0, py, 1600, 2560), fill=(12, 10, 8, 255))
    draw.line((180, py + 17, 1420, py + 17), fill=(120, 140, 195, 125), width=3)
    title_font, lines, gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 52)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in lines) + max(0, len(lines) - 1) * gap
    author_height = draw.textbbox((0, 0), author, font=author_font)[3] - draw.textbbox((0, 0), author, font=author_font)[1]
    y = py + 120 + max(0, (2560 - py - 230 - (title_height + 118 + author_height)) // 2)
    y = _standard_cover_center(draw, y, lines, title_font, (220, 215, 200), gap, 1600) + 118
    _standard_cover_center(draw, y, [author], author_font, (180, 170, 160), 12, 1600)
    if model:
        model_font = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, 2560 - 110, [model], model_font, (130, 120, 140), 12, 1600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cover for The Blue Ridge Covenant")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    create_cover(args.metadata, args.out)
