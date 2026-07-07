#!/usr/bin/env python3
"""Cover: One-way observation glass reflecting therapy room, lone woman on patient side, shadowy figure on clinician side, cold institutional white/blue-fluorescent/reflection gray."""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path


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

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Canvas dimensions
# ---------------------------------------------------------------------------
WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765  # panel starts below here


# ---------------------------------------------------------------------------
# Standard cover helpers (required by AGENTS.md)
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


def _draw_background(draw: ImageDraw.ImageDraw) -> None:
    """Institutional grey-white gradient background."""
    for y in range(ART_HEIGHT):
        t = y / ART_HEIGHT
        r = int(210 - t * 60)
        g = int(215 - t * 55)
        b = int(225 - t * 40)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_observation_room(draw: ImageDraw.ImageDraw) -> None:
    """The therapy room seen through the one-way glass, dimly lit."""
    # Wall gradient — pale cool grey
    for y in range(ART_HEIGHT):
        t = y / ART_HEIGHT
        r = int(190 - t * 60)
        g = int(195 - t * 55)
        b = int(205 - t * 50)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))

    # Floor
    floor_y = 1300
    draw.rectangle([(0, floor_y), (WIDTH, ART_HEIGHT)], fill=(160, 165, 175))
    # Floor tiles
    for tx in range(0, WIDTH, 80):
        for ty in range(floor_y, ART_HEIGHT, 80):
            draw.rectangle([tx, ty, tx + 78, ty + 78],
                           fill=(155, 160, 170), outline=(145, 150, 160), width=1)

    # Window with blinds on the far wall
    win_x, win_y = WIDTH // 2 - 120, 200
    draw.rectangle([win_x, win_y, win_x + 240, win_y + 300], fill=(120, 130, 150))
    # Blinds
    for by in range(win_y + 10, win_y + 290, 12):
        draw.line([(win_x + 5, by), (win_x + 235, by)], fill=(100, 110, 130), width=3)

    # Chair for patient
    chair_x, chair_y = WIDTH // 2, 1150
    # Chair back
    draw.rectangle([chair_x - 40, chair_y - 120, chair_x + 40, chair_y - 80], fill=(80, 75, 72))
    # Chair seat
    draw.rectangle([chair_x - 50, chair_y - 30, chair_x + 50, chair_y], fill=(85, 80, 78))
    # Chair legs
    for lx in [chair_x - 40, chair_x + 40]:
        draw.line([(lx, chair_y), (lx - 5, chair_y + 60)], fill=(60, 55, 52), width=5)
        draw.line([(lx, chair_y), (lx + 5, chair_y + 60)], fill=(60, 55, 52), width=5)


def _draw_lone_woman(draw: ImageDraw.ImageDraw) -> None:
    """Lone woman sitting on the patient side of the room, silhouetted."""
    cx, base_y = WIDTH // 2, 1120
    dark = (55, 50, 55)

    # Body (sitting in chair)
    draw.ellipse([cx - 25, base_y - 90, cx + 25, base_y - 30], fill=dark)
    draw.line([(cx, base_y - 30), (cx, base_y)], fill=dark, width=18)
    # Legs (bent, sitting)
    draw.line([(cx - 5, base_y), (cx - 30, base_y + 50)], fill=dark, width=10)
    draw.line([(cx + 5, base_y), (cx + 30, base_y + 50)], fill=dark, width=10)
    # Head
    draw.ellipse([cx - 18, base_y - 135, cx + 18, base_y - 95], fill=dark)
    # Hair
    draw.ellipse([cx - 20, base_y - 138, cx + 20, base_y - 115], fill=(40, 35, 40))
    # Arms
    draw.line([(cx - 15, base_y - 50), (cx - 50, base_y - 20)], fill=dark, width=6)
    draw.line([(cx + 15, base_y - 30), (cx + 50, base_y - 10)], fill=dark, width=6)


