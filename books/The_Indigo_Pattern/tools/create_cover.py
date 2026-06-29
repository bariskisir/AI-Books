#!/usr/bin/env python3
"""Create a custom cover for The Indigo Pattern."""

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


def draw_couture_scene(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.5:
            c = lerp((17, 22, 35), (34, 49, 76), t / 0.5)
        else:
            c = lerp((34, 49, 76), (14, 14, 20), (t - 0.5) / 0.5)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Pattern paper worktable.
    draw.polygon([(170, 1450), (1430, 1450), (1320, 1638), (280, 1640)], fill=(214, 196, 156, 235), outline=(100, 78, 54, 160))
    for x in range(250, 1350, 95):
        draw.line((x, 1465, x - 70, 1632), fill=(124, 96, 60, 80), width=3)
    for y in range(1480, 1630, 36):
        draw.line((220, y, 1380, y + random.randint(-8, 8)), fill=(124, 96, 60, 70), width=2)

    # Indigo couture gown on a dress form.
    cx = W // 2
    draw.rectangle((cx - 40, 255, cx + 40, 475), fill=(76, 61, 52, 255))
    draw.ellipse((cx - 85, 215, cx + 85, 310), fill=(178, 164, 138, 255), outline=(90, 70, 54, 150))
    bodice = [(cx - 175, 470), (cx + 170, 470), (cx + 115, 895), (cx - 110, 895)]
    skirt = [(cx - 125, 875), (cx + 125, 875), (cx + 405, 1428), (cx - 410, 1428)]
    draw.polygon(skirt, fill=(12, 38, 91, 245), outline=(82, 110, 156, 180))
    draw.polygon(bodice, fill=(16, 48, 112, 252), outline=(118, 146, 190, 190))
    draw.arc((cx - 176, 415, cx + 180, 645), 20, 160, fill=(198, 214, 230, 210), width=6)
    draw.line((cx - 150, 480, cx + 95, 895), fill=(88, 124, 186, 180), width=9)
    for i in range(16):
        x = cx - 360 + i * 48
        draw.line((cx, 900, x, 1420), fill=(40, 70, 130, 100), width=4)

    # Pale glove, steamer head, and blue dust trail.
    draw.rounded_rectangle((250, 1135, 500, 1245), radius=24, fill=(230, 222, 205, 235), outline=(80, 70, 62, 160), width=3)
    for i in range(5):
        draw.rounded_rectangle((270 + i * 40, 1070 - i * 5, 307 + i * 40, 1150), radius=16, fill=(232, 225, 208, 230), outline=(86, 76, 66, 120), width=2)
    draw.ellipse((1148, 1168, 1305, 1328), fill=(66, 74, 82, 245), outline=(198, 184, 150, 170), width=5)
    draw.rectangle((1210, 1300, 1248, 1465), fill=(70, 78, 84, 235))
    for _ in range(180):
        x = random.randint(260, 1290)
        y = int(1120 + 250 * math.sin((x - 260) / 150) + random.randint(-38, 38))
        if 250 < y < 1480:
            s = random.randint(2, 6)
            draw.ellipse((x, y, x + s, y + s), fill=(42, 82, 184, random.randint(90, 210)))

    # Missing pattern book and labeled evidence tag.
    draw.rectangle((185, 520, 480, 760), fill=(88, 62, 44, 245), outline=(210, 174, 112, 170), width=5)
    draw.rectangle((220, 555, 455, 715), fill=(222, 204, 160, 235))
    draw.ellipse((390, 568, 445, 618), fill=(92, 54, 35, 130))
    draw.text((242, 610), "IDA SAYEGH", font=font("arialbd.ttf", 31), fill=(42, 36, 32, 230))
    draw.text((242, 653), "CRESCENT DRAFT", font=font("arial.ttf", 26), fill=(64, 50, 42, 225))

    # Thread arcs and cutting notches around the dress.
    for i in range(9):
        y = 615 + i * 72
        draw.arc((210, y, 1390, y + 280), 190, 350, fill=(118, 150, 222, 55), width=3)
    for x, y in [(570, 770), (1010, 760), (640, 1080), (960, 1110)]:
        draw.polygon([(x, y), (x + 28, y + 8), (x + 8, y + 35)], fill=(236, 226, 188, 230))

    # Soft steam cloud over neckline.
    cloud = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud, "RGBA")
    for _ in range(28):
        x = random.randint(cx - 260, cx + 260)
        y = random.randint(410, 690)
        cd.arc((x - 160, y - 45, x + 160, y + 85), 185, 355, fill=(220, 226, 218, random.randint(35, 82)), width=random.randint(5, 12))
    cloud = cloud.filter(ImageFilter.GaussianBlur(1.8))
    draw.bitmap((0, 0), cloud, fill=None)

    tagline = "TEXTILE FORENSICS  ARCHIVE  COUTURE"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(232, 220, 184, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Indigo Pattern")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("the-indigo-pattern-cover")
    image = Image.new("RGBA", (W, H), (14, 16, 22, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_couture_scene(draw)
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
    draw.rectangle((0, panel_y, width, height), fill=(235, 231, 216, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(58, 72, 104, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (38, 46, 62), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (72, 78, 88), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (108, 108, 100), 6, width)


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
