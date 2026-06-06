#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Ballroom of Shadows."""

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
    """Deep mauve to dark violet to near-black gradient for gothic mystery feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((40, 10, 35), (90, 30, 70), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((90, 30, 70), (50, 15, 45), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((50, 15, 45), (10, 5, 15), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_floor(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a ballroom floor with perspective lines."""
    center_x = width // 2
    floor_start_y = int(height * 0.6)
    floor_end_y = height

    # Floor gradient
    for y in range(floor_start_y, floor_end_y):
        t = (y - floor_start_y) / (floor_end_y - floor_start_y)
        c = lerp_color((40, 15, 35), (15, 5, 20), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Perspective floor lines
    vanish_x = center_x
    vanish_y = int(height * 0.35)

    for i in range(-8, 9):
        if i == 0:
            continue
        spacing = 40 + abs(i) * 30
        x1 = center_x + i * spacing
        x2 = center_x + i * spacing * 3
        y1 = floor_start_y + 20
        y2 = height
        # Floor planks
        draw.line([(center_x, y1), (x2, y2)], fill=(60, 25, 50), width=2)
        # Reflected in reverse
        draw.line([(center_x, y1), (width - x2, y2)], fill=(60, 25, 50), width=2)


def draw_chandelier(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a chandelier at the top center."""
    cx, cy = width // 2, 120

    # Chain
    for i in range(6):
        draw.line([(cx, cy - 40), (cx, cy + i * 15)], fill=(180, 150, 100), width=2)

    # Main body - elliptical shape
    draw.ellipse([cx - 100, cy - 30, cx + 100, cy + 60], fill=None, outline=(180, 150, 100), width=3)
    draw.ellipse([cx - 80, cy - 15, cx + 80, cy + 45], fill=(160, 130, 80, 60), outline=(180, 150, 100), width=2)

    # Inner ring
    draw.ellipse([cx - 50, cy - 10, cx + 50, cy + 30], outline=(200, 170, 110), width=2)

    # Candle arms
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        arm_len = 70
        ax = cx + int(arm_len * math.cos(rad))
        ay = cy + 15 + int(arm_len * math.sin(rad) * 0.5)
        draw.line([(cx, cy + 15), (ax, ay)], fill=(180, 150, 100), width=2)
        # Flame glow
        fx = ax + int(10 * math.cos(rad))
        fy = ay - 15
        draw.ellipse([fx - 4, fy - 10, fx + 4, fy], fill=(255, 220, 100))
        draw.ellipse([fx - 8, fy - 14, fx + 8, fy - 2], fill=(255, 200, 80, 80))

    # Central glow
    draw.ellipse([cx - 60, cy - 20, cx + 60, cy + 40], fill=(180, 140, 80, 40))
    draw.ellipse([cx - 30, cy - 10, cx + 30, cy + 20], fill=(200, 160, 90, 60))

    # Light rays emanating upward
    for i in range(12):
        rad = math.radians(i * 30)
        rlen = 60
        rx = cx + int(rlen * math.cos(rad))
        ry = cy - 20 + int(rlen * math.sin(rad) * 0.3)
        draw.line([(cx, cy - 10), (rx, ry)], fill=(200, 170, 100, 40), width=1)


def draw_mirrors(draw: ImageDraw, width: int, height: int) -> None:
    """Draw arched mirrors on the left and right walls."""
    # Left mirror
    lx, ly = 80, 160
    lw, lh = 180, 350

    # Mirror arch (rectangle + half-ellipse top)
    draw.rectangle([lx, ly + 60, lx + lw, ly + lh], fill=(30, 15, 35, 180), outline=(140, 110, 80), width=3)
    draw.ellipse([lx, ly, lx + lw, ly + 120], fill=(30, 15, 35, 180), outline=(140, 110, 80), width=3)

    # Mirror surface shimmer
    for i in range(3):
        sx = lx + 20 + i * 50
        draw.line([(sx, ly + 40), (sx + 30, ly + lh - 20)], fill=(120, 80, 110, 30), width=1)

    # Reflection glow in mirror
    draw.ellipse([lx + 30, ly + 80, lx + lw - 30, ly + lh - 40], fill=(100, 50, 80, 20))

    # Right mirror
    rx, ry = width - 80 - 180, 160
    rw, rh = 180, 350

    draw.rectangle([rx, ry + 60, rx + rw, ry + rh], fill=(30, 15, 35, 180), outline=(140, 110, 80), width=3)
    draw.ellipse([rx, ry, rx + rw, ry + 120], fill=(30, 15, 35, 180), outline=(140, 110, 80), width=3)

    for i in range(3):
        sx = rx + 20 + i * 50
        draw.line([(sx, ry + 40), (sx + 30, ry + rh - 20)], fill=(120, 80, 110, 30), width=1)

    draw.ellipse([rx + 30, ry + 80, rx + rw - 30, ry + rh - 40], fill=(100, 50, 80, 20))


def draw_columns(draw: ImageDraw, width: int, height: int) -> None:
    """Draw ornate columns flanking the scene."""
    column_positions = [
        (30, 100, height),
        (width - 30, 100, height),
    ]

    for cx, cy_start, cy_end in column_positions:
        # Column body
        draw.rectangle([cx - 15, cy_start, cx + 15, cy_end], fill=(60, 30, 40))
        # Highlight
        draw.rectangle([cx - 5, cy_start, cx + 5, cy_end], fill=(80, 40, 55))
        # Capital
        draw.rectangle([cx - 25, cy_start, cx + 25, cy_start + 30], fill=(100, 70, 50))
        draw.rectangle([cx - 20, cy_start + 30, cx + 20, cy_start + 40], fill=(80, 55, 40))
        # Base
        draw.rectangle([cx - 25, cy_end - 30, cx + 25, cy_end], fill=(100, 70, 50))
        # Fluting lines
        for f in range(-8, 9, 4):
            if f == 0:
                continue
            draw.line([(cx + f, cy_start + 45), (cx + f, cy_end - 35)], fill=(70, 35, 45), width=1)


def draw_dancers(draw: ImageDraw, width: int, height: int) -> None:
    """Draw silhouetted dancers in the center of the floor."""
    cx, cy = width // 2, int(height * 0.42)

    # Main couple - waltzing
    # Man silhouette
    man_points = [
        (cx - 40, cy - 80),  # head
        (cx - 30, cy - 60),  # right shoulder
        (cx - 20, cy - 30),  # right arm extended
        (cx, cy),             # hand
        (cx + 5, cy + 10),   # hip
        (cx - 5, cy + 40),   # right leg
        (cx - 15, cy + 70),  # right foot
        (cx - 20, cy + 70),  # heel
        (cx - 25, cy + 40),  # left leg
        (cx - 40, cy - 10),  # left arm
        (cx - 50, cy - 30),  # left shoulder
    ]
    draw.polygon(man_points, fill=(20, 10, 20))

    # Man head detail
    draw.ellipse([cx - 48, cy - 90, cx - 32, cy - 74], fill=(25, 12, 22))

    # Woman silhouette
    woman_points = [
        (cx + 5, cy - 80),   # head
        (cx + 15, cy - 55),  # left shoulder
        (cx + 25, cy - 25),  # left arm
        (cx + 40, cy - 5),   # hand on shoulder
        (cx + 35, cy + 5),   # dress side
        (cx + 50, cy + 50),  # dress flare
        (cx + 55, cy + 70),  # hem
        (cx - 5, cy + 70),   # hem left
        (cx - 5, cy + 50),   # inner dress
        (cx, cy + 20),       # waist
        (cx, cy),            # hip
        (cx + 5, cy - 10),   # hand area
        (cx + 5, cy - 30),   # upper arm
    ]
    draw.polygon(woman_points, fill=(25, 12, 22))

    # Woman head detail
    draw.ellipse([cx - 2, cy - 90, cx + 14, cy - 74], fill=(25, 12, 22))

    # Hair up for woman
    draw.ellipse([cx, cy - 96, cx + 16, cy - 78], fill=(20, 8, 18))

    # Dress overlay - gold/mauve shimmer lines
    for ly in range(cy + 10, cy + 65, 8):
        spread = 20 + (ly - cy - 10) * 0.6
        draw.line(
            [(cx + 35 - int(spread * 2.5), ly), (cx + 35 + int(spread * 1.5), ly)],
            fill=(180, 120, 100, 30),
            width=1,
        )

    # Additional smaller dancers in background
    for i, (dx, dy, scale) in enumerate([
        (cx - 120, cy - 30, 0.5),
        (cx + 120, cy - 25, 0.5),
        (cx - 80, cy + 20, 0.4),
        (cx + 80, cy + 25, 0.4),
    ]):
        # Silhouette pairs
        draw.ellipse([dx - 6, dy - 12, dx + 6, dy], fill=(40, 20, 35, 80))
        draw.ellipse([dx + 8, dy - 10, dx + 18, dy + 2], fill=(40, 20, 35, 80))
        draw.line([(dx, dy), (dx - 5, dy + 20)], fill=(40, 20, 35, 60), width=2)
        draw.line([(dx + 12, dy), (dx + 17, dy + 20)], fill=(40, 20, 35, 60), width=2)


def draw_gold_accents(draw: ImageDraw, width: int, height: int) -> None:
    """Draw decorative gold accents and scrollwork."""
    # Top border cornice
    draw.rectangle([(0, 0), (width, 8)], fill=(140, 110, 80))
    draw.rectangle([(0, 8), (width, 12)], fill=(100, 75, 55))

    # Bottom border before panel
    draw.rectangle([(0, TITLE_PANEL_TOP - 4), (width, TITLE_PANEL_TOP)], fill=(140, 110, 80))

    # Decorative scrollwork at top
    cx = width // 2
    for i in range(-2, 3):
        sx = cx + i * 200
        draw.arc([sx - 40, 20, sx + 40, 80], 0, 180, fill=(160, 120, 80, 60), width=2)
        draw.arc([sx - 20, 35, sx + 20, 65], 180, 360, fill=(140, 100, 70, 40), width=1)

    # Small decorative diamonds
    for i in range(8):
        dx = 100 + i * 200
        draw.polygon([(dx, 14), (dx + 6, 20), (dx, 26), (dx - 6, 20)], fill=(180, 140, 90))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 8, 20, 220))

    # Gold border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 140, 90), width=3)
    draw.line([(0, panel_top + 3), (width, panel_top + 3)], fill=(100, 75, 50), width=1)

    # Decorative corner flourishes on panel
    for cx_pos in [100, width - 100]:
        draw.arc([cx_pos - 30, panel_top - 15, cx_pos + 30, panel_top + 15], 0, 180, fill=(180, 140, 90, 80), width=2)

    # Title text
    title = "The Ballroom\nof Shadows"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, white
    lines = title.split("\n")
    y_offset = panel_top + 60
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # Shadow for readability
        draw.text((tx + 2, y_offset + 2), line, fill=(0, 0, 0), font=title_font)
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 90

    # Decorative line
    line_y = y_offset + 5
    draw.line([(width // 2 - 100, line_y), (width // 2 + 100, line_y)], fill=(180, 140, 90), width=1)

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
    ay = line_y + 20
    draw.text((ax + 1, ay + 1), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, ay), author, fill=(200, 180, 160), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Ballroom of Shadows")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Ballroom floor with perspective
    draw_floor(draw, WIDTH, HEIGHT)

    # Step 3: Columns
    draw_columns(draw, WIDTH, HEIGHT)

    # Step 4: Mirrors on walls
    draw_mirrors(draw, WIDTH, HEIGHT)

    # Step 5: Chandelier
    draw_chandelier(draw, WIDTH, HEIGHT)

    # Step 6: Gold accents and decorative borders
    draw_gold_accents(draw, WIDTH, HEIGHT)

    # Step 7: Dancers
    draw_dancers(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, width=WIDTH, height=HEIGHT, font_paths=font_paths)

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