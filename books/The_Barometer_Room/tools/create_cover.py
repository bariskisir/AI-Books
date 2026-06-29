#!/usr/bin/env python3
"""Create a book-specific cover for The Barometer Room."""

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
    candidates = [
        FONT_DIR / name,
        FONT_DIR / "arialbd.ttf",
        FONT_DIR / "arial.ttf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def vertical_gradient(draw: ImageDraw.ImageDraw, top, bottom) -> None:
    for y in range(H):
        t = y / max(1, H - 1)
        col = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3)) + (255,)
        draw.line((0, y, W, y), fill=col)


def draw_storm_harbor(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-barometer-room-cover")
    vertical_gradient(draw, (20, 34, 48), (8, 18, 29))

    # Rain bands and distant lightning.
    for _ in range(420):
        x = random.randint(-100, W + 100)
        y = random.randint(0, 1660)
        length = random.randint(42, 95)
        alpha = random.randint(34, 92)
        draw.line((x, y, x - 20, y + length), fill=(166, 190, 207, alpha), width=random.randint(1, 3))
    bolt = [(1120, 150), (1078, 305), (1140, 300), (1056, 520), (1100, 390), (1048, 400)]
    draw.line(bolt, fill=(228, 238, 215, 130), width=5)
    draw.line(bolt, fill=(141, 202, 223, 80), width=13)

    # Harbor silhouette: cranes, warehouses, and flooded quay.
    draw.rectangle((0, 1225, W, 1765), fill=(14, 29, 38, 245))
    for x in range(80, W, 245):
        draw.rectangle((x, 1080 + (x % 3) * 32, x + 155, 1228), fill=(22, 38, 44, 245))
        draw.rectangle((x + 22, 1130, x + 50, 1228), fill=(206, 190, 112, 95))
    for base in (260, 650, 1060, 1350):
        draw.line((base, 1215, base + 85, 930), fill=(29, 45, 51, 250), width=14)
        draw.line((base + 85, 930, base + 260, 1030), fill=(29, 45, 51, 250), width=10)
        draw.line((base + 85, 930, base - 38, 1040), fill=(29, 45, 51, 220), width=8)
    for y in range(1330, 1765, 38):
        draw.line((0, y, W, y + random.randint(-18, 18)), fill=(66, 105, 123, 85), width=3)
    for _ in range(65):
        x = random.randint(0, W)
        y = random.randint(1340, 1705)
        draw.line((x, y, x + random.randint(40, 130), y + random.randint(-8, 8)), fill=(190, 211, 202, random.randint(35, 85)), width=2)

    # Main analog barograph chart.
    chart = (190, 425, 1410, 980)
    draw.rounded_rectangle(chart, radius=18, fill=(229, 224, 205, 240), outline=(76, 66, 54, 230), width=7)
    for gx in range(chart[0] + 60, chart[2] - 20, 100):
        draw.line((gx, chart[1] + 30, gx, chart[3] - 35), fill=(130, 116, 96, 55), width=2)
    for gy in range(chart[1] + 65, chart[3] - 20, 70):
        draw.line((chart[0] + 40, gy, chart[2] - 40, gy), fill=(130, 116, 96, 55), width=2)
    draw.text((chart[0] + 54, chart[1] + 36), "BAROMETER ROOM TRACE", font=font("arialbd.ttf", 32), fill=(62, 55, 48, 235))
    points = []
    for i in range(0, 1080, 20):
        t = i / 1080
        x = chart[0] + 70 + i
        if t < 0.42:
            y = 650 + math.sin(t * 24) * 16 + random.randint(-4, 4)
        elif t < 0.62:
            y = 650 + (t - 0.42) * 980 + random.randint(-7, 7)
        else:
            y = 845 + (t - 0.62) * 145 + math.sin(t * 18) * 10
        points.append((x, min(chart[3] - 55, int(y))))
    draw.line(points, fill=(114, 24, 31, 245), width=7, joint="curve")
    draw.ellipse((1000, 772, 1038, 810), fill=(114, 24, 31, 245))
    draw.text((1048, 755), "18:31", font=font("arialbd.ttf", 36), fill=(114, 24, 31, 245))

    # Buoy B-17 and dashboard warning panel.
    draw.ellipse((255, 1088, 428, 1205), fill=(214, 96, 51, 245), outline=(252, 218, 163, 190), width=6)
    draw.rectangle((318, 1008, 365, 1110), fill=(218, 222, 210, 230))
    draw.polygon([(342, 950), (300, 1015), (384, 1015)], fill=(238, 221, 170, 210), outline=(59, 65, 63, 180))
    draw.text((228, 1228), "B-17", font=font("arialbd.ttf", 46), fill=(237, 223, 170, 230))
    draw.line((430, 1118, 640, 910), fill=(238, 211, 113, 145), width=5)
    for r in (60, 105, 150):
        draw.arc((342 - r, 990 - r, 342 + r, 990 + r), 214, 326, fill=(238, 211, 113, 120), width=4)

    panel = (995, 1050, 1425, 1370)
    draw.rounded_rectangle(panel, radius=14, fill=(18, 31, 38, 235), outline=(167, 194, 190, 155), width=4)
    draw.text((1030, 1088), "HARBORVIEW", font=font("arialbd.ttf", 34), fill=(190, 220, 210, 230))
    draw.rectangle((1030, 1142, 1390, 1210), fill=(182, 64, 55, 235))
    draw.text((1054, 1156), "PRESSURE RATE CRITICAL", font=font("arialbd.ttf", 27), fill=(246, 233, 202, 245))
    draw.text((1030, 1248), "DISPLAY SMOOTHING OFF", font=font("arialbd.ttf", 28), fill=(229, 210, 142, 225))
    draw.text((1030, 1292), "RAW ARCHIVE PRESERVED", font=font("arial.ttf", 27), fill=(187, 207, 196, 218))

    # Interior brass instrument ghosted over the sky.
    draw.ellipse((635, 1040, 940, 1345), outline=(187, 143, 70, 150), width=11)
    draw.ellipse((690, 1095, 885, 1290), outline=(229, 194, 108, 110), width=5)
    for angle in range(210, 331, 20):
        rad = math.radians(angle)
        cx, cy = 787, 1192
        x1 = cx + math.cos(rad) * 80
        y1 = cy + math.sin(rad) * 80
        x2 = cx + math.cos(rad) * 96
        y2 = cy + math.sin(rad) * 96
        draw.line((x1, y1, x2, y2), fill=(223, 190, 116, 120), width=3)
    draw.line((787, 1192, 706, 1158), fill=(229, 194, 108, 180), width=6)
    draw.ellipse((776, 1181, 798, 1203), fill=(229, 194, 108, 190))

    tagline = "STORM DATA  HARBOR WARNING  FALLING PRESSURE"
    tag_font = font("georgia.ttf", 35)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(224, 218, 188, 224))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Barometer Room")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (12, 18, 24, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_storm_harbor(draw)
    veil = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vd = ImageDraw.Draw(veil, "RGBA")
    vd.rectangle((0, 0, W, 1765), fill=(5, 12, 18, 34))
    image.alpha_composite(veil.filter(ImageFilter.GaussianBlur(1.2)))
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
    draw.rectangle((0, panel_y, width, height), fill=(232, 228, 214, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(63, 82, 86, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (38, 52, 56), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (72, 82, 78), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (102, 112, 104), 6, width)


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
