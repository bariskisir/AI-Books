#!/usr/bin/env python3
"""Create a book-specific cover for The Bureau of Small Miracles."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560
FONT_DIR = Path("C:/Windows/Fonts")


def font(name: str, size: int):
    for candidate in (FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"):
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def draw_bureau_scene(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-bureau-of-small-miracles-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(38*(1-t)+21*t), int(53*(1-t)+39*t), int(64*(1-t)+47*t), 255))

    # Bureau windows and public counter.
    draw.rectangle((0, 1240, W, 1765), fill=(45, 56, 60, 240))
    for i, x in enumerate(range(160, 1320, 230)):
        draw.rounded_rectangle((x, 360, x+165, 1030), radius=12, fill=(226, 220, 184, 235), outline=(92, 104, 101, 210), width=5)
        draw.rectangle((x+20, 420, x+145, 980), fill=(35, 53, 61, 245))
        draw.line((x+82, 420, x+82, 980), fill=(226, 220, 184, 100), width=3)
        draw.line((x+20, 700, x+145, 700), fill=(226, 220, 184, 100), width=3)
    draw.rounded_rectangle((145, 1260, 1455, 1600), radius=22, fill=(211, 203, 174, 240), outline=(85, 74, 55, 220), width=7)
    draw.text((210, 1300), "PUBLIC LEDGER", font=font("arialbd.ttf", 46), fill=(54, 55, 50, 230))

    # Ledger rows.
    rows = [("NEED", "OPEN"), ("REPAIR", "APPROVED"), ("BEAUTY", "WAIT"), ("MERCY", "FIRST")]
    for idx, (left, right) in enumerate(rows):
        y = 1375 + idx*48
        draw.line((205, y+38, 1390, y+38), fill=(107, 98, 76, 100), width=2)
        draw.text((225, y), left, font=font("arialbd.ttf", 30), fill=(61, 62, 55, 220))
        draw.text((1050, y), right, font=font("arial.ttf", 30), fill=(61, 62, 55, 220))

    # Bottled sparks in cabinet.
    cab = (565, 610, 1035, 1180)
    draw.rounded_rectangle(cab, radius=18, fill=(28, 39, 46, 245), outline=(156, 132, 83, 220), width=8)
    draw.text((625, 645), "CABINET 7", font=font("arialbd.ttf", 38), fill=(225, 205, 136, 230))
    for row in range(3):
        for col in range(4):
            x = 635 + col*90
            y = 735 + row*125
            draw.rounded_rectangle((x, y, x+48, y+86), radius=16, fill=(196, 213, 206, 80), outline=(221, 229, 205, 180), width=3)
            cx, cy = x+24, y+45
            glow = Image.new("RGBA", (W, H), (0,0,0,0))
            gd = ImageDraw.Draw(glow, "RGBA")
            gd.ellipse((cx-38, cy-38, cx+38, cy+38), fill=(255, 221, 98, 35))
            draw.bitmap((0,0), glow.filter(ImageFilter.GaussianBlur(10)), fill=None)
            draw.ellipse((cx-8, cy-8, cx+8, cy+8), fill=(255, 226, 119, 235))

    # Miracle clocks.
    for x, label, color in [(250, "MARKET", (212, 94, 73)), (1210, "LUXURY", (87, 176, 151))]:
        draw.ellipse((x-135, 740, x+135, 1010), fill=(220, 213, 185, 235), outline=(96, 86, 64, 220), width=8)
        draw.text((x-72, 1030), label, font=font("arialbd.ttf", 29), fill=(226, 220, 184, 220))
        draw.line((x, 875, x+72, 835), fill=(54, 54, 48, 230), width=7)
        draw.line((x, 875, x-22, 785), fill=(54, 54, 48, 230), width=7)
        draw.arc((x-105, 770, x+105, 980), 40, 320, fill=color+(230,), width=8)

    # Forms and stamps.
    draw.polygon([(300, 1110), (535, 1160), (500, 1310), (260, 1260)], fill=(239, 234, 209, 230), outline=(91, 83, 66, 170))
    draw.text((325, 1160), "FORM 12-B", font=font("arialbd.ttf", 30), fill=(62, 58, 52, 230))
    draw.rounded_rectangle((1080, 1135, 1325, 1240), radius=18, outline=(174, 54, 49, 220), width=7)
    draw.text((1110, 1168), "DENIED", font=font("arialbd.ttf", 42), fill=(174, 54, 49, 220))

    # Floating sparks.
    for _ in range(160):
        x = random.randint(110, 1490)
        y = random.randint(230, 1510)
        s = random.randint(2, 6)
        draw.ellipse((x, y, x+s, y+s), fill=(255, 224, 119, random.randint(55, 170)))

    tagline = "BUREAUCRATIC FANTASY  CIVIC MERCY  PUBLIC LEDGERS"
    tag_font = font("georgia.ttf", 35)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(238, 226, 174, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Bureau of Small Miracles")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (28, 38, 46, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_bureau_scene(draw)
    _draw_standard_cover_title_panel(image, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "PNG", optimize=True)


def _standard_cover_font(name: str, size: int):
    font_dir = globals().get("FONT_DIR", globals().get("FONTS_DIR", None))
    candidates = []
    if font_dir is not None:
        candidates.append(Path(font_dir) / name)
    candidates.extend([Path("C:/Windows/Fonts") / name, Path("C:/Windows/Fonts") / "arialbd.ttf", Path("C:/Windows/Fonts") / "arial.ttf"])
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
    return "Bar\u0131\u015f K\u0131s\u0131r"


def _draw_standard_cover_title_panel(image, title: str = "", author: str = "", model: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Bar\u0131\u015f K\u0131s\u0131r")).strip()
    model = _standard_cover_repair_text(str(model or "")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(230, 224, 201, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(72, 88, 86, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (40, 54, 58), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (74, 82, 76), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (104, 108, 96), 6, width)


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
