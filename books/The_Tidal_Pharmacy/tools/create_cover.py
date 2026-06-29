#!/usr/bin/env python3
"""Create a book-specific cover for The Tidal Pharmacy."""

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


def draw_tidal_pharmacy(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-tidal-pharmacy-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(18*(1-t)+9*t), int(52*(1-t)+71*t), int(72*(1-t)+92*t), 255))

    # Harbor and islands.
    draw.rectangle((0, 1060, W, 1765), fill=(30, 86, 101, 245))
    for y0 in range(1120, 1700, 90):
        draw.arc((-80, y0, 360, y0 + 130), 0, 180, fill=(117, 187, 195, 85), width=4)
        draw.arc((420, y0 + 30, 920, y0 + 160), 0, 180, fill=(117, 187, 195, 70), width=4)
        draw.arc((1000, y0 - 15, 1660, y0 + 145), 0, 180, fill=(117, 187, 195, 78), width=4)
    draw.polygon([(0, 990), (300, 870), (640, 965), (1040, 850), (1600, 1015), (1600, 1180), (0, 1180)], fill=(36, 71, 66, 235))
    draw.rectangle((150, 1200, 1445, 1282), fill=(78, 62, 48, 245))
    for x in range(180, 1420, 120):
        draw.rectangle((x, 1265, x + 28, 1595), fill=(55, 47, 40, 245))

    # Pharmacy cold crate and public seal.
    draw.rounded_rectangle((235, 760, 860, 1210), radius=34, fill=(219, 236, 236, 240), outline=(55, 95, 103, 210), width=6)
    draw.rectangle((235, 930, 860, 995), fill=(57, 196, 218, 210))
    draw.text((290, 815), "PUBLIC MEDICINE", font=font("arialbd.ttf", 38), fill=(37, 72, 78, 230))
    draw.text((305, 1035), "SEAL 8813", font=font("arialbd.ttf", 46), fill=(210, 73, 56, 235))
    for x in range(285, 820, 85):
        draw.line((x, 1125, x + 45, 1125), fill=(44, 88, 96, 130), width=5)

    # Clouded insulin vial under magnifier.
    draw.ellipse((990, 690, 1395, 1095), fill=(220, 239, 234, 58), outline=(220, 240, 231, 210), width=7)
    draw.line((1305, 1015, 1485, 1195), fill=(35, 54, 55, 230), width=24)
    draw.rounded_rectangle((1110, 785, 1275, 1010), radius=32, fill=(221, 238, 244, 220), outline=(40, 77, 89, 190), width=4)
    draw.rectangle((1138, 740, 1248, 800), fill=(75, 117, 130, 230))
    for _ in range(46):
        x = random.randint(1135, 1258)
        y = random.randint(830, 985)
        s = random.randint(2, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(240, 255, 255, random.randint(75, 160)))
    draw.text((1028, 1032), "CLOUDED INSULIN", font=font("arialbd.ttf", 27), fill=(31, 69, 76, 225))

    # Temperature graph and tide window.
    draw.rounded_rectangle((210, 1360, 835, 1575), radius=20, fill=(6, 24, 31, 205), outline=(101, 221, 232, 135), width=3)
    draw.text((250, 1392), "COPIED TEMPERATURE CURVE", font=font("arialbd.ttf", 26), fill=(193, 238, 233, 225))
    last = None
    for x in range(250, 800, 18):
        y = 1510 + int(math.sin(x * 0.035) * 24)
        if last:
            draw.line((last[0], last[1], x, y), fill=(88, 231, 220, 220), width=4)
        last = (x, y)
    draw.rounded_rectangle((940, 1345, 1388, 1588), radius=18, fill=(230, 222, 188, 228), outline=(91, 74, 51, 170), width=3)
    draw.text((980, 1380), "TIDE WINDOW", font=font("arialbd.ttf", 31), fill=(63, 50, 37, 230))
    draw.text((1008, 1445), "00:34 - 01:12", font=font("arialbd.ttf", 42), fill=(30, 90, 103, 235))
    draw.text((988, 1510), "MERIDIAN SKIFF", font=font("arial.ttf", 28), fill=(68, 58, 44, 220))

    # Ferry and skiff silhouettes.
    draw.polygon([(980, 1170), (1290, 1170), (1355, 1235), (920, 1235)], fill=(31, 47, 50, 245))
    draw.rectangle((1040, 1080, 1220, 1170), fill=(38, 62, 66, 245))
    draw.line((180, 1660, 1460, 1660), fill=(118, 199, 207, 185), width=7)
    for x in range(220, 1410, 155):
        draw.arc((x, 1630, x + 110, 1695), 0, 180, fill=(135, 214, 218, 120), width=3)
    draw.text((515, 1692), "COLD CHAIN MUST FOLLOW THE TIDE", font=font("arialbd.ttf", 30), fill=(202, 233, 226, 220))

    # Salt crystals and ledger tags.
    for _ in range(150):
        x = random.randint(130, 1490)
        y = random.randint(700, 1650)
        s = random.randint(1, 5)
        draw.rectangle((x, y, x + s, y + s), fill=(224, 246, 244, random.randint(40, 130)))
    draw.rounded_rectangle((965, 520, 1425, 630), radius=14, fill=(239, 231, 196, 225), outline=(80, 62, 42, 150), width=3)
    draw.text((995, 555), "HARBOR BOOK != MANIFEST", font=font("arialbd.ttf", 23), fill=(68, 53, 38, 225))

    tagline = "COLD CHAIN  TIDE LOGS  PUBLIC MEDICINE"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tidal Pharmacy")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (18, 52, 72, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_tidal_pharmacy(draw)
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
