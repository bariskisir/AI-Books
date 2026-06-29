#!/usr/bin/env python3
"""
Cover art for The Color of Eight Thoughts.

Scene: the blue-green dark of a Mediterranean reef. A single shaft of gold
light falls from the surface through the water. An octopus rests among the
amphorae of an old wreck, her skin a shifting map of warm color — reds, ochres,
golds — against the cold blue; one large horizontal-pupilled eye catches the
light. Near her arms a small gold ring and the green-dark gleam of a brass
instrument. Deep teal and indigo water, one warm gold light-fall.
"""

from __future__ import annotations

import argparse
import json
import math
import random
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


WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765


def draw_water(draw: ImageDraw.ImageDraw) -> None:
    """Deep water: teal up high fading to near-black indigo at the sea floor."""
    for y in range(ART_HEIGHT):
        t = y / ART_HEIGHT
        r = int(18 + (10 - 18) * t)
        g = int(78 + (28 - 78) * t)
        b = int(96 + (54 - 96) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_lightfall(image: Image.Image) -> None:
    """A shaft of gold light angling down from the surface."""
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    top_x = 700
    for i in range(220, 0, -2):
        a = int(46 * (1 - i / 220))
        gd.polygon([(top_x - i // 3, 0), (top_x + i // 3, 0),
                    (top_x + 260 + i, ART_HEIGHT), (top_x + 60 - i, ART_HEIGHT)],
                   fill=(255, 232, 168, a))
    glow = glow.filter(ImageFilter.GaussianBlur(20))
    image.paste(Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB"), (0, 0))


def draw_amphorae(draw: ImageDraw.ImageDraw) -> None:
    """A scatter of old clay jars on the sea floor behind the octopus."""
    floor = 1300
    jars = [(180, 1380, 0.9, 18), (360, 1500, 1.15, -12), (1230, 1410, 1.0, 14),
            (1420, 1520, 1.25, 8), (1040, 1360, 0.8, -20)]
    for (jx, jy, s, rot) in jars:
        w = int(120 * s)
        h = int(300 * s)
        col = (58, 70, 64)
        # body (belly) + neck as stacked ellipses/rounded rect
        draw.ellipse([(jx - w // 2, jy - h // 2), (jx + w // 2, jy + h // 4)], fill=col)
        draw.rectangle([(jx - w // 6, jy - h // 2 - h // 6), (jx + w // 6, jy - h // 4)], fill=col)
        draw.ellipse([(jx - w // 5, jy - h // 2 - h // 5), (jx + w // 5, jy - h // 3)], fill=(50, 62, 58))
        # handles
        draw.arc([(jx - w // 2 - 14, jy - h // 2 - 6), (jx - w // 6, jy - h // 6)], 250, 30, fill=col, width=8)
        draw.arc([(jx + w // 6, jy - h // 2 - 6), (jx + w // 2 + 14, jy - h // 6)], 150, 290, fill=col, width=8)


def draw_relics(image: Image.Image) -> None:
    """The brass instrument's gleam and the small gold ring near the den."""
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    # brass instrument — an arc catching green-gold light, lower left
    bx, by = 470, 1560
    gd.arc([(bx - 150, by - 150), (bx + 150, by + 150)], 200, 340, fill=(176, 196, 120, 230), width=16)
    gd.line([(bx - 120, by + 70), (bx + 120, by + 40)], fill=(150, 170, 96, 200), width=10)
    for r in range(60, 0, -3):
        a = int(90 * (1 - r / 60))
        gd.ellipse([(bx + 90 - r, by - 40 - r), (bx + 90 + r, by - 40 + r)], fill=(220, 236, 150, max(0, a // 4)))
    # gold ring — small bright circle near the arms, lower right
    rx, ry = 1080, 1600
    for r in range(34, 0, -2):
        a = int(120 * (1 - r / 34))
        gd.ellipse([(rx - r, ry - r), (rx + r, ry + r)], fill=(255, 226, 140, max(0, a // 4)))
    gd.ellipse([(rx - 30, ry - 30), (rx + 30, ry + 30)], outline=(255, 232, 150, 255), width=10)
    glow = glow.filter(ImageFilter.GaussianBlur(2))
    image.paste(Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB"), (0, 0))


def draw_octopus(image: Image.Image) -> None:
    """The octopus: mantle, eight curling arms, mottled warm skin, one bright eye."""
    base = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    d = ImageDraw.Draw(base)
    cx, cy = 800, 880
    skin = (150, 96, 78)

    # eight arms — curling tapering tentacles radiating down and out
    rng = random.Random(11)
    arm_angles = [200, 230, 255, 280, 305, 330, 150, 120]
    for a in arm_angles:
        ang = math.radians(a)
        x, y = cx + math.cos(ang) * 120, cy + math.sin(ang) * 120
        width = 46
        seg = 16
        curl = rng.uniform(-0.16, 0.16)
        da = 0.0
        for i in range(seg):
            ang2 = ang + da
            nx = x + math.cos(ang2) * 46
            ny = y + math.sin(ang2) * 46
            w2 = max(4, int(width * (1 - i / seg)))
            d.line([(x, y), (nx, ny)], fill=skin, width=w2)
            d.ellipse([(nx - w2 // 2, ny - w2 // 2), (nx + w2 // 2, ny + w2 // 2)], fill=skin)
            x, y = nx, ny
            da += curl + rng.uniform(-0.05, 0.05)

    # mantle / head
    d.ellipse([(cx - 150, cy - 230), (cx + 150, cy + 90)], fill=skin)
    d.ellipse([(cx - 168, cy - 70), (cx + 168, cy + 150)], fill=skin)

    # mottled warm color map over the body
    mottle = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    md = ImageDraw.Draw(mottle)
    palette = [(196, 120, 70, 90), (210, 150, 60, 80), (150, 60, 50, 90),
               (120, 70, 100, 70), (220, 170, 90, 70)]
    rng2 = random.Random(5)
    for _ in range(260):
        mx = cx + rng2.randint(-160, 160)
        my = cy + rng2.randint(-230, 150)
        rr = rng2.randint(10, 34)
        md.ellipse([(mx - rr, my - rr), (mx + rr, my + rr)], fill=rng2.choice(palette))
    mottle = mottle.filter(ImageFilter.GaussianBlur(7))
    # clip mottle to the octopus silhouette by pasting using base alpha as mask
    body_mask = base.split()[3]
    base.alpha_composite(Image.composite(mottle, Image.new("RGBA", mottle.size, (0, 0, 0, 0)), body_mask))

    # the eye — large, horizontal pupil, catching the gold light
    ex, ey = cx + 64, cy - 120
    d2 = ImageDraw.Draw(base)
    d2.ellipse([(ex - 60, ey - 44), (ex + 60, ey + 44)], fill=(230, 214, 150, 255))
    d2.ellipse([(ex - 60, ey - 44), (ex + 60, ey + 44)], outline=(120, 80, 60, 255), width=4)
    d2.rectangle([(ex - 44, ey - 9), (ex + 44, ey + 9)], fill=(16, 18, 16, 255))  # horizontal pupil
    d2.ellipse([(ex + 20, ey - 14), (ex + 34, ey)], fill=(255, 250, 230, 230))  # glint

    image.paste(Image.alpha_composite(image.convert("RGBA"), base).convert("RGB"), (0, 0))


def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Color of Eight Thoughts")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (14, 54, 70))
    draw = ImageDraw.Draw(image)

    draw_water(draw)
    draw_lightfall(image)
    draw_amphorae(ImageDraw.Draw(image))
    draw_relics(image)
    draw_octopus(image)

    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)

if __name__ == "__main__":
    main()
