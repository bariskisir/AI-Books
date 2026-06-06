#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Vanishing of Eleanor Rigby."""

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
    """Dark blue-grey to near-black gradient for psychological mystery mood."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((20, 25, 40), ((10, 12, 25)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((10, 12, 25), ((5, 5, 15)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((5, 5, 15), ((2, 2, 8)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_hotel_corridor(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a receding hotel corridor with doors on both sides."""
    vanishing_y = int(height * 0.35)
    vanishing_x = width // 2

    # Floor
    for y in range(vanishing_y + 80, int(height * 0.75)):
        t = (y - (vanishing_y + 80)) / (height * 0.75 - (vanishing_y + 80))
        floor_w = int(400 + t * 1000)
        alpha = int(30 + t * 60)
        left = max(0, vanishing_x - floor_w // 2)
        right = min(width, vanishing_x + floor_w // 2)
        draw.line([(left, y), (right, y)], fill=(30, 28, 35, alpha))

    # Ceiling
    for y in range(vanishing_y, vanishing_y + 60):
        t = (y - vanishing_y) / 60
        ceil_w = int(200 + t * 400)
        left = max(0, vanishing_x - ceil_w // 2)
        right = min(width, vanishing_x + ceil_w // 2)
        draw.line([(left, y), (right, y)], fill=(15, 14, 20, 80))

    # Walls - left side doors
    for i in range(5):
        door_top = vanishing_y + 50 + i * 70
        door_bottom = door_top + 55
        t = i / 4
        door_width = int(60 + t * 100)
        door_x = vanishing_x - int(120 + t * 300)
        if door_x < 0:
            continue
        # Door frame
        draw.rectangle([door_x, door_top, door_x + door_width, door_bottom], fill=(25, 22, 30, 180))
        # Door panel
        draw.rectangle([door_x + 5, door_top + 5, door_x + door_width - 5, door_bottom - 5], fill=(35, 32, 42, 200))
        # Door number
        if i == 1:
            draw.rectangle([door_x + door_width // 2 - 10, door_top + 22, door_x + door_width // 2 + 10, door_top + 32], fill=(60, 55, 50, 150))

    # Walls - right side doors (mirrored)
    for i in range(5):
        door_top = vanishing_y + 50 + i * 70
        door_bottom = door_top + 55
        t = i / 4
        door_width = int(60 + t * 100)
        door_x = vanishing_x + int(20 + t * 200)
        if door_x + door_width > width:
            continue
        draw.rectangle([door_x, door_top, door_x + door_width, door_bottom], fill=(25, 22, 30, 180))
        draw.rectangle([door_x + 5, door_top + 5, door_x + door_width - 5, door_bottom - 5], fill=(35, 32, 42, 200))

    # Wall lines
    for i in range(3):
        y = vanishing_y + 60 + i * 100
        draw.line([(0, y), (width, y)], fill=(15, 14, 20, 40), width=1)


def draw_locked_door(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a prominent locked door with a chain, slightly ajar, center-left."""
    dx, dy = width // 2 - 100, int(height * 0.52)
    door_w, door_h = 180, 300

    # Door frame
    draw.rectangle([dx, dy, dx + door_w, dy + door_h], fill=(30, 25, 35))
    # Door panel
    draw.rectangle([dx + 8, dy + 8, dx + door_w - 8, dy + door_h - 8], fill=(40, 35, 45))
    # Dark crack (slightly open)
    draw.rectangle([dx + door_w - 4, dy + 60, dx + door_w + 8, dy + door_h - 60], fill=(5, 5, 10))

    # Door handle
    draw.ellipse([dx + door_w // 2 + 20, dy + door_h // 2 - 10, dx + door_w // 2 + 36, dy + door_h // 2 + 6], fill=(180, 160, 120))
    draw.ellipse([dx + door_w // 2 + 23, dy + door_h // 2 - 7, dx + door_w // 2 + 33, dy + door_h // 2 + 3], fill=(120, 100, 70))

    # Chain lock
    chain_x = dx + door_w + 5
    chain_y = dy + 40
    for link in range(4):
        draw.ellipse([chain_x - 3, chain_y + link * 8, chain_x + 5, chain_y + link * 8 + 6], fill=(160, 140, 100))
    # Lock body
    draw.rectangle([chain_x - 6, chain_y - 4, chain_x + 8, chain_y + 4], fill=(140, 120, 80))
    # Keyhole
    draw.ellipse([chain_x - 2, chain_y - 2, chain_x + 4, chain_y + 3], fill=(20, 18, 25))

    # Glow from behind the door
    for i in range(3):
        glow_x = dx + door_w + 2 + i
        draw.line([(glow_x, dy + 60), (glow_x, dy + door_h - 60)], fill=(60, 55, 80, 30 - i * 10))


def draw_vinyl_record(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a vinyl record leaning against the wall."""
    vx, vy = width - 250, int(height * 0.55)
    r = 70

    # Record (black circle with label)
    draw.ellipse([vx - r, vy - r, vx + r, vy + r], fill=(15, 15, 18))
    # Grooves
    for i in range(1, 5):
        gr = r - i * 12
        draw.ellipse([vx - gr, vy - gr, vx + gr, vy + gr], outline=(25, 25, 30), width=1)
    # Label
    draw.ellipse([vx - 22, vy - 22, vx + 22, vy + 22], fill=(180, 40, 40))
    draw.ellipse([vx - 16, vy - 16, vx + 16, vy + 16], fill=(200, 50, 50))
    # Center hole
    draw.ellipse([vx - 4, vy - 4, vx + 4, vy + 4], fill=(10, 10, 10))

    # Shadow of record on wall
    for i in range(5):
        shadow_r = r + i * 2
        draw.ellipse([vx - shadow_r + 8, vy - shadow_r + 8, vx + shadow_r + 8, vy + shadow_r + 8],
                     outline=(5, 5, 12, 20 - i * 4), width=1)


def draw_yellow_submarine(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small yellow submarine silhouette on the wall as Beatles imagery."""
    sx, sy = 160, int(height * 0.38)

    # Submarine body
    body_pts = [
        (sx - 50, sy),
        (sx + 40, sy - 10),
        (sx + 60, sy - 5),
        (sx + 70, sy),
        (sx + 60, sy + 5),
        (sx + 40, sy + 10),
        (sx - 50, sy + 8),
    ]
    draw.polygon(body_pts, fill=(200, 180, 50, 120))

    # Periscope
    draw.line([(sx + 10, sy - 10), (sx + 10, sy - 30)], fill=(180, 160, 40, 120), width=3)
    draw.ellipse([sx + 5, sy - 35, sx + 15, sy - 28], fill=(200, 180, 50, 120))

    # Portholes
    for px in [sx - 30, sx - 5, sx + 20]:
        draw.ellipse([px - 5, sy - 4, px + 5, sy + 4], fill=(180, 200, 220, 100))

    # Propeller
    draw.ellipse([sx - 60, sy - 8, sx - 50, sy + 8], fill=(150, 130, 40, 100))

    # Shadow of submarine
    shadow_pts = [
        (sx - 45, sy + 20),
        (sx + 65, sy + 12),
        (sx + 55, sy + 18),
        (sx - 40, sy + 25),
    ]
    draw.polygon(shadow_pts, fill=(5, 5, 10, 40))


def draw_shadow_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a tall shadow figure at the end of the corridor."""
    fx, fy = width // 2, int(height * 0.28)

    # Silhouette figure
    # Body
    draw.rectangle([fx - 15, fy + 30, fx + 15, fy + 120], fill=(3, 3, 8, 150))
    # Head
    draw.ellipse([fx - 12, fy + 8, fx + 12, fy + 35], fill=(3, 3, 8, 150))
    # Arms
    draw.line([(fx - 15, fy + 50), (fx - 40, fy + 70)], fill=(3, 3, 8, 150), width=5)
    draw.line([(fx + 15, fy + 50), (fx + 40, fy + 70)], fill=(3, 3, 8, 150), width=5)
    # Legs
    draw.line([(fx - 5, fy + 120), (fx - 15, fy + 160)], fill=(3, 3, 8, 150), width=6)
    draw.line([(fx + 5, fy + 120), (fx + 15, fy + 160)], fill=(3, 3, 8, 150), width=6)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        c = lerp_color((8, 8, 15), ((3, 3, 8)), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(60, 55, 70), width=2)
    draw.line([(0, panel_top + 2), (width, panel_top + 2)], fill=(25, 22, 35), width=1)

    # Title text
    title = "The Vanishing of\nEleanor Rigby"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    lines = title.split("\n")
    y_offset = panel_top + 100
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        # Shadow for readability
        draw.text((tx + 2, y_offset + 2), line, fill=(40, 40, 55), font=title_font)
        draw.text((tx, y_offset), line, fill=(240, 240, 245), font=title_font)
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
    draw.text((ax + 1, ay + 1), author, fill=(60, 60, 80), font=author_font)
    draw.text((ax, ay), author, fill=(180, 180, 195), font=author_font)

    # Small decorative line
    draw.line([(width // 2 - 80, y_offset - 10), (width // 2 + 80, y_offset - 10)], fill=(60, 55, 70), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Hotel corridor
    draw_hotel_corridor(draw, WIDTH, HEIGHT)

    # Step 3: Shadow figure at end of corridor
    draw_shadow_figure(draw, WIDTH, HEIGHT)

    # Step 4: Locked door
    draw_locked_door(draw, WIDTH, HEIGHT)

    # Step 5: Vinyl record
    draw_vinyl_record(draw, WIDTH, HEIGHT)

    # Step 6: Yellow submarine (Beatles imagery)
    draw_yellow_submarine(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
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