def _draw_clinician_shadow(draw: ImageDraw.ImageDraw) -> None:
    """Shadowy figure on the clinician side of the glass, barely visible."""
    cx, base_y = WIDTH // 2 + 200, 1100
    dark = (25, 22, 28)

    # Shadow body
    draw.ellipse([cx - 40, base_y - 160, cx + 40, base_y - 60], fill=dark)
    draw.line([(cx, base_y - 60), (cx, base_y)], fill=dark, width=25)
    # Head
    draw.ellipse([cx - 25, base_y - 210, cx + 25, base_y - 160], fill=dark)
    # Arm holding clipboard
    draw.line([(cx + 20, base_y - 80), (cx + 60, base_y - 40)], fill=dark, width=8)


def _draw_glass_reflection(draw: ImageDraw.ImageDraw) -> None:
    """Faint diagonal glare across the glass suggesting one-way mirror."""
    for i in range(0, 40):
        t = i / 40
        x1 = 100 + i * 8
        x2 = 300 + i * 8
        y1 = 80
        y2 = 1000
        a = int(20 * (1 - abs(t - 0.5) * 2))
        draw.line([(x1, y1), (x2, y2)], fill=(190, 195, 210, a), width=3)


def _draw_foreground_frame(draw: ImageDraw.ImageDraw) -> None:
    """Dark foreground framing suggesting the observation booth."""
    pillar_w = 70
    pillar_color = (35, 37, 48)
    draw.rectangle([(0, 0), (pillar_w, ART_HEIGHT)], fill=pillar_color)
    draw.rectangle([(WIDTH - pillar_w, 0), (WIDTH, ART_HEIGHT)], fill=pillar_color)
    for d in range(0, 50):
        t = d / 50
        grey = int(35 + t * 25)
        draw.line([(pillar_w, ART_HEIGHT - d - 1), (WIDTH - pillar_w, ART_HEIGHT - d - 1)],
                  fill=(grey, grey + 2, grey + 6))
    for d in range(0, 35):
        t = d / 35
        grey = int(40 - t * 15)
        draw.line([(pillar_w, d), (WIDTH - pillar_w, d)],
                  fill=(grey, grey + 2, grey + 6))


def _draw_clinical_label(draw: ImageDraw.ImageDraw) -> None:
    """Small institutional label."""
    label_font = _standard_cover_font("arial.ttf", 22)
    label_text = "OBSERVATION SUITE A  |  ONE-WAY GLASS"
    label_color = (130, 140, 160)
    draw.text((116, ART_HEIGHT - 52), label_text, font=label_font, fill=label_color)


def generate_cover(metadata: dict, out_path: Path) -> None:
    title = _standard_cover_resolve_title(metadata)
    author = _standard_cover_resolve_author(metadata)
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (200, 205, 215))
    draw = ImageDraw.Draw(image)

    # Build the art layer — therapy room behind one-way glass
    _draw_background(draw)
    _draw_observation_room(draw)
    _draw_lone_woman(draw)
    _draw_glass_reflection(draw)
    _draw_clinician_shadow(draw)
    _draw_foreground_frame(draw)
    _draw_clinical_label(draw)

    # Convert to RGBA for tint overlay, then back to RGB
    image = image.convert("RGBA")
    # Cold blue fluorescent overlay
    overlay = Image.new("RGBA", (WIDTH, ART_HEIGHT), (140, 155, 210, 18))
    image.paste(overlay, (0, 0), overlay)
    image = image.convert("RGB")

    # Subtle blur pass through glass region
    glass_region = image.crop((70, 80, WIDTH - 70, ART_HEIGHT - 60))
    glass_blurred = glass_region.filter(ImageFilter.GaussianBlur(radius=0.8))
    image.paste(glass_blurred, (70, 80))

    # Draw the title panel
    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(out_path), "PNG")
    print(f"Cover saved: {out_path}  ({out_path.stat().st_size:,} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cover for The Thousand Faces")
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    generate_cover(metadata, args.out)


if __name__ == "__main__":
    main()
