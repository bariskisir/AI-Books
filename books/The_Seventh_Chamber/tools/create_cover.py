#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Seventh Chamber."""

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
    """Desert gold at top to deep tomb darkness at bottom."""
    for y in range(height):
        if y < height * 0.35:
            t = y / (height * 0.35)
            c = lerp_color((210, 170, 90), (180, 130, 60), t)
        elif y < height * 0.65:
            t = (y - height * 0.35) / (height * 0.30)
            c = lerp_color((180, 130, 60), (100, 70, 40), t)
        else:
            t = (y - height * 0.65) / (height * 0.35)
            c = lerp_color((100, 70, 40), (20, 15, 10), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_dunes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw undulating desert sand dunes across the middle ground."""
    import random

    rng = random.Random(3)

    base_y = int(height * 0.55)
    for dune_idx in range(6):
        points = []
        dune_height = rng.randint(30, 80)
        dune_width = rng.randint(200, 500)
        start_x = rng.randint(-100, width - 100)

        for x in range(0, width + 20, 10):
            rel_x = x - start_x
            peak = math.sin(rel_x * math.pi / dune_width) * dune_height
            if peak < 0:
                peak *= 0.3
            y = base_y + dune_idx * 20 + peak
            points.append((x, y))

        shade = 60 + dune_idx * 10
        draw.polygon(points + [(width, height), (0, height)], fill=(shade, shade - 10, shade - 20))


def draw_rock_face(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the cliff face and tomb entrance."""
    cx = width // 2

    # Cliff face - large irregular shape
    cliff_points = [
        (cx - 350, int(height * 0.20)),
        (cx - 280, int(height * 0.18)),
        (cx - 150, int(height * 0.15)),
        (cx + 150, int(height * 0.15)),
        (cx + 280, int(height * 0.18)),
        (cx + 380, int(height * 0.22)),
        (cx + 400, int(height * 0.40)),
        (cx + 390, int(height * 0.50)),
        (cx + 360, int(height * 0.58)),
        (cx + 320, int(height * 0.65)),
        (cx - 320, int(height * 0.65)),
        (cx - 360, int(height * 0.58)),
        (cx - 390, int(height * 0.50)),
        (cx - 400, int(height * 0.40)),
    ]
    draw.polygon(cliff_points, fill=(130, 110, 80))

    # Cliff face shading - vertical striations
    for sx in range(cx - 350, cx + 380, 15):
        shade_offset = (sx % 30) - 15
        draw.line(
            [(sx, int(height * 0.18)), (sx, int(height * 0.65))],
            fill=(max(0, 130 + shade_offset), max(0, 110 + shade_offset), max(0, 80 + shade_offset)),
            width=2,
        )

    # Tomb entrance - dark rectangle
    door_w, door_h = 120, 180
    door_x = cx - door_w // 2
    door_y = int(height * 0.35)
    draw.rectangle([door_x, door_y, door_x + door_w, door_y + door_h], fill=(10, 8, 5))

    # Doorframe
    frame_color = (160, 140, 100)
    draw.rectangle([door_x - 8, door_y - 8, door_x + door_w + 8, door_y], fill=frame_color)
    draw.rectangle([door_x - 8, door_y, door_x, door_y + door_h], fill=frame_color)
    draw.rectangle([door_x + door_w, door_y, door_x + door_w + 8, door_y + door_h], fill=frame_color)
    draw.rectangle([door_x - 8, door_y + door_h, door_x + door_w + 8, door_y + door_h + 8], fill=frame_color)

    # Door arch
    draw.arc(
        [door_x - 8, door_y - 60, door_x + door_w + 8, door_y + 20],
        start=180, end=0, fill=frame_color, width=8,
    )

    # Carved hieroglyphs above door
    glyph_positions = [(cx - 100, int(height * 0.28)), (cx + 30, int(height * 0.26)), (cx - 50, int(height * 0.30))]
    for gx, gy in glyph_positions:
        # Ankh-like shapes
        draw.ellipse([gx, gy, gx + 12, gy + 6], fill=(170, 150, 110))
        draw.rectangle([gx + 5, gy + 6, gx + 7, gy + 20], fill=(170, 150, 110))


def draw_torchlight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw torchlight glow emanating from the tomb entrance."""
    cx = width // 2
    door_y = int(height * 0.35)
    door_h = 180

    # Torch glow - multiple semi-transparent layers
    for radius in [250, 180, 120, 70]:
        alpha = max(10, 60 - radius // 5)
        draw.ellipse(
            [cx - radius, door_y + door_h // 2 - radius, cx + radius, door_y + door_h // 2 + radius],
            fill=(255, 200, 100, alpha),
        )

    # Torch flame inside door
    flame_points = [
        (cx - 8, door_y + 10),
        (cx, door_y - 15),
        (cx + 8, door_y + 10),
    ]
    draw.polygon(flame_points, fill=(255, 180, 50, 200))
    draw.polygon([(cx - 4, door_y + 5), (cx, door_y - 5), (cx + 4, door_y + 5)], fill=(255, 255, 200, 220))

    # Light ray emanating from door
    for angle in range(-20, 25, 5):
        rad = math.radians(angle)
        x_end = int(cx + math.sin(rad) * 300)
        y_end = int(door_y + door_h // 2 + math.cos(rad) * 200)
        draw.line([(cx, door_y + door_h // 2), (x_end, y_end)], fill=(255, 220, 150, 15), width=6)


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stars in the upper portion of the cover."""
    import random

    rng = random.Random(17)
    star_y_max = int(height * 0.25)

    for _ in range(80):
        x = rng.randint(50, width - 50)
        y = rng.randint(10, star_y_max)
        size = rng.randint(1, 3)
        brightness = rng.randint(180, 255)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, brightness, 200))


def draw_hieroglyphic_border(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a decorative border of Egyptian-style symbols along the sides."""
    import random

    rng = random.Random(42)
    symbols = [
        (0, 0, 15, 8),
        (0, 0, 8, 15),
        (0, 0, 12, 12),
        (0, 0, 6, 18),
    ]

    for side in range(2):
        x_base = 15 if side == 0 else width - 25
        for sy in range(100, height - 100, 80):
            sx, sy_off, sw, sh = symbols[rng.randint(0, len(symbols) - 1)]
            draw.ellipse(
                [x_base + sx, sy + sy_off, x_base + sx + sw, sy + sy_off + sh],
                fill=(180, 160, 120, 80),
            )


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 12, 8, 220))

    # Gold border at top of panel
    draw.line([(200, panel_top), (width - 200, panel_top)], fill=(180, 150, 70), width=3)
    draw.line([(200, panel_top + 1), (width - 200, panel_top + 1)], fill=(100, 80, 40), width=1)

    # Title text
    title = "The Seventh\nChamber"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    lines = title.split("\n")
    y_offset = panel_top + 90
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 240), font=title_font)
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
    draw.text((ax, ay), author, fill=(200, 180, 140), font=author_font)

    # Gold line below author
    draw.line([(400, ay + 50), (width - 400, ay + 50)], fill=(180, 150, 70, 150), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Sand dunes
    draw_dunes(draw, WIDTH, HEIGHT)

    # Step 3: Rock face and tomb entrance
    draw_rock_face(draw, WIDTH, HEIGHT)

    # Step 4: Torchlight
    draw_torchlight(draw, WIDTH, HEIGHT)

    # Step 5: Stars
    draw_stars(draw, WIDTH, HEIGHT)

    # Step 6: Hieroglyphic border elements
    draw_hieroglyphic_border(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
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