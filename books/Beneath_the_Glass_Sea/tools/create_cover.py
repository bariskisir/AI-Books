#!/usr/bin/env python3
"""Cover: Beneath the Glass Sea — underwater dome city, cracked glass."""

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

    # Deep ocean gradient — dark blue-green to deeper black-blue
    for y in range(H):
        t = y / H
        r = int(8 + 15 * (1 - t))
        g = int(50 + 30 * (1 - t) - 20 * t)
        b = int(100 + 80 * (1 - t) - 40 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Light rays filtering from above
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for i in range(7):
        x = 200 + i * 200 + random.randint(-50, 50)
        for j in range(60):
            alpha = max(0, 25 - j * 2 + random.randint(-5, 5))
            rd.line(
                (x, 0, x + random.randint(-40, 40), 1200 + j * 20),
                fill=(150, 220, 255, max(0, alpha)),
                width=random.randint(10, 30),
            )
    rays = rays.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, rays)
    draw = ImageDraw.Draw(img, "RGBA")

    # Underwater dome city — semi-ellipse
    dome_cx, dome_cy = W // 2, 1200
    dome_rx, dome_ry = 500, 400
    # Dome outline
    draw.arc(
        (dome_cx - dome_rx, dome_cy - dome_ry, dome_cx + dome_rx, dome_cy + dome_ry),
        0, 180, fill=(120, 200, 230, 60), width=8,
    )
    # Dome glass fill (translucent)
    dome_pts = []
    for a in range(181):
        rad = math.radians(a)
        x = dome_cx + dome_rx * math.cos(rad)
        y = dome_cy - dome_ry * math.sin(rad)
        dome_pts.append((x, y))
    dome_pts.append((dome_cx + dome_rx, dome_cy))
    dome_pts.append((dome_cx - dome_rx, dome_cy))
    draw.polygon(dome_pts, fill=(80, 160, 200, 40))

    # City buildings inside dome
    for i in range(20):
        bx = dome_cx - 400 + i * 42 + random.randint(-10, 10)
        bh = 80 + random.randint(40, 200)
        by = dome_cy - bh
        bw = 20 + random.randint(5, 20)
        if (bx - dome_cx) ** 2 / dome_rx**2 + (by + bh / 2 - dome_cy) ** 2 / dome_ry**2 < 0.8:
            draw.rectangle(
                (bx, by, bx + bw, dome_cy),
                fill=(30 + random.randint(0, 30), 50 + random.randint(0, 30), 80 + random.randint(0, 40), 180),
            )
            # Window lights
            for wy in range(by + 10, dome_cy - 10, 25):
                for wx in range(bx + 4, bx + bw - 4, 12):
                    if random.random() > 0.3:
                        draw.rectangle(
                            (wx, wy, wx + 6, wy + 8),
                            fill=(255, 220, 120, min(200, 100 + random.randint(0, 100))),
                        )

    # Cracked glass lines
    crack_start = (dome_cx - 100, dome_cy - dome_ry + 20)
    crack_color = (200, 230, 255, 120)
    segments = [(crack_start, (dome_cx - 50, dome_cy - dome_ry + 80))]
    segments.append(((dome_cx - 50, dome_cy - dome_ry + 80), (dome_cx + 30, dome_cy - dome_ry + 130)))
    segments.append(((dome_cx - 50, dome_cy - dome_ry + 80), (dome_cx - 120, dome_cy - dome_ry + 150)))
    segments.append(((dome_cx + 30, dome_cy - dome_ry + 130), (dome_cx + 100, dome_cy - dome_ry + 120)))
    segments.append(((dome_cx + 30, dome_cy - dome_ry + 130), (dome_cx + 60, dome_cy - dome_ry + 200)))
    segments.append(((dome_cx - 120, dome_cy - dome_ry + 150), (dome_cx - 180, dome_cy - dome_ry + 190)))
    segments.append(((dome_cx - 120, dome_cy - dome_ry + 150), (dome_cx - 80, dome_cy - dome_ry + 220)))
    for s, e in segments:
        draw.line((s[0], s[1], e[0], e[1]), fill=crack_color, width=3)

    # Bubble particles rising
    for _ in range(80):
        bx = random.randint(200, 1400)
        by = random.randint(300, 1800)
        br = random.randint(2, 8)
        ba = random.randint(20, 70)
        draw.ellipse(
            (bx - br, by - br, bx + br, by + br),
            fill=(180, 220, 255, ba), outline=(200, 235, 255, ba + 20),
        )

    # Seabed silhouette
    seabed_y = 1700
    for x in range(0, W, 4):
        h = 20 + 10 * math.sin(x / 80) + 5 * math.sin(x / 30) + random.randint(-5, 5)
        draw.rectangle((x, seabed_y + h, x + 4, H), fill=(15, 40, 50, 255))

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(8, 20, 30, 240))
    draw.line((220, 1950, W - 220, 1950), fill=(100, 200, 230, 150), width=2)
    draw.line((220, H - 160, W - 220, H - 160), fill=(100, 200, 230, 100), width=2)

    # Subtitle text
    tf = font("georgiab.ttf", 105)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    y = centered(draw, 1990, ["A CLIMATE FICTION NOVEL"], sf, (120, 200, 230), 6)
    y += 30
    wrapped_title = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, wrapped_title, tf, (180, 220, 240), 10)
    y += 50
    centered(draw, y, [author], af, (150, 200, 220), 6)

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