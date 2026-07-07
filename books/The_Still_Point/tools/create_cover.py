#!/usr/bin/env python3
"""Cover: White lighthouse on remote Scottish island against gray storm sea, isolated and stark, lighthouse white/storm gray/sea slate."""

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

    # Storm sky gradient: dark slate to deep navy to pale gray horizon
    for y in range(H):
        t = y / H
        if t < 0.7:
            r = int(15 + 30 * (t / 0.7))
            g = int(15 + 40 * (t / 0.7))
            b = int(40 + 60 * (t / 0.7))
        else:
            r = int(45 + 80 * ((t - 0.7) / 0.3))
            g = int(55 + 90 * ((t - 0.7) / 0.3))
            b = int(100 + 100 * ((t - 0.7) / 0.3))
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Storm clouds in upper portion
    cloud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_layer, "RGBA")
    cloud_colors = [(30, 35, 50, 180), (50, 55, 70, 150), (20, 25, 40, 200)]
    for i in range(18):
        cx = int(W * (i / 18) + math.sin(i * 1.7) * 80)
        cy = int(100 + math.cos(i * 2.3) * 120 + i * 15)
        rx = 120 + int(math.sin(i * 1.1) * 60)
        ry = 40 + int(math.cos(i * 0.7) * 20)
        col = cloud_colors[i % 3]
        cd.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=col)
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, cloud_layer)

    # Sea / ocean
    sea_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sea_layer, "RGBA")
    ocean_y = 1200
    for y in range(ocean_y, H):
        t = (y - ocean_y) / (H - ocean_y)
        wave = math.sin(y * 0.03) * 20 + math.sin(y * 0.07) * 10
        r = int(20 + 30 * t)
        g = int(40 + 50 * t)
        b = int(70 + 40 * t)
        a = 180 + int(40 * t)
        sd.line((0, y, W, y), fill=(r, g, b, min(a, 255)))
    # Wave crests (whitecaps)
    for i in range(30):
        wx = int(W * (i / 30) + math.sin(i * 4.1) * 80)
        wy = int(ocean_y + 100 + math.sin(i * 2.3) * 60 + i * 8)
        wr = 3 + int(math.sin(i * 1.7) * 4)
        sd.ellipse((wx - wr, wy - wr, wx + wr, wy + wr), fill=(200, 210, 220, 120))
    img = Image.alpha_composite(img, sea_layer)

    # Spray / mist at cliff line
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist, "RGBA")
    for i in range(80):
        mx = int(W * (i / 80) + math.sin(i * 3.7) * 50)
        my = int(1150 + math.sin(i * 5.1) * 80)
        mr = 8 + int(math.sin(i * 2.9) * 6)
        md.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=(200, 210, 230, int(30 + 30 * math.sin(i * 1.3))))
    mist = mist.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, mist)

    # Cliff face
    cliff = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd2 = ImageDraw.Draw(cliff, "RGBA")
    points = []
    for x in range(0, W, 4):
        cliff_top = 1180 + math.sin(x * 0.002) * 60 + math.sin(x * 0.005) * 30
        cliff_base = H
        col = int(40 + 20 * math.sin(x * 0.003))
        cd2.line((x, cliff_top, x, cliff_base), fill=(col, col - 10, col - 15, 220))
    img = Image.alpha_composite(img, cliff)

    # Lighthouse tower
    lx, ly = W // 2, 0
    tower_base_y = 1180
    tower_w = 60
    tower_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tower_layer, "RGBA")
    # Main tower body (tapered)
    for y in range(200, tower_base_y):
        t = (y - 200) / (tower_base_y - 200)
        tw = int(tower_w * (1 - t * 0.35))
        x1 = lx - tw // 2
        x2 = lx + tw // 2
        # White tower with shadow
        shade = 220 - int(t * 40)
        td.line((x1, y, x2, y), fill=(shade, shade, shade, 240))
    # Red bands
    for band_y in range(350, tower_base_y, 120):
        for y in range(band_y, min(band_y + 25, tower_base_y)):
            t = (y - 200) / (tower_base_y - 200)
            tw = int(tower_w * (1 - t * 0.35))
            x1 = lx - tw // 2
            x2 = lx + tw // 2
            td.line((x1, y, x2, y), fill=(180, 40, 40, 230))
    # Lantern room
    lantern_y = 170
    lh = 30
    td.rectangle((lx - 35, lantern_y, lx + 35, lantern_y + lh), fill=(50, 50, 55, 240))
    # Glass panels
    td.rectangle((lx - 30, lantern_y + 2, lx + 30, lantern_y + lh - 2), fill=(200, 210, 230, 100))
    # Light beam
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam, "RGBA")
    beam_angle = 0.4
    for i in range(60):
        distance = i * 15
        bx = lx + math.cos(beam_angle) * distance
        by = lantern_y + lh // 2 + math.sin(beam_angle) * distance * 0.3
        br = max(2, 30 - i // 2)
        alpha = max(10, 80 - i)
        bd.ellipse((bx - br, by - br, bx + br, by + br), fill=(255, 230, 150, alpha))
    beam = beam.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, beam)
    img = Image.alpha_composite(img, tower_layer)

    # Title panel at bottom
    panel_y = 1920
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(overlay, "RGBA")
    for y in range(panel_y, H):
        t = (y - panel_y) / (H - panel_y)
        a = int(200 + 55 * t)
        pd.line((0, y, W, y), fill=(8, 6, 12, min(a, 255)))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img, "RGBA")

    # Decorative lines
    draw.line((220, 1970, W - 220, 1970), fill=(180, 190, 210, 150), width=2)
    draw.line((220, H - 100, W - 220, H - 100), fill=(180, 190, 210, 100), width=1)

    # Title text
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 38)
    sf = font("arial.ttf", 22)

    # Subtitle line (genre)
    centered(draw, 1990, ["LITERARY FICTION"], sf, (150, 160, 200, 180), 4)

    # Title - wrap long title
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, 2060, title_lines, tf, (220, 225, 240, 255), 8)

    y += 30
    centered(draw, y, ["BY"], sf, (150, 155, 170, 160), 4)
    y += 24
    centered(draw, y, [author], af, (200, 205, 220, 230), 4)

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