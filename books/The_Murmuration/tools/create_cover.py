#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Murmuration."""

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
    """Twilight sky: deep violet at top, amber on horizon, dark at bottom."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((15, 5, 30), ((80, 20, 60)), t)
        elif y < height * 0.55:
            t = (y - height * 0.4) / (height * 0.15)
            c = lerp_color((80, 20, 60), ((200, 90, 40)), t)
        elif y < height * 0.6:
            t = (y - height * 0.55) / (height * 0.05)
            c = lerp_color((200, 90, 40), ((240, 160, 60)), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((240, 160, 60), ((10, 8, 15)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_starling_birds(draw: ImageDraw, width: int, height: int) -> None:
    """Draw hundreds of small bird shapes in murmuration patterns across the sky."""
    rng = random.Random(13)

    # Generate murmuration particles
    for _ in range(1200):
        x = rng.randint(100, width - 100)
        # Birds cluster between top and mid-section, thinning out
        if rng.random() < 0.7:
            y = rng.randint(50, int(height * 0.5))
        else:
            y = rng.randint(int(height * 0.5), int(height * 0.7))

        size = rng.uniform(1.5, 5.0)
        # Opacity varies
        alpha = rng.randint(60, 220)
        dark = rng.randint(10, 50)

        # Each starling is a tiny V or short line
        angle = rng.uniform(-0.3, 0.3)
        dx = int(math.cos(angle) * size * 3)
        dy = int(math.sin(angle) * size * 2)

        draw.line(
            [x - dx, y - dy, x + dx, y + dy],
            fill=(dark, dark, dark, alpha),
            width=max(1, int(size * 0.8)),
        )

        # Some with slight wing indication
        if size > 3 and rng.random() < 0.3:
            wx = int(dx * 0.6)
            wy = int(dy * 0.6 + 2)
            draw.line(
                [x - wx, y - wy, x + wx, y - wy],
                fill=(dark, dark, dark, alpha),
                width=1,
            )


def draw_murmuration_swirl(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dense swirl of birds forming a murmuration wave."""
    rng = random.Random(7)

    cx, cy = width // 2, int(height * 0.3)
    for i in range(800):
        angle = rng.uniform(0, math.pi * 2)
        dist = rng.uniform(20, 350)
        spiral_factor = dist / 350
        x = cx + int(math.cos(angle + spiral_factor * 2) * dist)
        y = cy + int(math.sin(angle + spiral_factor * 3) * dist * 0.6) - int(spiral_factor * 80)

        if x < 0 or x >= width or y < 0 or y >= height:
            continue

        alpha = rng.randint(80, 200)
        s = rng.uniform(2, 4)
        draw.line(
            [x - int(s), y - int(s * 0.5), x + int(s), y + int(s * 0.5)],
            fill=(20, 15, 25, alpha),
            width=max(1, int(s * 0.6)),
        )


def draw_lone_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small lone figure standing on the observation platform."""
    fx = width // 2 + 60
    fy = int(height * 0.72)

    # Figure - small silhouette
    # Head
    draw.ellipse([fx - 6, fy - 18, fx + 6, fy - 8], fill=(5, 3, 10))
    # Body
    draw.rectangle([fx - 5, fy - 8, fx + 5, fy + 12], fill=(5, 3, 10))
    # Legs
    draw.line([fx - 3, fy + 12, fx - 4, fy + 24], fill=(5, 3, 10), width=3)
    draw.line([fx + 3, fy + 12, fx + 4, fy + 24], fill=(5, 3, 10), width=3)

    # Camera tripod beside figure
    draw.line([fx + 25, fy, fx + 25, fy + 28], fill=(5, 3, 10), width=2)
    draw.line([fx + 25, fy + 28, fx + 20, fy + 35], fill=(5, 3, 10), width=2)
    draw.line([fx + 25, fy + 28, fx + 30, fy + 35], fill=(5, 3, 10), width=2)
    # Camera body
    draw.rectangle([fx + 21, fy - 3, fx + 29, fy + 3], fill=(5, 3, 10))
    # Lens
    draw.rectangle([fx + 29, fy - 2, fx + 38, fy + 2], fill=(5, 3, 10))


def draw_reed_bed(draw: ImageDraw, width: int, height: int) -> None:
    """Draw dark reed silhouettes along the bottom of the sky area."""
    rng = random.Random(5)
    for x in range(0, width, 6):
        h = rng.randint(30, 90)
        base_y = int(height * 0.72)
        draw.line(
            [x, base_y - h, x, base_y],
            fill=(8, 6, 12),
            width=1,
        )
        # Slight bend
        if rng.random() < 0.3:
            draw.line(
                [x, base_y - h, x + 2, base_y - h - 5],
                fill=(8, 6, 12),
                width=1,
            )


def draw_amber_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a glowing amber patch near the horizon where sun sets."""
    cx, cy = width // 2, int(height * 0.55)
    for r in range(60, 200, 5):
        alpha = max(0, 60 - r // 4)
        draw.ellipse(
            [cx - r, cy - r // 2, cx + r, cy + r // 2],
            fill=(240, 160, 60, alpha),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 8, 15, 220))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(200, 100, 50), width=2)

    # Title text using arialbd.ttf
    title = "The Murmuration"
    title_font_size = 84
    try:
        title_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = ty + 110
    draw.text((ax, ay), author, fill=(200, 180, 160), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Murmuration")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (twilight sky)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Amber glow near horizon
    draw_amber_glow(draw, WIDTH, HEIGHT)

    # Step 3: Murmuration swirl in the sky
    draw_murmuration_swirl(draw, WIDTH, HEIGHT)

    # Step 4: Starling birds scattered across sky
    draw_starling_birds(draw, WIDTH, HEIGHT)

    # Step 5: Reed bed silhouettes
    draw_reed_bed(draw, WIDTH, HEIGHT)

    # Step 6: Lone figure with camera
    draw_lone_figure(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    draw_title_panel(draw, WIDTH, HEIGHT)

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