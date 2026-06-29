#!/usr/bin/env python3
"""Create a custom cover for The Smoke Library."""

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


def draw_library_fire(draw: ImageDraw.ImageDraw) -> None:
    # Smoke-dark reading room with a low smoke band that mirrors the investigation clue.
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.42:
            c = lerp((12, 18, 24), (35, 43, 48), t / 0.42)
        elif t < 0.72:
            c = lerp((35, 43, 48), (70, 64, 54), (t - 0.42) / 0.30)
        else:
            c = lerp((70, 64, 54), (24, 18, 17), (t - 0.72) / 0.28)
        draw.line((0, y, W, y), fill=(*c, 255))

    for y in range(900, 1220, 8):
        alpha = int(120 * (1 - abs(y - 1060) / 190))
        draw.line((0, y, W, y), fill=(18, 22, 22, max(0, alpha)), width=9)

    # Broken skylight and pale ash light from above.
    draw.polygon([(540, 110), (1070, 70), (1170, 250), (445, 305)], fill=(154, 172, 168, 70), outline=(218, 214, 184, 120))
    for x in range(520, 1120, 90):
        draw.line((x, 95, x + 120, 285), fill=(224, 218, 190, 55), width=4)
    for i in range(18):
        x = random.randint(480, 1160)
        draw.line((x, 260, x - random.randint(120, 260), 990), fill=(235, 218, 172, random.randint(16, 32)), width=random.randint(3, 7))

    # Tall shelving bays, warped by heat.
    shelf_colors = [(64, 41, 31), (78, 50, 35), (48, 34, 29), (95, 60, 38)]
    for bay, x in enumerate(range(120, 1490, 245)):
        lean = random.randint(-18, 18)
        draw.polygon([(x, 390), (x + 180, 385 + lean), (x + 205, 1530), (x - 18, 1535)], fill=(30, 24, 22, 235), outline=(117, 82, 55, 120))
        for shelf_y in range(500, 1450, 145):
            draw.line((x - 10, shelf_y, x + 200, shelf_y + lean // 2), fill=(116, 78, 48, 190), width=10)
            for k in range(9):
                bx = x + 5 + k * 20 + random.randint(-2, 2)
                top = shelf_y - random.randint(55, 112)
                bottom = shelf_y - 8
                col = random.choice(shelf_colors)
                if random.random() < 0.28:
                    col = (18, 17, 16)
                draw.rectangle((bx, top, bx + random.randint(10, 18), bottom), fill=(*col, 230))

    # Charred central table with surviving evidence.
    draw.polygon([(330, 1390), (1275, 1365), (1450, 1585), (210, 1610)], fill=(42, 30, 24, 245), outline=(122, 84, 55, 160))
    draw.line((310, 1438, 1286, 1414), fill=(176, 122, 64, 120), width=5)
    draw.rectangle((520, 1430, 900, 1540), fill=(229, 222, 190, 230), outline=(72, 56, 45, 180), width=3)
    draw.text((548, 1455), "V-9 HOLDING", font=font("arialbd.ttf", 34), fill=(56, 45, 38, 235))
    draw.text((550, 1498), "DO NOT ERASE", font=font("arial.ttf", 28), fill=(92, 54, 43, 220))

    # Sprinkler head and red seal wax, specific to the case evidence.
    draw.ellipse((1085, 1425, 1235, 1575), fill=(52, 58, 58, 255), outline=(194, 180, 138, 170), width=5)
    for a in range(0, 360, 45):
        r = math.radians(a)
        draw.line((1160, 1500, 1160 + 92 * math.cos(r), 1500 + 92 * math.sin(r)), fill=(170, 152, 112, 160), width=5)
    draw.ellipse((1126, 1466, 1194, 1534), fill=(112, 120, 112, 255))
    draw.ellipse((960, 1505, 1038, 1578), fill=(145, 26, 28, 245), outline=(80, 15, 18, 210), width=4)
    draw.line((999, 1542, 1088, 1448), fill=(145, 26, 28, 185), width=5)

    # Smoke curls and ash flecks.
    smoke = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(smoke, "RGBA")
    for i in range(42):
        x = random.randint(20, W - 80)
        y = random.randint(340, 1320)
        w = random.randint(220, 520)
        h = random.randint(42, 110)
        sd.arc((x - w // 2, y - h // 2, x + w // 2, y + h // 2), random.randint(160, 240), random.randint(300, 380), fill=(190, 186, 166, random.randint(18, 48)), width=random.randint(5, 13))
    smoke = smoke.filter(ImageFilter.GaussianBlur(2.2))
    draw.bitmap((0, 0), smoke, fill=None)
    for _ in range(260):
        x = random.randint(0, W)
        y = random.randint(120, PANEL_Y - 80)
        s = random.randint(1, 4)
        draw.rectangle((x, y, x + s, y + s), fill=(230, 218, 185, random.randint(35, 115)))

    tagline = "ARSON  RARE BOOKS  INSURANCE FRAUD"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 315), tagline, font=tag_font, fill=(228, 216, 180, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Smoke Library")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("the-smoke-library-cover")
    image = Image.new("RGBA", (W, H), (16, 16, 18, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_library_fire(draw)
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
    draw.rectangle((0, panel_y, width, height), fill=(235, 229, 214, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(94, 82, 66, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (50, 48, 42), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (88, 76, 58), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (112, 102, 84), 6, width)


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
