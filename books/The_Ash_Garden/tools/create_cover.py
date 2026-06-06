#!/usr/bin/env python3
"""Cover: The Ash Garden — literary fiction, post-internment California."""

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

    # Sepia gradient background
    for y in range(H):
        t = y / H
        r = int(160 - 80 * t)
        g = int(130 - 60 * t)
        b = int(80 - 40 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Sky glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 300, 100, W // 2 + 300, 500), fill=(220, 190, 140, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Distant barbed wire fence line
    wire_y = 1100
    draw.line((0, wire_y, W, wire_y), fill=(40, 30, 20, 200), width=3)
    for wx in range(0, W, 80):
        # Post
        draw.line((wx, wire_y - 60, wx, wire_y + 20), fill=(50, 40, 30, 220), width=6)
        # Barb wire diagonals
        draw.line((wx - 10, wire_y - 10, wx + 10, wire_y + 10), fill=(60, 50, 40, 200), width=2)
        draw.line((wx - 10, wire_y + 5, wx + 10, wire_y - 5), fill=(60, 50, 40, 200), width=2)

    # Empty garden beds in foreground
    for bx in [200, 500, 800, 1100, 1400]:
        draw.rectangle((bx, 1450, bx + 120, 1580), fill=(100, 80, 55, 180))
        draw.rectangle((bx + 5, 1455, bx + 115, 1575), fill=(80, 60, 40, 200))
        # Dead plant stalks
        for _ in range(4):
            sx = bx + 15 + int(25 * __import__("random").random())
            sy = 1460 + int(100 * __import__("random").random())
            draw.line((sx, sy, sx, sy - 40), fill=(60, 50, 35, 180), width=2)
            draw.line((sx, sy - 40, sx - 8, sy - 50), fill=(60, 50, 35, 180), width=2)
            draw.line((sx, sy - 40, sx + 8, sy - 50), fill=(60, 50, 35, 180), width=2)

    # Lone figure silhouette
    fx, fy = W // 2, 1180
    # Body
    draw.ellipse((fx - 15, fy - 60, fx + 15, fy), fill=(30, 25, 20, 220))
    # Head
    draw.ellipse((fx - 12, fy - 85, fx + 12, fy - 60), fill=(30, 25, 20, 220))
    # Skirt
    draw.polygon(
        [(fx - 16, fy), (fx - 35, fy + 50), (fx + 35, fy + 50), (fx + 16, fy)],
        fill=(30, 25, 20, 220),
    )

    # Bare tree silhouette (left side)
    tx, ty = 250, 900
    draw.line((tx, ty, tx, ty + 400), fill=(40, 30, 20, 200), width=12)
    for angle in range(-60, 80, 30):
        rad = math.radians(angle)
        bx = tx + 100 * math.cos(rad)
        by = ty + 100 * math.sin(rad)
        draw.line((tx, ty + 20, bx, by), fill=(40, 30, 20, 200), width=6)
        if angle % 60 == 0:
            rad2 = math.radians(angle + 20)
            cx = bx + 50 * math.cos(rad2)
            cy = by + 50 * math.sin(rad2)
            draw.line((bx, by, cx, cy), fill=(40, 30, 20, 200), width=3)

    # Faint dust particles in the air
    for _ in range(40):
        px = int(W * __import__("random").random())
        py = int(600 + 600 * __import__("random").random())
        pr = int(2 + 4 * __import__("random").random())
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr),
            fill=(200, 180, 140, int(20 + 30 * __import__("random").random())),
        )

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(25, 20, 15, 245))
    draw.line((300, 1960, W - 300, 1960), fill=(200, 170, 120, 200), width=2)
    draw.line((300, 2500, W - 300, 2500), fill=(200, 170, 120, 120), width=1)

    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    y = 2000
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1100), tf, (210, 180, 130), 8)
    y += 60
    centered(draw, y, [author], af, (190, 170, 150), 6)

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