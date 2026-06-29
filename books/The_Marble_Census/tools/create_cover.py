#!/usr/bin/env python3
"""Create a book-specific cover for The Marble Census."""

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


def draw_marble_square(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-marble-census-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(46*(1-t)+20*t), int(50*(1-t)+34*t), int(56*(1-t)+43*t), 255))

    # Rain-lit civic square.
    draw.rectangle((0, 1215, W, 1765), fill=(42, 45, 47, 245))
    for y in range(1240, 1740, 55):
        draw.line((0, y, W, y + random.randint(-10, 10)), fill=(118, 126, 126, 70), width=2)
    for _ in range(240):
        x = random.randint(-60, W + 60)
        y = random.randint(180, 1600)
        draw.line((x, y, x - 16, y + random.randint(35, 75)), fill=(190, 202, 205, random.randint(35, 85)), width=2)

    # Courthouse and tenement silhouettes.
    draw.rectangle((90, 665, 430, 1215), fill=(28, 31, 34, 235))
    draw.rectangle((1180, 585, 1510, 1215), fill=(30, 33, 36, 235))
    for x0 in (130, 220, 310, 1220, 1310, 1400):
        for y0 in (735, 865, 995):
            draw.rectangle((x0, y0, x0 + 45, y0 + 70), fill=(217, 193, 116, 75))
    draw.polygon([(540, 645), (800, 410), (1060, 645)], fill=(82, 82, 78, 235))
    draw.rectangle((585, 645, 1015, 1215), fill=(64, 66, 65, 240))
    for x in range(630, 980, 85):
        draw.rectangle((x, 755, x + 42, 1215), fill=(37, 39, 41, 240))

    # Meridian statue.
    sx, sy = 800, 870
    marble = (217, 217, 205, 245)
    shadow = (152, 154, 148, 230)
    draw.rectangle((650, 1195, 950, 1320), fill=(186, 184, 170, 245), outline=(95, 94, 86, 200), width=5)
    draw.text((690, 1238), "MC-001", font=font("arialbd.ttf", 39), fill=(73, 72, 67, 230))
    draw.ellipse((sx - 55, sy - 250, sx + 55, sy - 140), fill=marble, outline=shadow, width=4)
    draw.polygon([(sx - 95, sy - 140), (sx + 95, sy - 140), (sx + 145, sy + 260), (sx - 145, sy + 260)], fill=marble, outline=shadow)
    draw.line((sx + 20, sy - 90, sx + 235, sy - 165), fill=marble, width=34)
    draw.ellipse((sx + 220, sy - 182, sx + 260, sy - 142), fill=marble, outline=shadow, width=3)
    draw.line((sx - 25, sy - 80, sx - 135, sy + 55), fill=shadow, width=9)
    for yy in range(sy - 80, sy + 230, 44):
        draw.arc((sx - 120, yy, sx + 120, yy + 120), 190, 345, fill=(170, 171, 162, 130), width=4)

    # Census ledger and erased-address papers.
    draw.rounded_rectangle((195, 1350, 635, 1595), radius=16, fill=(230, 225, 203, 235), outline=(91, 80, 60, 190), width=4)
    draw.text((235, 1380), "MARBLE CENSUS", font=font("arialbd.ttf", 32), fill=(55, 50, 44, 230))
    for i, txt in enumerate(["MC-001  TURNED", "MARA VALE", "ROLL RESTORED"]):
        draw.text((235, 1440 + i * 42), txt, font=font("arial.ttf", 28), fill=(60, 55, 48, 220))
    draw.rounded_rectangle((1030, 1350, 1395, 1540), radius=14, fill=(234, 228, 206, 230), outline=(120, 45, 42, 180), width=4)
    draw.text((1072, 1392), "VACANT", font=font("arialbd.ttf", 47), fill=(145, 48, 45, 220))
    draw.line((1058, 1464, 1370, 1464), fill=(145, 48, 45, 210), width=7)
    draw.text((1072, 1488), "NAME ERASED", font=font("arial.ttf", 29), fill=(80, 66, 58, 210))

    # Dust and marble chips.
    for _ in range(180):
        x = random.randint(140, 1460)
        y = random.randint(710, 1615)
        s = random.randint(2, 7)
        draw.ellipse((x, y, x + s, y + s), fill=(222, 219, 202, random.randint(45, 150)))

    tagline = "CIVIC GOTHIC  LIVING STATUES  ERASED NAMES"
    tag_font = font("georgia.ttf", 35)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(225, 218, 190, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Marble Census")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (31, 35, 40, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_marble_square(draw)
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
