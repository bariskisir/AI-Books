#!/usr/bin/env python3
"""Create a book-specific cover for The Sable Equation."""

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


def draw_sable_equation(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-sable-equation-cover")
    for y in range(H):
        t = y / H
        r = int(16 * (1 - t) + 36 * t)
        g = int(19 * (1 - t) + 31 * t)
        b = int(23 * (1 - t) + 37 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog, "RGBA")
    for y0 in range(280, 1320, 150):
        fd.ellipse((-260, y0, W + 280, y0 + 250), fill=(180, 190, 178, 18))
    fog = fog.filter(ImageFilter.GaussianBlur(22))
    draw.bitmap((0, 0), fog)

    # Actuarial equation board.
    draw.rounded_rectangle((160, 270, 1440, 720), radius=26, fill=(22, 31, 29, 235), outline=(155, 178, 150, 120), width=4)
    draw.text((215, 320), "LOSS RATIO = CLAIMS / PREMIUM", font=font("arialbd.ttf", 54), fill=(226, 225, 196, 235))
    draw.text((235, 405), "S-14: low premium + high expected loss + reinsurance recovery", font=font("arial.ttf", 34), fill=(193, 209, 188, 215))
    draw.text((235, 465), "address rank  clinic distance  payment friction  reserve gap", font=font("arial.ttf", 32), fill=(157, 177, 164, 210))
    draw.line((235, 555, 1310, 555), fill=(95, 122, 105, 180), width=5)
    for x, label, val in [(265, "PREMIUM", "LOW"), (545, "CLAIMS", "HIGH"), (815, "RESERVE", "LOW"), (1080, "RECOVERY", "HIGH")]:
        draw.rounded_rectangle((x, 590, x + 210, 665), radius=10, fill=(235, 226, 195, 220), outline=(85, 72, 55, 160), width=2)
        draw.text((x + 22, 605), label, font=font("arialbd.ttf", 25), fill=(53, 48, 42, 235))
        draw.text((x + 68, 633), val, font=font("arialbd.ttf", 27), fill=(128, 45, 44, 235))

    # Street cluster map with S-14 target.
    map_box = (155, 810, 680, 1390)
    draw.rounded_rectangle(map_box, radius=22, fill=(229, 219, 188, 232), outline=(80, 68, 51, 165), width=4)
    draw.text((205, 850), "ADDRESS CLUSTER", font=font("arialbd.ttf", 36), fill=(56, 49, 39, 235))
    for i in range(8):
        y = 930 + i * 48
        draw.line((210, y, 620, y + random.randint(-16, 16)), fill=(102, 107, 87, 150), width=5)
    for i in range(6):
        x = 245 + i * 60
        draw.line((x, 925, x + random.randint(-30, 40), 1295), fill=(102, 107, 87, 120), width=4)
    cluster = [(375, 1055), (422, 1090), (462, 1148), (405, 1215), (335, 1190), (315, 1110)]
    draw.polygon(cluster, fill=(116, 25, 31, 105), outline=(158, 42, 48, 235))
    draw.text((372, 1128), "S-14", font=font("arialbd.ttf", 44), fill=(97, 18, 23, 245))
    for _ in range(35):
        x = random.randint(230, 600)
        y = random.randint(965, 1285)
        color = (42, 54, 48, 220) if random.random() > 0.24 else (142, 31, 35, 240)
        draw.ellipse((x, y, x + 12, y + 12), fill=color)

    # Reinsurance and ledger stack.
    draw.rounded_rectangle((840, 815, 1430, 1395), radius=22, fill=(28, 31, 34, 232), outline=(180, 158, 104, 135), width=4)
    draw.text((895, 855), "REINSURANCE LAYER", font=font("arialbd.ttf", 36), fill=(231, 213, 168, 235))
    layers = [("POLICIES", 1015, (63, 83, 76)), ("S-14 POOL", 1110, (95, 42, 45)), ("SIDE LETTER", 1205, (122, 93, 54)), ("RECOVERY", 1300, (42, 72, 83))]
    for label, y, color in layers:
        draw.rounded_rectangle((910, y, 1345, y + 58), radius=8, fill=(*color, 230), outline=(225, 211, 176, 105), width=2)
        draw.text((960, y + 13), label, font=font("arialbd.ttf", 28), fill=(236, 230, 201, 235))
    draw.line((1128, 985, 1128, 1320), fill=(223, 196, 132, 210), width=8)
    draw.polygon([(1128, 1350), (1097, 1303), (1159, 1303)], fill=(223, 196, 132, 210))

    # Mortality table and claim envelopes.
    draw.rounded_rectangle((170, 1445, 730, 1700), radius=18, fill=(224, 218, 192, 225), outline=(72, 64, 50, 150), width=3)
    draw.text((215, 1480), "CLEAN MORTALITY TABLE", font=font("arialbd.ttf", 31), fill=(48, 45, 38, 235))
    for i in range(5):
        y = 1545 + i * 30
        draw.line((215, y, 675, y), fill=(111, 110, 91, 130), width=2)
        draw.text((230, y + 5), f"{45+i*5}", font=font("arial.ttf", 21), fill=(58, 55, 47, 210))
        draw.rectangle((320, y + 8, 320 + 42 + i * 39, y + 22), fill=(63, 93, 86, 205))
    for i, x in enumerate((850, 1035, 1220)):
        y = 1465 + i * 50
        draw.polygon([(x, y), (x + 290, y + 35), (x + 260, y + 170), (x - 30, y + 135)], fill=(232, 221, 190, 230), outline=(88, 74, 51, 150))
        draw.line((x, y, x + 122, y + 103), fill=(132, 45, 45, 170), width=4)
        draw.text((x + 45, y + 78), "CLAIM REVIEW", font=font("arialbd.ttf", 22), fill=(62, 52, 39, 220))

    for _ in range(120):
        x = random.randint(80, 1520)
        y = random.randint(230, 1710)
        alpha = random.randint(35, 130)
        draw.text((x, y), random.choice(["0", "1", "+", "=", "%"]), font=font("arial.ttf", random.randint(16, 28)), fill=(192, 205, 183, alpha))

    tagline = "ACTUARIAL AUDIT  PROXY BIAS  BURIAL CLAIMS"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 190), tagline, font=tag_font, fill=(229, 219, 181, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Sable Equation")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (16, 19, 23, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_sable_equation(draw)
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
