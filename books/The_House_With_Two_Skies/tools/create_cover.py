#!/usr/bin/env python3
"""
Cover art for The House With Two Skies.

Scene: a grey stone farmhouse on a Welsh hill, seen at the seam of two worlds.
The sky is split down the middle: on the left a clear gold dawn above a living,
leafed orchard; on the right a slate dusk above bare, fallen trees. The two
skies meet over the ridge of the roof. One small upstairs window — the still
room — burns warm against the slate side, the only lit thing on the hill.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765
SPLIT = WIDTH // 2


def draw_split_sky(draw: ImageDraw.ImageDraw) -> None:
    """Left: clear gold dawn. Right: slate overcast dusk."""
    horizon = 1150
    for y in range(horizon):
        t = y / horizon
        # left dawn
        lr = int(244 + (250 - 244) * t)
        lg = int(206 + (224 - 206) * t)
        lb = int(140 + (196 - 140) * t)
        draw.line([(0, y), (SPLIT, y)], fill=(lr, lg, lb))
        # right dusk
        rr = int(96 + (150 - 96) * t)
        rg = int(104 + (158 - 104) * t)
        rb = int(116 + (170 - 116) * t)
        draw.line([(SPLIT, y), (WIDTH, y)], fill=(rr, rg, rb))


def draw_seam_line(image: Image.Image) -> None:
    """A soft luminous join where the two skies meet."""
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for i in range(60, 0, -1):
        a = int(60 * (1 - i / 60))
        gd.line([(SPLIT - i, 0), (SPLIT - i, 1150)], fill=(255, 245, 220, a))
        gd.line([(SPLIT + i, 0), (SPLIT + i, 1150)], fill=(255, 245, 220, a))
    gd.line([(SPLIT, 0), (SPLIT, 1150)], fill=(255, 250, 235, 120))
    glow = glow.filter(ImageFilter.GaussianBlur(6))
    image.paste(Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB"), (0, 0))


def draw_sun(draw: ImageDraw.ImageDraw) -> None:
    """Low dawn sun on the left side."""
    cx, cy, r = 360, 360, 110
    for rr in range(r, 0, -2):
        t = rr / r
        draw.ellipse([(cx - rr, cy - rr), (cx + rr, cy + rr)],
                     fill=(int(255), int(232 - 10 * (1 - t)), int(176 - 40 * (1 - t))))


def draw_hill(draw: ImageDraw.ImageDraw) -> None:
    """The green hill rising to the house, darker on the dusk side."""
    horizon = 1150
    for y in range(horizon, ART_HEIGHT):
        t = (y - horizon) / (ART_HEIGHT - horizon)
        # left lit green
        lg = (int(70 + 30 * t), int(104 + 30 * t), int(54 + 20 * t))
        rg = (int(48 + 22 * t), int(70 + 26 * t), int(50 + 18 * t))
        draw.line([(0, y), (SPLIT, y)], fill=lg)
        draw.line([(SPLIT, y), (WIDTH, y)], fill=rg)
    # rolling ridge line
    draw.line([(0, horizon), (WIDTH, horizon)], fill=(40, 58, 40), width=3)


def draw_orchard(draw: ImageDraw.ImageDraw) -> None:
    """Left: living leafed trees. Right: bare and a fallen one."""
    base = 1150
    # living trees (left)
    for tx in (150, 300, 470):
        draw.line([(tx, base + 120), (tx, base + 20)], fill=(60, 46, 34), width=10)
        draw.ellipse([(tx - 52, base - 70), (tx + 52, base + 40)], fill=(64, 110, 58))
        draw.ellipse([(tx - 40, base - 40), (tx + 40, base + 50)], fill=(78, 126, 66))
    # bare trees (right)
    for tx in (1120, 1290, 1450):
        draw.line([(tx, base + 120), (tx, base - 40)], fill=(54, 52, 50), width=9)
        for (ax, ay) in [(-40, -10), (40, -20), (-26, -50), (28, -46), (0, -70)]:
            draw.line([(tx, base - 10), (tx + ax, base - 10 + ay)], fill=(54, 52, 50), width=5)
    # a fallen tree on the right
    draw.line([(1180, base + 150), (1380, base + 95)], fill=(50, 46, 42), width=14)


def draw_house(image: Image.Image) -> None:
    """Grey stone farmhouse straddling the seam, one warm upstairs window."""
    draw = ImageDraw.Draw(image)
    hx, hy = WIDTH // 2, 1000
    hw, hh = 360, 300
    left = hx - hw // 2
    top = hy - hh
    # walls
    draw.rectangle([(left, top), (left + hw, hy)], fill=(120, 120, 124))
    # stone texture
    import random
    rng = random.Random(3)
    for yy in range(top + 8, hy, 22):
        for xx in range(left + 6, left + hw - 6, 40):
            draw.rectangle([(xx, yy), (xx + rng.choice([26, 30, 34]), yy + 16)],
                           outline=(98, 98, 102), width=1)
    # roof
    draw.polygon([(left - 26, top), (left + hw + 26, top), (hx, top - 150)], fill=(58, 60, 66))
    # chimney with a thread of smoke
    draw.rectangle([(left + 40, top - 92), (left + 70, top - 20)], fill=(72, 70, 72))
    # downstairs door
    draw.rectangle([(hx - 28, hy - 120), (hx + 28, hy)], fill=(46, 40, 36))
    # windows (dark) and the one warm still-room window upstairs on the dusk side
    for wx in (left + 60, hx + 70):
        draw.rectangle([(wx, hy - 110), (wx + 56, hy - 40)], fill=(40, 44, 52))
    # the lit window — upper right (dusk side)
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    wx, wy, ww, wh = hx + 56, top + 70, 64, 84
    for r in range(70, 0, -3):
        a = int(120 * (1 - r / 70))
        gd.ellipse([(wx - r, wy - r), (wx + ww + r, wy + wh + r)], fill=(255, 214, 130, max(0, a // 4)))
    gd.rectangle([(wx, wy), (wx + ww, wy + wh)], fill=(255, 226, 158, 255))
    gd.line([(wx + ww // 2, wy), (wx + ww // 2, wy + wh)], fill=(180, 150, 90, 255), width=3)
    gd.line([(wx, wy + wh // 2), (wx + ww, wy + wh // 2)], fill=(180, 150, 90, 255), width=3)
    glow = glow.filter(ImageFilter.GaussianBlur(1))
    image.paste(Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB"), (0, 0))


def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The House With Two Skies")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (160, 170, 160))
    draw = ImageDraw.Draw(image)

    draw_split_sky(draw)
    draw_sun(draw)
    draw_seam_line(image)
    draw_hill(ImageDraw.Draw(image))
    draw_orchard(ImageDraw.Draw(image))
    draw_house(image)

    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    image.save(out_path, "PNG")
    print(f"Cover saved: {out_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers
# ---------------------------------------------------------------------------

def _standard_cover_font(name, size):
    candidates = [name, "arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]
    if "bd" in name.lower() or "bold" in name.lower():
        candidates = [name, "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()

def _standard_cover_repair_text(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text

def _standard_cover_wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        trial = " ".join(current + [word])
        box = draw.textbbox((0, 0), trial, font=font)
        if current and box[2] - box[0] > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines or [text]

def _standard_cover_center(draw, y, lines, font, fill, gap, width):
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font)
        draw.text(((width - (box[2] - box[0])) // 2, y), line, font=font, fill=fill)
        y += box[3] - box[1] + gap
    return y

def _standard_cover_title_font(draw, title, max_width):
    for size in (116, 104, 96, 88, 80, 72, 66, 60):
        font = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), font, max_width)
        heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]
        if len(lines) <= 4 and sum(heights) + max(0, len(lines) - 1) * 18 <= 430:
            return font, lines, 18
    font = _standard_cover_font("arialbd.ttf", 58)
    return font, _standard_cover_wrap(draw, title.upper(), font, max_width), 14

def _standard_cover_resolve_title(local_vars):
    for key in ("title", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value
    return ""

def _standard_cover_resolve_author(local_vars):
    for key in ("author", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value
    return "Barış Kısır"

def _draw_standard_cover_title_panel(image, title="", author="", model=""):
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    py = 1765
    draw.rectangle((0, py, 1600, 2560), fill=(18, 16, 14, 255))
    draw.line((180, py + 17, 1420, py + 17), fill=(180, 168, 145, 125), width=3)
    title_font, lines, gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 52)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in lines) + max(0, len(lines) - 1) * gap
    author_height = draw.textbbox((0, 0), author, font=author_font)[3] - draw.textbbox((0, 0), author, font=author_font)[1]
    y = py + 120 + max(0, (2560 - py - 230 - (title_height + 118 + author_height)) // 2)
    y = _standard_cover_center(draw, y, lines, title_font, (235, 225, 205), gap, 1600) + 118
    _standard_cover_center(draw, y, [author], author_font, (195, 185, 168), 12, 1600)
    if model:
        model_font = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, 2560 - 110, [model], model_font, (145, 132, 115), 12, 1600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cover for The House With Two Skies")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    create_cover(args.metadata, args.out)
