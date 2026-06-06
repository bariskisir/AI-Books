#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Lighthouse at the End."""

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
    """Dark seafoam to deep indigo to near-black gradient for lighthouse horror feel."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((10, 35, 30), (5, 20, 40), t)
        elif y < height * 0.7:
            t = (y - height * 0.3) / (height * 0.4)
            c = lerp_color((5, 20, 40), (3, 5, 20), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((3, 5, 20), (1, 1, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_lighthouse(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the lighthouse tower with spiral stairs visible through a cutaway."""
    cx = width // 2
    tower_base_y = int(height * 0.75)
    tower_top_y = int(height * 0.15)
    tower_w = 120
    tower_h = tower_base_y - tower_top_y

    # Tower body
    draw.rectangle([cx - tower_w // 2, tower_top_y, cx + tower_w // 2, tower_base_y], fill=(220, 225, 230, 200))

    # Tower stripes (red/white alternating)
    stripe_h = 30
    for i in range(tower_top_y, tower_base_y, stripe_h * 2):
        draw.rectangle([cx - tower_w // 2, i, cx + tower_w // 2, min(i + stripe_h, tower_base_y)], fill=(180, 50, 40, 180))

    # Spiral stairs visible through cutaway (center strip)
    stair_x1 = cx - 25
    stair_x2 = cx + 25
    for step_y in range(tower_top_y + 60, tower_base_y - 40, 18):
        draw.line([(stair_x1, step_y), (stair_x2, step_y + 6)], fill=(180, 160, 140), width=3)
        # Small figure on one stair
        if step_y == tower_top_y + 60 + 18 * 8:
            draw.ellipse([cx - 6, step_y - 12, cx + 6, step_y], fill=(30, 30, 35))
            draw.rectangle([cx - 4, step_y, cx + 4, step_y + 10], fill=(40, 40, 45))

    # Lens room / lantern room at top
    lr_top = tower_top_y - 60
    lr_bot = tower_top_y
    draw.rectangle([cx - 40, lr_top, cx + 40, lr_bot], fill=(200, 205, 210))
    # Glass panes
    for px in range(-3, 4):
        pane_x = cx + px * 10
        draw.rectangle([pane_x - 4, lr_top + 5, pane_x + 4, lr_bot - 5], fill=(180, 200, 210, 150))

    # Light beam from lens room - angled
    beam_color = (255, 200, 100, 40)
    for angle in range(-30, 35, 5):
        rad = math.radians(angle)
        end_x = cx + int(math.cos(rad) * width)
        end_y = lr_top - 50
        draw.line([(cx, lr_top + 10), (end_x, end_y)], fill=beam_color, width=int(8 + abs(angle) * 0.3))

    # Central glow in lens room
    draw.ellipse([cx - 15, lr_top + 10, cx + 15, lr_bot - 10], fill=(255, 220, 100, 200))
    draw.ellipse([cx - 8, lr_top + 15, cx + 8, lr_bot - 15], fill=(255, 255, 200, 220))

    # Gallery (balcony rail)
    gallery_y = lr_top
    draw.line([(cx - 50, gallery_y), (cx + 50, gallery_y)], fill=(100, 100, 105), width=3)
    for rail_x in range(cx - 45, cx + 50, 12):
        draw.line([(rail_x, gallery_y), (rail_x, gallery_y - 12)], fill=(100, 100, 105), width=2)

    # Door at base of tower
    door_w, door_h = 40, 60
    draw.rectangle([cx - door_w // 2, tower_base_y - door_h, cx + door_w // 2, tower_base_y], fill=(50, 40, 35))
    draw.arc([cx - 10, tower_base_y - door_h, cx + 10, tower_base_y - door_h + 15], 0, 180, fill=(255, 220, 100, 120), width=2)

    # Warm light spilling from door
    spill = draw.rectangle([cx - 30, tower_base_y - 5, cx + 30, tower_base_y + 30], fill=(255, 200, 100, 60))


def draw_sea(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the sea at the base with suggestion of submerged city."""
    sea_top = int(height * 0.72)
    # Ocean surface
    for y in range(sea_top, height):
        t = (y - sea_top) / (height - sea_top)
        c = lerp_color((10, 15, 25), ((2, 4, 12)), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Wave lines on surface
    wave_y = sea_top
    for x in range(0, width, 4):
        offset = int(math.sin(x * 0.02) * 3)
        draw.point((x, wave_y + offset), fill=(60, 80, 100, 80))

    # Submerged city lights
    import random
    rng = random.Random(42)
    for _ in range(60):
        x = rng.randint(50, width - 50)
        y = rng.randint(sea_top + 20, sea_top + 300)
        size = rng.randint(2, 6)
        brightness = rng.randint(80, 200)
        color = (brightness, brightness, 180, 120)
        # Faint city structure shapes
        if rng.random() < 0.15:
            tw = rng.randint(10, 30)
            th = rng.randint(20, 60)
            draw.rectangle([x - tw // 2, y - th, x + tw // 2, y], fill=(20, 30, 50, 100))
        # City lights
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)
        # Brighter center
        draw.ellipse([x - size // 3, y - size // 3, x + size // 3, y + size // 3], fill=(brightness + 55, brightness + 55, 255, 150))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 12, 18, 230))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 70, 80), width=2)

    # Title text - use arialbd (bold arial)
    title = "The Lighthouse\nat the End"
    title_font_size = 72
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
        # White text with a subtle glow
        draw.text((tx + 2, y_offset + 2), line, fill=(40, 50, 60), font=title_font)
        draw.text((tx, y_offset), line, fill=(240, 240, 245), font=title_font)
        y_offset += 95

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    author_line = f"by {author}"
    try:
        abbox = draw.textbbox((0, 0), author_line, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = y_offset + 35
    draw.text((ax, ay), author_line, fill=(180, 185, 195), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Lighthouse at the End")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (dark seafoam to black)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Sea with submerged city
    draw_sea(draw, WIDTH, HEIGHT)

    # Step 3: Lighthouse tower with cutaway stairs and glowing lens
    draw_lighthouse(draw, WIDTH, HEIGHT)

    # Step 4: Title panel at bottom
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
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