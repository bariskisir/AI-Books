#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Radio Operator."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1600, 2560
TITLE_FONT_SIZE = 100
AUTHOR_FONT_SIZE = 48
TAGLINE_FONT_SIZE = 30
FONT_PATH = Path("C:/Windows/Fonts/arialbd.ttf")
FONT_PATH_REG = Path("C:/Windows/Fonts/arial.ttf")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def draw_gradient(draw: ImageDraw, top_color: tuple, bottom_color: tuple) -> None:
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_morse_code(draw: ImageDraw) -> None:
    """Draw morse code dots and dashes across the image."""
    morse = ".-. .- -.. .. ---"
    dot_radius = 4
    dash_w, dash_h = 20, 4
    start_y = 400
    x = 100
    y = start_y
    for ch in morse:
        if ch == ".":
            draw.ellipse([x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                         fill=(200, 180, 120, 60))
            x += 20
        elif ch == "-":
            draw.rectangle([x, y - dash_h // 2, x + dash_w, y + dash_h // 2],
                           fill=(200, 180, 120, 60))
            x += dash_w + 8
        elif ch == " ":
            x += 30
        elif ch == "/":
            x += 40
    # Second line of morse
    y = 550
    x = WIDTH - 300
    for ch in ".--. .- -. -.-. . ..- .--.":
        if ch == ".":
            draw.ellipse([x - dot_radius, y - dot_radius, x + dot_radius, y + dot_radius],
                         fill=(200, 160, 100, 40))
            x += 18
        elif ch == "-":
            draw.rectangle([x, y - dash_h // 2, x + dash_w, y + dash_h // 2],
                           fill=(200, 160, 100, 40))
            x += dash_w + 6
        elif ch == " ":
            x += 25
        elif ch == "/":
            x += 35


def draw_radio_equipment(draw: ImageDraw) -> None:
    """Draw simplified radio equipment using PIL primitives."""
    # Main radio unit
    rx, ry = 400, 850
    rw, rh = 800, 500

    # Radio body
    draw.rounded_rectangle([rx, ry, rx + rw, ry + rh], radius=15,
                           fill=(60, 55, 45), outline=(140, 130, 100), width=3)

    # Speaker grille (horizontal lines)
    grille_y = ry + 40
    for i in range(10):
        draw.rectangle([rx + 60, grille_y + i * 18, rx + 180, grille_y + i * 18 + 6],
                       fill=(100, 95, 80))
        draw.rectangle([rx + 200, grille_y + i * 18, rx + 320, grille_y + i * 18 + 6],
                       fill=(100, 95, 80))

    # Dials
    dial_centers = [(rx + 500, ry + 100), (rx + 650, ry + 100), (rx + 500, ry + 280), (rx + 650, ry + 280)]
    for cx, cy in dial_centers:
        draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45],
                     fill=(30, 28, 25), outline=(160, 150, 120), width=2)
        draw.ellipse([cx - 35, cy - 35, cx + 35, cy + 35],
                     fill=(50, 48, 40), outline=(120, 110, 90), width=1)
        # Needle
        draw.line([(cx, cy), (cx + 15, cy - 25)], fill=(200, 80, 40), width=3)

    # Frequency display panel
    draw.rectangle([rx + 480, ry + 190, rx + 740, ry + 250],
                   fill=(20, 60, 30), outline=(100, 140, 100), width=2)

    # Dial markings
    for cx, cy in dial_centers:
        for angle in range(0, 360, 30):
            import math
            rad = math.radians(angle)
            x1 = cx + 30 * math.cos(rad)
            y1 = cy + 30 * math.sin(rad)
            x2 = cx + 40 * math.cos(rad)
            y2 = cy + 40 * math.sin(rad)
            draw.line([(x1, y1), (x2, y2)], fill=(180, 170, 140), width=1)

    # Knobs at bottom of radio
    for i, offset_x in enumerate([rx + 150, rx + 350, rx + 550, rx + 650]):
        draw.ellipse([offset_x, ry + rh - 80, offset_x + 60, ry + rh - 20],
                     fill=(40, 38, 30), outline=(150, 140, 110), width=2)
        # Knob grip lines
        for j in range(4):
            angle = j * 45
            import math
            rad = math.radians(angle)
            cx2 = offset_x + 30 + 15 * math.cos(rad)
            cy2 = ry + rh - 50 + 15 * math.sin(rad)
            draw.line([(offset_x + 30, ry + rh - 50), (cx2, cy2)],
                      fill=(180, 170, 140), width=1)


def draw_headphones(draw: ImageDraw) -> None:
    """Draw a pair of headphones hanging nearby."""
    hx, hy = 200, 680
    # Headband
    draw.arc([hx, hy, hx + 200, hy + 180], start=0, end=180,
             fill=(100, 95, 80), width=12)
    # Ear cups
    draw.ellipse([hx - 10, hy + 120, hx + 50, hy + 200],
                 fill=(50, 48, 40), outline=(140, 130, 100), width=3)
    draw.ellipse([hx + 160, hy + 120, hx + 220, hy + 200],
                 fill=(50, 48, 40), outline=(140, 130, 100), width=3)
    # Ear cup padding
    draw.ellipse([hx + 2, hy + 132, hx + 38, hy + 188],
                 fill=(80, 75, 65), outline=(160, 150, 120), width=1)
    draw.ellipse([hx + 172, hy + 132, hx + 208, hy + 188],
                 fill=(80, 75, 65), outline=(160, 150, 120), width=1)
    # Cord
    draw.line([(hx + 20, hy + 200), (hx + 20, hy + 380), (hx + 400, hy + 380)],
              fill=(60, 58, 50), width=3)


def draw_bunker_elements(draw: ImageDraw) -> None:
    """Draw subtle bunker/fortification elements."""
    # Sandbags at top
    for i in range(12):
        bx = i * 140 - 20
        by = 50
        draw.rounded_rectangle([bx, by, bx + 130, by + 50], radius=8,
                               fill=(110, 100, 70), outline=(140, 130, 100), width=2)
        draw.rounded_rectangle([bx + 10, by + 40, bx + 140, by + 90], radius=8,
                               fill=(100, 90, 65), outline=(130, 120, 95), width=2)

    # Barbed wire / defense lines at top
    for i in range(8):
        wx = i * 220 + 50
        draw.line([(wx, 160), (wx + 80, 200), (wx + 160, 160)],
                  fill=(120, 110, 90), width=3)
        # Barbs
        draw.line([(wx + 30, 175), (wx + 40, 195)], fill=(150, 140, 120), width=2)
        draw.line([(wx + 80, 200), (wx + 70, 220)], fill=(150, 140, 120), width=2)
        draw.line([(wx + 130, 175), (wx + 120, 195)], fill=(150, 140, 120), width=2)


def draw_signal_waves(draw: ImageDraw) -> None:
    """Draw radio signal waves emanating from the equipment."""
    for i in range(5):
        y_base = 1450 + i * 60
        points = []
        for x in range(200, WIDTH - 100, 10):
            from math import sin, radians
            wave = 20 * sin(radians(x * 1.5 + i * 40))
            points.append((x, y_base + wave))
        if len(points) > 1:
            draw.line(points, fill=(180, 200, 160, 80 - i * 12), width=3 - i // 3)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    with open(metadata_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Warm olive to sepia gradient
    top_color = (85, 75, 50)
    bottom_color = (45, 35, 20)
    draw_gradient(draw, top_color, bottom_color)

    # Draw elements
    draw_bunker_elements(draw)
    draw_morse_code(draw)
    draw_headphones(draw)
    draw_radio_equipment(draw)
    draw_signal_waves(draw)

    # Title panel at bottom
    panel_y1 = 1920
    panel_y2 = 2560
    draw.rectangle([(0, panel_y1), (WIDTH, panel_y2)], fill=(20, 18, 15, 230))

    # Load fonts
    try:
        title_font = ImageFont.truetype(str(FONT_PATH), TITLE_FONT_SIZE)
        author_font = ImageFont.truetype(str(FONT_PATH_REG), AUTHOR_FONT_SIZE)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Title - white text
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_w) // 2
    title_y = panel_y1 + 100
    draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font)

    # Author below title
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = author_bbox[2] - author_bbox[0]
    author_x = (WIDTH - author_w) // 2
    author_y = title_y + 140
    draw.text((author_x, author_y), author, fill=(200, 190, 170), font=author_font)

    # Save
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
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)