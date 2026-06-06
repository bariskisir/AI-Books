#!/usr/bin/env python3
"""Generate a cover image for The Hotel at the End of the World."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH, HEIGHT = 1600, 2560


def resolve_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Try to load arialbd/arial, fall back to default."""
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for path in candidates:
        p = Path(path)
        if p.exists():
            try:
                return ImageFont.truetype(str(p), size)
            except Exception:
                continue
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()


def draw_gradient(draw: ImageDraw.Draw) -> None:
    """Deep midnight-blue-to-gold gradient background."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        # midnight blue (10, 10, 50) -> deep navy -> dark gold -> gold accent
        r = int(10 + ratio * 180)
        g = int(10 + ratio * 130)
        b = int(50 + ratio * 30)
        if ratio > 0.6:
            # warm gold toward bottom
            r = int(120 + (ratio - 0.6) / 0.4 * 100)
            g = int(80 + (ratio - 0.6) / 0.4 * 60)
            b = int(20 + (ratio - 0.6) / 0.4 * 10)
        draw.line([(0, y), (WIDTH, y)], fill=(min(r, 255), min(g, 255), min(b, 255)))


def draw_mountains(draw: ImageDraw.Draw) -> None:
    """Patagonian mountain silhouettes."""
    peaks = [
        (0, 1400, 200, 1100, 400, 1300),
        (300, 1300, 500, 950, 700, 1200),
        (600, 1200, 800, 850, 1000, 1150),
        (900, 1150, 1100, 900, 1300, 1200),
        (1200, 1200, 1400, 1000, 1600, 1250),
    ]
    for x1, y1, x2, y2, x3, y3 in peaks:
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(20, 15, 40, 180))


def draw_hotel_facade(draw: ImageDraw.Draw) -> None:
    """Vintage hotel facade against the mountains."""
    # Main building
    hotel_left = 400
    hotel_top = 800
    hotel_width = 800
    hotel_height = 600

    # Building body
    draw.rectangle(
        [hotel_left, hotel_top, hotel_left + hotel_width, hotel_top + hotel_height],
        fill=(30, 25, 50, 200),
        outline=(180, 160, 100),
        width=3,
    )

    # Roof
    draw.polygon(
        [
            (hotel_left - 40, hotel_top),
            (hotel_left + hotel_width // 2, hotel_top - 120),
            (hotel_left + hotel_width + 40, hotel_top),
        ],
        fill=(40, 35, 60),
        outline=(180, 160, 100),
        width=3,
    )

    # Windows - rows and columns
    win_w, win_h = 60, 100
    gap_x, gap_y = 30, 50
    margin_x = 80
    margin_y = 60
    cols = (hotel_width - 2 * margin_x + gap_x) // (win_w + gap_x)
    rows = (hotel_height - 2 * margin_y + gap_y) // (win_h + gap_y)
    for row in range(rows):
        for col in range(cols):
            x = hotel_left + margin_x + col * (win_w + gap_x)
            y = hotel_top + margin_y + row * (win_h + gap_y)
            # Warm lit windows
            brightness = 200 + 55 * math.sin(row * 1.2 + col * 0.8)
            draw.rectangle(
                [x, y, x + win_w, y + win_h],
                fill=(int(brightness), int(brightness * 0.8), 60),
                outline=(100, 90, 50),
            )

    # Entrance door
    door_x = hotel_left + hotel_width // 2 - 50
    door_y = hotel_top + hotel_height - 160
    draw.rectangle(
        [door_x, door_y, door_x + 100, door_y + 160],
        fill=(60, 55, 80),
        outline=(180, 160, 100),
        width=3,
    )
    # Door arch
    draw.arc(
        [door_x, door_y - 40, door_x + 100, door_y + 10],
        start=180, end=0,
        fill=(180, 160, 100),
        width=3,
    )

    # Sign above entrance
    sign_y = door_y - 120
    draw.text(
        (WIDTH // 2, sign_y),
        "HOTEL",
        fill=(200, 180, 120),
        font=resolve_font(28, bold=True),
        anchor="mm",
    )


def draw_vintage_lobby(draw: ImageDraw.Draw) -> None:
    """Subtle vintage lobby elements at the bottom."""
    # Chandelier silhouette
    cx, cy = WIDTH // 2, 720
    draw.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], fill=(200, 180, 100))
    # Chains
    for offset in [-30, 0, 30]:
        for i in range(5):
            draw.ellipse(
                [cx + offset - 3, cy + 10 + i * 12 - 3, cx + offset + 3, cy + 10 + i * 12 + 3],
                fill=(180, 160, 90),
            )
    # Light glow
    draw.ellipse(
        [cx - 100, cy - 100, cx + 100, cy + 100],
        fill=(200, 180, 60, 20),
    )


def draw_title_panel(draw: ImageDraw.Draw) -> None:
    """Dark panel at bottom with white title text."""
    panel_top = 1920
    panel_height = 640

    # Semi-transparent dark panel
    for y in range(panel_top, HEIGHT):
        alpha = int(120 + (y - panel_top) / panel_height * 60)
        draw.line(
            [(0, y), (WIDTH, y)],
            fill=(10, 8, 25, min(alpha, 180)),
        )

    # Title
    title_font = resolve_font(64, bold=True)
    title = "The Hotel at the\nEnd of the World"
    draw.multiline_text(
        (WIDTH // 2, panel_top + 100),
        title,
        fill=(255, 255, 255),
        font=title_font,
        anchor="mm",
        align="center",
        spacing=10,
    )

    # Author
    author_font = resolve_font(32, bold=False)
    draw.text(
        (WIDTH // 2, panel_top + 240),
        "Barış Kısır",
        fill=(200, 180, 120),
        font=author_font,
        anchor="mm",
    )

    # Decorative line
    line_y = panel_top + 280
    draw.line(
        [(WIDTH // 2 - 150, line_y), (WIDTH // 2 + 150, line_y)],
        fill=(180, 160, 100),
        width=2,
    )



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
    parser.add_argument("--metadata", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    if args.metadata:
        metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
        title = metadata.get("title", "The Hotel at the End of the World")
    else:
        title = "The Hotel at the End of the World"

    out_path = args.out or Path("The_Hotel_at_the_End_of_the_World/covers/The_Hotel_at_the_End_of_the_World.png")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (10, 10, 50, 255))
    draw = ImageDraw.Draw(img)

    # Gradient background
    draw_gradient(draw)

    # Mountain silhouettes
    draw_mountains(draw)

    # Hotel facade
    draw_hotel_facade(draw)

    # Vintage lobby elements
    draw_vintage_lobby(draw)

    # Title panel
    draw_title_panel(draw)

    # Soft glow filter
    img = img.filter(ImageFilter.GaussianBlur(radius=1))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


if __name__ == "__main__":
    main()