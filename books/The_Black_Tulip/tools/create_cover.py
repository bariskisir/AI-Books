#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Black Tulip."""

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
    """Warm Dutch sky gradient: deep tulip red to amber to dark brown."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((180, 80, 60), (210, 140, 70), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((210, 140, 70), (140, 90, 50), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((140, 90, 50), (60, 35, 20), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_sky_elements(draw: ImageDraw, width: int, height: int) -> None:
    """Draw clouds and a sun in the upper portion of the image."""
    rng = random.Random(13)

    # Sun glow
    sun_x, sun_y = width // 3, int(height * 0.12)
    for r in range(60, 10, -5):
        alpha = max(0, 180 - r * 3)
        draw.ellipse(
            [sun_x - r, sun_y - r, sun_x + r, sun_y + r],
            fill=(255, 220, 150, alpha),
        )

    # Clouds
    for _ in range(6):
        cx = rng.randint(100, width - 100)
        cy = rng.randint(50, int(height * 0.2))
        cw = rng.randint(120, 250)
        ch = rng.randint(30, 60)
        draw.ellipse([cx, cy, cx + cw, cy + ch], fill=(220, 200, 170, 80))
        draw.ellipse([cx + cw // 3, cy - 15, cx + cw * 2 // 3, cy + ch + 10], fill=(210, 190, 160, 60))


def draw_canal(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a canal with reflections in the middle distance."""
    cy = int(height * 0.55)
    ch = int(height * 0.08)

    # Water body
    draw.rectangle([(0, cy), (width, cy + ch)], fill=(70, 90, 100, 180))

    # Water shimmer lines
    rng = random.Random(17)
    for _ in range(30):
        lx = rng.randint(0, width)
        ly = cy + rng.randint(0, ch)
        lw = rng.randint(20, 80)
        draw.line([(lx, ly), (lx + lw, ly)], fill=(120, 150, 160, 60), width=1)


