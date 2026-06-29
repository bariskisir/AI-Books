#!/usr/bin/env python3
"""Create a book-specific cover for The Luthiers Cipher."""

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


def draw_violin_cipher(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-luthiers-cipher-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(40*(1-t)+22*t), int(28*(1-t)+36*t), int(26*(1-t)+44*t), 255))

    # Workshop wall and bench.
    draw.rectangle((0, 1050, W, 1765), fill=(56, 44, 38, 245))
    for y in range(1080, 1740, 76):
        draw.line((0, y, W, y + random.randint(-8, 8)), fill=(101, 76, 58, 85), width=3)
    draw.rectangle((0, 1515, W, 1765), fill=(92, 64, 42, 248))
    draw.line((0, 1515, W, 1515), fill=(169, 125, 78, 150), width=5)

    # Hanging archive papers and court order.
    for x, y, rot, label in [(145, 335, -8, "EVACUATION"), (1120, 315, 6, "INJUNCTION"), (1010, 875, -5, "BELLER")]:
        paper = Image.new("RGBA", (330, 430), (0, 0, 0, 0))
        pd = ImageDraw.Draw(paper, "RGBA")
        pd.rounded_rectangle((0, 0, 330, 430), radius=14, fill=(231, 219, 183, 235), outline=(91, 69, 47, 170), width=3)
        pd.text((34, 35), label, font=font("arialbd.ttf", 32), fill=(75, 54, 39, 230))
        for i in range(7):
            pd.line((35, 105 + i*38, 290, 105 + i*38), fill=(101, 81, 61, 115), width=3)
        paper = paper.rotate(rot, expand=True, resample=Image.Resampling.BICUBIC)
        draw.bitmap((x, y), paper)

    # Violin body on bench.
    cx, cy = 760, 1110
    varnish = (139, 68, 34, 255)
    glow = (217, 132, 59, 190)
    draw.ellipse((cx - 255, cy - 455, cx + 35, cy - 45), fill=varnish, outline=(63, 34, 25, 230), width=7)
    draw.ellipse((cx - 20, cy - 455, cx + 270, cy - 45), fill=varnish, outline=(63, 34, 25, 230), width=7)
    draw.ellipse((cx - 310, cy - 95, cx - 15, cy + 425), fill=varnish, outline=(63, 34, 25, 230), width=7)
    draw.ellipse((cx + 5, cy - 95, cx + 300, cy + 425), fill=varnish, outline=(63, 34, 25, 230), width=7)
    draw.rectangle((cx - 120, cy - 430, cx + 120, cy + 390), fill=varnish)
    for off in (-95, 95):
        draw.arc((cx + off - 45, cy - 220, cx + off + 55, cy + 40), 82, 278, fill=(48, 26, 20, 235), width=13)
    draw.rounded_rectangle((cx - 42, cy - 560, cx + 42, cy - 255), radius=28, fill=(68, 37, 27, 255))
    draw.rectangle((cx - 98, cy - 575, cx + 98, cy - 515), fill=(55, 31, 23, 255))
    draw.rounded_rectangle((cx - 80, cy + 250, cx + 80, cy + 335), radius=20, fill=(48, 28, 24, 255))
    for x in (cx - 54, cx - 18, cx + 18, cx + 54):
        draw.line((x, cy - 565, x, cy + 320), fill=(226, 211, 174, 210), width=4)
    draw.polygon([(cx - 105, cy + 25), (cx + 105, cy + 25), (cx + 76, cy + 95), (cx - 76, cy + 95)], fill=(228, 198, 132, 245), outline=(80, 48, 31, 210))
    for i in range(18):
        x = cx - 180 + i * 22
        draw.arc((x, cy - 300, x + 360, cy + 420), 255, 287, fill=(glow[0], glow[1], glow[2], 35), width=4)

    # Inner rib cipher magnifier.
    draw.ellipse((1035, 1030, 1390, 1385), fill=(221, 231, 218, 54), outline=(224, 232, 211, 210), width=7)
    draw.line((1305, 1325, 1465, 1495), fill=(62, 47, 38, 230), width=24)
    draw.rounded_rectangle((1085, 1160, 1340, 1268), radius=18, fill=(82, 48, 34, 235), outline=(211, 172, 111, 175), width=4)
    draw.text((1112, 1188), "17 4 9 / B", font=font("arialbd.ttf", 38), fill=(234, 207, 149, 235))

    # Dendrochronology ring chart and varnish sample.
    draw.rounded_rectangle((150, 1225, 545, 1435), radius=18, fill=(22, 28, 27, 210), outline=(218, 184, 124, 120), width=3)
    draw.text((185, 1250), "SPRUCE RING MATCH", font=font("arialbd.ttf", 27), fill=(224, 203, 158, 220))
    for i, x in enumerate(range(185, 510, 16)):
        h = 55 + int(math.sin(i * 1.7) * 32) + random.randint(-8, 8)
        draw.line((x, 1395, x, 1395 - h), fill=(202, 184, 142, 185), width=4)
    draw.rounded_rectangle((1025, 1460, 1370, 1588), radius=14, fill=(235, 224, 190, 230), outline=(85, 58, 38, 190), width=4)
    draw.text((1060, 1490), "VARNISH: AMBER / MADDER", font=font("arialbd.ttf", 24), fill=(77, 55, 39, 230))
    draw.ellipse((1295, 1525, 1332, 1562), fill=(185, 82, 35, 230))

    # Rosin and shavings.
    for _ in range(130):
        x = random.randint(95, 1500)
        y = random.randint(1180, 1660)
        s = random.randint(1, 5)
        draw.ellipse((x, y, x + s, y + s), fill=(228, 193, 126, random.randint(45, 140)))
    for _ in range(36):
        x = random.randint(180, 1420)
        y = random.randint(1470, 1695)
        draw.arc((x, y, x + random.randint(60, 150), y + random.randint(15, 45)), 185, 350, fill=(187, 129, 69, 130), width=3)

    tagline = "VIOLIN PROVENANCE  VARNISH LAYERS  HIDDEN MARK"
    tag_font = font("georgia.ttf", 34)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 285), tagline, font=tag_font, fill=(230, 216, 178, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Luthiers Cipher")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (40, 28, 26, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_violin_cipher(draw)
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
