#!/usr/bin/env python3
"""Cover: The Last Rose of Summer — Romantic Drama set in Provence."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]; FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

def font(n, s):
    for c in [FONT_DIR / n, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()

def wrap(d, t, f, w):
    wo = t.split(); li = []; cu = []
    for wd in wo:
        p = " ".join([*cu, wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w: cu.append(wd)
        else: li.append(" ".join(cu)); cu = [wd]
    if cu: li.append(" ".join(cu))
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

    img = Image.new("RGBA", (W, H), (255, 200, 210, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Sunset gradient: warm pink to lavender to deep purple
    for y in range(H):
        t = y / H
        if t < 0.4:
            # Top: warm sunset pinks and oranges
            r = int(255 - 60 * (t / 0.4))
            g = int(180 - 40 * (t / 0.4))
            b = int(180 + 30 * (t / 0.4))
        elif t < 0.7:
            # Middle: lavender and purple
            r = int(195 - 40 * ((t - 0.4) / 0.3))
            g = int(140 + 20 * ((t - 0.4) / 0.3))
            b = int(210 + 10 * ((t - 0.4) / 0.3))
        else:
            # Bottom: deep twilight
            r = int(155 - 60 * ((t - 0.7) / 0.3))
            g = int(160 - 50 * ((t - 0.7) / 0.3))
            b = int(220 - 30 * ((t - 0.7) / 0.3))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    draw = ImageDraw.Draw(img, "RGBA")

    # Sun disk
    sun_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun_layer)
    sd.ellipse((W // 2 - 200, 500, W // 2 + 200, 900), fill=(255, 200, 100, 200))
    sun_layer = sun_layer.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, sun_layer)

    # Provence villa silhouette
    draw = ImageDraw.Draw(img, "RGBA")
    villa_x = W // 2 - 180
    villa_y = 1000
    # Main house body
    draw.rectangle((villa_x, villa_y, villa_x + 360, villa_y + 300), fill=(80, 60, 100, 160))
    # Roof
    draw.polygon([(villa_x - 30, villa_y), (villa_x + 390, villa_y), (villa_x + 180, villa_y - 120)], fill=(60, 40, 80, 180))
    # Windows (lit)
    for wx, wy in [(villa_x + 40, villa_y + 60), (villa_x + 160, villa_y + 60),
                    (villa_x + 280, villa_y + 60), (villa_x + 40, villa_y + 180),
                    (villa_x + 160, villa_y + 180), (villa_x + 280, villa_y + 180)]:
        draw.rectangle((wx, wy, wx + 50, wy + 70), fill=(255, 220, 140, 200))
    # Door
    draw.rectangle((villa_x + 145, villa_y + 200, villa_x + 215, villa_y + 300), fill=(40, 30, 60, 200))

    # Cypress trees
    for cx, ch in [(W // 2 - 400, 500), (W // 2 + 400, 550)]:
        draw.rectangle((cx, villa_y + 300 - ch, cx + 30, villa_y + 300), fill=(40, 60, 40, 180))

    # Rolling hills in background
    for hx, hy, hr in [(200, 1100, 600), (600, 1150, 500), (1000, 1080, 550), (1400, 1120, 450)]:
        draw.ellipse((hx - hr, hy - hr // 2, hx + hr, hy + hr // 2), fill=(120, 80, 120, 80))

    # Rose garden — rows of rose bushes with blooms
    rose_start_y = 1350
    for row in range(6):
        ry = rose_start_y + row * 45
        for col in range(11):
            rx = 150 + col * 120
            # Bush
            draw.ellipse((rx - 25, ry - 20, rx + 25, ry + 25), fill=(40, 70, 40, 200))
            # Rose bloom — various pinks
            rose_color = (
                int(220 + 35 * math.sin(row + col)),
                int(100 + 60 * math.sin(row * 2 + col * 3)),
                int(140 + 50 * math.cos(row + col * 2)),
                220
            )
            draw.ellipse((rx - 10, ry - 25, rx + 10, ry - 5), fill=rose_color)
            # Inner highlight
            draw.ellipse((rx - 4, ry - 19, rx + 4, ry - 11), fill=(255, 200, 220, 180))

    # Lavender field in foreground
    for lx in range(0, W, 15):
        ly = 1700 + int(20 * math.sin(lx * 0.05))
        draw.ellipse((lx - 3, ly - 8, lx + 3, ly + 8), fill=(140, 100, 200, 160))

    # Title panel at bottom
    panel_y = 1920
    draw.rectangle((0, panel_y, W, H), fill=(25, 15, 40, 235))
    # Top border line
    draw.line((200, panel_y + 15, W - 200, panel_y + 15), fill=(255, 180, 200, 200), width=3)
    # Bottom border line
    draw.line((200, H - 140, W - 200, H - 140), fill=(255, 180, 200, 120), width=2)

    # Title
    tf = font("arialbd.ttf", 90)
    af = font("arialbd.ttf", 36)
    sf = font("arial.ttf", 28)

    # Title in white
    title_lines = wrap(draw, ti.upper(), tf, 1300)
    y = centered(draw, panel_y + 45, title_lines, tf, (255, 255, 255, 255), 10)

    # Author in white, slightly smaller
    y += 25
    bb = draw.textbbox((0, 0), au, font=af)
    draw.text(((W - (bb[2] - bb[0])) // 2, y), au, font=af, fill=(220, 200, 220, 255))

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
        ROOT / a.out if not a.out.is_absolute() else a.out
    )


if __name__ == "__main__":
    main()