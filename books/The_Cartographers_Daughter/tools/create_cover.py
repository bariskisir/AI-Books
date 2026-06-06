#!/usr/bin/env python3
"""Cover: The Cartographer's Daughter — antique map, uncharted island, sailing ship."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(n, s):
    candidates = [FONT_DIR / n, FONT_DIR / "georgiab.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), s)
    return ImageFont.load_default()


def wrap(d, t, f, w):
    words = t.split()
    lines = []
    cur = []
    for wd in words:
        p = " ".join(cur + [wd])
        if d.textbbox((0, 0), p, font=f)[2] <= w:
            cur.append(wd)
        else:
            lines.append(" ".join(cur))
            cur = [wd]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(d, y, lines, f, fl, g):
    for l in lines:
        bb = d.textbbox((0, 0), l, font=f)
        d.text(((W - (bb[2] - bb[0])) // 2, y), l, font=f, fill=fl)
        y += bb[3] - bb[1] + g
    return y


def make_cover(mp, op):
    meta = json.loads(mp.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")

    # Parchment-toned base image
    img = Image.new("RGBA", (W, H), (210, 180, 140, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Parchment gradient — darker at edges, lighter center (antique map look)
    for y in range(H):
        t = y / H
        r = int(180 + 30 * (1 - abs(t - 0.5) * 1.2))
        g = int(150 + 30 * (1 - abs(t - 0.5) * 1.2))
        b = int(100 + 40 * (1 - abs(t - 0.5) * 1.2))
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Aged paper texture — scattered speckles
    for _ in range(3000):
        sx, sy = random.randint(0, W), random.randint(0, H)
        sr = random.randint(1, 3)
        sd = random.randint(40, 80)
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(sd, sd, sd, 30))

    # Compass rose (upper left area)
    cx, cy = 200, 300
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        length = 80 if angle % 90 == 0 else 50
        ex = cx + length * math.cos(rad)
        ey = cy + length * math.sin(rad)
        draw.line((cx, cy, ex, ey), fill=(120, 90, 50, 200), width=3)
    # Compass circle
    draw.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), outline=(120, 90, 50, 180), width=3)
    draw.ellipse((cx - 100, cy - 100, cx + 100, cy + 100), outline=(120, 90, 50, 100), width=1)
    # N label
    nf = font("arial.ttf", 36)
    draw.text((cx - 15, cy - 125), "N", font=nf, fill=(180, 60, 40, 220))

    # Rhumb lines (navigational lines crossing the map)
    for _ in range(20):
        rx1, ry1 = random.randint(0, W), random.randint(0, 1600)
        rx2, ry2 = random.randint(0, W), random.randint(0, 1600)
        draw.line((rx1, ry1, rx2, ry2), fill=(140, 110, 70, 30), width=1)

    # Uncharted island in center
    island_center = (W // 2, 750)
    # Draw island as irregular polygon
    island_points = []
    num_points = 16
    for i in range(num_points):
        angle = 2 * math.pi * i / num_points
        base_radius = 180 + random.randint(-30, 30)
        # Make it irregular
        if i % 3 == 0:
            base_radius += 50
        if i % 5 == 0:
            base_radius -= 40
        px = island_center[0] + int(base_radius * math.cos(angle))
        py = island_center[1] + int(base_radius * 0.7 * math.sin(angle))
        island_points.append((px, py))
    draw.polygon(island_points, fill=(160, 140, 90, 220), outline=(100, 80, 40, 200), width=3)

    # Island interior detail — hills and shading
    for _ in range(30):
        hx = island_center[0] + random.randint(-120, 120)
        hy = island_center[1] + random.randint(-100, 100)
        hr = random.randint(10, 30)
        draw.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=(140, 120, 80, 100))

    # Coast soundings (depth numbers)
    sf = font("arial.ttf", 18)
    for _ in range(12):
        sx = island_center[0] + int(220 * math.cos(random.random() * 2 * math.pi))
        sy = island_center[1] + int(160 * math.sin(random.random() * 2 * math.pi))
        depth = str(random.randint(5, 40))
        draw.text((sx, sy), depth, font=sf, fill=(100, 80, 50, 120))

    # Sea monsters / mythical creatures
    # Sea serpent coil
    sx_start, sy_start = 1100, 500
    for i in range(8):
        sx = sx_start + i * 20
        sy = sy_start + int(25 * math.sin(i * 0.8))
        draw.ellipse((sx - 8, sy - 8, sx + 8, sy + 8), fill=(100, 140, 120, 80))
    # Head
    draw.ellipse((sx_start + 160, sy_start - 20, sx_start + 190, sy_start + 10), fill=(80, 120, 100, 100))

    # Sailing ship silhouette (upper right area)
    ship_x, ship_y = 1250, 600
    # Hull
    draw.polygon(
        [(ship_x - 100, ship_y), (ship_x - 120, ship_y + 40), (ship_x + 100, ship_y + 40), (ship_x + 80, ship_y)],
        fill=(60, 50, 35, 200),
    )
    # Masts
    for mx, mh in [(ship_x - 30, -120), (ship_x, -150), (ship_x + 30, -120)]:
        draw.line((mx, ship_y, mx, ship_y + mh), fill=(50, 40, 30, 200), width=4)
    # Sails
    for mx, mh, sw, sh in [
        (ship_x - 30, -110, 30, 60),
        (ship_x, -140, 40, 70),
        (ship_x + 30, -110, 30, 60),
    ]:
        draw.ellipse((mx - sw, ship_y + mh, mx + sw, ship_y + mh + sh), fill=(80, 70, 55, 180))

    # "Uncharted" label on map area
    ul = font("arial.ttf", 24)
    draw.text((island_center[0] - 60, island_center[1] + 130), "TERRA INCOGNITA", font=ul, fill=(120, 90, 50, 150))

    # Latitude / Longitude lines on edges
    for _ in range(6):
        ly = random.randint(100, 1500)
        draw.line((0, ly, W, ly), fill=(160, 130, 90, 40), width=1)
    for _ in range(4):
        lx = random.randint(50, 1550)
        draw.line((lx, 0, lx, 1800), fill=(160, 130, 90, 40), width=1)

    # Decorative border (old map style)
    draw.rectangle((20, 20, W - 20, H - 20), outline=(120, 90, 50, 150), width=4)
    draw.rectangle((30, 30, W - 30, H - 30), outline=(120, 90, 50, 80), width=1)

    # Vignette darkening at edges
    for y in range(H):
        t = y / H
        edge_factor = 1.0 - abs(t - 0.5) * 2
        edge_factor = max(0, edge_factor)
        edge_dark = 0
        if y < 100:
            edge_dark = int((100 - y) * 0.8)
        elif y > H - 100:
            edge_dark = int((y - (H - 100)) * 0.8)
        if edge_dark > 0:
            draw.line((0, y, W, y), fill=(0, 0, 0, edge_dark))

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(30, 25, 20, 245))
    # Gold lines
    draw.line((200, 1980, W - 200, 1980), fill=(200, 170, 90, 220), width=3)
    draw.line((200, H - 120, W - 200, H - 120), fill=(200, 170, 90, 100), width=1)

    # Fonts
    tf = font("georgiab.ttf", 90)
    af = font("arialbd.ttf", 40)
    sf_small = font("arial.ttf", 28)

    # Centered title on panel
    y = 2020
    wrapped_lines = wrap(draw, title.upper(), tf, 1300)
    y = centered(draw, y, wrapped_lines, tf, (210, 190, 140), 12)
    y += 40
    # Author
    centered(draw, y, [author], af, (200, 180, 130), 6)

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

    meta_path = ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata
    out_path = ROOT / a.out if not a.out.is_absolute() else a.out
    make_cover(meta_path, out_path)


if __name__ == "__main__":
    main()