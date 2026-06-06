#!/usr/bin/env python3
"""Generate a genre-appropriate cover image for The House on the Cliff."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560
TITLE_FONT_SIZE = 96
AUTHOR_FONT_SIZE = 48
GENRE_FONT_SIZE = 28


def hex_to_rgb(hex_color: str) -> tuple[int, ...]:
    h = hex_color.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def draw_gradient(draw: ImageDraw.Draw, top_color: str, bottom_color: str) -> None:
    top_rgb = hex_to_rgb(top_color)
    bottom_rgb = hex_to_rgb(bottom_color)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_rgb[0] * (1 - ratio) + bottom_rgb[0] * ratio)
        g = int(top_rgb[1] * (1 - ratio) + bottom_rgb[1] * ratio)
        b = int(top_rgb[2] * (1 - ratio) + bottom_rgb[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def load_font(size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype("arialbd.ttf", size)
    except (OSError, IOError):
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf", size)
        except (OSError, IOError):
            return ImageFont.load_default()


def draw_house(draw: ImageDraw.Draw) -> None:
    """Draw a clifftop house silhouette with glass walls using PIL primitives."""
    # Cliff face
    cliff_color = (90, 85, 80)
    cliff_points = [
        (0, 1400),
        (0, 1600),
        (400, 1500),
        (600, 1450),
        (850, 1480),
        (1100, 1420),
        (1400, 1500),
        (1600, 1450),
        (1600, 1700),
        (0, 1700),
    ]
    draw.polygon(cliff_points, fill=cliff_color)

    # Cliff top
    cliff_top_color = (110, 100, 90)
    cliff_top_points = [
        (0, 1400),
        (400, 1500),
        (600, 1450),
        (850, 1480),
        (1100, 1420),
        (1400, 1500),
        (1600, 1450),
        (1600, 1400),
        (1400, 1380),
        (1100, 1360),
        (850, 1400),
        (600, 1380),
        (400, 1420),
        (0, 1350),
    ]
    draw.polygon(cliff_top_points, fill=cliff_top_color)

    # House structure - modern glass box design
    house_color = (70, 70, 80)
    glass_color = (160, 190, 210, 180)

    # Main house body
    house_x, house_y = 550, 1050
    house_w, house_h = 500, 350

    # Steel frame outline
    draw.rectangle([house_x, house_y, house_x + house_w, house_y + house_h], outline=house_color, width=4)

    # Glass panels (left side)
    glass_left = house_x + 10
    glass_top = house_y + 10
    glass_w = (house_w - 30) // 2
    glass_h = (house_h - 30) // 2

    draw.rectangle(
        [glass_left, glass_top, glass_left + glass_w, glass_top + glass_h],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )
    draw.rectangle(
        [glass_left, glass_top + glass_h + 10, glass_left + glass_w, glass_top + 2 * glass_h + 10],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )

    # Glass panels (right side)
    glass_right = glass_left + glass_w + 10
    draw.rectangle(
        [glass_right, glass_top, glass_right + glass_w, glass_top + glass_h],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )
    draw.rectangle(
        [glass_right, glass_top + glass_h + 10, glass_right + glass_w, glass_top + 2 * glass_h + 10],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )

    # Cross beams
    draw.line(
        [house_x, house_y + house_h // 2, house_x + house_w, house_y + house_h // 2],
        fill=house_color,
        width=2,
    )
    draw.line(
        [house_x + house_w // 2, house_y, house_x + house_w // 2, house_y + house_h],
        fill=house_color,
        width=2,
    )

    # Roof line - flat modern roof
    draw.line(
        [house_x - 20, house_y, house_x + house_w + 20, house_y],
        fill=house_color,
        width=6,
    )

    # Second smaller structure to the right
    house2_x = house_x + house_w + 40
    house2_y = house_y + 50
    house2_w = 200
    house2_h = 250
    draw.rectangle([house2_x, house2_y, house2_x + house2_w, house2_y + house2_h], outline=house_color, width=4)
    draw.rectangle(
        [house2_x + 10, house2_y + 10, house2_x + house2_w - 10, house2_y + house2_h - 10],
        fill=glass_color,
        outline=(100, 130, 160),
        width=2,
    )
    draw.line(
        [house2_x + house2_w // 2, house2_y, house2_x + house2_w // 2, house2_y + house2_h],
        fill=house_color,
        width=2,
    )

    # Deck / balcony extending from house
    deck_color = (80, 78, 75)
    draw.rectangle([house_x - 30, house_y + house_h, house_x + 120, house_y + house_h + 15], fill=deck_color)
    draw.rectangle([house_x + house_w - 80, house_y + house_h, house_x + house_w, house_y + house_h + 15], fill=deck_color)

    # Railings
    for x_pos in range(house_x - 20, house_x + 130, 25):
        draw.line([(x_pos, house_y + house_h), (x_pos, house_y + house_h + 15)], fill=(100, 100, 100), width=2)
    for x_pos in range(house_x + house_w - 70, house_x + house_w + 10, 25):
        draw.line([(x_pos, house_y + house_h), (x_pos, house_y + house_h + 15)], fill=(100, 100, 100), width=2)


def draw_ocean(draw: ImageDraw.Draw) -> None:
    """Draw the Pacific Ocean in the background."""
    ocean_top = 1050
    # Ocean gradient
    for y in range(ocean_top, 1400):
        ratio = (y - ocean_top) / 350
        r = int(30 * (1 - ratio) + 20 * ratio)
        g = int(80 * (1 - ratio) + 60 * ratio)
        b = int(140 * (1 - ratio) + 110 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Horizon line
    draw.line([(0, ocean_top), (WIDTH, ocean_top)], fill=(180, 200, 220), width=1)

    # Waves
    wave_color = (100, 140, 180, 60)
    for i in range(20):
        wx = i * 80
        wy = ocean_top + 100 + (i % 3) * 30
        draw.arc([wx, wy, wx + 60, wy + 20], 0, 180, fill=wave_color, width=1)


def draw_sky(draw: ImageDraw.Draw) -> None:
    """Draw the sky with clouds."""
    # Sun glow
    sun_x, sun_y = 1200, 400
    for r in range(120, 0, -5):
        alpha = max(0, 255 - r * 2)
        draw.ellipse(
            [sun_x - r, sun_y - r, sun_x + r, sun_y + r],
            fill=(255, 200, 100, alpha),
            outline=None,
        )

    # Sun
    draw.ellipse([sun_x - 30, sun_y - 30, sun_x + 30, sun_y + 30], fill=(255, 220, 120))

    # Clouds
    cloud_color = (220, 225, 230)
    clouds = [
        (200, 300, 150, 50),
        (500, 250, 200, 40),
        (900, 350, 120, 35),
        (1400, 280, 180, 45),
    ]
    for cx, cy, cw, ch in clouds:
        draw.ellipse([cx, cy, cx + cw, cy + ch], fill=cloud_color)
        draw.ellipse([cx - 30, cy + 10, cx + cw - 30, cy + ch - 10], fill=cloud_color)
        draw.ellipse([cx + 40, cy - 10, cx + cw + 40, cy + ch - 20], fill=cloud_color)


def draw_bottom_panel(draw: ImageDraw.Draw) -> None:
    """Draw the dark bottom panel with title and author."""
    panel_y = 1920
    panel_height = HEIGHT - panel_y

    # Dark semi-transparent panel
    draw.rectangle([0, panel_y, WIDTH, HEIGHT], fill=(20, 20, 30, 220))

    # Decorative line
    line_y = panel_y + 30
    draw.line([(WIDTH // 2 - 150, line_y), (WIDTH // 2 + 150, line_y)], fill=(100, 120, 150), width=2)

    # Title
    try:
        title_font = load_font(TITLE_FONT_SIZE)
    except Exception:
        title_font = ImageFont.load_default()

    title = "The House on the Cliff"
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    ty = panel_y + 60
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Author
    try:
        author_font = load_font(AUTHOR_FONT_SIZE)
    except Exception:
        author_font = ImageFont.load_default()

    author = "Barış Kısır"
    bbox = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox[2] - bbox[0]
    ax = (WIDTH - aw) // 2
    ay = ty + TITLE_FONT_SIZE + 40
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Genre label
    try:
        genre_font = load_font(GENRE_FONT_SIZE)
    except Exception:
        genre_font = ImageFont.load_default()

    genre = "Domestic Suspense"
    bbox = draw.textbbox((0, 0), genre, font=genre_font)
    gw = bbox[2] - bbox[0]
    gx = (WIDTH - gw) // 2
    gy = ay + AUTHOR_FONT_SIZE + 20
    draw.text((gx, gy), genre, fill=(150, 160, 180), font=genre_font)



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

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata.get("title", "The House on the Cliff")
    author = metadata.get("author", "Barış Kısır")
    genre = metadata.get("genre", "Domestic Suspense")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Ocean blue to cliff gray gradient background
    draw_gradient(draw, "#1a3a5c", "#5a5a5a")

    # Sky
    draw_sky(draw)

    # Ocean
    draw_ocean(draw)

    # Cliff and house
    draw_house(draw)

    # Bottom panel with text
    draw_bottom_panel(draw)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()