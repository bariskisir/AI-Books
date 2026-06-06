#!/usr/bin/env python3
"""Cover: The Kaiser's Watch — alternate history Berlin spy thriller."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()

def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0,0), p, font=fnt)[2] <= mw: cur.append(w)
        else: lines.append(" ".join(cur)); cur = [w]
    if cur: lines.append(" ".join(cur))
    return lines

def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0,0), line, font=fnt)
        draw.text(((W-(bb[2]-bb[0]))//2, y), line, font=fnt, fill=fill)
        y += bb[3]-bb[1] + gap
    return y

def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    img = Image.new("RGBA", (W, H), (0,0,0,255)); draw = ImageDraw.Draw(img, "RGBA")

    # Iron-blue to dark-gray gradient background
    for y in range(H):
        t = y / H
        r = int(70 - 40 * t); g = int(85 - 45 * t); b = int(110 - 55 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Clouds / mist layer
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0)); md = ImageDraw.Draw(mist)
    for _ in range(25):
        cx = int(1600 * __import__("random").random())
        cy = int(400 + 300 * __import__("random").random())
        rx = int(300 + 500 * __import__("random").random())
        ry = int(40 + 60 * __import__("random").random())
        md.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(180, 190, 210, 20))
    mist = mist.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img, "RGBA")

    # Berlin building silhouettes
    buildings = [
        (0, 900, 180, 1400), (160, 870, 140, 1430),
        (280, 920, 200, 1380), (450, 850, 120, 1450),
        (550, 890, 180, 1410), (700, 860, 160, 1440),
        (830, 910, 140, 1390), (950, 880, 200, 1420),
        (1100, 850, 150, 1450), (1220, 890, 170, 1410),
        (1360, 870, 140, 1430), (1480, 900, 120, 1400),
    ]
    for bx, by, bw, bh in buildings:
        draw.rectangle((bx, by, bx + bw, by + bh), fill=(25, 30, 40, 220))
        # Windows
        for wy in range(by + 30, by + bh - 40, 50):
            for wx in range(bx + 15, bx + bw - 15, 35):
                if __import__("random").random() > 0.3:
                    draw.rectangle((wx, wy, wx + 12, wy + 18), fill=(200, 180, 120, 60))

    # Imperial flags on buildings
    flag_poles = [(200, 870), (500, 850), (800, 910), (1050, 880)]
    for fx, fy in flag_poles:
        draw.rectangle((fx, fy - 120, fx + 4, fy), fill=(100, 90, 80, 220))
        # Flag: black-white-red horizontal stripes
        flag_w, flag_h = 50, 30
        draw.rectangle((fx + 4, fy - 120, fx + 4 + flag_w, fy - 120 + flag_h // 3), fill=(30, 30, 30, 220))
        draw.rectangle((fx + 4, fy - 120 + flag_h // 3, fx + 4 + flag_w, fy - 120 + 2 * flag_h // 3), fill=(220, 220, 220, 220))
        draw.rectangle((fx + 4, fy - 120 + 2 * flag_h // 3, fx + 4 + flag_w, fy - 120 + flag_h), fill=(180, 30, 30, 220))

    # Cobblestone street
    for y in range(1400, 1520, 8):
        shade = 50 + int(20 * math.sin(y * 0.1))
        draw.line((0, y, W, y), fill=(shade, shade - 5, shade - 10, 200))

    # Large clock face floating above the street
    cx, cy = W // 2, 580
    clock_r = 200
    # Clock outer ring
    draw.ellipse((cx - clock_r, cy - clock_r, cx + clock_r, cy + clock_r), fill=(180, 170, 140, 200))
    draw.ellipse((cx - clock_r + 12, cy - clock_r + 12, cx + clock_r - 12, cy + clock_r - 12), fill=(220, 215, 190, 230))
    draw.ellipse((cx - clock_r + 20, cy - clock_r + 20, cx + clock_r - 20, cy + clock_r - 20), fill=(245, 240, 220, 240))
    # Hour markers
    for i in range(12):
        angle = math.radians(i * 30 - 90)
        x1 = cx + 150 * math.cos(angle)
        y1 = cy + 150 * math.sin(angle)
        x2 = cx + 175 * math.cos(angle)
        y2 = cy + 175 * math.sin(angle)
        draw.line((x1, y1, x2, y2), fill=(40, 40, 50, 220), width=6)
    # Clock hands
    import datetime
    now = datetime.datetime.now()
    h_angle = math.radians((now.hour % 12) * 30 + now.minute * 0.5 - 90)
    m_angle = math.radians(now.minute * 6 - 90)
    draw.line((cx, cy, cx + 90 * math.cos(h_angle), cy + 90 * math.sin(h_angle)), fill=(40, 40, 50, 220), width=8)
    draw.line((cx, cy, cx + 130 * math.cos(m_angle), cy + 130 * math.sin(m_angle)), fill=(40, 40, 50, 220), width=5)
    draw.ellipse((cx - 10, cy - 10, cx + 10, cy + 10), fill=(40, 40, 50, 220))

    # Clock shadow/glow
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((cx - clock_r - 30, cy - clock_r - 30, cx + clock_r + 30, cy + clock_r + 30), fill=(200, 190, 160, 20))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Title panel at bottom
    draw.rectangle((0, 1920, W, H), fill=(20, 22, 30, 240))
    # Decorative line top
    draw.line((200, 1940, W - 200, 1940), fill=(180, 170, 140, 200), width=3)
    # Decorative line bottom
    draw.line((200, H - 120, W - 200, H - 120), fill=(180, 170, 140, 120), width=2)

    # Small genre text
    centered(draw, 1970, ["ALTERNATE HISTORY  |  SPY THRILLER"], font("arial.ttf", 28), (160, 155, 140), 6)

    # Title
    tf = font("georgiab.ttf", 120)
    title_lines = wrap(draw, title.upper(), tf, 1300)
    y = 2070
    y = centered(draw, y, title_lines, tf, (200, 190, 165), 10)

    # Author
    y += 50
    af = font("arialbd.ttf", 44)
    centered(draw, y, [author], af, (180, 175, 160), 6)

    # Tagline
    y += 80
    sf = font("arial.ttf", 26)
    centered(draw, y, ["A CLOCKMAKER. A SPY. A CITY OF SECRETS."], sf, (140, 135, 125), 6)

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
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
               ROOT / a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__":
    main()