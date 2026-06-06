#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Orchid Thief of Calcutta."""

from __future__ import annotations

import argparse
import json
import math
import random
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


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Emerald green to deep violet gradient for Bengal jungle atmosphere."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((15, 50, 25), (40, 80, 50), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((40, 80, 50), (60, 30, 70), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 30, 70), (10, 5, 20), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_jungle_canopy(draw: ImageDraw, width: int, height: int) -> None:
    """Draw layered jungle foliage and vines across the top."""
    rng = random.Random(101)

    # Upper canopy - broad dark leaves
    for _ in range(30):
        x = rng.randint(-50, width + 50)
        y = rng.randint(0, int(height * 0.3))
        leaf_w = rng.randint(120, 250)
        leaf_h = rng.randint(60, 140)
        shade = rng.randint(10, 30)
        draw.ellipse([x - leaf_w // 2, y - leaf_h // 2, x + leaf_w // 2, y + leaf_h // 2],
                      fill=(shade, shade + 20, shade + 10))

    # Mid canopy
    for _ in range(20):
        x = rng.randint(-30, width + 30)
        y = rng.randint(int(height * 0.2), int(height * 0.45))
        leaf_w = rng.randint(80, 160)
        leaf_h = rng.randint(40, 90)
        shade = rng.randint(20, 40)
        draw.ellipse([x - leaf_w // 2, y - leaf_h // 2, x + leaf_w // 2, y + leaf_h // 2],
                      fill=(shade, shade + 25, shade + 15))

    # Hanging vines
    for _ in range(15):
        start_x = rng.randint(50, width - 50)
        start_y = rng.randint(0, int(height * 0.3))
        vine_len = rng.randint(100, 300)
        points = []
        for s in range(40):
            t = s / 40
            x = start_x + rng.randint(-15, 15)
            y = start_y + vine_len * t + rng.randint(-10, 10)
            points.append((x, y))
        draw.line(points, fill=(20, 35, 15), width=rng.randint(3, 6))


def draw_botanical_garden_bungalow(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a colonial bungalow with veranda, set in the jungle."""
    rng = random.Random(303)
    cx, cy = width // 2, int(height * 0.58)
    w, h = 260, 160

    # Main building
    draw.rectangle([cx - w // 2, cy - h // 2, cx + w // 2, cy + h // 2], fill=(45, 40, 35))

    # Roof - colonial style with wide overhang
    draw.polygon([
        (cx - w // 2 - 30, cy - h // 2),
        (cx, cy - h // 2 - 90),
        (cx + w // 2 + 30, cy - h // 2)
    ], fill=(55, 30, 20))

    # Veranda posts
    for px in [cx - 100, cx - 50, cx + 50, cx + 100]:
        draw.rectangle([px - 3, cy + 10, px + 3, cy + h // 2], fill=(60, 55, 50))

    # Veranda roof
    draw.polygon([
        (cx - w // 2 - 20, cy + 10),
        (cx - w // 2 - 10, cy - 15),
        (cx + w // 2 + 10, cy - 15),
        (cx + w // 2 + 20, cy + 10)
    ], fill=(50, 35, 25))

    # Windows (glowing warm light)
    for wx in [cx - 70, cx + 40]:
        draw.rectangle([wx - 20, cy - 40, wx + 15, cy - 5], fill=(255, 200, 100))
        # Cross frame
        draw.line([(wx, cy - 40), (wx, cy - 5)], fill=(40, 35, 30), width=2)
        draw.line([(wx - 20, cy - 22), (wx + 15, cy - 22)], fill=(40, 35, 30), width=2)
        # Glow
        for i in range(2):
            draw.rectangle(
                [wx - 20 - i, cy - 40 - i, wx + 15 + i, cy - 5 + i],
                outline=(255, 200, 100, 30), width=1
            )

    # Door
    draw.rectangle([cx - 12, cy - 15, cx + 12, cy + h // 2], fill=(35, 30, 25))
    draw.ellipse([cx + 6, cy + 10, cx + 10, cy + 14], fill=(200, 170, 100))

    # Chimney
    draw.rectangle([cx + 50, cy - h // 2 - 70, cx + 65, cy - h // 2 - 15], fill=(40, 30, 25))

    # Smoke wisps
    for i in range(3):
        sx = cx + 55 + rng.randint(-5, 5) if i > 0 else cx + 55
        sy = cy - h // 2 - 80 - i * 25
        r = 10 + i * 8
        draw.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(150, 150, 160, 60 - i * 15))


def draw_orchid(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the Fire Orchid as the central focal image with glowing petals."""
    cx, cy = width // 2, int(height * 0.38)

    # Stem curving up from bottom
    stem_points = []
    for s in range(30):
        t = s / 30
        x = cx + math.sin(t * 1.5) * 15
        y = cy + 120 - t * 120
        stem_points.append((x, y))
    draw.line(stem_points, fill=(10, 30, 10), width=8)

    # Dark green leaves
    draw.polygon([
        (cx - 10, cy + 40),
        (cx - 60, cy + 20),
        (cx - 10, cy + 25)
    ], fill=(15, 40, 15))
    draw.polygon([
        (cx + 10, cy + 50),
        (cx + 70, cy + 30),
        (cx + 10, cy + 35)
    ], fill=(15, 40, 15))

    # Orchid bloom - outer glow
    for g in range(8, 0, -1):
        alpha = 15 + g * 5
        draw.ellipse([
            cx - 35 - g * 4, cy - 40 - g * 4,
            cx + 35 + g * 4, cy + 40 + g * 4
        ], fill=(255, 80, 30, alpha))

    # Seven petals
    petals = [
        (0, -45, 20, 30),     # top
        (-35, -25, 25, 25),   # top-left
        (35, -25, 25, 25),    # top-right
        (-40, 5, 22, 28),     # mid-left
        (40, 5, 22, 28),      # mid-right
        (-25, 30, 20, 22),    # bottom-left
        (25, 30, 20, 22),     # bottom-right
    ]

    for px, py, pw, ph in petals:
        draw.ellipse([
            cx + px - pw // 2, cy + py - ph // 2,
            cx + px + pw // 2, cy + py + ph // 2
        ], fill=(255, 120, 40, 220))
        # Inner petal glow
        draw.ellipse([
            cx + px - pw // 4, cy + py - ph // 4,
            cx + px + pw // 4, cy + py + ph // 4
        ], fill=(255, 200, 80, 200))

    # Center of bloom
    draw.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=(180, 40, 20))
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 220, 50))


