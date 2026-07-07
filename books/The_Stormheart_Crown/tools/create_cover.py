#!/usr/bin/env python3
"""Cover: Storm-wreathed island, lightning striking cliffside city, dark silver-veined circlet floating above obsidian, storm gray/lightning white/silver."""

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
    title = metadata.get("title", "The Stormheart Crown")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Storm sky gradient: black to dark slate to pale storm green
    for y in range(H):
        t = y / H
        if t < 0.3:
            c = lerp_color((5, 5, 10), (20, 18, 30), t / 0.3)
        elif t < 0.6:
            c = lerp_color((20, 18, 30), (50, 45, 60), (t - 0.3) / 0.3)
        else:
            c = lerp_color((50, 45, 60), (30, 35, 40), (t - 0.6) / 0.4)
        draw.line([(0, y), (W, y)], fill=c)

    # Storm clouds
    cloud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_layer)
    for _ in range(25):
        cx = random.randint(0, W)
        cy = random.randint(0, 600)
        rx = random.randint(100, 300)
        ry = random.randint(30, 80)
        a = random.randint(60, 130)
        cd.ellipse([cx - rx, cy - ry, cx + rx, cy + ry], fill=(30, 28, 40, a))
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, cloud_layer)

    # Obsidian island (dark jagged rock)
    island_pts = []
    for x in range(-50, W + 50, 10):
        y = 1200 + int(30 * math.sin(x * 0.008) + 20 * math.sin(x * 0.015) + 15 * math.sin(x * 0.025))
        island_pts.append((x, y))
    island_pts.append((W + 50, H))
    island_pts.append((-50, H))
    draw.polygon(island_pts, fill=(12, 10, 15))
    # Cliff detail
    for x in range(0, W, 4):
        cliff_y = 1200 + int(25 * math.sin(x * 0.01) + 15 * math.sin(x * 0.02))
        shade = 15 + int(8 * math.sin(x * 0.03))
        draw.line([(x, cliff_y), (x, H)], fill=(shade, shade - 2, shade + 3), width=2)

    # Cliffside city — towers silhouetted on the island
    buildings = [
        (300, 1100, 40, 300), (360, 1080, 50, 350), (440, 1120, 35, 280),
        (520, 1060, 45, 380), (600, 1100, 55, 320), (680, 1050, 60, 400),
        (760, 1110, 40, 300), (840, 1070, 50, 360), (920, 1090, 35, 340),
        (1000, 1080, 45, 370), (1080, 1120, 40, 290), (1160, 1100, 50, 330),
        (1240, 1080, 35, 350),
    ]
    for bx, by, bw, bh in buildings:
        draw.rectangle([bx, by, bx + bw, by + bh], fill=(18, 15, 22))
        draw.rectangle([bx, by, bx + bw, by + bh], outline=(25, 22, 30), width=1)
        # Lit windows
        for wy in range(by + 10, by + bh - 10, 18):
            for wx in range(bx + 5, bx + bw - 5, 14):
                if random.random() > 0.5:
                    draw.rectangle([wx, wy, wx + 6, wy + 8], fill=(200, 180, 100, 150))

    # Lightning strikes
    for _ in range(5):
        lx = random.randint(100, W - 100)
        ly = random.randint(50, 400)
        bolt_pts = [(lx, ly)]
        cx, cy = lx, ly
        for _ in range(random.randint(5, 10)):
            cx += random.randint(-40, 40)
            cy += random.randint(50, 100)
            bolt_pts.append((cx, cy))
            if cy > 1100:
                break
        for i in range(len(bolt_pts) - 1):
            draw.line([bolt_pts[i], bolt_pts[i + 1]], fill=(220, 220, 255, 180), width=4)
            draw.line([bolt_pts[i], bolt_pts[i + 1]], fill=(255, 255, 255, 60), width=10)

    # Silver-veined circlet floating above obsidian
    crown_cx, crown_cy = W // 2, 880
    # Crown glow
    for r in range(130, 0, -8):
        a = max(3, 50 - (130 - r) // 4)
        draw.ellipse([crown_cx - r, crown_cy - r, crown_cx + r, crown_cy + r],
                     fill=(150, 160, 180, a))
    # Crown band (two elliptical rings)
    for i in range(2):
        offset = i * 8
        draw.ellipse(
            [crown_cx - 100 - offset, crown_cy - 30 - offset,
             crown_cx + 100 + offset, crown_cy + 30 + offset],
            outline=(180, 190, 210, 200 - i * 40), width=5 + i,
        )
    # Crown points / spires
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        px = crown_cx + int(110 * math.cos(rad))
        py = crown_cy + int(35 * math.sin(rad))
        # Upward spike
        sp_x = crown_cx + int(130 * math.cos(rad))
        sp_y = crown_cy + int(50 * math.sin(rad)) - 30
        draw.line([(px, py), (sp_x, sp_y)], fill=(190, 200, 220, 180), width=5)
        # Small gem at tip
        draw.ellipse([sp_x - 5, sp_y - 5, sp_x + 5, sp_y + 5], fill=(200, 210, 230, 200))
    # Silver veins (thin bright lines across the band)
    for _ in range(12):
        a = random.uniform(0, 2 * math.pi)
        r1 = random.randint(60, 100)
        r2 = random.randint(60, 100)
        x1 = crown_cx + int(r1 * math.cos(a))
        y1 = crown_cy + int(r1 * math.sin(a) * 0.3)
        x2 = crown_cx + int(r2 * math.cos(a + 0.3))
        y2 = crown_cy + int(r2 * math.sin(a + 0.3) * 0.3)
        draw.line([(x1, y1), (x2, y2)], fill=(220, 230, 255, 120), width=2)

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