def draw_tulip_fields(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rows of colorful tulips in the foreground fields."""
    rng = random.Random(5)
    field_top = int(height * 0.50)
    field_bottom = int(height * 0.75)

    colors = [
        (180, 40, 40),    # Red
        (200, 60, 50),    # Tulip red
        (160, 30, 80),    # Dark pink
        (220, 180, 40),   # Yellow
        (200, 100, 30),   # Orange
        (140, 40, 120),   # Purple
        (40, 40, 40),     # Near-black (the goal)
    ]

    # Draw rows of tulips
    for row in range(12):
        ry = field_top + row * 18 + rng.randint(0, 5)
        rx = rng.randint(0, 20)
        while rx < width:
            # Tulip flower
            flower_color = rng.choice(colors)
            flower_h = rng.randint(12, 20)
            flower_w = rng.randint(8, 14)

            # Petals (three overlapping ellipses)
            draw.ellipse([rx, ry - flower_h, rx + flower_w, ry], fill=flower_color)
            draw.ellipse([rx - 3, ry - flower_h + 3, rx + flower_w + 3, ry + 2], fill=flower_color)

            # Stem
            stem_h = rng.randint(15, 25)
            draw.line([(rx + flower_w // 2, ry), (rx + flower_w // 2, ry + stem_h)], fill=(60, 80, 40), width=2)

            rx += rng.randint(25, 45)


def draw_windmill(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a Dutch windmill on the horizon."""
    mx = int(width * 0.75)
    my = int(height * 0.42)

    # Base tower (trapezoidal)
    tower_w_top = 40
    tower_w_bot = 55
    tower_h = 120
    draw.polygon(
        [
            (mx - tower_w_top // 2, my - tower_h),
            (mx + tower_w_top // 2, my - tower_h),
            (mx + tower_w_bot // 2, my),
            (mx - tower_w_bot // 2, my),
        ],
        fill=(120, 80, 50),
    )

    # Tower cap (conical roof)
    draw.polygon(
        [
            (mx - tower_w_top // 2 - 5, my - tower_h),
            (mx + tower_w_top // 2 + 5, my - tower_h),
            (mx, my - tower_h - 30),
        ],
        fill=(100, 60, 35),
    )

    # Blades
    blade_length = 70
    blade_width = 8
    for angle in [0, 45, 90, 135]:
        rad = angle * 3.14159 / 180
        ex = mx + int(blade_length * __import__("math").cos(rad))
        ey = (my - tower_h) + int(blade_length * __import__("math").sin(rad))
        draw.line([(mx, my - tower_h), (ex, ey)], fill=(80, 55, 35), width=blade_width)

    # Blade cross-bars
    for angle in [22.5, 67.5, 112.5, 157.5]:
        rad = angle * 3.14159 / 180
        mid_x = mx + int(blade_length * 0.5 * __import__("math").cos(rad))
        mid_y = (my - tower_h) + int(blade_length * 0.5 * __import__("math").sin(rad))
        perp_rad = rad + 1.5708
        px1 = mid_x + int(15 * __import__("math").cos(perp_rad))
        py1 = mid_y + int(15 * __import__("math").sin(perp_rad))
        px2 = mid_x - int(15 * __import__("math").cos(perp_rad))
        py2 = mid_y - int(15 * __import__("math").sin(perp_rad))
        draw.line([(px1, py1), (px2, py2)], fill=(80, 55, 35), width=3)

    # Door
    draw.rectangle([mx - 10, my - 30, mx + 10, my], fill=(60, 35, 20))


def draw_canal_house(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a traditional Amsterdam canal house silhouette on the horizon."""
    hx = int(width * 0.25)
    hy = int(height * 0.42)

    # Building body
    bw, bh = 70, 100
    draw.rectangle([hx - bw // 2, hy - bh, hx + bw // 2, hy], fill=(90, 65, 45))

    # Gable
    gable_w = bw + 20
    draw.polygon(
        [
            (hx - gable_w // 2, hy - bh),
            (hx + gable_w // 2, hy - bh),
            (hx + bw // 2, hy - bh - 30),
            (hx - bw // 2, hy - bh - 30),
        ],
        fill=(100, 75, 55),
    )

    # Windows
    for wx in range(-20, 25, 20):
        wy = hy - bh + 15
        draw.rectangle([hx + wx - 6, wy, hx + wx + 6, wy + 20], fill=(200, 180, 130, 150))
        draw.rectangle([hx + wx - 6, wy, hx + wx + 6, wy + 20], outline=(60, 40, 25), width=1)

    # Door
    draw.rectangle([hx - 8, hy - 25, hx + 8, hy], fill=(60, 35, 20))


def draw_canal_bridge(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a small arched bridge over the canal."""
    bx = int(width * 0.5)
    by = int(height * 0.53)

    # Arch
    arch_r = 60
    for y_offset in range(arch_r):
        line_width = max(1, 8 - y_offset // 4)
        # Left side of arch
        draw.arc(
            [bx - arch_r, by - arch_r + y_offset, bx + arch_r, by + arch_r],
            start=0,
            end=180,
            fill=(100, 75, 55),
            width=line_width,
        )

    # Bridge surface
    draw.line([(bx - arch_r - 20, by), (bx + arch_r + 20, by)], fill=(120, 90, 65), width=6)

    # Railings
    draw.line([(bx - arch_r - 20, by - 12), (bx + arch_r + 20, by - 12)], fill=(80, 55, 35), width=3)
    for px in range(bx - arch_r, bx + arch_r + 1, 15):
        draw.line([(px, by - 12), (px, by)], fill=(80, 55, 35), width=2)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(30, 20, 15, 220))

    # Subtle border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 100, 50), width=3)

    # Subtle inner glow line
    draw.line([(0, panel_top + 4), (width, panel_top + 4)], fill=(80, 50, 30, 100), width=1)

    # Title text
    title = "The Black Tulip"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 90
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Decorative line under title
    line_y = ty + 85
    line_w = 200
    draw.line([(width // 2 - line_w // 2, line_y), (width // 2 + line_w // 2, line_y)], fill=(180, 100, 50), width=2)

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
    ay = line_y + 40
    draw.text((ax, ay), author, fill=(220, 200, 180), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (warm Dutch sky)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Sky elements (clouds, sun)
    draw_sky_elements(draw, WIDTH, HEIGHT)

    # Step 3: Canal in middle distance
    draw_canal(draw, WIDTH, HEIGHT)

    # Step 4: Canal house silhouette
    draw_canal_house(draw, WIDTH, HEIGHT)

    # Step 5: Windmill on horizon
    draw_windmill(draw, WIDTH, HEIGHT)

    # Step 6: Small arched bridge
    draw_canal_bridge(draw, WIDTH, HEIGHT)

    # Step 7: Tulip fields in foreground
    draw_tulip_fields(draw, WIDTH, HEIGHT)

    # Step 8: Title panel (dark background, white text)
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
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