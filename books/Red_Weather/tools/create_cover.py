#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for Red Weather (Climate Thriller)."""

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
    """Toxic sky gradient: dark crimson at top, toxic yellow-green mid, black-red at bottom."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((80, 10, 10), (180, 50, 20), t)
        elif y < height * 0.5:
            t = (y - height * 0.3) / (height * 0.2)
            c = lerp_color((180, 50, 20), (200, 160, 40), t)
        elif y < height * 0.7:
            t = (y - height * 0.5) / (height * 0.2)
            c = lerp_color((200, 160, 40), (140, 30, 20), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((140, 30, 20), (20, 5, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_toxic_clouds(draw: ImageDraw, width: int, height: int) -> None:
    """Draw toxic clouds in the sky using ellipses."""
    rng = random.Random(101)
    cloud_color = (180, 150, 50, 80)
    for _ in range(30):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.45))
        w = rng.randint(80, 250)
        h = rng.randint(30, 80)
        alpha = rng.randint(30, 80)
        c = (180, 160, 60, alpha) if rng.random() < 0.5 else (200, 80, 40, alpha)
        draw.ellipse([x, y, x + w, y + h], fill=c)


def draw_red_ocean(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the red-stained ocean in the lower portion with wave patterns."""
    ocean_top = int(height * 0.55)
    for y in range(ocean_top, int(height * 0.85)):
        t = (y - ocean_top) / (height * 0.3)
        c = lerp_color((160, 30, 20), (100, 10, 10), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_waves(draw: ImageDraw, width: int, height: int) -> None:
    """Draw crimson wave lines across the ocean surface."""
    ocean_top = int(height * 0.55)
    rng = random.Random(202)
    for i in range(20):
        y_base = ocean_top + rng.randint(5, int(height * 0.25))
        points = []
        for x in range(0, width + 20, 10):
            y = y_base + int(math.sin((x + i * 50) * 0.008) * 10) + rng.randint(-3, 3)
            points.append((x, y))
        wave_color = (180, 40, 30, 100) if i % 2 == 0 else (120, 20, 15, 80)
        draw.line(points, fill=wave_color, width=rng.randint(2, 5))


def draw_research_vessel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouette of a research vessel on the ocean."""
    ship_y = int(height * 0.58)
    cx = width // 2 + 80

    # Hull
    hull_points = [
        (cx - 180, ship_y),
        (cx - 160, ship_y + 40),
        (cx + 160, ship_y + 40),
        (cx + 180, ship_y),
    ]
    draw.polygon(hull_points, fill=(10, 5, 5))

    # Deck house
    draw.rectangle([cx - 60, ship_y - 50, cx + 60, ship_y], fill=(15, 10, 10))

    # Bridge
    draw.rectangle([cx - 35, ship_y - 75, cx + 35, ship_y - 50], fill=(20, 15, 15))

    # Bridge windows (dim light)
    for wx in range(-20, 25, 15):
        draw.rectangle([cx + wx, ship_y - 70, cx + wx + 8, ship_y - 55], fill=(200, 180, 60, 120))

    # Smokestack
    draw.rectangle([cx - 15, ship_y - 110, cx + 15, ship_y - 75], fill=(10, 5, 5))

    # Mast
    draw.line([(cx - 80, ship_y), (cx - 80, ship_y - 120)], fill=(5, 5, 5), width=3)
    draw.line([(cx + 80, ship_y), (cx + 80, ship_y - 100)], fill=(5, 5, 5), width=3)

    # Antenna dish on mast
    draw.ellipse([cx - 85, ship_y - 130, cx - 75, ship_y - 120], fill=(30, 20, 15))

    # A-frame at stern
    aframe_points = [
        (cx + 140, ship_y),
        (cx + 130, ship_y - 60),
        (cx + 150, ship_y - 60),
        (cx + 160, ship_y),
    ]
    draw.polygon(aframe_points, fill=(10, 5, 5))


def draw_toxic_wisps(draw: ImageDraw, width: int, height: int) -> None:
    """Draw toxic yellow-green wisps rising from the ocean."""
    rng = random.Random(303)
    ocean_top = int(height * 0.55)
    for _ in range(15):
        x = rng.randint(100, width - 100)
        y_start = ocean_top + rng.randint(0, 80)
        wisp_color = (180, 200, 50, rng.randint(20, 50))
        points = []
        for step in range(30):
            px = x + int(math.sin(step * 0.5 + rng.random()) * 30)
            py = y_start - step * 8
            points.append((px, py))
        draw.line(points, fill=wisp_color, width=rng.randint(3, 8))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 5, 5, 220))

    # Subtle red border at top
    draw.line([(0, panel_top), (width, panel_top)], fill=(140, 30, 20), width=3)

    # Title text - use arialbd.ttf
    title = "Red Weather"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        try:
            title_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), title_font_size)
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
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        try:
            author_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), author_font_size)
        except Exception:
            author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = ty + 120
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)


def draw_red_particles(draw: ImageDraw, width: int, height: int) -> None:
    """Draw small red particles/cells floating in the air - the algae aerosolized."""
    rng = random.Random(404)
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.7))
        size = rng.randint(2, 6)
        alpha = rng.randint(100, 200)
        color = (180, 30, 20, alpha) if rng.random() < 0.7 else (200, 180, 50, alpha)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=color)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (toxic sky)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Toxic clouds
    draw_toxic_clouds(draw, WIDTH, HEIGHT)

    # Step 3: Red-stained ocean
    draw_red_ocean(draw, WIDTH, HEIGHT)

    # Step 4: Crimson wave lines
    draw_waves(draw, WIDTH, HEIGHT)

    # Step 5: Research vessel silhouette
    draw_research_vessel(draw, WIDTH, HEIGHT)

    # Step 6: Toxic wisps rising from ocean
    draw_toxic_wisps(draw, WIDTH, HEIGHT)

    # Step 7: Red particles (aerosolized algae)
    draw_red_particles(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
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