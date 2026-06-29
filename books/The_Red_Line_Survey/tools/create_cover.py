#!/usr/bin/env python3
"""Create a custom cover for The Red Line Survey."""

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


def draw_survey_scene(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.55:
            c = lerp((24, 33, 35), (72, 83, 72), t / 0.55)
        else:
            c = lerp((72, 83, 72), (28, 25, 22), (t - 0.55) / 0.45)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Mountain ridges and old plat paper.
    for ridge, color in [
        ([(0, 720), (210, 610), (430, 700), (650, 560), (890, 690), (1120, 545), (1600, 705), (1600, 1180), (0, 1180)], (46, 66, 62, 230)),
        ([(0, 980), (270, 830), (520, 920), (820, 760), (1100, 930), (1400, 790), (1600, 900), (1600, 1390), (0, 1390)], (57, 78, 68, 240)),
    ]:
        draw.polygon(ridge, fill=color)

    paper = [(205, 320), (1395, 250), (1460, 1515), (155, 1585)]
    draw.polygon(paper, fill=(222, 211, 177, 232), outline=(92, 76, 52, 170))
    for x in range(260, 1360, 120):
        draw.line((x, 330, x - 95, 1560), fill=(116, 94, 62, 70), width=2)
    for y in range(420, 1510, 110):
        draw.line((190, y, 1430, y - 75), fill=(116, 94, 62, 62), width=2)

    # Topographic contours.
    for i in range(16):
        y = 525 + i * 58
        draw.arc((250 - i * 10, y - 120, 1380 + i * 12, y + 260), 190, 350, fill=(77, 99, 72, 92), width=4)

    # Cemetery stones and spring.
    for i in range(12):
        x = 340 + (i % 6) * 86
        y = 1010 + (i // 6) * 95
        draw.rounded_rectangle((x, y, x + 42, y + 72), radius=16, fill=(182, 180, 160, 235), outline=(82, 78, 68, 150), width=3)
    draw.ellipse((1035, 1115, 1225, 1245), fill=(68, 126, 142, 190), outline=(184, 224, 218, 190), width=5)
    for i in range(4):
        draw.arc((1020 - i * 20, 1100 - i * 12, 1240 + i * 20, 1260 + i * 14), 20, 180, fill=(170, 218, 210, 95), width=3)

    # Survey monument and tripod.
    draw.polygon([(744, 836), (857, 820), (905, 1325), (700, 1340)], fill=(102, 96, 82, 245), outline=(48, 42, 34, 180))
    draw.ellipse((715, 790, 875, 860), fill=(185, 151, 82, 245), outline=(82, 66, 42, 190), width=5)
    draw.text((747, 813), "1983", font=font("arialbd.ttf", 28), fill=(60, 45, 28, 230))
    draw.line((1260, 520, 1185, 1190), fill=(38, 42, 40, 230), width=8)
    draw.line((1260, 520, 1320, 1220), fill=(38, 42, 40, 230), width=8)
    draw.line((1260, 520, 1260, 1180), fill=(38, 42, 40, 230), width=8)
    draw.rectangle((1218, 455, 1302, 535), fill=(60, 68, 72, 245), outline=(220, 204, 142, 170), width=4)

    # Red fraud line cuts across graves, spring, and claim.
    pts = [(220, 1330), (425, 1170), (620, 1085), (805, 1010), (980, 930), (1190, 770), (1375, 575)]
    for width, alpha in [(26, 70), (13, 238)]:
        for a, b in zip(pts, pts[1:]):
            draw.line((*a, *b), fill=(188, 24, 36, alpha), width=width)
    for p in pts:
        draw.ellipse((p[0] - 11, p[1] - 11, p[0] + 11, p[1] + 11), fill=(196, 26, 36, 235))

    # Blue corrected line follows ridge.
    blue = [(250, 760), (500, 700), (730, 620), (970, 675), (1250, 610), (1425, 650)]
    for a, b in zip(blue, blue[1:]):
        draw.line((*a, *b), fill=(54, 112, 205, 180), width=7)

    # Coordinate grid and evidence labels.
    draw.rectangle((275, 1370, 650, 1495), fill=(238, 228, 190, 230), outline=(78, 62, 45, 170), width=3)
    draw.text((300, 1400), "RIDGE-4", font=font("arialbd.ttf", 36), fill=(52, 44, 36, 230))
    draw.text((300, 1447), "BASE POINT SPOOFED", font=font("arial.ttf", 26), fill=(126, 32, 38, 235))
    for _ in range(120):
        x = random.randint(250, 1410)
        y = random.randint(360, 1510)
        if random.random() < 0.55:
            draw.rectangle((x, y, x + 3, y + 3), fill=(70, 57, 38, random.randint(45, 95)))

    # Drone/GPS signal arcs.
    signal = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(signal, "RGBA")
    for i in range(7):
        sd.arc((930 - i * 80, 210 - i * 36, 1590 + i * 40, 910 + i * 70), 200, 290, fill=(225, 232, 190, 60), width=5)
    signal = signal.filter(ImageFilter.GaussianBlur(0.7))
    draw.bitmap((0, 0), signal, fill=None)

    tagline = "BOUNDARY FRAUD  GPS SPOOFING  LAND RECORDS"
    tag_font = font("georgia.ttf", 36)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 270), tagline, font=tag_font, fill=(232, 220, 184, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Red Line Survey")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("the-red-line-survey-cover")
    image = Image.new("RGBA", (W, H), (18, 20, 22, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_survey_scene(draw)
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
    draw.rectangle((0, panel_y, width, height), fill=(235, 229, 211, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(88, 78, 60, 170), width=3)
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
    _standard_cover_center(draw, y, [author], author_font, (86, 80, 66), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (112, 106, 92), 6, width)


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
