#!/usr/bin/env python3
"""Cover: The Moscow Protocol — Kremlin silhouette, gray winter, red accents."""

from __future__ import annotations
import argparse, json, math, random
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
    # Gray winter gradient — cold steel sky fading to dirty snow
    for y in range(H):
        t = y/H
        r = int(90 - 50*t); g = int(95 - 50*t); b = int(105 - 50*t)
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))
    # Red accent glow low on horizon
    glow = Image.new("RGBA", (W,H), (0,0,0,0)); gd = ImageDraw.Draw(glow)
    gd.ellipse((W//2-400, 1400, W//2+400, 1800), fill=(180,30,30,60))
    glow = glow.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, glow); draw = ImageDraw.Draw(img, "RGBA")
    # Kremlin wall silhouette
    wall_y = 1300
    draw.rectangle((100, wall_y, W-100, wall_y+180), fill=(25, 25, 30, 220))
    # Crenellations (merlons) along top of wall
    for x in range(100, W-100, 45):
        draw.rectangle((x, wall_y-40, x+30, wall_y), fill=(25, 25, 30, 220))
    # Kremlin towers
    towers = [
        (200, 1200, 60, 120),   # left tower
        (W//2-40, 1150, 80, 150), # central Savior Tower
        (W-200, 1200, 60, 120)   # right tower
    ]
    for tx, ty, tw, th in towers:
        draw.rectangle((tx-tw//2, ty, tx+tw//2, ty+th), fill=(20, 20, 25, 220))
        # Spire
        spire_h = 60
        draw.polygon([(tx-tw//4, ty), (tx, ty-spire_h), (tx+tw//4, ty)], fill=(25, 25, 30, 220))
        # Red star at top of central tower
        if abs(tx - W//2) < 10:
            draw.polygon([(tx, ty-spire_h-25), (tx-12, ty-spire_h-5), (tx+12, ty-spire_h-5)], fill=(180,20,20,200))
            draw.polygon([(tx, ty-spire_h-25), (tx-10, ty-spire_h-15), (tx+10, ty-spire_h-15)], fill=(200,25,25,200))
    # Snowy ground
    draw.rectangle((0, wall_y+180, W, H), fill=(60, 65, 70, 200))
    # Coat silhouette — a figure in a long winter coat
    fx, fy = W//2 + 200, 1350
    # Coat body
    draw.polygon([(fx-35, fy), (fx+35, fy), (fx+30, fy+200), (fx-30, fy+200)], fill=(15, 12, 10, 200))
    # Head
    draw.ellipse((fx-15, fy-50, fx+15, fy-10), fill=(10, 10, 12, 200))
    # Hat
    draw.rectangle((fx-20, fy-70, fx+20, fy-45), fill=(10, 10, 12, 200))
    # Coat collar lifted
    draw.polygon([(fx-35, fy), (fx-25, fy+30), (fx+25, fy+30), (fx+35, fy)], fill=(20, 18, 15, 200))
    # Breath mist
    for _ in range(8):
        bx = fx + random.randint(-20, 20)
        by = fy + random.randint(-60, -30)
        br = random.randint(8, 20)
        draw.ellipse((bx-br, by-br, bx+br, by+br), fill=(200,200,210,15+random.randint(0,15)))
    # Snowflakes
    for _ in range(80):
        sx = random.randint(0, W)
        sy = random.randint(0, H)
        sr = random.randint(1, 3)
        draw.ellipse((sx-sr, sy-sr, sx+sr, sy+sr), fill=(220,220,230,40+random.randint(0,60)))
    # Red accent line across lower third
    draw.line((0, 1920, W, 1920), fill=(180, 40, 40, 200), width=3)
    # Title panel
    draw.rectangle((0, 1960, W, H), fill=(20, 22, 28, 245))
    draw.line((240, 2000, W-240, 2000), fill=(180, 40, 40, 180), width=2)
    draw.line((240, H-180, W-240, H-180), fill=(180, 40, 40, 80), width=1)
    tf = font("georgiab.ttf", 100); af = font("arialbd.ttf", 40); sf = font("arial.ttf", 28)
    y = centered(draw, 2020, ["A SPY THRILLER"], sf, (180, 40, 40), 6)
    y += 30
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1200), tf, (210, 205, 200), 10)
    y += 50
    centered(draw, y, [author], af, (190, 185, 180), 6)
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
    make_cover(ROOT/a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT/a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__": main()