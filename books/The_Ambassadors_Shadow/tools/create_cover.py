#!/usr/bin/env python3
"""Cover: The Ambassador's Shadow — UN building, globe, dark blue and gold."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= mw:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dark blue to navy gradient background
    for y in range(H):
        t = y / H
        r = int(15 + 10 * t)
        g = int(20 + 15 * t)
        b = int(50 + 30 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Globe silhouette — faint glowing circle
    globe = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(globe)
    cx, cy, cr = W // 2, 600, 380
    gd.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), fill=(40, 60, 120, 80))
    # Latitude/longitude lines on globe
    for angle in [0, 45, 90, 135]:
        rad = math.radians(angle)
        gd.ellipse(
            (cx - cr, cy - cr, cx + cr, cy + cr),
            outline=(100, 140, 200, 60),
            width=1,
        )
    gd.ellipse((cx - cr, cy - cr, cx + cr, cy + cr), outline=(150, 180, 220, 100), width=2)
    # Meridian arcs
    for i in range(-2, 3):
        lx = cx + i * cr // 3
        gd.arc(
            (lx - cr // 4, cy - cr, lx + cr // 4, cy + cr),
            -90,
            90,
            fill=(100, 140, 200, 50),
            width=1,
        )
    globe = globe.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, globe)

    # UN building silhouette — simplified geometric facade
    un_building = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ud = ImageDraw.Draw(un_building)
    bx, bw, bh = cx - 300, 600, 600
    by = cy + 50
    # Main building block
    ud.rectangle((bx, by, bx + bw, by + bh), fill=(20, 30, 60, 200))
    # Window grid
    cols, rows = 15, 20
    cw = bw // cols
    rh = bh // rows
    for col in range(cols):
        for row in range(rows):
            wx = bx + col * cw + 4
            wy = by + row * rh + 2
            uw = cw - 8
            uh = rh - 4
            brightness = int(120 + 60 * math.sin(col * 1.7 + row * 2.3))
            ud.rectangle(
                (wx, wy, wx + uw, wy + uh),
                fill=(brightness, brightness + 20, brightness + 40, 180),
            )
    # Left wing
    ud.rectangle((bx - 80, by + 100, bx, by + bh - 50), fill=(15, 25, 55, 200))
    # Right wing
    ud.rectangle((bx + bw, by + 100, bx + bw + 80, by + bh - 50), fill=(15, 25, 55, 200))
    # Flagpole
    ud.rectangle((cx - 3, by - 120, cx + 3, by), fill=(200, 180, 100, 220))
    un_building = un_building.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, un_building)

    # Shadowy figures in foreground (silhouettes)
    draw = ImageDraw.Draw(img)
    figure_positions = [(200, 1400), (600, 1450), (1000, 1420), (1400, 1470)]
    for fx, fy in figure_positions:
        # Body
        draw.ellipse((fx - 15, fy - 40, fx + 15, fy + 10), fill=(10, 8, 15, 200))
        # Head
        draw.ellipse((fx - 10, fy - 55, fx + 10, fy - 35), fill=(10, 8, 15, 200))
        # Legs
        draw.line((fx - 6, fy + 10, fx - 12, fy + 50), fill=(10, 8, 15, 200), width=6)
        draw.line((fx + 6, fy + 10, fx + 12, fy + 50), fill=(10, 8, 15, 200), width=6)

    # Gold accent lines
    draw.line((100, 1600, W - 100, 1600), fill=(200, 170, 80, 150), width=2)
    draw.line((300, 1610, W - 300, 1610), fill=(180, 150, 60, 80), width=1)

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(8, 10, 20, 240))
    draw.line((200, 1960, W - 200, 1960), fill=(200, 170, 80, 200), width=3)
    draw.line((200, H - 160, W - 200, H - 160), fill=(200, 170, 80, 100), width=2)

    # Small genre tag
    sf = font("arial.ttf", 28)
    centered(draw, 1990, ["A POLITICAL THRILLER"], sf, (160, 140, 100), 4)

    # Title
    tf = font("georgiab.ttf", 105)
    af = font("arialbd.ttf", 42)
    title_lines = wrap(draw, title.upper(), tf, 1300)
    y = centered(draw, 2080, title_lines, tf, (220, 190, 130), 10)
    y += 50

    # Author
    author_lines = wrap(draw, author, af, 1200)
    centered(draw, y, author_lines, af, (200, 180, 160), 6)

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
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()
