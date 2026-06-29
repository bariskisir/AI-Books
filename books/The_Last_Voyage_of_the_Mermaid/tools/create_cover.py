#!/usr/bin/env python3
"""Cover: The Last Voyage of the Mermaid — nautical horror, derelict yacht at sea."""

from __future__ import annotations
import argparse, json, math, random
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
    p = FONT_DIR / name
    if p.exists():
        return ImageFont.truetype(str(p), size)
    # fallback
    for alt in ["arial.ttf", "Arial.ttf"]:
        fp = FONT_DIR / alt
        if fp.exists():
            return ImageFont.truetype(str(fp), size)
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
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Midnight sea gradient: black to deep blue-black to dark teal
    for y in range(H):
        t = y / H
        if t < 0.15:
            # Pure black sky
            v = int(3 + 5 * (t / 0.15))
            r, g, b = v, v, v + 2
        elif t < 0.4:
            # Dark horizon transition
            s = (t - 0.15) / 0.25
            r = int(8 + 20 * s)
            g = int(8 + 25 * s)
            b = int(10 + 50 * s)
        elif t < 0.7:
            # Sea surface, dark teal
            s2 = (t - 0.4) / 0.3
            r = int(28 - 15 * s2)
            g = int(33 - 18 * s2)
            b = int(60 - 30 * s2)
        else:
            # Deep water, nearly black
            s3 = (t - 0.7) / 0.3
            r = int(13 - 8 * s3)
            g = int(15 - 10 * s3)
            b = int(30 - 20 * s3)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Moon
    moon_x, moon_y = 1100, 200
    moon_r = 60
    # Moon glow
    glow_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    glow_draw.ellipse(
        (moon_x - moon_r * 4, moon_y - moon_r * 4, moon_x + moon_r * 4, moon_y + moon_r * 4),
        fill=(180, 200, 220, 20),
    )
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, glow_img)

    # Moon body
    draw.ellipse(
        (moon_x - moon_r, moon_y - moon_r, moon_x + moon_r, moon_y + moon_r),
        fill=(200, 210, 220, 180),
    )
    # Moon craters (subtle)
    for _ in range(6):
        cx = moon_x + int(random.gauss(0, 25))
        cy = moon_y + int(random.gauss(0, 25))
        cr = int(4 + 8 * random.random())
        draw.ellipse(
            (cx - cr, cy - cr, cx + cr, cy + cr),
            fill=(160, 175, 190, 60),
        )

    # Moon reflection on water
    for i in range(6):
        ry = int(1020 + i * 20 + 10 * random.random())
        rw = int(80 - i * 10 + 20 * random.random())
        alpha = int(30 - i * 4)
        draw.ellipse(
            (moon_x - rw, ry - 2, moon_x + rw, ry + 2),
            fill=(180, 200, 220, max(0, alpha)),
        )

    # Stars
    for _ in range(300):
        sx = int(W * random.random())
        sy = int(400 * random.random())
        sr = 1 + int(2 * random.random())
        alpha = int(80 + 120 * random.random())
        draw.ellipse(
            (sx - sr, sy - sr, sx + sr, sy + sr),
            fill=(200, 210, 230, alpha),
        )

    # Derelict Yacht silhouette
    yacht_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    yachtdraw = ImageDraw.Draw(yacht_layer)

    # Hull - center bottom, angled slightly
    hull_pts = [
        (400, 1100),   # bow left
        (1200, 1100),  # stern right
        (1300, 1180),  # stern bottom
        (300, 1180),   # bow bottom
    ]
    yachtdraw.polygon(hull_pts, fill=(25, 30, 40, 220))

    # Hull detail line
    yachtdraw.line(
        (420, 1130, 1240, 1130),
        fill=(50, 55, 70, 150), width=2,
    )

    # Deck
    deck_pts = [
        (450, 1100),   # bow deck
        (1150, 1100),  # stern deck
        (1200, 1060),  # stern upper
        (500, 1060),   # bow upper
    ]
    yachtdraw.polygon(deck_pts, fill=(30, 35, 50, 200))

    # Cabin / upper structure
    cabin_pts = [
        (650, 1060),
        (1050, 1060),
        (1000, 960),
        (700, 960),
    ]
    yachtdraw.polygon(cabin_pts, fill=(18, 22, 35, 220))

    # Bridge / wheelhouse
    bridge_pts = [
        (750, 960),
        (950, 960),
        (920, 890),
        (780, 890),
    ]
    yachtdraw.polygon(bridge_pts, fill=(22, 28, 42, 230))

    # Windows on cabin (glowing faintly)
    for wx in [730, 780, 830, 880, 930]:
        yachtdraw.rectangle(
            (wx, 1000, wx + 30, 1040),
            fill=(120, 140, 160, 60),
            outline=(180, 190, 200, 40),
        )
    # Bridge windows
    for wx in [790, 830, 870]:
        yachtdraw.rectangle(
            (wx, 910, wx + 25, 950),
            fill=(140, 160, 180, 70),
            outline=(200, 210, 220, 50),
        )

    # Mast / rigging
    yachtdraw.line((820, 890, 820, 700), fill=(25, 30, 45, 180), width=3)
    yachtdraw.line((820, 700, 780, 680), fill=(25, 30, 45, 150), width=2)
    yachtdraw.line((820, 700, 860, 680), fill=(25, 30, 45, 150), width=2)

    # Rigging lines
    yachtdraw.line((780, 680, 500, 1060), fill=(20, 25, 40, 100), width=1)
    yachtdraw.line((860, 680, 1150, 1060), fill=(20, 25, 40, 100), width=1)

    # Frayed party streamers hanging from rigging
    streamer_colors = [(180, 140, 160, 80), (160, 180, 140, 80), (140, 160, 180, 80)]
    for sx in [780, 800, 820, 840, 860]:
        sc = random.choice(streamer_colors)
        for i in range(3):
            sy = 680 + i * 30
            swob = 5 + int(10 * random.random())
            yachtdraw.arc(
                (sx - swob, sy, sx + swob, sy + 25),
                180, 360,
                fill=sc, width=2,
            )

    # Bowsprit
    yachtdraw.line((450, 1100, 350, 1080), fill=(25, 30, 45, 180), width=3)

    # Lifeboat on deck
    yachtdraw.ellipse(
        (580, 1070, 630, 1095),
        fill=(40, 45, 60, 200),
    )

    img = Image.alpha_composite(img, yacht_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Water surface detail - wave lines at waterline
    for wx in range(0, W, 30):
        wy = 1130 + int(15 * math.sin(wx * 0.05 + 2))
        draw.line(
            (wx - 15, wy, wx + 15, wy + int(5 * math.sin(wx * 0.03))),
            fill=(15, 18, 30, 120), width=2,
        )

    # Bone white shapes — ghostly figures on deck (subtle)
    figure_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(figure_layer)
    for fx, fy in [(680, 1065), (720, 1062), (760, 1063), (1100, 1065), (1060, 1061)]:
        for _ in range(1):
            # Ghost figure, faint
            alpha = int(15 + 25 * random.random())
            fdraw.ellipse(
                (fx - 4, fy - 15, fx + 4, fy + 5),
                fill=(200, 210, 220, alpha),
            )
            fdraw.rectangle(
                (fx - 3, fy + 5, fx + 3, fy + 20),
                fill=(200, 210, 220, alpha - 5),
            )
    figure_layer = figure_layer.filter(ImageFilter.GaussianBlur(3))
    img = Image.alpha_composite(img, figure_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Title panel at bottom
    # Accent lines - bone white
    draw.line((200, H - 180, W - 200, H - 180), fill=(200, 200, 210, 80), width=2)

    # Title text - use arialbd as instructed
    ttf = font("arialbd.ttf", 86)
    title_lines = wrap(draw, title, ttf, 1300)

    y = 2000
    y = centered(draw, y, title_lines, ttf, (230, 235, 245), 8)
    y += 30

    # Author name
    autf = font("arial.ttf", 36)
    centered(draw, y, [author], autf, (180, 190, 200), 6)

    # Genre line at bottom
    sf = font("arial.ttf", 22)
    centered(
        draw,
        H - 120,
        ["NAUTICAL HORROR"],
        sf,
        (120, 130, 150),
        4,
    )

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op, "PNG", optimize=True)



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