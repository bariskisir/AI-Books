#!/usr/bin/env python3
"""Create a book-specific cover for The Gravity Orchestra."""

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


def draw_orbit_scene(draw: ImageDraw.ImageDraw) -> None:
    random.seed("the-gravity-orchestra-cover")
    for y in range(H):
        t = y / H
        draw.line((0, y, W, y), fill=(int(3*(1-t)+14*t), int(13*(1-t)+26*t), int(31*(1-t)+45*t), 255))

    # Stars.
    for _ in range(220):
        x = random.randint(0, W)
        y = random.randint(40, 1510)
        s = random.randint(1, 4)
        a = random.randint(80, 210)
        draw.ellipse((x, y, x+s, y+s), fill=(220, 232, 236, a))

    # Earth limb.
    earth = Image.new("RGBA", (W, H), (0,0,0,0))
    ed = ImageDraw.Draw(earth, "RGBA")
    ed.ellipse((-340, 1110, 1940, 2770), fill=(23, 79, 104, 255), outline=(106, 191, 205, 210), width=12)
    ed.ellipse((-300, 1160, 1900, 2730), outline=(185, 229, 228, 70), width=28)
    for _ in range(30):
        x = random.randint(80, 1500)
        y = random.randint(1290, 1690)
        ed.arc((x-210, y-45, x+210, y+90), 190, 355, fill=(235, 245, 241, random.randint(45, 95)), width=random.randint(4, 10))
    draw.bitmap((0,0), earth.filter(ImageFilter.GaussianBlur(0.4)), fill=None)

    # Resonance arcs and falling debris.
    cx, cy = 800, 1180
    for r, col in [(480, (102, 184, 210, 130)), (610, (238, 191, 96, 130)), (740, (145, 216, 194, 110))]:
        draw.arc((cx-r, cy-r, cx+r, cy+r), 200, 345, fill=col, width=5)
    for _ in range(95):
        ang = random.uniform(math.radians(205), math.radians(345))
        r = random.choice([480, 610, 740]) + random.randint(-18, 18)
        x = cx + math.cos(ang)*r
        y = cy + math.sin(ang)*r
        draw.line((x, y, x+random.randint(18, 58), y+random.randint(4, 25)), fill=(230, 214, 160, random.randint(90, 190)), width=random.randint(2, 5))

    # Salvage tug.
    tx, ty = 690, 820
    draw.rounded_rectangle((tx-115, ty-45, tx+120, ty+55), radius=18, fill=(218, 224, 219, 240), outline=(93, 117, 126, 220), width=5)
    draw.rectangle((tx-55, ty-105, tx+55, ty-45), fill=(90, 130, 148, 230))
    draw.rectangle((tx-185, ty-25, tx-115, ty+25), fill=(70, 94, 112, 230))
    draw.rectangle((tx+120, ty-25, tx+205, ty+25), fill=(70, 94, 112, 230))
    draw.line((tx+125, ty+20, tx+290, ty+110), fill=(220, 222, 210, 220), width=8)
    draw.line((tx+290, ty+110, tx+365, ty+72), fill=(220, 222, 210, 220), width=8)
    draw.ellipse((tx+350, ty+55, tx+395, ty+100), outline=(220, 222, 210, 220), width=7)
    draw.polygon([(tx-170, ty-58), (tx-245, ty-160), (tx-110, ty-95)], fill=(54, 84, 108, 210))
    draw.text((tx-90, ty-12), "LITTLE", font=font("arialbd.ttf", 26), fill=(37, 51, 58, 220))

    # Satellites.
    for sx, sy, rot in [(360, 600, -12), (1170, 560, 18), (1110, 1005, -28)]:
        draw.rectangle((sx-42, sy-28, sx+42, sy+28), fill=(190, 194, 186, 230), outline=(88, 99, 108, 200), width=3)
        draw.rectangle((sx-150, sy-18, sx-50, sy+18), fill=(38, 90, 120, 220))
        draw.rectangle((sx+50, sy-18, sx+150, sy+18), fill=(38, 90, 120, 220))
        draw.line((sx-150, sy, sx+150, sy), fill=(162, 198, 204, 120), width=2)

    # Anchor platform silhouette.
    draw.rounded_rectangle((510, 1220, 1090, 1390), radius=28, fill=(48, 63, 78, 240), outline=(148, 169, 176, 190), width=5)
    draw.text((605, 1274), "ANCHOR NINE", font=font("arialbd.ttf", 40), fill=(211, 221, 213, 225))
    draw.rectangle((455, 1265, 510, 1345), fill=(91, 112, 122, 230))
    draw.rectangle((1090, 1265, 1148, 1345), fill=(91, 112, 122, 230))

    tagline = "ORBITAL DEBRIS  SALVAGE TUG  USABLE SKY"
    tag_font = font("georgia.ttf", 38)
    bb = draw.textbbox((0, 0), tagline, font=tag_font)
    draw.text(((W - (bb[2] - bb[0])) // 2, 305), tagline, font=tag_font, fill=(226, 232, 215, 230))


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Gravity Orchestra")
    author = metadata.get("author", "Bar\u0131\u015f K\u0131s\u0131r")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (4, 10, 25, 255))
    draw = ImageDraw.Draw(image, "RGBA")
    draw_orbit_scene(draw)
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
    draw.rectangle((0, panel_y, width, height), fill=(228, 231, 219, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(55, 84, 108, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (24, 42, 56), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (66, 82, 88), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (98, 108, 108), 6, width)


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
