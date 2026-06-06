#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Last Telegram."""

from __future__ import annotations

import argparse
import json
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920
FONTS_DIR = Path("C:/Windows/Fonts")
TITLE_FONT_PATH = FONTS_DIR / "georgiab.ttf"
AUTHOR_FONT_PATH = FONTS_DIR / "arialbd.ttf"
SMALL_FONT_PATH = FONTS_DIR / "arial.ttf"


def wrap_title(title: str, max_chars: int = 14) -> str:
    return "\n".join(textwrap.wrap(title, width=max_chars))


def draw_morse(draw: ImageDraw, x: int, y: int, scale: float = 1.0) -> None:
    """Draw a decorative Morse code pattern."""
    dots = [(0, 0), (2, 0), (0, 1), (2, 2), (1, 3)]
    dashes = [(5, 0), (7, 0), (5, 1), (7, 2), (7, 3)]
    for dx, dy in dots:
        cx = x + int(dx * 6 * scale)
        cy = y + int(dy * 6 * scale)
        draw.ellipse([cx, cy, cx + int(4 * scale), cy + int(4 * scale)], fill=(220, 200, 170, 60))
    for dx, dy in dashes:
        rx = x + int(dx * 6 * scale)
        ry = y + int(dy * 6 * scale)
        rw = int(12 * scale)
        rh = int(4 * scale)
        draw.rectangle([rx, ry, rx + rw, ry + rh], fill=(220, 200, 170, 60))


def draw_telegram_machine(draw: ImageDraw, cx: int, base_y: int) -> None:
    """Draw a simplified telegram / teleprinter machine."""
    # Main body
    body_w, body_h = 300, 160
    x1 = cx - body_w // 2
    y1 = base_y
    draw.rectangle([x1, y1, x1 + body_w, y1 + body_h], fill=(60, 55, 50), outline=(140, 130, 110), width=2)

    # Paper feed slot
    slot_w, slot_h = 200, 12
    sx = cx - slot_w // 2
    sy = y1 + 20
    draw.rectangle([sx, sy, sx + slot_w, sy + slot_h], fill=(230, 215, 190))
    # Paper curl
    for i in range(3):
        curl_y = sy + slot_h + 2 + i * 8
        draw.line([sx + 10, curl_y, sx + slot_w - 10, curl_y], fill=(200, 185, 160), width=1)

    # Keys area
    key_area_y = sy + slot_h + 30
    key_w, key_h = 18, 10
    for row in range(4):
        for col in range(12):
            kx = x1 + 15 + col * (key_w + 4)
            ky = key_area_y + row * (key_h + 4)
            draw.rectangle([kx, ky, kx + key_w, ky + key_h], fill=(45, 42, 38), outline=(100, 95, 85))
            if row == 0 and col < 6:
                draw.rectangle([kx + 2, ky + 2, kx + key_w - 2, ky + key_h - 2], fill=(200, 50, 50, 80))

    # Roller at the top
    roller_y = y1 - 10
    draw.rectangle([cx - 120, roller_y, cx + 120, roller_y + 10], fill=(80, 75, 70))


def draw_microphone(draw: ImageDraw, x: int, y: int) -> None:
    """Draw a vintage microphone silhouette."""
    head_r = 20
    draw.ellipse([x - head_r, y - head_r, x + head_r, y + head_r], outline=(140, 130, 110), width=3)
    draw.line([x, y + head_r, x, y + head_r + 40], fill=(140, 130, 110), width=4)
    draw.arc([x - 15, y + 50, x + 15, y + 70], 0, 180, fill=(140, 130, 110), width=2)


