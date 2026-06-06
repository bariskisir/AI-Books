#!/usr/bin/env python3
"""Cover: The Palermo Exchange — warm stone, Vespa, shadowed doorway."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(n, s):
    for c in [FONT_DIR / n, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()


def wrap(d, t, f, w):
    wo = t.split()
    li = []
    cu = []
    for wd in wo:
        p = " ".join([*cu, wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w:
            cu.append(wd)
        else:
            li.append(" ".join(cu))
            cu = [wd]
    if cu:
        li.append(" ".join(cu))
    return li


def centered(d, y, li, f, fl, g):
    for l in li:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), l, font=f, fill=fl)
        y += bb[3] - bb[1] + g
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    ti = m["title"]
    au = m.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (180, 140, 100, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm stone gradient background
    for y in range(H):
        t = y / H
        r = int(180 - 40 * t)
        g = int(140 - 30 * t)
        b = int(100 - 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Narrow street perspective (vicolo) — converging walls
    wall_color = (160, 120, 80, 120)
    draw.polygon([(0, 0), (300, 600), (300, 1400), (0, 1800)], fill=wall_color)  # left wall
    draw.polygon([(W, 0), (1300, 600), (1300, 1400), (W, 1800)], fill=wall_color)  # right wall

    # Stone texture lines on walls
    for i in range(8):
        x1 = int(300 + i * 30)
        x2 = int(1300 - i * 30)
        draw.line((x1, 600 + i * 100, x2, 600 + i * 100), fill=(140, 100, 65, 80), width=2)

    # Shadowed doorway on left wall
    door_x = 120
    door_y = 900
    draw.rectangle((door_x, door_y, door_x + 160, door_y + 280), fill=(30, 25, 20, 220))
    draw.arc((door_x - 10, door_y - 10, door_x + 170, door_y + 30), 180, 360, fill=(50, 40, 30, 200), width=8)

    # Arch above doorway
    draw.arc((door_x - 20, door_y - 40, door_x + 180, door_y + 40), 180, 0, fill=(100, 75, 50, 180), width=6)

    # Warm light spilling from doorway
    for i in range(5):
        alpha = 20 - i * 3
        draw.ellipse((door_x - 30 - i * 10, door_y + 260, door_x + 190 + i * 10, door_y + 300 + i * 30),
                     fill=(220, 180, 100, max(0, alpha)))

    # Vespa silhouette on right side
    vx, vy = 1250, 1100
    # Body
    draw.ellipse((vx - 60, vy - 40, vx + 60, vy + 60), fill=(50, 45, 40, 200))
    # Handlebars
    draw.line((vx - 40, vy - 50, vx + 20, vy - 60), fill=(60, 55, 50, 200), width=6)
    # Front shield
    draw.polygon([(vx + 10, vy - 30), (vx + 50, vy - 10), (vx + 50, vy + 30), (vx + 10, vy + 10)],
                 fill=(55, 50, 45, 200))
    # Wheels
    draw.ellipse((vx - 30, vy + 50, vx + 10, vy + 80), fill=(40, 35, 30, 200))
    draw.ellipse((vx + 20, vy + 50, vx + 60, vy + 80), fill=(40, 35, 30, 200))
    # Seat
    draw.rectangle((vx - 30, vy - 20, vx + 10, vy + 5), fill=(45, 40, 35, 200))

    # Shuttered window on right wall above
    wx, wy = 1350, 750
    draw.rectangle((wx, wy, wx + 120, wy + 160), fill=(80, 60, 40, 150))
    # Shutter slats
    for i in range(6):
        draw.line((wx, wy + 20 + i * 24, wx + 120, wy + 20 + i * 24), fill=(60, 45, 30, 180), width=3)

    # Wrought iron balcony railing
    bx, by = 500, 700
    draw.rectangle((bx, by, bx + 200, by + 20), fill=(40, 35, 30, 160))
    for i in range(8):
        draw.line((bx + 20 + i * 24, by + 20, bx + 20 + i * 24, by + 60), fill=(40, 35, 30, 140), width=3)
    draw.line((bx, by + 60, bx + 200, by + 60), fill=(40, 35, 30, 140), width=4)

    # Cobblestone texture on ground
    for gx in range(0, W, 50):
        for gy in range(1400, 1920, 30):
            if ((gx // 50) + (gy // 30)) % 2:
                draw.ellipse((gx, gy, gx + 20, gy + 10), fill=(130, 95, 65, 50))

    # Title panel
    draw.rectangle((0, 1920, W, H), fill=(25, 22, 18, 245))
    draw.line((240, 1960, W - 240, 1960), fill=(200, 160, 100, 200), width=2)
    draw.line((240, H - 150, W - 240, H - 150), fill=(200, 160, 100, 100), width=1)

    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    # Genre tag
    centered(draw, 2000, ["A CRIME THRILLER"], sf, (200, 160, 100), 6)

    # Title
    y = 2060
    title_lines = wrap(draw, ti.upper(), tf, 1200)
    y = centered(draw, y, title_lines, tf, (210, 195, 170), 10)
    y += 50

    # Author
    centered(draw, y, [au], af, (180, 175, 160), 6)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(op, "PNG", optimize=True)



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

def _draw_standard_cover_title_panel(image, title: str = "", author: str = "") -> None:
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
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()