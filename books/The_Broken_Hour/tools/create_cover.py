#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Broken Hour."""

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
    """Deep midnight blue to brass to near-black gradient for the time-loop feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((5, 5, 20), (20, 15, 40), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((20, 15, 40), (60, 50, 30), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((60, 50, 30), (10, 8, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_clock_faces(draw: ImageDraw, width: int, height: int) -> None:
    """Draw floating clock faces in the upper and middle areas."""
    rng = random.Random(13)
    clocks = [
        (width // 2, height // 3, 200),
        (width // 4, height // 5, 100),
        (3 * width // 4, height // 4, 120),
        (width // 3, height // 2, 80),
        (2 * width // 3, height * 3 // 5, 90),
    ]

    for cx, cy, radius in clocks:
        # Clock body - brass/gold
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            fill=(70, 55, 30),
            outline=(140, 120, 60),
            width=4,
        )

        # Inner face
        inner_r = radius - 15
        draw.ellipse(
            [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
            fill=(45, 40, 30),
            outline=(100, 85, 45),
            width=2,
        )

        # Hour markers
        for h in range(12):
            angle = math.radians(h * 30 - 90)
            x1 = cx + int((inner_r - 8) * math.cos(angle))
            y1 = cy + int((inner_r - 8) * math.sin(angle))
            x2 = cx + int((inner_r - 20) * math.cos(angle))
            y2 = cy + int((inner_r - 20) * math.sin(angle))
            draw.line([(x1, y1), (x2, y2)], fill=(180, 170, 140), width=3)

        # Hands - different times on different clocks
        hour_angle = math.radians(rng.randint(0, 360) - 90)
        min_angle = math.radians(rng.randint(0, 360) - 90)
        # Hour hand
        hx = cx + int((inner_r * 0.5) * math.cos(hour_angle))
        hy = cy + int((inner_r * 0.5) * math.sin(hour_angle))
        draw.line([(cx, cy), (hx, hy)], fill=(200, 180, 120), width=5)
        # Minute hand
        mx = cx + int((inner_r * 0.7) * math.cos(min_angle))
        my = cy + int((inner_r * 0.7) * math.sin(min_angle))
        draw.line([(cx, cy), (mx, my)], fill=(200, 180, 120), width=3)

        # Center dot
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(180, 160, 100))

        # Glow effect around clocks
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        for i in range(3):
            gdraw.ellipse(
                [cx - radius - i * 8, cy - radius - i * 8, cx + radius + i * 8, cy + radius + i * 8],
                outline=(140, 120, 60, 30 // (i + 1)),
                width=2,
            )
        draw._image.paste(glow, (0, 0), glow)


def draw_broken_watch(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large broken pocket watch at center-right."""
    cx, cy = width // 2 + 60, height // 2
    radius = 140

    # Cracked body
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(80, 65, 40),
        outline=(160, 140, 70),
        width=5,
    )

    # Crack lines
    draw.line([(cx - 40, cy - 60), (cx + 20, cy + 10), (cx - 30, cy + 80)], fill=(200, 180, 130), width=2)
    draw.line([(cx - 40, cy - 60), (cx + 50, cy - 30)], fill=(200, 180, 130), width=2)
    draw.line([(cx + 20, cy + 10), (cx + 70, cy + 50)], fill=(200, 180, 130), width=2)

    # Inner face
    inner_r = radius - 18
    draw.ellipse(
        [cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r],
        fill=(50, 45, 35),
        outline=(110, 95, 50),
        width=2,
    )

    # Roman numeral markers (simplified)
    for h in range(12):
        angle = math.radians(h * 30 - 90)
        x1 = cx + int((inner_r - 6) * math.cos(angle))
        y1 = cy + int((inner_r - 6) * math.sin(angle))
        x2 = cx + int((inner_r - 18) * math.cos(angle))
        y2 = cy + int((inner_r - 18) * math.sin(angle))
        draw.line([(x1, y1), (x2, y2)], fill=(160, 150, 120), width=2)

    # Hands frozen at 4:14
    # Hour hand pointing roughly at 4
    h_angle = math.radians(4 * 30 + 14 * 0.5 - 90)
    hx = cx + int((inner_r * 0.45) * math.cos(h_angle))
    hy = cy + int((inner_r * 0.45) * math.sin(h_angle))
    draw.line([(cx, cy), (hx, hy)], fill=(200, 180, 120), width=6)

    # Minute hand pointing at 14 minutes
    m_angle = math.radians(14 * 6 - 90)
    mx = cx + int((inner_r * 0.65) * math.cos(m_angle))
    my = cy + int((inner_r * 0.65) * math.sin(m_angle))
    draw.line([(cx, cy), (mx, my)], fill=(200, 180, 120), width=4)

    # Center pin
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(180, 160, 100))

    # Chain
    for i in range(8):
        chain_x = cx + radius + 10 + i * 12
        chain_y = cy - 30 + i * 6
        draw.ellipse(
            [chain_x - 4, chain_y - 4, chain_x + 4, chain_y + 4],
            fill=(100, 85, 45),
            outline=(140, 120, 60),
        )


