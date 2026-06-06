#!/usr/bin/env python3
"""Cover: The Glass Shoe — a noir Cinderella with glass slipper and city shadows."""

from __future__ import annotations
import argparse, json, math, random
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

    # Noir gradient: deep navy/charcoal at top to dark indigo at bottom
    for y in range(H):
        t = y / H
        r = int(25 + 10 * t)
        g = int(20 + 15 * t)
        b = int(55 + 30 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Glittering ballroom glow — soft golden light radiating from center
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 500, 200, W // 2 + 500, 1000), fill=(220, 180, 100, 40))
    gd.ellipse((W // 2 - 300, 300, W // 2 + 300, 900), fill=(240, 200, 120, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)

    # City skyline silhouette in lower mid
    draw = ImageDraw.Draw(img, "RGBA")
    skyline_y = 1400
    buildings = [
        (100, skyline_y, 450, 1600),
        (130, skyline_y, 200, 1520),
        (380, skyline_y, 520, 1550),
        (500, skyline_y, 650, 1580),
        (650, skyline_y, 780, 1530),
        (800, skyline_y, 950, 1570),
        (950, skyline_y, 1100, 1540),
        (1050, skyline_y, 1250, 1590),
        (1200, skyline_y, 1350, 1520),
        (1300, skyline_y, 1500, 1560),
    ]
    for x1, y1, x2, y2 in buildings:
        draw.rectangle((x1, y1, x2, y2), fill=(15, 12, 18, 200))

    # Occasional lit windows
    for _ in range(30):
        bx = random.choice(buildings)
        wx = random.randint(bx[0] + 5, bx[2] - 5)
        wy = random.randint(bx[1] + 10, bx[3] - 10)
        draw.rectangle((wx, wy, wx + 8, wy + 12), fill=(240, 210, 120, 100 + int(50 * random.random())))

    # Glass slipper — elegant, translucent, angled
    slipper_x, slipper_y = W // 2 - 30, 940
    # Slipper body (pointed toe)
    draw.polygon(
        [
            (slipper_x - 120, slipper_y + 100),
            (slipper_x - 140, slipper_y + 40),
            (slipper_x - 100, slipper_y),
            (slipper_x, slipper_y - 20),
            (slipper_x + 80, slipper_y),
            (slipper_x + 100, slipper_y + 40),
            (slipper_x + 80, slipper_y + 100),
        ],
        fill=(200, 210, 230, 100),
        outline=(180, 190, 220, 180),
        width=3,
    )
    # Heel
    draw.line(
        (slipper_x + 60, slipper_y + 100, slipper_x + 40, slipper_y + 220),
        fill=(180, 190, 220, 180),
        width=8,
    )
    # Sole
    draw.arc(
        (slipper_x - 140, slipper_y + 80, slipper_x + 100, slipper_y + 120),
        0,
        180,
        fill=(180, 190, 220, 120),
        width=3,
    )
    # Sparkle highlights
    for _ in range(25):
        sx = slipper_x + random.randint(-130, 100)
        sy = slipper_y + random.randint(-20, 100)
        sr = random.randint(1, 4)
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(255, 255, 255, random.randint(80, 220)),
        )

    # Silver shoe shimmer lines
    for _ in range(8):
        lx = slipper_x + random.randint(-120, 90)
        ly = slipper_y + random.randint(0, 90)
        draw.line(
            (lx, ly, lx + random.randint(-20, 20), ly + random.randint(10, 30)),
            fill=(200, 210, 240, random.randint(30, 100)),
            width=1,
        )

    # Falling glass sparkles
    for _ in range(40):
        fx = random.randint(100, W - 100)
        fy = random.randint(100, H - 400)
        fs = random.randint(1, 3)
        draw.ellipse(
            (fx - fs, fy - fs, fx + fs, fy + fs),
            fill=(255, 255, 255, random.randint(40, 160)),
        )

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(240, 238, 235, 235))
    draw.line((250, 1940, W - 250, 1940), fill=(80, 70, 90, 180), width=2)
    draw.line((250, H - 120, W - 250, H - 120), fill=(80, 70, 90, 100), width=1)

    # Genre tag line
    tf_small = font("arial.ttf", 28)
    centered(draw, 1960, ["A FAIRY TALE RETELLING"], tf_small, (100, 95, 110), 4)

    # Title
    tf = font("georgiab.ttf", 100)
    title_lines = wrap(draw, title.upper(), tf, 1300)
    y_title = centered(draw, 2020, title_lines, tf, (30, 25, 35), 8)
    y_title += 20

    # Divider
    draw.line((550, y_title, W - 550, y_title), fill=(80, 70, 90, 120), width=1)
    y_title += 30

    # Author
    af = font("arialbd.ttf", 40)
    centered(draw, y_title, [author], af, (60, 55, 70), 6)

    # Small decorative line near bottom
    draw.line((500, H - 70, W - 500, H - 70), fill=(80, 70, 90, 60), width=1)

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