#!/usr/bin/env python3
"""Create a custom cover for The Glass Harp."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
PANEL_Y = 1765
FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    path = FONT_DIR / name
    if path.exists():
        return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def draw_concert_hall(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.48:
            c = lerp((13, 18, 28), (39, 49, 67), t / 0.48)
        else:
            c = lerp((39, 49, 67), (12, 10, 15), (t - 0.48) / 0.52)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Concert hall shell and warm stage.
    draw.polygon([(150, 1500), (1450, 1500), (1250, 520), (350, 520)], fill=(44, 30, 34, 245), outline=(144, 109, 84, 150))
    draw.polygon([(280, 1510), (1320, 1510), (1130, 835), (470, 835)], fill=(171, 112, 66, 220))
    for i in range(18):
        y = 840 + i * 36
        draw.arc((240 + i * 5, y, 1360 - i * 5, y + 260), 200, 340, fill=(96, 60, 45, 95), width=4)

    # Suspended glass acoustic canopy, with one fractured section.
    canopy = [(315, 430), (1285, 380), (1390, 665), (225, 730)]
    draw.polygon(canopy, fill=(174, 208, 220, 92), outline=(225, 238, 232, 185))
    for x in range(345, 1300, 120):
        draw.line((x, 415, x + 120, 700), fill=(235, 244, 226, 120), width=5)
    broken = [(835, 405), (1010, 398), (1048, 552), (956, 623), (880, 560)]
    draw.polygon(broken, fill=(40, 50, 62, 170), outline=(240, 250, 236, 210))
    for _ in range(38):
        x = random.randint(835, 1050)
        y = random.randint(430, 675)
        draw.line((x, y, x + random.randint(-55, 55), y + random.randint(35, 120)), fill=(231, 246, 240, random.randint(75, 160)), width=random.randint(2, 5))

    # Falling glass fragments over the stage.
    for _ in range(90):
        cx = random.randint(500, 1120)
        cy = random.randint(725, 1320)
        size = random.randint(8, 32)
        pts = [(cx, cy), (cx + random.randint(-size, size), cy + random.randint(5, size * 2)), (cx + random.randint(-size, size), cy + random.randint(-size, size))]
        draw.polygon(pts, fill=(197, 232, 235, random.randint(55, 125)), outline=(240, 248, 238, random.randint(45, 120)))

    # Frequency graph across the hall, with one dangerous spike.
    graph = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(graph, "RGBA")
    base = 1185
    prev = None
    for i in range(180):
        x = 135 + i * 7
        amp = 30 * math.sin(i * 0.22) + 14 * math.sin(i * 0.61)
        if 91 <= i <= 98:
            amp -= 330 * (1 - abs(i - 94.5) / 4.5)
        y = base + amp
        if prev:
            gd.line((prev[0], prev[1], x, y), fill=(245, 218, 116, 210), width=7)
        prev = (x, y)
    graph = graph.filter(ImageFilter.GaussianBlur(0.7))
    draw.bitmap((0, 0), graph, fill=None)

    # Music stand and altered score.
    draw.rectangle((510, 1320, 1090, 1510), fill=(232, 226, 200, 238), outline=(72, 58, 48, 180), width=4)
    staff_y = 1360
    for row in range(5):
        draw.line((555, staff_y + row * 18, 1042, staff_y + row * 18), fill=(42, 42, 48, 210), width=3)
    for x in (640, 760, 860):
        draw.ellipse((x, 1405, x + 26, 1424), fill=(32, 32, 38, 225))
        draw.line((x + 24, 1413, x + 24, 1342), fill=(32, 32, 38, 225), width=4)
    draw.line((930, 1350, 930, 1460), fill=(155, 18, 30, 240), width=7)
    draw.text((948, 1368), "sustained note", font=font("arial.ttf", 31), fill=(120, 28, 34, 230))

    # Cable lines and empty seats.
    for x in range(370, 1260, 145):
        draw.line((x, 0, x + 80, 430), fill=(214, 220, 204, 80), width=3)
    for row in range(9):
        y = 1510 - row * 54
        for col in range(13 - row // 2):
            x = 205 + col * 92 + row * 22
            draw.ellipse((x, y, x + 58, y + 28), fill=(35, 20, 24, 210), outline=(116, 70, 54, 90))

    tagline = "ACOUSTICS  GLASS  HIDDEN RESONANCE"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 275), tagline, font=tag_font, fill=(231, 220, 180, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Glass Harp")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("the-glass-harp-cover")
    image = Image.new("RGBA", (W, H), (14, 14, 18, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_concert_hall(draw)
    _draw_standard_cover_title_panel(
        image,
        _standard_cover_resolve_title(locals()),
        _standard_cover_resolve_author(locals()),
        model,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "PNG", optimize=True)


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


def _draw_standard_cover_title_panel(image, title: str = "", author: str = "", model: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    model = _standard_cover_repair_text(str(model or "")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(235, 231, 219, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(78, 84, 96, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (44, 48, 56), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (82, 80, 74), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (112, 108, 98), 6, width)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
