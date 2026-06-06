#!/usr/bin/env python3
"""Cover: The Seventh Precinct — noir, dark alley, rain, neon sign."""

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

    # Base image - dark gradient
    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dark noir gradient: black to deep gray to dark blue
    for y in range(H):
        t = y / H
        r = int(15 + 25 * t)
        g = int(15 + 20 * t)
        b_val = int(25 + 40 * t)
        draw.line((0, y, W, y), fill=(r, g, b_val, 255))

    # Brick wall texture on left and right sides
    brick_color = (60, 35, 30, 60)
    for bx in range(0, 200, 40):
        for by in range(0, 1900, 20):
            draw.rectangle((bx, by, bx + 38, by + 18), fill=brick_color, outline=None)
    for bx in range(W - 200, W, 40):
        for by in range(0, 1900, 20):
            draw.rectangle((bx, by, bx + 38, by + 18), fill=brick_color, outline=None)

    # Wet street at bottom third
    street_top = 1400
    for y in range(street_top, 1920):
        t = (y - street_top) / (1920 - street_top)
        gray = int(10 + 30 * t)
        draw.line((0, y, W, y), fill=(gray, gray, gray + 5, 255))

    # Street reflection - faint light on wet ground
    for y in range(street_top, 1920):
        t = (y - street_top) / (1920 - street_top)
        alpha = int(max(0, 15 * (1 - t)))
        draw.line((400, y, 1200, y), fill=(120, 60, 40, alpha))

    # Neon sign glow
    neon_center_x = 300
    neon_center_y = 400
    neon_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ng_draw = ImageDraw.Draw(neon_glow)
    # Outer glow circle
    for r in range(80, 0, -2):
        alpha = int(12 * (1 - r / 80))
        ng_draw.ellipse(
            (neon_center_x - r, neon_center_y - r, neon_center_x + r, neon_center_y + r),
            fill=(255, 30, 30, alpha),
        )
    # Inner glow
    ng_draw.ellipse(
        (neon_center_x - 40, neon_center_y - 40, neon_center_x + 40, neon_center_y + 40),
        fill=(255, 50, 50, 80),
    )
    neon_glow = neon_glow.filter(ImageFilter.GaussianBlur(5))
    img = Image.alpha_composite(img, neon_glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Neon sign "SEVENTH" text glow
    neon_font = font("arialbd.ttf", 80)
    neon_text = "SEVENTH"
    nt_bb = draw.textbbox((0, 0), neon_text, font=neon_font)
    nt_x = neon_center_x - (nt_bb[2] - nt_bb[0]) // 2
    nt_y = neon_center_y - (nt_bb[3] - nt_bb[1]) // 2
    draw.text((nt_x, nt_y), neon_text, font=neon_font, fill=(255, 40, 40, 220))
    # red reflection
    draw.text((nt_x + 2, nt_y + 2), neon_text, font=neon_font, fill=(200, 20, 20, 100))

    # "PRECINCT" smaller
    sub_font = font("arial.ttf", 40)
    sub_text = "PRECINCT"
    st_bb = draw.textbbox((0, 0), sub_text, font=sub_font)
    st_x = neon_center_x - (st_bb[2] - st_bb[0]) // 2
    draw.text((st_x, nt_y + 90), sub_text, font=sub_font, fill=(255, 60, 60, 200))

    # Rain streaks
    for _ in range(200):
        rx = int(random.random() * W)
        ry = int(random.random() * H)
        rlen = int(20 + 40 * random.random())
        ralpha = int(20 + 40 * random.random())
        draw.line(
            (rx, ry, rx + 2, ry + rlen),
            fill=(180, 180, 200, ralpha),
            width=1,
        )

    # Fedora silhouette - detective
    fx, fy = 1200, 750
    # Hat brim
    draw.ellipse((fx - 120, fy + 10, fx + 120, fy + 40), fill=(5, 5, 5, 230))
    # Hat crown
    draw.polygon(
        [(fx - 70, fy + 15), (fx - 70, fy - 60), (fx + 70, fy - 60), (fx + 70, fy + 15)],
        fill=(5, 5, 5, 230),
    )
    # Hat band
    draw.rectangle((fx - 70, fy - 10, fx + 70, fy + 5), fill=(15, 10, 10, 230))
    # Head under hat
    draw.ellipse((fx - 50, fy + 15, fx + 50, fy + 90), fill=(5, 5, 5, 220))
    # Collar / trench coat
    draw.polygon(
        [
            (fx - 80, fy + 80),
            (fx - 120, fy + 250),
            (fx + 120, fy + 250),
            (fx + 80, fy + 80),
        ],
        fill=(5, 5, 5, 210),
    )
    # Shoulders
    draw.polygon(
        [
            (fx - 120, fy + 250),
            (fx - 200, fy + 400),
            (fx + 200, fy + 400),
            (fx + 120, fy + 250),
        ],
        fill=(5, 5, 5, 200),
    )
    # Collar lapels
    draw.polygon(
        [(fx - 50, fy + 80), (fx - 70, fy + 160), (fx, fy + 160)],
        fill=(15, 12, 12, 200),
    )
    draw.polygon(
        [(fx + 50, fy + 80), (fx + 70, fy + 160), (fx, fy + 160)],
        fill=(15, 12, 12, 200),
    )

    # Light pole silhouette left
    lp_x = 100
    draw.rectangle((lp_x, 600, lp_x + 8, 1500), fill=(5, 5, 5, 180))
    # Lamp head
    draw.ellipse(
        (lp_x - 25, 585, lp_x + 33, 620), fill=(10, 10, 10, 200)
    )
    # Light cone from lamp
    light_cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lc_draw = ImageDraw.Draw(light_cone)
    lc_draw.polygon(
        [(lp_x - 20, 620), (lp_x - 300, 1400), (lp_x + 300, 1400)],
        fill=(220, 200, 150, 8),
    )
    light_cone = light_cone.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img, light_cone)
    draw = ImageDraw.Draw(img, "RGBA")

    # Light pool on ground
    light_pool = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    lpd = ImageDraw.Draw(light_pool)
    lpd.ellipse((lp_x - 200, 1350, lp_x + 200, 1550), fill=(220, 200, 150, 6))
    light_pool = light_pool.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, light_pool)
    draw = ImageDraw.Draw(img, "RGBA")

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(8, 6, 8, 245))
    # Top line
    draw.line((200, 1960, W - 200, 1960), fill=(200, 50, 50, 200), width=3)
    # Bottom line
    draw.line((200, H - 100, W - 200, H - 100), fill=(200, 50, 50, 150), width=2)

    # Title text
    tf = font("georgiab.ttf", 110)
    af = font("arialbd.ttf", 42)
    sf = font("arial.ttf", 28)

    y = 2010
    y = centered(draw, y, ["A NOIR NOVEL"], sf, (180, 50, 50), 4)
    y += 30
    wrapped_title = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, wrapped_title, tf, (220, 55, 55), 10)
    y += 50
    centered(draw, y, [author], af, (180, 170, 160), 6)

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