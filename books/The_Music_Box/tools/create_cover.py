#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Music Box."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1600
HEIGHT = 2560


def gradient(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    color_top: tuple[int, int, int],
    color_bottom: tuple[int, int, int],
) -> None:
    for y in range(height):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / height)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / height)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_music_box(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    """Draw an ornate music box at center (cx, cy) with given size."""
    half = size // 2
    # Box body - rosewood color
    box_color = (65, 35, 20)  # dark rosewood
    gold_color = (212, 175, 55)
    lid_color = (80, 45, 25)

    # Main body (rectangle)
    draw.rounded_rectangle(
        [(cx - half, cy - half // 2), (cx + half, cy + half // 2)],
        radius=8,
        fill=box_color,
        outline=gold_color,
        width=3,
    )

    # Lid (slightly elevated, trapezoid-like via rounded rect)
    lid_top = cy - half // 2 - size // 6
    draw.rounded_rectangle(
        [(cx - half + 10, lid_top), (cx + half - 10, cy - half // 2)],
        radius=6,
        fill=lid_color,
        outline=gold_color,
        width=2,
    )

    # Gold keyhole / winding key detail
    key_x = cx
    key_y = lid_top - 8
    draw.ellipse(
        [(key_x - 6, key_y - 6), (key_x + 6, key_y + 6)],
        fill=gold_color,
        outline=(180, 140, 30),
        width=1,
    )
    # Key stem
    draw.line([(key_x, key_y - 6), (key_x, key_y - 20)], fill=gold_color, width=3)
    draw.ellipse(
        [(key_x - 4, key_y - 24), (key_x + 4, key_y - 18)],
        fill=gold_color,
    )

    # Gold inlay lines on body
    inset = 15
    draw.line(
        [(cx - half + inset, cy - 10), (cx + half - inset, cy - 10)],
        fill=gold_color,
        width=1,
    )
    draw.line(
        [(cx - half + inset, cy + 10), (cx + half - inset, cy + 10)],
        fill=gold_color,
        width=1,
    )

    # Brass drum visible (partial circle at top of body)
    drum_cy = cy - half // 4
    draw.ellipse(
        [(cx - half // 3, drum_cy - 12), (cx + half // 3, drum_cy + 12)],
        fill=(180, 160, 100),
        outline=gold_color,
        width=1,
    )
    # Teeth on drum
    for i in range(-4, 5):
        tx = cx + i * 12
        draw.line(
            [(tx, drum_cy - 14), (tx, drum_cy + 14)],
            fill=(140, 120, 70),
            width=2,
        )


def draw_sheet_music(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    """Draw a sheet music page."""
    # Page
    draw.rectangle(
        [(x, y), (x + width, y + height)],
        fill=(245, 240, 230),
        outline=(180, 170, 150),
        width=1,
    )
    # Staff lines
    staff_y = y + 20
    staff_spacing = 6
    note_color = (40, 35, 30)
    for staff in range(3):
        for line in range(5):
            ly = staff_y + line * staff_spacing
            draw.line(
                [(x + 15, ly), (x + width - 15, ly)],
                fill=(120, 110, 90),
                width=1,
            )
        # Treble clef (simplified)
        clef_x = x + 20
        clef_y = staff_y + 8
        draw.text((clef_x, clef_y - 10), "\U0001d11e", fill=note_color, font_size=20)
        # Some note dots
        for ni, nx in enumerate([x + 50, x + 100, x + 150, x + 200]):
            ny = staff_y + staff_spacing * (ni % 5)
            draw.ellipse([(nx, ny - 3), (nx + 6, ny + 3)], fill=note_color)
            # Stem
            draw.line([(nx + 6, ny), (nx + 6, ny - 18)], fill=note_color, width=1)
        staff_y += 40


def draw_piano_keys(draw: ImageDraw.ImageDraw, x: int, y: int, num_keys: int, key_width: int, key_height: int) -> None:
    """Draw piano keyboard section."""
    white_key_color = (245, 242, 235)
    black_key_color = (25, 20, 15)
    outline_color = (100, 95, 85)

    for i in range(num_keys):
        kx = x + i * key_width
        draw.rectangle(
            [(kx, y), (kx + key_width - 1, y + key_height)],
            fill=white_key_color,
            outline=outline_color,
            width=1,
        )
        # Black keys (simplified pattern)
        if i % 7 not in (2, 6):
            draw.rectangle(
                [(kx + key_width - key_width // 3, y),
                 (kx + key_width + key_width // 3, y + key_height * 3 // 5)],
                fill=black_key_color,
            )


def draw_therapy_room_elements(draw: ImageDraw.ImageDraw) -> None:
    """Draw subtle therapy room elements in the background."""
    # A window with soft light
    win_x, win_y = 1200, 300
    win_w, win_h = 250, 350
    draw.rectangle(
        [(win_x, win_y), (win_x + win_w, win_y + win_h)],
        fill=(100, 110, 140),
        outline=(80, 85, 100),
        width=2,
    )
    # Window cross
    draw.line(
        [(win_x + win_w // 2, win_y), (win_x + win_w // 2, win_y + win_h)],
        fill=(60, 65, 80),
        width=2,
    )
    draw.line(
        [(win_x, win_y + win_h // 2), (win_x + win_w, win_y + win_h // 2)],
        fill=(60, 65, 80),
        width=2,
    )
    # Soft light glow
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for r in range(80, 0, -4):
        alpha = max(0, 20 - r // 4)
        glow_draw.ellipse(
            [(win_x + win_w // 2 - r, win_y + win_h // 2 - r),
             (win_x + win_w // 2 + r, win_y + win_h // 2 + r)],
            fill=(200, 210, 240, alpha),
        )
    draw._image.paste(glow, (0, 0), glow)



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
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path, default=Path("The_Music_Box/covers/The_Music_Box.png"))
    args = parser.parse_args()

    title = "The Music Box"
    author = "Barış Kısır"

    if args.metadata:
        meta = json.loads(args.metadata.read_text(encoding="utf-8"))
        title = meta.get("title", title)
        author = meta.get("author", author)

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Background gradient: dark psychological suspense palette
    gradient(draw, WIDTH, HEIGHT, (20, 15, 35), (45, 30, 50))
    # Add a deep burgundy accent gradient at the bottom
    for y in range(1800, HEIGHT):
        factor = (y - 1800) / 760
        r = int(45 + (65 - 45) * factor)
        g = int(30 + (20 - 30) * factor)
        b = int(50 + (40 - 50) * factor)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Subtle background texture - faint circles
    for i in range(20):
        cx = (i * 300 + 100) % WIDTH
        cy = (i * 200 + 50) % 1700
        r = 80 + i * 10
        draw.ellipse(
            [(cx - r, cy - r), (cx + r, cy + r)],
            outline=(60, 50, 70, 30),
            width=1,
        )

    # Therapy room elements
    draw_therapy_room_elements(draw)

    # Sheet music - left side, floating
    draw_sheet_music(draw, 60, 400, 200, 260)

    # Piano keys - bottom section of the imagery area
    draw_piano_keys(draw, 150, 1100, 18, 35, 120)

    # More sheet music - right side
    draw_sheet_music(draw, 1200, 550, 200, 260)

    # Music box - center, prominent
    draw_music_box(draw, WIDTH // 2, 700, 250)

    # Rose and vine decorative elements
    vine_color = (80, 120, 60)
    rose_color = (160, 40, 50)
    # Vines around music box
    for angle in range(0, 360, 30):
        rad = math.radians(angle)
        vx = WIDTH // 2 + int(200 * math.cos(rad))
        vy = 700 + int(180 * math.sin(rad))
        # Small leaves
        draw.ellipse(
            [(vx - 4, vy - 8), (vx + 4, vy)],
            fill=vine_color,
        )
        if angle % 60 == 0:
            # Small rose
            draw.ellipse(
                [(vx - 6, vy - 6), (vx + 6, vy + 6)],
                fill=rose_color,
            )

    # Gold ornamental lines
    gold_color = (180, 140, 50)
    for x_pos in [200, WIDTH - 200]:
        draw.line(
            [(x_pos, 1300), (x_pos + 80, 1350)],
            fill=gold_color,
            width=1,
        )
        draw.line(
            [(x_pos, 1300), (x_pos + 80, 1250)],
            fill=gold_color,
            width=1,
        )

    # Title panel at bottom (y=1920-2560)
    panel_top = 1920
    panel_height = HEIGHT - panel_top

    # Dark semi-transparent panel
    panel = Image.new("RGBA", (WIDTH, panel_height), (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rectangle(
        [(0, 0), (WIDTH, panel_height)],
        fill=(10, 8, 15, 220),
    )
    # Gold top border
    panel_draw.line(
        [(0, 0), (WIDTH, 0)],
        fill=gold_color,
        width=3,
    )
    img.paste(panel, (0, panel_top), panel)

    # Load fonts
    font_dir = Path("C:/Windows/Fonts")
    title_font_path = font_dir / "arialbd.ttf"
    author_font_path = font_dir / "arial.ttf"

    title_font = ImageFont.truetype(str(title_font_path), 72)
    author_font = ImageFont.truetype(str(author_font_path), 36)

    # Draw title centered in the panel
    title_y = panel_top + 60
    bbox = draw.textbbox((0, 0), title, font=title_font)
    title_w = bbox[2] - bbox[0]
    title_x = (WIDTH - title_w) // 2
    draw.text((title_x, title_y), title, fill=(255, 255, 255), font=title_font)

    # Gold decorative line under title
    line_y = title_y + 100
    draw.line(
        [(WIDTH // 2 - 100, line_y), (WIDTH // 2 + 100, line_y)],
        fill=gold_color,
        width=2,
    )

    # Author below title
    author_y = line_y + 30
    bbox2 = draw.textbbox((0, 0), author, font=author_font)
    author_w = bbox2[2] - bbox2[0]
    author_x = (WIDTH - author_w) // 2
    draw.text((author_x, author_y), author, fill=(200, 195, 190), font=author_font)

    # Save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()