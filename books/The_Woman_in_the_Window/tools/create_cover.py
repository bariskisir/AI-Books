#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Woman in the Window."""

from __future__ import annotations

import argparse
import json
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
    """Deep night blue to dark indigo gradient for the neon-noir feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((5, 5, 30), ((10, 10, 50)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((10, 10, 50), ((20, 15, 60)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((20, 15, 60), ((5, 5, 20)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_city_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark city skyline silhouette across the middle."""
    rng = random.Random(17)
    buildings = []
    x = 0
    while x < width:
        bw = rng.randint(40, 120)
        bh = rng.randint(80, 250)
        bx = x
        by = int(height * 0.65) - bh
        buildings.append((bx, by, bw, bh))
        # Windows on each building
        for wy in range(by + 15, int(height * 0.65) - 10, 20):
            for wx in range(bx + 8, bx + bw - 8, 18):
                if rng.random() < 0.35:
                    win_color = (255, 220, 100, 80) if rng.random() < 0.6 else (200, 150, 50, 60)
                    draw.rectangle([wx, wy, wx + 6, wy + 10], fill=win_color)
        x += bw + rng.randint(5, 20)
    for bx, by, bw, bh in buildings:
        draw.rectangle([bx, by, bx + bw, int(height * 0.65)], fill=(8, 8, 25))
        # Subtle outline
        draw.rectangle([bx, by, bx + bw, int(height * 0.65)], outline=(15, 15, 40), width=1)


def draw_apartment_window(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the focal apartment window with a woman silhouette."""
    cx, cy = width // 2, int(height * 0.38)
    ww, wh = 320, 420

    # Window frame
    draw.rectangle([cx - ww // 2, cy - wh // 2, cx + ww // 2, cy + wh // 2], fill=(20, 15, 50))
    draw.rectangle([cx - ww // 2 - 8, cy - wh // 2 - 8, cx + ww // 2 + 8, cy + wh // 2 + 8], fill=(30, 25, 40))

    # Interior glow
    inner_color = (40, 35, 60, 200)
    draw.rectangle([cx - ww // 2 + 4, cy - wh // 2 + 4, cx + ww // 2 - 4, cy + wh // 2 - 4], fill=inner_color)

    # Warm lamp glow through window
    glow_center = (cx + 60, cy + 40)
    for r in range(100, 10, -10):
        alpha = max(5, 40 - r // 3)
        draw.ellipse(
            [glow_center[0] - r, glow_center[1] - r, glow_center[0] + r, glow_center[1] + r],
            fill=(255, 200, 100, alpha),
        )

    # Window cross-frames (mullions)
    draw.line(
        [cx - ww // 2 + 4, cy, cx + ww // 2 - 4, cy], fill=(25, 20, 50), width=4
    )
    draw.line(
        [cx, cy - wh // 2 + 4, cx, cy + wh // 2 - 4], fill=(25, 20, 50), width=4
    )

    # Woman silhouette in the window
    # Body
    wx, wy = cx + 20, cy + 40
    draw.polygon(
        [
            (wx - 15, wy + 100),  # bottom left of dress
            (wx + 15, wy + 100),  # bottom right of dress
            (wx + 12, wy + 30),   # waist right
            (wx + 8, wy),         # shoulder right
            (wx + 5, wy - 40),   # head top right
            (wx - 5, wy - 40),   # head top left
            (wx - 8, wy),        # shoulder left
            (wx - 12, wy + 30),  # waist left
        ],
        fill=(180, 30, 30, 220),
    )
    # Head
    draw.ellipse([wx - 8, wy - 55, wx + 8, wy - 35], fill=(180, 30, 30, 220))
    # Arm raised (pressing against glass)
    draw.line([(wx - 8, wy + 5), (wx - 40, wy - 20)], fill=(180, 30, 30, 220), width=6)

    # Window glass reflection
    for i in range(3):
        rx = cx - ww // 2 + 10 + i * 100
        draw.line(
            [(rx, cy - wh // 2 + 10), (rx + 20, cy - wh // 2 + 40)],
            fill=(100, 100, 180, 20),
            width=2,
        )


def draw_neon_signs(draw: ImageDraw, width: int, height: int) -> None:
    """Draw neon signs and reflections in the cityscape."""
    rng = random.Random(42)
    neon_colors = [
        (255, 50, 100, 180),   # hot pink
        (50, 200, 255, 180),   # cyan
        (255, 200, 50, 180),   # amber
        (200, 50, 255, 180),   # purple
    ]

    # Scattered neon signs on buildings
    for _ in range(12):
        x = rng.randint(30, width - 30)
        y = rng.randint(int(height * 0.45), int(height * 0.60))
        color = rng.choice(neon_colors)
        sw = rng.randint(30, 80)
        sh = rng.randint(8, 16)

        # Glow
        for g in range(3):
            draw.rectangle(
                [x - g * 2, y - g * 2, x + sw + g * 2, y + sh + g * 2],
                outline=(color[0], color[1], color[2], color[3] // (g + 2)),
                width=1,
            )
        # Sign
        draw.rectangle([x, y, x + sw, y + sh], fill=color)

    # Street-level neon glow
    for _ in range(6):
        x = rng.randint(50, width - 50)
        y = int(height * 0.72)
        color = rng.choice(neon_colors)
        for r in range(30, 5, -5):
            draw.ellipse(
                [x - r, y - r, x + r, y + r],
                fill=(color[0], color[1], color[2], 10),
            )


def draw_camera_lens(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a camera lens in the lower portion of the image as a visual motif."""
    cx, cy = width // 2 - 200, int(height * 0.55)
    radius = 50

    # Outer ring
    for r in range(radius, radius - 8, -1):
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(40, 40, 50))
    # Inner ring
    draw.ellipse([cx - radius + 8, cy - radius + 8, cx + radius - 8, cy + radius - 8], fill=(15, 15, 25))
    # Glass
    draw.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(60, 60, 100, 200))
    # Reflection on glass
    draw.ellipse([cx - 12, cy - 12, cx + 5, cy + 5], fill=(150, 150, 200, 60))


