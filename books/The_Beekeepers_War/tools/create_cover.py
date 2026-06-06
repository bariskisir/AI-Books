#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Beekeeper's War."""

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
    """Mud brown to blood red to near-black gradient for the Western Front."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 60, 40), (120, 50, 40), t)
        elif y < height * 0.75:
            t = (y - height * 0.4) / (height * 0.35)
            c = lerp_color((120, 50, 40), (60, 20, 15), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((60, 20, 15), (10, 5, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_barbed_wire(draw: ImageDraw, width: int, height: int) -> None:
    """Draw barbed wire across the foreground."""
    import random

    rng = random.Random(17)
    wire_y = int(height * 0.55)
    # Main wire strands
    for strand_offset in range(-15, 20, 15):
        points = []
        for x in range(0, width, 8):
            y = wire_y + strand_offset + rng.randint(-3, 3)
            points.append((x, y))
        draw.line(points, fill=(40, 35, 30), width=2)

    # Barbs
    for i in range(width // 40):
        bx = i * 40 + rng.randint(5, 25)
        by = wire_y + rng.randint(-18, 18)
        draw.line([(bx, by), (bx - 8, by + 12)], fill=(50, 45, 40), width=2)
        draw.line([(bx, by), (bx + 8, by + 12)], fill=(50, 45, 40), width=2)
        draw.line([(bx, by), (bx, by + 14)], fill=(50, 45, 40), width=2)


def draw_trench_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a trench line and sandbags at the horizon."""
    horizon = int(height * 0.52)
    # Trench parapet
    draw.rectangle([(0, horizon - 15), (width, horizon)], fill=(55, 45, 35))
    # Sandbags
    import random

    rng = random.Random(8)
    for x in range(0, width, 30):
        bag_h = rng.randint(8, 14)
        bag_w = rng.randint(22, 32)
        draw.rectangle([x, horizon - bag_h, x + bag_w, horizon], fill=(65, 50, 38))
        # Highlight
        draw.rectangle([x, horizon - bag_h, x + bag_w, horizon - bag_h + 3], fill=(75, 60, 45))


def draw_beehives(draw: ImageDraw, width: int, height: int) -> None:
    """Draw two beehive skeps in the middle distance."""
    import random

    rng = random.Random(42)

    # Left hive
    hx1 = int(width * 0.35)
    hy1 = int(height * 0.40)
    draw.ellipse([hx1 - 25, hy1 - 30, hx1 + 25, hy1 + 20], fill=(120, 95, 60))
    draw.ellipse([hx1 - 22, hy1 - 25, hx1 + 22, hy1 + 15], fill=(140, 110, 70))
    # Entrance
    draw.ellipse([hx1 - 6, hy1 + 8, hx1 + 6, hy1 + 18], fill=(50, 40, 30))
    # Bees around left hive
    for _ in range(6):
        bx = hx1 + rng.randint(-35, 35)
        by = hy1 + rng.randint(-40, 15)
        draw.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(200, 160, 40))

    # Right hive
    hx2 = int(width * 0.58)
    hy2 = int(height * 0.38)
    draw.ellipse([hx2 - 28, hy2 - 32, hx2 + 28, hy2 + 22], fill=(130, 100, 65))
    draw.ellipse([hx2 - 24, hy2 - 27, hx2 + 24, hy2 + 17], fill=(150, 115, 75))
    draw.ellipse([hx2 - 6, hy2 + 10, hx2 + 6, hy2 + 20], fill=(50, 40, 30))
    # Bees around right hive
    for _ in range(5):
        bx = hx2 + rng.randint(-35, 35)
        by = hy2 + rng.randint(-40, 15)
        draw.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(200, 160, 40))


def draw_poppies(draw: ImageDraw, width: int, height: int) -> None:
    """Draw red poppies scattered across the foreground."""
    import random

    rng = random.Random(23)

    for _ in range(40):
        x = rng.randint(50, width - 50)
        y = rng.randint(int(height * 0.50), int(height * 0.85))
        size = rng.randint(4, 10)
        # Petal (red)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(180, 25, 20))
        draw.ellipse([x - size + 2, y - size + 2, x + size - 2, y + size - 2], fill=(200, 35, 30))
        # Center (black)
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(15, 10, 8))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(30, 25, 20))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 60, 40), width=3)

    # Title text
    title = "The Beekeeper's\nWar"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
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
    draw.text((ax, ay), author, fill=(200, 190, 180), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Beekeeper's War")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Trench silhouette
    draw_trench_silhouette(draw, WIDTH, HEIGHT)

    # Step 3: Beehives
    draw_beehives(draw, WIDTH, HEIGHT)

    # Step 4: Barbed wire
    draw_barbed_wire(draw, WIDTH, HEIGHT)

    # Step 5: Poppies
    draw_poppies(draw, WIDTH, HEIGHT)

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