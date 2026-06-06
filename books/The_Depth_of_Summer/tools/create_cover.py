#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Depth of Summer using PIL."""

from __future__ import annotations

import argparse
import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 1600
HEIGHT = 2560
PANEL_TOP = 1920
PANEL_BOTTOM = HEIGHT

FONTS_DIR = Path("C:/Windows/Fonts")
TITLE_FONT_PATH = FONTS_DIR / "arialbd.ttf"
AUTHOR_FONT_PATH = FONTS_DIR / "arialbd.ttf"
SMALL_FONT_PATH = FONTS_DIR / "arial.ttf"


def draw_sky(draw: ImageDraw.ImageDraw) -> None:
    """Draw a sunset sky gradient over the estuary."""
    for y in range(0, PANEL_TOP):
        progress = y / PANEL_TOP
        if progress < 0.2:
            r = int(255 - progress * 80)
            g = int(200 - progress * 60)
            b = int(120 - progress * 40)
        elif progress < 0.5:
            r = int(239 - (progress - 0.2) * 30)
            g = int(188 - (progress - 0.2) * 40)
            b = int(112 - (progress - 0.2) * 30)
        elif progress < 0.75:
            r = int(230 - (progress - 0.5) * 60)
            g = int(170 - (progress - 0.5) * 50)
            b = int(97 - (progress - 0.5) * 40)
        else:
            r = int(200 - (progress - 0.75) * 80)
            g = int(142 - (progress - 0.75) * 50)
            b = int(77 - (progress - 0.75) * 30)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, r), max(0, g), max(0, b)))


def draw_sun(draw: ImageDraw.ImageDraw) -> None:
    """Draw a setting sun low on the horizon over the marsh."""
    cx, cy = 800, 1350
    for radius in range(180, 0, -1):
        alpha = int(180 * (1 - radius / 180))
        if radius > 80:
            color = (255, 200, 70, alpha)
        else:
            color = (255, 180, 50)
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=color[:3] if radius <= 80 else None,
            outline=None,
        )
    draw.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=(255, 210, 80))


def draw_marsh_grass(draw: ImageDraw.ImageDraw) -> None:
    """Draw marsh grass in the foreground of the estuary."""
    base_y = 1550
    grass_color = (80, 130, 60)
    dark_grass = (60, 105, 45)
    gold_grass = (160, 140, 60)

    for x in range(0, WIDTH, 3):
        height = int(60 + math.sin(x * 0.08) * 30 + math.sin(x * 0.03) * 20)
        if x % 6 == 0:
            color = dark_grass
        elif x % 9 == 0:
            color = gold_grass
        else:
            color = grass_color
        draw.line([(x, base_y), (x, base_y - height)], fill=color, width=2)

    # Second row of taller marsh grass
    for x in range(0, WIDTH, 5):
        height = int(100 + math.sin(x * 0.06 + 1) * 35 + math.sin(x * 0.02) * 25)
        color = (70, 115, 50) if x % 7 == 0 else (90, 140, 65)
        draw.line([(x, base_y), (x, base_y - height)], fill=color, width=1)

    # Fallen / bent grass foreground
    for x in range(0, WIDTH, 8):
        bend_x = x + int(math.sin(x * 0.1) * 20)
        for h in [30, 50, 70]:
            color = (55, 95, 40)
            draw.line(
                [(x, base_y + h), (bend_x, base_y + h - 30)],
                fill=color,
                width=2,
            )


def draw_water_channels(draw: ImageDraw.ImageDraw) -> None:
    """Draw tidal channels winding through the marsh."""
    channel_color = (20, 60, 80)
    light_channel = (30, 80, 100)
    for i in range(4):
        start_x = 200 + i * 350
        start_y = 1300
        for x in range(start_x, WIDTH, 2):
            y = int(
                start_y
                + math.sin((x - start_x) * 0.008 + i) * 40
                + math.sin((x - start_x) * 0.02 + i * 2) * 20
            )
            width = max(1, int(3 + math.sin((x - start_x) * 0.005 + i) * 2))
            color = light_channel if i % 2 == 0 else channel_color
            draw.line([(x, y), (x, y + width)], fill=color)


def draw_skiff(draw: ImageDraw.ImageDraw) -> None:
    """Draw a small wooden skiff on a channel."""
    cx, cy = 650, 1380
    # Skiff hull
    hull_points = [
        (cx - 80, cy),
        (cx - 60, cy + 15),
        (cx + 60, cy + 15),
        (cx + 80, cy),
    ]
    draw.polygon(hull_points, fill=(100, 80, 60))
    draw.line([(cx - 80, cy), (cx + 80, cy)], fill=(60, 45, 30), width=3)

    # Seat
    draw.line([(cx - 20, cy - 2), (cx + 20, cy - 2)], fill=(80, 60, 40), width=4)

    # Oars
    draw.line([(cx - 40, cy - 5), (cx - 100, cy - 40)], fill=(120, 100, 70), width=3)
    draw.line([(cx + 40, cy - 5), (cx + 100, cy - 40)], fill=(120, 100, 70), width=3)

    # Small figure silhouette
    draw.ellipse([cx - 8, cy - 28, cx + 8, cy - 12], fill=(40, 35, 30))
    draw.line([cx, cy - 12, cx, cy], fill=(40, 35, 30), width=3)


