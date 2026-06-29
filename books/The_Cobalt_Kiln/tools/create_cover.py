#!/usr/bin/env python3
"""Create a book-specific cover for The Cobalt Kiln."""

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


def draw_cobalt_kiln(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-cobalt-kiln-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(28*(1-t)+39*t), int(34*(1-t)+30*t), int(45*(1-t)+37*t), 255))

    # Museum lab and kiln chamber glow.
    draw.rectangle((0, 1065, W, 1765), fill=(52, 45, 39, 248))
    draw.rectangle((0, 1470, W, 1765), fill=(91, 65, 42, 250))
    draw.ellipse((980, 550, 1570, 1190), fill=(111, 54, 30, 80), outline=(195, 101, 47, 170), width=8)
    draw.rectangle((1090, 750, 1470, 1260), fill=(38, 34, 31, 240), outline=(195, 101, 47, 160), width=6)
    draw.arc((1125, 620, 1435, 910), 180, 360, fill=(211, 122, 58, 160), width=10)
    draw.text((1030, 1295), "PRIVATE COBALT KILN", font=font("arialbd.ttf", 28), fill=(231, 184, 116, 220))

    # Central cobalt bowl.
    cx, cy = 690, 1045
    draw.ellipse((cx - 315, cy - 130, cx + 315, cy + 130), fill=(19, 66, 142, 255), outline=(8, 30, 72, 230), width=8)
    draw.ellipse((cx - 260, cy - 88, cx + 260, cy + 88), fill=(37, 112, 198, 250), outline=(145, 193, 226, 95), width=5)
    draw.rectangle((cx - 210, cy, cx + 210, cy + 310), fill=(23, 81, 164, 255))
    draw.ellipse((cx - 210, cy + 210, cx + 210, cy + 410), fill=(15, 53, 122, 255), outline=(6, 28, 72, 220), width=7)
    for i in range(11):
        x = cx - 240 + i * 48
        draw.arc((x, cy - 35, x + 180, cy + 340), 235, 292, fill=(122, 184, 225, 70), width=5)
    draw.text((cx - 77, cy + 255), "T-44", font=font("arialbd.ttf", 50), fill=(230, 230, 195, 210))

    # Magnifier over foot mark and lacquer.
    draw.ellipse((220, 650, 575, 1005), fill=(225, 238, 231, 55), outline=(224, 236, 220, 210), width=7)
    draw.line((500, 940, 660, 1110), fill=(40, 39, 35, 230), width=24)
    draw.rounded_rectangle((300, 790, 500, 900), radius=16, fill=(26, 77, 145, 240), outline=(229, 208, 139, 180), width=4)
    draw.text((348, 818), "T-44", font=font("arialbd.ttf", 36), fill=(239, 229, 181, 235))
    draw.line((292, 880, 512, 812), fill=(80, 34, 28, 190), width=10)

    # Evidence cards.
    draw.rounded_rectangle((130, 1245, 555, 1428), radius=16, fill=(235, 226, 190, 230), outline=(85, 65, 43, 170), width=3)
    draw.text((170, 1280), "FALSE PERMIT", font=font("arialbd.ttf", 31), fill=(76, 56, 38, 230))
    draw.line((175, 1345, 510, 1345), fill=(102, 78, 55, 130), width=4)
    draw.text((172, 1372), "EXPORT BEFORE EXCAVATION", font=font("arialbd.ttf", 22), fill=(150, 57, 47, 225))
    draw.rounded_rectangle((930, 1280, 1435, 1458), radius=18, fill=(8, 24, 41, 218), outline=(73, 165, 220, 140), width=3)
    draw.text((975, 1315), "COBALT ISOTOPE TRACE", font=font("arialbd.ttf", 29), fill=(185, 221, 240, 230))
    for i, x in enumerate(range(985, 1390, 28)):
        h = 35 + int(math.sin(i * 1.2) * 25) + random.randint(-6, 6)
        draw.line((x, 1422, x, 1422 - h), fill=(76, 183, 236, 205), width=5)

    # Ash scar and shard comparison.
    draw.rounded_rectangle((640, 1375, 875, 1502), radius=18, fill=(28, 39, 43, 230), outline=(206, 143, 74, 145), width=3)
    draw.arc((675, 1408, 835, 1492), 12, 172, fill=(232, 156, 76, 230), width=8)
    draw.text((662, 1340), "ASH RING", font=font("arialbd.ttf", 27), fill=(231, 185, 127, 220))
    for _ in range(170):
        x = random.randint(140, 1480)
        y = random.randint(590, 1660)
        s = random.randint(1, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(183, 210, 236, random.randint(35, 125)))

    tagline = "CERAMIC PROVENANCE  KILN SCARS  HIDDEN MARKS"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Cobalt Kiln")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (28, 34, 45, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_cobalt_kiln(draw)
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
