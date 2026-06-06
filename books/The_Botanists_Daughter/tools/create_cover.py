#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Botanist's Daughter."""

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
    """Warm parchment-to-forest green gradient for the herbarium feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((210, 195, 165), (160, 140, 100), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((160, 140, 100), (80, 100, 60), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((80, 100, 60), (20, 40, 20), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_pressed_flower(draw: ImageDraw, cx: int, cy: int, scale: float, rotation: float) -> None:
    """Draw a stylized pressed flower with stem and petals."""
    rng = random.Random(hash((cx, cy, scale)) & 0xFFFFFFFF)
    petal_color = (180, 150, 120, 200)
    stem_color = (100, 130, 80, 200)

    # Stem
    stem_len = int(60 * scale)
    end_x = cx + int(stem_len * math.sin(rotation))
    end_y = cy + int(stem_len * math.cos(rotation))
    draw.line([(cx, cy), (end_x, end_y)], fill=stem_color, width=max(1, int(2 * scale)))

    # Leaves
    lx1 = cx + int(20 * scale * math.sin(rotation + 0.5))
    ly1 = cy + int(15 * scale * math.cos(rotation + 0.5))
    draw.ellipse([lx1 - 8 * scale, ly1 - 4 * scale, lx1 + 8 * scale, ly1 + 4 * scale], fill=(120, 150, 90, 180))
    lx2 = cx + int(25 * scale * math.sin(rotation - 0.3))
    ly2 = cy + int(20 * scale * math.cos(rotation - 0.3))
    draw.ellipse([lx2 - 6 * scale, ly2 - 3 * scale, lx2 + 6 * scale, ly2 + 3 * scale], fill=(120, 150, 90, 180))

    # Petals around center
    for i in range(rng.randint(5, 8)):
        angle = rotation + i * (2 * math.pi / 8) + rng.uniform(-0.2, 0.2)
        petal_dist = int(12 * scale) + rng.randint(-3, 3)
        px = cx + int(petal_dist * math.cos(angle))
        py = cy + int(petal_dist * math.sin(angle))
        draw.ellipse(
            [px - 6 * scale, py - 3 * scale, px + 6 * scale, py + 3 * scale],
            fill=petal_color,
        )

    # Center
    draw.ellipse([cx - 4 * scale, cy - 4 * scale, cx + 4 * scale, cy + 4 * scale], fill=(160, 130, 90, 220))


def draw_herbarium_specimens(draw: ImageDraw, width: int, height: int) -> None:
    """Draw mounted pressed plants on the cover like an herbarium sheet."""
    rng = random.Random(42)

    # Stylized herbarium label in upper left
    label_x, label_y = 80, 100
    draw.rectangle(
        [label_x, label_y, label_x + 280, label_y + 160],
        fill=(230, 220, 200, 180),
        outline=(160, 140, 100),
        width=1,
    )
    draw.line([(label_x + 10, label_y + 30), (label_x + 270, label_y + 30)], fill=(140, 120, 80), width=1)
    draw.line([(label_x + 10, label_y + 60), (label_x + 270, label_y + 60)], fill=(140, 120, 80), width=1)
    draw.line([(label_x + 10, label_y + 90), (label_x + 270, label_y + 90)], fill=(140, 120, 80), width=1)
    draw.line([(label_x + 10, label_y + 120), (label_x + 270, label_y + 120)], fill=(140, 120, 80), width=1)

    # Large fern frond - pressed specimen look - left side
    fern_x, fern_y = 250, 500
    for i in range(40):
        t = i / 40
        fx = fern_x + int(t * 300)
        fy = fern_y - int(200 * math.sin(t * math.pi) + 50 * math.cos(t * 4))
        draw.ellipse([fx - 3, fy - 2, fx + 3, fy + 2], fill=(90, 120, 70, 200))

    # Central stem for fern
    draw.line([(fern_x, fern_y), (fern_x + 300, fern_y)], fill=(80, 100, 60, 180), width=2)

    # Small pressed flower cluster - right side
    for i in range(6):
        sx = width - 200 + rng.randint(-30, 30)
        sy = 500 + rng.randint(-40, 40)
        draw_pressed_flower(draw, sx, sy, 1.0 + rng.random() * 0.5, rng.random() * math.pi)

    # Pressed leaves scattered
    for i in range(12):
        lx = rng.randint(100, width - 100)
        ly = rng.randint(600, 1200)
        rot = rng.random() * math.pi
        # Leaf shape as ellipse
        leaf_color = (100, 130, 80, 150)
        draw.ellipse(
            [lx - 15, ly - 6, lx + 15, ly + 6],
            fill=leaf_color,
        )

    # More specimens in lower area
    for i in range(8):
        sx = rng.randint(150, width - 150)
        sy = rng.randint(1300, 1800)
        draw_pressed_flower(draw, sx, sy, 0.8 + rng.random() * 0.8, rng.random() * math.pi)


def draw_botanical_journal(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an open journal with botanical sketches."""
    cx, cy = width // 2, int(height * 0.4)

    # Journal spread
    draw.rectangle(
        [cx - 250, cy - 180, cx + 250, cy + 180],
        fill=(200, 185, 160, 200),
        outline=(140, 120, 80),
        width=2,
    )

    # Spine
    draw.line([(cx, cy - 180), (cx, cy + 180)], fill=(120, 100, 70), width=3)

    # Left page - sketch lines
    for i in range(6):
        ly = cy - 120 + i * 40
        draw.line([(cx - 230, ly), (cx - 20, ly)], fill=(120, 100, 70, 120), width=1)

    # Right page - plant sketch
    draw.ellipse([cx + 40, cy - 120, cx + 120, cy - 40], fill=(160, 140, 100, 100))
    draw.ellipse([cx + 100, cy - 80, cx + 180, cy], fill=(160, 140, 100, 100))
    draw.line([(cx + 80, cy + 20), (cx + 80, cy + 140)], fill=(80, 100, 60, 150), width=2)

    # Botanical notes on right page
    for i in range(4):
        ny = cy + 40 + i * 30
        draw.line([(cx + 30, ny), (cx + 220, ny)], fill=(100, 80, 60, 100), width=1)