def draw_heron(draw: ImageDraw.ImageDraw) -> None:
    """Draw a blue heron standing in the shallows."""
    cx, cy = 1100, 1390
    # Legs
    draw.line([(cx - 5, cy), (cx - 5, cy - 40)], fill=(60, 55, 50), width=2)
    draw.line([(cx + 5, cy), (cx + 5, cy - 42)], fill=(60, 55, 50), width=2)

    # Body
    body_top = cy - 55
    draw.ellipse(
        [cx - 12, body_top - 20, cx + 12, body_top + 25], fill=(140, 155, 170)
    )

    # Neck and head
    draw.line(
        [cx, body_top, cx + 5, body_top - 30],
        fill=(140, 155, 170),
        width=3,
    )
    draw.ellipse([cx - 4, body_top - 38, cx + 6, body_top - 28], fill=(140, 155, 170))

    # Beak
    draw.line(
        [cx + 5, body_top - 35, cx + 20, body_top - 33],
        fill=(200, 180, 100),
        width=2,
    )


def draw_mudflats(draw: ImageDraw.ImageDraw) -> None:
    """Draw exposed mudflats in the lower estuary."""
    for y in range(1450, PANEL_TOP):
        progress = (y - 1450) / (PANEL_TOP - 1450)
        r = int(80 + progress * 30)
        g = int(60 + progress * 20)
        b = int(40 + progress * 15)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Ripple texture on mudflats
    for x in range(0, WIDTH, 15):
        for y_offset in range(0, 200, 8):
            y = 1500 + y_offset
            wave = int(math.sin((x + y_offset) * 0.05) * 3)
            draw.point((x, y + wave), fill=(60, 45, 30))


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    """Draw the title panel at the bottom of the cover with white text on dark."""
    # Dark semi-transparent panel
    for y in range(PANEL_TOP, PANEL_BOTTOM):
        progress = (y - PANEL_TOP) / (PANEL_BOTTOM - PANEL_TOP)
        r = int(20 + progress * 10)
        g = int(25 + progress * 10)
        b = int(35 + progress * 10)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Top border accent line
    draw.line([(0, PANEL_TOP), (WIDTH, PANEL_TOP)], fill=(100, 160, 180), width=2)

    # Load fonts
    try:
        title_font = ImageFont.truetype(str(TITLE_FONT_PATH), 72)
        subtitle_font = ImageFont.truetype(str(TITLE_FONT_PATH), 48)
        author_font = ImageFont.truetype(str(AUTHOR_FONT_PATH), 36)
    except (OSError, IOError):
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Wrap title
    wrapped = textwrap.wrap(title, width=18)
    title_lines = wrapped if wrapped else [title]

    total_text_height = len(title_lines) * 80 + 60
    start_y = PANEL_TOP + (PANEL_BOTTOM - PANEL_TOP - total_text_height) // 2

    for i, line in enumerate(title_lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (WIDTH - tw) // 2
        ty = start_y + i * 80
        # Shadow
        draw.text((tx + 2, ty + 2), line, fill=(0, 0, 0), font=title_font)
        # Main text — WHITE
        draw.text((tx, ty), line, fill=(255, 255, 255), font=title_font)

    # Author name
    author_y = start_y + len(title_lines) * 80 + 20
    bbox = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox[2] - bbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax + 1, author_y + 1), author, fill=(0, 0, 0), font=author_font)
    draw.text((ax, author_y), author, fill=(200, 210, 220), font=author_font)


def draw_sunset_reflection(draw: ImageDraw.ImageDraw) -> None:
    """Draw sun reflection on the water channels."""
    cx = 800
    for offset in range(0, 80, 4):
        alpha = max(0, 80 - offset)
        r = int(255 * (1 - offset / 80))
        g = int(200 * (1 - offset / 80))
        for x in range(cx - 80 - offset, cx + 80 + offset, 4):
            y = 1350 + offset
            draw.point((x, y), fill=(r, g, 80, alpha) if alpha > 20 else (r, g, 80))


def create_cover(metadata: dict, output_path: Path) -> None:
    """Generate the full cover image."""
    title = metadata.get("title", "The Depth of Summer")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGB", (WIDTH, HEIGHT), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    draw_sky(draw)
    draw_sun(draw)
    draw_sunset_reflection(draw)
    draw_water_channels(draw)
    draw_mudflats(draw)
    draw_marsh_grass(draw)
    draw_skiff(draw)
    draw_heron(draw)
    draw_title_panel(draw, title, author)

    # Soft glow
    glow = img.filter(ImageFilter.GaussianBlur(radius=2))
    img = Image.blend(img, glow, 0.12)

    output_path.parent.mkdir(parents=True, exist_ok=True)
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

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    create_cover(metadata, args.out)


if __name__ == "__main__":
    main()