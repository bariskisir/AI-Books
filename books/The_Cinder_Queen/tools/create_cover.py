#!/usr/bin/env python3
"""Cover: The Cinder Queen — Dark fantasy with ash crown and ember glow."""

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

    # Dark gradient: black at top -> crimson -> dark red at bottom
    for y in range(H):
        t = y / H
        if t < 0.4:
            # Black to deep crimson
            r = int(10 + 60 * (t / 0.4))
            g = int(5 + 15 * (t / 0.4))
            b = int(5 + 10 * (t / 0.4))
        elif t < 0.7:
            # Crimson to dark red
            r = int(70 + 80 * ((t - 0.4) / 0.3))
            g = int(20 + 20 * ((t - 0.4) / 0.3))
            b = int(15 + 10 * ((t - 0.4) / 0.3))
        else:
            # Dark red to near-black
            r = int(150 - 120 * ((t - 0.7) / 0.3))
            g = int(40 - 30 * ((t - 0.7) / 0.3))
            b = int(25 - 20 * ((t - 0.7) / 0.3))
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # --- Background: Ruined throne room arch ---
    # Left pillar
    draw.polygon(
        [(80, 400), (180, 400), (200, 2200), (60, 2200)],
        fill=(25, 15, 15, 200),
    )
    # Right pillar
    draw.polygon(
        [(W - 80, 400), (W - 180, 400), (W - 200, 2200), (W - 60, 2200)],
        fill=(25, 15, 15, 200),
    )
    # Arch
    for i in range(20):
        a = math.pi * (0.5 + i / 40)
        x = W // 2 + int(600 * math.cos(a))
        y0 = 400 + int(200 * math.sin(a))
        draw.ellipse((x - 8, y0 - 8, x + 8, y0 + 8), fill=(40 + i * 3, 20 + i * 2, 15, 180))
    # Arch connecting line
    draw.arc(
        [W // 2 - 620, 200, W // 2 + 620, 600],
        start=0, end=180, fill=(50, 25, 20, 180), width=12,
    )

    # Cracked stone floor
    for i in range(12):
        x0 = random.randint(100, W - 100)
        draw.line(
            (x0, 1900 + random.randint(0, 200), x0 + random.randint(-40, 40), 2200),
            fill=(15, 8, 8, 150),
            width=random.randint(2, 5),
        )

    # --- Crown: ash-covered, floating above a throne silhouette ---
    # Throne silhouette (lower center, ruins)
    tx, ty = W // 2, 1550
    draw.polygon(
        [(tx - 120, ty), (tx - 100, ty - 200), (tx - 80, ty - 180),
         (tx - 60, ty - 250), (tx - 40, ty - 230), (tx - 30, ty - 280),
         (tx, ty - 300), (tx + 30, ty - 280), (tx + 40, ty - 230),
         (tx + 60, ty - 250), (tx + 80, ty - 180), (tx + 100, ty - 200),
         (tx + 120, ty)],
        fill=(20, 12, 10, 220),
    )

    # Crown above throne
    crown_cx, crown_cy = W // 2, 1150
    crown_color = (60, 55, 50, 220)  # Ash-gray iron

    # Crown base band
    draw.rectangle(
        (crown_cx - 140, crown_cy + 40, crown_cx + 140, crown_cy + 80),
        fill=crown_color,
    )
    # Crown points (uneven like the description)
    points_heights = [160, 200, 140, 220, 180, 240, 170, 210, 150, 190, 160, 230, 170]
    for i, ph in enumerate(points_heights):
        px = crown_cx - 130 + i * 22
        draw.polygon(
            [(px, crown_cy + 40), (px + 6, crown_cy - ph), (px + 12, crown_cy + 40)],
            fill=(65 + random.randint(-10, 10), 58 + random.randint(-10, 10),
                  50 + random.randint(-10, 10), 230),
        )

    # Ash overlay on crown (darker patches)
    for _ in range(30):
        ax = crown_cx - 130 + random.randint(0, 260)
        ay = crown_cy - 200 + random.randint(0, 240)
        ar = random.randint(2, 8)
        draw.ellipse(
            (ax - ar, ay - ar, ax + ar, ay + ar),
            fill=(30, 25, 22, random.randint(80, 160)),
        )

    # --- Ember glow around crown ---
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    # Large soft glow
    gdraw.ellipse(
        (crown_cx - 300, crown_cy - 300, crown_cx + 300, crown_cy + 300),
        fill=(200, 50, 20, 40),
    )
    gdraw.ellipse(
        (crown_cx - 180, crown_cy - 180, crown_cx + 180, crown_cy + 180),
        fill=(255, 80, 30, 60),
    )
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Ember particles floating upward
    for _ in range(80):
        ex = crown_cx + random.randint(-200, 200)
        ey = crown_cy - random.randint(100, 600)
        er = random.randint(1, 4)
        eo = random.randint(80, 200)
        draw.ellipse(
            (ex - er, ey - er, ex + er, ey + er),
            fill=(255, random.randint(60, 180), random.randint(10, 60), eo),
        )

    # -- Bottom panel: light title panel --
    panel_y = 1920
    panel_h = H - panel_y
    draw.rectangle((0, panel_y, W, H), fill=(18, 15, 14, 240))

    # Decorative lines
    draw.line((220, panel_y + 30, W - 220, panel_y + 30), fill=(180, 80, 40, 200), width=2)
    draw.line((220, H - 120, W - 220, H - 120), fill=(180, 80, 40, 120), width=2)

    # Title
    tf = font("georgiab.ttf", 100)
    title_lines = wrap(draw, title.upper(), tf, 1100)
    if len(title_lines) > 2:
        tf = font("georgiab.ttf", 80)
        title_lines = wrap(draw, title.upper(), tf, 1100)
    y = centered(draw, panel_y + 80, title_lines, tf, (210, 170, 140), 10)

    # Author
    y += 40
    af = font("arialbd.ttf", 42)
    centered(draw, y, [author], af, (180, 160, 140), 6)

    # Small ember accents at bottom
    for _ in range(20):
        ex = random.randint(100, W - 100)
        ey = H - random.randint(50, 150)
        er = random.randint(1, 3)
        draw.ellipse(
            (ex - er, ey - er, ex + er, ey + er),
            fill=(255, random.randint(40, 120), 10, random.randint(60, 160)),
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