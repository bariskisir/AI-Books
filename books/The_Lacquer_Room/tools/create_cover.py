#!/usr/bin/env python3
"""Create a book-specific cover for The Lacquer Room."""

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


def draw_lacquer_room(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-lacquer-room-cover")
    for y in range(H):
        t = y / H
        r = int(34 * (1 - t) + 13 * t)
        g = int(29 * (1 - t) + 14 * t)
        b = int(31 * (1 - t) + 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Conservation-room light.
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light, "RGBA")
    ld.polygon([(1010, 0), (1335, 0), (860, 1765), (505, 1765)], fill=(234, 222, 174, 70))
    ld.polygon([(210, 0), (430, 0), (640, 1765), (360, 1765)], fill=(155, 188, 195, 28))
    draw.bitmap((0, 0), light.filter(ImageFilter.GaussianBlur(25)), fill=None)

    # Lacquer screen panels.
    screen = (210, 430, 1390, 1340)
    panel_w = (screen[2] - screen[0]) // 6
    for i in range(6):
        x0 = screen[0] + i * panel_w
        x1 = x0 + panel_w - 8
        shade = 12 + i * 3
        draw.rounded_rectangle((x0, screen[1], x1, screen[3]), radius=8, fill=(shade, shade, shade + 5, 250), outline=(105, 83, 49, 220), width=5)
        draw.line((x1, screen[1] + 12, x1, screen[3] - 12), fill=(198, 160, 74, 90), width=3)

    # Gold landscape and cranes.
    for y in (1000, 1085, 1170):
        pts = []
        for x in range(250, 1350, 75):
            pts.append((x, y + random.randint(-28, 24)))
        draw.line(pts, fill=(206, 164, 70, 190), width=7)
    for x, y, s in [(460, 735, 1.0), (785, 675, 1.2), (1120, 790, .95)]:
        gold = (226, 185, 82, 230)
        draw.ellipse((x - 16*s, y - 14*s, x + 16*s, y + 14*s), fill=gold)
        draw.line((x, y, x - 82*s, y + 60*s), fill=gold, width=int(6*s))
        draw.line((x, y, x + 96*s, y + 45*s), fill=gold, width=int(6*s))
        draw.line((x - 7*s, y + 12*s, x - 22*s, y + 82*s), fill=gold, width=int(4*s))
        draw.line((x + 8*s, y + 12*s, x + 22*s, y + 82*s), fill=gold, width=int(4*s))

    # Raking-light rectangle exposing hidden temple mark.
    mark_box = (665, 1122, 970, 1240)
    draw.rounded_rectangle(mark_box, radius=10, fill=(36, 30, 26, 245), outline=(235, 212, 134, 220), width=4)
    draw.line((520, 1040, 1040, 1230), fill=(242, 226, 154, 155), width=9)
    mark_font = font("arialbd.ttf", 42)
    draw.text((700, 1154), "KOSEN-IN", font=mark_font, fill=(226, 210, 150, 220))
    draw.text((704, 1202), "INV. 4", font=font("arial.ttf", 29), fill=(205, 188, 130, 190))

    # Microscope, swabs, sample map.
    draw.rounded_rectangle((160, 1320, 580, 1600), radius=20, fill=(222, 218, 198, 230), outline=(104, 91, 67, 180), width=4)
    draw.text((195, 1350), "LAYER MAP", font=font("arialbd.ttf", 32), fill=(57, 48, 39, 230))
    colors = [(18,18,22), (198,151,65), (115,55,42), (232,225,200), (68,83,89)]
    for i, col in enumerate(colors):
        draw.rectangle((205, 1410 + i*27, 530, 1430 + i*27), fill=col+(230,) if len(col)==3 else col)
    draw.line((1140, 1320, 1280, 1510), fill=(205, 210, 202, 230), width=20)
    draw.ellipse((1230, 1475, 1385, 1595), outline=(205, 210, 202, 230), width=18)
    draw.rectangle((1258, 1270, 1312, 1360), fill=(205, 210, 202, 230))
    for x in (710, 770, 830):
        draw.line((x, 1415, x + 240, 1560), fill=(237, 230, 208, 200), width=7)
        draw.ellipse((x + 228, 1548, x + 258, 1578), fill=(245, 236, 215, 220))

    # Dust motes.
    for _ in range(140):
        x = random.randint(130, 1470)
        y = random.randint(260, 1615)
        s = random.randint(2, 5)
        draw.ellipse((x, y, x+s, y+s), fill=(232, 206, 145, random.randint(35, 105)))

    tagline = "ART CONSERVATION  PROVENANCE  REPATRIATION"
    tag_font = font("georgia.ttf", 37)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(226, 208, 158, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Lacquer Room")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (18, 18, 21, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_lacquer_room(draw)
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
    draw.rectangle((0, panel_y, width, height), fill=(231, 224, 207, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(96, 72, 42, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (39, 34, 31), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (84, 69, 52), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (112, 98, 82), 6, width)


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
