#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Shot."""

from __future__ import annotations

import argparse
import json
import math
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
    """Sky blue to grass green gradient for Wimbledon feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((70, 140, 210), ((100, 180, 230)), t)
        else:
            t = (y - height * 0.4) / (height * 0.6)
            c = lerp_color((100, 180, 230), ((20, 100, 40)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_grass_court(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a tennis court from a perspective view."""
    # Court surface (trapezoid for perspective)
    court_top = int(height * 0.25)
    court_bottom = int(height * 0.78)
    court_left = int(width * 0.15)
    court_right = int(width * 0.85)
    center_x = width // 2

    # Main court area - green rectangle (grass)
    court_color = (40, 130, 60)
    court_poly = [
        (court_left + 120, court_top),
        (court_right - 120, court_top),
        (court_right, court_bottom),
        (court_left, court_bottom),
    ]
    draw.polygon(court_poly, fill=court_color)

    # Court lines - white
    line_color = (240, 240, 240)

    # Singles sidelines
    draw.line([(court_left + 160, court_top), (court_left + 30, court_bottom)], fill=line_color, width=3)
    draw.line([(court_right - 160, court_top), (court_right - 30, court_bottom)], fill=line_color, width=3)

    # Doubles sidelines
    draw.line([(court_left + 120, court_top), (court_left, court_bottom)], fill=line_color, width=2)
    draw.line([(court_right - 120, court_top), (court_right, court_bottom)], fill=line_color, width=2)

    # Baseline
    draw.line([(court_left + 30, court_bottom), (court_right - 30, court_bottom)], fill=line_color, width=3)

    # Service line (top)
    service_y = court_top + int((court_bottom - court_top) * 0.35)
    draw.line([(court_left + 135, service_y), (court_right - 135, service_y)], fill=line_color, width=3)

    # Center service line
    center_top_x = court_left + (court_right - court_left) // 2
    center_bottom_x = court_left + 30 + (court_right - court_left - 60) // 2
    draw.line([(center_top_x, court_top), (center_bottom_x, court_bottom)], fill=line_color, width=3)

    # Center hash at baseline
    hash_left = center_bottom_x - 15
    hash_right = center_bottom_x + 15
    draw.line([(hash_left, court_bottom), (hash_right, court_bottom)], fill=line_color, width=3)


def draw_net(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the tennis net across the middle of the court."""
    net_y = int(height * 0.42)
    net_left = int(width * 0.12)
    net_right = int(width * 0.88)

    # Net band (top)
    draw.line([(net_left, net_y), (net_right, net_y)], fill=(200, 200, 200), width=4)

    # Net posts
    post_height = 40
    draw.rectangle([net_left - 4, net_y - post_height, net_left, net_y], fill=(180, 180, 180))
    draw.rectangle([net_right, net_y - post_height, net_right + 4, net_y], fill=(180, 180, 180))

    # Net mesh (vertical lines)
    for x in range(net_left, net_right, 8):
        draw.line([(x, net_y - 35), (x, net_y + 15)], fill=(180, 180, 180, 80), width=1)

    # Net white tape at top
    draw.line([(net_left, net_y - 2), (net_right, net_y - 2)], fill=(255, 255, 255), width=5)
    draw.line([(net_left, net_y + 14), (net_right, net_y + 14)], fill=(200, 200, 200), width=2)


def draw_tennis_ball(draw: ImageDraw, x: int, y: int, size: int = 20) -> None:
    """Draw a tennis ball."""
    # Ball shadow/glow
    draw.ellipse([x - size - 5, y - size - 5, x + size + 5, y + size + 5], fill=(100, 200, 100, 40))

    # Ball body
    ball_color = (210, 210, 100)
    draw.ellipse([x - size, y - size, x + size, y + size], fill=ball_color)

    # Ball line (seam)
    draw.arc([x - size, y - size, x + size, y + size], 0, 360, fill=(180, 180, 80), width=2)
    draw.arc([x - size + 2, y - size + 2, x + size - 2, y + size - 2], 200, 340, fill=(180, 180, 80), width=1)

    # Highlight
    draw.ellipse([x - size // 3, y - size // 3, x + size // 8, y + size // 8], fill=(255, 255, 200, 100))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 40, 20))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(30, 80, 40), width=3)

    # Title text
    title = "The Last Shot"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 80
    # Shadow
    draw.text((tx + 2, ty + 2), title, fill=(0, 0, 0), font=title_font)
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Decorative line
    line_y = ty + 100
    draw.line([(width // 2 - 120, line_y), (width // 2 + 120, line_y)], fill=(60, 180, 80), width=2)

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
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
    ay = line_y + 40
    draw.text((ax + 1, ay + 1), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, ay), author, fill=(200, 230, 200), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Shot")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Sky-to-grass gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Grass court with white lines
    draw_grass_court(draw, WIDTH, HEIGHT)

    # Step 3: Tennis net
    draw_net(draw, WIDTH, HEIGHT)

    # Step 4: Tennis balls scattered on court
    draw_tennis_ball(draw, WIDTH // 2 + 200, int(HEIGHT * 0.55), 18)
    draw_tennis_ball(draw, WIDTH // 2 - 250, int(HEIGHT * 0.35), 14)
    draw_tennis_ball(draw, WIDTH // 2 + 300, int(HEIGHT * 0.70), 12)

    # Step 5: Centre Court roof/outline silhouette at top
    roof_color = (50, 60, 70, 180)
    roof_points = [
        (int(WIDTH * 0.3), int(HEIGHT * 0.08)),
        (int(WIDTH * 0.4), int(HEIGHT * 0.02)),
        (int(WIDTH * 0.6), int(HEIGHT * 0.02)),
        (int(WIDTH * 0.7), int(HEIGHT * 0.08)),
        (int(WIDTH * 0.7), int(HEIGHT * 0.15)),
        (int(WIDTH * 0.3), int(HEIGHT * 0.15)),
    ]
    draw.polygon(roof_points, fill=roof_color)

    # Roof support lines
    for rx in range(int(WIDTH * 0.33), int(WIDTH * 0.68), int(WIDTH * 0.07)):
        draw.line(
            [(rx, int(HEIGHT * 0.10)), (rx + 30, int(HEIGHT * 0.04))],
            fill=(100, 110, 120, 120), width=2
        )

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
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