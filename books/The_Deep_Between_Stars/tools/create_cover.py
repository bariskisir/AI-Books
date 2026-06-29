#!/usr/bin/env python3
"""Cover: The Deep Between Stars — oceanic horror at the Marianas Trench."""

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
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep ocean gradient: black to deep blue to dark teal
    for y in range(H):
        t = y / H
        if t < 0.3:
            # Very dark abyss black
            v = int(5 + 10 * (t / 0.3))
            r, g, b = v, v, v + 8
        elif t < 0.7:
            # Transition to deep blue
            s = (t - 0.3) / 0.4
            r = int(5 + 15 * s)
            g = int(5 + 30 * s)
            b = int(13 + 80 * s)
        else:
            # Dark teal black
            s2 = (t - 0.7) / 0.3
            r = int(20 - 10 * s2)
            g = int(35 - 20 * s2)
            b = int(93 - 50 * s2)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Bioluminescent particles (scattered in upper middle)
    import random
    for _ in range(200):
        x = int(W * random.random())
        y = int(300 + 1400 * random.random())
        r = int(2 + 5 * random.random())
        alpha = int(20 + 80 * random.random())
        # Blue-green glow
        draw.ellipse(
            (x - r, y - r, x + r, y + r),
            fill=(100 + int(100 * random.random()), 200, 220, alpha),
        )

    # Bioluminescent glow layer
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for _ in range(30):
        x = int(W * random.random())
        y = int(200 + 1400 * random.random())
        rad = int(20 + 80 * random.random())
        alpha = int(15 + 40 * random.random())
        gdraw.ellipse(
            (x - rad, y - rad, x + rad, y + rad),
            fill=(60, 180, 220, alpha),
        )
    glow = glow.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Abyssal trench wall silhouette (left)
    points_left = []
    for y in range(400, 1600, 10):
        offset = int(80 + 40 * (1 + math.sin(y * 0.02 + 1.3)) * 0.5)
        x = 100 + offset + int(30 * (1 + math.sin(y * 0.015)))
        points_left.append((x, y))
    points_left += [(0, 1600), (0, 400)]
    draw.polygon(points_left, fill=(10, 15, 30, 220))

    # Abyssal trench wall silhouette (right)
    points_right = []
    for y in range(400, 1600, 10):
        offset = int(80 + 40 * (1 + math.sin(y * 0.018 + 2.1)) * 0.5)
        x = W - 100 - offset - int(30 * (1 + math.sin(y * 0.012 + 0.7)))
        points_right.append((x, y))
    points_right += [(W, 1600), (W, 400)]
    draw.polygon(points_right, fill=(8, 12, 25, 220))

    # Seafloor ridge at bottom
    floor = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fdraw = ImageDraw.Draw(floor)
    fdraw.polygon(
        [(0, 1700), (W, 1700), (W, 1850), (0, 1850)],
        fill=(8, 10, 20, 200),
    )
    fdraw.polygon(
        [(0, 1800), (W // 2 - 200, 1750), (W, 1800), (W, 1920), (0, 1920)],
        fill=(12, 15, 28, 200),
    )
    img = Image.alpha_composite(img, floor)
    draw = ImageDraw.Draw(img, "RGBA")

    # Research station lights in the abyss
    # Station body
    station_x, station_y = W // 2, 1200
    draw.rectangle(
        (station_x - 40, station_y - 60, station_x + 40, station_y + 60),
        fill=(60, 70, 90, 200),
        outline=(100, 140, 180, 180),
        width=2,
    )
    # Station modules
    draw.rectangle(
        (station_x - 55, station_y - 30, station_x - 40, station_y + 30),
        fill=(50, 60, 80, 200),
    )
    draw.rectangle(
        (station_x + 40, station_y - 40, station_x + 55, station_y + 40),
        fill=(50, 60, 80, 200),
    )
    # Floodlight beams
    for angle in [-1, 0, 1]:
        lx = station_x + angle * 30
        ly = station_y + 60
        for i in range(8):
            alpha = 40 - 5 * i
            w = 8 + i * 6
            draw.ellipse(
                (lx - w, ly + i * 8 - 2, lx + w, ly + i * 8 + 2),
                fill=(180, 220, 255, alpha),
            )
    # Bright window lights
    for wy in range(-40, 41, 20):
        draw.rectangle(
            (station_x - 5, station_y + wy - 4, station_x + 5, station_y + wy + 4),
            fill=(200, 230, 255, 220),
        )
    # Light glow around station
    slayer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(slayer)
    sdraw.ellipse(
        (station_x - 120, station_y - 100, station_x + 120, station_y + 100),
        fill=(80, 150, 220, 30),
    )
    slayer = slayer.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, slayer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Cable / tether line from station down into darkness
    draw.line(
        (station_x, station_y + 60, W // 2 + 30, 1700),
        fill=(40, 50, 70, 150),
        width=2,
    )
    # Small descending sub shape on cable
    draw.ellipse(
        (W // 2 + 10, 1500, W // 2 + 50, 1530),
        fill=(50, 65, 90, 200),
    )

    # Title panel at bottom
    # Accent line top of panel
    # Accent line bottom
    draw.line((250, H - 200, W - 250, H - 200), fill=(80, 150, 200, 100), width=2)

    # Title text
    ttf = font("georgiab.ttf", 90)
    title_lines = wrap(draw, title, ttf, 1300)

    y = centered(
        draw,
        1990,
        ["A NOVEL OF THE DEEP"],
        font("arial.ttf", 28),
        (100, 160, 200),
        4,
    )
    y += 20
    y = centered(draw, y, title_lines, ttf, (180, 210, 240), 8)
    y += 30

    # Author name
    autf = font("arialbd.ttf", 40)
    centered(draw, y, [author], autf, (150, 170, 200), 6)

    # Subtitle line
    sf = font("arial.ttf", 22)
    centered(
        draw,
        H - 130,
        ["OCEANIC HORROR"],
        sf,
        (90, 120, 150),
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