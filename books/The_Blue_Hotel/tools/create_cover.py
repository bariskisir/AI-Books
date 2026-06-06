#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Blue Hotel."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


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
    """Deep blue-gray to storm-dark gradient for the blizzard Western feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((20, 30, 50), ((40, 50, 75)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((40, 50, 75), ((60, 65, 85)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 65, 85), ((25, 30, 45)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_hotel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a two-story frontier hotel in the blizzard."""
    cx, cy = width // 2, int(height * 0.38)
    hotel_w, hotel_h = 340, 280

    rng = random.Random(101)
    rng.seed(101)

    # Main building body
    draw.rectangle(
        [cx - hotel_w // 2, cy - hotel_h // 2, cx + hotel_w // 2, cy + hotel_h // 2],
        fill=(55, 50, 45),
    )

    # Roof line
    draw.polygon(
        [(cx - hotel_w // 2 - 20, cy - hotel_h // 2), (cx, cy - hotel_h // 2 - 50), (cx + hotel_w // 2 + 20, cy - hotel_h // 2)],
        fill=(40, 35, 30),
    )

    # Second floor windows (dark)
    for i in range(4):
        wx = cx - 120 + i * 75
        wy = cy - 80
        draw.rectangle([wx, wy, wx + 35, wy + 45], fill=(15, 15, 20))
        # Window frame
        draw.rectangle([wx, wy, wx + 35, wy + 45], outline=(80, 75, 70), width=2)

    # First floor windows (some lit)
    for i in range(3):
        wx = cx - 100 + i * 90
        wy = cy + 15
        if i == 0:
            draw.rectangle([wx, wy, wx + 40, wy + 55], fill=(180, 160, 100))
            # Warm glow
            for g in range(2):
                draw.rectangle(
                    [wx - g, wy - g, wx + 40 + g, wy + 55 + g],
                    outline=(180, 160, 100, 30),
                    width=1,
                )
        else:
            draw.rectangle([wx, wy, wx + 40, wy + 55], fill=(15, 15, 20))
        draw.rectangle([wx, wy, wx + 40, wy + 55], outline=(80, 75, 70), width=2)

    # Door
    door_x, door_y = cx - 15, cy + 40
    draw.rectangle([door_x, door_y, door_x + 30, door_y + 70], fill=(40, 35, 30))
    draw.rectangle([door_x + 22, door_y + 25, door_x + 28, door_y + 31], fill=(200, 180, 100))

    # Porch
    draw.rectangle(
        [cx - hotel_w // 2 - 30, cy + hotel_h // 2 - 10, cx + hotel_w // 2 + 30, cy + hotel_h // 2 + 10],
        fill=(50, 45, 40),
    )

    # Porch posts
    for p in range(-3, 4):
        px = cx + p * 80
        if abs(px - cx) > hotel_w // 2:
            continue
        draw.rectangle([px - 4, cy + hotel_h // 2 - 60, px + 4, cy + hotel_h // 2 + 5], fill=(50, 45, 40))

    # Porch roof
    draw.polygon(
        [(cx - hotel_w // 2 - 35, cy + hotel_h // 2 - 60), (cx, cy + hotel_h // 2 - 75), (cx + hotel_w // 2 + 35, cy + hotel_h // 2 - 60)],
        fill=(40, 35, 30),
    )

    # Sign
    sign_w, sign_h = 180, 35
    draw.rectangle(
        [cx - sign_w // 2, cy - hotel_h // 2 - 70, cx + sign_w // 2, cy - hotel_h // 2 - 35],
        fill=(45, 55, 95),
    )
    # Sign text placeholder
    try:
        sign_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 20)
        draw.text((cx - 55, cy - hotel_h // 2 - 65), "BLUE HOTEL", fill=(200, 200, 210), font=sign_font)
    except Exception:
        pass


def draw_blizzard(draw: ImageDraw, width: int, height: int) -> None:
    """Draw falling snow and wind effects."""
    rng = random.Random(42)
    rng.seed(42)

    for _ in range(300):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.8))
        size = rng.randint(1, 4)
        alpha = rng.randint(100, 220)
        draw.ellipse([x, y, x + size, y + size], fill=(220, 230, 255, alpha))

    # Wind streaks
    for _ in range(20):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.7))
        length = rng.randint(30, 100)
        draw.line(
            [(x, y), (x + length, y - length // 3)],
            fill=(200, 210, 230, 40),
            width=1,
        )


def draw_poker_table(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a faint poker table in the lower portion, suggesting the saloon theme."""
    cx, cy = width // 2, int(height * 0.65)

    # Table surface (ellipse)
    draw.ellipse(
        [cx - 140, cy - 50, cx + 140, cy + 50],
        fill=(20, 60, 30),
        outline=(40, 80, 50),
        width=2,
    )

    # Chips
    rng = random.Random(77)
    rng.seed(77)
    chip_colors = [(200, 50, 50), (50, 50, 200), (200, 200, 50), (200, 200, 200)]
    for _ in range(12):
        cx_chip = cx + rng.randint(-100, 100)
        cy_chip = cy + rng.randint(-30, 30)
        color = chip_colors[rng.randint(0, 3)]
        draw.ellipse([cx_chip - 6, cy_chip - 6, cx_chip + 6, cy_chip + 6], fill=color)

    # Cards
    for i in range(3):
        cx_card = cx - 50 + i * 40
        cy_card = cy - 15
        draw.rectangle(
            [cx_card, cy_card, cx_card + 18, cy_card + 26],
            fill=(220, 215, 200),
            outline=(100, 95, 85),
            width=1,
        )


def draw_snow_ground(draw: ImageDraw, width: int, height: int) -> None:
    """Draw snow-covered ground at the bottom."""
    ground_top = int(height * 0.78)
    for y in range(ground_top, height):
        t = (y - ground_top) / (height - ground_top)
        c = lerp_color((180, 195, 210), ((200, 210, 225)), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Snowdrifts
    for i in range(6):
        dx = i * 300 + random.randint(-50, 50)
        dy = ground_top + random.randint(-20, 20)
        draw.ellipse(
            [dx - 100, dy - 20, dx + 150, dy + 30],
            fill=(195, 210, 225, 100),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 15, 25))

    # Subtle blue border at top
    draw.line([(0, panel_top), (width, panel_top)], fill=(45, 55, 95), width=3)

    # Title text
    title = "The Blue\nHotel"
    title_font_size = 78
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in WHITE
    lines = title.split("\n")
    y_offset = panel_top + 70
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 95

    # Author name
    author = "Barış Kısır"
    author_font_size = 42
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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(180, 190, 220), font=author_font)

    # Genre line
    genre_text = "A Suspense Western"
    genre_font_size = 24
    try:
        genre_font = ImageFont.truetype(str(font_paths["small"]), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()

    try:
        gbbox = draw.textbbox((0, 0), genre_text, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    gy = ay + 55
    draw.text((gx, gy), genre_text, fill=(120, 130, 160), font=genre_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Blue Hotel")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Snow ground
    draw_snow_ground(draw, WIDTH, HEIGHT)

    # Step 3: Hotel in blizzard
    draw_hotel(draw, WIDTH, HEIGHT)

    # Step 4: Poker table suggestion
    draw_poker_table(draw, WIDTH, HEIGHT)

    # Step 5: Blizzard effects (snow + wind)
    draw_blizzard(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften the image slightly
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def _standard_cover_font(name: str, size: int):
    font_dir = globals().get("FONT_DIR", globals().get("FONTS_DIR", None))
    candidates = []
    if font_dir is not None:
        candidates.append(Path(font_dir) / name)
    candidates.extend([
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts") / "arialbd.ttf",
        Path("C:/Windows/Fonts") / "arial.ttf",
    ])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _standard_cover_repair_text(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def _standard_cover_wrap(draw, text: str, selected_font, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=selected_font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _standard_cover_center(draw, y: int, lines: list[str], selected_font, fill, line_gap: int, width: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _standard_cover_title_font(draw, title: str, max_width: int):
    for size in (116, 104, 96, 88, 80, 72):
        selected = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), selected, max_width)
        heights = [draw.textbbox((0, 0), line, font=selected)[3] - draw.textbbox((0, 0), line, font=selected)[1] for line in lines]
        total = sum(heights) + max(0, len(lines) - 1) * 18
        if len(lines) <= 4 and total <= 430:
            return selected, lines, 18
    selected = _standard_cover_font("arialbd.ttf", 68)
    return selected, _standard_cover_wrap(draw, title.upper(), selected, max_width), 16


def _standard_cover_metadata_from_locals(local_vars):
    for key in ("metadata", "meta", "data", "m", "book", "book_data"):
        value = local_vars.get(key)
        if isinstance(value, dict):
            return value

    candidates = []
    args = local_vars.get("args")
    if args is not None:
        candidates.append(getattr(args, "metadata", None))
    for key in ("metadata_path", "meta_path", "mp"):
        candidates.append(local_vars.get(key))

    for metadata_path in candidates:
        if not metadata_path:
            continue
        try:
            json_mod = __import__("json")
            path_cls = __import__("pathlib").Path
            return json_mod.loads(path_cls(metadata_path).read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def _standard_cover_resolve_title(local_vars):
    for key in ("title", "ti", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value

    metadata = _standard_cover_metadata_from_locals(local_vars)
    for key in ("title", "book_title", "name"):
        value = metadata.get(key)
        if value:
            return value

    args = local_vars.get("args")
    candidates = []
    if args is not None:
        candidates.append(getattr(args, "out", None))
    for key in ("output_path", "out_path", "op", "out"):
        candidates.append(local_vars.get(key))

    for output_path in candidates:
        if not output_path:
            continue
        try:
            path_cls = __import__("pathlib").Path
            stem = path_cls(output_path).stem.replace("_", " ").strip()
            if stem:
                return stem
        except Exception:
            continue
    return ""


def _standard_cover_resolve_author(local_vars):
    for key in ("author", "au", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value

    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("author")
    if value:
        return value
    return "Barış Kısır"

def _draw_standard_cover_title_panel(image, title: str = "", author: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(3, 5, 8, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(160, 225, 209, 105), width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (244, 249, 238), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (210, 229, 221), 12, width)
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