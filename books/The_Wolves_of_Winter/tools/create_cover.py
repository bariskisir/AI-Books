#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Wolves of Winter."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_sky_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Deep arctic night gradient: dark blue to pale ice blue."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((5, 10, 30), ((15, 20, 60)), t)
        elif y < height * 0.7:
            t = (y - height * 0.3) / (height * 0.4)
            c = lerp_color((15, 20, 60), ((60, 90, 120)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 90, 120), ((120, 150, 180)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_aurora(draw: ImageDraw, width: int, height: int) -> None:
    """Draw aurora borealis bands across the sky."""
    import random

    rng = random.Random(13)

    for band in range(4):
        base_y = rng.randint(200, 600)
        base_x = rng.randint(-200, width + 200)
        band_height = rng.randint(60, 150)
        band_width = rng.randint(400, 800)

        # Aurora color: green-blue with transparency
        if band < 2:
            color = (80, 255, 180, 60)
            inner = (120, 255, 200, 80)
        else:
            color = (40, 180, 255, 50)
            inner = (60, 200, 255, 70)

        # Draw undulating aurora
        points = []
        steps = 40
        for s in range(steps + 1):
            t = s / steps
            x = base_x + band_width * t + rng.randint(-30, 30)
            y = base_y + math.sin(t * math.pi * 4) * band_height * 0.3 + rng.randint(-10, 10)
            points.append((x, y))

        # Upper edge
        for s in range(steps + 1):
            t = s / steps
            x = base_x + band_width * t + rng.randint(-30, 30)
            y = base_y + math.sin(t * math.pi * 4) * band_height * 0.3 + rng.randint(-10, 10) - band_height
            points.append((x, y))

        if len(points) > 2:
            draw.polygon(points, fill=color)

        # Brighter inner band
        inner_points = []
        for s in range(steps + 1):
            t = s / steps
            x = base_x + band_width * t + rng.randint(-20, 20)
            y = base_y + math.sin(t * math.pi * 4) * band_height * 0.2 + rng.randint(-5, 5)
            inner_points.append((x, y))
        for s in range(steps + 1):
            t = s / steps
            x = base_x + band_width * t + rng.randint(-20, 20)
            y = base_y + math.sin(t * math.pi * 4) * band_height * 0.2 + rng.randint(-5, 5) - band_height // 2
            inner_points.append((x, y))

        if len(inner_points) > 2:
            draw.polygon(inner_points, fill=inner)


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered stars in the upper portion of the sky."""
    import random

    rng = random.Random(42)
    for _ in range(200):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.5))
        size = rng.randint(1, 3)
        brightness = rng.randint(150, 255)
        draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness, 200))


def draw_frozen_plain(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the frozen plain with ridges and snow-covered ground."""
    import random

    rng = random.Random(8)

    # Snow-covered ground - lower portion
    ground_top = int(height * 0.65)

    # Wide snow plain
    draw.rectangle([(0, ground_top), (width, height)], fill=(200, 210, 220))

    # Snow ridges
    for ridge in range(6):
        ry = ground_top + rng.randint(0, int(height * 0.15))
        rx = rng.randint(-100, width + 100)
        rw = rng.randint(200, 600)
        rh = rng.randint(20, 60)

        shade = rng.randint(180, 210)
        draw.ellipse(
            [rx - rw // 2, ry - rh // 2, rx + rw // 2, ry + rh // 2],
            fill=(shade, shade + 10, shade + 20),
        )

    # Distant mountain shapes
    for m in range(3):
        mx = width // 4 + m * width // 4 + rng.randint(-80, 80)
        my = ground_top - rng.randint(40, 120)
        mw = rng.randint(150, 300)
        mh = rng.randint(100, 250)

        # Mountain triangle
        draw.polygon(
            [(mx - mw // 2, ground_top), (mx, my), (mx + mw // 2, ground_top)],
            fill=(180, 195, 210),
        )
        # Snow cap
        draw.polygon(
            [(mx - mw // 6, my + mh * 0.3), (mx, my), (mx + mw // 6, my + mh * 0.3)],
            fill=(220, 230, 240),
        )


def draw_wolf_pack(draw: ImageDraw, width: int, height: int) -> None:
    """Draw wolf silhouettes on a ridge."""
    import random

    rng = random.Random(5)

    # Ridge line
    ridge_y = int(height * 0.68)

    # Draw 5 wolf silhouettes
    wolf_positions = [
        (width // 2 - 160, ridge_y, 0.4),
        (width // 2 - 80, ridge_y - 5, 0.5),
        (width // 2, ridge_y - 8, 0.55),
        (width // 2 + 90, ridge_y - 3, 0.45),
        (width // 2 + 180, ridge_y, 0.35),
    ]

    for wx, wy, scale in wolf_positions:
        # Wolf body silhouette
        body_len = int(80 * scale)
        body_h = int(25 * scale)
        # Body
        draw.ellipse(
            [wx - body_len // 2, wy - body_h // 2, wx + body_len // 2, wy + body_h // 2],
            fill=(25, 25, 35),
        )
        # Head
        head_x = wx + int(body_len * 0.35)
        head_y = wy - int(body_h * 0.3)
        draw.ellipse(
            [head_x - int(15 * scale), head_y - int(12 * scale), head_x + int(15 * scale), head_y + int(12 * scale)],
            fill=(20, 20, 30),
        )
        # Snout
        draw.polygon(
            [
                (head_x, head_y - int(5 * scale)),
                (head_x + int(20 * scale), head_y - int(2 * scale)),
                (head_x + int(20 * scale), head_y + int(5 * scale)),
                (head_x, head_y + int(5 * scale)),
            ],
            fill=(20, 20, 30),
        )
        # Ears
        draw.polygon(
            [
                (head_x - int(5 * scale), head_y - int(10 * scale)),
                (head_x, head_y - int(20 * scale)),
                (head_x + int(8 * scale), head_y - int(10 * scale)),
            ],
            fill=(20, 20, 30),
        )
        # Tail
        tail_x = wx - int(body_len * 0.4)
        tail_y = wy - int(body_h * 0.1)
        draw.line(
            [tail_x, tail_y, tail_x - int(30 * scale), tail_y - int(15 * scale)],
            fill=(20, 20, 30),
            width=max(1, int(5 * scale)),
        )
        # Legs
        for leg_offset in [-int(20 * scale), int(20 * scale)]:
            draw.line(
                [wx + leg_offset, wy, wx + leg_offset + int(3 * scale), wy + int(30 * scale)],
                fill=(20, 20, 30),
                width=max(1, int(6 * scale)),
            )


def draw_snow_texture(draw: ImageDraw, width: int, height: int) -> None:
    """Add subtle snow flurries to the scene."""
    import random

    rng = random.Random(21)
    for _ in range(150):
        x = rng.randint(0, width)
        y = rng.randint(0, height)
        size = rng.randint(1, 3)
        brightness = rng.randint(200, 255)
        alpha = rng.randint(100, 200)
        draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness, brightness, alpha))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark semi-transparent panel background
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        alpha = int(180 + 75 * t)
        draw.line([(0, y), (width, y)], fill=(10, 12, 20, alpha))

    # Subtle border line at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 120, 160), width=2)

    # Title
    title = "The Wolves of\nWinter"
    title_font_size = 76
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
    lines = title.split("\n")
    y_offset = panel_top + 100
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 95

    # Author
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = y_offset + 50
    draw.text((ax, ay), author, fill=(200, 210, 230), font=author_font)

    # Subtitle line - genre tag
    genre_text = "A Prehistoric Survival Novel"
    genre_font_size = 22
    try:
        genre_font = ImageFont.truetype(str(font_paths["small"]), genre_font_size)
    except Exception:
        genre_font = ImageFont.load_default()

    try:
        gbbox = draw.textbbox((0, 0), genre_text, font=genre_font)
        gw = gbbox[2] - gbbox[0]
    except Exception:
        gw = 0
    gx = (width - gw) // 2
    gy = ay + 55
    draw.text((gx, gy), genre_text, fill=(160, 180, 200), font=genre_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Wolves of Winter")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Sky gradient background
    draw_sky_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Stars
    draw_stars(draw, WIDTH, HEIGHT)

    # Step 3: Aurora borealis
    draw_aurora(draw, WIDTH, HEIGHT)

    # Step 4: Frozen plain with mountains
    draw_frozen_plain(draw, WIDTH, HEIGHT)

    # Step 5: Wolf pack silhouettes on ridge
    draw_wolf_pack(draw, WIDTH, HEIGHT)

    # Step 6: Snow flurries
    draw_snow_texture(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
    img = img.filter(ImageFilter.SMOOTH)

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

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()