#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for Zero Day Protocol."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


FONT_DIR = Path("C:/Windows/Fonts")
WIDTH, HEIGHT = 1600, 2560
PANEL_Y = 1920

COLORS = {
    "bg_top": (5, 20, 5),
    "bg_mid": (10, 35, 10),
    "bg_bot": (0, 5, 0),
    "accent_green": (0, 180, 60),
    "accent_red": (220, 30, 30),
    "accent_dark_red": (140, 10, 10),
    "circuit_line": (0, 200, 80),
    "circuit_node": (0, 220, 100),
    "circuit_dim": (0, 100, 40),
    "warning_text": (255, 50, 50),
    "panel_bg": (240, 240, 248),
    "title_text": (5, 20, 5),
    "author_text": (60, 60, 80),
}


def make_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.5:
            t2 = t * 2
            r = int(COLORS["bg_top"][0] + (COLORS["bg_mid"][0] - COLORS["bg_top"][0]) * t2)
            g = int(COLORS["bg_top"][1] + (COLORS["bg_mid"][1] - COLORS["bg_top"][1]) * t2)
            b = int(COLORS["bg_top"][2] + (COLORS["bg_mid"][2] - COLORS["bg_top"][2]) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(COLORS["bg_mid"][0] + (COLORS["bg_bot"][0] - COLORS["bg_mid"][0]) * t2)
            g = int(COLORS["bg_mid"][1] + (COLORS["bg_bot"][1] - COLORS["bg_mid"][1]) * t2)
            b = int(COLORS["bg_mid"][2] + (COLORS["bg_bot"][2] - COLORS["bg_mid"][2]) * t2)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_scan_lines(draw: ImageDraw.ImageDraw) -> None:
    """Draw horizontal scan lines across the upper portion."""
    for y in range(0, PANEL_Y, 4):
        alpha = random.randint(2, 6)
        draw.line([(0, y), (WIDTH, y)], fill=(0, 255, 0, alpha))


def draw_circuit_traces(draw: ImageDraw.ImageDraw) -> None:
    """Draw circuit-board style traces."""
    for _ in range(30):
        x = random.randint(50, WIDTH - 50)
        y = random.randint(50, PANEL_Y - 200)
        length = random.randint(60, 300)
        direction = random.choice(["h", "v", "L", "7"])
        color = random.choice([COLORS["circuit_line"], COLORS["circuit_dim"], COLORS["circuit_line"]])
        line_w = random.choice([1, 2])

        if direction == "h":
            draw.line([(x, y), (x + length, y)], fill=color, width=line_w)
            draw.ellipse([x + length - 3, y - 3, x + length + 3, y + 3], fill=COLORS["circuit_node"])
        elif direction == "v":
            draw.line([(x, y), (x, y + length)], fill=color, width=line_w)
            draw.ellipse([x - 3, y + length - 3, x + 3, y + length + 3], fill=COLORS["circuit_node"])
        elif direction == "L":
            mid = length // 2
            draw.line([(x, y), (x + mid, y)], fill=color, width=line_w)
            draw.line([(x + mid, y), (x + mid, y + mid)], fill=color, width=line_w)
            draw.ellipse([x + mid - 3, y + mid - 3, x + mid + 3, y + mid + 3], fill=COLORS["circuit_node"])
        else:
            mid = length // 2
            draw.line([(x, y), (x, y + mid)], fill=color, width=line_w)
            draw.line([(x, y + mid), (x + mid, y + mid)], fill=color, width=line_w)
            draw.ellipse([x + mid - 3, y + mid - 3, x + mid + 3, y + mid + 3], fill=COLORS["circuit_node"])

    # Add some IC-like rectangles
    for _ in range(6):
        x = random.randint(100, WIDTH - 150)
        y = random.randint(100, PANEL_Y - 300)
        w = random.randint(40, 100)
        h = random.randint(30, 60)
        draw.rectangle([x, y, x + w, y + h], fill=(5, 30, 10), outline=COLORS["circuit_line"], width=1)
        # Pins
        for px in range(x + 5, x + w, 12):
            draw.line([(px, y - 6), (px, y)], fill=COLORS["circuit_line"], width=1)
            draw.line([(px, y + h), (px, y + h + 6)], fill=COLORS["circuit_line"], width=1)


def draw_warning_elements(draw: ImageDraw.ImageDraw) -> None:
    """Draw red warning symbols and countdown elements."""
    # Central warning triangle
    cx, cy = WIDTH // 2, PANEL_Y // 2 - 50
    size = 120

    # Triangle warning sign
    points = [(cx, cy - size), (cx - size, cy + size), (cx + size, cy + size)]
    draw.polygon(points, outline=COLORS["accent_red"], width=4)
    draw.polygon(points, fill=None)

    # Inner exclamation mark
    bar_x = cx - 6
    draw.rectangle([bar_x, cy - size + 40, bar_x + 12, cy + 10], fill=COLORS["accent_red"])
    draw.ellipse([cx - 8, cy + 25, cx + 8, cy + 45], fill=COLORS["accent_red"])

    # Pulsing rings around warning
    for i in range(3):
        radius = 160 + i * 40
        alpha = 40 - i * 10
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=(COLORS["accent_red"][0], COLORS["accent_red"][1], COLORS["accent_red"][2], alpha),
            width=2,
        )

    # Horizontal warning bars
    for i, y_pos in enumerate([150, 190, 230]):
        draw.rectangle([0, y_pos, WIDTH, y_pos + 3], fill=COLORS["accent_dark_red"])

    # Glitch lines (random red/bright-green horizontal streaks)
    for _ in range(15):
        y = random.randint(250, PANEL_Y - 100)
        x_start = random.randint(0, WIDTH - 200)
        x_end = x_start + random.randint(40, 300)
        glitch_color = random.choice([
            COLORS["accent_red"],
            COLORS["accent_green"],
            (255, 255, 255),
        ])
        draw.line([(x_start, y), (x_end, y)], fill=glitch_color, width=random.randint(1, 3))


