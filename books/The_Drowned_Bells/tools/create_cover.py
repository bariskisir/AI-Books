#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Drowned Bells using PIL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 2560
FONT_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
AUTHOR = "Barış Kısır"  # Barış Kısır


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, top: str, bottom: str) -> None:
    top_rgb = hex_to_rgb(top)
    bot_rgb = hex_to_rgb(bottom)
    for y in range(HEIGHT):
        t = y / HEIGHT
        color = lerp_color(top_rgb, bot_rgb, t)
        draw.line([(0, y), (WIDTH, y)], fill=color, width=1)


def draw_mist(draw: ImageDraw) -> None:
    """Draw layered mist bands across the middle of the image."""
    mist_color = (200, 210, 215, 60)
    for i in range(8):
        y_base = 600 + i * 80
        x_offset = 100 + i * 30
        for layer in range(3):
            y = y_base + layer * 10
            alpha = 30 - i * 2
            if alpha <= 0:
                continue
            points = [
                (0, y),
                (300 + x_offset + layer * 50, y - 20 - layer * 5),
                (700 + x_offset + layer * 80, y + 15 + layer * 3),
                (WIDTH, y - 10 + layer * 4),
                (WIDTH, y + 10 + layer * 4),
                (700 + x_offset + layer * 80, y + 30 + layer * 6),
                (300 + x_offset + layer * 50, y + 10 + layer * 2),
                (0, y + 15),
            ]
            draw.polygon(points, fill=(200, 210, 215, alpha))


