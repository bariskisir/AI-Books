#!/usr/bin/env python3
"""Generate cover image for The Street of Many Doors."""

import argparse
import json
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


WIDTH, HEIGHT = 1600, 2560
FONT_PATH = "arialbd.ttf"
FONT_FALLBACK = "arial.ttf"


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))  # type: ignore


def draw_gradient(draw: ImageDraw, top_color: tuple, bottom_color: tuple) -> None:
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = lerp_color(top_color, bottom_color, t)
        draw.line([(0, y), (WIDTH, y)], fill=color)


def draw_street(draw: ImageDraw) -> None:
    """Draw cobblestone street at the bottom-center of the cover."""
    street_y_start = 900
    # Dark grey street area
    draw.rectangle([(0, street_y_start), (WIDTH, HEIGHT)], fill=(45, 40, 35))

    # Cobblestones
    stone_color = (60, 55, 50)
    highlight = (70, 65, 60)
    cy = street_y_start + 20
    while cy < HEIGHT:
        cx = 20
        row_offset = 40 if (cy // 50) % 2 else 0
        while cx < WIDTH - 20:
            stone_w = 60 + (cy % 20)
            stone_h = 28 + (cy % 10)
            draw.ellipse(
                [(cx + row_offset, cy), (cx + row_offset + stone_w, cy + stone_h)],
                fill=stone_color, outline=highlight
            )
            cx += stone_w + 8
        cy += 38


def draw_building_facade(draw: ImageDraw) -> None:
    """Draw the building wall where doors will be placed."""
    # Building wall
    wall_color = (185, 165, 140)
    draw.rectangle([(0, 0), (WIDTH, 1000)], fill=(195, 175, 150))

    # Windows on upper floors
    for row in range(3):
        for col in range(5):
            wx = 150 + col * 310
            wy = 80 + row * 220
            # Window frame
            draw.rectangle([(wx, wy), (wx + 180, wy + 140)], fill=(80, 75, 90))
            # Window pane glow
            draw.rectangle([(wx + 8, wy + 8), (wx + 172, wy + 132)], fill=(210, 195, 140))
            # Window cross
            draw.line([(wx + 90, wy + 8), (wx + 90, wy + 132)], fill=(70, 65, 60), width=3)
            draw.line([(wx + 8, wy + 70), (wx + 172, wy + 70)], fill=(70, 65, 60), width=3)
            # Arch top
            draw.arc([(wx, wy - 10), (wx + 180, wy + 20)], 180, 0, fill=(80, 75, 90), width=4)


def draw_doors(draw: ImageDraw) -> None:
    """Draw a row of colorful doors on the street."""
    door_colors = [
        (30, 80, 160),   # Blue
        (50, 130, 70),   # Green
        (170, 40, 40),   # Red
        (40, 40, 40),    # Black
        (200, 170, 40),  # Yellow
        (140, 100, 60),  # Iron / brown
        (180, 200, 210), # Glass / light blue
        (130, 90, 50),   # Worn wood
        (180, 120, 60),  # Terracotta
        (80, 60, 120),   # Purple
    ]

    door_w = 110
    door_h = 250
    start_x = 60
    y = 720

    for i, color in enumerate(door_colors):
        x = start_x + i * (door_w + 35)

        # Door shadow
        draw.rectangle([(x + 4, y + 4), (x + door_w + 4, y + door_h + 4)], fill=(30, 25, 20))

        # Door body
        draw.rectangle([(x, y), (x + door_w, y + door_h)], fill=color)

        # Door panels
        panel_color = tuple(max(0, c - 30) for c in color)
        # Top panel
        draw.rectangle([(x + 12, y + 15), (x + door_w - 12, y + 90)], fill=panel_color, outline=None)
        # Bottom panel
        draw.rectangle([(x + 12, y + 105), (x + door_w - 12, y + door_h - 15)], fill=panel_color, outline=None)

        # Door handle
        handle_color = (200, 180, 100) if i % 2 == 0 else (180, 150, 80)
        draw.ellipse(
            [(x + door_w - 22, y + door_h // 2 - 5), (x + door_w - 14, y + door_h // 2 + 5)],
            fill=handle_color, outline=(100, 90, 60), width=1
        )

        # Arch top for every other door
        if i % 2 == 0:
            draw.arc([(x - 2, y - 30), (x + door_w + 2, y + 10)], 180, 0, fill=color, width=8)
            # Keystone
            ks_x = x + door_w // 2
            draw.polygon([(ks_x - 8, y - 30), (ks_x + 8, y - 30), (ks_x, y - 42)], fill=(160, 150, 130))


def draw_cafe(draw: ImageDraw) -> None:
    """Draw a small cafe awning and table on the right side."""
    # Awning
    awning_x = 1200
    awning_y = 550
    draw.rectangle([(awning_x, awning_y), (awning_x + 350, awning_y + 60)], fill=(160, 50, 50))
    # Awning stripes
    for s in range(7):
        sx = awning_x + s * 50
        draw.rectangle([(sx, awning_y), (sx + 25, awning_y + 60)], fill=(200, 180, 150))

    # Cafe table
    table_x = awning_x + 100
    table_y = awning_y + 100
    draw.ellipse([(table_x, table_y), (table_x + 70, table_y + 10)], fill=(80, 75, 70))
    draw.line([(table_x + 10, table_y + 10), (table_x + 10, table_y + 40)], fill=(60, 55, 50), width=4)
    draw.line([(table_x + 60, table_y + 10), (table_x + 60, table_y + 40)], fill=(60, 55, 50), width=4)

    # Chair silhouette
    chair_x = table_x + 85
    chair_y = table_y - 5
    draw.rectangle([(chair_x, chair_y), (chair_x + 35, chair_y + 35)], fill=(50, 45, 40))
    # Back
    draw.rectangle([(chair_x + 3, chair_y - 20), (chair_x + 32, chair_y)], fill=(50, 45, 40))


def draw_title_panel(draw: ImageDraw, title: str, author: str) -> None:
    """Draw the dark title panel at the bottom of the cover."""
    panel_y = 1920
    panel_height = HEIGHT - panel_y  # 640

    # Dark panel
    draw.rectangle([(0, panel_y), (WIDTH, HEIGHT)], fill=(25, 22, 20))

    # Subtle top border line
    draw.line([(100, panel_y), (WIDTH - 100, panel_y)], fill=(180, 140, 80), width=2)

    # Title text
    title_font_size = 72
    title_font = None
    try:
        title_font = ImageFont.truetype(FONT_PATH, title_font_size)
    except (IOError, OSError):
        try:
            title_font = ImageFont.truetype(FONT_FALLBACK, title_font_size)
        except (IOError, OSError):
            title_font = ImageFont.load_default()

    # Draw title with word wrapping
    words = title.split()
    line1 = " ".join(words[:4])
    line2 = " ".join(words[4:])

    # Center each line
    if title_font:
        # Try to get bbox for centering
        try:
            bbox1 = title_font.getbbox(line1)
            bbox2 = title_font.getbbox(line2)
            tw1 = bbox1[2] - bbox1[0]
            tw2 = bbox2[2] - bbox2[0]
        except AttributeError:
            tw1 = title_font.getsize(line1)[0]
            tw2 = title_font.getsize(line2)[0]
    else:
        tw1 = len(line1) * 20
        tw2 = len(line2) * 20

    tx1 = (WIDTH - tw1) // 2
    tx2 = (WIDTH - tw2) // 2

    text_color = (255, 255, 255)
    draw.text((tx1, panel_y + 40), line1, fill=text_color, font=title_font)
    draw.text((tx2, panel_y + 130), line2, fill=text_color, font=title_font)

    # Author
    author_font_size = 36
    author_font = None
    try:
        author_font = ImageFont.truetype(FONT_PATH, author_font_size)
    except (IOError, OSError):
        try:
            author_font = ImageFont.truetype(FONT_FALLBACK, author_font_size)
        except (IOError, OSError):
            author_font = ImageFont.load_default()

    if author_font:
        try:
            abbox = author_font.getbbox(author)
            aw = abbox[2] - abbox[0]
        except AttributeError:
            aw = author_font.getsize(author)[0]
    else:
        aw = len(author) * 12

    ax = (WIDTH - aw) // 2
    draw.text((ax, panel_y + 220), author, fill=(200, 180, 150), font=author_font)

    # Decorative line under author
    draw.line([(WIDTH // 2 - 80, panel_y + 280), (WIDTH // 2 + 80, panel_y + 280)], fill=(180, 140, 80), width=1)

    # Small decoration - door symbols
    for i in range(5):
        dx = WIDTH // 2 - 120 + i * 60
        dy = panel_y + 310
        dw = 20
        dh = 35
        door_col = lerp_color((30, 80, 160), (170, 40, 40), i / 4)
        draw.rectangle([(dx, dy), (dx + dw, dy + dh)], fill=door_col)
        # Tiny handle
        draw.ellipse([(dx + dw - 6, dy + dh // 2 - 2), (dx + dw - 3, dy + dh // 2 + 2)], fill=(200, 180, 100))


def draw_lamppost(draw: ImageDraw) -> None:
    """Draw a decorative lamppost on the left side."""
    x = 60
    # Pole
    draw.line([(x, 400), (x, 750)], fill=(50, 45, 40), width=6)
    # Lamp head
    draw.ellipse([(x - 15, 380), (x + 15, 410)], fill=(220, 200, 120))
    draw.ellipse([(x - 12, 395), (x + 12, 410)], fill=(50, 45, 40))
    # Glow effect
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for r in range(60, 10, -5):
        alpha = max(0, 30 - r // 2)
        glow_draw.ellipse([(x - r, 390 - r), (x + r, 390 + r)], fill=(255, 220, 150, alpha))
    draw._image.paste(glow, (0, 0), glow)


def generate_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Background gradient - terracotta to sage green
    top_color = (175, 130, 100)   # warm terracotta
    mid_color = (140, 155, 130)   # sage transition
    bottom_color = (100, 130, 110) # deeper sage

    for y in range(HEIGHT):
        if y < HEIGHT // 2:
            t = y / (HEIGHT // 2)
            c = lerp_color(top_color, mid_color, t)
        else:
            t = (y - HEIGHT // 2) / (HEIGHT // 2)
            c = lerp_color(mid_color, bottom_color, t)
        draw.line([(0, y), (WIDTH, y)], fill=c)

    # Draw elements
    draw_building_facade(draw)
    draw_doors(draw)
    draw_cafe(draw)
    draw_lamppost(draw)
    draw_street(draw)
    draw_title_panel(draw, title, author)

    # Convert to RGB and save
    final = img.convert("RGB")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(final, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    final.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    generate_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()