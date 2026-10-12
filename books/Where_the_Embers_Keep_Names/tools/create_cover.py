#!/usr/bin/env python3
"""Cover: Where the Embers Keep Names — snow slope, converging rails, ember dots, stove glow."""

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
rng.seed(1802026)

SKY = (10, 16, 40)
HORIZON = (52, 74, 120)
SNOW = (205, 218, 235)
EMBER = (235, 120, 40)
EMBER_HOT = (255, 200, 90)
RAIL = (30, 30, 40)


def _background() -> Image.Image:
    img = Image.new("RGBA", (W, H), SKY + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        if t < 0.42:
            lt = t / 0.42
            r = int(SKY[0] + (HORIZON[0] - SKY[0]) * lt)
            g = int(SKY[1] + (HORIZON[1] - SKY[1]) * lt)
            b = int(SKY[2] + (HORIZON[2] - SKY[2]) * lt)
        else:
            lt = min(1.0, (t - 0.42) / 0.2)
            r = int(HORIZON[0] + (SNOW[0] - HORIZON[0]) * lt)
            g = int(HORIZON[1] + (SNOW[1] - HORIZON[1]) * lt)
            b = int(HORIZON[2] + (SNOW[2] - HORIZON[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # stars + moon
    for _ in range(130):
        x = rng.randint(0, W)
        y = rng.randint(0, int(H * 0.35))
        b = rng.randint(150, 255)
        draw.point((x, y), fill=(b, b, 255, rng.randint(80, 200)))
    d = ImageDraw.Draw(img, "RGBA")
    d.ellipse((250, 120, 370, 240), fill=(230, 235, 245, 200))
    # snowfall
    for _ in range(220):
        x = rng.randint(0, W)
        y = rng.randint(0, H)
        r = rng.randint(1, 4)
        d.ellipse((x - r, y - r, x + r, y + r), fill=(235, 242, 250, rng.randint(60, 160)))
    return img


def _slope_rails(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    horizon = int(H * 0.55)
    pts = [(0, horizon)]
    for x in range(0, W + 40, 40):
        pts.append((x, horizon + int(60 * math.sin(x * 0.002 + 0.4)) + int((x / W) * 160)))
    pts += [(W, H), (0, H)]
    d.polygon(pts, fill=(*SNOW, 255))
    # slope shading
    for _ in range(60):
        x = rng.randint(0, W)
        y = rng.randint(horizon, H)
        d.ellipse((x - 30, y - 8, x + 30, y + 8), fill=(180, 196, 218, 60))
    # converging rails to vanishing point
    vx, vy = W // 2 + 120, horizon + 10
    for off in (-1, 1):
        d.line((W // 2 + off * 320, H, vx + off * 6, vy), fill=(*RAIL, 235), width=14)
    for i in range(24):
        t = i / 23
        y = int(H - t * (H - vy))
        half = int(320 * (1 - t) + 6 * t)
        d.line((W // 2 - half, y, W // 2 + half, y), fill=(70, 60, 55, 220), width=max(2, int(12 * (1 - t) + 2)))
    # station hut silhouette
    hx, hy = 320, horizon + 120
    d.rectangle((hx - 130, hy - 130, hx + 130, hy + 40), fill=(26, 24, 34, 255))
    d.polygon([(hx - 150, hy - 130), (hx, hy - 200), (hx + 150, hy - 130)], fill=(20, 18, 28, 255))
    # lit window + stove pipe smoke
    d.rectangle((hx - 40, hy - 70, hx + 40, hy + 10), fill=(*EMBER_HOT, 230))
    for i in range(6):
        d.ellipse((hx + 90 - i * 8, hy - 260 - i * 46, hx + 130 - i * 8, hy - 220 - i * 46),
                  fill=(200, 200, 210, 40))
    return Image.alpha_composite(base, layer)


def _embers(base: Image.Image) -> Image.Image:
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    core = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(core)
    # ember trail along the rails + scattered burns
    for _ in range(70):
        if rng.random() < 0.55:
            t = rng.random()
            x = int(W // 2 + (rng.randint(-320, 320)) * (1 - t))
            y = int(H - t * (H - int(H * 0.55)))
        else:
            x = rng.randint(60, W - 60)
            y = rng.randint(int(H * 0.5), int(H * 0.72))
        r = rng.randint(3, 12)
        col = rng.choice([EMBER, EMBER_HOT, (200, 60, 30)])
        gd.ellipse((x - r * 3, y - r * 3, x + r * 3, y + r * 3), fill=(*col, 30))
        cd.ellipse((x - r, y - r, x + r, y + r), fill=(*col, rng.randint(150, 230)))
    glow = glow.filter(ImageFilter.GaussianBlur(14))
    img = Image.alpha_composite(base, glow)
    return Image.alpha_composite(img, core)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = _background()
    img = _slope_rails(img)
    img = _embers(img)
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
