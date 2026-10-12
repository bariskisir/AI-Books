#!/usr/bin/env python3
"""Cover: The Orchard of Grafted Light — glowing glass apples on night branches, fair lanterns."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

rng = random.Random()
rng.seed(1602026)

NIGHT = (14, 12, 38)
PLUM = (58, 30, 78)
GOLD = (240, 200, 110)
LEAF = (90, 160, 120)
APPLE = (170, 230, 150)
MAGENTA = (200, 90, 140)


def _background() -> Image.Image:
    img = Image.new("RGBA", (W, H), NIGHT + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        lt = min(1.0, t / 0.6)
        r = int(NIGHT[0] + (PLUM[0] - NIGHT[0]) * lt)
        g = int(NIGHT[1] + (PLUM[1] - NIGHT[1]) * lt)
        b = int(NIGHT[2] + (PLUM[2] - NIGHT[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # stars
    for _ in range(160):
        x = rng.randint(0, W)
        y = rng.randint(0, int(H * 0.5))
        b = rng.randint(150, 255)
        draw.point((x, y), fill=(b, b, 255, rng.randint(80, 220)))
    return img


def _branches(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # great boughs sweeping from edges
    for (x0, y0, x1, y1, x2, y2, w) in [
        (-40, int(H * 0.30), 500, int(H * 0.36), 900, int(H * 0.22), 26),
        (W + 40, int(H * 0.42), 1100, int(H * 0.40), 700, int(H * 0.52), 30),
        (-40, int(H * 0.55), 450, int(H * 0.58), 1000, int(H * 0.50), 20),
        (W + 40, int(H * 0.16), 1200, int(H * 0.22), 800, int(H * 0.10), 18),
    ]:
        steps = 40
        prev = (x0, y0)
        for i in range(1, steps + 1):
            t = i / steps
            x = int((1 - t) ** 2 * x0 + 2 * (1 - t) * t * x1 + t ** 2 * x2)
            y = int((1 - t) ** 2 * y0 + 2 * (1 - t) * t * y1 + t ** 2 * y2)
            d.line((prev, (x, y)), fill=(24, 16, 30, 230), width=max(2, int(w * (1 - t * 0.6))))
            prev = (x, y)
    # twigs
    for _ in range(40):
        x = rng.randint(60, W - 60)
        y = rng.randint(int(H * 0.08), int(H * 0.6))
        d.line((x, y, x + rng.randint(-70, 70), y + rng.randint(-50, 50)),
               fill=(24, 16, 30, 200), width=4)
    return Image.alpha_composite(base, layer)


def _apples(base: Image.Image) -> Image.Image:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    for _ in range(34):
        x = rng.randint(90, W - 90)
        y = rng.randint(int(H * 0.08), int(H * 0.60))
        r = rng.randint(22, 52)
        col = rng.choice([APPLE, GOLD, LEAF, MAGENTA])
        gd.ellipse((x - r * 2, y - r * 2, x + r * 2, y + r * 2),
                   fill=(*col, 26))
        cd.ellipse((x - r, y - r, x + r, y + r), fill=(*col, 215))
        # glass shine
        cd.ellipse((x - r, y - r, x - r // 4, y - r // 4), fill=(255, 255, 255, 130))
        # stem
        cd.line((x, y - r, x + 6, y - r - 16), fill=(60, 40, 26, 230), width=5)
        # inner memory swirl
        cd.arc((x - r // 2, y - r // 2, x + r // 2, y + r // 2),
               rng.randint(0, 180), rng.randint(180, 360), fill=(255, 255, 255, 90), width=3)
    glow = glow.filter(ImageFilter.GaussianBlur(18))
    img = Image.alpha_composite(base, glow)
    return Image.alpha_composite(img, core)


def _lanterns(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # fair wagon lanterns along bottom third
    for x in range(120, W - 60, 150):
        y = int(H * 0.66) + rng.randint(-24, 24)
        d.line((x, y - 60, x, y - 10), fill=(20, 14, 24, 200), width=4)
        d.ellipse((x - 16, y - 34, x + 16, y + 6), fill=(*GOLD, 200))
        d.ellipse((x - 30, y - 48, x + 30, y + 20), fill=(*GOLD, 30))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(base, layer)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = _background()
    img = _branches(img)
    img = _apples(img)
    img = _lanterns(img)
    draw = ImageDraw.Draw(img, "RGBA")
    for vy in range(H):
        vt = 1 - abs(vy - H // 2) / (H // 2)
        vv = int(45 * max(0, 1 - vt))
        if vv > 0:
            draw.line((0, vy, vv, vy), fill=(0, 0, 0, 55))
            draw.line((W - vv, vy, W, vy), fill=(0, 0, 0, 55))
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)


def main() -> None:
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
