#!/usr/bin/env python3
"""Cover: Red Phoenix Rising — city skyline at sunset with hero silhouette."""

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

    # Sunset gradient: deep red -> orange -> yellow -> dark purple sky
    for y in range(H):
        t = y / H
        if t < 0.3:
            # Upper sky: deep purple to red
            r = int(180 - 80 * (t / 0.3))
            g = int(60 - 40 * (t / 0.3))
            b = int(120 - 60 * (t / 0.3))
        elif t < 0.55:
            # Mid sky: red to orange
            lt = (t - 0.3) / 0.25
            r = int(100 + 155 * lt)
            g = int(20 + 120 * lt)
            b = int(60 - 50 * lt)
        else:
            # Lower sky: orange to dark
            lt = (t - 0.55) / 0.45
            r = int(255 - 180 * lt)
            g = int(140 - 110 * lt)
            b = int(10 - 10 * lt)
        draw.line((0,y,W,y), fill=(max(0,min(255,r)),max(0,min(255,g)),max(0,min(255,b)),255))

    # Sun glow
    sun = Image.new("RGBA", (W,H), (0,0,0,0)); sd = ImageDraw.Draw(sun)
    sd.ellipse((W//2-250, 900, W//2+250, 1400), fill=(255,200,80,180))
    sd.ellipse((W//2-150, 950, W//2+150, 1350), fill=(255,220,120,220))
    sun = sun.filter(ImageFilter.GaussianBlur(40))
    img = Image.alpha_composite(img, sun); draw = ImageDraw.Draw(img, "RGBA")

    # City skyline silhouette
    buildings = [
        (200, 1300, 80, 400), (280, 1280, 60, 350), (340, 1350, 100, 300),
        (440, 1200, 70, 500), (510, 1250, 90, 450), (600, 1300, 80, 380),
        (680, 1150, 100, 550), (780, 1180, 70, 480), (850, 1220, 60, 400),
        (910, 1300, 90, 350), (1000, 1250, 100, 400), (1100, 1200, 80, 500),
        (1180, 1280, 70, 380), (1250, 1320, 90, 320), (1340, 1300, 80, 350),
    ]
    skyline_color = (10, 8, 15, 230)
    for bx, by, bw, bh in buildings:
        draw.rectangle((bx, by, bx+bw, by+bh), fill=skyline_color)
        # Windows
        for wy in range(by+20, by+bh-20, 45):
            for wx in range(bx+10, bx+bw-10, 25):
                if (wx // 25 + wy // 45) % 3 == 0:
                    draw.rectangle((wx, wy, wx+8, wy+12), fill=(255,200,100,80))

    # Tallest tower with spire
    tx, ty, tw, th = 740, 950, 80, 750
    draw.rectangle((tx, ty, tx+tw, ty+th), fill=skyline_color)
    # Spire
    draw.polygon([(tx+tw//2, ty-120), (tx+tw//2-15, ty), (tx+tw//2+15, ty)], fill=skyline_color)

    # Hero silhouette on rooftop
    hx, hy = 760, 950
    # Body
    draw.line((hx, hy, hx, hy+100), fill=(5,5,10,255), width=8)
    # Arms outstretched
    draw.line((hx-60, hy+20, hx+60, hy+20), fill=(5,5,10,255), width=6)
    # Head
    draw.ellipse((hx-12, hy-30, hx+12, hy-6), fill=(5,5,10,255))
    # Cape billowing
    draw.polygon([(hx-50, hy-10), (hx-120, hy+60), (hx-80, hy+100), (hx-40, hy+40)], fill=(60,15,15,200))
    draw.polygon([(hx+50, hy-10), (hx+120, hy+60), (hx+80, hy+100), (hx+40, hy+40)], fill=(60,15,15,200))
    # Phoenix emblem on chest (small circle)
    draw.ellipse((hx-10, hy+30, hx+10, hy+50), fill=(220,80,30,200))

    # Smoke/ash particles
    for _ in range(80):
        x = int(W * __import__('random').random())
        y = int(800 + 600 * __import__('random').random())
        r = int(2 + 5 * __import__('random').random())
        a = int(20 + 40 * __import__('random').random())
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(200,150,80,a))

    # Title panel — light rectangle at bottom
    draw.rectangle((0, 1920, W, H), fill=(20, 18, 22, 245))
    draw.line((300, 1960, W-300, 1960), fill=(255, 180, 60, 200), width=3)
    draw.line((300, H-150, W-300, H-150), fill=(255, 180, 60, 120), width=2)

    # Title
    tf = font("georgiab.ttf", 110)
    af = font("arialbd.ttf", 42)
    sf = font("arial.ttf", 28)

    y = 2010
    tw_lines = wrap(draw, title.upper(), tf, 1200)
    if len(tw_lines) > 1:
        tf2 = font("georgiab.ttf", 80)
        tw_lines = wrap(draw, title.upper(), tf2, 1200)
        y = centered(draw, y, tw_lines, tf2, (255, 190, 80), 8)
    else:
        y = centered(draw, y, tw_lines, tf, (255, 190, 80), 8)

    y += 30
    centered(draw, y, ["SUPERHERO NOVEL"], sf, (200, 180, 160), 4)
    y += 35
    centered(draw, y, [author], af, (220, 200, 180), 6)

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