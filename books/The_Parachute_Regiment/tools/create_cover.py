#!/usr/bin/env python3
"""Cover: The Parachute Regiment — paratroopers against a dawn sky over Normandy."""

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

    # Dawn sky gradient: deep blue top -> amber mid -> pale yellow horizon
    for y in range(H):
        t = y / H
        if t < 0.4:
            # Deep blue to purple
            r = int(40 + 60 * (t / 0.4))
            g = int(30 + 80 * (t / 0.4))
            b = int(80 + 100 * (t / 0.4))
        elif t < 0.6:
            # Purple to amber
            lt = (t - 0.4) / 0.2
            r = int(100 + 120 * lt)
            g = int(110 + 80 * lt)
            b = int(180 - 140 * lt)
        else:
            # Amber to pale horizon
            lt = (t - 0.6) / 0.4
            r = int(220 - 60 * lt)
            g = int(190 - 100 * lt)
            b = int(40 - 20 * lt)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Sun glow behind clouds
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse((W // 2 - 300, 600, W // 2 + 300, 1000), fill=(255, 200, 80, 180))
    sun = sun.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, sun)
    draw = ImageDraw.Draw(img, "RGBA")

    # Distant horizon line
    draw.rectangle((0, 1400, W, 1420), fill=(60, 80, 40, 180))

    # French countryside: rolling hills
    for i, (cy, cw, ch) in enumerate(
        [(1450, 2000, 180), (1500, 1600, 140), (1550, 1200, 100)]
    ):
        olive = int(70 + 30 * i)
        draw.polygon(
            [
                (W // 2 - cw // 2, cy + ch),
                (W // 2 - cw // 2, cy),
                (W // 2, cy - ch // 2),
                (W // 2 + cw // 2, cy),
                (W // 2 + cw // 2, cy + ch),
            ],
            fill=(olive, olive + 20, int(30 + 15 * i), 200),
        )

    # Church steeple silhouette
    sx, sy = W // 2 - 200, 1350
    draw.polygon(
        [(sx - 10, sy + 50), (sx - 10, sy), (sx, sy - 40), (sx + 10, sy), (sx + 10, sy + 50)],
        fill=(25, 30, 20, 220),
    )
    draw.rectangle((sx - 20, sy + 50, sx + 20, sy + 70), fill=(25, 30, 20, 220))

    # Paratrooper silhouettes descending (upper portion)
    chutes = [
        (400, 450, True),
        (700, 300, False),
        (1050, 500, True),
        (500, 650, False),
        (1200, 350, True),
        (850, 700, False),
        (300, 550, True),
    ]
    for cx, cy, facing_left in chutes:
        # Canopy
        canopy_w = 80
        canopy_h = 30
        for j in range(3):
            offset = j * 10
            draw.ellipse(
                (
                    cx - canopy_w // 2 + offset,
                    cy - canopy_h - offset * 2,
                    cx + canopy_w // 2 - offset,
                    cy - offset,
                ),
                outline=(180, 190, 170, 120),
                width=2,
            )
        # Riser lines
        for rx in [-15, 0, 15]:
            draw.line(
                (cx + rx, cy - 5, cx + rx, cy + 20),
                fill=(160, 160, 150, 100),
                width=1,
            )
        # Soldier shape
        soldier_dir = -1 if facing_left else 1
        draw.line(
            (cx, cy + 20, cx + soldier_dir * 12, cy + 40),
            fill=(20, 18, 15, 220),
            width=4,
        )
        draw.line(
            (cx + soldier_dir * 12, cy + 40, cx + soldier_dir * 8, cy + 55),
            fill=(20, 18, 15, 220),
            width=3,
        )
        draw.ellipse(
            (cx - 5, cy + 12, cx + 5, cy + 22),
            fill=(20, 18, 15, 220),
        )

    # C-47 transport silhouette high up
    px, py = 200, 150
    draw.polygon(
        [
            (px, py),
            (px + 120, py - 10),
            (px + 180, py + 5),
            (px + 200, py + 8),
            (px + 180, py + 12),
            (px + 120, py + 12),
            (px, py + 8),
        ],
        fill=(15, 12, 10, 160),
    )
    # Wing
    draw.polygon(
        [
            (px + 40, py - 5),
            (px + 100, py - 5),
            (px + 100, py + 3),
            (px + 40, py + 3),
        ],
        fill=(15, 12, 10, 140),
    )
    # Second C-47 further back
    px2, py2 = 1300, 200
    draw.polygon(
        [
            (px2, py2),
            (px2 + 80, py2 - 6),
            (px2 + 120, py2 + 3),
            (px2 + 130, py2 + 5),
            (px2 + 120, py2 + 8),
            (px2 + 80, py2 + 8),
            (px2, py2 + 5),
        ],
        fill=(15, 12, 10, 120),
    )

    # Hedge rows and field patterns on ground
    for fx in range(100, W, 250):
        draw.rectangle((fx, 1480, fx + 6, 1700), fill=(50, 65, 35, 160))

    # Title panel at bottom (light coloured, as specified)
    # The spec says: y=1920 to y=2560, light rectangle
    draw.rectangle((0, 1920, W, H), fill=(240, 235, 225, 245))
    # Decorative top line
    draw.line((300, 1950, W - 300, 1950), fill=(180, 140, 80, 200), width=3)
    # Decorative bottom line
    draw.line((300, H - 180, W - 300, H - 180), fill=(180, 140, 80, 150), width=2)

    # Title
    tf = font("georgiab.ttf", 90)
    af = font("arialbd.ttf", 38)
    sf = font("arial.ttf", 22)

    y = centered(draw, 2000, ["D-DAY 1944"], sf, (140, 110, 60), 4)
    y += 20

    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, title_lines, tf, (40, 35, 25), 8)
    y += 40

    centered(draw, y, [author], af, (80, 75, 65), 6)

    # Small line at bottom
    centered(draw, H - 120, ["A WAR DRAMA"], sf, (130, 125, 110), 4)

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