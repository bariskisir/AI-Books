#!/usr/bin/env python3
"""Cover: The Kaiser's Watch — alternate history Berlin spy thriller."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)


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
    model = m.get("model", "")
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
    # Decorative line top
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
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
               ROOT / a.out if not a.out.is_absolute() else a.out)

if __name__ == "__main__":
    main()