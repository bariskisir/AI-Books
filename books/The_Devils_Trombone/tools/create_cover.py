#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Devil's Trombone — Jazz Fiction."""

from __future__ import annotations

import argparse
import json
import math
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920
FONTS_DIR = Path("C:/Windows/Fonts")
TITLE_FONT_PATH = FONTS_DIR / "arialbd.ttf"
AUTHOR_FONT_PATH = FONTS_DIR / "arialbd.ttf"
SMALL_FONT_PATH = FONTS_DIR / "arial.ttf"


def wrap_title(title: str, max_chars: int = 14) -> str:
    return "\n".join(textwrap.wrap(title, width=max_chars))


def draw_trombone(draw: ImageDraw, cx: int, cy: int, scale: float = 1.0) -> None:
    """Draw a trombone silhouette in gold."""
    s = scale
    # Slide — horizontal tube
    slide_top = cy
    slide_left = cx - int(140 * s)
    slide_right = cx + int(140 * s)
    slide_h = int(14 * s)
    draw.rectangle(
        [slide_left, slide_top, slide_right, slide_top + slide_h],
        fill=(212, 175, 55, 200),
        outline=(180, 140, 30, 220),
        width=2,
    )

    # Bell — flared end on the right
    bell_x = slide_right
    bell_top = slide_top - int(30 * s)
    bell_bottom = slide_top + slide_h + int(30 * s)
    bell_right = bell_x + int(60 * s)
    draw.polygon(
        [
            (bell_x, bell_top),
            (bell_x, bell_bottom),
            (bell_right, bell_top + int(20 * s)),
            (bell_right, bell_bottom - int(20 * s)),
        ],
        fill=(212, 175, 55, 180),
        outline=(180, 140, 30, 220),
        width=2,
    )

    # Mouthpiece on the left
    mp_x = slide_left
    mp_w = int(20 * s)
    mp_h = int(10 * s)
    draw.ellipse(
        [mp_x - mp_w, slide_top - mp_h // 2, mp_x, slide_top + slide_h + mp_h // 2],
        fill=(180, 140, 30, 200),
    )

    # Slide brace (the crossbar)
    brace_x = cx - int(30 * s)
    brace_w = int(60 * s)
    draw.rectangle(
        [brace_x, slide_top - int(4 * s), brace_x + brace_w, slide_top + slide_h + int(4 * s)],
        fill=(160, 120, 20, 180),
    )

    # Music notes rising from the bell
    note_positions = [
        (bell_x + int(80 * s), bell_top - int(20 * s), 0.7),
        (bell_x + int(130 * s), bell_top - int(60 * s), 0.5),
        (bell_x + int(60 * s), bell_top - int(90 * s), 0.6),
        (bell_x + int(110 * s), bell_top - int(120 * s), 0.4),
    ]
    for nx, ny, ns in note_positions:
        nr = int(8 * ns * s)
        draw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(255, 215, 0, 150))
        # Stem
        stem_top = ny - int(30 * ns * s)
        draw.line([nx, ny - nr, nx, stem_top], fill=(255, 215, 0, 120), width=max(2, int(3 * ns)))
        # Flag
        if ns > 0.4:
            flag_x = nx + int(2 * ns * s)
            draw.arc(
                [flag_x, stem_top, flag_x + int(20 * ns * s), stem_top + int(15 * ns * s)],
                270, 90,
                fill=(255, 215, 0, 100),
                width=2,
            )


def draw_stage(draw: ImageDraw) -> None:
    """Draw a stage silhouette at the bottom of the image area."""
    # Stage floor
    stage_y = HEIGHT - 600
    draw.rectangle([0, stage_y, WIDTH, HEIGHT], fill=(20, 15, 10, 180))

    # Stage edge highlight
    draw.line([(0, stage_y), (WIDTH, stage_y)], fill=(100, 80, 50, 100), width=3)

    # Floorboards
    for i in range(0, WIDTH, 60):
        draw.line([(i, stage_y), (i, HEIGHT)], fill=(30, 25, 20, 80), width=1)

    # Spotlight cone from above
    spot_cx = WIDTH // 2
    spot_points = []
    for i in range(0, 201):
        t = i / 200
        angle = t * math.pi - math.pi / 2
        r = 500 + t * 300
        x = spot_cx + r * math.cos(angle)
        y = stage_y - 200 + t * 300
        spot_points.append((x, y))
    if len(spot_points) > 2:
        draw.polygon(spot_points, fill=(255, 220, 150, 15))