def draw_light_particles(draw: ImageDraw, width: int, height: int) -> None:
    """Draw floating ember-like light particles around the orchid."""
    rng = random.Random(42)

    for _ in range(80):
        x = rng.randint(200, width - 200)
        y = rng.randint(int(height * 0.15), int(height * 0.55))
        size = rng.randint(2, 6)
        glow_size = size * 3
        alpha = rng.randint(40, 120)

        # Warm gold / ember particles
        draw.ellipse(
            [x - glow_size, y - glow_size, x + glow_size, y + glow_size],
            fill=(255, 180, 50, alpha // 3)
        )
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(255, 200, 80, alpha)
        )


def draw_foreground_foliage(draw: ImageDraw, width: int, height: int) -> None:
    """Draw tropical foliage silhouettes at the bottom edges framing the scene."""
    rng = random.Random(202)

    # Left side foliage
    for _ in range(10):
        x = rng.randint(-30, 200)
        y = rng.randint(int(height * 0.65), height)
        leaf_w = rng.randint(60, 150)
        leaf_h = rng.randint(30, 80)
        shade = rng.randint(5, 15)
        draw.ellipse([x - leaf_w // 2, y - leaf_h, x + leaf_w // 2, y],
                      fill=(shade, shade + 10, shade + 5))

    # Right side foliage
    for _ in range(10):
        x = rng.randint(width - 200, width + 30)
        y = rng.randint(int(height * 0.65), height)
        leaf_w = rng.randint(60, 150)
        leaf_h = rng.randint(30, 80)
        shade = rng.randint(5, 15)
        draw.ellipse([x - leaf_w // 2, y - leaf_h, x + leaf_w // 2, y],
                      fill=(shade, shade + 10, shade + 5))

    # Bottom edge fern-like fronds
    for _ in range(12):
        start_x = rng.randint(0, width)
        start_y = height - rng.randint(0, 50)
        angle = rng.uniform(-0.3, 0.3)
        points = []
        for s in range(25):
            t = s / 25
            x = start_x + t * rng.randint(100, 250) * (1 if rng.random() < 0.5 else -1)
            y = start_y - t * rng.randint(80, 180) + math.sin(t * 5) * 15
            points.append((x, y))
        draw.line(points, fill=(5, 12, 5), width=rng.randint(3, 6))


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark semi-transparent panel
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        alpha = 180 + int(t * 60)
        draw.line([(0, y), (width, y)], fill=(10, 8, 15, alpha))

    # Decorative top border line
    draw.line([(100, panel_top), (width - 100, panel_top)], fill=(180, 150, 80, 120), width=2)
    # Small decorative diamond at center top of panel
    cx_mid = width // 2
    draw.polygon([
        (cx_mid, panel_top + 8),
        (cx_mid + 6, panel_top + 16),
        (cx_mid, panel_top + 24),
        (cx_mid - 6, panel_top + 16)
    ], fill=(200, 170, 80))

    # Title text - use arialbd.ttf
    title = "The Orchid Thief\nof Calcutta"
    title_font_size = 68
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        try:
            title_font = ImageFont.truetype(str(font_paths["fallback"]), title_font_size)
        except Exception:
            title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 60
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 85

    # Author name
    author = "Barış Kısır"
    author_font_size = 34
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
    ay = y_offset + 45
    draw.text((ax, ay), author, fill=(220, 200, 170), font=author_font)

    # Bottom decorative line
    draw.line([(200, height - 30), (width - 200, height - 30)], fill=(180, 150, 80, 100), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Orchid Thief of Calcutta")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (emerald to violet)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Jungle canopy and hanging vines
    draw_jungle_canopy(draw, WIDTH, HEIGHT)

    # Step 3: Colonial bungalow
    draw_botanical_garden_bungalow(draw, WIDTH, HEIGHT)

    # Step 4: The Fire Orchid (central focal point)
    draw_orchid(draw, WIDTH, HEIGHT)

    # Step 5: Floating ember light particles
    draw_light_particles(draw, WIDTH, HEIGHT)

    # Step 6: Foreground foliage
    draw_foreground_foliage(draw, WIDTH, HEIGHT)

    # Step 7: Dark title panel at bottom
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
        "fallback": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, draw, WIDTH, HEIGHT, font_paths)

    # Soften the image slightly
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