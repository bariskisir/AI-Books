#!/usr/bin/env python3
"""Cover: Woman on trapeze against yellow-brown dust storm sky, accordion figure below, circus tent silhouettes, dust yellow/trapeze silhouette/tent red."""

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

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1, c2, t):
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tin Accordion")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Dust storm sky gradient: yellow-brown to ochre
    for y in range(H):
        t = y / H
        if t < 0.4:
            c = lerp_color((180, 140, 60), (160, 110, 50), t / 0.4)
        elif t < 0.7:
            c = lerp_color((160, 110, 50), (120, 80, 40), (t - 0.4) / 0.3)
        else:
            c = lerp_color((120, 80, 40), (60, 40, 20), (t - 0.7) / 0.3)
        draw.line([(0, y), (W, y)], fill=c)

    # Dust storm layers
    dust = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dd = ImageDraw.Draw(dust)
    for _ in range(50):
        dx = random.randint(0, W)
        dy = random.randint(0, 1200)
        dr = random.randint(30, 150)
        a = random.randint(15, 45)
        dd.ellipse([dx - dr, dy - dr, dx + dr, dy + dr],
                   fill=(180, 160, 100, a))
    dust = dust.filter(ImageFilter.GaussianBlur(12))
    img = Image.alpha_composite(img, dust)
    draw = ImageDraw.Draw(img)

    # Circus tent silhouettes (background)
    tents = [
        (200, 1100, 300, 700), (500, 1080, 250, 650),
        (750, 1120, 200, 600), (950, 1060, 350, 750),
        (1300, 1100, 280, 680),
    ]
    for tx, ty, tw, th in tents:
        # Tent peak
        draw.polygon([(tx, ty), (tx - tw // 2, ty + th), (tx + tw // 2, ty + th)],
                     fill=(60, 35, 25, 180))
        # Tent body
        draw.rectangle([tx - tw // 2, ty + int(th * 0.2), tx + tw // 2, ty + th],
                       fill=(50, 30, 20, 160))
        # Tent stripe
        draw.polygon([(tx - tw // 2, ty + th), (tx, ty), (tx + tw // 2, ty + th)],
                     outline=(80, 45, 35), width=4)
        # Flag at peak
        draw.line([(tx, ty), (tx, ty - 40)], fill=(40, 30, 20), width=3)
        draw.polygon([(tx, ty - 40), (tx + 20, ty - 35), (tx, ty - 30)],
                     fill=(120, 30, 30, 150))

    # Ground
    draw.rectangle([(0, 1200), (W, H)], fill=(40, 28, 15))
    for x in range(0, W, 6):
        gy = 1200 + int(8 * math.sin(x * 0.02) + 5 * math.sin(x * 0.05))
        draw.line([(x, gy), (x, H)], fill=(35, 24, 12), width=3)

    # Trapeze bar (horizontal)
    trapeze_y = 600
    draw.line([(200, trapeze_y), (1400, trapeze_y)], fill=(100, 90, 80), width=6)
    # Ropes
    for rx in [300, 1300]:
        draw.line([(rx, 0), (rx, trapeze_y)], fill=(80, 70, 60), width=4)

    # Woman on trapeze (silhouette)
    woman_cx = W // 2
    woman_y = trapeze_y
    # Body hanging from trapeze
    draw.line([(woman_cx, woman_y), (woman_cx, woman_y + 120)], fill=(25, 20, 18), width=8)
    # Arms holding bar
    draw.line([(woman_cx, woman_y + 10), (woman_cx - 60, woman_y)], fill=(25, 20, 18), width=6)
    draw.line([(woman_cx, woman_y + 10), (woman_cx + 60, woman_y)], fill=(25, 20, 18), width=6)
    # Legs (bent gracefully)
    draw.line([(woman_cx, woman_y + 120), (woman_cx - 40, woman_y + 170)], fill=(25, 20, 18), width=7)
    draw.line([(woman_cx, woman_y + 120), (woman_cx + 30, woman_y + 180)], fill=(25, 20, 18), width=7)
    # Head
    draw.ellipse([woman_cx - 14, woman_y + 18, woman_cx + 14, woman_y + 46], fill=(25, 20, 18))
    # Hair flowing
    for i in range(5):
        hx = woman_cx + 10 + i * 8
        hy = woman_y + 25 + i * 5
        draw.line([(woman_cx + 10, woman_y + 25), (hx, hy)], fill=(20, 15, 12), width=3)

    # Accordion figure below
    acc_cx = W // 2
    acc_y = 1150
    # Body
    draw.ellipse([acc_cx - 30, acc_y - 80, acc_cx + 30, acc_y], fill=(30, 25, 20))
    # Legs
    draw.line([(acc_cx - 10, acc_y), (acc_cx - 15, acc_y + 60)], fill=(30, 25, 20), width=8)
    draw.line([(acc_cx + 10, acc_y), (acc_cx + 15, acc_y + 60)], fill=(30, 25, 20), width=8)
    # Head (looking up)
    draw.ellipse([acc_cx - 15, acc_y - 110, acc_cx + 15, acc_y - 80], fill=(35, 28, 22))
    # Hat
    draw.rectangle([acc_cx - 22, acc_y - 130, acc_cx + 22, acc_y - 110], fill=(40, 32, 25))
    draw.rectangle([acc_cx - 30, acc_y - 120, acc_cx + 30, acc_y - 115], fill=(40, 32, 25))
    # Accordion (bellows shape)
    acc_w, acc_h = 60, 80
    draw.rectangle([acc_cx - acc_w // 2, acc_y - 60, acc_cx + acc_w // 2, acc_y - 60 + acc_h],
                   fill=(50, 40, 30))
    # Bellows lines
    for bi in range(6):
        bx = acc_cx - acc_w // 2 + bi * (acc_w // 6)
        draw.line([(bx, acc_y - 60), (bx, acc_y - 60 + acc_h)], fill=(35, 28, 22), width=2)
    # Accordion ends
    draw.rectangle([acc_cx - acc_w // 2 - 8, acc_y - 65, acc_cx - acc_w // 2, acc_y - 60 + acc_h + 5],
                   fill=(60, 48, 35))
    draw.rectangle([acc_cx + acc_w // 2, acc_y - 65, acc_cx + acc_w // 2 + 8, acc_y - 60 + acc_h + 5],
                   fill=(60, 48, 35))

    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()
