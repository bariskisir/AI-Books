#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Piano Tuner."""

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
    """Deep charcoal grey to foggy amber for Edinburgh Victorian atmosphere."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((15, 15, 20), (45, 35, 30), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((45, 35, 30), (80, 65, 50), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((80, 65, 50), (55, 45, 35), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_fog(draw: ImageDraw, width: int, height: int) -> None:
    """Draw layered fog bands across the cover."""
    rng = random.Random(17)
    for _ in range(30):
        y = rng.randint(200, int(height * 0.8))
        x = rng.randint(-100, width + 100)
        fog_w = rng.randint(300, 800)
        fog_h = rng.randint(40, 120)
        alpha = rng.randint(15, 40)
        draw.ellipse(
            [x, y, x + fog_w, y + fog_h],
            fill=(180, 175, 160, alpha),
        )


def draw_gas_lamp(draw: ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    """Draw a Victorian gas lamp with glow."""
    # Post
    post_w = int(6 * scale)
    post_h = int(180 * scale)
    draw.rectangle([x - post_w // 2, y - post_h, x + post_w // 2, y], fill=(30, 25, 20))

    # Lamp housing
    housing_w = int(30 * scale)
    housing_h = int(40 * scale)
    draw.rectangle(
        [x - housing_w // 2, y - post_h - housing_h, x + housing_w // 2, y - post_h],
        fill=(40, 35, 30),
    )

    # Glass glow
    glow_center = (x, y - post_h - housing_h // 2)
    for radius in range(60, 10, -10):
        alpha = max(0, 120 - radius * 2)
        draw.ellipse(
            [
                glow_center[0] - int(radius * scale),
                glow_center[1] - int(radius * scale),
                glow_center[0] + int(radius * scale),
                glow_center[1] + int(radius * scale),
            ],
            fill=(255, 200, 100, alpha),
        )

    # Inner light
    draw.rectangle(
        [x - int(12 * scale), y - post_h - housing_h + int(8 * scale),
         x + int(12 * scale), y - post_h - int(8 * scale)],
        fill=(255, 230, 150, 200),
    )


def draw_parlor_window(draw: ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    """Draw a tall Georgian window with warm interior light."""
    w = int(140 * scale)
    h = int(220 * scale)

    # Window frame
    draw.rectangle([x - w // 2, y - h, x + w // 2, y], fill=(200, 180, 150, 60))

    # Warm interior glow
    draw.rectangle([x - w // 2 + int(8 * scale), y - h + int(8 * scale),
                     x + w // 2 - int(8 * scale), y - int(8 * scale)],
                    fill=(255, 210, 120, 100))

    # Mullions (window cross-bars)
    # Horizontal
    draw.rectangle([x - w // 2, y - h // 2 - int(2 * scale),
                     x + w // 2, y - h // 2 + int(2 * scale)],
                    fill=(40, 35, 30))
    # Vertical
    draw.rectangle([x - int(2 * scale), y - h,
                     x + int(2 * scale), y],
                    fill=(40, 35, 30))

    # Window frame outline
    draw.rectangle([x - w // 2, y - h, x + w // 2, y], outline=(30, 25, 20), width=int(3 * scale))


def draw_grand_piano(draw: ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    """Draw a silhouette of a grand piano."""
    # Piano body (top view angled)
    body_w = int(240 * scale)
    body_h = int(160 * scale)

    # Main body
    draw.ellipse(
        [x - body_w // 2, y - body_h // 2, x + body_w // 2, y + body_h // 2],
        fill=(10, 8, 6),
    )

    # Lid prop
    lid_x = x + int(80 * scale)
    lid_y = y - int(60 * scale)
    draw.polygon(
        [(x, y - body_h // 2), (lid_x, lid_y), (x + body_w // 2, y)],
        fill=(15, 12, 10),
    )

    # Keyboard
    kb_w = int(100 * scale)
    kb_h = int(20 * scale)
    draw.rectangle(
        [x - kb_w // 2, y + body_h // 2 - kb_h, x + kb_w // 2, y + body_h // 2],
        fill=(200, 195, 185),
    )

    # Keys (white keys as lines)
    for i in range(14):
        kx = x - kb_w // 2 + int(i * kb_w / 14)
        draw.line([(kx, y + body_h // 2 - kb_h), (kx, y + body_h // 2)],
                  fill=(180, 175, 165), width=1)

    # Legs
    draw.line([(x - body_w // 3, y + body_h // 2), (x - body_w // 3, y + body_h // 2 + int(60 * scale))],
              fill=(10, 8, 6), width=int(6 * scale))
    draw.line([(x + body_w // 3, y + body_h // 2), (x + body_w // 3, y + body_h // 2 + int(60 * scale))],
              fill=(10, 8, 6), width=int(6 * scale))


def draw_edinburgh_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouette of Edinburgh rooflines and spires."""
    rng = random.Random(5)

    # Row of townhouse rooflines
    base_y = int(height * 0.45)
    x = 0
    while x < width:
        h = rng.randint(60, 150)
        w = rng.randint(80, 200)
        # Roof shape
        draw.polygon(
            [(x, base_y), (x + w // 2, base_y - h), (x + w, base_y)],
            fill=(8, 8, 10),
        )
        # Chimneys
        for _ in range(rng.randint(1, 3)):
            cx = x + rng.randint(10, w - 10)
            ch = rng.randint(20, 50)
            draw.rectangle([cx, base_y - h, cx + 8, base_y - h + ch], fill=(12, 10, 8))
        x += w - rng.randint(10, 30)

    # Castle silhouette / spire
    spire_x = width // 2 + 100
    spire_base = base_y
    # Tower
    draw.rectangle([spire_x - 30, spire_base - 200, spire_x + 30, spire_base], fill=(8, 8, 10))
    # Spire
    draw.polygon(
        [(spire_x - 20, spire_base - 200), (spire_x, spire_base - 280), (spire_x + 20, spire_base - 200)],
        fill=(8, 8, 10),
    )
    # Battlements
    for bx in range(spire_x - 30, spire_x + 35, 10):
        draw.rectangle([bx, spire_base - 200, bx + 6, spire_base - 190], fill=(8, 8, 10))


def draw_music_notes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw faint floating music note symbols."""
    rng = random.Random(13)
    for _ in range(25):
        x = rng.randint(100, width - 100)
        y = rng.randint(int(height * 0.15), int(height * 0.5))
        size = rng.randint(8, 20)
        alpha = rng.randint(20, 60)

        # Simple note shape: oval + stem
        # Oval head
        draw.ellipse(
            [x - size // 2, y - size // 4, x + size // 2, y + size // 4],
            fill=(200, 190, 170, alpha),
        )
        # Stem
        draw.line(
            [(x + size // 2, y), (x + size // 2, y - size)],
            fill=(200, 190, 170, alpha),
            width=max(1, size // 6),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 12, 10, 220))

    # Subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 70, 55), width=2)

    # Title text using arialbd.ttf (available font)
    title = "The Piano\nTuner"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered - WHITE text for readability on dark panel
    lines = title.split("\n")
    y_offset = panel_top + 80
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 95

    # Author name
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
    ay = y_offset + 30
    draw.text((ax, ay), author, fill=(200, 195, 185), font=author_font)

    # Add a line below author
    line_y = ay + 45
    draw.line(
        [(width // 2 - 60, line_y), (width // 2 + 60, line_y)],
        fill=(100, 90, 75), width=1,
    )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Piano Tuner")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Edinburgh skyline silhouette
    draw_edinburgh_skyline(draw, WIDTH, HEIGHT)

    # Step 3: Fog layers
    draw_fog(draw, WIDTH, HEIGHT)

    # Step 4: Windows with warm light
    draw_parlor_window(draw, WIDTH // 2 - 200, int(HEIGHT * 0.52), scale=1.1)
    draw_parlor_window(draw, WIDTH // 2 + 180, int(HEIGHT * 0.55), scale=0.9)

    # Step 5: Grand piano silhouette
    draw_grand_piano(draw, WIDTH // 2, int(HEIGHT * 0.48), scale=1.2)

    # Step 6: Gas lamps
    draw_gas_lamp(draw, int(WIDTH * 0.15), int(HEIGHT * 0.42), scale=1.0)
    draw_gas_lamp(draw, int(WIDTH * 0.85), int(HEIGHT * 0.42), scale=1.0)

    # Step 7: Floating music notes
    draw_music_notes(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

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