def create_cover(title: str, author: str, output_path: Path) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    # Gradient background: navy blue -> deep sepia -> dark brown
    for y in range(HEIGHT):
        if y < HEIGHT * 0.6:
            ratio = y / (HEIGHT * 0.6)
            r = int(10 + ratio * 40)
            g = int(20 + ratio * 25)
            b = int(55 + ratio * 10)
        else:
            ratio = (y - HEIGHT * 0.6) / (HEIGHT * 0.4)
            r = int(50 + ratio * 40)
            g = int(45 + ratio * 20)
            b = int(65 - ratio * 30)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Add subtle vignette overlay
    vignette = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    v_draw = ImageDraw.Draw(vignette)
    v_draw.ellipse([-200, -200, WIDTH + 200, HEIGHT + 200], fill=(0, 0, 0, 0))
    v_draw.rectangle([0, 0, WIDTH, HEIGHT], fill=(0, 0, 0, 120))
    img = Image.alpha_composite(img, vignette)
    draw = ImageDraw.Draw(img)

    # Decorative morse code dots scattered in the upper area
    for i in range(12):
        mx = 100 + (i * 130) % 1400
        my = 200 + (i * 97) % 900
        draw_morse(draw, mx, my, scale=1.2 if i % 2 == 0 else 0.8)

    # Draw telegram machine slightly above center
    machine_cx = WIDTH // 2
    machine_y = 550
    draw_telegram_machine(draw, machine_cx, machine_y)

    # Wavy lines suggesting morse / signal waves
    for wave in range(5):
        wy = 820 + wave * 15
        points = []
        for wx in range(200, 1401, 10):
            phase = (wx - 200) / 30 + wave * 0.8
            wavy = wy + int(8 * (phase % 6 - 3))
            points.append((wx, wavy))
        draw.line(points, fill=(200, 180, 150, 80), width=2)

    # Draw microphone
    draw_microphone(draw, 300, 400)
    draw_microphone(draw, 1300, 350)

    # Grid lines suggesting maps / signals
    for gx in range(0, WIDTH, 80):
        draw.line([(gx, 100), (gx, 700)], fill=(100, 90, 80, 30), width=1)
    for gy in range(100, 701, 60):
        draw.line([(0, gy), (WIDTH, gy)], fill=(100, 90, 80, 30), width=1)

    # Title panel (semi-transparent light rectangle at bottom)
    panel = Image.new("RGBA", (WIDTH, HEIGHT - TITLE_PANEL_TOP))
    p_draw = ImageDraw.Draw(panel)
    p_draw.rectangle([0, 0, WIDTH, HEIGHT - TITLE_PANEL_TOP], fill=(230, 220, 205, 220))
    # Subtle border at top of panel
    p_draw.line([(0, 0), (WIDTH, 0)], fill=(180, 160, 140), width=3)
    img.paste(panel, (0, TITLE_PANEL_TOP), panel)
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font_size = 80
    author_font_size = 40
    small_font_size = 24

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

    # Draw small decorative text "W.R.N.S. Signal Station"
    label = "W.R.N.S. Signal Station -- Shingle Cove"
    bbox = draw.textbbox((0, 0), label, font=small_font)
    label_w = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - label_w) // 2, TITLE_PANEL_TOP + 30),
        label,
        fill=(120, 100, 80),
        font=small_font,
    )

    # Draw wrapped title
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

    text_y = TITLE_PANEL_TOP + 60 + (400 - total_text_h) // 2
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=title_font)
        lw = bbox[2] - bbox[0]
        draw.text(
            ((WIDTH - lw) // 2, text_y),
            line,
            fill=(40, 35, 30),
            font=title_font,
        )
        text_y += line_heights[i] + 10

    # Draw author name
    author_label = f"by {author}"
    bbox = draw.textbbox((0, 0), author_label, font=author_font)
    aw = bbox[2] - bbox[0]
    draw.text(
        ((WIDTH - aw) // 2, TITLE_PANEL_TOP + total_text_h + 90),
        author_label,
        fill=(80, 65, 55),
        font=author_font,
    )

    # Decorative line under title area
    line_y = TITLE_PANEL_TOP + total_text_h + 75
    draw.line([(600, line_y), (1000, line_y)], fill=(140, 120, 100), width=2)

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