#!/usr/bin/env python3
"""Cover: The Mountain Will Not Fall — survival thriller, K2 mountaineering."""

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
    title = m["title"]
    author = m.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Cold gradient background: dark steel blue -> gray -> white
    for y in range(H):
        t = y / H
        if t < 0.5:
            # Dark storm sky
            r = int(40 + 60 * (t * 2))
            g = int(50 + 70 * (t * 2))
            b = int(75 + 80 * (t * 2))
        else:
            # Fading to gray-white
            r = int(100 + 155 * ((t - 0.5) * 2))
            g = int(120 + 135 * ((t - 0.5) * 2))
            b = int(155 + 100 * ((t - 0.5) * 2))
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Storm clouds in upper section
    cloud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_layer)
    for _ in range(30):
        cx = random.randint(0, W)
        cy = random.randint(0, 600)
        cr = random.randint(80, 250)
        ca = random.randint(15, 40)
        cd.ellipse((cx - cr, cy - cr // 2, cx + cr, cy + cr // 2),
                    fill=(180, 185, 190, ca))
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, cloud_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # K2 peak - main triangular massif in the upper center
    peak_points = [
        (W // 2 - 200, 1400),   # base left
        (W // 2, 150),          # summit
        (W // 2 + 220, 1400),   # base right
    ]
    draw.polygon(peak_points, fill=(200, 200, 210, 180))
    draw.polygon(peak_points, fill=None, outline=(160, 160, 170, 200), width=3)

    # Snow cap on summit
    snow_points = [
        (W // 2 - 40, 350),
        (W // 2, 150),
        (W // 2 + 45, 350),
        (W // 2, 380),
    ]
    draw.polygon(snow_points, fill=(240, 245, 250, 220))

    # Ridge lines on the mountain
    ridges = [
        (W // 2 - 160, 800, W // 2 - 60, 500),
        (W // 2 + 170, 900, W // 2 + 60, 550),
        (W // 2 - 180, 1200, W // 2 - 80, 700),
        (W // 2 + 190, 1100, W // 2 + 80, 650),
    ]
    for x1, y1, x2, y2 in ridges:
        draw.line((x1, y1, x2, y2), fill=(180, 185, 195, 150), width=3)

    # Secondary mountain peak (left)
    left_peak = [
        (100, 1400),
        (300, 400),
        (500, 1400),
    ]
    draw.polygon(left_peak, fill=(170, 175, 185, 120))
    draw.polygon(left_peak, fill=None, outline=(150, 155, 165, 100), width=2)

    # Secondary mountain peak (right)
    right_peak = [
        (1100, 1400),
        (1300, 550),
        (1500, 1400),
    ]
    draw.polygon(right_peak, fill=(165, 170, 180, 110))
    draw.polygon(right_peak, fill=None, outline=(145, 150, 160, 100), width=2)

    # Climbing rope lines (zigzag up the mountain)
    rope_points = [
        (W // 2 - 180, 1350, W // 2 - 150, 1200),
        (W // 2 - 150, 1200, W // 2 - 100, 1050),
        (W // 2 - 100, 1050, W // 2 - 120, 900),
        (W // 2 - 120, 900, W // 2 - 60, 750),
        (W // 2 - 60, 750, W // 2 - 80, 600),
        (W // 2 - 80, 600, W // 2 - 30, 450),
    ]
    for x1, y1, x2, y2 in rope_points:
        draw.line((x1, y1, x2, y2), fill=(220, 150, 50, 180), width=5)
        draw.line((x1, y1, x2, y2), fill=(240, 180, 80, 100), width=3)

    # Snow storm streaks (diagonal white lines)
    for _ in range(60):
        sx = random.randint(0, W)
        sy = random.randint(0, 1500)
        sl = random.randint(10, 50)
        sa = random.randint(10, 35)
        draw.line(
            (sx, sy, sx + sl, sy + sl // 3),
            fill=(255, 255, 255, sa),
            width=random.randint(1, 3),
        )

    # Snow particles
    for _ in range(120):
        px = random.randint(0, W)
        py = random.randint(0, 1800)
        pr = random.randint(1, 4)
        pa = random.randint(40, 120)
        draw.ellipse(
            (px - pr, py - pr, px + pr, py + pr),
            fill=(255, 255, 255, pa),
        )

    # Crevasse lines on glacier foreground
    for _ in range(8):
        cx = random.randint(100, W - 100)
        cy = random.randint(1300, 1500)
        cw = random.randint(60, 150)
        draw.arc(
            (cx, cy, cx + cw, cy + 30),
            start=random.randint(0, 180),
            end=random.randint(180, 360),
            fill=(100, 110, 130, 120),
            width=3,
        )

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(230, 225, 218, 250))
    draw.line((250, 1960, W - 250, 1960), fill=(120, 130, 140, 150), width=2)
    draw.line((250, 2500, W - 250, 2500), fill=(120, 130, 140, 100), width=1)

    tf = font("georgiab.ttf", 90)
    af = font("arialbd.ttf", 42)
    sf = font("arial.ttf", 24)

    # Title
    y = 2020
    y = centered(draw, y, wrap(draw, title, tf, 1100), tf, (30, 35, 45), 6)
    y += 50

    # Author name
    centered(draw, y, [author], af, (70, 75, 85), 6)

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