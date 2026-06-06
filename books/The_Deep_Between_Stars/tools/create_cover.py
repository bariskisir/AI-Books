#!/usr/bin/env python3
"""Cover: The Deep Between Stars — oceanic horror at the Marianas Trench."""

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

    # Deep ocean gradient: black to deep blue to dark teal
    for y in range(H):
        t = y / H
        if t < 0.3:
            # Very dark abyss black
            v = int(5 + 10 * (t / 0.3))
            r, g, b = v, v, v + 8
        elif t < 0.7:
            # Transition to deep blue
            s = (t - 0.3) / 0.4
            r = int(5 + 15 * s)
            g = int(5 + 30 * s)
            b = int(13 + 80 * s)
        else:
            # Dark teal black
            s2 = (t - 0.7) / 0.3
            r = int(20 - 10 * s2)
            g = int(35 - 20 * s2)
            b = int(93 - 50 * s2)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Bioluminescent particles (scattered in upper middle)
    import random
    for _ in range(200):
        x = int(W * random.random())
        y = int(300 + 1400 * random.random())
        r = int(2 + 5 * random.random())
        alpha = int(20 + 80 * random.random())
        # Blue-green glow
        draw.ellipse(
            (x - r, y - r, x + r, y + r),
            fill=(100 + int(100 * random.random()), 200, 220, alpha),
        )

    # Bioluminescent glow layer
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for _ in range(30):
        x = int(W * random.random())
        y = int(200 + 1400 * random.random())
        rad = int(20 + 80 * random.random())
        alpha = int(15 + 40 * random.random())
        gdraw.ellipse(
            (x - rad, y - rad, x + rad, y + rad),
            fill=(60, 180, 220, alpha),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Abyssal trench wall silhouette (left)
    points_left = []
    for y in range(400, 1600, 10):
        offset = int(80 + 40 * (1 + math.sin(y * 0.02 + 1.3)) * 0.5)
        x = 100 + offset + int(30 * (1 + math.sin(y * 0.015)))
        points_left.append((x, y))
    points_left += [(0, 1600), (0, 400)]
    draw.polygon(points_left, fill=(10, 15, 30, 220))

    # Abyssal trench wall silhouette (right)
    points_right = []
    for y in range(400, 1600, 10):
        offset = int(80 + 40 * (1 + math.sin(y * 0.018 + 2.1)) * 0.5)
        x = W - 100 - offset - int(30 * (1 + math.sin(y * 0.012 + 0.7)))
        points_right.append((x, y))
    points_right += [(W, 1600), (W, 400)]
    draw.polygon(points_right, fill=(8, 12, 25, 220))

    # Seafloor ridge at bottom
    floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(floor)
    fdraw.polygon(
        [(0, 1700), (W, 1700), (W, 1850), (0, 1850)],
        fill=(8, 10, 20, 200),
    )
    fdraw.polygon(
        [(0, 1800), (W // 2 - 200, 1750), (W, 1800), (W, 1920), (0, 1920)],
        fill=(12, 15, 28, 200),
    )
    img = Image.alpha_composite(img, floor)
    draw = ImageDraw.Draw(img, "RGBA")

    # Research station lights in the abyss
    # Station body
    station_x, station_y = W // 2, 1200
    draw.rectangle(
        (station_x - 40, station_y - 60, station_x + 40, station_y + 60),
        fill=(60, 70, 90, 200),
        outline=(100, 140, 180, 180),
        width=2,
    )
    # Station modules
    draw.rectangle(
        (station_x - 55, station_y - 30, station_x - 40, station_y + 30),
        fill=(50, 60, 80, 200),
    )
    draw.rectangle(
        (station_x + 40, station_y - 40, station_x + 55, station_y + 40),
        fill=(50, 60, 80, 200),
    )
    # Floodlight beams
    for angle in [-1, 0, 1]:
        lx = station_x + angle * 30
        ly = station_y + 60
        for i in range(8):
            alpha = 40 - 5 * i
            w = 8 + i * 6
            draw.ellipse(
                (lx - w, ly + i * 8 - 2, lx + w, ly + i * 8 + 2),
                fill=(180, 220, 255, alpha),
            )
    # Bright window lights
    for wy in range(-40, 41, 20):
        draw.rectangle(
            (station_x - 5, station_y + wy - 4, station_x + 5, station_y + wy + 4),
            fill=(200, 230, 255, 220),
        )
    # Light glow around station
    slayer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(slayer)
    sdraw.ellipse(
        (station_x - 120, station_y - 100, station_x + 120, station_y + 100),
        fill=(80, 150, 220, 30),
    )
    slayer = slayer.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, slayer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Cable / tether line from station down into darkness
    draw.line(
        (station_x, station_y + 60, W // 2 + 30, 1700),
        fill=(40, 50, 70, 150),
        width=2,
    )
    # Small descending sub shape on cable
    draw.ellipse(
        (W // 2 + 10, 1500, W // 2 + 50, 1530),
        fill=(50, 65, 90, 200),
    )

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(12, 14, 20, 245))
    # Accent line top of panel
    draw.line((250, 1940, W - 250, 1940), fill=(80, 150, 200, 150), width=2)
    # Accent line bottom
    draw.line((250, H - 200, W - 250, H - 200), fill=(80, 150, 200, 100), width=2)

    # Title text
    ttf = font("georgiab.ttf", 90)
    title_lines = wrap(draw, title, ttf, 1300)

    y = centered(
        draw,
        1990,
        ["A NOVEL OF THE DEEP"],
        font("arial.ttf", 28),
        (100, 160, 200),
        4,
    )
    y += 20
    y = centered(draw, y, title_lines, ttf, (180, 210, 240), 8)
    y += 30

    # Author name
    autf = font("arialbd.ttf", 40)
    centered(draw, y, [author], autf, (150, 170, 200), 6)

    # Subtitle line
    sf = font("arial.ttf", 22)
    centered(
        draw,
        H - 130,
        ["OCEANIC HORROR"],
        sf,
        (90, 120, 150),
        4,
    )

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