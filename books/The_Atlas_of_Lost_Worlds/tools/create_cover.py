#!/usr/bin/env python3
"""Create a project-local raster cover for The Atlas of Lost Worlds."""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
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


def centered(draw: ImageDraw.ImageDraw, y: int, lines: list[str], selected_font: ImageFont.FreeTypeFont, fill: tuple[int, int, int], gap: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    rng = random.Random(title)

    img = Image.new("RGB", (W, H), (12, 15, 25))
    draw = ImageDraw.Draw(img, "RGBA")

    for y in range(H):
        t = y / (H - 1)
        r = int(8 + 35 * t)
        g = int(12 + 28 * t)
        b = int(30 + 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    stars = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stars, "RGBA")
    for _ in range(200):
        x = rng.randrange(0, W)
        y = rng.randrange(0, 800)
        alpha = rng.randrange(80, 200)
        size = rng.randrange(1, 4)
        sd.ellipse((x, y, x + size, y + size), fill=(255, 255, 240, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), stars)
    draw = ImageDraw.Draw(img, "RGBA")

    draw.rectangle((0, 1000, W, 1650), fill=(18, 22, 45, 200))
    for y in range(1050, 1640, 25):
        draw.line((0, y, W, y + rng.randrange(-10, 11)), fill=(45, 55, 90, 40), width=3)

    for x in range(80, W, 140):
        h = rng.randrange(100, 280)
        draw.rectangle((x, 1000 - h, x + rng.randrange(50, 100), 1000), fill=(10, 12, 30, 230))
        if rng.random() < 0.4:
            draw.rectangle((x + 15, 1050 - h // 2, x + 30, 1065 - h // 2), fill=(200, 180, 120, 90))

    draw.polygon([(0, H), (700, 1620), (900, 1620), (W, H)], fill=(5, 8, 15, 240))
    path = [(300 + i * 16, 1950 + int(45 * rng.random()) + int(70 * (i / 50))) for i in range(51)]
    draw.line(path, fill=(180, 160, 100, 180), width=6)
    draw.line([(x, y + 8) for x, y in path], fill=(220, 210, 180, 100), width=2)

    compass_x, compass_y = 1350, 500
    draw.ellipse((compass_x - 60, compass_y - 60, compass_x + 60, compass_y + 60), outline=(180, 160, 100, 150), width=4)
    draw.line((compass_x, compass_y - 50, compass_x, compass_y + 50), fill=(180, 160, 100, 120), width=3)
    draw.line((compass_x - 50, compass_y, compass_x + 50, compass_y), fill=(180, 160, 100, 120), width=3)
    draw.polygon([(compass_x, compass_y - 45), (compass_x - 8, compass_y - 15), (compass_x + 8, compass_y - 15)], fill=(200, 50, 50, 180))
    draw.polygon([(compass_x, compass_y + 45), (compass_x - 8, compass_y + 15), (compass_x + 8, compass_y + 15)], fill=(100, 100, 120, 120))

    draw.rectangle((0, 1765, W, H), fill=(5, 8, 15, 255))
    draw.line((190, 1782, W - 190, 1782), fill=(180, 160, 100, 120), width=3)
    title_font = font("georgiab.ttf", 120)
    author_font = font("arialbd.ttf", 52)
    subtitle_font = font("arial.ttf", 34)
    y = 1840
    y = centered(draw, y, ["A CARTOGRAPHIC FANTASY"], subtitle_font, (180, 160, 100), 16)
    y += 60
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1250), title_font, (240, 235, 220), 20)
    y += 100
    centered(draw, y, [author], author_font, (200, 195, 180), 12)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(output_path, "PNG", optimize=True)


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


def _standard_cover_resolve_model(local_vars):
    for key in ("model", "mo", "MODEL"):
        value = local_vars.get(key)
        if value:
            return value
    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("model")
    if value:
        return value
    return ""


def _draw_standard_cover_title_panel(image, title: str = "", author: str = "", model: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(3, 5, 8, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(160, 225, 209, 105), width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (244, 249, 238), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (210, 229, 221), 12, width)
    if not model:
        model = _standard_cover_resolve_model(locals())
    if model:
        mf = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, height - 110, [model], mf, (140, 140, 160), 12, width)
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