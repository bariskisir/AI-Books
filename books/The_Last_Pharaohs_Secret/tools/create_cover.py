#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Pharaoh's Secret."""

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
    """Nile sunset gradient: deep indigo at top, gold/orange mid, dark bronze at bottom."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((15, 5, 40), ((80, 30, 60)), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((80, 30, 60), ((180, 100, 40)), t)
        else:
            t = (y - height * 0.6) / (height * 0.4)
            c = lerp_color((180, 100, 40), ((40, 20, 10)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_sun(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the setting sun over the Nile horizon."""
    cx, cy = width // 2, int(height * 0.45)
    radius = 120

    # Outer glow
    for i in range(5):
        r = radius + i * 30
        alpha = max(0, 60 - i * 10)
        draw.ellipse(
            [cx - r, cy - r, cx + r, cy + r],
            fill=(255, 200, 50, alpha),
        )

    # Sun disk
    draw.ellipse(
        [cx - radius, cy - radius, cx + radius, cy + radius],
        fill=(255, 180, 40),
    )
    draw.ellipse(
        [cx - radius - 20, cy - radius - 20, cx + radius + 20, cy + radius + 20],
        outline=(255, 220, 100, 80),
        width=4,
    )

    # Sun rays
    for angle_deg in range(0, 360, 15):
        rad = math.radians(angle_deg)
        inner_r = radius + 10
        outer_r = radius + 60
        x1 = cx + int(inner_r * math.cos(rad))
        y1 = cy + int(inner_r * math.sin(rad))
        x2 = cx + int(outer_r * math.cos(rad))
        y2 = cy + int(outer_r * math.sin(rad))
        draw.line([(x1, y1), (x2, y2)], fill=(255, 200, 60, 100), width=3)


