#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Train in the Snow."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1600, 2560


def draw_gradient(draw: ImageDraw.ImageDraw) -> None:
    """Draw a vertical gradient from midnight blue (top) to icy white (bottom)."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(10 + ratio * 200)
        g = int(15 + ratio * 210)
        b = int(50 + ratio * 230)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_mountains(draw: ImageDraw.ImageDraw) -> None:
    """Draw stylized alpine landscape with snow-capped peaks."""
    # Background mountains (lighter blue)
    peaks = [
        (0, 1400, 250, 920, 500, 1400),
        (300, 1400, 600, 860, 900, 1400),
        (700, 1400, 1000, 800, 1300, 1400),
        (1100, 1400, 1400, 900, 1600, 1400),
    ]
    for x1, y1, x2, y2, x3, y3 in peaks:
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(70, 90, 140, 180))

    # Foreground mountains (deeper blue)
    fg_peaks = [
        (-50, 1500, 200, 1050, 450, 1500),
        (400, 1500, 650, 1000, 900, 1500),
        (800, 1500, 1050, 980, 1300, 1500),
        (1200, 1500, 1450, 1020, 1650, 1500),
    ]
    for x1, y1, x2, y2, x3, y3 in fg_peaks:
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(30, 45, 90))

    # Snow caps on foreground peaks
    snow_caps = [
        (160, 1080, 200, 1050, 240, 1080),
        (610, 1030, 650, 1000, 690, 1030),
        (1010, 1010, 1050, 980, 1090, 1010),
        (1410, 1050, 1450, 1020, 1490, 1050),
    ]
    for x1, y1, x2, y2, x3, y3 in snow_caps:
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(220, 230, 245))


def draw_train(draw: ImageDraw.ImageDraw) -> None:
    """Draw a stylized snowbound train on the tracks."""
    # Snow-covered ground
    draw.rectangle([(0, 1400), (WIDTH, 1550)], fill=(230, 240, 250))

    # Train body
    train_x, train_y = 450, 1280
    train_w, train_h = 700, 180

    # Locomotive body
    draw.rectangle([(train_x, train_y), (train_x + train_w, train_y + train_h)], fill=(20, 30, 60))
    # Locomotive cabin
    draw.rectangle([(train_x + 50, train_y - 40), (train_x + 180, train_y)], fill=(25, 35, 70))
    # Smokestack
    draw.rectangle([(train_x + 90, train_y - 70), (train_x + 120, train_y - 40)], fill=(40, 40, 40))
    # Smokestack top
    draw.ellipse([(train_x + 85, train_y - 80), (train_x + 125, train_y - 65)], fill=(50, 50, 50))

    # Boiler door on front
    draw.ellipse([(train_x + train_w - 60, train_y + 40), (train_x + train_w - 10, train_y + 90)], fill=(80, 60, 40))
    # Headlight
    draw.ellipse([(train_x + train_w - 10, train_y + 20), (train_x + train_w + 10, train_y + 50)], fill=(255, 240, 180))

    # Cowcatcher
    draw.polygon(
        [
            (train_x + train_w, train_y + train_h - 20),
            (train_x + train_w + 40, train_y + train_h + 10),
            (train_x + train_w, train_y + train_h),
        ],
        fill=(40, 40, 40),
    )

    # Carriages
    for i in range(3):
        cx = train_x - 190 * (i + 1)
        draw.rectangle([(cx, train_y + 10), (cx + 170, train_y + train_h - 10)], fill=(25, 35, 70))
        # Windows
        for j in range(4):
            wx = cx + 15 + j * 38
            draw.rectangle([(wx, train_y + 30), (wx + 25, train_y + 70)], fill=(100, 120, 180))
            # Warm window glow
            draw.rectangle([(wx + 2, train_y + 32), (wx + 23, train_y + 68)], fill=(200, 180, 120))

    # Wheels
    for wx in [train_x + 50, train_x + 200, train_x + 350, train_x + 550, train_x + 650]:
        draw.ellipse([(wx, train_y + train_h - 15), (wx + 35, train_y + train_h + 20)], fill=(50, 50, 50))

    # Tracks
    draw.line([(0, train_y + train_h + 15), (WIDTH, train_y + train_h + 15)], fill=(80, 80, 80), width=4)
    draw.line([(0, train_y + train_h + 30), (WIDTH, train_y + train_h + 30)], fill=(80, 80, 80), width=4)

    # Snow on top of train
    snow_y = train_y - 5
    for i in range(-3, 4):
        sx = train_x + i * 100
        sw = 120
        draw.ellipse([(sx, snow_y - 8), (sx + sw, snow_y + 3)], fill=(240, 245, 255))


def draw_steam(draw: ImageDraw.ImageDraw) -> None:
    """Draw stylized steam from the locomotive."""
    steam_base = (540, 1190)
    # Multiple overlapping translucent circles for steam
    steam_positions = [
        (540, 1180, 40),
        (510, 1150, 55),
        (560, 1140, 45),
        (490, 1110, 60),
        (550, 1100, 50),
        (470, 1070, 45),
        (530, 1050, 55),
        (450, 1020, 35),
        (510, 1000, 40),
    ]
    for sx, sy, sr in steam_positions:
        draw.ellipse(
            [(sx - sr, sy - sr), (sx + sr, sy + sr)],
            fill=(200, 210, 230, 60),
        )


def draw_snowflakes(draw: ImageDraw.ImageDraw) -> None:
    """Draw scattered snowflakes in the sky."""
    flakes = [
        (100, 300, 3),
        (300, 150, 2),
        (500, 400, 4),
        (700, 200, 3),
        (900, 350, 2),
        (1100, 100, 3),
        (1300, 450, 4),
        (1500, 250, 2),
        (200, 600, 3),
        (400, 500, 2),
        (800, 550, 3),
        (1200, 600, 2),
        (1400, 400, 3),
        (600, 700, 2),
        (1000, 650, 4),
        (300, 800, 2),
        (1100, 800, 3),
        (700, 900, 2),
        (900, 750, 3),
        (150, 450, 2),
    ]
    for fx, fy, fs in flakes:
        # Draw star-like snowflake
        for i in range(4):
            angle = i * 45
            import math
            ex = fx + fs * math.cos(math.radians(angle))
            ey = fy + fs * math.sin(math.radians(angle))
            draw.line([(fx, fy), (ex, ey)], fill=(255, 255, 255, 180), width=1)


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    """Draw the title panel at the bottom of the cover with WHITE text on dark panel."""
    panel_top = 1920

    # Dark semi-transparent panel
    draw.rectangle([(0, panel_top), (WIDTH, HEIGHT)], fill=(15, 20, 45, 220))

    # Decorative line above title
    draw.line([(400, panel_top + 30), (1200, panel_top + 30)], fill=(180, 190, 210), width=2)
    draw.line([(600, panel_top + 36), (1000, panel_top + 36)], fill=(180, 190, 210), width=1)

    # Snowflake ornament
    draw.ellipse([(780, panel_top + 50), (820, panel_top + 70)], fill=(180, 190, 210))

    # Title - use arialbd.ttf
    try:
        font_large = ImageFont.truetype("arialbd.ttf", 72)
        font_medium = ImageFont.truetype("arialbd.ttf", 42)
        font_author = ImageFont.truetype("arialbd.ttf", 24)
    except (OSError, IOError):
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_author = ImageFont.load_default()

    # Title
    title_text = title.upper()
    bbox = draw.textbbox((0, 0), title_text, font=font_large)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, panel_top + 85), title_text, fill=(255, 255, 255), font=font_large)

    # Decorative line below title
    draw.line([(500, panel_top + 175), (1100, panel_top + 175)], fill=(140, 150, 180), width=1)

    # Genre line
    genre_text = "A Winter Mystery"
    bbox = draw.textbbox((0, 0), genre_text, font=font_medium)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, panel_top + 200), genre_text, fill=(200, 210, 230), font=font_medium)

    # Author
    author_text = f"by {author}"
    bbox = draw.textbbox((0, 0), author_text, font=font_author)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, panel_top + 270), author_text, fill=(255, 255, 255), font=font_author)

    # Decorative line at bottom
    draw.line([(400, panel_top + 320), (1200, panel_top + 320)], fill=(180, 190, 210), width=2)


def build(metadata_path: Path, output_path: Path) -> None:
    """Generate the cover image."""
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw)
    draw_mountains(draw)
    draw_train(draw)
    draw_steam(draw)
    draw_snowflakes(draw)
    draw_title_panel(draw, title, author)

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
    build(args.metadata, args.out)


if __name__ == "__main__":
    main()