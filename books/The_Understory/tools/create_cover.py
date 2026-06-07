#!/usr/bin/env python3
"""
Cover art for The Understory.

Scene: a cross-section of an old-growth forest, above and below the soil line.
Above: dark fir trunks against a dim green dusk, with one great Mother-tree
broader than the rest. Below: the soil, and through it a luminous web of
mycelial threads — pale gold against the dark earth — connecting the roots of
the trees, with one bright node at the center where a small sapling is fed
from below. Earth browns and forest greens above; the glowing network beneath.
"""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765
SOIL = 760  # soil line: above = forest, below = network


def draw_sky_and_soil(draw: ImageDraw.ImageDraw) -> None:
    """Dim green forest dusk above the soil line; dark earth below."""
    for y in range(SOIL):
        t = y / SOIL
        r = int(28 + (40 - 28) * t)
        g = int(48 + (66 - 48) * t)
        b = int(40 + (46 - 40) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    for y in range(SOIL, ART_HEIGHT):
        t = (y - SOIL) / (ART_HEIGHT - SOIL)
        r = int(40 + (18 - 40) * t)
        g = int(30 + (12 - 30) * t)
        b = int(22 + (10 - 22) * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))
    # soil line
    draw.line([(0, SOIL), (WIDTH, SOIL)], fill=(58, 44, 30), width=4)


def draw_trees(draw: ImageDraw.ImageDraw) -> None:
    """Dark fir trunks rising from the soil line; one great Mother-tree."""
    trunks = [(150, 26), (340, 30), (1180, 28), (1380, 34), (1500, 22)]
    for (tx, w) in trunks:
        draw.rectangle([(tx - w, 60), (tx + w, SOIL)], fill=(22, 26, 22))
        # suggestion of branches
        for by in range(160, SOIL, 90):
            draw.line([(tx, by), (tx - 70, by - 30)], fill=(20, 30, 22), width=6)
            draw.line([(tx, by), (tx + 70, by - 30)], fill=(20, 30, 22), width=6)
    # the Mother — broad, central, tallest
    mx, mw = 760, 70
    draw.rectangle([(mx - mw, 30), (mx + mw, SOIL)], fill=(28, 22, 18))
    for by in range(130, SOIL, 80):
        draw.line([(mx, by), (mx - 150, by - 46)], fill=(26, 34, 24), width=9)
        draw.line([(mx, by), (mx + 150, by - 46)], fill=(26, 34, 24), width=9)


def draw_network(image: Image.Image) -> None:
    """The glowing mycelial web below the soil, connecting the roots."""
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    rng = random.Random(9)

    # root anchors descending from each trunk into the soil
    anchors = []
    for tx in (150, 340, 760, 1180, 1380, 1500):
        ay = SOIL
        # a few descending roots
        for _ in range(3):
            x, y = tx, ay
            for _ in range(rng.randint(4, 7)):
                nx = x + rng.randint(-60, 60)
                ny = y + rng.randint(40, 90)
                if ny > ART_HEIGHT - 30:
                    break
                gd.line([(x, y), (nx, ny)], fill=(120, 92, 58, 200), width=4)
                x, y = nx, ny
            anchors.append((x, y))

    # central bright node — a sapling fed from below
    node = (800, 1180)
    anchors.append(node)

    # the web: faint glowing threads connecting many points
    points = anchors + [(rng.randint(60, WIDTH - 60), rng.randint(SOIL + 40, ART_HEIGHT - 30))
                        for _ in range(70)]
    for i, p in enumerate(points):
        # connect each point to two or three near neighbors
        nbrs = sorted(points, key=lambda q: (q[0] - p[0]) ** 2 + (q[1] - p[1]) ** 2)[1:4]
        for q in nbrs:
            a = rng.randint(28, 70)
            gd.line([p, q], fill=(210, 196, 120, a), width=1)
    # node clusters glow
    for p in points:
        if rng.random() < 0.5:
            gd.ellipse([(p[0] - 2, p[1] - 2), (p[0] + 2, p[1] + 2)], fill=(230, 214, 140, 120))

    glow = glow.filter(ImageFilter.GaussianBlur(1))

    # bright central node + its halo and the little sapling above the soil
    halo = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    nx, ny = node
    for r in range(160, 0, -3):
        a = int(120 * (1 - r / 160))
        hd.ellipse([(nx - r, ny - r), (nx + r, ny + r)], fill=(255, 232, 150, max(0, a // 5)))
    hd.ellipse([(nx - 12, ny - 12), (nx + 12, ny + 12)], fill=(255, 244, 196, 230))
    # threads reaching up from node to the soil line (feeding the sapling)
    for _ in range(6):
        x, y = nx, ny
        tx = nx + rng.randint(-40, 40)
        hd.line([(nx, ny), (tx, SOIL)], fill=(255, 232, 150, 150), width=2)
    halo = halo.filter(ImageFilter.GaussianBlur(2))

    out = Image.alpha_composite(image.convert("RGBA"), glow)
    out = Image.alpha_composite(out, halo)
    image.paste(out.convert("RGB"), (0, 0))

    # the sapling itself, small and green, just above the soil over the node
    d = ImageDraw.Draw(image)
    sx = nx
    d.line([(sx, SOIL), (sx, SOIL - 90)], fill=(70, 54, 36), width=8)
    d.ellipse([(sx - 46, SOIL - 150), (sx + 46, SOIL - 60)], fill=(70, 122, 60))
    d.ellipse([(sx - 34, SOIL - 130), (sx + 34, SOIL - 50)], fill=(92, 146, 72))


def create_cover(metadata_path: str, out_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Understory")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (30, 44, 36))
    draw = ImageDraw.Draw(image)

    draw_sky_and_soil(draw)
    draw_trees(ImageDraw.Draw(image))
    draw_network(image)

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
    parser = argparse.ArgumentParser(description="Generate cover for The Understory")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    create_cover(args.metadata, args.out)
