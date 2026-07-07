#!/usr/bin/env python3
"""Cover: The Long Truce — Dark blue-steel marble hall, glowing holographic Judge-7 orb, orbiting data rings, steel blue/hologram cyan/white."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


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


def _standard_cover_font(name, size):
    font_dir = "C:/Windows/Fonts"
    candidates = [Path(font_dir) / name, Path("C:/Windows/Fonts") / "arialbd.ttf", Path("C:/Windows/Fonts") / "arial.ttf"]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _standard_cover_repair_text(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def _standard_cover_wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=font)[2] <= max_width:
            current.append(word)
        else:
            lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _standard_cover_center(draw, y, lines, font, fill, gap, width):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        x = (width - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, font=font, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def _standard_cover_title_font(draw, title, max_width):
    for size in (116, 104, 96, 88, 80, 72):
        f = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), f, max_width)
        heights = [draw.textbbox((0, 0), l, font=f)[3] - draw.textbbox((0, 0), l, font=f)[1] for l in lines]
        total = sum(heights) + max(0, len(lines) - 1) * 18
        if len(lines) <= 4 and total <= 430:
            return f, lines, 18
    f = _standard_cover_font("arialbd.ttf", 68)
    return f, _standard_cover_wrap(draw, title.upper(), f, max_width), 16


def _standard_cover_resolve_title(local_vars):
    for k in ("title", "ti", "book_title", "TITLE"):
        v = local_vars.get(k)
        if v:
            return v
    import json, pathlib
    mp = local_vars.get("args")
    if mp and getattr(mp, "metadata", None):
        try:
            return json.loads(pathlib.Path(mp.metadata).read_text(encoding="utf-8")).get("title", "")
        except:
            pass
    for k in ("output_path", "out_path", "op", "out"):
        v = local_vars.get(k)
        if v:
            return pathlib.Path(v).stem.replace("_", " ").strip()
    return ""


def _standard_cover_resolve_author(local_vars):
    for k in ("author", "au", "AUTHOR"):
        v = local_vars.get(k)
        if v:
            return v
    import json, pathlib
    mp = local_vars.get("args")
    if mp and getattr(mp, "metadata", None):
        try:
            return json.loads(pathlib.Path(mp.metadata).read_text(encoding="utf-8")).get("author", "Barış Kısır")
        except:
            pass
    return "Barış Kısır"



def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Long Truce")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # --- Background gradient: deep marble blue to cold steel ---
    for y in range(0, HEIGHT):
        t = y / HEIGHT
        r = int(25 + t * 35)
        g = int(30 + t * 40)
        b = int(55 + t * 50)
        draw.line((0, y, WIDTH, y), fill=(r, g, b))

    # --- Marble hall floor (perspective lines) ---
    floor_start = 1300
    for y in range(floor_start, 1760):
        t = (y - floor_start) / 460
        r = int(60 - t * 15)
        g = int(65 - t * 15)
        b = int(80 - t * 15)
        draw.line((0, y, WIDTH, y), fill=(r, g, b))

    # Floor tile grid (perspective)
    tile_color = (100, 105, 120, 60)
    for tx in range(0, WIDTH, 80):
        draw.line((tx, floor_start, tx + int((WIDTH - tx) * 0.3), 1760), fill=tile_color, width=1)
    for ty in range(floor_start, 1760, 30):
        shrink = 1 - (ty - floor_start) / 460 * 0.7
        draw.line((int(WIDTH / 2 - 600 * shrink), ty, int(WIDTH / 2 + 600 * shrink), ty), fill=tile_color, width=1)

    # --- Marble pillars ---
    pillar_color = (130, 135, 150)
    pillar_highlight = (170, 175, 190)
    for px in [100, 300, 600, 800, 1000, 1200, 1400]:
        # Pillar body
        draw.rectangle((px, 200, px + 40, 1400), fill=pillar_color)
        draw.rectangle((px + 8, 200, px + 32, 1400), fill=pillar_highlight)
        # Capital (top)
        draw.rectangle((px - 10, 180, px + 50, 220), fill=(100, 105, 120))
        draw.rectangle((px - 20, 170, px + 60, 190), fill=(90, 95, 110))

    # --- Central AI arbiter (glowing holographic form) ---
    center_x = WIDTH // 2
    center_y = 550

    # Outer glow rings
    for r in range(300, 60, -15):
        alpha = max(0, 30 - (300 - r) // 10)
        draw.ellipse((center_x - r, center_y - r, center_x + r, center_y + r),
                     outline=(160, 225, 255, alpha), width=2)

    # Core sphere
    for r in range(120, 0, -5):
        intensity = int(255 - (120 - r) * 1.5)
        draw.ellipse((center_x - r, center_y - r, center_x + r, center_y + r),
                     fill=(intensity, intensity, 255, 200 - r))

    # Inner bright core
    draw.ellipse((center_x - 30, center_y - 30, center_x + 30, center_y + 30),
                 fill=(220, 230, 255, 230))

    # Orbiting data rings around the arbiter
    def draw_ring(radius, tilt, color, width=3):
        import math
        points = []
        for a in range(0, 360, 5):
            rad = math.radians(a)
            x = center_x + radius * math.cos(rad)
            y = center_y + radius * math.sin(rad) * tilt
            points.append((x, y))
        for i in range(len(points) - 1):
            draw.line((points[i], points[i + 1]), fill=color, width=width)

    draw_ring(180, 0.6, (100, 200, 255, 80), 2)
    draw_ring(210, 0.4, (150, 220, 255, 60), 1)
    draw_ring(240, 0.5, (80, 180, 255, 40), 1)

    # --- Human silhouettes (citizens before the arbiter) ---
    def draw_silhouette(cx, cy, scale=1.0, color=(15, 20, 35)):
        s = scale
        r = 10 * s
        # Head
        draw.ellipse((cx - r, cy - r * 2.5, cx + r, cy), fill=color)
        # Body
        body_top = cy
        body_bot = cy + 35 * s
        draw.polygon([(cx - 8 * s, body_top), (cx + 8 * s, body_top), (cx + 12 * s, body_bot), (cx - 12 * s, body_bot)], fill=color)
        # Arms raised in supplication
        draw.line((cx, body_top + 8 * s, cx - 14 * s, body_top - 2 * s), fill=color, width=int(3 * s))
        draw.line((cx, body_top + 8 * s, cx + 14 * s, body_top - 2 * s), fill=color, width=int(3 * s))
        # Legs
        draw.line((cx - 5 * s, body_bot, cx - 8 * s, body_bot + 14 * s), fill=color, width=int(3 * s))
        draw.line((cx + 5 * s, body_bot, cx + 8 * s, body_bot + 14 * s), fill=color, width=int(3 * s))

    # Rows of people facing the arbiter
    for row, y_base, sc in [(1, 1250, 1.0), (2, 1320, 0.9), (3, 1380, 0.8)]:
        count = 7 if row == 1 else 9 if row == 2 else 11
        spread = 500 if row == 1 else 550 if row == 2 else 600
        start_x = WIDTH // 2 - spread // 2
        for i in range(count):
            px = start_x + spread * i // (count - 1) if count > 1 else WIDTH // 2
            draw_silhouette(px, y_base, sc)

    # --- Light beams from arbiter downward ---
    beam = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bdraw = ImageDraw.Draw(beam)
    for ba in range(-2, 3):
        bx = center_x + ba * 80
        bdraw.polygon([(bx - 15, center_y + 100), (bx + 15, center_y + 100),
                        (bx + 100, 1400), (bx - 100, 1400)],
                       fill=(160, 220, 255, 12))
    img = Image.alpha_composite(img, beam)

    # --- Glowing verdict text in air ---
    verdict_font = _standard_cover_font("arial.ttf", 18)
    verdict_lines = [
        "JUDGE-7: VERDICT",
        "\"I learned that suffering",
        "is not symmetrical.\""
    ]
    vx = WIDTH // 2
    for i, line in enumerate(verdict_lines):
        bb = draw.textbbox((0, 0), line, font=verdict_font)
        draw.text((vx - (bb[2] - bb[0]) // 2, 880 + i * 28), line, font=verdict_font,
                  fill=(180, 220, 255, 100))

    # --- Float subtle 'code rain' on left and right ---
    import random
    code_chars = "01"
    for cx in [50, 1550]:
        for cy in range(300, 1200, 60):
            char = random.choice(code_chars)
            draw.text((cx + random.randint(-20, 20), cy),
                      char, font=_standard_cover_font("arial.ttf", 10),
                      fill=(100, 180, 255, 30))

    # --- Bottom title panel ---
    _draw_standard_cover_title_panel(img, title=title, author="Barış Kısır")

    img.save(output_path)
    print(f"Cover saved to {output_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
