#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Ghost of the Grand Hotel."""

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
    """Dark teal-to-ivory gradient for the haunted hotel atmosphere."""
    for y in range(height):
        if y < height * 0.6:
            t = y / (height * 0.6)
            c = lerp_color((5, 25, 30), (15, 50, 55), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((15, 50, 55), (210, 200, 185), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_hotel_facade(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the grand hotel facade with dome, wings, and lit windows."""
    cx = width // 2
    base_y = int(height * 0.55)

    # Central building
    cw, ch = 320, 280
    draw.rectangle([cx - cw // 2, base_y - ch, cx + cw // 2, base_y], fill=(25, 35, 40))

    # Central dome
    dome_top = base_y - ch - 60
    draw.ellipse([cx - 80, dome_top, cx + 80, dome_top + 100], fill=(30, 45, 50))
    draw.ellipse([cx - 40, dome_top - 30, cx + 40, dome_top + 30], fill=(35, 50, 55))

    # Left wing
    lw, lh = 200, 200
    draw.rectangle([cx - cw // 2 - lw, base_y - lh, cx - cw // 2, base_y], fill=(20, 30, 35))

    # Right wing
    draw.rectangle([cx + cw // 2, base_y - lh, cx + cw // 2 + lw, base_y], fill=(20, 30, 35))

    # Roof details on wings
    for wing_x in [cx - cw // 2 - lw, cx + cw // 2]:
        draw.rectangle([wing_x + 10, base_y - lh - 20, wing_x + 190, base_y - lh], fill=(25, 38, 42))
        # Small dormers
        for d in range(3):
            dx = wing_x + 20 + d * 60
            draw.rectangle([dx, base_y - lh - 40, dx + 30, base_y - lh - 10], fill=(30, 45, 50))

    # Windows on main building
    win_color = (180, 160, 120)
    for row in range(5):
        for col in range(7):
            wx = cx - cw // 2 + 20 + col * 42
            wy = base_y - ch + 20 + row * 50
            alpha = 120 if row < 3 and col % 2 == 0 else 60
            draw.rectangle([wx, wy, wx + 25, wy + 30], fill=win_color + (alpha,))

    # Windows on wings
    for wing_x in [cx - cw // 2 - lw, cx + cw // 2]:
        for row in range(3):
            for col in range(4):
                wx = wing_x + 15 + col * 45
                wy = base_y - lh + 20 + row * 55
                draw.rectangle([wx, wy, wx + 25, wy + 30], fill=win_color + (60,))

    # Entrance
    door_w, door_h = 60, 80
    draw.rectangle([cx - door_w // 2 - 5, base_y - door_h, cx + door_w // 2 + 5, base_y], fill=(40, 30, 20))
    # Door arch
    draw.ellipse([cx - door_w // 2 - 5, base_y - door_h - 20, cx + door_w // 2 + 5, base_y - door_h + 20], fill=(40, 30, 20))
    # Door light
    draw.ellipse([cx - 12, base_y - door_h - 8, cx + 12, base_y - door_h + 16], fill=(220, 200, 150, 100))

    # Columns at entrance
    for col_x in [cx - 35, cx + 35]:
        draw.rectangle([col_x - 3, base_y - door_h - 10, col_x + 3, base_y], fill=(50, 60, 65))

    # Balconies
    for bal_y in [base_y - ch + 60, base_y - ch + 130]:
        draw.line([(cx - 100, bal_y), (cx + 100, bal_y)], fill=(40, 55, 60), width=3)
        for pillar in range(5):
            px = cx - 100 + pillar * 50
            draw.rectangle([px, bal_y - 8, px + 4, bal_y], fill=(40, 55, 60))


def draw_lake_mountains(draw: ImageDraw, width: int, height: int) -> None:
    """Draw Lake Geneva and mountains in the background behind the hotel."""
    # Mountains
    for i, (mtn_x, mtn_h, mtn_w) in enumerate([
        (100, 60, 200), (350, 90, 180), (600, 50, 150),
        (900, 100, 220), (1200, 55, 160), (1450, 70, 190),
    ]):
        color = (60, 75, 85) if i % 2 == 0 else (70, 85, 95)
        draw.polygon([
            (mtn_x, int(height * 0.25)),
            (mtn_x + mtn_w // 2, int(height * 0.25) - mtn_h),
            (mtn_x + mtn_w, int(height * 0.25)),
        ], fill=color)

    # Lake surface
    lake_top = int(height * 0.25)
    lake_bottom = int(height * 0.42)
    for y in range(lake_top, lake_bottom):
        t = (y - lake_top) / (lake_bottom - lake_top)
        c = lerp_color((70, 85, 95), (20, 45, 55), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Lake ripples
    for rx in range(100, width - 100, 80):
        for ry in range(lake_top + 20, lake_bottom - 10, 25):
            draw.line([(rx, ry), (rx + 40, ry - 2)], fill=(100, 130, 140, 40), width=1)


def draw_vintage_key(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an ornate vintage key on the left side."""
    kx, ky = width // 2 - 280, int(height * 0.75)

    # Key shaft
    shaft_length = 120
    draw.line([(kx, ky), (kx + shaft_length, ky)], fill=(180, 160, 120), width=6)
    draw.line([(kx, ky + 8), (kx + shaft_length, ky + 8)], fill=(160, 140, 100), width=2)

    # Key bow (ornate top)
    bow_cx = kx
    bow_cy = ky - 30
    # Outer ring
    draw.ellipse([bow_cx - 25, bow_cy - 25, bow_cx + 25, bow_cy + 25], outline=(180, 160, 120), width=5)
    # Inner hole
    draw.ellipse([bow_cx - 10, bow_cy - 10, bow_cx + 10, bow_cy + 10], outline=(180, 160, 120), width=3)
    # Decorative notches on bow
    for angle in [45, 135, 225, 315]:
        rad = math.radians(angle)
        nx = bow_cx + int(22 * math.cos(rad))
        ny = bow_cy + int(22 * math.sin(rad))
        draw.ellipse([nx - 4, ny - 4, nx + 4, ny + 4], fill=(200, 180, 140))

    # Key teeth at the end
    tooth_start = kx + shaft_length - 30
    for t in range(3):
        tx = tooth_start + t * 12
        draw.rectangle([tx, ky + 8, tx + 4, ky + 22], fill=(180, 160, 120))
    # Bottom tooth
    draw.rectangle([tx, ky + 8, tx + 4, ky + 28], fill=(180, 160, 120))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 20, 25, 230))

    # Thin accent line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 160, 120), width=3)

    # Ornamental line below accent
    for x in range(200, width - 200, 40):
        draw.line([(x, panel_top + 15), (x + 20, panel_top + 15)], fill=(100, 130, 140, 80), width=1)

    # Title text - use arialbd.ttf (available)
    title = "The Ghost of\nthe Grand Hotel"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

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
        y_offset += 85

    # Decorative divider
    div_y = y_offset - 45
    for x in range(width // 2 - 80, width // 2 + 80, 20):
        draw.line([(x, div_y), (x + 10, div_y)], fill=(180, 160, 120), width=1)

    # Author name
    author = "Barış Kısır"
    author_font_size = 32
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
    draw.text((ax, div_y + 30), author, fill=(200, 190, 170), font=author_font)

    # Room number detail
    room_text = "Room 307"
    room_font_size = 20
    try:
        room_font = ImageFont.truetype(str(font_paths["small"]), room_font_size)
    except Exception:
        room_font = ImageFont.load_default()
    try:
        rbbox = draw.textbbox((0, 0), room_text, font=room_font)
        rw = rbbox[2] - rbbox[0]
    except Exception:
        rw = 0
    draw.text(((width - rw) // 2, height - 50), room_text, fill=(120, 150, 155), font=room_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Ghost of the Grand Hotel")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Lake and mountains (behind hotel)
    draw_lake_mountains(draw, WIDTH, HEIGHT)

    # Step 3: Hotel facade
    draw_hotel_facade(draw, WIDTH, HEIGHT)

    # Step 4: Vintage key
    draw_vintage_key(draw, WIDTH, HEIGHT)

    # Step 5: Title panel
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