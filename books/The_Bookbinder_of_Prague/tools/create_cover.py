#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Bookbinder of Prague."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

WIDTH, HEIGHT = 1600, 2560
DARK_PANEL_COLOR = (20, 16, 12)
TEXT_WHITE = (245, 242, 238)
GOLD_COLOR = (212, 175, 55)

FONT_PATH = "C:/Windows/Fonts/arialbd.ttf"


def draw_gradient(draw: ImageDraw.Draw) -> None:
    """Vertical sepia gradient background."""
    for y in range(HEIGHT):
        blend = y / HEIGHT
        r = int(30 * (1 - blend) + 70 * blend)
        g = int(25 * (1 - blend) + 40 * blend)
        b = int(18 * (1 - blend) + 25 * blend)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_prague_skyline(draw: ImageDraw.Draw) -> None:
    """Stylized Prague skyline silhouette with St. Vitus Cathedral and bridge."""
    spire_color = (15, 12, 8)
    cx = WIDTH // 2
    base_y = 1400

    # Cathedral spires
    draw.polygon([(cx - 30, base_y), (cx, 600), (cx + 30, base_y)], fill=spire_color)
    draw.rectangle([cx - 40, base_y - 200, cx + 40, base_y], fill=spire_color)
    draw.polygon([(cx - 100, base_y), (cx - 70, 750), (cx - 40, base_y)], fill=spire_color)
    draw.polygon([(cx + 40, base_y), (cx + 70, 750), (cx + 100, base_y)], fill=spire_color)
    draw.rectangle([cx - 130, base_y - 350, cx + 130, base_y], fill=spire_color)

    # Rose window
    draw.ellipse([cx - 30, base_y - 280, cx + 30, base_y - 220], fill=(25, 20, 15))
    draw.ellipse([cx - 25, base_y - 275, cx + 25, base_y - 225], fill=(60, 50, 35))

    # Roof line
    for x in range(cx - 200, cx + 201, 40):
        peak = base_y - 100 if abs(x - cx) > 130 else base_y - 350
        draw.polygon([(x - 15, base_y), (x, peak), (x + 15, base_y)], fill=spire_color)

    # Bridge towers
    for bx, by in [(280, 1250), (1320, 1250)]:
        draw.rectangle([bx - 25, by - 180, bx + 25, by], fill=spire_color)
        draw.polygon([(bx - 20, by - 180), (bx, by - 240), (bx + 20, by - 180)], fill=spire_color)
        draw.rectangle([bx - 10, by - 60, bx + 10, by], fill=(25, 20, 15))

    # Bridge
    draw.rectangle([150, 1280, WIDTH - 150, 1295], fill=spire_color)

    # Small buildings along the bridge
    for i in range(8):
        bx = 350 + i * 120
        bh = 60 + (i % 3) * 20
        draw.rectangle([bx - 20, 1295 - bh, bx + 20, 1295], fill=spire_color)

    # Lower city buildings
    for i in range(12):
        bx = 100 + i * 130
        bh = 120 + (i % 4) * 30
        draw.rectangle([bx - 30, 1400 - bh, bx + 30, 1400], fill=spire_color)


