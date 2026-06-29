#!/usr/bin/env python3
"""Create a book-specific cover for The Typefounders Proof."""

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


def draw_typefounders_proof(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-typefounders-proof-cover")
    for y in range(H):
        t = y / H
        r = int(39 * (1 - t) + 55 * t)
        g = int(36 * (1 - t) + 44 * t)
        b = int(31 * (1 - t) + 34 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow, "RGBA")
    for r in range(140, 720, 90):
        gd.ellipse((800 - r, 760 - r, 800 + r, 760 + r), outline=(229, 195, 126, max(8, 58 - r // 14)), width=18)
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    draw.bitmap((0, 0), glow)

    # Printer's stone and proof sheet.
    draw.rounded_rectangle((175, 260, 1425, 1185), radius=30, fill=(36, 38, 35, 244), outline=(188, 164, 106, 120), width=5)
    draw.rounded_rectangle((395, 340, 1205, 1075), radius=16, fill=(232, 222, 190, 242), outline=(87, 70, 46, 160), width=4)
    draw.text((455, 405), "BELL & VALE PRESSWORKS", font=font("georgia.ttf", 43), fill=(54, 45, 34, 235))
    draw.line((455, 470, 1140, 470), fill=(102, 82, 53, 150), width=4)
    proof_lines = [
        "TRUST TRANSFER PROOF",
        "set and approved, 1889",
        "worker clause dissolved",
        "witnessed under foundry seal",
    ]
    for i, line in enumerate(proof_lines):
        draw.text((485, 535 + i * 68), line, font=font("cour.ttf", 34), fill=(44, 39, 32, 225))
    draw.rectangle((500, 845, 1110, 915), outline=(122, 45, 38, 190), width=5)
    draw.text((535, 860), "LOWERCASE e: WRONG WOUND", font=font("arialbd.ttf", 30), fill=(122, 45, 38, 230))
    draw.text((725, 665), "e", font=font("georgiab.ttf", 190), fill=(45, 40, 33, 235))
    draw.arc((815, 735, 875, 795), 200, 320, fill=(142, 36, 34, 235), width=9)

    # Type cases.
    for base_x, base_y in [(145, 1240), (925, 1235)]:
        draw.rounded_rectangle((base_x, base_y, base_x + 530, base_y + 360), radius=16, fill=(83, 61, 42, 235), outline=(191, 147, 91, 130), width=4)
        for row in range(4):
            for col in range(6):
                x0 = base_x + 24 + col * 80
                y0 = base_y + 24 + row * 74
                draw.rectangle((x0, y0, x0 + 64, y0 + 56), fill=(38, 32, 28, 230), outline=(128, 96, 61, 150), width=2)
                letter = random.choice("etaoinshrdlucm")
                color = (224, 210, 172, 210) if random.random() > 0.16 else (154, 48, 42, 230)
                draw.text((x0 + 20, y0 + 5), letter, font=font("georgiab.ttf", 36), fill=color)
    draw.text((245, 1625), "TYPE CASE", font=font("arialbd.ttf", 28), fill=(222, 196, 139, 220))
    draw.text((1035, 1620), "SUBSTITUTE SORTS", font=font("arialbd.ttf", 28), fill=(222, 196, 139, 220))

    # Press roller and galley.
    draw.rounded_rectangle((230, 1710, 1370, 1825), radius=22, fill=(30, 31, 30, 242), outline=(198, 165, 99, 120), width=4)
    draw.rectangle((325, 1742, 1275, 1792), fill=(10, 11, 10, 240))
    for x in range(345, 1225, 60):
        draw.text((x, 1737), random.choice(["A", "E", "R", "T", "9", "&"]), font=font("georgiab.ttf", 42), fill=(221, 211, 178, 210))
    draw.line((245, 1865, 1340, 1865), fill=(183, 141, 82, 190), width=10)
    for x in range(290, 1300, 125):
        draw.line((x, 1850, x + 80, 1910), fill=(125, 92, 56, 170), width=4)

    # Evidence cards.
    cards = [
        ((130, 760, 335, 975), "WATERMARK", "1894"),
        ((1265, 760, 1480, 975), "INK PEAK", "MODERN"),
        ((150, 450, 335, 655), "ALLOY", "1902"),
        ((1265, 450, 1478, 655), "LIGATURE", "1896"),
    ]
    for box, label, value in cards:
        draw.rounded_rectangle(box, radius=13, fill=(225, 214, 178, 232), outline=(75, 58, 38, 155), width=3)
        draw.text((box[0] + 22, box[1] + 38), label, font=font("arialbd.ttf", 25), fill=(52, 44, 33, 230))
        draw.text((box[0] + 35, box[1] + 105), value, font=font("arialbd.ttf", 36), fill=(128, 44, 39, 230))

    # Scattered proof marks and matrix numbers.
    for _ in range(115):
        x = random.randint(90, 1510)
        y = random.randint(245, 1720)
        alpha = random.randint(35, 115)
        mark = random.choice(["e", "fi", "BV", "1902", "*", "M"])
        draw.text((x, y), mark, font=font("cour.ttf", random.randint(18, 30)), fill=(231, 215, 169, alpha))

    tagline = "LETTERPRESS  MATRICES  INK CHEMISTRY"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 185), tagline, font=tag_font, fill=(230, 210, 161, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Typefounders Proof")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (39, 36, 31, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_typefounders_proof(draw)
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
