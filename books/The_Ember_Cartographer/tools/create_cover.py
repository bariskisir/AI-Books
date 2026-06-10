#!/usr/bin/env python3
"""Custom PIL cover generator."""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

def _scene(image, scene: str, title: str) -> None:
    random.seed(title)
    draw = ImageDraw.Draw(image, "RGBA")
    def gradient(a, b):
        for y in range(H):
            t = y / H
            draw.line((0, y, W, y), fill=tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,))
    if scene == "apothecary":
        gradient((16, 26, 29), (61, 83, 66))
        draw.ellipse((1030, 170, 1400, 540), fill=(232, 226, 186, 185))
        for x in range(120, W, 210):
            draw.rectangle((x, 260, x + 90, 1350), fill=(30, 42, 38, 210), outline=(160, 185, 150, 80), width=3)
            for y in range(330, 1260, 150):
                draw.line((x, y, x + 90, y), fill=(185, 205, 164, 70), width=2)
                draw.ellipse((x + 25, y - 56, x + 65, y - 16), fill=(226, 236, 202, 95))
        for i in range(22):
            bx = 230 + i * 52
            by = 1160 + int(80 * math.sin(i))
            draw.line((bx, by, bx + 35, by - 250), fill=(86, 128, 92, 180), width=5)
            draw.ellipse((bx + 8, by - 280, bx + 74, by - 214), fill=(225, 232, 196, 150))
        draw.rectangle((190, 1320, 1410, 1530), fill=(19, 24, 24, 180), outline=(209, 194, 142, 110), width=4)
    elif scene == "sundial":
        gradient((38, 32, 25), (132, 95, 45))
        cx, cy = W // 2, 900
        for r in range(620, 80, -42):
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(222, 184, 104, 30 + r // 18), width=5)
        for a in range(0, 360, 15):
            rad = math.radians(a)
            draw.line((cx + math.cos(rad) * 150, cy + math.sin(rad) * 150, cx + math.cos(rad) * 590, cy + math.sin(rad) * 590), fill=(238, 204, 129, 80), width=3)
        draw.polygon([(cx, cy - 360), (cx + 78, cy + 70), (cx - 40, cy + 35)], fill=(38, 29, 20, 230), outline=(240, 198, 112, 160))
        draw.line((cx, cy, cx + 470, cy + 65), fill=(5, 5, 5, 185), width=22)
        for i in range(12):
            x = 210 + (i % 4) * 310
            y = 260 + (i // 4) * 145
            draw.arc((x, y, x + 170, y + 170), 0, 300, fill=(230, 190, 95, 120), width=7)
    else:
        gradient((21, 27, 31), (116, 48, 35))
        draw.polygon([(150, 1360), (550, 520), (850, 1040), (1110, 450), (1460, 1360)], fill=(46, 39, 36, 245), outline=(204, 92, 45, 160))
        for r in range(520, 40, -30):
            draw.ellipse((800-r, 780-r, 800+r, 780+r), fill=(233, 95, 41, max(0, 90 - r // 7)))
        for i in range(18):
            x = random.randint(150, 1450)
            y = random.randint(220, 1350)
            draw.line((x, y, x + random.randint(-80, 80), y + random.randint(120, 260)), fill=(218, 82, 39, 90), width=random.randint(2, 5))
        draw.rectangle((245, 1340, 1355, 1530), fill=(230, 210, 160, 170), outline=(63, 44, 34, 190), width=5)

def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    image = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    _scene(image, metadata.get("cover_scene", ""), title)
    _draw_standard_cover_title_panel(image, _standard_cover_resolve_title(locals()), author, model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.convert("RGB").save(output_path, "PNG", optimize=True)

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    make_cover(ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata, ROOT / args.out if not args.out.is_absolute() else args.out)

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
            return json.loads(Path(metadata_path).read_text(encoding="utf-8"))
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
            stem = Path(output_path).stem.replace("_", " ").strip()
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
    draw.rectangle((0, panel_y, width, height), fill=(224, 216, 190, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(75, 58, 42, 150), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (54, 42, 32), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (78, 52, 34), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (91, 75, 58), 6, width)

if __name__ == "__main__":
    main()
