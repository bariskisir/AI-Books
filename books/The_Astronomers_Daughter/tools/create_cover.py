#!/usr/bin/env python3
"""Generate a book cover using PIL for The Astronomer's Daughter."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Pillow is required. Install with: pip install Pillow")


WIDTH, HEIGHT = 1600, 2560
FONT_DIR = Path("C:/Windows/Fonts")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return tuple(int(h[i : i + 2], 16) for i in (0, 2, 4))


def star_points(cx: float, cy: float, outer: float, inner: float, n: int = 5) -> list[tuple[float, float]]:
    pts = []
    for i in range(n * 2):
        angle = -90 + i * (360 / (n * 2))
        r = outer if i % 2 == 0 else inner
        import math
        pts.append((cx + r * math.cos(math.radians(angle)), cy + r * math.sin(math.radians(angle))))
    return pts


def create_cover(metadata_path: Path, output_path: Path) -> None:
    with open(metadata_path, encoding="utf-8") as f:
        meta = json.load(f)

    title = meta["title"]
    author = meta["author"]

    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Deep navy-to-charcoal gradient background
    navy = hex_to_rgb("0a1628")  # Deep night
    star_gold = hex_to_rgb("d4af37")  # Star gold accent
    dark_panel = hex_to_rgb("0a0d14")  # Very dark for bottom panel

    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(navy[0] * (1 - ratio) + 15 * ratio)
        g = int(navy[1] * (1 - ratio) + 18 * ratio)
        b = int(navy[2] * (1 - ratio) + 30 * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Star chart circles
    import math
    cx, cy = WIDTH // 2, HEIGHT // 2 - 120
    for r in [300, 450, 600]:
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(100, 110, 130, 80), width=1)

    # Grid lines (declination/right-ascension)
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x2 = cx + 700 * math.cos(rad)
        y2 = cy + 700 * math.sin(rad)
        draw.line([(cx, cy), (x2, y2)], fill=(60, 70, 90, 60), width=1)

    # Observatory dome silhouette
    dome_cx, dome_cy = cx, cy + 80
    dome_r = 180
    draw.arc([dome_cx - dome_r, dome_cy - dome_r, dome_cx + dome_r, dome_cy + dome_r], 0, 180, fill=(180, 185, 195), width=3)
    draw.rectangle([dome_cx - dome_r, dome_cy, dome_cx + dome_r, dome_cy + 60], fill=(180, 185, 195))
    # Slit in dome
    draw.rectangle([dome_cx - 6, dome_cy - dome_r + 20, dome_cx + 6, dome_cy], fill=(10, 15, 30))

    # Telescope silhouette
    telescope_x = dome_cx + 280
    telescope_y = dome_cy - 40
    draw.line([(telescope_x, telescope_y), (telescope_x + 120, telescope_y - 200)], fill=(200, 205, 215), width=6)
    draw.line([(telescope_x + 120, telescope_y - 200), (telescope_x + 135, telescope_y - 220)], fill=(200, 205, 215), width=8)
    # Tripod
    draw.line([(telescope_x, telescope_y), (telescope_x - 30, telescope_y + 80)], fill=(160, 165, 175), width=3)
    draw.line([(telescope_x, telescope_y), (telescope_x + 30, telescope_y + 80)], fill=(160, 165, 175), width=3)
    draw.line([(telescope_x - 30, telescope_y + 80), (telescope_x + 30, telescope_y + 80)], fill=(160, 165, 175), width=3)

    # Stars scattered across sky
    import random
    random.seed(42)
    for _ in range(200):
        sx = random.randint(0, WIDTH)
        sy = random.randint(0, HEIGHT // 2 + 200)
        size = random.randint(1, 3)
        brightness = random.randint(160, 255)
        draw.ellipse([sx, sy, sx + size, sy + size], fill=(brightness, brightness, int(brightness * 0.9)))

    # Bright stars with cross
    bright_stars = [(200, 180), (400, 100), (1200, 250), (1400, 150), (100, 500), (1500, 400)]
    for sx, sy in bright_stars:
        draw.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 245, 220))
        for arm in range(4):
            rad = math.radians(arm * 45)
            dx = 8 * math.cos(rad)
            dy = 8 * math.sin(rad)
            draw.line([(sx - dx, sy - dy), (sx + dx, sy + dy)], fill=(255, 245, 220, 120), width=1)

    # Comet with tail
    comet_x, comet_y = 1100, 350
    draw.ellipse([comet_x - 6, comet_y - 6, comet_x + 6, comet_y + 6], fill=(255, 240, 200))
    # Tail
    tail_points = []
    for t in range(60):
        tx = comet_x - t * 18 + random.randint(-4, 4)
        ty = comet_y - t * 5 + random.randint(-8, 8)
        tw = max(1, 20 - t // 3)
        alpha = max(10, 180 - t * 3)
        draw.ellipse([tx - tw, ty - tw // 2, tx + tw, ty + tw // 2], fill=(255, 235, 180, alpha))
    draw.ellipse([comet_x - 8, comet_y - 8, comet_x + 8, comet_y + 8], fill=(255, 250, 230))

    # Additional constellation lines
    const_stars = [(300, 400), (450, 350), (550, 420), (480, 500), (350, 480)]
    for i in range(len(const_stars) - 1):
        draw.line([const_stars[i], const_stars[i + 1]], fill=(120, 130, 160, 100), width=1)
    for sx, sy in const_stars:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(200, 210, 240))

    # Dark bottom panel for title
    draw.rectangle([(0, 1880), (WIDTH, 2240)], fill=dark_panel)
    # Gold accent line above panel
    draw.rectangle([(200, 1876), (WIDTH - 200, 1880)], fill=star_gold)

    # Title text
    title_font_path = FONT_DIR / "arialbd.ttf"
    try:
        title_font = ImageFont.truetype(str(title_font_path), 84)
    except (IOError, OSError):
        title_font = ImageFont.load_default()

    author_font_path = FONT_DIR / "ariali.ttf"
    try:
        author_font = ImageFont.truetype(str(author_font_path), 44)
    except (IOError, OSError):
        author_font = ImageFont.load_default()

    # Draw title centered in panel
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = title_bbox[2] - title_bbox[0]
    title_x = (WIDTH - title_w) // 2
    draw.text((title_x, 1920), title, fill=(255, 255, 255), font=title_font)

    # Author below title
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_w = author_bbox[2] - author_bbox[0]
    author_x = (WIDTH - author_w) // 2
    draw.text((author_x, 2040), author, fill=(212, 175, 55), font=author_font)

    # Gold accent line below author area
    draw.rectangle([(400, 2160), (WIDTH - 400, 2164)], fill=star_gold)

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
    parser = argparse.ArgumentParser(description="Generate book cover")
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()