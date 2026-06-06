#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Man Who Forgot His Wife."""

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
    """Clinical white fading to deep memory blue, then dark."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((200, 210, 220), (100, 130, 170), t)
        elif y < height * 0.7:
            t = (y - height * 0.3) / (height * 0.4)
            c = lerp_color((100, 130, 170), (30, 40, 70), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((30, 40, 70), (10, 10, 20), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_hospital_room(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a hospital bed and medical equipment in the upper half."""
    bed_x = width // 2
    bed_y = int(height * 0.38)

    # Hospital bed frame
    draw.rectangle([bed_x - 140, bed_y - 20, bed_x + 140, bed_y + 60], fill=(180, 190, 200))
    draw.rectangle([bed_x - 140, bed_y - 20, bed_x + 140, bed_y - 15], fill=(160, 170, 180))
    # Rails
    draw.rectangle([bed_x - 140, bed_y - 20, bed_x - 135, bed_y + 60], fill=(150, 160, 170))
    draw.rectangle([bed_x + 135, bed_y - 20, bed_x + 140, bed_y + 60], fill=(150, 160, 170))

    # Patient silhouette (blanket-covered figure)
    draw.ellipse([bed_x - 50, bed_y - 50, bed_x + 50, bed_y + 5], fill=(70, 80, 100))
    draw.rectangle([bed_x - 50, bed_y - 20, bed_x + 50, bed_y + 50], fill=(60, 70, 90))
    # Blanket line
    draw.line([(bed_x - 50, bed_y - 15), (bed_x + 50, bed_y - 15)], fill=(50, 60, 80), width=2)

    # IV stand
    draw.line([(bed_x + 170, bed_y - 80), (bed_x + 170, bed_y + 60)], fill=(140, 150, 160), width=3)
    draw.rectangle([bed_x + 160, bed_y - 80, bed_x + 180, bed_y - 75], fill=(140, 150, 160))
    # IV bag
    draw.rectangle([bed_x + 163, bed_y - 70, bed_x + 177, bed_y - 30], fill=(200, 220, 240, 180))
    draw.line([(bed_x + 170, bed_y - 30), (bed_x + 170, bed_y + 20)], fill=(180, 200, 220), width=1)

    # Heart monitor
    monitor_x = bed_x - 250
    monitor_y = bed_y - 100
    draw.rectangle([monitor_x - 40, monitor_y - 30, monitor_x + 40, monitor_y + 30], fill=(30, 35, 40))
    draw.rectangle([monitor_x - 35, monitor_y - 25, monitor_x + 35, monitor_y + 25], fill=(10, 20, 15))
    # Heartbeat line
    hb_points = []
    for i in range(70):
        t = i / 69
        if t < 0.3:
            y = monitor_y + 10
        elif t < 0.4:
            y = monitor_y - 10
        elif t < 0.5:
            y = monitor_y + 15
        elif t < 0.6:
            y = monitor_y - 12
        elif t < 0.7:
            y = monitor_y + 10
        else:
            y = monitor_y + 10
        hb_points.append((monitor_x - 30 + i, y))
    draw.line(hb_points, fill=(0, 255, 0), width=2)


