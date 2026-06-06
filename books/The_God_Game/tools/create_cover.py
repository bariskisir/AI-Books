#!/usr/bin/env python3
"""Generate a 1600x2560 PNG book cover for The God Game."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH, HEIGHT = 1600, 2560
PANEL_TOP = 1920
FONTS_DIR = Path("C:/Windows/Fonts")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def make_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Vertical gradient: deep crimson (top) to very dark red (mid) to near-black (bottom)."""
    colors = [
        (30, 5, 8),     # near-black
        (60, 10, 15),   # very dark red
        (90, 15, 20),   # dark maroon
        (140, 25, 35),  # deep crimson
        (180, 40, 50),  # rich red
        (140, 25, 35),  # deep crimson
        (80, 12, 18),   # dark maroon
        (40, 6, 10),    # very dark
        (20, 3, 5),     # near-black
    ]
    band_height = height // len(colors)
    for i, (r, g, b) in enumerate(colors):
        for y in range(i * band_height, (i + 1) * band_height if i < len(colors) - 1 else height):
            draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_arches(draw: ImageDraw, width: int, height: int) -> None:
    """Draw arched library windows / alcoves suggesting the Vatican library."""
    arch_color = (60, 50, 40, 40)
    for i in range(4):
        cx = width // 5 * (i + 1)
        top_y = height // 6
        arch_width = 180
        arch_height = 300
        left = cx - arch_width // 2
        right = cx + arch_width // 2
        # Arch top (semicircle)
        draw.arc([left, top_y, right, top_y + arch_width], 0, 180, fill=(80, 65, 55, 40), width=3)
        # Pillars
        draw.line([left, top_y + arch_width // 2, left, top_y + arch_width // 2 + arch_height], fill=(70, 55, 45), width=4)
        draw.line([right, top_y + arch_width // 2, right, top_y + arch_width // 2 + arch_height], fill=(70, 55, 45), width=4)
        # Faint glow inside arch
        glow = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.ellipse([left + 10, top_y + 20, right - 10, top_y + arch_width - 10], fill=(200, 160, 80, 15))
        draw.bitmap((0, 0), glow, fill=None)


def draw_scroll(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an ancient scroll in the center of the image."""
    cx = width // 2
    cy = height // 2 - 100
    scroll_width = 500
    scroll_height = 200
    left = cx - scroll_width // 2
    right = cx + scroll_width // 2
    top = cy - scroll_height // 2
    bottom = cy + scroll_height // 2

    # Scroll body
    draw.rectangle([left, top, right, bottom], fill=(180, 160, 120, 60), outline=(200, 180, 140, 80))
    # Rolled top edge
    draw.ellipse([left - 10, top - 15, left + 20, top + 15], fill=(160, 140, 100, 80))
    draw.ellipse([right - 20, top - 15, right + 10, top + 15], fill=(160, 140, 100, 80))
    # Rolled bottom edge
    draw.ellipse([left - 10, bottom - 15, left + 20, bottom + 15], fill=(160, 140, 100, 80))
    draw.ellipse([right - 20, bottom - 15, right + 10, bottom + 15], fill=(160, 140, 100, 80))
    # Script lines
    script_y = top + 30
    while script_y < bottom - 20:
        draw.line([left + 25, script_y, right - 25, script_y], fill=(100, 85, 60, 40), width=2)
        script_y += 18


def draw_candlelight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw candle glow effects at the bottom and sides."""
    # Bottom candle glow
    for radius in range(200, 50, -10):
        alpha = max(0, 30 - (200 - radius) // 7)
        if alpha <= 0:
            continue
        draw.ellipse(
            [width // 2 - radius, height - radius * 2, width // 2 + radius, height + radius],
            fill=(220, 180, 80, alpha),
        )
    # Small candle flame near bottom-left
    candle_x, candle_y = 250, HEIGHT - 300
    draw.ellipse([candle_x - 8, candle_y - 20, candle_x + 8, candle_y], fill=(255, 220, 100, 180))
    draw.ellipse([candle_x - 5, candle_y - 35, candle_x + 5, candle_y - 20], fill=(255, 200, 80, 160))
    # Candle body
    draw.rectangle([candle_x - 6, candle_y, candle_x + 6, candle_y + 80], fill=(220, 200, 170, 200))
    # Light pool from candle
    for r in range(150, 10, -10):
        a = max(0, 12 - (150 - r) // 15)
        if a <= 0:
            continue
        draw.ellipse(
            [candle_x - r, candle_y - r * 2, candle_x + r, candle_y + r],
            fill=(255, 200, 100, a),
        )
    # Second candle right side
    candle2_x, candle2_y = WIDTH - 250, HEIGHT - 400
    draw.ellipse([candle2_x - 8, candle2_y - 20, candle2_x + 8, candle2_y], fill=(255, 220, 100, 180))
    draw.ellipse([candle2_x - 5, candle2_y - 35, candle2_x + 5, candle2_y - 20], fill=(255, 200, 80, 160))
    draw.rectangle([candle2_x - 6, candle2_y, candle2_x + 6, candle2_y + 80], fill=(220, 200, 170, 200))
    for r in range(120, 10, -10):
        a = max(0, 10 - (120 - r) // 15)
        if a <= 0:
            continue
        draw.ellipse(
            [candle2_x - r, candle2_y - r * 2, candle2_x + r, candle2_y + r],
            fill=(255, 200, 100, a),
        )


def draw_title_panel(img: Image, draw: ImageDraw, title: str, author: str) -> None:
    """Draw the bottom title panel with light rectangle."""
    # Light rectangle panel
    draw.rectangle([0, PANEL_TOP, WIDTH, HEIGHT], fill=(240, 230, 215, 220))
    # Top border line
    draw.line([0, PANEL_TOP, WIDTH, PANEL_TOP], fill=(180, 160, 130, 200), width=3)

    try:
        title_font = ImageFont.truetype(str(FONTS_DIR / "georgiab.ttf"), 72)
        title_small = ImageFont.truetype(str(FONTS_DIR / "georgiab.ttf"), 56)
        author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 40)
        small_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 28)
    except (IOError, OSError):
        try:
            title_font = ImageFont.truetype(str(FONTS_DIR / "georgia.ttf"), 72)
            title_small = ImageFont.truetype(str(FONTS_DIR / "georgia.ttf"), 56)
            author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 40)
            small_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 28)
        except (IOError, OSError):
            title_font = ImageFont.load_default()
            title_small = ImageFont.load_default()
            author_font = ImageFont.load_default()
            small_font = ImageFont.load_default()

    y = PANEL_TOP + 40
    genre_line = "A Religious Thriller"
    try:
        bbox = small_font.getbbox(genre_line)
        tw = bbox[2] - bbox[0] if bbox else small_font.getlength(genre_line)
        draw.text(((WIDTH - tw) / 2, y), genre_line, fill=(120, 100, 80), font=small_font)
    except AttributeError:
        draw.text((WIDTH // 2, y), genre_line, fill=(120, 100, 80), font=small_font, anchor="mt")

    y += 50

    # Title - wrap if too long
    title_text = title.upper()
    try:
        bbox = title_font.getbbox(title_text)
        tw = bbox[2] - bbox[0] if bbox else title_font.getlength(title_text)
    except AttributeError:
        tw = 0

    if tw > WIDTH - 100:
        # Split title into words and wrap
        words = title_text.split()
        line1 = ""
        line2 = ""
        half = len(words) // 2
        line1 = " ".join(words[:half])
        line2 = " ".join(words[half:])
        try:
            bbox = title_small.getbbox(line1)
            tw1 = bbox[2] - bbox[0] if bbox else title_small.getlength(line1)
            draw.text(((WIDTH - tw1) / 2, y), line1, fill=(40, 20, 15), font=title_small)
        except AttributeError:
            draw.text((WIDTH // 2, y), line1, fill=(40, 20, 15), font=title_small, anchor="mt")
        y += title_small.size + 10 if hasattr(title_small, 'size') else 66
        try:
            bbox = title_small.getbbox(line2)
            tw2 = bbox[2] - bbox[0] if bbox else title_small.getlength(line2)
            draw.text(((WIDTH - tw2) / 2, y), line2, fill=(40, 20, 15), font=title_small)
        except AttributeError:
            draw.text((WIDTH // 2, y), line2, fill=(40, 20, 15), font=title_small, anchor="mt")
    else:
        try:
            bbox = title_font.getbbox(title_text)
            tw = bbox[2] - bbox[0] if bbox else title_font.getlength(title_text)
            draw.text(((WIDTH - tw) / 2, y), title_text, fill=(40, 20, 15), font=title_font)
        except AttributeError:
            draw.text((WIDTH // 2, y), title_text, fill=(40, 20, 15), font=title_font, anchor="mt")

    if hasattr(title_font, 'size'):
        y += title_font.size + 30
    else:
        y += 102

    # Author
    author_text = f"by {author}"
    try:
        bbox = author_font.getbbox(author_text)
        tw = bbox[2] - bbox[0] if bbox else author_font.getlength(author_text)
        draw.text(((WIDTH - tw) / 2, y), author_text, fill=(80, 60, 50), font=author_font)
    except AttributeError:
        draw.text((WIDTH // 2, y), author_text, fill=(80, 60, 50), font=author_font, anchor="mt")


def create_cover(title: str, author: str, output_path: Path) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient
    make_gradient(draw, WIDTH, HEIGHT)

    # Vatican arches
    draw_arches(draw, WIDTH, HEIGHT)

    # Scroll
    draw_scroll(draw, WIDTH, HEIGHT)

    # Candlelight
    draw_candlelight(draw, WIDTH, HEIGHT)

    # Vignette overlay
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for r in range(max(WIDTH, HEIGHT) // 2, 0, -10):
        alpha = max(0, 60 - (max(WIDTH, HEIGHT) // 2 - r) // 5)
        if alpha <= 0:
            continue
        vdraw.ellipse(
            [WIDTH // 2 - r, HEIGHT // 2 - r, WIDTH // 2 + r, HEIGHT // 2 + r],
            fill=(0, 0, 0, alpha),
        )
    img = Image.alpha_composite(img, vignette)

    # Convert back to RGB for drawing
    rgb = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    rgb.paste(img, (0, 0), img)
    draw = ImageDraw.Draw(rgb)

    # Title panel
    draw_title_panel(rgb, draw, title, author)

    # Subtle noise filter for texture
    _draw_standard_cover_title_panel(rgb, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    rgb.save(output_path, "PNG")
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
    title = metadata.get("title", "The God Game")
    author = metadata.get("author", "Barış Kısır")
    output_path = args.out.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    create_cover(title, author, output_path)


if __name__ == "__main__":
    main()