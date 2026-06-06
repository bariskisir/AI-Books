#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Miracle of Saint John's."""

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
    """Warm stone gray to deep blue gradient for the inspirational/spiritual feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((120, 110, 100), (90, 75, 65), t)
        elif y < height * 0.75:
            t = (y - height * 0.4) / (height * 0.35)
            c = lerp_color((90, 75, 65), (50, 45, 60), t)
        else:
            t = (y - height * 0.75) / (height * 0.25)
            c = lerp_color((50, 45, 60), (20, 15, 30), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_church(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized church facade with stained glass window and bell tower."""
    cx = width // 2
    base_y = int(height * 0.65)

    # Church body
    body_w, body_h = 400, 300
    draw.rectangle(
        [cx - body_w // 2, base_y - body_h, cx + body_w // 2, base_y],
        fill=(100, 90, 85),
        outline=(70, 60, 55),
        width=2,
    )

    # Bell tower
    tower_w, tower_h = 100, 200
    tower_x = cx - body_w // 2 - tower_w + 20
    draw.rectangle(
        [tower_x, base_y - body_h - tower_h + 60, tower_x + tower_w, base_y - body_h + 60],
        fill=(105, 95, 88),
        outline=(70, 60, 55),
        width=2,
    )

    # Tower spire
    spire_h = 80
    draw.polygon(
        [
            (tower_x - 10, base_y - body_h - tower_h + 60),
            (tower_x + tower_w // 2, base_y - body_h - tower_h + 60 - spire_h),
            (tower_x + tower_w + 10, base_y - body_h - tower_h + 60),
        ],
        fill=(80, 70, 65),
    )

    # Cross on spire
    cx_tower = tower_x + tower_w // 2
    cross_top = base_y - body_h - tower_h + 60 - spire_h - 30
    draw.line([(cx_tower, cross_top), (cx_tower, cross_top + 25)], fill=(200, 180, 120), width=4)
    draw.line([(cx_tower - 12, cross_top + 10), (cx_tower + 12, cross_top + 10)], fill=(200, 180, 120), width=4)

    # Roof
    draw.polygon(
        [
            (cx - body_w // 2 - 20, base_y - body_h),
            (cx, base_y - body_h - 80),
            (cx + body_w // 2 + 20, base_y - body_h),
        ],
        fill=(80, 70, 60),
    )

    # Stained glass window (central, large)
    win_w, win_h = 140, 200
    win_x, win_y = cx - win_w // 2, base_y - body_h + 30

    # Window arch shape
    draw.arc(
        [win_x, win_y, win_x + win_w, win_y + win_h],
        start=0, end=180, fill=(130, 110, 100), width=3,
    )
    draw.rectangle(
        [win_x, win_y + win_h // 2, win_x + win_w, win_y + win_h],
        fill=None, outline=(130, 110, 100), width=3,
    )

    # Stained glass colors - draw segments
    import random
    rng = random.Random(17)

    colors = [
        (200, 50, 50, 180),    # red
        (50, 80, 200, 180),    # blue
        (200, 180, 50, 180),   # gold
        (50, 180, 80, 180),    # green
        (180, 100, 50, 180),   # amber
        (150, 50, 180, 180),   # violet
    ]

    # Fill window with stained glass segments
    segments = 6
    seg_h = win_h // segments
    for s in range(segments):
        sy = win_y + s * seg_h
        color = rng.choice(colors)
        draw.rectangle(
            [win_x + 3, sy + 2, win_x + win_w - 3, sy + seg_h - 2],
            fill=color,
        )

    # Window glow effect
    for i in range(5):
        glow_color = (255, 200, 100, 30 - i * 5)
        draw.rectangle(
            [win_x - i, win_y - i, win_x + win_w + i, win_y + win_h + i],
            outline=None,
            width=0,
        )

    # Rose window above
    rose_r = 40
    rose_cx = cx
    rose_cy = win_y - 60
    draw.ellipse(
        [rose_cx - rose_r, rose_cy - rose_r, rose_cx + rose_r, rose_cy + rose_r],
        fill=(100, 90, 85),
        outline=(70, 60, 55),
        width=2,
    )

    # Rose window segments
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = rose_cx + 5 * math.cos(rad)
        y1 = rose_cy + 5 * math.sin(rad)
        x2 = rose_cx + (rose_r - 5) * math.cos(rad)
        y2 = rose_cy + (rose_r - 5) * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=rng.choice(colors), width=3)

    # Door
    door_w, door_h = 60, 100
    draw.arc(
        [cx - door_w // 2, base_y - door_h, cx + door_w // 2, base_y],
        start=0, end=180, fill=(60, 50, 45), width=3,
    )
    draw.rectangle(
        [cx - door_w // 2, base_y - door_h // 2, cx + door_w // 2, base_y],
        fill=(50, 40, 35),
    )


def draw_city_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw faint city skyline in the background."""
    import random
    rng = random.Random(42)

    base_y = int(height * 0.65)
    buildings = []

    # Left side buildings
    for i in range(8):
        bw = rng.randint(30, 60)
        bh = rng.randint(60, 180)
        bx = i * 80 - 20
        by = base_y - bh
        buildings.append((bx, by, bw, bh))

    # Right side buildings
    for i in range(8):
        bw = rng.randint(30, 60)
        bh = rng.randint(60, 180)
        bx = width - 160 + i * 80
        by = base_y - bh
        buildings.append((bx, by, bw, bh))

    for bx, by, bw, bh in buildings:
        draw.rectangle([bx, by, bx + bw, base_y], fill=(60, 55, 50, 150))

        # Windows on buildings
        for wy in range(by + 5, base_y - 5, 15):
            for wx in range(bx + 4, bx + bw - 4, 12):
                if rng.random() < 0.6:
                    win_brightness = rng.randint(30, 60)
                    draw.rectangle(
                        [wx, wy, wx + 6, wy + 8],
                        fill=(win_brightness + 180, win_brightness + 170, win_brightness + 100, 100),
                    )


def draw_stained_glass_light(draw: ImageDraw, width: int, height: int) -> None:
    """Draw colored light beams from the window onto the ground."""
    cx = width // 2
    window_top = int(height * 0.25)
    window_bottom = int(height * 0.48)
    ground_y = int(height * 0.65)

    colors = [
        (200, 50, 50, 20),
        (50, 80, 200, 20),
        (200, 180, 50, 15),
        (50, 180, 80, 15),
        (180, 100, 50, 15),
        (150, 50, 180, 15),
    ]

    import random
    rng = random.Random(17)

    for i in range(6):
        angle_offset = rng.uniform(-0.3, 0.3)
        left_ratio = i / 6 + angle_offset * 0.1
        right_ratio = (i + 1) / 6 + angle_offset * 0.1

        src_left = cx - 70 + int(140 * left_ratio)
        src_right = cx - 70 + int(140 * right_ratio)

        spread = 200
        dst_left = cx - spread + int(spread * 2 * left_ratio)
        dst_right = cx - spread + int(spread * 2 * right_ratio)

        draw.polygon(
            [
                (src_left, window_top),
                (src_right, window_top),
                (dst_right, ground_y),
                (dst_left, ground_y),
            ],
            fill=rng.choice(colors),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom of the cover with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 15, 30, 220))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(200, 180, 120), width=3)

    # Title text
    title = "The Miracle of\nSaint John's"
    title_font_size = 72
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

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
        y_offset += 90

    # Author name in white
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
    draw.text((ax, ay), author, fill=(200, 180, 120), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Miracle of Saint John's")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Faint city skyline
    draw_city_skyline(draw, WIDTH, HEIGHT)

    # Step 3: Stained glass light beams
    draw_stained_glass_light(draw, WIDTH, HEIGHT)

    # Step 4: Church facade
    draw_church(draw, WIDTH, HEIGHT)

    # Step 5: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
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