def draw_mirror_reflection(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a fractured mirror effect suggesting shattered memory."""
    mirror_x = width // 2 + 200
    mirror_y = int(height * 0.25)

    # Mirror frame
    frame_size = 80
    draw.rectangle(
        [mirror_x - frame_size, mirror_y - frame_size, mirror_x + frame_size, mirror_y + frame_size],
        outline=(150, 160, 170),
        width=3,
    )

    # Mirror surface (faded reflection)
    draw.rectangle(
        [mirror_x - frame_size + 5, mirror_y - frame_size + 5, mirror_x + frame_size - 5, mirror_y + frame_size - 5],
        fill=(180, 200, 220, 80),
    )

    # Crack lines
    crack_points = [
        (mirror_x, mirror_y - frame_size + 5),
        (mirror_x - 20, mirror_y - 10),
        (mirror_x - 15, mirror_y + 10),
        (mirror_x - 30, mirror_y + frame_size - 5),
    ]
    draw.line(crack_points, fill=(120, 130, 140), width=2)

    crack_points2 = [
        (mirror_x + 5, mirror_y - frame_size + 5),
        (mirror_x + 25, mirror_y + 5),
        (mirror_x + 20, mirror_y + 30),
        (mirror_x + 35, mirror_y + frame_size - 5),
    ]
    draw.line(crack_points2, fill=(120, 130, 140), width=2)

    # Horizontal crack
    draw.line(
        [(mirror_x - frame_size + 5, mirror_y), (mirror_x + frame_size - 5, mirror_y)],
        fill=(130, 140, 150),
        width=1,
    )

    # Fragment missing (dark triangle)
    draw.polygon(
        [
            (mirror_x + 10, mirror_y - 20),
            (mirror_x + 40, mirror_y - 40),
            (mirror_x + 50, mirror_y - 5),
        ],
        fill=(20, 25, 35),
    )


def draw_family_photo(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a faded family photograph lying on the bedside table."""
    photo_x = width // 2 - 230
    photo_y = int(height * 0.48)

    # Photo with slight rotation
    cos_a = 0.98
    sin_a = 0.02

    # Photo frame
    pw, ph = 100, 70
    corners = [
        (photo_x, photo_y),
        (photo_x + pw, photo_y - int(pw * sin_a)),
        (photo_x + pw + int(ph * sin_a), photo_y + ph),
        (photo_x + int(ph * sin_a), photo_y + ph),
    ]
    draw.polygon(corners, fill=(200, 190, 180))
    draw.polygon(corners, outline=(160, 150, 140), width=2)

    # Inner photo area
    inner = [
        (photo_x + 5, photo_y + 5),
        (photo_x + pw - 5, photo_y - int(pw * sin_a) + 5),
        (photo_x + pw - 5 + int(ph * sin_a), photo_y + ph - 5),
        (photo_x + 5 + int(ph * sin_a), photo_y + ph - 5),
    ]
    draw.polygon(inner, fill=(160, 170, 185, 100))

    # Three stick figures (family)
    fx, fy = photo_x + 25, photo_y + 30
    # Adult 1
    draw.ellipse([fx, fy, fx + 10, fy + 10], fill=(60, 50, 70))
    draw.line([(fx + 5, fy + 10), (fx + 5, fy + 35)], fill=(60, 50, 70), width=2)
    draw.line([(fx + 5, fy + 20), (fx - 5, fy + 28)], fill=(60, 50, 70), width=2)
    draw.line([(fx + 5, fy + 20), (fx + 15, fy + 28)], fill=(60, 50, 70), width=2)

    # Adult 2
    fx2 = photo_x + 50
    draw.ellipse([fx2, fy, fx2 + 10, fy + 10], fill=(70, 40, 60))
    draw.line([(fx2 + 5, fy + 10), (fx2 + 5, fy + 35)], fill=(70, 40, 60), width=2)
    draw.line([(fx2 + 5, fy + 20), (fx2 - 5, fy + 28)], fill=(70, 40, 60), width=2)
    draw.line([(fx2 + 5, fy + 20), (fx2 + 15, fy + 28)], fill=(70, 40, 60), width=2)

    # Child
    fx3 = photo_x + 37
    fy3 = fy + 20
    draw.ellipse([fx3, fy3, fx3 + 7, fy3 + 7], fill=(80, 70, 80))
    draw.line([(fx3 + 3, fy3 + 7), (fx3 + 3, fy3 + 25)], fill=(80, 70, 80), width=2)

    # Photo corner fold
    draw.polygon(
        [(photo_x + pw - 5, photo_y - int(pw * sin_a) + 5), (photo_x + pw, photo_y - int(pw * sin_a)), (photo_x + pw - 8, photo_y - int(pw * sin_a) + 8)],
        fill=(140, 130, 120),
    )


def draw_memory_fragments(draw: ImageDraw, width: int, height: int) -> None:
    """Draw scattered memory fragments — floating polaroid-like shapes."""
    rng = random.Random(42)
    fragments = [
        (int(width * 0.15), int(height * 0.55), 60, 45),
        (int(width * 0.78), int(height * 0.5), 50, 40),
        (int(width * 0.1), int(height * 0.7), 45, 35),
        (int(width * 0.85), int(height * 0.65), 55, 40),
    ]

    for fx, fy, fw, fh in fragments:
        # Fragment shape (polaroid)
        draw.rectangle([fx, fy, fx + fw, fy + fh], fill=(200, 205, 215, 80))
        draw.rectangle([fx, fy, fx + fw, fy + fh], outline=(180, 185, 195, 120), width=1)
        # Image area inside
        draw.rectangle([fx + 3, fy + 3, fx + fw - 3, fy + fh - 12], fill=(160, 170, 185, 60))

    # Floating question marks
    question_positions = [
        (int(width * 0.2), int(height * 0.35)),
        (int(width * 0.8), int(height * 0.4)),
        (int(width * 0.35), int(height * 0.6)),
        (int(width * 0.7), int(height * 0.58)),
    ]

    for qx, qy in question_positions:
        # Draw question mark shape
        draw.ellipse([qx - 3, qy - 10, qx + 3, qy - 4], fill=(180, 200, 230, 100))
        draw.line([(qx, qy - 4), (qx, qy + 2)], fill=(180, 200, 230, 100), width=2)
        draw.line([(qx, qy + 8), (qx, qy + 10)], fill=(180, 200, 230, 100), width=2)


def draw_clinical_lights(draw: ImageDraw, width: int, height: int) -> None:
    """Draw overhead fluorescent light bars."""
    # Light fixture 1
    lx, ly = width // 2 - 120, 60
    draw.rectangle([lx, ly, lx + 240, ly + 15], fill=(40, 45, 55))
    draw.rectangle([lx + 5, ly + 3, lx + 115, ly + 12], fill=(200, 220, 255, 60))
    draw.rectangle([lx + 125, ly + 3, lx + 235, ly + 12], fill=(200, 220, 255, 60))

    # Light glow
    for i in range(5):
        glow_alpha = 20 - i * 4
        draw.rectangle(
            [lx - i * 10, ly + 15, lx + 240 + i * 10, ly + 15 + i * 8],
            fill=(200, 220, 255, max(0, glow_alpha)),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 15, 25))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(40, 45, 70), width=2)

    # Title text
    title = "The Man Who\nForgot His Wife"
    title_font_size = 68
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

    # Genre tagline
    tagline = "An Amnesia Thriller"
    tag_font_size = 22
    try:
        tag_font = ImageFont.truetype(str(font_paths["small"]), tag_font_size)
    except Exception:
        tag_font = ImageFont.load_default()

    try:
        tbbox = draw.textbbox((0, 0), tagline, font=tag_font)
        tw = tbbox[2] - tbbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    draw.text((tx, y_offset + 10), tagline, fill=(140, 150, 180), font=tag_font)

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
    ay = y_offset + 65
    draw.text((ax, ay), author, fill=(200, 210, 230), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Man Who Forgot His Wife")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Clinical fluorescent lights
    draw_clinical_lights(draw, WIDTH, HEIGHT)

    # Step 3: Hospital room
    draw_hospital_room(draw, WIDTH, HEIGHT)

    # Step 4: Fractured mirror
    draw_mirror_reflection(draw, WIDTH, HEIGHT)

    # Step 5: Family photo
    draw_family_photo(draw, WIDTH, HEIGHT)

    # Step 6: Memory fragments
    draw_memory_fragments(draw, WIDTH, HEIGHT)

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