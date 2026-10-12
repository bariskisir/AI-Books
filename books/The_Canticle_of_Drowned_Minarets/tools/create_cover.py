#!/usr/bin/env python3
"""Cover: The Canticle of Drowned Minarets — drowned minarets rising from dark water, sound-wave arcs."""

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
rng.seed(1402026)

DEEP = (8, 30, 42)
MID = (16, 70, 88)
GLOW = (40, 140, 150)
GOLD = (220, 190, 110)
FOAM = (180, 220, 215)


def _background() -> Image.Image:
    img = Image.new("RGBA", (W, H), DEEP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        if t < 0.45:
            lt = t / 0.45
            r = int(DEEP[0] + (MID[0] - DEEP[0]) * lt)
            g = int(DEEP[1] + (MID[1] - DEEP[1]) * lt)
            b = int(DEEP[2] + (MID[2] - DEEP[2]) * lt)
        else:
            lt = (t - 0.45) / 0.55
            r = int(MID[0] + (8 - MID[0]) * lt)
            g = int(MID[1] + (22 - MID[1]) * lt)
            b = int(MID[2] + (30 - MID[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img


def _minarets(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    horizon = int(H * 0.52)
    specs = [(300, 1.0), (620, 1.25), (980, 0.9), (1290, 1.1)]
    for x, s in specs:
        hgt = int(520 * s)
        top = horizon - hgt
        # shaft
        d.polygon([(x - 22 * s, horizon), (x - 22 * s, top + 90 * s),
                   (x + 22 * s, top + 90 * s), (x + 22 * s, horizon)],
                  fill=(6, 18, 26, 235))
        # balconies
        for by in (top + 150 * s, top + 260 * s):
            d.rectangle((x - 44 * s, by, x + 44 * s, by + 12 * s),
                        fill=(6, 18, 26, 235))
        # upper taper + cap
        d.polygon([(x - 22 * s, top + 90 * s), (x, top), (x + 22 * s, top + 90 * s)],
                  fill=(6, 18, 26, 235))
        d.ellipse((x - 6, top - 46 * s, x + 6, top - 34 * s), fill=(10, 26, 34, 235))
        # reflection
        for i in range(1, 26):
            wob = int(10 * math.sin(i * 0.9 + x))
            alpha = max(0, 120 - i * 5)
            d.line((x - 22 * s + wob, horizon + i * 9, x + 22 * s + wob, horizon + i * 9),
                   fill=(60, 150, 155, alpha), width=2)
        # waterline foam
        d.ellipse((x - 70 * s, horizon - 8, x + 70 * s, horizon + 14),
                  fill=(180, 220, 215, 60))
    return Image.alpha_composite(base, layer)


def _sound_arcs(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, int(H * 0.52)
    for i in range(9):
        r = 120 + i * 95
        alpha = max(0, 90 - i * 9)
        d.arc((cx - r, cy - r // 3, cx + r, cy + r // 3), 195, 345,
              fill=(*GOLD, alpha), width=3)
        d.arc((cx - r - 30, cy - r // 3 - 10, cx + r + 30, cy + r // 3 + 10), 200, 340,
              fill=(*GLOW, alpha // 2), width=1)
    # rising notes
    for _ in range(26):
        x = rng.randint(80, W - 80)
        y = rng.randint(int(H * 0.15), int(H * 0.48))
        r = rng.randint(3, 9)
        d.ellipse((x - r, y - r, x + r, y + r),
                  fill=(*rng.choice([GOLD, FOAM, GLOW]), rng.randint(40, 120)))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(base, layer)


def _moon_glint(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    mx, my = 1210, 210
    d.ellipse((mx - 46, my - 46, mx + 46, my + 46), fill=(235, 240, 225, 200))
    d.ellipse((mx - 60, my - 60, mx + 60, my + 60), fill=(235, 240, 225, 20))
    for i in range(40):
        y = int(H * 0.55) + i * 12
        w = max(4, 90 - i * 2)
        d.line((mx - w + rng.randint(-8, 8), y, mx + w + rng.randint(-8, 8), y),
               fill=(220, 235, 220, 70), width=3)
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(base, layer)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = _background()
    img = _moon_glint(img)
    img = _minarets(img)
    img = _sound_arcs(img)
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
