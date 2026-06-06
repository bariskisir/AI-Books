#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Job (Heist Noir)."""

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
    """Dark steel-blue to near-black gradient for the noir city feel."""
    for y in range(height):
        if y < height * 0.5:
            t = y / (height * 0.5)
            c = lerp_color((5, 5, 15), (20, 15, 30), t)
        else:
            t = (y - height * 0.5) / (height * 0.5)
            c = lerp_color((20, 15, 30), ((8, 5, 10)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_city_skyline(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark city skyline silhouette across the middle."""
    buildings = [
        (50, int(height * 0.55), 80, int(height * 0.65)),
        (130, int(height * 0.50), 60, int(height * 0.65)),
        (190, int(height * 0.60), 100, int(height * 0.65)),
        (290, int(height * 0.52), 70, int(height * 0.65)),
        (360, int(height * 0.58), 90, int(height * 0.65)),
        (450, int(height * 0.48), 55, int(height * 0.65)),
        (505, int(height * 0.55), 120, int(height * 0.65)),
        (625, int(height * 0.53), 65, int(height * 0.65)),
        (690, int(height * 0.60), 85, int(height * 0.65)),
        (775, int(height * 0.50), 75, int(height * 0.65)),
        (850, int(height * 0.56), 100, int(height * 0.65)),
        (950, int(height * 0.48), 60, int(height * 0.65)),
        (1010, int(height * 0.55), 110, int(height * 0.65)),
        (1120, int(height * 0.52), 70, int(height * 0.65)),
        (1190, int(height * 0.58), 90, int(height * 0.65)),
        (1280, int(height * 0.50), 80, int(height * 0.65)),
        (1360, int(height * 0.55), 70, int(height * 0.65)),
        (1430, int(height * 0.60), 100, int(height * 0.65)),
        (1530, int(height * 0.52), 60, int(height * 0.65)),
    ]

    for bx, by, bw, bh in buildings:
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(10, 8, 15))

    # Some lit windows in the buildings
    import random

    rng = random.Random(42)
    for bx, by, bw, bh in buildings:
        for _ in range(rng.randint(2, 6)):
            wx = bx + rng.randint(5, bw - 10)
            wy = by + rng.randint(5, bh - 15)
            draw.rectangle([wx, wy, wx + 4, wy + 6], fill=(60, 55, 40, 180))
            draw.rectangle([wx, wy, wx + 4, wy + 6], fill=(80, 75, 55, 100))


def draw_vault_door(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large vault door silhouette in the center, slightly above middle."""
    cx = width // 2
    cy = int(height * 0.38)
    door_w = 360
    door_h = 460

    # Door frame
    draw.rectangle(
        [cx - door_w // 2 - 15, cy - door_h // 2 - 15, cx + door_w // 2 + 15, cy + door_h // 2 + 15],
        fill=(15, 12, 10),
    )

    # Door body
    draw.rectangle(
        [cx - door_w // 2, cy - door_h // 2, cx + door_w // 2, cy + door_h // 2],
        fill=(25, 22, 20),
    )

    # Door edge highlight
    draw.rectangle(
        [cx - door_w // 2, cy - door_h // 2, cx + door_w // 2, cy + door_h // 2],
        outline=(45, 40, 35),
        width=2,
    )

    # Circular dial in center of door
    dial_r = 55
    dial_cx = cx
    dial_cy = cy + 20
    draw.ellipse(
        [dial_cx - dial_r, dial_cy - dial_r, dial_cx + dial_r, dial_cy + dial_r],
        fill=(35, 30, 25),
        outline=(55, 50, 40),
        width=3,
    )

    # Inner dial ring
    draw.ellipse(
        [dial_cx - 30, dial_cy - 30, dial_cx + 30, dial_cy + 30],
        fill=(45, 40, 35),
        outline=(65, 60, 50),
        width=2,
    )

    # Dial markings
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        x1 = dial_cx + 40 * math.cos(rad)
        y1 = dial_cy + 40 * math.sin(rad)
        x2 = dial_cx + 48 * math.cos(rad)
        y2 = dial_cy + 48 * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=(80, 75, 65), width=2)

    # Handle (spoked wheel below dial)
    handle_cx = cx
    handle_cy = cy + 100
    handle_r = 35
    draw.ellipse(
        [handle_cx - handle_r, handle_cy - handle_r, handle_cx + handle_r, handle_cy + handle_r],
        fill=(30, 25, 20),
        outline=(50, 45, 40),
        width=3,
    )

    # Spokes
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        x1 = handle_cx + 12 * math.cos(rad)
        y1 = handle_cy + 12 * math.sin(rad)
        x2 = handle_cx + handle_r * math.cos(rad)
        y2 = handle_cy + handle_r * math.sin(rad)
        draw.line([(x1, y1), (x2, y2)], fill=(55, 50, 45), width=2)

    # Hinges on the right side
    for hinge_y in [cy - door_h // 4, cy, cy + door_h // 4]:
        draw.rectangle(
            [cx + door_w // 2 - 5, hinge_y - 10, cx + door_w // 2 + 5, hinge_y + 10],
            fill=(35, 30, 25),
        )

    # Bolts on the left side
    for bolt_y in [cy - door_h // 4, cy, cy + door_h // 4]:
        draw.ellipse(
            [cx - door_w // 2 - 8, bolt_y - 8, cx - door_w // 2 + 2, bolt_y + 8],
            fill=(50, 45, 40),
        )

    # Amber glow from dial
    for i in range(4):
        glow_size = dial_r + 10 + i * 15
        alpha = 25 - i * 5
        draw.ellipse(
            [dial_cx - glow_size, dial_cy - glow_size, dial_cx + glow_size, dial_cy + glow_size],
            outline=(180, 120, 30, alpha),
            width=2,
        )


def draw_old_man_silhouette(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a silhouette of an old man walking away below the vault."""
    cx = width // 2
    base_y = int(height * 0.72)

    # Body (trench coat silhouette)
    body_top = base_y - 120
    body_w = 40
    # Coat shape
    draw.polygon(
        [
            (cx - 15, body_top + 30),  # shoulders
            (cx + 15, body_top + 30),
            (cx + 22, base_y),  # coat bottom right
            (cx + 15, base_y + 10),
            (cx - 15, base_y + 10),
            (cx - 22, base_y),  # coat bottom left
        ],
        fill=(5, 5, 8),
    )

    # Head
    draw.ellipse([cx - 10, body_top, cx + 10, body_top + 22], fill=(5, 5, 8))

    # Hat (fedora)
    draw.ellipse([cx - 18, body_top - 3, cx + 18, body_top + 8], fill=(5, 5, 8))
    draw.rectangle([cx - 14, body_top + 5, cx + 14, body_top + 12], fill=(5, 5, 8))

    # Legs
    draw.rectangle([cx - 14, base_y, cx - 4, base_y + 30], fill=(5, 5, 8))
    draw.rectangle([cx + 4, base_y, cx + 14, base_y + 30], fill=(5, 5, 8))

    # Shadow on ground
    draw.ellipse([cx - 35, base_y + 28, cx + 35, base_y + 36], fill=(0, 0, 0, 80))


def draw_steel_accents(draw: ImageDraw, width: int, height: int) -> None:
    """Draw subtle steel/amber decorative lines."""
    import random

    rng = random.Random(13)

    # Horizontal steel lines across the cover
    for y_pos in [height * 0.15, height * 0.78, height * 0.82]:
        draw.line([(100, y_pos), (width - 100, y_pos)], fill=(60, 55, 50, 60), width=1)

    # Amber accent dots
    for _ in range(30):
        x = rng.randint(50, width - 50)
        y = rng.randint(100, int(height * 0.85))
        if abs(x - width // 2) < 200 and y > height * 0.25 and y < height * 0.55:
            continue
        size = rng.randint(1, 3)
        alpha = rng.randint(30, 80)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(180, 120, 30, alpha))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom with white text for readability."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    for y in range(panel_top, height):
        t = (y - panel_top) / (height - panel_top)
        if t < 0.3:
            c = (12, 10, 15, 220)
        else:
            c = (8, 6, 10, 230)
        draw.line([(0, y), (width, y)], fill=c)

    # Steel border at top of panel
    draw.line([(0, panel_top), (width, panel_top)], fill=(100, 95, 85), width=2)
    draw.line([(0, panel_top + 3), (width, panel_top + 3)], fill=(50, 45, 40), width=1)

    # Title text
    title = "The Last Job"
    title_font_size = 82
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
    draw.text((tx, panel_top + 90), title, fill=(255, 255, 255), font=title_font)

    # Subtitle genre line
    subtitle = "A HEIST NOIR"
    sub_font_size = 28
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
    draw.text((sx, panel_top + 210), subtitle, fill=(180, 120, 30), font=sub_font)

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
    ay = panel_top + 280
    draw.text((ax, ay), author, fill=(200, 195, 190), font=author_font)

    # Bottom steel line
    draw.line([(0, height - 1), (width, height - 1)], fill=(60, 55, 50), width=2)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Job")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: City skyline
    draw_city_skyline(draw, WIDTH, HEIGHT)

    # Step 3: Vault door
    draw_vault_door(draw, WIDTH, HEIGHT)

    # Step 4: Steel accents
    draw_steel_accents(draw, WIDTH, HEIGHT)

    # Step 5: Old man silhouette
    draw_old_man_silhouette(draw, WIDTH, HEIGHT)

    # Step 6: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
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