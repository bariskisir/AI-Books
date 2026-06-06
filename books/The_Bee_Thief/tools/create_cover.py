#!/usr/bin/env python3
"""Create cover image for The Bee Thief — Rural Noir."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


WIDTH, HEIGHT = 1600, 2560
OUT = Path(__file__).resolve().parents[3] / "books" / "The_Bee_Thief" / "covers" / "The_Bee_Thief.png"


def gradient(draw: ImageDraw, top: tuple[int, int, int], bottom: tuple[int, int, int]) -> None:
    for y in range(HEIGHT):
        r = int(top[0] + (bottom[0] - top[0]) * y / HEIGHT)
        g = int(top[1] + (bottom[1] - top[1]) * y / HEIGHT)
        b = int(top[2] + (bottom[2] - top[2]) * y / HEIGHT)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_field(draw: ImageDraw) -> None:
    # Rollings fields in gold/brown
    colors = [(180, 130, 60), (160, 110, 40), (140, 90, 30)]
    for i, y_base in enumerate([1400, 1550, 1700]):
        c = colors[i % len(colors)]
        for x in range(0, WIDTH, 8):
            h = 50 + int(30 * (x / WIDTH))
            y = y_base + int(20 * (x / WIDTH))
            draw.rectangle([x, y, x + 4, y + h], fill=c)


def draw_hive(draw: ImageDraw, x: int, y: int, dead: bool = True) -> None:
    # Hive body
    bw, bh = 120, 90
    base_color = (160, 130, 80) if dead else (200, 170, 100)
    draw.rectangle([x, y, x + bw, y + bh], fill=base_color, outline=(80, 60, 30), width=2)

    # Hive entrance at bottom
    entrance_color = (40, 30, 15) if dead else (60, 50, 30)
    draw.rectangle([x + 35, y + bh - 18, x + 85, y + bh - 6], fill=entrance_color)

    if dead:
        # Skull-and-crossbones style X for dead hive
        draw.line([(x + 20, y + 20), (x + 100, y + 70)], fill=(80, 30, 15), width=3)
        draw.line([(x + 100, y + 20), (x + 20, y + 70)], fill=(80, 30, 15), width=3)
    else:
        # Small dots for bees
        for _ in range(6):
            bx = x + 40 + (_ * 12)
            by = y + 30 + (_ % 3) * 15
            draw.ellipse([bx, by, bx + 6, by + 6], fill=(220, 180, 40))


def draw_single_bee(draw: ImageDraw, x: int, y: int) -> None:
    # Body
    draw.ellipse([x - 8, y - 4, x + 8, y + 4], fill=(200, 160, 40))
    # Stripes
    draw.rectangle([x - 2, y - 4, x + 2, y + 4], fill=(30, 20, 10))
    draw.rectangle([x - 6, y - 4, x - 4, y + 4], fill=(30, 20, 10))
    draw.rectangle([x + 4, y - 4, x + 6, y + 4], fill=(30, 20, 10))
    # Wings
    draw.ellipse([x - 10, y - 12, x - 2, y - 4], fill=(200, 210, 230, 160))
    draw.ellipse([x + 2, y - 12, x + 10, y - 4], fill=(200, 210, 230, 160))
    # Flight trail
    for i in range(6):
        tx = x - (i + 1) * 10
        ty = y + (i % 3) * 5 - 5
        draw.ellipse([tx - 1, ty - 1, tx + 1, ty + 1], fill=(220, 190, 80, 120))


def draw_title_panel(draw: ImageDraw) -> None:
    # Dark panel at bottom
    draw.rectangle([0, 1920, WIDTH, 2560], fill=(30, 20, 10))

    try:
        font_title = ImageFont.truetype("arialbd.ttf", 80)
        font_author = ImageFont.truetype("arialbd.ttf", 36)
    except (IOError, OSError):
        font_title = ImageFont.load_default()
        font_author = ImageFont.load_default()

    # Title text
    title = "THE BEE THIEF"
    bbox = draw.textbbox((0, 0), title, font=font_title)
    tw = bbox[2] - bbox[0]
    tx = (WIDTH - tw) // 2
    draw.text((tx, 2040), title, fill=(255, 255, 255), font=font_title)

    # Author text
    author = "Barış Kısır"
    bbox = draw.textbbox((0, 0), author, font=font_author)
    aw = bbox[2] - bbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax, 2180), author, fill=(200, 180, 120), font=font_author)

    # Genre line
    genre = "Rural Noir"
    try:
        font_genre = ImageFont.truetype("arialbd.ttf", 24)
    except (IOError, OSError):
        font_genre = ImageFont.load_default()
    bbox = draw.textbbox((0, 0), genre, font=font_genre)
    gw = bbox[2] - bbox[0]
    gx = (WIDTH - gw) // 2
    draw.text((gx, 2260), genre, fill=(160, 140, 80), font=font_genre)



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
    parser.add_argument("--metadata", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()

    if args.metadata:
        meta = json.loads(args.metadata.read_text(encoding="utf-8"))
        title = meta.get("title", "The Bee Thief")
    else:
        title = "The Bee Thief"

    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background: dark brown sky to gold fields
    gradient(draw, top=(60, 40, 20), bottom=(180, 140, 60))

    # Sun / moon glow
    draw.ellipse([600, 200, 1000, 600], fill=(220, 190, 120, 80))

    # Distant fields
    draw_field(draw)

    # Dead hives
    draw_hive(draw, 200, 1000, dead=True)
    draw_hive(draw, 500, 1050, dead=True)
    draw_hive(draw, 800, 1020, dead=True)
    draw_hive(draw, 1100, 1060, dead=True)

    # Scattered dead hives in distance
    draw_hive(draw, 100, 1200, dead=True)
    draw_hive(draw, 1300, 1180, dead=True)

    # Single bee flying
    draw_single_bee(draw, 850, 500)

    # Title panel
    draw_title_panel(draw)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()
