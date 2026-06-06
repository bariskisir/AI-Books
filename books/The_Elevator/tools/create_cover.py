#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Elevator."""

from __future__ import annotations

import argparse
import json
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
    """Steel gray to amber-alert gradient for high-stakes thriller feel."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((20, 20, 30), ((60, 50, 45)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((60, 50, 45), ((80, 60, 35)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((80, 60, 35), ((15, 10, 8)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_elevator_interior(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the interior of an elevator car with control panel."""
    # Elevator walls
    wall_left = int(width * 0.1)
    wall_right = int(width * 0.9)
    wall_top = int(height * 0.08)
    wall_bottom = int(height * 0.72)

    # Back wall
    draw.rectangle([wall_left, wall_top, wall_right, wall_bottom], fill=(65, 62, 58), outline=(90, 85, 80), width=2)

    # Wall panels (horizontal lines)
    panel_y = wall_top + 80
    for i in range(4):
        draw.line(
            [(wall_left + 10, panel_y), (wall_right - 10, panel_y)],
            fill=(80, 76, 72),
            width=1,
        )
        panel_y += 80

    # Vertical panel seams
    for x_offset in range(wall_left + 60, wall_right, 120):
        draw.line([(x_offset, wall_top), (x_offset, wall_bottom)], fill=(75, 71, 67), width=1)

    # Floor
    draw.rectangle([wall_left, wall_bottom, wall_right, height], fill=(45, 40, 35), outline=(55, 50, 45), width=1)
    # Floor tile lines
    for tile_y in range(wall_bottom + 20, height, 30):
        draw.line([(wall_left, tile_y), (wall_right, tile_y)], fill=(50, 45, 40), width=1)

    # Elevator doors (center)
    door_left = int(width * 0.35)
    door_right = int(width * 0.65)
    door_top = wall_top
    door_bottom = wall_bottom

    # Door frames
    draw.rectangle([door_left, door_top, door_right, door_bottom], fill=(55, 52, 48), outline=(100, 95, 90), width=3)

    # Left door
    draw.rectangle([door_left + 5, door_top + 5, (door_left + door_right) // 2 - 2, door_bottom - 5],
                   fill=(70, 67, 62), outline=(90, 85, 80), width=1)
    # Right door
    draw.rectangle([(door_left + door_right) // 2 + 2, door_top + 5, door_right - 5, door_bottom - 5],
                   fill=(70, 67, 62), outline=(90, 85, 80), width=1)
    # Door seam (centerline)
    draw.line([((door_left + door_right) // 2, door_top + 5), ((door_left + door_right) // 2, door_bottom - 5)],
              fill=(40, 38, 35), width=2)

    # Door window
    window_margin = 15
    draw.rectangle([door_left + window_margin, door_top + 30, door_right - window_margin, door_top + 130],
                   fill=(25, 25, 35), outline=(100, 95, 90), width=2)
    # Dark beyond the doors
    draw.rectangle([door_left + window_margin + 2, door_top + 32, door_right - window_margin - 2, door_top + 128],
                   fill=(10, 10, 20))


def draw_control_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an elevator control panel with glowing countdown display."""
    wall_bottom = int(height * 0.72)

    # Panel position - to the right of doors
    panel_x = int(width * 0.72)
    panel_y = wall_bottom - 160

    # Panel body
    draw.rectangle([panel_x, panel_y, panel_x + 70, panel_y + 140],
                   fill=(40, 38, 35), outline=(100, 95, 90), width=2)

    # Display screen
    draw.rectangle([panel_x + 8, panel_y + 10, panel_x + 62, panel_y + 55],
                   fill=(10, 8, 8), outline=(60, 55, 50), width=1)

    # Countdown numbers (glowing red)
    countdown_text = "16:44"
    try:
        font_small = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 28)
        bbox = draw.textbbox((0, 0), countdown_text, font=font_small)
        tw = bbox[2] - bbox[0]
        tx = panel_x + 35 - tw // 2
        # Glow effect
        for glow_offset in range(3, 0, -1):
            draw.text((tx, panel_y + 17), countdown_text, fill=(60, 0, 0, 30 // glow_offset), font=font_small)
        draw.text((tx, panel_y + 17), countdown_text, fill=(255, 30, 30), font=font_small)
    except Exception:
        pass

    # Floor buttons
    btn_y = panel_y + 70
    for i in range(5):
        draw.rectangle([panel_x + 10, btn_y, panel_x + 60, btn_y + 14],
                       fill=(55, 52, 48), outline=(80, 75, 70), width=1)
        # Amber glow on some buttons
        if i == 2:
            draw.rectangle([panel_x + 10, btn_y, panel_x + 60, btn_y + 14],
                           fill=(80, 60, 20, 180), outline=(120, 90, 30), width=1)
        btn_y += 18

    # Emergency call button (red)
    draw.rectangle([panel_x + 10, panel_y + 155, panel_x + 60, panel_y + 172],
                   fill=(80, 15, 15), outline=(120, 30, 30), width=1)
    try:
        font_tiny = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 9)
        draw.text((panel_x + 35, panel_y + 157), "ALARM", fill=(255, 100, 100), font=font_tiny)
    except Exception:
        pass


def draw_people_silhouettes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw shadowy silhouettes of trapped people in the elevator."""
    wall_bottom = int(height * 0.72)
    door_left = int(width * 0.35)
    door_right = int(width * 0.65)
    wall_left = int(width * 0.1)
    wall_right = int(width * 0.9)

    # People silhouettes (dark figures against the walls)
    positions = [
        (wall_left + 25, wall_bottom - 10, 1.0),
        (wall_left + 45, wall_bottom - 15, 0.8),
        (wall_left + 75, wall_bottom - 5, 0.9),
        (door_left - 20, wall_bottom - 8, 0.7),
        (door_right + 20, wall_bottom - 12, 1.1),
        (wall_right - 30, wall_bottom - 5, 0.85),
        (wall_right - 55, wall_bottom - 18, 0.75),
    ]

    for px, base_y, scale in positions:
        h = int(80 * scale)
        # Body
        draw.ellipse([px - int(10 * scale), base_y - h, px + int(10 * scale), base_y - int(30 * scale)],
                     fill=(15, 12, 10))
        # Head
        draw.ellipse([px - int(6 * scale), base_y - h - int(14 * scale), px + int(6 * scale), base_y - h],
                     fill=(12, 10, 8))


def draw_amber_alert(draw: ImageDraw, width: int, height: int) -> None:
    """Draw amber alert lights/stripes suggesting danger."""
    # Top warning stripe
    for x in range(0, width, 40):
        stripe_color = (200, 120, 20, 180) if (x // 40) % 2 == 0 else (100, 60, 10, 100)
        draw.rectangle([x, 0, x + 40, 18], fill=stripe_color)

    # Amber glow from the control panel area
    wall_bottom = int(height * 0.72)
    panel_x = int(width * 0.72)
    panel_y = wall_bottom - 160

    # Glow ring around display
    for r in range(8, 0, -1):
        draw.ellipse(
            [panel_x + 20 - r, panel_y + 15 - r, panel_x + 50 + r, panel_y + 50 + r],
            outline=(200, 100, 0, 20 // (r + 1)),
            width=1,
        )

    # Ambient amber light on right wall
    draw.rectangle([int(width * 0.72), int(height * 0.25), int(width * 0.9), int(height * 0.35)],
                   fill=(200, 120, 20, 15))


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(12, 10, 10, 220))

    # Subtle top border
    draw.line([(0, panel_top), (width, panel_top)], fill=(200, 120, 20), width=3)

    # Title text
    title = "The Elevator"
    try:
        title_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 86)
    except Exception:
        title_font = ImageFont.load_default()

    try:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    draw.text((tx, panel_top + 90), title, fill=(255, 255, 255), font=title_font)

    # Author name
    author = "Barış Kısır"
    try:
        author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), 32)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    draw.text((ax, panel_top + 200), author, fill=(200, 200, 200), font=author_font)

    # Tagline
    tagline = "A HIGH-STAKES THRILLER"
    try:
        tag_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 18)
    except Exception:
        tag_font = ImageFont.load_default()

    try:
        tbbox = draw.textbbox((0, 0), tagline, font=tag_font)
        tw = tbbox[2] - tbbox[0]
    except Exception:
        tw = 0
    draw.text(((width - tw) // 2, panel_top + 250), tagline, fill=(200, 120, 20), font=tag_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Elevator")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Elevator interior
    draw_elevator_interior(draw, WIDTH, HEIGHT)

    # Step 3: Control panel with countdown
    draw_control_panel(draw, WIDTH, HEIGHT)

    # Step 4: People silhouettes
    draw_people_silhouettes(draw, WIDTH, HEIGHT)

    # Step 5: Amber alert effects
    draw_amber_alert(draw, WIDTH, HEIGHT)

    # Step 6: Title panel with white text on dark background
    draw_title_panel(draw, WIDTH, HEIGHT)

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