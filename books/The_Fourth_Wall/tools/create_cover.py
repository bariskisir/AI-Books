#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Fourth Wall (metafiction)."""

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
    """Cream-to-ink-black gradient — page to void."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((245, 240, 230), (200, 190, 175), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((200, 190, 175), (80, 70, 65), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((80, 70, 65), (15, 10, 10), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_typewriter(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized typewriter silhouette."""
    cx, cy = width // 2, int(height * 0.35)
    base_w, base_h = 280, 40
    roller_w, roller_h = 260, 30
    keys_w, keys_h = 200, 60

    # Base
    draw.rectangle([cx - base_w // 2, cy, cx + base_w // 2, cy + base_h], fill=(30, 25, 20))
    # Roller / carriage
    draw.rectangle([cx - roller_w // 2, cy - roller_h, cx + roller_w // 2, cy], fill=(40, 35, 30))
    draw.rectangle([cx - roller_w // 2 - 10, cy - roller_h - 5, cx + roller_w // 2 + 10, cy - roller_h], fill=(50, 45, 40))
    # Keys area
    draw.rectangle([cx - keys_w // 2, cy + base_h, cx + keys_w // 2, cy + base_h + keys_h], fill=(35, 30, 25))
    # Key rows
    rng = random.Random(8)
    for row in range(4):
        for col in range(8):
            kx = cx - keys_w // 2 + 15 + col * 24 + rng.randint(-2, 2)
            ky = cy + base_h + 10 + row * 14 + rng.randint(-1, 1)
            draw.ellipse([kx - 5, ky - 5, kx + 5, ky + 5], fill=(60, 55, 50))

    # Paper coming out of typewriter
    draw.rectangle(
        [cx - roller_w // 2 + 20, cy - roller_h - 120, cx + roller_w // 2 - 20, cy - roller_h],
        fill=(240, 235, 225),
    )
    # Lines of text on the paper
    for line_idx in range(5):
        ly = cy - roller_h - 100 + line_idx * 18
        lx = cx - roller_w // 2 + 40
        for _ in range(rng.randint(4, 10)):
            lx += rng.randint(12, 20)
            draw.line([(lx, ly), (lx + 8, ly)], fill=(80, 75, 70), width=2)


def draw_manuscript_pages(draw: ImageDraw, width: int, height: int) -> None:
    """Scattered manuscript pages floating/drifting."""
    rng = random.Random(14)
    for _ in range(12):
        px = rng.randint(100, width - 100)
        py = rng.randint(int(height * 0.1), int(height * 0.75))
        angle = rng.uniform(-0.3, 0.3)
        pw, ph = 140, 180

        # Page shadow
        page_img = Image.new("RGBA", (int(pw + 20), int(ph + 20)), (0, 0, 0, 0))
        page_draw = ImageDraw.Draw(page_img)
        page_draw.rectangle([10, 10, 10 + pw, 10 + ph], fill=(235, 230, 220, 200))
        # Text lines on page
        for l in range(5):
            lx = 30
            ly = 40 + l * 28
            for _ in range(rng.randint(3, 7)):
                lx += rng.randint(15, 25)
                page_draw.line([(lx, ly), (lx + rng.randint(20, 50), ly)], fill=(100, 95, 90, 150), width=2)
        rotated = page_img.rotate(angle * 180 / math.pi, expand=True, resample=Image.BICUBIC)
        ox = int(px - rotated.width // 2)
        oy = int(py - rotated.height // 2)
        draw._image.paste(rotated, (ox, oy), rotated)


def draw_figure(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a blurred human figure — Nora/Marcus bleeding through."""
    cx = width // 2
    cy = int(height * 0.58)

    # Create a figure layer
    fig = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    fig_draw = ImageDraw.Draw(fig)

    # Head
    head_r = 30
    fig_draw.ellipse([cx - head_r, cy - 120 - head_r, cx + head_r, cy - 120 + head_r], fill=(60, 55, 50, 160))
    # Body
    body_pts = [
        (cx - 50, cy - 90),
        (cx + 50, cy - 90),
        (cx + 60, cy + 40),
        (cx + 70, cy + 100),
        (cx - 70, cy + 100),
        (cx - 60, cy + 40),
    ]
    fig_draw.polygon(body_pts, fill=(60, 55, 50, 150))

    # Apply blur
    fig = fig.filter(ImageFilter.GaussianBlur(radius=12))
    draw._image.paste(fig, (0, 0), fig)


def draw_crack(draw: ImageDraw, width: int, height: int) -> None:
    """A crack/shatter across the center — the fourth wall breaking."""
    rng = random.Random(3)
    start_x = width // 2 + rng.randint(-100, 100)
    start_y = int(height * 0.25)

    for _ in range(3):
        x, y = start_x, start_y
        points = []
        steps = 30
        for s in range(steps + 1):
            t = s / steps
            x += rng.randint(-8, 8)
            y += int(height * 0.5 / steps) + rng.randint(-3, 3)
            points.append((x, y))
        draw.line(points, fill=(200, 195, 185, 180), width=rng.randint(1, 3))

    # Small shatter fragments near the crack
    for _ in range(20):
        fx = start_x + rng.randint(-100, 100)
        fy = start_y + rng.randint(50, 400)
        draw.polygon(
            [(fx, fy), (fx + rng.randint(-10, 10), fy + rng.randint(-10, 10)), (fx + rng.randint(-10, 10), fy + rng.randint(-10, 10))],
            fill=(200, 195, 185, 120),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Dark panel at bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 15, 15, 230))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(80, 75, 70), width=2)

    # Title text
    title = "The Fourth Wall"
    title_font_size = 80
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
    ay = ty + 120
    draw.text((ax, ay), author, fill=(200, 195, 185), font=author_font)

    # Subtitle line: genre descriptor
    genre_text = "METAFICTION"
    genre_font_size = 20
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
    gy = ay + 50
    draw.text((gx, gy), genre_text, fill=(150, 145, 135), font=genre_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Fourth Wall")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Crack across the image (fourth wall breaking)
    draw_crack(draw, WIDTH, HEIGHT)

    # Step 3: Scattered manuscript pages
    draw_manuscript_pages(draw, WIDTH, HEIGHT)

    # Step 4: Typewriter silhouette
    draw_typewriter(draw, WIDTH, HEIGHT)

    # Step 5: Blurred figure
    draw_figure(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
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