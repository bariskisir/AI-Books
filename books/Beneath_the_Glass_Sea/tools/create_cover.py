#!/usr/bin/env python3
"""Cover: Beneath the Glass Sea — underwater dome city, cracked glass."""

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

    # Deep ocean gradient — dark blue-green to deeper black-blue
    for y in range(H):
        t = y / H
        r = int(8 + 15 * (1 - t))
        g = int(50 + 30 * (1 - t) - 20 * t)
        b = int(100 + 80 * (1 - t) - 40 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Light rays filtering from above
    rays = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    rd = ImageDraw.Draw(rays)
    for i in range(7):
        x = 200 + i * 200 + random.randint(-50, 50)
        for j in range(60):
            alpha = max(0, 25 - j * 2 + random.randint(-5, 5))
            rd.line(
                (x, 0, x + random.randint(-40, 40), 1200 + j * 20),
                fill=(150, 220, 255, max(0, alpha)),
                width=random.randint(10, 30),
            )
    rays = rays.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, rays)
    draw = ImageDraw.Draw(img, "RGBA")

    # Underwater dome city — semi-ellipse
    dome_cx, dome_cy = W // 2, 1200
    dome_rx, dome_ry = 500, 400
    # Dome outline
    draw.arc(
        (dome_cx - dome_rx, dome_cy - dome_ry, dome_cx + dome_rx, dome_cy + dome_ry),
        0, 180, fill=(120, 200, 230, 60), width=8,
    )
    # Dome glass fill (translucent)
    dome_pts = []
    for a in range(181):
        rad = math.radians(a)
        x = dome_cx + dome_rx * math.cos(rad)
        y = dome_cy - dome_ry * math.sin(rad)
        dome_pts.append((x, y))
    dome_pts.append((dome_cx + dome_rx, dome_cy))
    dome_pts.append((dome_cx - dome_rx, dome_cy))
    draw.polygon(dome_pts, fill=(80, 160, 200, 40))

    # City buildings inside dome
    for i in range(20):
        bx = dome_cx - 400 + i * 42 + random.randint(-10, 10)
        bh = 80 + random.randint(40, 200)
        by = dome_cy - bh
        bw = 20 + random.randint(5, 20)
        if (bx - dome_cx) ** 2 / dome_rx**2 + (by + bh / 2 - dome_cy) ** 2 / dome_ry**2 < 0.8:
            draw.rectangle(
                (bx, by, bx + bw, dome_cy),
                fill=(30 + random.randint(0, 30), 50 + random.randint(0, 30), 80 + random.randint(0, 40), 180),
            )
            # Window lights
            for wy in range(by + 10, dome_cy - 10, 25):
                for wx in range(bx + 4, bx + bw - 4, 12):
                    if random.random() > 0.3:
                        draw.rectangle(
                            (wx, wy, wx + 6, wy + 8),
                            fill=(255, 220, 120, min(200, 100 + random.randint(0, 100))),
                        )

    # Cracked glass lines
    crack_start = (dome_cx - 100, dome_cy - dome_ry + 20)
    crack_color = (200, 230, 255, 120)
    segments = [(crack_start, (dome_cx - 50, dome_cy - dome_ry + 80))]
    segments.append(((dome_cx - 50, dome_cy - dome_ry + 80), (dome_cx + 30, dome_cy - dome_ry + 130)))
    segments.append(((dome_cx - 50, dome_cy - dome_ry + 80), (dome_cx - 120, dome_cy - dome_ry + 150)))
    segments.append(((dome_cx + 30, dome_cy - dome_ry + 130), (dome_cx + 100, dome_cy - dome_ry + 120)))
    segments.append(((dome_cx + 30, dome_cy - dome_ry + 130), (dome_cx + 60, dome_cy - dome_ry + 200)))
    segments.append(((dome_cx - 120, dome_cy - dome_ry + 150), (dome_cx - 180, dome_cy - dome_ry + 190)))
    segments.append(((dome_cx - 120, dome_cy - dome_ry + 150), (dome_cx - 80, dome_cy - dome_ry + 220)))
    for s, e in segments:
        draw.line((s[0], s[1], e[0], e[1]), fill=crack_color, width=3)

    # Bubble particles rising
    for _ in range(80):
        bx = random.randint(200, 1400)
        by = random.randint(300, 1800)
        br = random.randint(2, 8)
        ba = random.randint(20, 70)
        draw.ellipse(
            (bx - br, by - br, bx + br, by + br),
            fill=(180, 220, 255, ba), outline=(200, 235, 255, ba + 20),
        )

    # Seabed silhouette
    seabed_y = 1700
    for x in range(0, W, 4):
        h = 20 + 10 * math.sin(x / 80) + 5 * math.sin(x / 30) + random.randint(-5, 5)
        draw.rectangle((x, seabed_y + h, x + 4, H), fill=(15, 40, 50, 255))

    # Title panel at bottom
    draw.line((220, H - 160, W - 220, H - 160), fill=(100, 200, 230, 100), width=2)

    # Subtitle text
    tf = font("georgiab.ttf", 105)
    af = font("arialbd.ttf", 40)
    sf = font("arial.ttf", 28)

    y = centered(draw, 1990, ["A CLIMATE FICTION NOVEL"], sf, (120, 200, 230), 6)
    y += 30
    wrapped_title = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y, wrapped_title, tf, (180, 220, 240), 10)
    y += 50
    centered(draw, y, [author], af, (150, 200, 220), 6)

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