def draw_street(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a wet street with reflections at the bottom."""
    street_top = int(height * 0.68)
    # Street surface
    draw.rectangle([(0, street_top), (width, height)], fill=(10, 8, 18))

    # Horizontal lane lines
    for lx in range(50, width, 200):
        draw.rectangle([lx, street_top + 30, lx + 80, street_top + 34], fill=(80, 80, 90))

    # Wet reflection of window light
    for _ in range(40):
        rx = random.randint(0, width)
        ry = random.randint(street_top, height)
        rw = random.randint(10, 60)
        rh = 2
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(30, 25, 60, 60))

    # Neon reflections on wet street
    for _ in range(15):
        rx = random.randint(0, width)
        ry = random.randint(street_top + 20, height - 20)
        rw = random.randint(5, 30)
        color = random.choice([
            (255, 50, 100, 40),
            (50, 200, 255, 40),
            (255, 200, 50, 40),
        ])
        draw.rectangle([rx, ry, rx + rw, ry + 3], fill=color)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark
    draw.rectangle([(0, panel_top), (width, height)], fill=(5, 5, 20))

    # Subtle border at top
    draw.line([(0, panel_top), (width, panel_top)], fill=(255, 50, 100, 100), width=2)

    # Title text
    title = "The Woman in\nthe Window"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered - WHITE text
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

    # Author name - WHITE
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
    ay = y_offset + 40
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Woman in the Window")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Night gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: City skyline
    draw_city_skyline(draw, WIDTH, HEIGHT)

    # Step 3: Wet street with reflections
    draw_street(draw, WIDTH, HEIGHT)

    # Step 4: Neon signs
    draw_neon_signs(draw, WIDTH, HEIGHT)

    # Step 5: The apartment window with woman silhouette
    draw_apartment_window(draw, WIDTH, HEIGHT)

    # Step 6: Camera lens element
    draw_camera_lens(draw, WIDTH, HEIGHT)

    # Step 7: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
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