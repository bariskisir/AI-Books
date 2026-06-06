#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Witch of Thornwood Hollow."""

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
    """Deep green to violet to near-black gradient for the enchanted forest feel."""
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color((10, 40, 20), ((60, 10, 60)), t)
        else:
            t = (y - height * 0.5) / (height * 0.5)
            c = lerp_color((60, 10, 60), ((5, 0, 15)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_cottage(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small crooked cottage at the forest edge."""
    cx, cy = width // 2, int(height * 0.55)
    w, h = 200, 160

    # Main body
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=(30, 20, 15))

    # Roof
    draw.polygon([(cx - w // 2 - 20, cy - h // 2), (cx, cy - h // 2 - 80), (cx + w // 2 + 20, cy - h // 2)], fill=(60, 30, 20))

    # Door
    draw.rectangle([cx - 20, cy - 10, cx + 20, cy + h // 2], fill=(50, 35, 25))
    draw.ellipse([cx + 12, cy + 30, cx + 18, cy + 36], fill=(255, 200, 100))

    # Window (glowing)
    draw.rectangle([cx - 60, cy - 40, cx - 25, cy - 5], fill=(255, 220, 100))
    draw.rectangle([cx - 60, cy - 40, cx - 25, cy - 5], fill=(255, 220, 100, 80))

    # Window glow effect
    for i in range(3):
        draw.rectangle(
            [cx - 60 - i, cy - 40 - i, cx - 25 + i, cy - 5 + i],
            outline=(255, 220, 100, 40 // (i + 1)),
            width=1,
        )

    # Chimney
    draw.rectangle([cx + 40, cy - h // 2 - 60, cx + 60, cy - h // 2 - 10], fill=(40, 25, 20))
    # Smoke
    draw.ellipse([cx + 45, cy - h // 2 - 80, cx + 65, cy - h // 2 - 60], fill=(180, 180, 190, 60))
    draw.ellipse([cx + 55, cy - h // 2 - 100, cx + 80, cy - h // 2 - 75], fill=(160, 160, 170, 40))

    # Fence
    for fx in range(cx - 140, cx + 160, 30):
        if abs(fx - cx) < 100:
            continue
        draw.rectangle([fx, cy + h // 2 - 10, fx + 6, cy + h // 2 + 50], fill=(40, 30, 20))


def draw_trees(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stylized twisted trees flanking the scene."""
    tree_positions = [
        (100, height * 0.4, 2.2),
        (250, height * 0.35, 1.8),
        (width - 100, height * 0.38, 2.0),
        (width - 250, height * 0.32, 1.6),
        (50, height * 0.55, 1.4),
        (width - 50, height * 0.5, 1.5),
    ]

    for tx, ty, scale in tree_positions:
        trunk_h = int(180 * scale)
        trunk_w = int(20 * scale)
        # Trunk
        draw.rectangle([tx - trunk_w // 2, int(ty - trunk_h), tx + trunk_w // 2, int(ty)], fill=(15, 10, 8))
        # Branches
        for bx in range(-1, 2):
            br_y = int(ty - trunk_h * 0.4 + bx * 40 * scale)
            draw.line(
                [tx, br_y, tx - int(60 * scale * bx), br_y - int(30 * scale)], fill=(15, 10, 8), width=int(4 * scale)
            )
        # Canopy
        draw.ellipse(
            [
                tx - int(80 * scale),
                int(ty - trunk_h - 60 * scale),
                tx + int(80 * scale),
                int(ty - trunk_h + 10 * scale),
            ],
            fill=(5, 20, 10),
        )
        draw.ellipse(
            [
                tx - int(60 * scale) - 20,
                int(ty - trunk_h - 40 * scale),
                tx + int(60 * scale) + 20,
                int(ty - trunk_h + 20 * scale),
            ],
            fill=(8, 25, 12),
        )


def draw_glowing_flowers(draw: ImageDraw, width: int, height: int) -> None:
    """Draw small glowing flowers/light particles across the lower forest."""
    import random

    rng = random.Random(42)
    for _ in range(120):
        x = rng.randint(50, width - 50)
        y = rng.randint(int(height * 0.4), int(height * 0.7))
        size = rng.randint(3, 8)
        # Glow color: green or violet
        if rng.random() < 0.5:
            color = (100, 255, 150, 180)
            glow = (60, 200, 100, 60)
        else:
            color = (200, 100, 255, 180)
            glow = (150, 50, 200, 60)

        # Outer glow
        draw.ellipse([x - size * 2, y - size * 2, x + size * 2, y + size * 2], fill=glow)
        # Inner flower
        draw.ellipse([x - size // 2, y - size // 2, x + size // 2, y + size // 2], fill=color)
        # Center
        draw.ellipse([x - 1, y - 1, x + 1, y + 1], fill=(255, 255, 255, 200))


def draw_thorns(draw: ImageDraw, width: int, height: int) -> None:
    """Draw black thorn vines creeping from the edges."""
    import random

    rng = random.Random(7)

    # Bottom left thorns
    for i in range(8):
        start_x = rng.randint(-20, 200)
        start_y = rng.randint(int(height * 0.6), height)
        end_x = start_x + rng.randint(100, 400)
        end_y = start_y - rng.randint(100, 300)
        points = []
        steps = 20
        for s in range(steps + 1):
            t = s / steps
            x = start_x + (end_x - start_x) * t + rng.randint(-20, 20)
            y = start_y + (end_y - start_y) * t + rng.randint(-15, 15)
            points.append((x, y))
        draw.line(points, fill=(10, 5, 15), width=rng.randint(3, 8))

    # Bottom right thorns
    for i in range(8):
        start_x = width - rng.randint(-20, 200)
        start_y = rng.randint(int(height * 0.6), height)
        end_x = start_x - rng.randint(100, 400)
        end_y = start_y - rng.randint(100, 300)
        points = []
        steps = 20
        for s in range(steps + 1):
            t = s / steps
            x = start_x + (end_x - start_x) * t + rng.randint(-20, 20)
            y = start_y + (end_y - start_y) * t + rng.randint(-15, 15)
            points.append((x, y))
        draw.line(points, fill=(10, 5, 15), width=rng.randint(3, 8))


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a light rectangular title panel at the bottom of the cover."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - semi-transparent light rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(220, 215, 205, 200))

    # Add a subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 170, 155), width=2)

    # Title text
    title = "The Witch of\nThornwood Hollow"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(30, 25, 40), font=title_font)
        y_offset += 90

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
    draw.text((ax, ay), author, fill=(60, 55, 70), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Witch of Thornwood Hollow")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Background trees
    draw_trees(draw, WIDTH, HEIGHT)

    # Step 3: Thorns creeping from edges
    draw_thorns(draw, WIDTH, HEIGHT)

    # Step 4: Cottage with glowing window
    draw_cottage(draw, WIDTH, HEIGHT)

    # Step 5: Glowing flowers
    draw_glowing_flowers(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "georgiab.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, draw, WIDTH, HEIGHT, font_paths)

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