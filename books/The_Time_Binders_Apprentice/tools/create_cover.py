#!/usr/bin/env python3
"""Cover: The Time-Binder's Apprentice — clockwork gears, Edwardian London, timeline threads."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int):
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            try:
                from PIL import ImageFont
                return ImageFont.truetype(str(c), size)
            except Exception:
                pass
    from PIL import ImageFont
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        bb = draw.textbbox((0, 0), p, font=fnt)
        if bb[2] <= mw:
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


def draw_gear(draw, cx, cy, inner_r, outer_r, teeth, angle_offset=0, fill=None, outline=None):
    """Draw a gear shape."""
    points = []
    for i in range(teeth * 2):
        a = angle_offset + (math.pi * i) / teeth
        r = outer_r if i % 2 == 0 else inner_r
        x = cx + r * math.cos(a)
        y = cy + r * math.sin(a)
        points.append((x, y))
    if fill:
        draw.polygon(points, fill=fill, outline=outline)


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Gradient background: deep teal to amber-gold
    for y in range(H):
        t = y / H
        r = int(10 + 220 * max(0, t - 0.3))
        g = int(15 + 180 * max(0, t - 0.3))
        b = int(50 + 100 * max(0, t - 0.3))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Glowing timeline threads (horizontal flowing lines)
    thread_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(thread_layer)
    for i in range(15):
        y_base = int(100 + 1400 * (i / 15) + random.randint(-30, 30))
        r = random.randint(0, 255)
        g = random.randint(180, 255)
        b = random.randint(50, 200)
        alpha = random.randint(60, 120)
        for x in range(0, W, 4):
            wave = int(8 * math.sin(x / 80 + i * 1.5))
            td.point((x, y_base + wave), fill=(r, g, b, alpha))
    thread_layer = thread_layer.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, thread_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Large gear behind (center, semitransparent)
    gear_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(gear_layer)
    draw_gear(gd, W // 2, 700, 200, 280, 24, angle_offset=0,
              fill=(200, 150, 60, 60), outline=(220, 180, 80, 100))
    draw_gear(gd, W // 2, 700, 80, 140, 12, angle_offset=0.3,
              fill=(180, 120, 40, 80), outline=(200, 160, 70, 100))
    gear_layer = gear_layer.filter(ImageFilter.GaussianBlur(4))
    img = Image.alpha_composite(img, gear_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Small gears scattered
    for cx, cy, outer, inner, teeth, off in [
        (300, 500, 60, 40, 8, 0.5),
        (1300, 400, 50, 32, 6, 1.2),
        (250, 1000, 40, 25, 6, 0.8),
        (1350, 950, 55, 35, 8, 0.2),
        (400, 300, 30, 18, 5, 0.9),
        (1200, 600, 45, 28, 6, 1.5),
        (800, 300, 35, 20, 5, 0.4),
    ]:
        glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gld = ImageDraw.Draw(glow)
        draw_gear(gld, cx, cy, inner, outer, teeth, off,
                  fill=(180, 140, 60, 80), outline=(220, 180, 80, 120))
        glow = glow.filter(ImageFilter.GaussianBlur(3))
        img = Image.alpha_composite(img, glow)

    draw = ImageDraw.Draw(img, "RGBA")
    for cx, cy, outer, inner, teeth, off in [
        (300, 500, 60, 40, 8, 0.5),
        (1300, 400, 50, 32, 6, 1.2),
        (250, 1000, 40, 25, 6, 0.8),
        (1350, 950, 55, 35, 8, 0.2),
        (400, 300, 30, 18, 5, 0.9),
        (1200, 600, 45, 28, 6, 1.5),
        (800, 300, 35, 20, 5, 0.4),
    ]:
        draw_gear(draw, cx, cy, inner, outer, teeth, off,
                  fill=None, outline=(230, 190, 100, 200))

    # Edwardian city silhouette
    silhouette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(silhouette)

    # Buildings
    buildings = [
        (100, 1100, 140, 500),
        (260, 1150, 100, 450),
        (380, 1050, 150, 550),
        (550, 1100, 80, 500),
        (650, 1080, 120, 520),
        (790, 1120, 100, 480),
        (910, 1060, 130, 540),
        (1060, 1100, 90, 500),
        (1170, 1090, 110, 510),
        (1300, 1070, 140, 530),
        (1460, 1110, 80, 490),
    ]
    for bx, by, bw, bh in buildings:
        sd.rectangle((bx, by, bx + bw, by + bh), fill=(15, 12, 10, 220))
        # windows
        wy = by + 30
        while wy < by + bh - 20:
            for wx in range(bx + 15, bx + bw - 15, 25):
                if random.random() > 0.4:
                    alpha = random.randint(80, 200)
                    sd.rectangle((wx, wy, wx + 10, wy + 14), fill=(255, 200, 80, alpha))
            wy += 25

    # Church spire
    spire_x = 750
    sd.polygon([(spire_x, 1060), (spire_x - 50, 1550), (spire_x + 50, 1550)], fill=(15, 12, 10, 220))
    sd.rectangle((spire_x - 80, 1500, spire_x + 80, 1580), fill=(15, 12, 10, 220))

    clock_tower = 1200
    sd.rectangle((clock_tower - 30, 1000, clock_tower + 30, 1600), fill=(15, 12, 10, 220))
    sd.rectangle((clock_tower - 45, 1000, clock_tower + 45, 1050), fill=(15, 12, 10, 220))
    # clock face
    sd.ellipse((clock_tower - 20, 1060, clock_tower + 20, 1100), fill=(200, 160, 60, 180))

    img = Image.alpha_composite(img, silhouette)

    # Glowing light burst from center
    burst = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(burst)
    for i in range(30):
        a = random.uniform(0, 2 * math.pi)
        length = random.randint(400, 800)
        for t_int in range(0, length, 20):
            t = float(t_int)
            x = W // 2 + t * math.cos(a)
            y = 700 + t * math.sin(a)
            if 0 <= x < W and 0 <= y < H:
                alpha = max(0, 60 - t // 15)
                bd.point((x, y), fill=(255, 200, 80, int(alpha)))
    burst = burst.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, burst)
    draw = ImageDraw.Draw(img, "RGBA")

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(12, 10, 8, 245))
    draw.line((220, 1960, W - 220, 1960), fill=(220, 180, 100, 200), width=3)
    draw.line((220, H - 160, W - 220, H - 160), fill=(220, 180, 100, 120), width=2)

    # Decorative gear icons on title panel sides
    for side_x in [100, W - 100]:
        for r_mult, sz in [(0, 10), (1, 6)]:
            draw_gear(draw, side_x, 2150 + r_mult * 30, sz - 3, sz, 6, angle_offset=r_mult * 0.5,
                      fill=(180, 140, 60, 100), outline=(200, 160, 70, 150))

    ttf = font("georgiab.ttf", 90)
    ttf2 = font("georgia.ttf", 80)
    af = font("arialbd.ttf", 36)

    y = centered(draw, 1980, ["TIME TRAVEL NOVEL"], font("arial.ttf", 28), (200, 160, 100), 6)
    y += 30

    title_text = title.upper()
    title_lines = wrap(draw, title_text, ttf, 1200)
    y = centered(draw, y, title_lines, ttf2, (220, 185, 120), 8)
    y += 40

    centered(draw, y, [author], af, (200, 190, 170), 6)

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