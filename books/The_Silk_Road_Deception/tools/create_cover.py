#!/usr/bin/env python3
"""Cover: The Silk Road Deception — desert caravan, ancient ruins, amber and sand."""

from __future__ import annotations
import argparse, json
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

    # Amber-to-sand-to-terracotta gradient
    for y in range(H):
        t = y / H
        if t < 0.4:
            r, g, b = 210, 170, 100
        elif t < 0.7:
            r, g, b = 195, 140, 80
        else:
            r, g, b = 170, 100, 60
        fade = 1.0 - (max(0, y - 1920) / 640) * 0.4
        draw.line(
            (0, y, W, y),
            fill=(int(r * fade), int(g * fade), int(b * fade), 255),
        )

    # Sun disc (hazy desert sun)
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse((W // 2 - 180, 400, W // 2 + 180, 760), fill=(240, 210, 140, 180))
    sun = sun.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, sun)
    draw = ImageDraw.Draw(img, "RGBA")

    # Distant ruins on the horizon (arches and pillars)
    # Arch 1
    rx, ry = 300, 1300
    draw.arc((rx, ry, rx + 160, ry + 280), 180, 0, fill=(140, 100, 60, 200), width=14)
    draw.rectangle((rx - 10, ry + 240, rx + 10, ry + 360), fill=(140, 100, 60, 200))
    draw.rectangle((rx + 150, ry + 240, rx + 170, ry + 360), fill=(140, 100, 60, 200))
    # Arch 2 (larger, center)
    rx2, ry2 = 680, 1180
    draw.arc((rx2, ry2, rx2 + 240, ry2 + 380), 180, 0, fill=(160, 115, 70, 200), width=16)
    draw.rectangle((rx2 - 10, ry2 + 320, rx2 + 10, ry2 + 460), fill=(160, 115, 70, 200))
    draw.rectangle((rx2 + 230, ry2 + 320, rx2 + 250, ry2 + 460), fill=(160, 115, 70, 200))
    # Broken pillar
    px, py = 1200, 1250
    draw.rectangle((px, py, px + 30, py + 350), fill=(150, 105, 60, 200))
    draw.rectangle((px - 15, py + 300, px + 45, py + 320), fill=(150, 105, 60, 200))
    # Partial column
    px2, py2 = 1050, 1350
    draw.rectangle((px2, py2, px2 + 20, py2 + 200), fill=(130, 90, 50, 180))

    # Desert caravan silhouette (camels and riders)
    camel_color = (60, 40, 25, 220)
    # Camel 1
    cx, cy = 400, 1550
    draw.ellipse((cx, cy, cx + 40, cy + 25), fill=camel_color)
    draw.ellipse((cx + 50, cy - 40, cx + 90, cy - 5), fill=camel_color)
    draw.arc((cx - 30, cy - 55, cx + 10, cy - 10), 240, 120, fill=camel_color, width=5)
    draw.line((cx + 20, cy - 5, cx + 60, cy + 25), fill=camel_color, width=4)  # legs
    draw.line((cx + 40, cy, cx + 80, cy + 25), fill=camel_color, width=4)
    # Rider on camel 1
    draw.ellipse((cx + 50, cy - 80, cx + 70, cy - 55), fill=(40, 30, 20, 230))
    draw.line((cx + 60, cy - 55, cx + 55, cy - 20), fill=(40, 30, 20, 230), width=4)

    # Camel 2
    cx2, cy2 = 550, 1530
    draw.ellipse((cx2, cy2, cx2 + 35, cy2 + 22), fill=camel_color)
    draw.ellipse((cx2 + 45, cy2 - 35, cx2 + 80, cy2 - 3), fill=camel_color)
    draw.arc((cx2 - 25, cy2 - 48, cx2 + 8, cy2 - 8), 240, 120, fill=camel_color, width=5)
    draw.line((cx2 + 15, cy2 - 3, cx2 + 50, cy2 + 22), fill=camel_color, width=4)
    draw.line((cx2 + 35, cy2 - 2, cx2 + 70, cy2 + 22), fill=camel_color, width=4)

    # Camel 3 (further, smaller)
    cx3, cy3 = 750, 1540
    draw.ellipse((cx3, cy3, cx3 + 30, cy3 + 18), fill=camel_color)
    draw.ellipse((cx3 + 38, cy3 - 30, cx3 + 68, cy3 - 2), fill=camel_color)
    draw.line((cx3 + 15, cy3, cx3 + 42, cy3 + 18), fill=camel_color, width=3)
    draw.line((cx3 + 30, cy3, cx3 + 58, cy3 + 18), fill=camel_color, width=3)

    # Sand dunes in foreground
    for i, (dx, dy, dw, dh) in enumerate(
        [
            (0, 1750, 800, 120),
            (500, 1780, 600, 100),
            (200, 1800, 500, 90),
            (1000, 1760, 700, 110),
            (1300, 1790, 400, 85),
        ]
    ):
        shade = 100 + i * 15
        draw.pieslice(
            (dx, dy, dx + dw, dy + dh * 2),
            180,
            0,
            fill=(shade, shade - 20, shade - 40, 200),
        )

    # Parchment map effect in lower sky area (a faint scroll-like shape)
    map_color = (200, 180, 140, 60)
    draw.rectangle((200, 900, 1400, 1120), fill=map_color)
    draw.rectangle((180, 900, 200, 1120), fill=(190, 170, 130, 70))
    draw.rectangle((1400, 900, 1420, 1120), fill=(190, 170, 130, 70))
    # Faint route line on map
    draw.line((300, 960, 600, 1000, 900, 950, 1200, 1020), fill=(160, 120, 70, 80), width=3)
    # Tiny marker dots on the map route
    for mx, my in [(300, 960), (600, 1000), (900, 950), (1200, 1020)]:
        draw.ellipse((mx - 4, my - 4, mx + 4, my + 4), fill=(180, 80, 40, 100))

    # Dust particles scattered
    import random as _rng

    for _ in range(80):
        x = int(W * _rng.random())
        y = int(800 + 1200 * _rng.random())
        r = int(2 + 5 * _rng.random())
        a = int(20 + 40 * _rng.random())
        draw.ellipse((x - r, y - r, x + r, y + r), fill=(220, 200, 160, a))

    # Title panel — light rectangle at bottom
    draw.rectangle((0, 1920, W, H), fill=(245, 240, 230, 245))
    # Decorative lines
    draw.line((200, 1960, W - 200, 1960), fill=(180, 140, 90, 200), width=2)
    draw.line((200, H - 160, W - 200, H - 160), fill=(180, 140, 90, 140), width=2)

    # Title text
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    # Genre line
    y = centered(draw, 2000, ["A HISTORICAL THRILLER"], sf, (160, 120, 70), 4)
    y += 30

    # Title (wrapped if needed)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, title_lines, tf, (40, 35, 30), 10)
    y += 40

    # Author
    centered(draw, y, [author], af, (100, 75, 50), 6)

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