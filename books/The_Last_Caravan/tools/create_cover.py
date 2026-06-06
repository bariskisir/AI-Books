#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Caravan."""

from __future__ import annotations

import argparse
import json
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
    """Gold to deep indigo desert gradient."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((210, 170, 80), (180, 130, 50), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((180, 130, 50), (120, 80, 60), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((120, 80, 60), (20, 10, 40), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_dunes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw sweeping sand dune shapes across the lower portion."""
    # Background dune
    points_bg = []
    for x in range(0, width + 10, 10):
        y = int(height * 0.55 + 60 * __import__("math").sin(x * 0.004 + 1.2) + 40 * __import__("math").sin(x * 0.008))
        points_bg.append((x, y))
    points_bg.append((width, height))
    points_bg.append((0, height))
    draw.polygon(points_bg, fill=(160, 110, 50, 180))

    # Mid dune
    points_mid = []
    for x in range(0, width + 10, 10):
        y = int(height * 0.62 + 50 * __import__("math").sin(x * 0.005 + 0.5) + 30 * __import__("math").sin(x * 0.009 + 2.0))
        points_mid.append((x, y))
    points_mid.append((width, height))
    points_mid.append((0, height))
    draw.polygon(points_mid, fill=(120, 75, 45, 200))

    # Foreground dune
    points_fg = []
    for x in range(0, width + 10, 10):
        y = int(height * 0.70 + 40 * __import__("math").sin(x * 0.006 + 3.0) + 25 * __import__("math").sin(x * 0.011 + 0.7))
        points_fg.append((x, y))
    points_fg.append((width, height))
    points_fg.append((0, height))
    draw.polygon(points_fg, fill=(80, 50, 30, 220))


def draw_caravan(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small camel caravan silhouette on the dunes."""
    import math

    caravan_y = int(height * 0.50)
    base_x = int(width * 0.25)

    # Draw 5 camels in silhouette
    for i in range(5):
        cx = base_x + i * 55 + int(15 * math.sin(i * 0.7))
        cy = caravan_y + int(10 * math.sin(i * 1.3))

        # Body
        draw.ellipse([cx - 18, cy - 12, cx + 18, cy + 8], fill=(40, 25, 15))

        # Hump
        draw.ellipse([cx - 8, cy - 22, cx + 8, cy - 2], fill=(40, 25, 15))

        # Neck and head
        draw.line([cx + 14, cy - 5, cx + 22, cy - 28, cx + 26, cy - 30], fill=(40, 25, 15), width=3)

        # Legs
        draw.line([cx - 12, cy + 8, cx - 14, cy + 30], fill=(40, 25, 15), width=2)
        draw.line([cx + 10, cy + 8, cx + 12, cy + 30], fill=(40, 25, 15), width=2)

        # Rider (small figure)
        draw.ellipse([cx - 5, cy - 28, cx + 5, cy - 20], fill=(40, 25, 15))


def draw_sun(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large hot sun in the upper portion."""
    cx, cy = int(width * 0.65), int(height * 0.15)
    radius = 80

    # Glow layers
    for r in range(radius * 3, radius, -8):
        alpha = max(0, min(60, 60 - (radius * 3 - r) // 8))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 200, 100, alpha))

    # Sun body
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], fill=(255, 180, 50))


def draw_oasis(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small oasis with palm trees in the distance."""
    import math

    ox, oy = int(width * 0.72), int(height * 0.48)

    # Water pool
    draw.ellipse([ox - 40, oy - 8, ox + 40, oy + 8], fill=(80, 140, 180, 120))
    draw.ellipse([ox - 35, oy - 5, ox + 35, oy + 5], fill=(60, 120, 160, 100))

    # Palm trees
    for i in range(3):
        px = ox - 25 + i * 25
        py = oy - 5

        # Trunk
        trunk_points = []
        for s in range(10):
            t = s / 10
            px_t = px - int(4 * t * t) + int(3 * math.sin(t * 3))
            py_t = py - int(60 * t)
            trunk_points.append((px_t, py_t))
        draw.line(trunk_points, fill=(50, 35, 20), width=4)

        # Fronds
        top_x, top_y = trunk_points[-1]
        for angle in range(-60, 90, 30):
            rad = math.radians(angle - 90)
            end_x = top_x + int(25 * math.cos(rad))
            end_y = top_y + int(25 * math.sin(rad))
            draw.line([top_x, top_y, end_x, end_y], fill=(30, 80, 30), width=2)


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a scattering of stars in the upper sky."""
    import random

    rng = random.Random(13)
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.35))
        size = rng.randint(1, 3)
        brightness = rng.randint(180, 255)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, brightness, 200))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        c = lerp_color((15, 10, 30), (5, 3, 15), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Top border accent - gold line
    draw.line([(0, panel_top), (width, panel_top)], fill=(210, 170, 80), width=3)

    # Decorative lines on sides
    for offset in [50, width - 50]:
        draw.line([(offset, panel_top + 15), (offset, panel_top + 25)], fill=(210, 170, 80), width=2)

    # Title text
    title = "The Last\nCaravan"
    title_font_size = 82
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    y_offset = panel_top + 80
    lines = title.split("\n")
    for idx, line in enumerate(lines):
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # Shadow for readability
        draw.text((tx + 2, y_offset + 2), line, fill=(0, 0, 0), font=title_font)
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
    ay = y_offset + 30

    # Author shadow
    draw.text((ax + 2, ay + 2), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, ay), author, fill=(255, 200, 100), font=author_font)

    # Bottom decorative line
    draw.line([(int(width * 0.35), ay + 55), (int(width * 0.65), ay + 55)], fill=(210, 170, 80), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Sun
    draw_sun(draw, WIDTH, HEIGHT)

    # Step 3: Stars in upper sky
    draw_stars(draw, WIDTH, HEIGHT)

    # Step 4: Dunes
    draw_dunes(draw, WIDTH, HEIGHT)

    # Step 5: Oasis
    draw_oasis(draw, WIDTH, HEIGHT)

    # Step 6: Camel caravan
    draw_caravan(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
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