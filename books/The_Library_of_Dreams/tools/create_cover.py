#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Library of Dreams."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


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
    """Midnight blue to deep indigo to silver-black gradient for a dreamlike feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((10, 10, 45), (25, 15, 70), t)
        elif y < height * 0.75:
            t = (y - height * 0.4) / (height * 0.35)
            c = lerp_color((25, 15, 70), (50, 40, 90), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((50, 40, 90), (15, 10, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered stars / light motes in the upper portion of the cover."""
    import random

    rng = random.Random(101)
    for _ in range(200):
        x = rng.randint(20, width - 20)
        y = rng.randint(20, int(height * 0.5))
        size = rng.randint(1, 4)
        brightness = rng.randint(150, 255)
        alpha = rng.randint(80, 220)
        if rng.random() < 0.3:
            color = (brightness, brightness, 255, alpha)
        else:
            color = (brightness, brightness, brightness, alpha)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)


def draw_floating_books(draw: ImageDraw, width: int, height: int) -> None:
    """Draw floating books drifting through the dreamscape."""
    import random

    rng = random.Random(42)

    positions = [
        (250, 500, -15, (100, 80, 140)),
        (400, 700, 10, (80, 100, 150)),
        (1100, 450, 20, (90, 70, 130)),
        (1300, 650, -8, (70, 110, 140)),
        (600, 950, 15, (110, 90, 150)),
        (1000, 1000, -12, (80, 80, 130)),
        (150, 1100, 5, (100, 100, 140)),
        (1400, 1100, -5, (90, 90, 135)),
        (800, 600, 25, (85, 75, 140)),
        (500, 1200, -20, (95, 85, 145)),
    ]

    for px, py, angle, color in positions:
        bw, bh = 40, 60
        # Book body
        rect = [
            (px - bw // 2, py - bh // 2),
            (px + bw // 2, py + bh // 2),
        ]
        draw.rectangle(rect, fill=color, outline=(180, 170, 200))
        # Spine line
        draw.line(
            [(px, py - bh // 2 + 4), (px, py + bh // 2 - 4)],
            fill=(200, 190, 220),
            width=2,
        )
        # Pages (side)
        draw.rectangle(
            [px + bw // 2 - 2, py - bh // 2 + 2, px + bw // 2 - 1, py + bh // 2 - 2],
            fill=(230, 225, 240),
        )
        # Glow around book
        for i in range(3):
            glow_alpha = 30 - i * 8
            if glow_alpha <= 0:
                continue
            draw.ellipse(
                [px - bw // 2 - 10 - i * 5, py - bh // 2 - 10 - i * 5,
                 px + bw // 2 + 10 + i * 5, py + bh // 2 + 10 + i * 5],
                outline=(150, 140, 200, glow_alpha),
                width=1,
            )


def draw_sleeping_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouetted sleeping figure floating near the center of the cover."""
    cx, cy = width // 2, int(height * 0.3)

    # Head
    head_r = 25
    draw.ellipse([cx - head_r, cy - head_r, cx + head_r, cy + head_r], fill=(180, 175, 200, 120))

    # Body (reclining)
    body_color = (160, 155, 185, 100)
    draw.ellipse([cx - 30, cy + 20, cx + 50, cy + 90], fill=body_color)
    # Legs
    draw.line([cx + 35, cy + 85, cx + 20, cy + 150], fill=(160, 155, 185, 100), width=10)
    draw.line([cx + 35, cy + 85, cx + 60, cy + 140], fill=(160, 155, 185, 100), width=10)
    # Arms
    draw.line([cx - 15, cy + 30, cx - 40, cy + 60], fill=(160, 155, 185, 100), width=6)
    draw.line([cx + 20, cy + 35, cx + 55, cy + 50], fill=(160, 155, 185, 100), width=6)

    # Dream wisps rising from the figure
    import random
    rng = random.Random(77)
    for _ in range(15):
        wx = cx + rng.randint(-60, 60)
        wy = cy - rng.randint(30, 120)
        ws = rng.randint(2, 6)
        alpha = rng.randint(60, 160)
        draw.ellipse([wx - ws, wy - ws, wx + ws, wy + ws], fill=(200, 190, 255, alpha))


def draw_distant_shelves(draw: ImageDraw, width: int, height: int) -> None:
    """Draw faint, distant bookshelves receding into the background."""
    shelf_y_start = int(height * 0.35)
    shelf_y_end = int(height * 0.55)

    for row in range(6):
        y_base = shelf_y_start + (shelf_y_end - shelf_y_start) * row // 6
        # Shelf line
        draw.line(
            [(100, y_base), (width - 100, y_base)],
            fill=(60, 55, 90, 80),
            width=1,
        )
        # Books on shelf
        import random
        rng = random.Random(200 + row)
        for b in range(12 + row * 2):
            bx = 120 + b * ((width - 240) // (14 + row * 2))
            by = y_base - 30
            bh = rng.randint(15, 30)
            bw = rng.randint(8, 15)
            b_color = (rng.randint(40, 80), rng.randint(30, 70), rng.randint(60, 100), 60)
            draw.rectangle([bx, by - bh, bx + bw, by], fill=b_color)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        c = lerp_color((20, 15, 45), (10, 8, 25), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(130, 120, 180, 150), width=3)

    # Title text
    title = "The Library of\nDreams"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

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
        y_offset += 95

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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(200, 195, 220), font=author_font)

    # Decorative line above author
    line_y = ay - 15
    draw.line([(width // 2 - 80, line_y), (width // 2 + 80, line_y)], fill=(150, 140, 200, 120), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Stars/motes in upper portion
    draw_stars(draw, WIDTH, HEIGHT)

    # Step 3: Distant shelves
    draw_distant_shelves(draw, WIDTH, HEIGHT)

    # Step 4: Floating books
    draw_floating_books(draw, WIDTH, HEIGHT)

    # Step 5: Sleeping figure with dream wisps
    draw_sleeping_figure(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

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