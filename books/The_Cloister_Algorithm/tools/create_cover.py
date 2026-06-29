#!/usr/bin/env python3
"""Create a book-specific cover for The Cloister Algorithm."""

from __future__ import annotations

import argparse
import json
import math
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


def draw_cloister_archive(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-cloister-algorithm-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(26*(1-t)+16*t), int(40*(1-t)+47*t), int(48*(1-t)+48*t), 255))

    # Abbey cloister and scanner room.
    draw.rectangle((0, 950, W, 1765), fill=(52, 64, 60, 245))
    for x in range(90, 1520, 230):
        draw.rectangle((x, 700, x + 115, 1500), fill=(43, 53, 51, 245))
        draw.arc((x - 28, 585, x + 143, 810), 180, 360, fill=(151, 162, 141, 190), width=14)
    draw.rectangle((0, 1510, W, 1765), fill=(37, 55, 48, 250))
    draw.polygon([(0, 1510), (455, 1380), (820, 1485), (1190, 1365), (1600, 1495), (1600, 1765), (0, 1765)], fill=(55, 94, 70, 220))

    # Blue scanner light and manuscript cradle.
    draw.rounded_rectangle((275, 1120, 1325, 1415), radius=28, fill=(18, 26, 28, 230), outline=(121, 168, 161, 150), width=4)
    draw.rounded_rectangle((355, 1195, 1245, 1348), radius=18, fill=(6, 17, 22, 240), outline=(52, 205, 233, 180), width=4)
    draw.rectangle((380, 1262, 1220, 1280), fill=(61, 219, 246, 220))
    for x in range(410, 1190, 70):
        draw.line((x, 1208, x + random.randint(-20, 20), 1340), fill=(83, 228, 246, 42), width=3)
    draw.text((430, 1146), "SOURCE IMAGE / MODEL OUTPUT", font=font("arialbd.ttf", 31), fill=(198, 230, 221, 220))

    # Palimpsest charter leaf with green overtext and brown undertext.
    leaf = [(505, 760), (1085, 700), (1160, 1095), (565, 1165)]
    draw.polygon(leaf, fill=(220, 207, 168, 238), outline=(83, 66, 46, 190))
    for i in range(8):
        y0 = 805 + i * 42
        draw.line((585, y0, 1040, y0 - 42), fill=(44, 108, 73, 95), width=4)
    for i in range(7):
        y0 = 875 + i * 38
        draw.line((615, y0, 1080, y0 - 48), fill=(106, 63, 37, 130), width=3)
    draw.text((635, 1018), "COMMUNIS AQUA", font=font("arialbd.ttf", 36), fill=(92, 58, 37, 215))

    # Algorithm confidence panel and cropped marginal note.
    draw.rounded_rectangle((130, 510, 540, 820), radius=22, fill=(11, 25, 28, 210), outline=(70, 204, 191, 150), width=3)
    draw.text((170, 545), "CONFIDENCE", font=font("arialbd.ttf", 32), fill=(199, 233, 220, 230))
    draw.text((205, 605), "98.2%", font=font("arialbd.ttf", 70), fill=(88, 234, 211, 235))
    draw.text((170, 705), "WRONG WHERE\nSOURCE IS DAMAGED", font=font("arialbd.ttf", 24), fill=(241, 141, 111, 225))
    draw.rounded_rectangle((1080, 515, 1455, 805), radius=18, fill=(226, 215, 177, 230), outline=(82, 65, 43, 170), width=3)
    draw.text((1115, 550), "CROPPED MARGIN", font=font("arialbd.ttf", 29), fill=(74, 54, 38, 230))
    draw.rectangle((1120, 625, 1420, 690), outline=(231, 83, 67, 210), width=6)
    draw.text((1135, 715), "meadow / millstream", font=font("arial.ttf", 27), fill=(83, 60, 42, 220))

    # File/version artifacts.
    for x, y, label in [(170, 910, "brigid_final"), (1100, 900, "meadow_final"), (1045, 1455, "POSTPROCESSOR")]:
        draw.rounded_rectangle((x, y, x + 315, y + 120), radius=15, fill=(235, 226, 192, 218), outline=(90, 74, 50, 155), width=3)
        draw.text((x + 24, y + 35), label, font=font("arialbd.ttf", 27), fill=(76, 56, 38, 225))
    for _ in range(90):
        x = random.randint(120, 1480)
        y = random.randint(710, 1600)
        draw.ellipse((x, y, x + 3, y + 3), fill=(225, 220, 178, random.randint(45, 130)))

    # Common meadow boundary and water line.
    draw.line((185, 1590, 1390, 1590), fill=(80, 168, 198, 190), width=8)
    for x in range(230, 1340, 150):
        draw.arc((x, 1560, x + 100, 1625), 0, 180, fill=(97, 197, 215, 130), width=3)
    draw.text((545, 1630), "COMMON MEADOW / WATER CLAUSE", font=font("arialbd.ttf", 30), fill=(198, 225, 205, 220))

    tagline = "DIGITAL HUMANITIES  PALIMPSEST LEAF  COMMON LAND"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Cloister Algorithm")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (26, 40, 48, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_cloister_archive(draw)
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