def draw_moss_texture(draw: ImageDraw, width: int, height: int) -> None:
    """Add subtle moss/texture along the bottom area."""
    rng = random.Random(17)
    for i in range(200):
        mx = rng.randint(50, width - 50)
        my = rng.randint(int(height * 0.75), height - 100)
        size = rng.randint(4, 12)
        shade = rng.randint(40, 100)
        draw.ellipse(
            [mx - size // 2, my - size // 2, mx + size // 2, my + size // 2],
            fill=(shade, shade + 20, shade - 10, 60),
        )


def draw_parchment_border(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a decorative border framing the cover."""
    border_color = (100, 85, 60, 100)
    # Top border
    for x in range(0, width, 20):
        y = 20 + int(5 * math.sin(x * 0.05))
        draw.ellipse([x, y - 2, x + 8, y + 2], fill=border_color)
    # Bottom border (above title panel)
    y = TITLE_PANEL_TOP - 15
    for x in range(0, width, 20):
        y_off = y + int(3 * math.sin(x * 0.05))
        draw.ellipse([x, y_off - 2, x + 8, y_off + 2], fill=border_color)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark green-brown
    draw.rectangle([(0, panel_top), (width, height)], fill=(25, 35, 20, 230))

    # Top accent line
    draw.line([(0, panel_top), (width, panel_top)], fill=(140, 120, 80), width=3)

    # Decorative corner ornaments
    ornament_color = (140, 120, 80)
    # Top-left corner
    draw.line([(20, panel_top + 10), (20, panel_top + 40)], fill=ornament_color, width=2)
    draw.line([(20, panel_top + 10), (50, panel_top + 10)], fill=ornament_color, width=2)
    # Top-right corner
    draw.line([(width - 20, panel_top + 10), (width - 20, panel_top + 40)], fill=ornament_color, width=2)
    draw.line([(width - 20, panel_top + 10), (width - 50, panel_top + 10)], fill=ornament_color, width=2)

    # Title text
    title = "The Botanist's\nDaughter"
    title_font_size = 68
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
    lines = title.split("\n")
    y_offset = panel_top + 90
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 95

    # Decorative line below title
    line_y = y_offset + 10
    draw.line([(width // 2 - 80, line_y), (width // 2 + 80, line_y)], fill=(140, 120, 80), width=1)

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
    ay = line_y + 30
    draw.text((ax, ay), author, fill=(200, 200, 200), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Botanist's Daughter")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background (parchment to forest green)
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Herbarium specimens and pressed flowers
    draw_herbarium_specimens(draw, WIDTH, HEIGHT)

    # Step 3: Botanical journal
    draw_botanical_journal(draw, WIDTH, HEIGHT)

    # Step 4: Moss texture at bottom
    draw_moss_texture(draw, WIDTH, HEIGHT)

    # Step 5: Parchment border
    draw_parchment_border(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
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