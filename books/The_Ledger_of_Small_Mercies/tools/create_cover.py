#!/usr/bin/env python3
"""Cover: The Ledger of Small Mercies — Balat row houses over an open ledger, tea-glass glow."""

from __future__ import annotations
import argparse, json, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

rng = random.Random()
rng.seed(1702026)

SKY = (88, 52, 48)
DUSK = (150, 96, 66)
PAPER = (232, 220, 196)
INK = (54, 40, 30)
TEA = (200, 110, 50)
HOUSE_COLS = [(158, 104, 76), (132, 88, 96), (176, 132, 84), (120, 110, 88), (148, 118, 100)]


def _background() -> Image.Image:
    img = Image.new("RGBA", (W, H), SKY + (255,))
    draw = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        lt = min(1.0, t / 0.55)
        r = int(SKY[0] + (DUSK[0] - SKY[0]) * lt)
        g = int(SKY[1] + (DUSK[1] - SKY[1]) * lt)
        b = int(SKY[2] + (DUSK[2] - SKY[2]) * lt)
        draw.line((0, y, W, y), fill=(r, g, b, 255))
    # gulls
    for _ in range(14):
        x = rng.randint(80, W - 80)
        y = rng.randint(80, int(H * 0.30))
        s = rng.randint(10, 22)
        draw.arc((x - s, y - 8, x, y + 8), 200, 340, fill=(30, 22, 22, 150), width=3)
        draw.arc((x, y - 8, x + s, y + 8), 200, 340, fill=(30, 22, 22, 150), width=3)
    return img


def _houses(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    base_y = int(H * 0.60)
    x = -20
    i = 0
    while x < W + 20:
        w = rng.randint(150, 230)
        h = rng.randint(220, 420)
        col = HOUSE_COLS[i % len(HOUSE_COLS)]
        d.rectangle((x, base_y - h, x + w, base_y), fill=(*col, 245))
        # roof
        d.polygon([(x - 8, base_y - h), (x + w // 2, base_y - h - 60), (x + w + 8, base_y - h)],
                  fill=(74, 50, 40, 245))
        # windows (some lit)
        for wy in range(base_y - h + 40, base_y - 30, 80):
            for wx in (x + 30, x + w - 62):
                lit = rng.random() < 0.45
                fill = (245, 200, 120, 230) if lit else (40, 32, 30, 230)
                d.rectangle((wx, wy, wx + 32, wy + 48), fill=fill)
                d.rectangle((wx, wy, wx + 32, wy + 48), outline=(40, 30, 26, 230), width=3)
        x += w + rng.randint(4, 14)
        i += 1
    # street shadow
    d.rectangle((0, base_y, W, base_y + 60), fill=(40, 28, 26, 255))
    return Image.alpha_composite(base, layer)


def _ledger(base: Image.Image) -> Image.Image:
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    # open book across lower middle
    cx, cy = W // 2, int(H * 0.47)
    bw, bh = 560, 190
    d.polygon([(cx - bw, cy - bh), (cx, cy - bh + 40), (cx, cy + bh), (cx - bw, cy + bh - 30)],
              fill=(*PAPER, 235))
    d.polygon([(cx + bw, cy - bh), (cx, cy - bh + 40), (cx, cy + bh), (cx + bw, cy + bh - 30)],
              fill=(214, 200, 176, 235))
    # ruled lines + two columns: OWED / FORGIVEN
    for side in (-1, 1):
        for r in range(7):
            y = cy - bh + 70 + r * 34
            x0 = cx + 40 * side if side > 0 else cx - bw + 60
            x1 = cx + bw - 60 if side > 0 else cx - 40
            d.line((x0, y, x1, y), fill=(*INK, 120), width=2)
        # one mercy tick in green on right page
        if side > 0:
            y = cy - bh + 70 + 3 * 34
            d.line((cx + 120, y + 2, cx + 150, y + 22), fill=(60, 130, 80, 220), width=6)
            d.line((cx + 150, y + 22, cx + 210, y - 26), fill=(60, 130, 80, 220), width=6)
    # tea glass glow
    tx, ty = cx + bw + 170, cy + 60
    d.ellipse((tx - 120, ty - 120, tx + 120, ty + 120), fill=(*TEA, 40))
    d.polygon([(tx - 34, ty - 70), (tx + 34, ty - 70), (tx + 22, ty + 60), (tx - 22, ty + 60)],
              fill=(*TEA, 210))
    d.polygon([(tx - 34, ty - 70), (tx + 34, ty - 70), (tx + 26, ty - 20), (tx - 26, ty - 20)],
              fill=(240, 190, 130, 210))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(base, layer)


def make_cover(mp: Path, op: Path) -> None:
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m["title"]
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")
    img = _background()
    img = _houses(img)
    img = _ledger(img)
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
