#!/usr/bin/env python3
"""Create a book-specific cover for The Brass Semaphore."""

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


def draw_brass_semaphore(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-brass-semaphore-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(30*(1-t)+42*t), int(44*(1-t)+54*t), int(57*(1-t)+61*t), 255))

    # Fog harbor and tower.
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog, "RGBA")
    for y0 in range(420, 1210, 120):
        fd.ellipse((-220, y0, W + 260, y0 + 250), fill=(210, 224, 218, 26))
    fog = fog.filter(ImageFilter.GaussianBlur(24))
    draw.bitmap((0, 0), fog)
    draw.rectangle((0, 1280, W, 1765), fill=(42, 65, 72, 245))
    for y0 in range(1360, 1710, 84):
        draw.arc((-120, y0, 520, y0 + 130), 0, 180, fill=(135, 175, 180, 80), width=4)
        draw.arc((680, y0 + 25, 1660, y0 + 165), 0, 180, fill=(135, 175, 180, 72), width=4)

    # Semaphore tower.
    draw.rectangle((690, 640, 910, 1395), fill=(45, 50, 49, 245), outline=(166, 178, 164, 145), width=5)
    draw.polygon([(655, 640), (800, 520), (945, 640)], fill=(65, 70, 66, 245), outline=(171, 182, 164, 140))
    draw.rectangle((620, 1365, 980, 1450), fill=(64, 55, 47, 245))
    pivot = (800, 610)
    brass = (214, 159, 78, 245)
    draw.ellipse((pivot[0]-34, pivot[1]-34, pivot[0]+34, pivot[1]+34), fill=brass, outline=(94, 65, 32, 220), width=4)
    draw.line((800, 610, 565, 470), fill=brass, width=24)
    draw.line((800, 610, 1035, 455), fill=brass, width=24)
    draw.polygon([(555, 448), (610, 482), (585, 535), (530, 500)], fill=(181, 39, 37, 230))
    draw.polygon([(1028, 430), (1088, 462), (1060, 520), (1000, 488)], fill=(224, 219, 175, 230))
    draw.text((714, 1480), "7-4-2", font=font("arialbd.ttf", 55), fill=(228, 193, 125, 235))

    # Gear and counterweight evidence.
    draw.rounded_rectangle((150, 885, 560, 1165), radius=22, fill=(24, 31, 31, 220), outline=(214, 159, 78, 160), width=4)
    draw.text((198, 920), "ALTERED GEAR", font=font("arialbd.ttf", 31), fill=(232, 206, 157, 230))
    for r in (80, 115):
        draw.ellipse((355-r, 1028-r, 355+r, 1028+r), outline=(214, 159, 78, 210), width=8)
    for ang in range(0, 360, 30):
        x1 = 355 + math.cos(math.radians(ang)) * 80
        y1 = 1028 + math.sin(math.radians(ang)) * 80
        x2 = 355 + math.cos(math.radians(ang)) * 128
        y2 = 1028 + math.sin(math.radians(ang)) * 128
        draw.line((x1, y1, x2, y2), fill=(214, 159, 78, 190), width=5)
    draw.rounded_rectangle((1045, 870, 1415, 1035), radius=18, fill=(231, 222, 190, 230), outline=(85, 65, 43, 170), width=3)
    draw.text((1085, 905), "PYC COUNTERWEIGHT", font=font("arialbd.ttf", 27), fill=(67, 50, 35, 230))
    draw.text((1138, 960), "PRIVATE YARD", font=font("arialbd.ttf", 34), fill=(153, 72, 52, 230))

    # Signal book and cargo ledger.
    draw.rounded_rectangle((130, 1225, 610, 1535), radius=18, fill=(232, 224, 190, 232), outline=(86, 66, 45, 160), width=3)
    draw.text((174, 1260), "MISSING SIGNAL PAGES", font=font("arialbd.ttf", 29), fill=(70, 52, 37, 230))
    for i, txt in enumerate(["7-4-2 EAST LANE", "FOG GAP", "PRIVATE TRANSFER"]):
        draw.text((180, 1328 + i * 50), txt, font=font("arial.ttf", 29), fill=(83, 61, 43, 220))
    draw.rounded_rectangle((970, 1220, 1465, 1525), radius=18, fill=(10, 23, 31, 220), outline=(122, 174, 190, 150), width=3)
    draw.text((1012, 1260), "CARGO LEDGER", font=font("arialbd.ttf", 31), fill=(203, 230, 224, 230))
    for i, cargo in enumerate(["MARIBEL TEA", "EASTWAKE COPPER", "ORISON GLASS"]):
        draw.text((1018, 1328 + i * 48), cargo, font=font("arial.ttf", 28), fill=(210, 223, 218, 220))

    # Harbor boats and signal scratches.
    draw.polygon([(250, 1580), (540, 1580), (595, 1640), (205, 1640)], fill=(28, 42, 45, 245))
    draw.rectangle((335, 1505, 470, 1580), fill=(37, 56, 60, 245))
    draw.line((255, 1678, 1370, 1678), fill=(139, 188, 190, 160), width=7)
    for x in range(300, 1320, 140):
        draw.arc((x, 1648, x + 96, 1715), 0, 180, fill=(151, 202, 202, 105), width=3)
    for _ in range(130):
        x = random.randint(90, 1510)
        y = random.randint(380, 1650)
        s = random.randint(1, 4)
        draw.ellipse((x, y, x + s, y + s), fill=(218, 232, 228, random.randint(35, 120)))

    tagline = "NAVAL SIGNALS  FOG LOGS  HARBOR CLAIMS"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Brass Semaphore")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (30, 44, 57, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_brass_semaphore(draw)
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