def draw_books_and_tools(draw: ImageDraw.Draw) -> None:
    """Stacked books and binding tools in the foreground."""
    book_colors = [
        (110, 40, 30), (55, 70, 50), (80, 55, 60),
        (60, 45, 30), (95, 35, 40), (45, 55, 65),
    ]

    # Left book stack
    bx, by = 200, 1330
    for i in range(7):
        bw = 160 + i * 10
        bh = 28 + i * 3
        color = book_colors[i % len(book_colors)]
        draw.rectangle([bx - bw // 2, by - bh, bx + bw // 2, by], fill=color)
        draw.rectangle([bx - bw // 2 + 5, by - bh + 4, bx - bw // 2 + 12, by - 4], fill=GOLD_COLOR)
        by -= bh - 3

    # Right book stack
    bx2, by2 = WIDTH - 200, 1350
    for i in range(6):
        bw = 140 + i * 8
        bh = 25 + i * 3
        color = book_colors[(i + 3) % len(book_colors)]
        draw.rectangle([bx2 - bw // 2, by2 - bh, bx2 + bw // 2, by2], fill=color)
        draw.rectangle([bx2 - bw // 2 + 5, by2 - bh + 4, bx2 - bw // 2 + 12, by2 - 4], fill=GOLD_COLOR)
        by2 -= bh - 3

    # Bone folder tool
    draw.line([(600, 1530), (720, 1380)], fill=(80, 72, 60), width=8)
    draw.line([(720, 1380), (740, 1355)], fill=(80, 72, 60), width=6)

    # Thread spool
    draw.ellipse([(800, 1480), (840, 1520)], fill=(160, 140, 110))
    draw.ellipse([(808, 1488), (832, 1512)], fill=(70, 60, 45))
    draw.line([(840, 1500), (920, 1430)], fill=(200, 190, 170), width=2)


def draw_parchment(draw: ImageDraw.Draw) -> None:
    """Open parchment scroll with text marks."""
    sx, sy = WIDTH // 2, 1680
    sw, sh = 520, 130

    draw.rectangle([sx - sw // 2, sy - sh // 2, sx + sw // 2, sy + sh // 2], fill=(210, 190, 160))
    draw.ellipse([sx - sw // 2 - 15, sy - sh // 2, sx - sw // 2 + 15, sy + sh // 2], fill=(180, 160, 130))
    draw.ellipse([sx + sw // 2 - 15, sy - sh // 2, sx + sw // 2 + 15, sy + sh // 2], fill=(180, 160, 130))

    for i in range(8):
        ly = sy - sh // 2 + 14 + i * 14
        draw.line([(sx - 210, ly), (sx + 210, ly)], fill=(100, 85, 65), width=2)

    # Hebrew letters on parchment
    letters = ["א", "ב", "ד", "ה", "ו", "ז"]
    for i, letter in enumerate(letters):
        draw.text((sx - 180 + i * 70, sy - 30), letter, fill=(80, 65, 45))


def draw_border(draw: ImageDraw.Draw) -> None:
    """Tooled leather ornamental border."""
    margin = 40
    draw.rectangle([margin, margin, WIDTH - margin, HEIGHT - margin], outline=(55, 45, 35), width=4)
    draw.rectangle([margin + 14, margin + 14, WIDTH - margin - 14, HEIGHT - margin - 14], outline=(55, 45, 35), width=1)

    for cx, cy in [
        (margin + 7, margin + 7), (WIDTH - margin - 7, margin + 7),
        (margin + 7, HEIGHT - margin - 7), (WIDTH - margin - 7, HEIGHT - margin - 7),
    ]:
        draw.rectangle([cx - 5, cy - 5, cx + 5, cy + 5], fill=GOLD_COLOR)

    # Gold filigree corners
    for ox, oy in [(margin + 20, margin + 20), (WIDTH - margin - 20, margin + 20),
                   (margin + 20, HEIGHT - margin - 20), (WIDTH - margin - 20, HEIGHT - margin - 20)]:
        draw.arc([ox - 30, oy - 30, ox + 30, oy + 30], 0, 90, fill=GOLD_COLOR, width=2)


def draw_title_panel(draw: ImageDraw.Draw) -> None:
    """Dark bottom panel with title and author."""
    panel_top = 1920
    draw.rectangle([0, panel_top, WIDTH, HEIGHT], fill=DARK_PANEL_COLOR)

    # Gold decorative lines
    for offset in [0, 3]:
        draw.line([(60, panel_top + offset), (WIDTH - 60, panel_top + offset)], fill=GOLD_COLOR, width=2 - offset)

    try:
        title_font = ImageFont.truetype(FONT_PATH, 80)
        author_font = ImageFont.truetype(FONT_PATH, 40)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    title = "The Bookbinder"
    subtitle = "of Prague"
    author = "Barış Kısır"

    bbox1 = draw.textbbox((0, 0), title, font=title_font)
    tx1 = (WIDTH - (bbox1[2] - bbox1[0])) // 2
    ty1 = panel_top + 60

    bbox2 = draw.textbbox((0, 0), subtitle, font=title_font)
    tx2 = (WIDTH - (bbox2[2] - bbox2[0])) // 2
    ty2 = ty1 + 95

    draw.text((tx1, ty1), title, fill=TEXT_WHITE, font=title_font)
    draw.text((tx2, ty2), subtitle, fill=TEXT_WHITE, font=title_font)

    line_y = ty2 + 90
    draw.line([(WIDTH // 2 - 120, line_y), (WIDTH // 2 + 120, line_y)], fill=GOLD_COLOR, width=1)

    bbox3 = draw.textbbox((0, 0), author, font=author_font)
    ax = (WIDTH - (bbox3[2] - bbox3[0])) // 2
    draw.text((ax, line_y + 25), author, fill=GOLD_COLOR, font=author_font)


def apply_vignette(img: Image.Image) -> Image.Image:
    """Apply a subtle vignette darkening the edges using blurred radial gradient."""
    vignette = Image.new("L", (WIDTH, HEIGHT), 180)
    v_draw = ImageDraw.Draw(vignette)
    cx, cy = WIDTH // 2, HEIGHT // 2
    v_draw.ellipse([cx - 800, cy - 800, cx + 800, cy + 800], fill=0)
    vignette = vignette.filter(ImageFilter.GaussianBlur(radius=200))
    dark = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    return Image.composite(img, dark, vignette)


def create_cover() -> Image.Image:
    """Create the full cover image."""
    img = Image.new("RGB", (WIDTH, HEIGHT), (30, 25, 18))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw)
    draw_prague_skyline(draw)
    draw_books_and_tools(draw)
    draw_parchment(draw)
    draw_border(draw)
    draw_title_panel(draw)

    img = apply_vignette(img)
    return img



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
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    cover = create_cover()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(cover, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    cover.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()