def draw_gears(draw: ImageDraw, width: int, height: int) -> None:
    """Draw decorative gears in the background."""
    rng = random.Random(7)
    gear_positions = [
        (120, height * 0.6, 50),
        (width - 100, height * 0.45, 40),
        (200, height * 0.75, 35),
        (width - 150, height * 0.7, 45),
        (width // 2, height * 0.15, 30),
    ]

    for gx, gy, gr in gear_positions:
        # Gear teeth
        num_teeth = 8
        outer_r = gr
        inner_r = gr - 8
        points = []
        for i in range(num_teeth * 2):
            angle = math.radians(i * 360 / (num_teeth * 2) - 90)
            r = outer_r if i % 2 == 0 else inner_r
            points.append((gx + r * math.cos(angle), gy + r * math.sin(angle)))
        draw.polygon(points, fill=(50, 42, 25), outline=(90, 75, 40), width=2)

        # Inner hole
        draw.ellipse(
            [gx - gr // 3, gy - gr // 3, gx + gr // 3, gy + gr // 3],
            fill=(35, 30, 20),
            outline=(70, 60, 35),
            width=2,
        )


def draw_time_rings(draw: ImageDraw, width: int, height: int) -> None:
    """Draw concentric time rings radiating from the broken watch."""
    cx, cy = width // 2 + 60, height // 2
    for r in range(180, 500, 40):
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            outline=(100, 85, 45, 40 - r // 20),
            width=1,
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 12, 8))

    # Subtle brass border at top
    draw.line([(0, panel_top), (width, panel_top)], fill=(140, 120, 60), width=3)

    # Decorative line ornaments
    ornament_y = panel_top + 15
    draw.line([(100, ornament_y), (width - 100, ornament_y)], fill=(80, 70, 40), width=1)
    # Small diamond ornament in center
    draw.polygon(
        [(width // 2, ornament_y - 4), (width // 2 + 4, ornament_y), (width // 2, ornament_y + 4), (width // 2 - 4, ornament_y)],
        fill=(180, 160, 100),
    )

    # Title text
    title = "The Broken\nHour"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
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
        y_offset += 95

    # Decorative separator
    sep_y = y_offset + 10
    draw.line([(350, sep_y), (width - 350, sep_y)], fill=(100, 85, 45), width=1)

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
    ay = sep_y + 20
    draw.text((ax, ay), author, fill=(200, 190, 170), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Broken Hour")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Time rings
    draw_time_rings(draw, WIDTH, HEIGHT)

    # Step 3: Background gears
    draw_gears(draw, WIDTH, HEIGHT)

    # Step 4: Floating clock faces
    draw_clock_faces(draw, WIDTH, HEIGHT)

    # Step 5: Broken watch focal point
    draw_broken_watch(draw, WIDTH, HEIGHT)

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