def draw_digital_grid(draw: ImageDraw.ImageDraw) -> None:
    """Draw a subtle digital grid overlay."""
    # Vertical lines
    for x in range(0, WIDTH, 80):
        alpha = random.randint(3, 8)
        for y in range(0, PANEL_Y, 4):
            draw.point((x, y), fill=(0, 255, 0, alpha))

    # Horizontal lines
    for y in range(0, PANEL_Y, 80):
        alpha = random.randint(3, 8)
        for x in range(0, WIDTH, 3):
            draw.point((x, y), fill=(0, 255, 0, alpha))


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    draw.rectangle([0, PANEL_Y, WIDTH, HEIGHT], fill=COLORS["panel_bg"])

    separator_y = PANEL_Y + 8
    draw.rectangle([60, separator_y, WIDTH - 60, separator_y + 3], fill=(0, 120, 40))

    georgia_bold_path = FONT_DIR / "georgiab.ttf"
    arial_bold_path = FONT_DIR / "arialbd.ttf"

    try:
        title_font = ImageFont.truetype(str(georgia_bold_path), 72)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        author_font = ImageFont.truetype(str(arial_bold_path), 32)
    except Exception:
        author_font = ImageFont.load_default()

    # Split title into two lines
    words = title.split()
    if len(words) <= 3:
        lines = [title]
    elif len(words) <= 4:
        mid = len(words) // 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]
    else:
        mid = len(words) // 2 + len(words) % 2
        lines = [" ".join(words[:mid]), " ".join(words[mid:])]

    center_x = WIDTH // 2

    # Calculate total height of title block
    title_heights = []
    title_widths = []
    for line_text in lines:
        try:
            bbox = draw.textbbox((0, 0), line_text, font=title_font)
            w = bbox[2] - bbox[0]
            h = bbox[3] - bbox[1]
        except Exception:
            w, h = title_font.getsize(line_text)
        title_widths.append(w)
        title_heights.append(h)

    total_title_h = sum(title_heights) + (len(lines) - 1) * 10
    title_start_y = PANEL_Y + (HEIGHT - PANEL_Y - total_title_h) // 2 - 40

    for i, line_text in enumerate(lines):
        y_pos = title_start_y + sum(title_heights[:i]) + i * 10
        draw.text((center_x - title_widths[i] // 2, y_pos), line_text, fill=COLORS["title_text"], font=title_font)

    # Author name
    author_y = HEIGHT - 80
    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw, _ = author_font.getsize(author)
    draw.text((center_x - aw // 2, author_y), author, fill=COLORS["author_text"], font=author_font)

    # Small text line
    bottom_line = "A Techno-Thriller"
    try:
        small_font = ImageFont.truetype(str(FONT_DIR / "arial.ttf"), 16)
        sbbox = draw.textbbox((0, 0), bottom_line, font=small_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        small_font = ImageFont.load_default()
        sw, _ = small_font.getsize(bottom_line)
    draw.text((center_x - sw // 2, HEIGHT - 115), bottom_line, fill=(140, 140, 160), font=small_font)



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
    title = metadata["title"]
    author = metadata["author"]

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_top"])
    draw = ImageDraw.Draw(img, "RGBA")

    make_gradient(draw)
    draw_digital_grid(draw)
    draw_circuit_traces(draw)
    draw_warning_elements(draw)

    draw_rgb = ImageDraw.Draw(img)
    draw_title_panel(draw_rgb, title, author)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()