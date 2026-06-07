#!/usr/bin/env python3
"""
Cover art for The Tessera Bureau.

Scene: a city fractured into adjacent parallel panes. A cool institutional
dusk over a tessellated grid; a skyline printed twice and slightly offset,
cyan and magenta, like a misregistered print — the two worlds drifting toward
each other. At the center a single warm doorway of light, a seam standing open,
and one small figure on the threshold deciding whether to step through.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    """Cool grey-blue institutional dusk."""
    for y in range(ART_HEIGHT):
        t = y / ART_HEIGHT
        r = int(34 + (78 - 34) * t)
        g = int(40 + (92 - 40) * t)
        b = int(58 + (110 - 58) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_tessellation(image: Image.Image) -> None:
    """A faint diamond-tile grid laid over the whole field — the city tessellated."""
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    step = 96
    col = (150, 170, 200, 26)
    for gy in range(-step, ART_HEIGHT + step, step):
        for gx in range(-step, WIDTH + step, step):
            od.line([(gx, gy + step // 2), (gx + step // 2, gy)], fill=col, width=2)
            od.line([(gx + step // 2, gy), (gx + step, gy + step // 2)], fill=col, width=2)
            od.line([(gx + step, gy + step // 2), (gx + step // 2, gy + step)], fill=col, width=2)
            od.line([(gx + step // 2, gy + step), (gx, gy + step // 2)], fill=col, width=2)
    image.paste(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"), (0, 0))


def _skyline(draw: ImageDraw.ImageDraw, base_y: int, color, dx: int) -> None:
    """A row of towers in a single flat color, offset by dx."""
    import random
    rng = random.Random(7)
    x = -40 + dx
    while x < WIDTH + 40:
        w = rng.choice([70, 90, 110, 140, 60])
        h = rng.choice([360, 520, 680, 440, 600, 300])
        top = base_y - h
        draw.rectangle([(x, top), (x + w, base_y)], fill=color)
        # a few lit windows as the same flat color, lighter
        x += w + rng.choice([10, 18, 26])


def draw_offset_skylines(image: Image.Image) -> None:
    """Two skylines, cyan and magenta, slightly offset — misregistered panes."""
    base_y = 1180
    cyan = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    mag = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    _skyline(ImageDraw.Draw(cyan), base_y, (70, 200, 210, 120), dx=-16)
    _skyline(ImageDraw.Draw(mag), base_y, (210, 70, 150, 110), dx=16)
    merged = Image.alpha_composite(image.convert("RGBA"), cyan)
    merged = Image.alpha_composite(merged, mag)
    image.paste(merged.convert("RGB"), (0, 0))


def draw_seam(image: Image.Image) -> None:
    """A vertical doorway of warm light at the center — the open seam."""
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    cx = WIDTH // 2
    door_w, door_h = 150, 470
    top = 740
    # halo
    for r in range(220, 0, -6):
        a = int(70 * (1 - r / 220))
        gd.ellipse([(cx - door_w // 2 - r, top - r), (cx + door_w // 2 + r, top + door_h + r)],
                   fill=(255, 226, 150, max(0, a // 5)))
    # the bright slit
    for i in range(door_w // 2, 0, -1):
        t = i / (door_w / 2)
        a = int(255 * (1 - t) ** 1.5)
        gd.rectangle([(cx - i, top), (cx + i, top + door_h)], fill=(255, 235, 180, a))
    gd.rectangle([(cx - 10, top), (cx + 10, top + door_h)], fill=(255, 248, 224, 255))
    glow = glow.filter(ImageFilter.GaussianBlur(3))
    image.paste(Image.alpha_composite(image.convert("RGBA"), glow).convert("RGB"), (0, 0))


def draw_figure(draw: ImageDraw.ImageDraw) -> None:
    """A small lone figure on the threshold, silhouetted against the seam."""
    cx = WIDTH // 2
    base = 1210
    col = (16, 18, 26)
    # legs
    draw.line([(cx - 16, base), (cx - 8, base - 70)], fill=col, width=15)
    draw.line([(cx + 16, base), (cx + 8, base - 70)], fill=col, width=15)
    # torso
    draw.line([(cx, base - 64), (cx, base - 150)], fill=col, width=30)
    # head
    draw.ellipse([(cx - 20, base - 196), (cx + 20, base - 150)], fill=col)
    # long shadow toward viewer
    draw.polygon([(cx - 22, base), (cx + 22, base), (cx + 70, base + 130), (cx - 70, base + 130)],
                 fill=(20, 24, 34))


def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Tessera Bureau")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (40, 48, 66))
    # overlays are full-height so alpha_composite matches the base image size
    draw = ImageDraw.Draw(image)

    draw_background(draw)
    draw_tessellation(image)
    draw_offset_skylines(image)
    draw_seam(image)
    draw_figure(ImageDraw.Draw(image))

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
    parser = argparse.ArgumentParser(description="Generate cover for The Tessera Bureau")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    create_cover(args.metadata, args.out)
