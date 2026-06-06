#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Book of Dirt."""

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
    """Terracotta-to-ochre gradient for the Australian outback feel."""
    for y in range(height):
        if y < height * 0.6:
            t = y / (height * 0.6)
            c = lerp_color((180, 90, 50), (200, 120, 60), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((200, 120, 60), (140, 70, 35), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_cracked_earth(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a network of cracks across the foreground, like dry mud."""
    rng = random.Random(42)
    base_y_start = int(height * 0.45)

    # Main crack network
    for _ in range(60):
        start_x = rng.randint(50, width - 50)
        start_y = rng.randint(base_y_start, height - 100)
        length = rng.randint(40, 250)
        angle = rng.uniform(0, 2 * math.pi)
        end_x = start_x + int(length * math.cos(angle))
        end_y = start_y + int(length * math.sin(angle))

        # Crack color: darker than background
        crack_color = (90, 45, 20)
        crack_width = rng.randint(1, 4)

        # Draw crack with slight curve
        points = []
        steps = 10
        for s in range(steps + 1):
            t = s / steps
            x = start_x + (end_x - start_x) * t + rng.randint(-5, 5)
            y = start_y + (end_y - start_y) * t + rng.randint(-3, 3)
            points.append((x, y))

        draw.line(points, fill=crack_color, width=crack_width)

    # Add some broader polygon cracks (larger plates)
    for _ in range(15):
        cx = rng.randint(100, width - 100)
        cy = rng.randint(base_y_start + 50, height - 150)
        sides = rng.randint(4, 7)
        radius = rng.randint(30, 80)
        polygon = []
        for s in range(sides):
            a = 2 * math.pi * s / sides + rng.uniform(-0.2, 0.2)
            r = radius * rng.uniform(0.7, 1.3)
            polygon.append((cx + r * math.cos(a), cy + r * math.sin(a)))
        draw.polygon(polygon, outline=(100, 50, 25), width=2)


def draw_lone_tree(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a solitary, drought-stricken tree on the horizon."""
    tx, ty = width // 2, int(height * 0.42)

    # Trunk - dark, twisted
    trunk_color = (50, 30, 15)
    draw.line([(tx, ty), (tx, ty + 180)], fill=trunk_color, width=14)

    # Branches - skeletal, reaching
    branches = [
        (0, -1.2, 100, 0.5),
        (0.3, -1.0, 70, 0.4),
        (-0.3, -0.9, 80, 0.4),
        (0.5, -0.7, 50, 0.3),
        (-0.5, -0.6, 60, 0.3),
        (0.15, -1.1, 90, 0.35),
        (-0.15, -1.0, 85, 0.35),
    ]

    for x_dir, y_dir, length, thickness in branches:
        bx = tx + int(x_dir * length)
        by = int(ty + y_dir * length)
        draw.line([(tx, ty - 20), (bx, by)], fill=trunk_color, width=int(12 * thickness))

        # Smaller sub-branches
        if length > 50:
            for sub in range(2):
                sub_x = bx + int(x_dir * length * 0.3 * (1 if sub == 0 else -1))
                sub_y = by - int(length * 0.25)
                draw.line([(bx, by), (sub_x, sub_y)], fill=trunk_color, width=int(6 * thickness))

    # No leaves - dead tree


def draw_sun(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a harsh sun bleaching the sky."""
    cx, cy = width // 2, int(height * 0.12)
    radius = 80

    # Sun glow
    for i in range(10):
        r = radius + i * 20
        alpha = max(0, 60 - i * 6)
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 200, 120, alpha))

    # Sun disc
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 220, 140))

    # Bright center
    draw.ellipse([cx - radius // 2, cy - radius // 2, cx + radius // 2, cy + radius // 2], fill=(255, 240, 200))


def draw_hills(draw: ImageDraw, width: int, height: int) -> None:
    """Draw distant red hills on the horizon."""
    horizon_y = int(height * 0.38)

    for i in range(3):
        shade = (170, 85, 45 - i * 10)
        hill_y = horizon_y - 30 + i * 15
        points = [(0, hill_y + 60)]
        for x in range(0, width + 10, 20):
            h = math.sin(x * 0.003 + i * 1.5) * 40 + math.sin(x * 0.007 + i * 2.0) * 20
            points.append((x, hill_y + h))
        points.append((width, hill_y + 60))
        points.append((0, hill_y + 60))
        draw.polygon(points, fill=shade)


def draw_dust_motes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw tiny dust particles floating in the air."""
    rng = random.Random(17)
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        size = rng.randint(1, 3)
        alpha = rng.randint(30, 100)
        draw.ellipse([x, y, x + size, y + size], fill=(220, 180, 140, alpha))


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark, semi-transparent
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        c = lerp_color((30, 18, 8), ((15, 8, 4)), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Add a thin ochre line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(200, 120, 60), width=3)

    # Title text
    title = "The Book of\nDirt"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, white text
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

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
    ay = y_offset + 40
    draw.text((ax, ay), author, fill=(220, 180, 140), font=author_font)


def draw_low_scrub(draw: ImageDraw, width: int, height: int) -> None:
    """Draw sparse dry scrub bushes at ground level."""
    rng = random.Random(33)
    horizon_y = int(height * 0.38)

    for _ in range(40):
        bx = rng.randint(20, width - 20)
        by = rng.randint(horizon_y + 30, height - 300)
        bush_size = rng.randint(8, 20)

        # Bush color - dry brown-green
        bush_color = (90, 65, 30)
        for s in range(3):
            ox = rng.randint(-bush_size, bush_size)
            oy = rng.randint(-bush_size // 2, bush_size // 2)
            draw.ellipse(
                [bx + ox - bush_size // 2, by + oy - bush_size // 3, bx + ox + bush_size // 2, by + oy + bush_size // 3],
                fill=bush_color,
            )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Book of Dirt")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Harsh sun
    draw_sun(draw, WIDTH, HEIGHT)

    # Step 3: Distant hills
    draw_hills(draw, WIDTH, HEIGHT)

    # Step 4: Lone dead tree
    draw_lone_tree(draw, WIDTH, HEIGHT)

    # Step 5: Low scrub
    draw_low_scrub(draw, WIDTH, HEIGHT)

    # Step 6: Dust motes
    draw_dust_motes(draw, WIDTH, HEIGHT)

    # Step 7: Cracked earth
    draw_cracked_earth(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
    }
    draw_title_panel(draw, draw, WIDTH, HEIGHT, font_paths)

    # Soften image slightly
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