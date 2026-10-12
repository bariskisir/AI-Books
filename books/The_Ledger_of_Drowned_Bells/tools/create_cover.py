#!/usr/bin/env python3
"""Cover: The Ledger of Drowned Bells — bronze bells in fog over a coastal cliff."""

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
rng.seed(1502026)

TOP = (38, 52, 58)
MID = (96, 118, 112)
LOW = (150, 160, 148)
BRONZE = (168, 128, 72)
BRONZE_DK = (96, 70, 40)
WAX = (52, 94, 74)


def _background() -> Image.Image:
    img = Image.new("RGBA", (W, H), TOP + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        if t < 0.5:
            lt = t / 0.5
            r = int(TOP[0] + (MID[0] - TOP[0]) * lt)
            g = int(TOP[1] + (MID[1] - TOP[1]) * lt)
            b = int(TOP[2] + (MID[2] - TOP[2]) * lt)
        else:
            lt = (t - 0.5) / 0.5
            r = int(MID[0] + (LOW[0] - MID[0]) * lt)
            g = int(MID[1] + (LOW[1] - MID[1]) * lt)
            b = int(MID[2] + (LOW[2] - MID[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    return img


def _cliff_sea(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    horizon = int(H * 0.62)
    pts = [(0, horizon)]
    for x in range(0, W + 40, 40):
        pts.append((x, horizon + int(26 * math.sin(x * 0.006 + 1.0))
                    + int(10 * math.sin(x * 0.02))))
    pts += [(W, H), (0, H)]
    d.polygon(pts, fill=(24, 34, 34, 255))
    # wave flecks
    for _ in range(120):
        x = rng.randint(0, W)
        y = rng.randint(horizon + 20, int(H * 0.72))
        d.line((x, y, x + rng.randint(8, 30), y), fill=(200, 215, 205, rng.randint(30, 90)), width=2)
    # cliff head left
    d.polygon([(0, horizon - 260), (330, horizon - 300), (420, horizon + 40), (0, horizon + 60)],
              fill=(20, 28, 28, 255))
    # tiny church silhouette on cliff
    d.rectangle((150, horizon - 420, 230, horizon - 300), fill=(14, 20, 20, 255))
    d.polygon([(140, horizon - 420), (190, horizon - 480), (240, horizon - 420)], fill=(14, 20, 20, 255))
    d.rectangle((300, horizon - 380, 330, horizon - 300), fill=(14, 20, 20, 255))
    return Image.alpha_composite(base, layer)


def _bells(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    specs = [(480, 520, 150), (800, 430, 190), (1120, 540, 130)]
    for x, y, s in specs:
        # yoke beam
        d.rectangle((x - s - 30, y - s - 40, x + s + 30, y - s - 18), fill=(30, 24, 18, 220))
        # crown + body
        d.ellipse((x - 26, y - s - 30, x + 26, y - s + 10), fill=BRONZE_DK + (220,))
        d.polygon([(x - s * 0.42, y - s + 6), (x + s * 0.42, y - s + 6),
                   (x + s * 0.62, y + s * 0.5), (x - s * 0.62, y + s * 0.5)],
                  fill=BRONZE + (225,))
        # lip
        d.ellipse((x - s * 0.62, y + s * 0.38, x + s * 0.62, y + s * 0.62), fill=BRONZE_DK + (225,))
        # highlight
        d.polygon([(x - s * 0.30, y - s + 6), (x - s * 0.12, y - s + 6),
                   (x - s * 0.20, y + s * 0.45), (x - s * 0.38, y + s * 0.45)],
                  fill=(225, 190, 130, 90))
        # inscription band + clapper
        d.line((x - s * 0.55, y + s * 0.1, x + s * 0.55, y + s * 0.1),
               fill=(60, 42, 24, 160), width=4)
        d.line((x, y + s * 0.55, x, y + s * 0.72), fill=(40, 30, 20, 220), width=8)
        d.ellipse((x - 14, y + s * 0.68, x + 14, y + s * 0.96), fill=(40, 30, 20, 220))
        # sound ripple
        for i in range(3):
            rr = s + 40 + i * 46
            d.arc((x - rr, y - rr // 2, x + rr, y + rr // 2), 200, 340,
                  fill=(210, 220, 205, 60 - i * 16), width=2)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(base, layer)


def _fog(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for _ in range(16):
        y = rng.randint(0, int(H * 0.6))
        hgt = rng.randint(26, 90)
        d.ellipse((-100, y, W + 100, y + hgt), fill=(215, 225, 215, rng.randint(14, 34)))
    # wax seal accent
    sx, sy = 1290, int(H * 0.60)
    d.ellipse((sx - 34, sy - 34, sx + 34, sy + 34), fill=(*WAX, 170))
    d.ellipse((sx - 22, sy - 22, sx + 22, sy + 22), fill=(40, 74, 56, 170))
    layer = layer.filter(ImageFilter.GaussianBlur(6))
    return Image.alpha_composite(base, layer)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = _background()
    img = _cliff_sea(img)
    img = _bells(img)
    img = _fog(img)
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
