#!/usr/bin/env python3
"""Cover: Neon Saints — a cyberpunk city at night with neon and rain."""

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

    # Night sky gradient: dark blue to deep purple to black
    for y in range(H):
        t = y / H
        if t < 0.4:
            r = int(8 + 5 * t * 2.5)
            g = int(5 + 10 * t * 2.5)
            b = int(25 + 20 * t * 2.5)
        elif t < 0.7:
            r = int(13 + 20 * (t - 0.4) * 3.3)
            g = int(15 + 5 * (t - 0.4) * 3.3)
            b = int(45 - 15 * (t - 0.4) * 3.3)
        else:
            r = int(33 - 25 * (t - 0.7) * 3.3)
            g = int(20 - 15 * (t - 0.7) * 3.3)
            b = int(30 - 25 * (t - 0.7) * 3.3)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # City skyline silhouette
    buildings = [
        (80, 800, 130, 1400),
        (160, 700, 200, 1400),
        (220, 900, 260, 1400),
        (300, 600, 150, 1400),
        (390, 750, 180, 1400),
        (480, 850, 120, 1400),
        (540, 650, 220, 1400),
        (650, 550, 160, 1400),
        (730, 700, 140, 1400),
        (800, 800, 180, 1400),
        (880, 600, 200, 1400),
        (970, 750, 130, 1400),
        (1030, 650, 170, 1400),
        (1110, 550, 150, 1400),
        (1180, 700, 190, 1400),
        (1270, 800, 120, 1400),
        (1330, 650, 160, 1400),
        (1400, 750, 180, 1400),
        (1480, 850, 130, 1400),
    ]
    for bx, bh, bw, by2 in buildings:
        draw.rectangle((bx, bh, bx + bw, by2), fill=(10, 8, 15, 220))

    # Spire (tallest building)
    spire_x = W // 2
    draw.polygon(
        [
            (spire_x - 40, 1400),
            (spire_x - 40, 450),
            (spire_x - 20, 300),
            (spire_x, 250),
            (spire_x + 20, 300),
            (spire_x + 40, 450),
            (spire_x + 40, 1400),
        ],
        fill=(8, 6, 12, 240),
    )
    # Spire tip glow
    draw.ellipse((spire_x - 15, 220, spire_x + 15, 260), fill=(0, 255, 255, 80))

    # Neon window lights on buildings
    for _ in range(120):
        import random

        bx = random.randint(20, W - 20)
        by = random.randint(500, 1350)
        color = random.choice(
            [
                (0, 255, 255, random.randint(40, 150)),
                (255, 0, 255, random.randint(40, 150)),
                (255, 100, 0, random.randint(30, 100)),
                (0, 200, 255, random.randint(30, 120)),
            ]
        )
        draw.rectangle((bx, by, bx + random.randint(4, 10), by + random.randint(4, 10)), fill=color)

    # Rain streaks (diagonal)
    for _ in range(200):
        import random

        rx = random.randint(0, W)
        ry = random.randint(0, min(1900, int(H * 0.75)))
        rlen = random.randint(20, 80)
        ralpha = random.randint(10, 40)
        draw.line(
            (rx, ry, rx - int(rlen * 0.3), ry + rlen),
            fill=(150, 180, 255, ralpha),
            width=1,
        )

    # Ground reflection / rain-slicked street
    for y in range(1420, 1500):
        t = (y - 1420) / 80
        r = int(5 + 15 * t)
        g = int(4 + 10 * t)
        b = int(12 + 20 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 200))

    # Cyan ground line glow
    draw.line((0, 1420, W, 1420), fill=(0, 255, 255, 60), width=2)

    # Holographic figure representation
    holox = W // 2 - 100
    # Body outline (glowing cyan)
    body_points = [
        (holox, 950),
        (holox - 20, 1050),
        (holox - 30, 1150),
        (holox, 1180),
        (holox + 30, 1150),
        (holox + 20, 1050),
        (holox, 950),
    ]
    draw.polygon(body_points, fill=None, outline=(0, 255, 255, 120), width=3)
    # Head
    draw.ellipse((holox - 20, 900, holox + 20, 945), fill=None, outline=(255, 0, 255, 150), width=3)
    # Arms
    draw.line((holox - 30, 1150, holox - 60, 1250), fill=(255, 0, 255, 100), width=3)
    draw.line((holox + 30, 1150, holox + 60, 1250), fill=(255, 0, 255, 100), width=3)
    # Legs
    draw.line((holox - 10, 1180, holox - 20, 1350), fill=(0, 255, 255, 100), width=3)
    draw.line((holox + 10, 1180, holox + 20, 1350), fill=(0, 255, 255, 100), width=3)
    # Holographic noise lines
    for _ in range(15):
        import random

        nx = holox + random.randint(-50, 50)
        ny = 900 + random.randint(0, 400)
        draw.line(
            (nx, ny, nx + random.randint(-10, 10), ny + random.randint(5, 15)),
            fill=(0, 255, 255, random.randint(20, 50)),
            width=1,
        )

    # Neon signs / holographic billboards
    sign_texts = ["NEON", "NULL", "DREAM"]
    for i, st in enumerate(sign_texts):
        sf = font("arialbd.ttf", 40)
        sx = 200 + i * 500
        sy = 700 + (i % 2) * 100
        col = (255, 0, 255, 60) if i % 2 == 0 else (0, 255, 255, 50)
        sbb = draw.textbbox((0, 0), st, font=sf)
        draw.rectangle(
            (sx - 10, sy - 5, sx + (sbb[2] - sbb[0]) + 10, sy + (sbb[3] - sbb[1]) + 5),
            fill=(0, 0, 0, 120),
        )
        draw.text((sx, sy), st, font=sf, fill=col)

    # Title panel at the bottom
    draw.rectangle((0, 1920, W, H), fill=(14, 12, 18, 245))
    draw.line((150, 1960, W - 150, 1960), fill=(255, 0, 255, 120), width=2)
    draw.line((150, H - 120, W - 150, H - 120), fill=(0, 255, 255, 80), width=2)

    # Title
    tf = font("georgiab.ttf", 110)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    af = font("arialbd.ttf", 44)

    y = centered(draw, 2020, ["A CYBERPUNK NOVEL"], font("arial.ttf", 28), (180, 180, 220), 4)
    y += 50
    y = centered(draw, y, title_lines, tf, (0, 255, 255), 10)
    y += 50
    centered(draw, y, [author], af, (255, 200, 200), 6)

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