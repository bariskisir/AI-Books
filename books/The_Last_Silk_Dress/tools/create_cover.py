#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Silk Dress."""

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
    """Rich gold-to-mahogany gradient for the Gilded Age feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 40, 20), (140, 90, 40), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((140, 90, 40), (60, 20, 10), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 20, 10), (20, 10, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouette of the 1890s New York skyline."""
    rng = random.Random(42)
    buildings = [
        (50, 550, 120),
        (120, 400, 90),
        (210, 600, 140),
        (300, 450, 100),
        (380, 500, 110),
        (450, 350, 80),
        (510, 650, 150),
        (600, 480, 100),
        (670, 380, 85),
        (730, 550, 120),
        (800, 420, 95),
        (860, 600, 130),
        (940, 500, 110),
        (1020, 450, 100),
        (1090, 550, 120),
        (1160, 380, 85),
        (1230, 600, 140),
        (1320, 450, 100),
        (1390, 350, 80),
        (1460, 500, 110),
        (1530, 400, 90),
    ]

    sky_y = int(height * 0.45)
    for bx, bh, bw in buildings:
        # Building body
        b_color = (10, 8, 5, 200)
        draw.rectangle([bx, sky_y - bh, bx + bw, sky_y], fill=b_color)
        # Windows (small lit rectangles)
        for wy in range(sky_y - bh + 15, sky_y - 10, 25):
            for wx in range(bx + 8, bx + bw - 8, 18):
                if rng.random() < 0.3:
                    win_color = (255, 220, 140, 80)
                    draw.rectangle([wx, wy, wx + 6, wy + 10], fill=win_color)

    # Church spire
    spire_x, spire_y = 350, sky_y - 600
    draw.polygon(
        [(spire_x, spire_y), (spire_x - 10, spire_y + 50), (spire_x + 10, spire_y + 50)],
        fill=(15, 10, 5),
    )
    draw.rectangle(
        [spire_x - 20, spire_y + 50, spire_x + 20, sky_y],
        fill=(15, 10, 5),
    )

    # Brooklyn Bridge silhouette suggestion
    bridge_y = sky_y - 20
    for t in range(0, width, 4):
        bridge_x = t
        bridge_y_offset = int(15 * math.sin(t / 120))
        draw.rectangle([bridge_x, bridge_y + bridge_y_offset, bridge_x + 2, bridge_y + bridge_y_offset + 3], fill=(5, 3, 2, 150))


def draw_dress_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an elegant dress silhouette in the center."""
    cx, cy = width // 2, int(height * 0.38)
    # Dress shape - bustle era silhouette
    dress_points = [
        (cx - 40, cy - 120),  # head
        (cx + 40, cy - 120),
        (cx + 50, cy - 80),   # shoulders
        (cx + 65, cy + 10),   # waist
        (cx + 120, cy + 120), # skirt right
        (cx + 140, cy + 260),
        (cx - 140, cy + 260),  # hem left
        (cx - 120, cy + 120),
        (cx - 65, cy + 10),
        (cx - 50, cy - 80),
    ]

    # Draw dress as a semi-transparent overlay
    draw.polygon(
        dress_points,
        fill=(200, 180, 160, 80),
        outline=(220, 200, 180, 150),
        width=2,
    )

    # Decorative details on the dress
    # Waistline
    draw.line(
        [(cx - 65, cy + 10), (cx + 65, cy + 10)],
        fill=(230, 210, 190, 120),
        width=2,
    )

    # Neckline detail
    draw.arc(
        [cx - 40, cy - 120, cx + 40, cy - 80],
        start=0, end=180,
        fill=(230, 210, 190, 150),
        width=2,
    )


def draw_pearls(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered pearl decorations."""
    rng = random.Random(7)
    for _ in range(60):
        x = rng.randint(100, width - 100)
        y = rng.randint(int(height * 0.15), int(height * 0.55))
        size = rng.randint(3, 7)
        # Pearl glow
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(230, 225, 220, 60),
        )
        # Pearl body
        draw.ellipse(
            [x - size // 2, y - size // 2, x + size // 2, y + size // 2],
            fill=(240, 235, 230, 200),
        )
        # Highlight
        draw.ellipse(
            [x - size // 4, y - size // 4, x + size // 4, y + size // 4],
            fill=(255, 255, 255, 180),
        )


def draw_gold_details(draw: ImageDraw, width: int, height: int) -> None:
    """Draw decorative gold filigree near the dress."""
    cx, cy = width // 2, int(height * 0.38)
    rng = random.Random(13)

    # Decorative swirls around the dress
    for angle_start in range(0, 360, 60):
        rad = math.radians(angle_start)
        r = 180
        sx = cx + int(r * math.cos(rad))
        sy = cy + int(r * math.sin(rad))

        # Small decorative swirl
        swirl_points = []
        for t in range(21):
            st = t / 20
            s_angle = st * math.pi * 2 + rad
            s_r = 15 + st * 25
            px = sx + int(s_r * math.cos(s_angle))
            py = sy + int(s_r * math.sin(s_angle))
            swirl_points.append((px, py))

        draw.line(swirl_points, fill=(200, 170, 80, 100), width=2)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 10, 8, 230))

    # Gold border at top of panel
    draw.line([(100, panel_top), (width - 100, panel_top)], fill=(180, 150, 60), width=3)

    # Gold accent lines
    draw.line([(200, panel_top + 10), (width - 200, panel_top + 10)], fill=(180, 150, 60, 100), width=1)

    # Title text
    title = "The Last\nSilk Dress"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered, in WHITE
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(245, 240, 235), font=title_font)
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
    ay = y_offset + 50
    draw.text((ax, ay), author, fill=(200, 185, 160), font=author_font)

    # Decorative line below author
    draw.line([(500, ay + 50), (width - 500, ay + 50)], fill=(180, 150, 60, 100), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Silk Dress")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: New York skyline silhouette
    draw_skyline(draw, WIDTH, HEIGHT)

    # Step 3: Pearl decorations
    draw_pearls(draw, WIDTH, HEIGHT)

    # Step 4: Gold filigree details
    draw_gold_details(draw, WIDTH, HEIGHT)

    # Step 5: Dress silhouette
    draw_dress_silhouette(draw, WIDTH, HEIGHT)

    # Step 6: Title panel at bottom
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