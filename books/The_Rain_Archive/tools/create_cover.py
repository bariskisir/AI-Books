#!/usr/bin/env python3
"""Cover: The Rain Archive - dry reservoir, public archive shelves, false blue rainfall column, canal valve, witness jars."""
from __future__ import annotations
import argparse, json, random, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560
PANEL_Y = 1765

def font(name, size):
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def make_cover(mp, op):
    metadata = json.loads(mp.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Rain Archive")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")
    random.seed("rain-archive-cover-redesign")
    img = Image.new("RGBA", (W, H), (30, 36, 42, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Burnt evening sky over a city seen as a water-rights map.
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        c = lerp((16, 32, 46), (165, 91, 62), t) if t < 0.55 else lerp((165, 91, 62), (185, 148, 96), (t - 0.55) / 0.45)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Distant city blocks as a flat cadastral grid.
    draw.rectangle((0, 1040, W, PANEL_Y), fill=(152, 124, 82, 255))
    for x in range(-80, W + 140, 145):
        draw.line((x, 1060, x - 180, PANEL_Y), fill=(95, 82, 64, 110), width=4)
    for y in range(1110, PANEL_Y, 130):
        draw.line((0, y, W, y - 72), fill=(105, 88, 64, 95), width=3)

    # Huge dry reservoir ring, cracked and empty, dominating the cover.
    cx, cy = 790, 1195
    draw.ellipse((cx - 505, cy - 335, cx + 505, cy + 335), fill=(196, 167, 106, 255), outline=(74, 72, 63, 220), width=14)
    draw.ellipse((cx - 360, cy - 235, cx + 360, cy + 235), fill=(148, 123, 83, 255), outline=(85, 74, 58, 180), width=7)
    for i in range(64):
        a = random.random() * math.tau
        r = random.randint(65, 330)
        x = cx + int(math.cos(a) * r)
        y = cy + int(math.sin(a) * r * 0.64)
        draw.line((x, y, x + random.randint(-95, 95), y + random.randint(-55, 55)), fill=(70, 60, 48, 115), width=3)

    # A false blue canal cuts across the truthful dry map.
    canal = [(0, 1455), (260, 1390), (535, 1432), (820, 1360), (1110, 1410), (W, 1305), (W, 1425), (1120, 1535), (820, 1490), (540, 1570), (260, 1518), (0, 1600)]
    draw.polygon(canal, fill=(31, 106, 148, 220))
    draw.line((0, 1455, 260, 1390, 535, 1432, 820, 1360, 1110, 1410, W, 1305), fill=(168, 219, 224, 150), width=5)

    # Torn July ledger page pinned over the map.
    page = [(150, 250), (720, 205), (690, 785), (190, 835)]
    draw.polygon(page, fill=(234, 224, 184, 245), outline=(78, 68, 52, 210))
    ledger_font = font("georgia.ttf", 28)
    draw.text((230, 310), "JULY GAUGE LOG", font=font("georgia.ttf", 42), fill=(70, 58, 45, 230))
    for i, day in enumerate(["07", "08", "09", "10", "11", "12"]):
        yy = 405 + i * 58
        draw.text((245, yy), f"{day}  0.0 mm", font=ledger_font, fill=(70, 58, 45, 210))
        draw.line((430, yy + 18, 610, yy + 4), fill=(136, 32, 35, 220), width=5)
    draw.polygon([(685, 208), (720, 205), (700, 325)], fill=(176, 154, 111, 230))

    # Witness jars, small and specific, arranged like evidence not decoration.
    for j, x in enumerate([920, 1015, 1110, 1205]):
        top = 560 + j * 28
        draw.rounded_rectangle((x, top, x + 66, 960), radius=18, fill=(220, 238, 232, 95), outline=(242, 238, 210, 230), width=4)
        draw.rectangle((x + 8, 845 - j * 34, x + 58, 950), fill=(52, 129, 154, 155))
        draw.rectangle((x + 6, top - 18, x + 60, top + 8), fill=(221, 214, 176, 245))
        draw.text((x + 12, top + 45), "JUL", font=font("arialbd.ttf", 18), fill=(52, 56, 52, 200))

    # Canal control house and a single archivist scale figure.
    draw.rectangle((1270, 1130, 1480, 1480), fill=(55, 61, 58, 245))
    draw.polygon([(1250, 1130), (1500, 1130), (1465, 1055), (1280, 1055)], fill=(74, 78, 70, 255))
    draw.rectangle((1340, 1270, 1410, 1480), fill=(25, 35, 42, 255))
    fx, fy = 760, 1655
    draw.ellipse((fx - 17, fy - 92, fx + 17, fy - 58), fill=(28, 28, 28, 255))
    draw.rectangle((fx - 16, fy - 58, fx + 16, fy + 35), fill=(28, 34, 38, 255))
    draw.rectangle((fx + 22, fy - 35, fx + 96, fy + 8), fill=(234, 222, 181, 255), outline=(75, 62, 46, 200), width=2)

    sf = font("georgia.ttf", 36)
    desc = "FALSE RAINFALL · TRUE WATER"
    bb = draw.textbbox((0, 0), desc, font=sf)
    draw.text(((W - (bb[2] - bb[0])) // 2, 165), desc, font=sf, fill=(232, 218, 180, 235))
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG", optimize=True)

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
    draw.rectangle((0, panel_y, width, height), fill=(236, 230, 216, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(88, 92, 82, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (52, 58, 52), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (86, 88, 74), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (112, 112, 94), 6, width)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path); a=p.parse_args()
    make_cover(ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT / a.out if not a.out.is_absolute() else a.out)
if __name__ == "__main__": main()