def draw_bell_tower(draw: ImageDraw) -> None:
    """Draw the bell tower emerging from the sea at center of image."""
    tower_x = WIDTH // 2
    base_y = 1600  # bottom of tower
    top_y = 450  # top of tower
    tower_width = 120

    # Main tower body
    draw.rectangle(
        [tower_x - tower_width // 2, top_y, tower_x + tower_width // 2, base_y],
        fill=(180, 185, 190),  # gray stone
        outline=(140, 145, 150),
        width=2,
    )

    # Tower top / parapet
    parapet_top = top_y - 30
    draw.rectangle(
        [tower_x - tower_width // 2 - 15, parapet_top, tower_x + tower_width // 2 + 15, top_y],
        fill=(160, 165, 170),
        outline=(130, 135, 140),
        width=2,
    )

    # Cross at top
    cross_height = 60
    cross_width = 30
    cross_y = parapet_top - cross_height
    # Vertical bar
    draw.rectangle(
        [tower_x - 5, cross_y, tower_x + 5, parapet_top],
        fill=(220, 220, 210),
    )
    # Horizontal bar
    draw.rectangle(
        [tower_x - cross_width // 2, cross_y + cross_height // 3, tower_x + cross_width // 2, cross_y + cross_height // 3 + 10],
        fill=(220, 220, 210),
    )

    # Arch window on tower
    window_top = top_y + 80
    window_bottom = window_top + 120
    window_width = 40
    draw.rectangle(
        [tower_x - window_width // 2, window_top, tower_x + window_width // 2, window_bottom],
        fill=(80, 85, 90),
    )
    # Arch top
    draw.arc(
        [tower_x - window_width // 2, window_top - 20, tower_x + window_width // 2, window_top + 20],
        start=180, end=0, fill=(80, 85, 90), width=window_width,
    )

    # Second window (lower)
    win2_top = window_bottom + 60
    win2_bottom = win2_top + 80
    draw.rectangle(
        [tower_x - window_width // 2, win2_top, tower_x + window_width // 2, win2_bottom],
        fill=(80, 85, 90),
    )
    draw.arc(
        [tower_x - window_width // 2, win2_top - 15, tower_x + window_width // 2, win2_top + 15],
        start=180, end=0, fill=(80, 85, 90), width=window_width,
    )

    # Bell at top of tower (visible through arch)
    bell_center_y = top_y + 140
    draw.ellipse(
        [tower_x - 15, bell_center_y - 12, tower_x + 15, bell_center_y + 12],
        fill=(210, 200, 150),  # bronze/gold bell
    )


def draw_sea(draw: ImageDraw) -> None:
    """Draw waves and sea surface at the base."""
    wave_color = (80, 110, 120)
    foam_color = (180, 195, 200)

    # Base sea
    for y in range(1500, HEIGHT - 640, 8):
        wave_offset = int(20 * ((y % 40) / 40))
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(60 + wave_offset, 90 + wave_offset, 100 + wave_offset),
            width=1,
        )

    # Foam lines at base of tower
    for i in range(10):
        foam_y = 1540 + i * 12
        draw.line(
            [(WIDTH // 2 - 200 - i * 15, foam_y), (WIDTH // 2 + 200 + i * 15, foam_y - 3 + i)],
            fill=foam_color,
            width=2,
        )


def draw_gulls(draw: ImageDraw) -> None:
    """Draw small gull silhouettes in the sky."""
    gull_positions = [
        (200, 200),
        (350, 160),
        (550, 220),
        (900, 150),
        (1100, 180),
        (1300, 240),
        (1450, 170),
    ]
    for x, y in gull_positions:
        # Simple gull shape: two curved lines
        draw.arc([x - 15, y - 5, x, y + 5], start=0, end=180, fill=(60, 65, 70), width=2)
        draw.arc([x, y - 5, x + 15, y + 5], start=180, end=360, fill=(60, 65, 70), width=2)


def draw_title_panel(draw: ImageDraw, title: str) -> None:
    """Draw a dark panel at the bottom with title and author in white."""
    panel_top = 1920
    panel_height = HEIGHT - panel_top

    # Dark semi-transparent panel
    for y in range(panel_top, HEIGHT):
        t = (y - panel_top) / panel_height
        alpha = int(180 * (1 - t * 0.3))
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(15, 18, 25, alpha),
            width=1,
        )

    # Add a subtle top border to the panel
    draw.line(
        [(0, panel_top), (WIDTH, panel_top)],
        fill=(100, 110, 120, 100),
        width=2,
    )

    try:
        title_font = ImageFont.truetype(str(FONT_PATH), 72)
        subtitle_font = ImageFont.truetype(str(FONT_PATH), 32)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()

    # Author text at top of panel
    author_y = panel_top + 50
    try:
        # Try to use subtitle font for author, fallback to default
        author_bbox = draw.textbbox((0, 0), AUTHOR, font=subtitle_font) if subtitle_font else draw.textbbox((0, 0), AUTHOR)
        author_w = author_bbox[2] - author_bbox[0]
        draw.text(
            ((WIDTH - author_w) // 2, author_y),
            AUTHOR,
            font=subtitle_font,
            fill=(200, 200, 200),
        )
    except Exception:
        draw.text((WIDTH // 2, author_y), AUTHOR, fill=(200, 200, 200))

    # Title
    title_y = author_y + 60
    lines = []
    words = title.split()
    current = ""
    for w in words:
        test = f"{current} {w}".strip()
        try:
            tw = draw.textbbox((0, 0), test, font=title_font)[2] - draw.textbbox((0, 0), test, font=title_font)[0]
        except Exception:
            tw = len(test) * 30
        if tw < WIDTH - 200:
            current = test
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)

    for i, line in enumerate(lines):
        ly = title_y + i * 90
        try:
            line_bbox = draw.textbbox((0, 0), line, font=title_font)
            lw = line_bbox[2] - line_bbox[0]
            draw.text(
                ((WIDTH - lw) // 2, ly),
                line,
                font=title_font,
                fill=(255, 255, 255),
            )
        except Exception:
            draw.text((WIDTH // 2, ly), line, fill=(255, 255, 255))

    # Decorative line below title
    deco_y = title_y + len(lines) * 90 + 30
    draw.line(
        [(WIDTH // 2 - 100, deco_y), (WIDTH // 2 + 100, deco_y)],
        fill=(180, 180, 180),
        width=2,
    )

    # Series/genre note
    series_y = deco_y + 40
    series_text = "A Coastal Gothic Novel"
    try:
        series_bbox = draw.textbbox((0, 0), series_text, font=subtitle_font)
        sw = series_bbox[2] - series_bbox[0]
        draw.text(
            ((WIDTH - sw) // 2, series_y),
            series_text,
            font=subtitle_font,
            fill=(180, 180, 180),
        )
    except Exception:
        draw.text((WIDTH // 2, series_y), series_text, fill=(180, 180, 180))


def create_cover(title: str, output_path: Path) -> None:
    """Generate the 1600x2560 cover image."""
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background — stormy gray-green to dark sea blue
    draw_gradient(draw, "#4A5550", "#1A2228")

    # Add a faint moon/light source
    moon_center = (1100, 280)
    for r in range(80, 0, -1):
        alpha = max(0, 20 - r // 4)
        draw.ellipse(
            [moon_center[0] - r, moon_center[1] - r, moon_center[0] + r, moon_center[1] + r],
            fill=(200, 210, 215, alpha),
        )

    # Draw gulls
    draw_gulls(draw)

    # Draw mist
    draw_mist(draw)

    # Sea
    draw_sea(draw)

    # Bell tower
    draw_bell_tower(draw)

    # Title panel at bottom
    draw_title_panel(draw, title)

    # Final solid black overlay at extreme bottom for clean edge
    draw.rectangle(
        [(0, 2500), (WIDTH, HEIGHT)],
        fill=(10, 10, 15),
    )

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(output_path, "PNG")
    print(f"Cover saved: {output_path}")



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

    metadata = json.loads(args.metadata.read_bytes())
    title = metadata.get("title", "The Drowned Bells")
    create_cover(title, args.out)


if __name__ == "__main__":
    main()