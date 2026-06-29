#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Ghost Bridge (Cosmic Horror)."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)



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
    """Green-gray to black gradient for the cosmic horror atmosphere."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((70, 80, 65), (40, 50, 40), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((40, 50, 40), (20, 25, 22), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((20, 25, 22), (5, 5, 8), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_mist(draw: ImageDraw, width: int, height: int) -> None:
    """Draw layered mist in the valley beneath the bridge."""
    rng = random.Random(17)
    for layer in range(6):
        alpha = 30 - layer * 4
        y_base = int(height * 0.35) + layer * 40
        for _ in range(60):
            x = rng.randint(0, width)
            y = y_base + rng.randint(-20, 20)
            r = rng.randint(40, 120)
            draw.ellipse([x - r, y - r // 2, x + r, y + r // 2], fill=(120, 130, 120, alpha))


def draw_valley_walls(draw: ImageDraw, width: int, height: int) -> None:
    """Draw dark valley walls on both sides."""
    # Left wall
    wall_points_left = []
    for y in range(int(height * 0.15), int(height * 0.7)):
        x_offset = int(80 * math.sin(y * 0.005)) + int(60 * math.sin(y * 0.012))
        wall_points_left.append((max(0, 200 + x_offset), y))
    for i in range(len(wall_points_left) - 1):
        draw.line([wall_points_left[i], wall_points_left[i + 1]], fill=(15, 18, 20), width=3)

    # Right wall
    wall_points_right = []
    for y in range(int(height * 0.15), int(height * 0.7)):
        x_offset = int(80 * math.sin(y * 0.005 + 1.5)) + int(60 * math.sin(y * 0.012 + 0.5))
        wall_points_right.append((min(width, width - 200 + x_offset), y))
    for i in range(len(wall_points_right) - 1):
        draw.line([wall_points_right[i], wall_points_right[i + 1]], fill=(15, 18, 20), width=3)


def draw_bridge(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the stone bridge arching over the valley."""
    bridge_y = int(height * 0.35)
    bridge_span = 700
    arch_height = 150
    cx = width // 2

    # Arch curve
    arch_points = []
    for x in range(cx - bridge_span // 2, cx + bridge_span // 2 + 1, 5):
        t = (x - (cx - bridge_span // 2)) / bridge_span
        y_offset = arch_height * math.sin(t * math.pi)
        arch_points.append((x, bridge_y - y_offset))

    # Draw arch outline (multiple passes for thickness)
    for offset in range(0, 25, 5):
        pts = [(x, y - offset) for x, y in arch_points]
        draw.line(pts, fill=(80, 85, 78), width=3)

    # Bridge deck (top)
    deck_y = bridge_y - arch_height
    draw.line([(cx - bridge_span // 2 - 30, deck_y), (cx + bridge_span // 2 + 30, deck_y)], fill=(90, 95, 88), width=12)
    draw.line([(cx - bridge_span // 2 - 30, deck_y), (cx + bridge_span // 2 + 30, deck_y)], fill=(70, 75, 68), width=8)

    # Parapet
    draw.line([(cx - bridge_span // 2 - 20, deck_y - 8), (cx + bridge_span // 2 + 20, deck_y - 8)], fill=(100, 105, 95), width=4)

    # Keystone marker at centre
    draw.rectangle([cx - 30, deck_y - 30, cx + 30, deck_y + 5], fill=(110, 115, 100))
    draw.rectangle([cx - 20, deck_y - 22, cx + 20, deck_y - 5], fill=(130, 135, 120))

    # Stones on arch (horizontal lines suggesting masonry)
    for i in range(1, 8):
        t = i / 8
        y_pos = bridge_y - arch_height * math.sin(t * math.pi)
        x_pos_l = cx - bridge_span // 2 * (1 - t)
        x_pos_r = cx + bridge_span // 2 * (1 - t)
        if x_pos_r - x_pos_l > 100:
            draw.line([(x_pos_l + 20, y_pos), (x_pos_r - 20, y_pos)], fill=(60, 65, 58), width=2)

    # Vertical stone divisions
    for i in range(-5, 6):
        if i == 0:
            continue
        t = abs(i) / 6
        x_pos = cx + i * 50
        y_top = bridge_y - arch_height * math.sin((abs(x_pos - cx) / (bridge_span // 2)) * math.pi)
        y_bot = y_top + 30
        if y_bot > bridge_y:
            y_bot = bridge_y
        draw.line([(x_pos, y_top), (x_pos, y_bot)], fill=(55, 60, 53), width=1)


def draw_runes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw ancient geometric rune patterns on the bridge arch."""
    cx = width // 2
    bridge_y = int(height * 0.35)
    arch_height = 150
    rng = random.Random(23)

    rune_positions = [
        (cx - 200, bridge_y - arch_height * 0.6),
        (cx - 100, bridge_y - arch_height * 0.85),
        (cx + 100, bridge_y - arch_height * 0.85),
        (cx + 200, bridge_y - arch_height * 0.6),
        (cx, bridge_y - arch_height * 0.95),
        (cx - 300, bridge_y - arch_height * 0.3),
        (cx + 300, bridge_y - arch_height * 0.3),
    ]

    for rx, ry in rune_positions:
        ry = int(ry)
        # Draw a geometric rune symbol
        size = rng.randint(12, 22)
        rune_color = (100, 110, 95, 180)

        # Different rune shapes
        shape_type = rng.randint(0, 3)
        if shape_type == 0:
            # Nested hexagon
            for s in range(size, 0, -5):
                pts = []
                for a in range(6):
                    angle = math.pi / 3 * a - math.pi / 6
                    pts.append((rx + s * math.cos(angle), ry + s * math.sin(angle)))
                draw.polygon(pts, outline=rune_color, width=1)
        elif shape_type == 1:
            # Spiral
            for a_deg in range(0, 360, 15):
                a_rad = math.radians(a_deg)
                r = size * (1 - a_deg / 720)
                if r > 2:
                    x1 = rx + r * math.cos(a_rad)
                    y1 = ry + r * math.sin(a_rad)
                    x2 = rx + (r - 2) * math.cos(a_rad + 0.15)
                    y2 = ry + (r - 2) * math.sin(a_rad + 0.15)
                    draw.line([(x1, y1), (x2, y2)], fill=rune_color, width=1)
        elif shape_type == 2:
            # Keyhole symbol
            draw.circle([rx, ry], size, outline=rune_color, width=2)
            draw.line([(rx, ry), (rx, ry + size + 5)], fill=rune_color, width=2)
        else:
            # Concentric circles
            for s in range(size, 0, -6):
                draw.circle([rx, ry], s, outline=rune_color, width=1)
            # Centre dot
            draw.circle([rx, ry], 2, fill=(140, 150, 135))


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 12, 15, 230))

    # Subtle top border line
    draw.line([(0, panel_top), (width, panel_top)], fill=(50, 55, 60), width=2)

    # Load title font (arialbd.ttf)
    title_font_size = 76
    title_font = None
    try:
        title_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), title_font_size)
    except Exception:
        try:
            title_font = ImageFont.truetype(str(FONTS_DIR / "ARIALBD.TTF"), title_font_size)
        except Exception:
            title_font = ImageFont.load_default()

    # Title text
    title_line1 = "The Ghost"
    title_line2 = "Bridge"

    # Draw title centered
    y_offset = panel_top + 80

    for line in [title_line1, title_line2]:
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
    author_font_size = 34
    try:
        author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), author_font_size)
    except Exception:
        try:
            author_font = ImageFont.truetype(str(FONTS_DIR / "ARIALBD.TTF"), author_font_size)
        except Exception:
            author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)

    # Genre line
    genre = "Cosmic Horror"
    genre_font_size = 22
    try:
        genre_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()
    try:
        gbbox = draw.textbbox((0, 0), genre, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    gy = ay + 55
    draw.text((gx, gy), genre, fill=(150, 155, 160), font=genre_font)


def draw_subtle_glow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a faint eerie glow emanating from beneath the bridge."""
    cx = width // 2
    glow_y = int(height * 0.35) + 50
    for r in range(250, 50, -20):
        alpha = max(2, 15 - r // 20)
        draw.ellipse(
            [cx - r, glow_y - r // 2, cx + r, glow_y + r // 2],
            fill=(80, 100, 80, alpha),
        )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Valley walls
    draw_valley_walls(draw, WIDTH, HEIGHT)

    # Step 3: Eerie glow from beneath
    draw_subtle_glow(draw, WIDTH, HEIGHT)

    # Step 4: Mist in the valley
    draw_mist(draw, WIDTH, HEIGHT)

    # Step 5: The stone bridge
    draw_bridge(draw, WIDTH, HEIGHT)

    # Step 6: Ancient runes on the arch
    draw_runes(draw, WIDTH, HEIGHT)

    # Step 7: Title panel (dark with white text)
    draw_title_panel(draw, WIDTH, HEIGHT)

    # Soften slightly
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), metadata.get("model", ""))
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