#!/usr/bin/env python3
"""Cover: The Social Engineer — A wall of hanging ID badges/lanyards, one face photo blurred into static, deep teal and brass palette, subtle fingerprint swirl."""

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


FONT_DIR = Path("C:/Windows/Fonts")
WIDTH, HEIGHT = 1600, 2560
PANEL_Y = 1920

COLORS = {
    "bg_top": (6, 26, 30),
    "bg_mid": (10, 48, 54),
    "bg_bot": (3, 12, 14),
    "teal": (28, 130, 128),
    "teal_dim": (14, 70, 72),
    "teal_light": (70, 190, 180),
    "brass": (198, 156, 84),
    "brass_dim": (120, 94, 52),
    "badge_bg": (224, 228, 226),
    "badge_shadow": (8, 22, 24),
    "lanyard": (36, 96, 96),
    "static": (200, 208, 204),
}


def make_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.5:
            t2 = t * 2
            r = int(COLORS["bg_top"][0] + (COLORS["bg_mid"][0] - COLORS["bg_top"][0]) * t2)
            g = int(COLORS["bg_top"][1] + (COLORS["bg_mid"][1] - COLORS["bg_top"][1]) * t2)
            b = int(COLORS["bg_top"][2] + (COLORS["bg_mid"][2] - COLORS["bg_top"][2]) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(COLORS["bg_mid"][0] + (COLORS["bg_bot"][0] - COLORS["bg_mid"][0]) * t2)
            g = int(COLORS["bg_mid"][1] + (COLORS["bg_bot"][1] - COLORS["bg_mid"][1]) * t2)
            b = int(COLORS["bg_mid"][2] + (COLORS["bg_bot"][2] - COLORS["bg_mid"][2]) * t2)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_fingerprint_swirl(draw: ImageDraw.ImageDraw, cx: int, cy: int, max_r: int, color) -> None:
    """Subtle fingerprint swirl: concentric arcs with gaps and slight wobble."""
    for r in range(18, max_r, 26):
        start = random.randint(0, 360)
        sweep = random.randint(180, 330)
        wobble = random.randint(-4, 4)
        bbox = [cx - r - wobble, cy - r + wobble, cx + r + wobble, cy + r - wobble]
        draw.arc(bbox, start=start, end=start + sweep, fill=color, width=2)
        if random.random() < 0.4:
            draw.arc([cx - r + 6, cy - r + 6, cx + r - 6, cy + r - 6],
                     start=(start + 40) % 360, end=(start + 90) % 360, fill=color, width=1)


def draw_lanyard(draw: ImageDraw.ImageDraw, top_x: int, badge_cx: int, badge_top: int, color) -> None:
    """V-shaped lanyard strap from the top of the image to the badge clip."""
    mid_y = badge_top - 90
    draw.line([(top_x - 70, -10), (badge_cx, mid_y)], fill=color, width=10)
    draw.line([(top_x + 70, -10), (badge_cx, mid_y)], fill=color, width=10)
    draw.rectangle([badge_cx - 14, mid_y - 6, badge_cx + 14, badge_top + 4], fill=COLORS["brass_dim"])
    draw.rectangle([badge_cx - 8, badge_top - 4, badge_cx + 8, badge_top + 8], fill=COLORS["brass"])


def draw_badge(draw: ImageDraw.ImageDraw, img: Image.Image, x: int, y: int, w: int, h: int,
               angle: float, face_static: bool, name_text: str) -> None:
    """Draw a single ID badge (optionally rotated) with a photo box and text lines."""
    badge = Image.new("RGBA", (w + 80, h + 80), (0, 0, 0, 0))
    bd = ImageDraw.Draw(badge)

    bd.rounded_rectangle([46, 46, w + 34, h + 34], radius=18, fill=COLORS["badge_shadow"])
    bd.rounded_rectangle([40, 40, w + 40, h + 40], radius=18, fill=COLORS["badge_bg"],
                         outline=COLORS["brass"], width=4)
    bd.rounded_rectangle([40, 40, w + 40, 96], radius=18, fill=COLORS["teal"])
    bd.rectangle([40, 72, w + 40, 96], fill=COLORS["teal"])
    bd.rectangle([w // 2 + 14, 56, w // 2 + 66, 80], fill=COLORS["brass"])

    ph_x, ph_y, ph_w, ph_h = 70, 120, 150, 190
    if face_static:
        face = Image.new("RGBA", (ph_w, ph_h), (30, 40, 40, 255))
        fd = ImageDraw.Draw(face)
        fd.ellipse([ph_w // 2 - 34, 30, ph_w // 2 + 34, 98], fill=(90, 100, 100, 255))
        fd.rectangle([ph_w // 2 - 44, 96, ph_w // 2 + 44, ph_h], fill=(90, 100, 100, 255))
        px = face.load()
        for py in range(ph_h):
            for pxx in range(ph_w):
                r0, g0, b0, a0 = px[pxx, py]
                n = random.randint(-90, 90)
                px[pxx, py] = (max(0, min(255, r0 + n)), max(0, min(255, g0 + n)),
                               max(0, min(255, b0 + n)), 255)
        face = face.filter(ImageFilter.GaussianBlur(3))
        for _ in range(26):
            sy = random.randint(0, ph_h - 2)
            shade = random.randint(160, 255)
            fd = ImageDraw.Draw(face)
            fd.line([(0, sy), (ph_w, sy)], fill=(shade, shade, shade, 220), width=1)
        badge.paste(face, (ph_x, ph_y))
    else:
        bd.rectangle([ph_x, ph_y, ph_x + ph_w, ph_y + ph_h], fill=(120, 140, 138))
        bd.ellipse([ph_x + ph_w // 2 - 34, ph_y + 30, ph_x + ph_w // 2 + 34, ph_y + 98],
                   fill=(70, 84, 82))
        bd.rectangle([ph_x + ph_w // 2 - 44, ph_y + 96, ph_x + ph_w // 2 + 44, ph_y + ph_h],
                     fill=(70, 84, 82))
    bd.rectangle([ph_x, ph_y, ph_x + ph_w, ph_y + ph_h], outline=COLORS["brass_dim"], width=2)

    try:
        name_font = ImageFont.truetype(str(FONT_DIR / "arialbd.ttf"), 26)
    except Exception:
        name_font = ImageFont.load_default()
    bd.text((ph_x + ph_w + 24, ph_y + 10), name_text, fill=(24, 40, 42), font=name_font)
    for i in range(4):
        ly = ph_y + 60 + i * 34
        length = random.randint(90, 170)
        bd.rounded_rectangle([ph_x + ph_w + 24, ly, ph_x + ph_w + 24 + length, ly + 14],
                             radius=6, fill=(150, 160, 158))
    bd.rectangle([70, h - 20, w + 10, h - 6], fill=(180, 188, 186))
    for bx in range(72, w + 6, 6):
        if random.random() < 0.5:
            bd.line([(bx, h - 20), (bx, h - 6)], fill=(40, 52, 54), width=2)

    if angle != 0:
        badge = badge.rotate(angle, resample=Image.BICUBIC, expand=True)
    img.paste(badge, (x, y), badge)


def draw_badge_wall(img: Image.Image, draw: ImageDraw.ImageDraw) -> None:
    """A wall of hanging ID badges; the central badge's face is static."""
    names = ["D. WHITFIELD", "A. V.", "CONTRACTOR", "VENDOR 114", "S. MARCHAND",
             "ANALYST 03", "AUDIT", "VISITOR", "TEMP"]
    positions = [
        (60, 300, -6), (430, 240, 4), (820, 300, -3), (1180, 250, 6),
        (140, 900, 3), (1010, 950, -5), (620, 620, -2),
    ]
    for i, (x, y, ang) in enumerate(positions):
        draw_lanyard(draw, x + 190, x + 190, y - 40, COLORS["lanyard"] if i % 2 else COLORS["teal_dim"])
        draw_badge(draw, img, x, y, 340, 430, ang, False, names[i % len(names)])

    cx_badge = (630, 1080)
    draw_lanyard(draw, cx_badge[0] + 190, cx_badge[0] + 190, cx_badge[1] - 40, COLORS["brass_dim"])
    draw_badge(draw, img, cx_badge[0], cx_badge[1], 340, 430, 0, True, "A. MERCER")

    glow = Image.new("RGBA", (WIDTH, PANEL_Y), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for r in range(360, 40, -30):
        gd.ellipse([cx_badge[0] + 190 - r, cx_badge[1] + 240 - r,
                    cx_badge[0] + 190 + r, cx_badge[1] + 240 + r],
                   outline=(198, 156, 84, max(4, 60 - r // 8)), width=2)
    img.paste(glow, (0, 0), glow)


def main() -> None:
    random.seed(20261008)

    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_top"])
    draw = ImageDraw.Draw(img, "RGBA")

    make_gradient(draw)

    for _ in range(40):
        y = random.randint(40, PANEL_Y - 60)
        x0 = random.randint(-100, WIDTH - 100)
        length = random.randint(80, 420)
        shade = random.choice([COLORS["teal_dim"], COLORS["teal"], (18, 90, 92)])
        draw.line([(x0, y), (x0 + length, y)], fill=shade + (random.randint(20, 60),),
                  width=random.randint(1, 2))

    draw_fingerprint_swirl(draw, WIDTH // 2, 860, 700, (70, 190, 180, 26))
    draw_fingerprint_swirl(draw, 240, 1560, 360, (198, 156, 84, 20))

    draw_badge_wall(img, draw)

    for _ in range(24):
        x = random.randint(0, WIDTH)
        y = random.randint(0, PANEL_Y)
        draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=COLORS["brass"] + (random.randint(40, 110),))

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()