def draw_nile(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the Nile river with reflection near the bottom."""
    y_base = int(height * 0.58)
    # River surface
    for y in range(y_base, y_base + 80):
        t = (y - y_base) / 80
        c = lerp_color((200, 140, 60), ((60, 40, 80)), t)
        draw.line([(0, y), (width, y)], fill=c)

    # Water reflection of sun
    ref_cx = width // 2
    for i in range(10):
        ref_y = y_base + 5 + i * 7
        ref_w = max(10, 120 - i * 10)
        alpha = max(20, 80 - i * 6)
        draw.rectangle(
            [ref_cx - ref_w, ref_y, ref_cx + ref_w, ref_y + 3],
            fill=(255, 200, 60, alpha),
        )


def draw_pyramid(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a distant pyramid silhouette on the horizon."""
    rng = random.Random(42)

    positions = [
        (width // 2 - 350, 0.42, 0.85),
        (width // 2 - 200, 0.45, 0.7),
        (width // 2 + 150, 0.40, 0.9),
        (width // 2 + 320, 0.43, 0.65),
    ]

    for px, scale_h, scale_w in positions:
        pyr_h = int(180 * scale_h)
        pyr_w = int(200 * scale_w)
        base_y = int(height * 0.55)
        top_y = base_y - pyr_h
        left_x = px - pyr_w // 2
        right_x = px + pyr_w // 2

        # Pyramid body
        draw.polygon(
            [(left_x, base_y), (right_x, base_y), (px, top_y)],
            fill=(40, 25, 15),
        )
        # Highlight side (sun-facing)
        draw.polygon(
            [(px, top_y), (px, base_y), (right_x, base_y)],
            fill=(60, 35, 20),
        )


def draw_hieroglyphs(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stylized hieroglyph symbols on the tomb wall."""
    rng = random.Random(7)
    symbols = []

    # Generate hieroglyph-like symbols (left side)
    for y in range(400, int(height * 0.45), 60):
        symbols.append({
            "x": rng.randint(40, 120),
            "y": y,
            "size": rng.randint(12, 20),
        })
        symbols.append({
            "x": rng.randint(150, 220),
            "y": y,
            "size": rng.randint(10, 16),
        })

    # Right side
    for y in range(400, int(height * 0.45), 50):
        symbols.append({
            "x": rng.randint(width - 220, width - 150),
            "y": y,
            "size": rng.randint(12, 18),
        })
        symbols.append({
            "x": rng.randint(width - 130, width - 50),
            "y": y,
            "size": rng.randint(10, 15),
        })

    for s in symbols:
        x, y, size = s["x"], s["y"], s["size"]
        # Eye of Horus style symbol
        color = (200, 170, 100, 120)
        # Ankh-like symbol
        draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
        draw.line([(x - size // 2, y), (x + size // 2, y)], fill=color, width=2)
        draw.ellipse([x - size // 3, y - size, x + size // 3, y - size // 2], fill=None, outline=color, width=2)

    # Larger decorative border hieroglyphs
    for x in range(50, width - 50, 60):
        if x < width // 3 or x > width * 2 // 3:
            h_y = int(height * 0.62)
            draw.rectangle([x, h_y, x + 20, h_y + 25], fill=None, outline=(180, 150, 80, 80), width=1)


def draw_tomb_entrance(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized tomb entrance doorway."""
    door_w = 180
    door_h = 300
    dx = width // 2
    top_y = int(height * 0.25)
    bottom_y = top_y + door_h

    # Doorway frame
    draw.polygon(
        [
            (dx - door_w // 2 - 30, bottom_y),
            (dx + door_w // 2 + 30, bottom_y),
            (dx + door_w // 2 + 30, top_y - 20),
            (dx, top_y - 80),
            (dx - door_w // 2 - 30, top_y - 20),
        ],
        fill=(30, 15, 8),
    )

    # Inner doorway (dark)
    draw.polygon(
        [
            (dx - door_w // 2, bottom_y - 5),
            (dx + door_w // 2, bottom_y - 5),
            (dx + door_w // 2, top_y - 10),
            (dx, top_y - 60),
            (dx - door_w // 2, top_y - 10),
        ],
        fill=(10, 5, 3),
    )

    # Door frame decoration
    draw.rectangle(
        [dx - door_w // 2 - 15, top_y - 15, dx - door_w // 2 - 8, bottom_y],
        fill=(200, 160, 60),
    )
    draw.rectangle(
        [dx + door_w // 2 + 8, top_y - 15, dx + door_w // 2 + 15, bottom_y],
        fill=(200, 160, 60),
    )

    # Winged sun disk above door
    disk_y = top_y - 100
    draw.ellipse(
        [dx - 30, disk_y - 20, dx + 30, disk_y + 20],
        fill=(220, 180, 40),
    )
    # Wings
    for i in range(5):
        wx = dx + 30 + i * 25
        wy = disk_y - 5 * i
        draw.line([(wx, wy), (wx + 20, wy - 10)], fill=(200, 160, 50, 150), width=3)
        wx = dx - 30 - i * 25
        wy = disk_y - 5 * i
        draw.line([(wx, wy), (wx - 20, wy - 10)], fill=(200, 160, 50, 150), width=3)


def draw_stars(draw: ImageDraw, width: int, height: int) -> None:
    """Draw stars in the upper sky."""
    rng = random.Random(13)
    for _ in range(80):
        x = rng.randint(0, width)
        y = rng.randint(0, int(height * 0.35))
        size = rng.randint(1, 3)
        brightness = rng.randint(150, 255)
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(brightness, brightness, brightness, brightness),
        )
        if size > 1 and rng.random() < 0.3:
            draw.line(
                [(x - size * 3, y), (x + size * 3, y)],
                fill=(brightness, brightness, brightness, 40),
                width=1,
            )
            draw.line(
                [(x, y - size * 3), (x, y + size * 3)],
                fill=(brightness, brightness, brightness, 40),
                width=1,
            )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark panel at the bottom with white title text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(15, 8, 5, 230))

    # Gold decorative border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(200, 160, 50), width=3)
    draw.line([(0, panel_top + 4), (width, panel_top + 4)], fill=(120, 90, 20), width=1)

    # Title text
    title = "The Last\nPharaoh's Secret"
    title_font_size = 80
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
        y_offset += 95

    # Decorative line between title and author
    line_y = y_offset + 10
    line_w = 200
    draw.line(
        [(width // 2 - line_w // 2, line_y), (width // 2 + line_w // 2, line_y)],
        fill=(200, 160, 50),
        width=2,
    )

    # Author
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
    ay = line_y + 35
    draw.text((ax, ay), author, fill=(220, 200, 170), font=author_font)

    # Small decorative ankh at bottom
    bottom_y = ay + 60
    draw.line([(width // 2 - 8, bottom_y), (width // 2 + 8, bottom_y)], fill=(200, 160, 50, 100), width=2)
    draw.line([(width // 2, bottom_y - 10), (width // 2, bottom_y + 10)], fill=(200, 160, 50, 100), width=2)
    draw.ellipse(
        [width // 2 - 5, bottom_y - 10, width // 2 + 5, bottom_y - 2],
        fill=None,
        outline=(200, 160, 50, 100),
        width=2,
    )


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Stars in upper sky
    draw_stars(draw, WIDTH, HEIGHT)

    # Step 3: Distant pyramids
    draw_pyramid(draw, WIDTH, HEIGHT)

    # Step 4: Nile river
    draw_nile(draw, WIDTH, HEIGHT)

    # Step 5: Setting sun
    draw_sun(draw, WIDTH, HEIGHT)

    # Step 6: Tomb entrance
    draw_tomb_entrance(draw, WIDTH, HEIGHT)

    # Step 7: Hieroglyphs
    draw_hieroglyphs(draw, WIDTH, HEIGHT)

    # Step 8: Title panel
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