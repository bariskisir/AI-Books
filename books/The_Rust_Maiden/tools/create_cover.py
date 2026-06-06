#!/usr/bin/env python3
"""Cover: The Rust Maiden — Dieselpunk Dust Bowl with giant walker."""

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
    # Rust / bronze / dust gradient
    for y in range(H):
        t = y/H
        r = int(180-80*t); g = int(100-60*t); b = int(30-20*t)
        draw.line((0,y,W,y), fill=(max(0,r),max(0,g),max(0,b),255))
    # Dust storm haze layer
    haze = Image.new("RGBA", (W, H), (0,0,0,0)); hd = ImageDraw.Draw(haze)
    for _ in range(80):
        x = int(random.random()*W); y = int(random.random()*H*0.75)
        s = int(10+30*random.random()); a = int(20+40*random.random())
        hd.ellipse((x-s,y-s,x+s,y+s), fill=(200,160,100,a))
    haze = haze.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, haze); draw = ImageDraw.Draw(img, "RGBA")
    # Giant walker silhouette (Iron Judge)
    wx, wy = W//2, int(H*0.45)
    # Body
    draw.polygon([(wx-120,wy-180),(wx+120,wy-180),(wx+160,wy),(wx-160,wy)], fill=(25,20,15,200))
    # Head / cockpit
    draw.rectangle((wx-40,wy-240,wx+40,wy-180), fill=(25,20,15,200))
    # Gun barrel
    draw.line((wx+120,wy-150,wx+280,wy-200), fill=(25,20,15,200), width=14)
    draw.line((wx+120,wy-150,wx+280,wy-200), fill=(60,50,40,100), width=10)
    # Legs
    draw.line((wx-80,wy,wx-120,wy+320), fill=(25,20,15,200), width=28)
    draw.line((wx+80,wy,wx+120,wy+320), fill=(25,20,15,200), width=28)
    draw.line((wx-120,wy+320,wx-160,wy+380), fill=(25,20,15,200), width=22)
    draw.line((wx+120,wy+320,wx+160,wy+380), fill=(25,20,15,200), width=22)
    # Knee joints glow (orange)
    draw.ellipse((wx-145,wy+140,wx-95,wy+190), fill=(220,120,40,150))
    draw.ellipse((wx+95,wy+140,wx+145,wy+190), fill=(220,120,40,150))
    # Small mechanic figure in front of walker
    mx, my = wx, wy+80
    draw.line((mx-12,my+40,mx,my,mx+12,my+40), fill=(30,25,20,255), width=5)
    draw.ellipse((mx-6,my-30,mx+6,my-18), fill=(30,25,20,255))
    # Wrench in hand
    draw.line((mx+12,my+10,mx+30,my-10), fill=(180,120,60,255), width=4)
    draw.ellipse((mx+28,my-16,mx+32,my-4), fill=(180,120,60,255))
    # Dust particles / debris around walker
    for _ in range(40):
        x = int(wx-300+600*random.random()); y = int(wy+100+200*random.random())
        r = int(2+6*random.random()); a = int(30+60*random.random())
        draw.ellipse((x-r,y-r,x+r,y+r), fill=(180,140,80,a))
    # Sun through dust
    sun_x, sun_y = W//2, int(H*0.15)
    sun = Image.new("RGBA", (W,H), (0,0,0,0)); sd = ImageDraw.Draw(sun)
    sd.ellipse((sun_x-120,sun_y-120,sun_x+120,sun_y+120), fill=(255,200,100,80))
    sun = sun.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, sun); draw = ImageDraw.Draw(img, "RGBA")
    # Title panel at bottom
    draw.rectangle((0,1920,W,H), fill=(15,12,10,240))
    draw.line((200,1960,W-200,1960), fill=(200,150,70,200), width=3)
    draw.line((200,H-160,W-200,H-160), fill=(200,150,70,120), width=2)
    # Rust ornament lines in panel
    for i in range(10):
        yp = 1980 + i*50
        draw.line((100,yp,W-100,yp), fill=(120,60,30,int(10+15*random.random())), width=1)
    tf = font("georgiab.ttf", 120); af = font("arialbd.ttf", 44)
    sf = font("arial.ttf", 28)
    y = centered(draw, 2030, ["DIESELPUNK NOVEL"], sf, (200,150,70), 6)
    y += 50
    y = centered(draw, y, wrap(draw, title.upper(), tf, 1300), tf, (220,180,110), 10)
    y += 70
    centered(draw, y, [f"by {author}"], af, (200,180,150), 6)
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