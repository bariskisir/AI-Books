#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Kitchen Witch."""

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


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Warm amber-to-sage gradient for cozy bakery feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((80, 50, 30), ((160, 120, 60)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((160, 120, 60), ((100, 130, 80)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((100, 130, 80), ((60, 80, 50)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_village_square(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small village square with cobblestones and buildings."""
    # Ground / cobblestones
    for i in range(20):
        cx = 100 + i * 75 + (i % 3) * 10
        cy = int(height * 0.58) + (i % 4) * 8
        r = 8 + (i % 3) * 2
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 100, 80, 150))
        draw.ellipse([cx - r // 2, cy - r // 2, cx + r // 2, cy + r // 2], fill=(100, 85, 65, 100))

    # Left building
    # Wall
    draw.rectangle([50, int(height * 0.35), 300, int(height * 0.58)], fill=(140, 110, 85))
    # Roof
    draw.polygon([(30, int(height * 0.35)), (175, int(height * 0.22)), (320, int(height * 0.35))], fill=(90, 60, 40))
    # Windows
    draw.rectangle([90, int(height * 0.40), 140, int(height * 0.48)], fill=(255, 200, 100, 200))
    draw.rectangle([200, int(height * 0.40), 250, int(height * 0.48)], fill=(255, 200, 100, 200))
    # Window glow
    for wx, wy in [(90, int(height * 0.40)), (200, int(height * 0.40))]:
        draw.rectangle([wx - 2, wy - 2, wx + 50, wy + 60], outline=(255, 220, 150, 80), width=2)

    # Right building
    draw.rectangle([width - 320, int(height * 0.38), width - 50, int(height * 0.58)], fill=(130, 100, 80))
    draw.polygon([(width - 340, int(height * 0.38)), (width - 185, int(height * 0.25)), (width - 30, int(height * 0.38))], fill=(80, 55, 35))
    # Window with warm light
    draw.rectangle([width - 250, int(height * 0.42), width - 200, int(height * 0.50)], fill=(255, 210, 120, 200))
    draw.rectangle([width - 160, int(height * 0.42), width - 110, int(height * 0.50)], fill=(255, 210, 120, 200))

    # Center fountain
    fx, fy = width // 2, int(height * 0.52)
    draw.ellipse([fx - 40, fy - 15, fx + 40, fy + 15], fill=(150, 140, 130))
    draw.ellipse([fx - 30, fy - 25, fx + 30, fy - 10], fill=(170, 200, 220, 180))
    draw.rectangle([fx - 4, fy - 35, fx + 4, fy - 25], fill=(140, 130, 120))
    draw.ellipse([fx - 8, fy - 40, fx + 8, fy - 32], fill=(160, 150, 140))


def draw_bakery_shop(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the central bakery with warm glowing windows."""
    cx, cy = width // 2, int(height * 0.50)

    # Shop front
    shop_w, shop_h = 260, 300
    sx, sy = cx - shop_w // 2, cy - shop_h // 2

    # Wall
    draw.rectangle([sx, sy, sx + shop_w, sy + shop_h], fill=(160, 120, 80))

    # Door
    draw.rectangle([cx - 25, sy + shop_h - 140, cx + 25, sy + shop_h], fill=(80, 55, 35))
    draw.ellipse([cx + 15, sy + shop_h - 70, cx + 20, sy + shop_h - 65], fill=(255, 200, 100))

    # Large display window
    draw.rectangle([sx + 20, sy + 30, sx + shop_w - 20, sy + 160], fill=(255, 220, 130, 220))
    # Window frame
    draw.rectangle([sx + 20, sy + 30, sx + shop_w - 20, sy + 160], outline=(100, 75, 50), width=3)
    draw.line([cx, sy + 30, cx, sy + 160], fill=(100, 75, 50), width=2)

    # Signboard above door
    sign_y = sy - 15
    draw.rectangle([cx - 70, sign_y - 20, cx + 70, sign_y + 5], fill=(60, 40, 25))
    draw.rectangle([cx - 70, sign_y - 20, cx + 70, sign_y + 5], outline=(200, 180, 140), width=1)

    # Awning
    for aw_x in range(sx, sx + shop_w, 30):
        draw.polygon(
            [(aw_x, sy - 5), (aw_x + 25, sy - 5), (aw_x + 12, sy - 30), (aw_x - 5, sy - 25)],
            fill=(140, 50, 40, 180),
        )


def draw_pies(draw: ImageDraw, width: int, height: int) -> None:
    """Draw steaming pies in the display window."""
    import random

    rng = random.Random(17)
    cx = width // 2
    sy = int(height * 0.41)

    pie_positions = [
        (cx - 70, sy + 20, 25),
        (cx + 20, sy + 30, 20),
        (cx - 40, sy + 50, 30),
        (cx + 50, sy + 60, 22),
    ]

    for px, py, size in pie_positions:
        # Pie body
        draw.ellipse([px - size, py - size // 2, px + size, py + size // 2], fill=(200, 150, 80))
        draw.ellipse([px - size + 3, py - size // 2 - 2, px + size - 3, py + size // 2 + 2], fill=(180, 130, 60))
        # Lattice crust (simplified)
        draw.line([px - size + 5, py, px + size - 5, py], fill=(160, 100, 40), width=2)
        draw.line([px, py - size // 4, px, py + size // 4], fill=(160, 100, 40), width=2)
        # Steam
        for s in range(3):
            sx = px + rng.randint(-8, 8)
            sy_s = py - size // 2 - 5 - s * 8
            draw.ellipse(
                [sx - 3 - s, sy_s - 2, sx + 3 + s, sy_s + 2],
                fill=(220, 210, 200, 100 - s * 25),
            )


def draw_village_lights(draw: ImageDraw, width: int, height: int) -> None:
    """Draw warm ambient light particles and stars."""
    import random

    rng = random.Random(23)

    # Warm light particles
    for _ in range(60):
        x = rng.randint(100, width - 100)
        y = rng.randint(50, int(height * 0.35))
        size = rng.randint(2, 5)
        brightness = rng.randint(100, 200)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, 180, 120))
        # Glow
        draw.ellipse([x - size * 2, y - size * 2, x + size * 2, y + size * 2], fill=(brightness, brightness, 200, 30))

    # Lamplight posts
    for lx in [120, width - 120]:
        ly = int(height * 0.48)
        draw.rectangle([lx - 3, ly, lx + 3, ly + 80], fill=(60, 55, 45))
        draw.ellipse([lx - 12, ly - 10, lx + 12, ly + 8], fill=(255, 200, 100, 200))
        # Lamp glow
        for g in range(3):
            glow_size = 20 + g * 15
            draw.ellipse(
                [lx - glow_size, ly - glow_size, lx + glow_size, ly + glow_size],
                fill=(255, 200, 100, 20 - g * 5),
            )


def draw_title_panel(draw: ImageDraw, draw_img: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(40, 30, 20, 230))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 150, 100), width=2)

    # Title text
    title = "The Kitchen Witch"
    title_font_size = 82
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 100
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Subtitle line
    subtitle = "A Cozy Fantasy"
    sub_font_size = 30
    try:
        sub_font = ImageFont.truetype(str(font_paths["small"]), sub_font_size)
    except Exception:
        sub_font = ImageFont.load_default()

    try:
        sbbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        sw = 0
    sx = (width - sw) // 2
    sy = ty + 100
    draw.text((sx, sy), subtitle, fill=(200, 180, 140), font=sub_font)

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
    ay = sy + 70
    draw.text((ax, ay), author, fill=(255, 255, 255), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Kitchen Witch")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Village square and buildings
    draw_village_square(draw, WIDTH, HEIGHT)

    # Step 3: Central bakery shop
    draw_bakery_shop(draw, WIDTH, HEIGHT)

    # Step 4: Pies in the window with steam
    draw_pies(draw, WIDTH, HEIGHT)

    # Step 5: Warm lights and lampposts
    draw_village_lights(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
    draw_title_panel(draw, draw, WIDTH, HEIGHT, font_paths)

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