def draw_club_window(draw: ImageDraw, x: int, y: int) -> None:
    """Draw a small New Orleans club window with warm light."""
    w, h = 120, 160
    # Window frame
    draw.rectangle([x, y, x + w, y + h], fill=(40, 35, 30, 200), outline=(80, 65, 50), width=3)
    # Warm light inside
    draw.rectangle([x + 8, y + 8, x + w - 8, y + h - 8], fill=(255, 200, 100, 40))
    # Window cross
    draw.line([(x + w // 2, y + 8), (x + w // 2, y + h - 8)], fill=(80, 65, 50), width=2)
    draw.line([(x + 8, y + h // 2), (x + w - 8, y + h // 2)], fill=(80, 65, 50), width=2)


def create_cover(title: str, author: str, output_path: Path) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Gradient background: midnight blue to deep purple to warm jazz gold
    for y in range(HEIGHT):
        if y < HEIGHT * 0.3:
            ratio = y / (HEIGHT * 0.3)
            r = int(8 + ratio * 10)
            g = int(5 + ratio * 8)
            b = int(20 + ratio * 15)
        elif y < HEIGHT * 0.6:
            ratio = (y - HEIGHT * 0.3) / (HEIGHT * 0.3)
            r = int(18 + ratio * 30)
            g = int(13 + ratio * 20)
            b = int(35 - ratio * 10)
        elif y < HEIGHT * 0.85:
            ratio = (y - HEIGHT * 0.6) / (HEIGHT * 0.25)
            r = int(48 + ratio * 60)
            g = int(33 + ratio * 50)
            b = int(25 - ratio * 10)
        else:
            ratio = (y - HEIGHT * 0.85) / (HEIGHT * 0.15)
            r = int(108 - ratio * 40)
            g = int(83 - ratio * 30)
            b = int(15 - ratio * 5)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, r), max(0, g), max(0, b)))

    # Dark vignette overlay
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([-300, -300, WIDTH + 300, HEIGHT + 300], fill=(0, 0, 0, 0))
    v_draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(0, 0, 0, 100))
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img)

    # City silhouette — French Quarter rooflines
    rooftops = [
        (0, 500, 120, 700), (100, 450, 100, 700), (180, 550, 80, 700),
        (250, 480, 140, 700), (370, 520, 90, 700), (440, 430, 110, 700),
        (530, 560, 100, 700), (610, 490, 130, 700), (720, 440, 110, 700),
        (810, 530, 90, 700), (880, 460, 120, 700), (980, 500, 100, 700),
        (1060, 420, 130, 700), (1170, 540, 90, 700), (1240, 470, 110, 700),
        (1330, 510, 100, 700), (1410, 450, 120, 700), (1510, 490, 90, 700),
    ]
    for rx, ry, rw, rh in rooftops:
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(10, 8, 12, 200))

    # St. Louis Cathedral spire (center-left)
    spire_base_x = 280
    spire_base_y = 430
    draw.polygon(
        [
            (spire_base_x - 30, spire_base_y + 270),
            (spire_base_x - 30, spire_base_y),
            (spire_base_x - 15, spire_base_y - 60),
            (spire_base_x, spire_base_y - 100),
            (spire_base_x + 15, spire_base_y - 60),
            (spire_base_x + 30, spire_base_y),
            (spire_base_x + 30, spire_base_y + 270),
        ],
        fill=(8, 6, 10, 220),
    )

    # Club windows with warm light scattered through the scene
    club_windows = [
        (150, 620), (500, 580), (850, 640), (1150, 560), (1400, 620),
    ]
    for cx, cy in club_windows:
        draw_club_window(draw, cx, cy)

    # Trombone silhouette center stage
    draw_trombone(draw, WIDTH // 2, 900, scale=1.6)

    # Stage at bottom of image
    draw_stage(draw)

    # Jazz notes scattered across the upper area
    note_positions = [
        (200, 300, 1.5), (400, 250, 1.0), (1100, 320, 1.2),
        (1300, 280, 0.8), (600, 220, 1.1), (900, 200, 0.9),
    ]
    for nx, ny, ns in note_positions:
        nr = int(10 * ns)
        draw.ellipse([nx - nr, ny - nr, nx + nr, ny + nr], fill=(255, 215, 0, 60))
        stem_top = ny - int(40 * ns)
        draw.line([nx, ny + nr, nx, stem_top], fill=(255, 215, 0, 50), width=max(2, int(3 * ns)))

    # Title panel at bottom: dark panel with white text
    panel = Image.new("RGBA", (WIDTH, HEIGHT - TITLE_PANEL_TOP))
    p_draw = ImageDraw.Draw(panel)
    p_draw.rectangle([0, 0, WIDTH, HEIGHT - TITLE_PANEL_TOP], fill=(14, 10, 8, 235))
    # Gold accent border at top of panel
    p_draw.line([(100, 0), (WIDTH - 100, 0)], fill=(212, 175, 55), width=3)
    # Subtle gold line near bottom
    p_draw.line([(100, HEIGHT - TITLE_PANEL_TOP - 30), (WIDTH - 100, HEIGHT - TITLE_PANEL_TOP - 30)], fill=(212, 175, 55, 80), width=1)
    img.paste(panel, (0, TITLE_PANEL_TOP), panel)
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font_size = 90
    author_font_size = 36
    small_font_size = 22

    try:
        title_font = ImageFont.truetype(str(TITLE_FONT_PATH), title_font_size)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
    try:
        author_font = ImageFont.truetype(str(AUTHOR_FONT_PATH), author_font_size)
    except (IOError, OSError):
        author_font = ImageFont.load_default()
    try:
        small_font = ImageFont.truetype(str(SMALL_FONT_PATH), small_font_size)
    except (IOError, OSError):
        small_font = ImageFont.load_default()

    # Location descriptor
    location = "NEW ORLEANS, 1955"
    bbox = draw.textbbox((0, 0), location, font=small_font)
    loc_w = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - loc_w) // 2, TITLE_PANEL_TOP + 25),
        location,
        fill=(212, 175, 55),
        font=small_font,
    )

    # Draw wrapped title in WHITE
    wrapped_title = wrap_title(title, max_chars=14)
    lines = wrapped_title.split("\n")
    total_text_h = 0
    line_heights = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lh = bbox[3] - bbox[1]
        line_heights.append(lh)
        total_text_h += lh
    total_text_h += (len(lines) - 1) * 10

    text_y = TITLE_PANEL_TOP + 70 + (400 - total_text_h) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lw = bbox[2] - bbox[0]
        draw.text(
            ((WIDTH - lw) // 2, text_y),
            line,
            fill=(255, 255, 255),
            font=title_font,
        )
        text_y += line_heights[i] + 10

    # Draw author name in white below title
    author_label = author
    bbox = draw.textbbox((0, 0), author_label, font=author_font)
    aw = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - aw) // 2, TITLE_PANEL_TOP + total_text_h + 100),
        author_label,
        fill=(200, 200, 200),
        font=author_font,
    )

    # Gold decorative line below author
    deco_y = TITLE_PANEL_TOP + total_text_h + 150
    draw.line([(600, deco_y), (1000, deco_y)], fill=(212, 175, 55, 150), width=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    img = img.convert("RGB")
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

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")

    create_cover(title, author, args.out)


if __name__ == "__main__":
    main()