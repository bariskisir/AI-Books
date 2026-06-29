#!/usr/bin/env python3
"""Create a book-specific cover for The Coral Clock."""

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


def draw_underwater_scene(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-coral-clock-cover")
    for y in range(H):
        t = y / H
        r = int(13 * (1 - t) + 5 * t)
        g = int(92 * (1 - t) + 35 * t)
        b = int(118 * (1 - t) + 58 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Light shafts.
    light = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(light, "RGBA")
    for x in (170, 520, 960, 1320):
        ld.polygon([(x, 0), (x + 130, 0), (x - 180, 1765), (x - 420, 1765)], fill=(170, 224, 216, 28))
    light = light.filter(ImageFilter.GaussianBlur(18))
    draw.bitmap((0, 0), light, fill=None)

    # Seafloor and reef masses.
    draw.rectangle((0, 1360, W, 1765), fill=(16, 64, 70, 230))
    for x in range(-40, W, 95):
        h = random.randint(65, 210)
        color = random.choice([(42, 122, 108, 235), (78, 67, 105, 235), (166, 92, 84, 230), (205, 139, 92, 230)])
        draw.ellipse((x, 1410 - h, x + 150, 1510 + h // 5), fill=color)
        for _ in range(5):
            bx = x + random.randint(10, 125)
            by = 1390 - random.randint(0, h)
            draw.line((bx, by, bx + random.randint(-35, 35), by - random.randint(35, 95)), fill=(210, 171, 117, 180), width=4)

    # Chronometer embedded in coral.
    cx, cy = 790, 1045
    draw.ellipse((cx - 245, cy - 245, cx + 245, cy + 245), fill=(126, 91, 45, 245), outline=(224, 183, 98, 230), width=16)
    draw.ellipse((cx - 190, cy - 190, cx + 190, cy + 190), fill=(214, 203, 169, 235), outline=(84, 67, 45, 180), width=8)
    for i in range(12):
        ang = math.radians(i * 30 - 90)
        x1 = cx + math.cos(ang) * 145
        y1 = cy + math.sin(ang) * 145
        x2 = cx + math.cos(ang) * 166
        y2 = cy + math.sin(ang) * 166
        draw.line((x1, y1, x2, y2), fill=(70, 61, 48, 180), width=4)
    draw.line((cx, cy, cx + 70, cy - 30), fill=(55, 48, 39, 235), width=8)
    draw.line((cx, cy, cx - 38, cy - 120), fill=(55, 48, 39, 235), width=8)
    draw.ellipse((cx - 16, cy - 16, cx + 16, cy + 16), fill=(55, 48, 39, 235))
    draw.text((cx - 95, cy + 72), "2:38", font=font("georgia.ttf", 48), fill=(82, 64, 42, 210))
    for _ in range(90):
        ang = random.random() * math.tau
        rad = random.randint(210, 310)
        x = cx + math.cos(ang) * rad
        y = cy + math.sin(ang) * rad
        col = random.choice([(216, 114, 94, 210), (235, 178, 112, 210), (93, 151, 126, 210)])
        draw.ellipse((x - 18, y - 12, x + 18, y + 12), fill=col)

    # Wreck ribs and corrected survey overlay.
    for x in (250, 335, 420, 505):
        draw.arc((x, 1200, x + 310, 1600), 205, 330, fill=(62, 42, 32, 210), width=16)
    draw.line((150, 1270, 1450, 1510), fill=(41, 28, 23, 190), width=18)
    draw.line((180, 720, 1420, 1370), fill=(101, 217, 230, 150), width=5)
    draw.line((320, 680, 1180, 1480), fill=(244, 207, 93, 135), width=5)
    for x, y, label in [(1085, 705, "RAW REEF LINE"), (215, 650, "FALSE CHANNEL")]:
        draw.rounded_rectangle((x, y, x + 300, y + 70), radius=12, fill=(12, 44, 54, 190), outline=(187, 230, 214, 120), width=3)
        draw.text((x + 20, y + 20), label, font=font("arialbd.ttf", 27), fill=(218, 236, 211, 230))

    # Small fish and bubbles.
    for _ in range(55):
        x = random.randint(80, 1500)
        y = random.randint(370, 1510)
        s = random.randint(8, 22)
        draw.polygon([(x, y), (x + s * 2, y - s), (x + s * 2, y + s)], fill=(169, 205, 194, random.randint(75, 150)))
    for _ in range(90):
        x = random.randint(70, 1530)
        y = random.randint(120, 1560)
        s = random.randint(3, 10)
        draw.ellipse((x, y, x + s, y + s), outline=(203, 235, 226, random.randint(70, 145)), width=2)

    tagline = "MARINE ARCHAEOLOGY  REEF RESTORATION  WRECK SITE"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(221, 235, 211, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Coral Clock")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (8, 45, 62, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_underwater_scene(draw)
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
    return "Bar\u0131\u015f K\u0131s\u0131r"


def _draw_standard_cover_title_panel(image, title: str = "", author: str = "", model: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Bar\u0131\u015f K\u0131s\u0131r")).strip()
    model = _standard_cover_repair_text(str(model or "")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(226, 231, 213, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(43, 112, 118, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (22, 67, 73), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (58, 89, 83), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (94, 115, 105), 6, width)


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
