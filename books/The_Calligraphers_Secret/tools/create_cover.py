#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Calligrapher's Secret."""

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
    """Warm parchment-to-deep ink gradient for the historical Baghdad feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((180, 140, 95), (120, 75, 40), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((120, 75, 40), (60, 35, 20), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 35, 20), (15, 8, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_archways(draw: ImageDraw, width: int, height: int) -> None:
    """Draw Abbasid-style arched arcades framing the scene."""
    arch_colors = [(80, 60, 40), (65, 48, 32), (55, 40, 28)]

    for row in range(3):
        for col in range(4):
            cx = 200 + col * 400 + row * 60
            cy = 350 + row * 300
            arch_w = 180 - row * 15
            arch_h = 250 - row * 20

            # Arch outline
            draw.arc(
                [cx - arch_w // 2, cy - arch_h // 2, cx + arch_w // 2, cy + arch_h // 2],
                0, 180, fill=arch_colors[row], width=4
            )
            # Pillars
            draw.rectangle(
                [cx - arch_w // 2 - 6, cy - arch_h // 2, cx - arch_w // 2 + 6, cy + arch_h // 2],
                fill=arch_colors[row]
            )
            draw.rectangle(
                [cx + arch_w // 2 - 6, cy - arch_h // 2, cx + arch_w // 2 + 6, cy + arch_h // 2],
                fill=arch_colors[row]
            )

            # Horseshoe arch inner detail
            if row == 0:
                inner_y = cy - arch_h // 2 + 20
                draw.arc(
                    [cx - arch_w // 4, inner_y, cx + arch_w // 4, cy + arch_h // 4],
                    0, 180, fill=(100, 78, 55), width=2
                )


def draw_calligraphy_border(draw: ImageDraw, width: int, height: int) -> None:
    """Draw decorative Kufic-style calligraphy border bands."""
    rng = random.Random(13)

    # Top decorative band
    for x in range(0, width, 8):
        h = 4 + int(math.sin(x * 0.05) * 3 + 1)
        y_top = 40 + rng.randint(0, 2)
        draw.rectangle([x, y_top, x + 4, y_top + h], fill=(180, 150, 70, 180))

    # Bottom decorative band (above title panel)
    for x in range(0, width, 6):
        h = 3 + int(math.sin(x * 0.08 + 2) * 2 + 1)
        y_bot = TITLE_PANEL_TOP - 60 + rng.randint(0, 2)
        draw.rectangle([x, y_bot, x + 3, y_bot + h], fill=(180, 150, 70, 200))


def draw_manuscript_page(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an open manuscript page with gold illumination in the center."""
    cx, cy = width // 2, height // 2 - 50
    pw, ph = 340, 440

    # Page shadow
    draw.rectangle(
        [cx - pw // 2 + 8, cy - ph // 2 + 8, cx + pw // 2 + 8, cy + ph // 2 + 8],
        fill=(20, 12, 6, 100)
    )

    # Page body (parchment)
    draw.rectangle(
        [cx - pw // 2, cy - ph // 2, cx + pw // 2, cy + ph // 2],
        fill=(215, 195, 160)
    )

    # Text lines (suggesting calligraphy)
    rng = random.Random(42)
    for i in range(12):
        ly = cy - ph // 2 + 30 + i * 32
        line_width = rng.randint(200, 280)
        lx = cx - line_width // 2

        # Simulated Arabic script line
        dx = 0
        while dx < line_width:
            seg_w = rng.randint(8, 24)
            seg_h = rng.randint(3, 6)
            draw.rectangle(
                [lx + dx, ly, lx + dx + seg_w, ly + seg_h],
                fill=(30, 20, 15)
            )
            dx += seg_w + rng.randint(2, 5)

    # Gold illumination border around the page
    border_color = (180, 150, 70)
    draw.rectangle(
        [cx - pw // 2 - 6, cy - ph // 2 - 6, cx + pw // 2 + 6, cy + ph // 2 + 6],
        outline=border_color, width=3
    )

    # Corner ornaments (floral arabesque suggestions)
    for sign_x, sign_y in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
        ox = cx + sign_x * (pw // 2 + 15)
        oy = cy + sign_y * (ph // 2 + 15)
        for r in range(3, 0, -1):
            draw.ellipse(
                [ox - r * 5, oy - r * 5, ox + r * 5, oy + r * 5],
                outline=(180, 150, 70, 200 - r * 30), width=1
            )


def draw_geometric_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw Islamic geometric star patterns in the upper area."""
    cx, cy = 800, 200

    # 8-pointed star
    outer_r = 80
    inner_r = 30
    points = []
    for i in range(16):
        angle = math.pi * i / 8 - math.pi / 2
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        points.append((x, y))

    draw.polygon(points, fill=(160, 130, 55, 120), outline=(180, 150, 70, 200))

    # Smaller surrounding stars
    for angle_offset, scale in [(0.5, 0.3), (2.3, 0.25), (4.0, 0.35), (5.2, 0.28)]:
        sx = cx + 160 * math.cos(angle_offset)
        sy = cy + 120 * math.sin(angle_offset)
        s_points = []
        for i in range(16):
            a = math.pi * i / 8 + angle_offset
            r = (outer_r * scale * 0.6) if i % 2 == 0 else (inner_r * scale * 0.6)
            x = sx + r * math.cos(a)
            y = sy + r * math.sin(a)
            s_points.append((x, y))
        draw.polygon(s_points, fill=(160, 130, 55, 80), outline=(180, 150, 70, 120))


def draw_ink_splatter(draw: ImageDraw, width: int, height: int) -> None:
    """Draw decorative ink splatters and dots suggesting manuscript wear."""
    rng = random.Random(7)

    for _ in range(30):
        x = rng.randint(100, width - 100)
        y = rng.randint(400, TITLE_PANEL_TOP - 100)
        size = rng.randint(2, 6)
        alpha = rng.randint(40, 120)
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(15, 8, 5, alpha)
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 12, 8, 230))

    # Gold accent line at top of panel
    draw.line([(200, panel_top), (width - 200, panel_top)], fill=(180, 150, 70), width=3)

    # Decorative dots flanking the accent line
    for dot_x in [180, width - 180]:
        draw.ellipse([dot_x - 4, panel_top - 4, dot_x + 4, panel_top + 4], fill=(180, 150, 70))

    # Title text - use arialbd.ttf
    title = "The Calligrapher's\nSecret"
    title_font_size = 64
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered in white
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
        y_offset += 85

    # Author name
    author = "Barış Kısır"
    author_font_size = 32
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
    draw.text((ax, ay), author, fill=(200, 180, 140), font=author_font)

    # Decorative line below author
    draw.line([(400, ay + 30), (width - 400, ay + 30)], fill=(100, 80, 55), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Calligrapher's Secret")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Parchment-to-ink gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Islamic geometric stars
    draw_geometric_stars(draw, WIDTH, HEIGHT)

    # Step 3: Abbasid archways
    draw_archways(draw, WIDTH, HEIGHT)

    # Step 4: Manuscript page with gold illumination
    draw_manuscript_page(draw, WIDTH, HEIGHT)

    # Step 5: Calligraphy border bands
    draw_calligraphy_border(draw, WIDTH, HEIGHT)

    # Step 6: Decorative ink splatters
    draw_ink_splatter(draw, WIDTH, HEIGHT)

    # Step 7: Title panel - use arialbd.ttf for title text (WHITE on dark panel)
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arial.ttf"),
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