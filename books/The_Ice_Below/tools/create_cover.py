#!/usr/bin/env python3
"""Cover: The Ice Below — Antarctic research station in winter darkness with aurora."""

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
    candidates = [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    """Wrap text to fit within mw pixels."""
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
    """Draw each line centered horizontally, return final y."""
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        x = (W - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")
    model = m.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Gradient background: deep midnight blue to dark teal ----
    for y in range(H):
        t = y / H
        if t < 0.6:
            r = int(5 + 10 * t)
            g = int(10 + 20 * t)
            b = int(40 + 80 * t)
        else:
            r = int(11 - 5 * (t - 0.6) / 0.4)
            g = int(22 - 10 * (t - 0.6) / 0.4)
            b = int(88 - 40 * (t - 0.6) / 0.4)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # ---- Aurora borealis/australis in the upper sky ----
    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ad = ImageDraw.Draw(aurora)

    # Multiple aurora bands with gradients
    aurora_colors = [
        (0, 180, 100, 40),   # green
        (0, 200, 120, 30),
        (30, 220, 140, 25),
        (0, 160, 200, 35),   # cyan
        (50, 100, 220, 30),  # blue
        (0, 180, 80, 20),
    ]

    for i, (ar, ag, ab, aa) in enumerate(aurora_colors):
        base_y = 100 + i * 90
        for j in range(15):
            x_start = int(-200 + i * 80 + random.gauss(0, 60))
            x_end = int(W + 200 - i * 60 + random.gauss(0, 60))
            y_center = base_y + int(random.gauss(0, 40))
            width = int(80 + random.gauss(0, 30))
            alpha = aa - j * 2
            if alpha <= 0:
                continue
            points = []
            segments = 60
            for s in range(segments + 1):
                frac = s / segments
                x = x_start + (x_end - x_start) * frac
                wobble = math.sin(frac * math.pi * 3 + i) * 40 + math.sin(frac * math.pi * 7 + i * 2) * 15
                y = y_center + wobble
                points.append((x, y))
            ad.line(points, fill=(ar, ag, ab, alpha), width=width)

    aurora = aurora.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, aurora)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Stars ----
    for _ in range(200):
        sx = int(random.random() * W)
        sy = int(random.random() * 1200)
        sr = 1 + int(2 * random.random())
        sb = int(180 + 75 * random.random())
        draw.ellipse((sx - sr, sy - sr, sx + sr, sy + sr), fill=(sb, sb, sb, int(100 + 155 * random.random())))

    # ---- Ice shelf / horizon line ----
    horizon_y = 1100
    for x in range(0, W, 2):
        offset = int(math.sin(x * 0.02) * 15 + math.sin(x * 0.07) * 5)
        h = int(60 + math.sin(x * 0.01) * 30 + offset)
        draw.rectangle(
            (x, horizon_y - h, x + 3, horizon_y),
            fill=(200, 220, 240, int(40 + 30 * abs(math.sin(x * 0.015)))),
        )

    # ---- Research station silhouette ----
    # Main building block
    station_x = W // 2 - 120
    station_y = horizon_y - 60
    draw.rectangle(
        (station_x, station_y, station_x + 240, station_y + 50),
        fill=(15, 18, 25, 200),
    )
    # Wing
    draw.rectangle(
        (station_x + 240, station_y + 10, station_x + 300, station_y + 50),
        fill=(15, 18, 25, 200),
    )
    # Tower
    draw.rectangle(
        (station_x + 100, station_y - 60, station_x + 140, station_y),
        fill=(12, 14, 20, 200),
    )
    # Tower top light
    draw.ellipse(
        (station_x + 110, station_y - 65, station_x + 130, station_y - 50),
        fill=(255, 50, 50, 150),
    )
    # Windows (lit)
    for wx in range(station_x + 20, station_x + 220, 35):
        for wy in range(station_y + 8, station_y + 45, 20):
            draw.rectangle((wx, wy, wx + 15, wy + 10), fill=(255, 200, 100, 80))
    # Antenna dishes
    draw.line(
        (station_x + 120, station_y - 60, station_x + 120, station_y - 100),
        fill=(20, 25, 35, 200),
        width=3,
    )
    draw.ellipse(
        (station_x + 105, station_y - 115, station_x + 135, station_y - 90),
        fill=None, outline=(20, 25, 35, 200), width=3,
    )

    # ---- Ice cracks / fissures in foreground ----
    for i in range(20):
        fx = int(100 + random.random() * (W - 200))
        fy = int(horizon_y + 50 + random.random() * 400)
        crack_len = int(50 + random.random() * 200)
        end_x = fx + int((random.random() - 0.5) * crack_len)
        end_y = fy + int(crack_len * 0.3)
        draw.line(
            (fx, fy, end_x, end_y),
            fill=(100, 130, 180, int(20 + 30 * random.random())),
            width=2,
        )

    # ---- Title panel at bottom ----
    panel_top = 1920
    draw.rectangle((0, panel_top, W, H), fill=(220, 225, 230, 240))
    draw.rectangle((0, panel_top, W, H), fill=(240, 242, 245, 255))

    # Subtle ice pattern in panel background
    for i in range(30):
        px = int(random.random() * W)
        py = int(panel_top + 40 + random.random() * (H - panel_top - 80))
        draw.ellipse(
            (px - 1, py - 1, px + 1, py + 1),
            fill=(200, 210, 220, 60),
        )

    # Thin accent lines
    draw.line((200, panel_top + 15, W - 200, panel_top + 15), fill=(0, 80, 140, 180), width=2)
    draw.line((200, H - 40, W - 200, H - 40), fill=(0, 80, 140, 100), width=1)

    # Location/descriptor line on the panel
    lf = font("arial.ttf", 28)
    lfl = ["ANTARCTIC DARKNESS"]
    y = centered(draw, panel_top + 35, lfl, lf, (0, 80, 140, 200), 6)

    # Title
    tf = font("georgiab.ttf", 100)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y + 50, title_lines, tf, (10, 15, 30, 255), 10)

    # Author
    af = font("arialbd.ttf", 38)
    y = centered(draw, y + 70, [author], af, (40, 45, 50, 255), 6)

    # Series tag
    sf = font("arial.ttf", 20)
    centered(draw, H - 55, ["AN ARCTIC THRILLER"], sf, (100, 105, 110, 180), 4)

    # ---- Save ----
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