#!/usr/bin/env python3
"""Cover: The Winter Garden — Winter walled garden, dove-to-slate sky, bare trees flanking brick wall with iron gate, frost-sprinkled path."""

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



ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Dove gray to winter blue gradient for the winter garden feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((180, 185, 190), (140, 155, 170), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((140, 155, 170), (100, 120, 140), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((100, 120, 140), (60, 75, 90), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_garden_wall(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a brick wall across the mid-section of the cover."""
    wall_y = int(height * 0.35)
    wall_h = 160

    # Wall body
    draw.rectangle([(0, wall_y), (width, wall_y + wall_h)], fill=(120, 90, 70))

    # Brick lines
    brick_h = 20
    brick_w = 60
    for row in range(wall_h // brick_h):
        y = wall_y + row * brick_h
        offset = (row % 2) * (brick_w // 2)
        for col in range(-1, (width // brick_w) + 2):
            x = col * brick_w + offset
            shade = 5 if random.random() < 0.3 else -5
            draw.rectangle(
                [(x, y), (x + brick_w - 2, y + brick_h - 2)],
                fill=(125 + shade, 95 + shade, 75 + shade),
                outline=(100, 75, 55),
            )

    # Wall cap
    draw.rectangle([(0, wall_y - 8), (width, wall_y)], fill=(100, 75, 55))
    draw.rectangle([(0, wall_y - 12), (width, wall_y - 8)], fill=(130, 100, 80))

    # Frost on wall top
    for x in range(0, width, 3):
        fh = random.randint(1, 4)
        draw.line([(x, wall_y - 12 - fh), (x, wall_y - 12)], fill=(220, 230, 240, 80))


def draw_gate(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an iron gate in the centre of the wall."""
    gate_cx = width // 2
    wall_y = int(height * 0.35)
    gate_w = 160
    gate_h = 140

    # Gate opening (dark)
    draw.rectangle(
        [(gate_cx - gate_w // 2, wall_y - 8), (gate_cx + gate_w // 2, wall_y + gate_h)],
        fill=(30, 35, 40),
    )

    # Iron gate bars
    bar_color = (50, 55, 60)
    # Vertical bars
    for i in range(7):
        x = gate_cx - gate_w // 2 + 10 + i * 23
        draw.line([(x, wall_y - 8), (x, wall_y + gate_h)], fill=bar_color, width=3)

    # Horizontal bars
    for i in range(4):
        y = wall_y - 8 + i * 35
        draw.line(
            [(gate_cx - gate_w // 2 + 8, y), (gate_cx + gate_w // 2 - 8, y)],
            fill=bar_color,
            width=2,
        )

    # Gate arch
    draw.arc(
        [(gate_cx - gate_w // 2, wall_y - 80), (gate_cx + gate_w // 2, wall_y - 8)],
        0, 180, fill=bar_color, width=3,
    )


def draw_bare_trees(draw: ImageDraw, width: int, height: int) -> None:
    """Draw bare winter trees flanking the wall."""
    rng = random.Random(17)

    positions = [
        (80, int(height * 0.28)),
        (200, int(height * 0.25)),
        (width - 80, int(height * 0.27)),
        (width - 200, int(height * 0.23)),
        (140, int(height * 0.32)),
        (width - 140, int(height * 0.30)),
    ]

    for tx, ty in positions:
        trunk_h = rng.randint(180, 280)
        trunk_w = rng.randint(8, 14)

        # Trunk
        color = (45, 35, 30)
        draw.rectangle([tx - trunk_w // 2, ty - trunk_h, tx + trunk_w // 2, ty], fill=color)

        # Main branches
        for angle in range(-60, 70, 25):
            branch_len = rng.randint(40, 100)
            bx = tx + int(branch_len * math.sin(math.radians(angle)))
            by = ty - trunk_h + rng.randint(30, trunk_h - 40)
            draw.line([(tx, by), (bx, by - 30)], fill=color, width=rng.randint(2, 5))

            # Sub-branches
            sub_angle = angle + rng.randint(-20, 20)
            sub_len = rng.randint(15, 35)
            sx = bx + int(sub_len * math.sin(math.radians(sub_angle)))
            sy = by - 30 + rng.randint(-10, 10)
            draw.line([(bx, by - 30), (sx, sy)], fill=color, width=rng.randint(1, 2))

        # Fine twigs
        for _ in range(8):
            start_x = tx + rng.randint(-40, 40)
            start_y = ty - trunk_h + rng.randint(10, trunk_h - 20)
            end_x = start_x + rng.randint(-50, 50)
            end_y = start_y - rng.randint(20, 60)
            draw.line([(start_x, start_y), (end_x, end_y)], fill=(60, 50, 45), width=1)


def draw_holly_branches(draw: ImageDraw, width: int, height: int) -> None:
    """Draw holly branches with red berries at the edges."""
    rng = random.Random(42)

    # Left side holly
    for i in range(4):
        start_x = rng.randint(-30, 60)
        start_y = rng.randint(int(height * 0.2), int(height * 0.55))
        end_x = start_x + rng.randint(80, 150)
        end_y = start_y - rng.randint(10, 60)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(40, 60, 30), width=3)

        # Holly leaves (simple ovals)
        for lf in range(4):
            lx = start_x + (end_x - start_x) * (lf / 4) + rng.randint(-5, 5)
            ly = start_y + (end_y - start_y) * (lf / 4) + rng.randint(-5, 5)
            draw.ellipse([lx - 6, ly - 4, lx + 6, ly + 4], fill=(30, 70, 25))
            # Red berry
            draw.ellipse([lx + 8, ly - 3, lx + 14, ly + 3], fill=(180, 20, 20))

    # Right side holly
    for i in range(4):
        start_x = width - rng.randint(-30, 60)
        start_y = rng.randint(int(height * 0.2), int(height * 0.55))
        end_x = start_x - rng.randint(80, 150)
        end_y = start_y - rng.randint(10, 60)
        draw.line([(start_x, start_y), (end_x, end_y)], fill=(40, 60, 30), width=3)

        for lf in range(4):
            lx = start_x + (end_x - start_x) * (lf / 4) + rng.randint(-5, 5)
            ly = start_y + (end_y - start_y) * (lf / 4) + rng.randint(-5, 5)
            draw.ellipse([lx - 6, ly - 4, lx + 6, ly + 4], fill=(30, 70, 25))
            draw.ellipse([lx - 14, ly - 3, lx - 8, ly + 3], fill=(180, 20, 20))


def draw_frost_effects(draw: ImageDraw, width: int, height: int) -> None:
    """Add frost and snow particle effects."""
    rng = random.Random(31)

    # Frost crystals on ground
    ground_y = int(height * 0.35) + 160
    for _ in range(200):
        x = rng.randint(0, width)
        y = rng.randint(ground_y, int(height * 0.45))
        size = rng.randint(1, 3)
        draw.ellipse([x, y, x + size, y + size], fill=(220, 230, 240, rng.randint(60, 150)))

    # Falling snow particles
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.6))
        size = rng.randint(1, 4)
        alpha = rng.randint(100, 200)
        draw.ellipse([x, y, x + size, y + size], fill=(240, 245, 250, alpha))


def draw_path(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a garden path leading from the gate toward the viewer."""
    gate_cx = width // 2
    wall_y = int(height * 0.35) + 160

    # Path widening as it approaches viewer
    path_points = [
        (gate_cx - 25, wall_y),
        (gate_cx + 25, wall_y),
        (gate_cx + 120, HEIGHT),
        (gate_cx - 120, HEIGHT),
    ]
    draw.polygon(path_points, fill=(150, 140, 130))

    # Path stones
    rng = random.Random(53)
    for y in range(wall_y, HEIGHT, 30):
        x_range = 25 + (y - wall_y) * 95 / (HEIGHT - wall_y)
        cx = gate_cx
        for _ in range(3):
            sx = cx + rng.randint(-int(x_range), int(x_range))
            sy = y + rng.randint(-8, 8)
            draw.ellipse(
                [sx - rng.randint(8, 18), sy - 4, sx + rng.randint(8, 18), sy + 4],
                fill=(160, 150, 140),
            )

    # Frost on path edges
    for _ in range(60):
        ex = gate_cx + rng.randint(-160, 160)
        ey = rng.randint(wall_y, HEIGHT)
        draw.ellipse([ex, ey, ex + 3, ey + 3], fill=(200, 210, 220, rng.randint(40, 100)))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom of the cover with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(25, 30, 40))

    # Subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 70, 85), width=2)

    # Holly berry decorative line at panel top
    for x in range(60, width - 60, 40):
        draw.ellipse([x - 3, panel_top + 15, x + 3, panel_top + 21], fill=(160, 20, 20))

    # Title text — use arialbd.ttf, WHITE
    title = "The Winter\nGarden"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 55
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

    # Author name — smaller, WHITE
    author = "Barış Kısır"
    author_font_size = 38
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = panel_top + 260
    draw.text((ax, ay), author, fill=(220, 225, 230), font=author_font)

    # Small decorative line below author
    dec_line_y = ay + 45
    dec_line_w = 80
    draw.line(
        [(width // 2 - dec_line_w // 2, dec_line_y), (width // 2 + dec_line_w // 2, dec_line_y)],
        fill=(160, 20, 20),
        width=1,
    )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Winter Garden")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    for y in range(HEIGHT):
        if y < HEIGHT * 0.4:
            t = y / (HEIGHT * 0.4)
            c = lerp_color((180, 185, 190), (140, 155, 170), t)
        elif y < HEIGHT * 0.7:
            t = (y - HEIGHT * 0.4) / (HEIGHT * 0.3)
            c = lerp_color((140, 155, 170), (100, 120, 140), t)
        else:
            t = (y - HEIGHT * 0.7) / (HEIGHT * 0.3)
            c = lerp_color((100, 120, 140), (60, 75, 90), t)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    rng_trees = random.Random(17)
    for tx, ty in [(80, int(HEIGHT * 0.28)), (200, int(HEIGHT * 0.25)), (WIDTH - 80, int(HEIGHT * 0.27)), (WIDTH - 200, int(HEIGHT * 0.23))]:
        th = rng_trees.randint(180, 280)
        draw.line([(tx, ty), (tx, ty - th)], fill=(45, 35, 30), width=rng_trees.randint(8, 14))
        for a in range(-60, 70, 25):
            bl = rng_trees.randint(40, 100)
            bx = tx + int(bl * math.sin(math.radians(a)))
            by = ty - th + rng_trees.randint(30, th - 40)
            draw.line([(tx, by), (bx, by - 30)], fill=(45, 35, 30), width=rng_trees.randint(2, 5))

    wall_y = int(HEIGHT * 0.35)
    wall_h = 160
    draw.rectangle([(0, wall_y), (WIDTH, wall_y + wall_h)], fill=(120, 90, 70))
    for row in range(wall_h // 20):
        y = wall_y + row * 20
        offset = (row % 2) * 30
        for col in range(-1, (WIDTH // 60) + 2):
            x = col * 60 + offset
            draw.rectangle([(x, y), (x + 58, y + 18)], fill=(125, 95, 75), outline=(100, 75, 55))
    draw.rectangle([(0, wall_y - 8), (WIDTH, wall_y)], fill=(100, 75, 55))

    gate_cx = WIDTH // 2
    gate_w = 160
    draw.rectangle([(gate_cx - gate_w // 2, wall_y - 8), (gate_cx + gate_w // 2, wall_y + wall_h)], fill=(30, 35, 40))
    for i in range(7):
        gx = gate_cx - gate_w // 2 + 10 + i * 23
        draw.line([(gx, wall_y - 8), (gx, wall_y + wall_h)], fill=(50, 55, 60), width=3)

    rng_frost = random.Random(31)
    ground_y = wall_y + wall_h
    for _ in range(200):
        fx = rng_frost.randint(0, WIDTH)
        fy = rng_frost.randint(ground_y, int(HEIGHT * 0.45))
        fs = rng_frost.randint(1, 3)
        draw.ellipse([fx, fy, fx + fs, fy + fs], fill=(220, 230, 240, rng_frost.randint(60, 150)))

    for _ in range(80):
        sx = rng_frost.randint(0, WIDTH)
        sy = rng_frost.randint(0, int(HEIGHT * 0.6))
        ss = rng_frost.randint(1, 3)
        draw.ellipse([sx, sy, sx + ss, sy + ss], fill=(240, 245, 250, rng_frost.randint(100, 200)))

    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()