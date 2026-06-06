#!/usr/bin/env python3
"""Generate cover image for The Last Tram — 1600x2560 slipstream cover."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
except ImportError:
    raise SystemExit("Pillow required: pip install Pillow")


WIDTH, HEIGHT = 1600, 2560
BG_COLOR = (35, 25, 20)
SEPIA_LIGHT = (210, 180, 140)
SEPIA_DARK = (60, 45, 35)
YELLOW_TRAM = (220, 175, 55)
COBBLE_GRAY = (110, 105, 100)
FONT_DIR = Path("C:/Windows/Fonts")


def hex_to_rgb(h: str) -> tuple[int, ...]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def make_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a vertical sepia-to-dark gradient."""
    for y in range(height):
        ratio = y / height
        r = int(BG_COLOR[0] * (1 - ratio) + SEPIA_LIGHT[0] * ratio * 0.3)
        g = int(BG_COLOR[1] * (1 - ratio) + SEPIA_LIGHT[1] * ratio * 0.3)
        b = int(BG_COLOR[2] * (1 - ratio) + SEPIA_LIGHT[2] * ratio * 0.3)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_stars(draw: ImageDraw, width: int, height: int, count: int = 80) -> None:
    """Scatter faint star-like dots in the upper portion."""
    import random

    random.seed(42)
    for _ in range(count):
        x = random.randint(0, width)
        y = random.randint(0, height // 3)
        r = random.randint(1, 3)
        alpha = random.randint(30, 100)
        shade = 200 + random.randint(0, 55)
        draw.ellipse(
            [x - r, y - r, x + r, y + r],
            fill=(shade, shade, shade, alpha),
        )


def draw_cobblestones(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a cobblestone street receding into the distance."""
    # Street base
    street_left = width // 4
    street_right = width * 3 // 4
    # Slight perspective: converging toward center
    for y_off in range(height // 3, height - 400, 12):
        ratio = (y_off - height // 3) / (height - 400 - height // 3)
        left_x = int(street_left + (width // 2 - street_left) * ratio)
        right_x = int(street_right - (street_right - width // 2) * ratio)
        # Base line
        gray_v = int(COBBLE_GRAY[0] * (0.4 + 0.6 * (1 - ratio)))
        draw.line([(left_x, y_off), (right_x, y_off)], fill=(gray_v, gray_v - 5, gray_v - 10), width=1)
        # Cobble curves
        spacing = max(8, int(20 * (1 - ratio * 0.7)))
        for x in range(left_x, right_x, spacing):
            rx = x + int((spacing // 3) * (1 if (x // spacing) % 2 == 0 else -1))
            ry = y_off + 2
            draw.arc(
                [rx, ry - 5, rx + spacing // 2, ry + 5],
                start=0,
                end=180,
                fill=(gray_v + 15, gray_v + 10, gray_v + 5),
                width=1,
            )


def draw_tram(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a vintage Lisbon tram in silhouette with yellow highlights."""
    cx, cy = width // 2, height // 3
    # Tram body
    tram_w, tram_h = 320, 180
    x0 = cx - tram_w // 2
    y0 = cy - tram_h // 2

    # Main body (dark silhouette with sepia tint)
    body_color = (55, 45, 35)
    draw.rounded_rectangle(
        [x0, y0, x0 + tram_w, y0 + tram_h],
        radius=12,
        fill=body_color,
    )

    # Yellow stripe
    stripe_y = y0 + tram_h // 3
    draw.rectangle(
        [x0 + 10, stripe_y, x0 + tram_w - 10, stripe_y + 6],
        fill=YELLOW_TRAM,
    )
    draw.rectangle(
        [x0 + 10, stripe_y + tram_h // 3, x0 + tram_w - 10, stripe_y + tram_h // 3 + 6],
        fill=YELLOW_TRAM,
    )

    # Windows
    win_color = (180, 160, 130)
    win_w, win_h = 40, 50
    for i in range(5):
        wx = x0 + 20 + i * (win_w + 15)
        wy = y0 + 15
        # Window frame
        draw.rounded_rectangle(
            [wx, wy, wx + win_w, wy + win_h],
            radius=4,
            fill=win_color,
            outline=body_color,
            width=2,
        )
        # Warm window glow
        draw.rounded_rectangle(
            [wx + 4, wy + 4, wx + win_w - 4, wy + win_h - 4],
            radius=3,
            fill=(230, 200, 140),
        )

    # Roof
    roof_color = (45, 35, 28)
    draw.rounded_rectangle(
        [x0 + 5, y0 - 15, x0 + tram_w - 5, y0],
        radius=6,
        fill=roof_color,
    )

    # Undercarriage
    under_color = (30, 25, 20)
    draw.rectangle(
        [x0 + 30, y0 + tram_h, x0 + tram_w - 30, y0 + tram_h + 15],
        fill=under_color,
    )

    # Wheels
    for wx in [x0 + 40, x0 + tram_w - 40]:
        draw.ellipse(
            [wx - 12, y0 + tram_h + 8, wx + 12, y0 + tram_h + 32],
            fill=(35, 30, 25),
            outline=(60, 50, 40),
            width=2,
        )

    # Headlight glow
    glow_center = (x0 + tram_w + 5, y0 + tram_h // 2)
    for r in range(40, 10, -5):
        alpha = max(30, 120 - r * 3)
        draw.ellipse(
            [glow_center[0] - r, glow_center[1] - r, glow_center[0] + r, glow_center[1] + r],
            fill=(YELLOW_TRAM[0], YELLOW_TRAM[1], YELLOW_TRAM[2], alpha),
        )
    # Bright center
    draw.ellipse(
        [glow_center[0] - 8, glow_center[1] - 8, glow_center[0] + 8, glow_center[1] + 8],
        fill=(255, 230, 150),
    )

    # Overhead wire
    draw.line(
        [(x0 - 20, y0 - 30), (x0 + tram_w + 20, y0 - 30)],
        fill=(60, 55, 48),
        width=3,
    )
    # Pantograph
    draw.line(
        [(x0 + tram_w // 2 - 10, y0 - 15), (x0 + tram_w // 2, y0 - 30)],
        fill=(60, 55, 48),
        width=2,
    )


def draw_moon(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a pale moon in the upper right."""
    mx, my = width - 180, 120
    moon_r = 50
    draw.ellipse(
        [mx - moon_r, my - moon_r, mx + moon_r, my + moon_r],
        fill=(210, 200, 180),
    )
    # Soft glow
    for r in range(moon_r + 10, moon_r + 60, 10):
        draw.ellipse(
            [mx - r, my - r, mx + r, my + r],
            fill=(180, 170, 150, 15),
        )


def draw_buildings(draw: ImageDraw, width: int, height: int) -> None:
    """Draw silhouette buildings on both sides of the street."""
    # Left buildings
    for i in range(4):
        bx = 20 + i * 90
        bh = 180 + i * 30
        draw.rectangle(
            [bx, height // 3 - bh, bx + 80, height - 450],
            fill=(40 + i * 5, 35 + i * 3, 30 + i * 2),
        )
        # Windows
        for wy in range(height // 3 - bh + 20, height - 470, 35):
            draw.rectangle(
                [bx + 15, wy, bx + 30, wy + 20],
                fill=(220, 200, 160, 30),
            )
            draw.rectangle(
                [bx + 45, wy, bx + 60, wy + 20],
                fill=(220, 200, 160, 30),
            )

    # Right buildings
    for i in range(3):
        bx = width - 100 - i * 100
        bh = 200 + i * 25
        draw.rectangle(
            [bx, height // 3 - bh, bx + 90, height - 450],
            fill=(38 + i * 4, 33 + i * 3, 28 + i * 2),
        )
        for wy in range(height // 3 - bh + 20, height - 470, 35):
            draw.rectangle(
                [bx + 20, wy, bx + 35, wy + 20],
                fill=(210, 190, 150, 25),
            )
            draw.rectangle(
                [bx + 55, wy, bx + 70, wy + 20],
                fill=(210, 190, 150, 25),
            )


def draw_title_panel(
    draw: ImageDraw,
    image: Image.Image,
    width: int,
    height: int,
    title_font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
    author_font: ImageFont.FreeTypeFont | ImageFont.ImageFont,
) -> None:
    """Draw dark title panel at bottom with white text."""
    panel_top = 1920
    # Dark panel with slight gradient
    for y in range(panel_top, HEIGHT):
        ratio = (y - panel_top) / (HEIGHT - panel_top)
        r = int(20 * (1 - ratio) + 40 * ratio)
        g = int(18 * (1 - ratio) + 35 * ratio)
        b = int(15 * (1 - ratio) + 28 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Thin gold line at top of panel
    draw.line([(100, panel_top), (width - 100, panel_top)], fill=YELLOW_TRAM, width=2)

    # Title
    title = "THE LAST TRAM"
    # Try to get bbox for centering
    bbox = draw.textbbox((0, 0), title, font=title_font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = (width - tw) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Author
    author = "Barış Kısır"
    bbox_a = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox_a[2] - bbox_a[0]
    ax = (width - aw) // 2
    ay = ty + th + 80
    draw.text((ax, ay), author, fill=(YELLOW_TRAM[0], YELLOW_TRAM[1], YELLOW_TRAM[2]), font=author_font)

    # Decorative line below author
    line_y = ay + 50
    draw.line([(width // 2 - 80, line_y), (width // 2 + 80, line_y)], fill=YELLOW_TRAM, width=1)



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
    parser = argparse.ArgumentParser(description="Generate cover for The Last Tram")
    parser.add_argument("--metadata", required=True, type=Path, help="Path to metadata JSON")
    parser.add_argument("--out", type=Path, default=None, help="Output PNG path")
    args = parser.parse_args()

    metadata_path = Path(args.metadata)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    out_path = Path(args.out) if args.out else Path(metadata["cover_path"])

    # Load fonts
    title_font_path = FONT_DIR / "arialbd.ttf"
    author_font_path = FONT_DIR / "arial.ttf"

    try:
        title_font = ImageFont.truetype(str(title_font_path), 72)
        author_font = ImageFont.truetype(str(author_font_path), 36)
    except (IOError, OSError):
        print("Warning: arialbd.ttf not found, using default font")
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Create image
    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image)

    # Build cover layers
    make_gradient(draw, WIDTH, HEIGHT)
    draw_stars(draw, WIDTH, HEIGHT)
    draw_moon(draw, WIDTH, HEIGHT)
    draw_buildings(draw, WIDTH, HEIGHT)
    draw_cobblestones(draw, WIDTH, HEIGHT)
    draw_tram(draw, WIDTH, HEIGHT)
    draw_title_panel(draw, image, WIDTH, HEIGHT, title_font, author_font)

    # Soft haze overlay for slipstream feel
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (180, 160, 130, 20))
    image = Image.alpha_composite(image, overlay)

    # Slight vignette
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    for r in range(max(WIDTH, HEIGHT) // 2, 0, -20):
        alpha = max(0, 60 - r // 6)
        v_draw.ellipse(
            [WIDTH // 2 - r, HEIGHT // 2 - r, WIDTH // 2 + r, HEIGHT // 2 + r],
            outline=(0, 0, 0, alpha),
            width=20,
        )
    image = Image.alpha_composite(image, vignette)

    # Convert to RGB for saving as PNG
    final = image.convert("RGB")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(final, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    final.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")

    # Verify
    img = Image.open(out_path)
    print(f"Dimensions: {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()