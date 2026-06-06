#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Candidate's Wife."""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_Y = 1920


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list[str]:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = f"{current_line} {word}".strip()
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines


def draw_gradient(draw: ImageDraw.ImageDraw, colors: list[tuple[int, int, int]]) -> None:
    """Draw a vertical gradient background."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        segments = len(colors) - 1
        seg = min(int(ratio * segments), segments - 1)
        local_ratio = (ratio * segments) - seg
        r = int(colors[seg][0] * (1 - local_ratio) + colors[seg + 1][0] * local_ratio)
        g = int(colors[seg][1] * (1 - local_ratio) + colors[seg + 1][1] * local_ratio)
        b = int(colors[seg][2] * (1 - local_ratio) + colors[seg + 1][2] * local_ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_phone_screen(draw: ImageDraw.ImageDraw) -> None:
    """Draw a phone screen with tweet text."""
    phone_x, phone_y = WIDTH // 2 - 100, 380
    phone_w, phone_h = 200, 340
    draw.rounded_rectangle(
        [phone_x, phone_y, phone_x + phone_w, phone_y + phone_h],
        radius=16,
        fill=(30, 30, 35),
        outline=(80, 80, 90),
        width=3,
    )
    # Screen area
    screen_x = phone_x + 12
    screen_y = phone_y + 40
    screen_w = phone_w - 24
    screen_h = phone_h - 50
    draw.rectangle([screen_x, screen_y, screen_x + screen_w, screen_y + screen_h], fill=(20, 25, 35))
    # Tweet text lines
    tweet_lines = [
        "Mark's speechwriter",
        "thinks 'compassion'",
        "is a noun you",
        "conjugate like a",
        "verb. The",
        "teleprompter is",
        "the real",
        "candidate tonight.",
    ]
    try:
        font_small = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 14)
    except (OSError, IOError):
        font_small = ImageFont.load_default()
    ty = screen_y + 10
    for line in tweet_lines:
        draw.text((screen_x + 10, ty), line, fill=(200, 220, 255), font=font_small)
        ty += 18
    # Send button
    draw.rounded_rectangle(
        [screen_x + screen_w - 50, screen_y + screen_h - 30, screen_x + screen_w - 10, screen_y + screen_h - 10],
        radius=6,
        fill=(29, 155, 240),
    )
    try:
        font_tiny = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 11)
    except (OSError, IOError):
        font_tiny = ImageFont.load_default()
    draw.text((screen_x + screen_w - 38, screen_y + screen_h - 26), "Send", fill=(255, 255, 255), font=font_tiny)


def draw_press_conference(draw: ImageDraw.ImageDraw) -> None:
    """Draw a podium and microphones."""
    # Podium
    podium_x, podium_y = WIDTH // 2 - 120, 850
    draw.rectangle([podium_x, podium_y, podium_x + 240, podium_y + 100], fill=(40, 40, 50), outline=(60, 60, 70), width=2)
    # Seal on podium
    draw.ellipse([podium_x + 80, podium_y + 15, podium_x + 160, podium_y + 55], fill=(30, 70, 130), outline=(60, 120, 200), width=2)
    # Microphones
    for mx_offset in [-30, 0, 30]:
        mx = WIDTH // 2 + mx_offset
        draw.rectangle([mx - 3, podium_y - 50, mx + 3, podium_y], fill=(100, 100, 110))
        draw.ellipse([mx - 8, podium_y - 65, mx + 8, podium_y - 50], fill=(80, 80, 90))
    # Camera flashes right side
    flash_x = WIDTH - 200
    for f_i in range(5):
        fx = flash_x + (f_i % 3) * 40
        fy = 900 + (f_i // 3) * 30
        draw.rectangle([fx, fy, fx + 20, fy + 15], fill=(50, 50, 60))
        flash_color = (200, 200, 100) if f_i % 2 == 0 else (180, 180, 80)
        draw.polygon([(fx + 10, fy - 8), (fx + 4, fy), (fx + 16, fy)], fill=flash_color)
    # Light beams from flashes
    for _ in range(3):
        lx = flash_x + 10
        ly = 870
        draw.polygon(
            [(lx, ly), (lx - 100, ly + 200), (lx + 100, ly + 200)],
            fill=(200, 200, 100, 20),
        )


def draw_chaos_elements(draw: ImageDraw.ImageDraw) -> None:
    """Draw abstract chaos elements - tweets, symbols, sparks."""
    # Floating tweet bubbles
    bubble_positions = [(100, 600), (1300, 500), (200, 1100), (1350, 1000)]
    for bx, by in bubble_positions:
        draw.rounded_rectangle([bx, by, bx + 100, by + 50], radius=8, fill=(30, 40, 60), outline=(60, 80, 120), width=1)
        draw.text((bx + 10, by + 10), "@voter", fill=(100, 150, 255), font=ImageFont.load_default())
        draw.text((bx + 10, by + 28), "...wait, what?", fill=(200, 200, 220), font=ImageFont.load_default())
    # Alert/warning symbols
    draw.polygon([(800, 450), (780, 500), (820, 500)], fill=(255, 200, 50))
    draw.polygon([(780, 1400), (760, 1450), (800, 1450)], fill=(255, 200, 50))
    # Trend lines
    for tx in range(0, WIDTH, WIDTH // 6):
        ty_base = 1200
        draw.line(
            [(tx, ty_base + 50), (tx + WIDTH // 12, ty_base + 30), (tx + WIDTH // 6, ty_base + 60)],
            fill=(255, 100, 100, 80),
            width=2,
        )


def create_cover(metadata: dict, output_path: Path) -> None:
    """Generate the cover image."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (10, 10, 30))
    draw = ImageDraw.Draw(img)

    # Background gradient: dark blue -> red -> dark
    draw_gradient(draw, [(10, 15, 45), (60, 20, 30), (15, 10, 25)])

    # Apply slight blur for depth
    img = img.filter(ImageFilter.GaussianBlur(radius=2))
    draw = ImageDraw.Draw(img)

    # Draw press conference elements
    draw_press_conference(draw)

    # Draw phone screen
    draw_phone_screen(draw)

    # Draw chaos elements
    draw_chaos_elements(draw)

    # Title panel at bottom
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, HEIGHT], fill=(240, 240, 245, 230))

    # Add a subtle red/blue stripe at top of panel
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH // 2, TITLE_PANEL_Y + 6], fill=(200, 50, 50))
    draw.rectangle([WIDTH // 2, TITLE_PANEL_Y, WIDTH, TITLE_PANEL_Y + 6], fill=(50, 80, 180))

    # Load fonts
    try:
        font_title = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 80)
        font_title_small = ImageFont.truetype("C:/Windows/Fonts/georgiab.ttf", 56)
        font_author = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 40)
        font_tagline = ImageFont.truetype("C:/Windows/Fonts/arial.ttf", 22)
    except (OSError, IOError) as e:
        print(f"Warning: Could not load fonts: {e}")
        font_title = ImageFont.load_default()
        font_title_small = ImageFont.load_default()
        font_author = ImageFont.load_default()
        font_tagline = ImageFont.load_default()

    # Title text
    title_text = metadata.get("title", "The Candidate's Wife")
    title_lines = wrap_text(title_text, font_title, WIDTH - 120, draw)

    # Draw title centered in the panel
    title_panel_center_y = TITLE_PANEL_Y + (HEIGHT - TITLE_PANEL_Y) // 2 - 40

    if len(title_lines) == 1:
        bbox = draw.textbbox((0, 0), title_lines[0], font=font_title)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw) // 2, title_panel_center_y - 30), title_lines[0], fill=(20, 20, 30), font=font_title)
    else:
        total_h = 0
        for i, line in enumerate(title_lines):
            if i == 0:
                bbox = draw.textbbox((0, 0), line, font=font_title_small)
            else:
                bbox = draw.textbbox((0, 0), line, font=font_title_small)
            total_h += (bbox[3] - bbox[1]) + 10
        current_y = title_panel_center_y - total_h // 2
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=font_title_small)
            tw = bbox[2] - bbox[0]
            draw.text(((WIDTH - tw) // 2, current_y), line, fill=(20, 20, 30), font=font_title_small)
            current_y += (bbox[3] - bbox[1]) + 10

    # Author name
    author_name = metadata.get("author", "Barış Kısır")
    bbox = draw.textbbox((0, 0), author_name, font=font_author)
    aw = bbox[2] - bbox[0]
    draw.text(((WIDTH - aw) // 2, TITLE_PANEL_Y + (HEIGHT - TITLE_PANEL_Y) - 80), author_name, fill=(60, 60, 70), font=font_author)

    # Genre tagline
    genre = metadata.get("genre", "")
    if genre:
        bbox = draw.textbbox((0, 0), f"A {genre} Novel", font=font_tagline)
        gw = bbox[2] - bbox[0]
        draw.text(((WIDTH - gw) // 2, TITLE_PANEL_Y + (HEIGHT - TITLE_PANEL_Y) - 130), f"A {genre} Novel", fill=(120, 120, 130), font=font_tagline)

    # Save
    output_path.parent.mkdir(parents=True, exist_ok=True)
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

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    create_cover(metadata, args.out)


if __name__ == "__main__":
    main()