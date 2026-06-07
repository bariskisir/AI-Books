#!/usr/bin/env python3
"""
Create the cover image for The Norsewoman.

Scene: A Norse longhouse at night under the aurora borealis.
A silhouette of a woman stands on a promontory above a dark fjord.
Cold blues, greens, and silver palette. Viking runes carved in stone
at the foreground. Longship prow visible below in the fjord.
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
ART_HEIGHT = 1765  # upper 65% approx


def draw_aurora(draw: ImageDraw.Draw, rng: random.Random) -> None:
    """Draw aurora borealis ribbons across the sky."""
    # Multiple aurora bands in greens and blue-greens
    aurora_colors = [
        (30, 180, 80, 60),   # green
        (20, 200, 120, 45),  # bright green
        (40, 160, 200, 40),  # cyan-green
        (60, 100, 220, 35),  # blue
        (100, 200, 150, 30), # light green
    ]

    for i, color in enumerate(aurora_colors):
        # Each aurora band is a wavy horizontal stripe
        base_y = 180 + i * 120 + rng.randint(-40, 40)
        amplitude = rng.randint(40, 100)
        frequency = rng.uniform(0.003, 0.007)
        phase = rng.uniform(0, math.pi * 2)
        thickness = rng.randint(30, 80)

        points = []
        for x in range(0, WIDTH + 10, 5):
            y = base_y + amplitude * math.sin(frequency * x + phase)
            points.append((x, int(y)))

        # Draw as a thick poly with transparency effect
        for t in range(thickness, 0, -3):
            alpha = int(color[3] * (1 - t / thickness) * 1.5)
            alpha = min(alpha, color[3])
            c = (color[0], color[1], color[2], alpha)
            shifted_up = [(p[0], p[1] - t // 2) for p in points]
            shifted_dn = [(p[0], p[1] + t // 2) for p in points]
            poly = shifted_up + list(reversed(shifted_dn))
            if len(poly) >= 3:
                draw.polygon(poly, fill=c)


def draw_stars(draw: ImageDraw.Draw, rng: random.Random) -> None:
    """Draw a field of cold stars in the upper sky."""
    for _ in range(340):
        x = rng.randint(0, WIDTH)
        y = rng.randint(0, int(ART_HEIGHT * 0.55))
        size = rng.choice([1, 1, 1, 2, 2, 3])
        brightness = rng.randint(160, 255)
        # Stars are mostly white-blue
        r = min(brightness, 200)
        g = min(brightness, 220)
        b = brightness
        alpha = rng.randint(140, 255)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(r, g, b, alpha))


def draw_sky_gradient(image: Image.Image) -> Image.Image:
    """Deep night-sky gradient: near-black at top to dark blue-grey midway."""
    sky = Image.new("RGBA", (WIDTH, ART_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sky)
    for y in range(ART_HEIGHT):
        t = y / ART_HEIGHT
        # Deep black-indigo at top, dark blue at horizon
        r = int(4 + 18 * t)
        g = int(6 + 20 * t)
        b = int(22 + 40 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))
    image.paste(sky, (0, 0), sky)
    return image


def draw_fjord(draw: ImageDraw.Draw) -> None:
    """Draw the dark fjord in the lower middle section of the art panel."""
    # Fjord water — very dark, near-black with faint silver reflections
    fjord_top = int(ART_HEIGHT * 0.62)
    fjord_bottom = ART_HEIGHT

    for y in range(fjord_top, fjord_bottom):
        t = (y - fjord_top) / (fjord_bottom - fjord_top)
        r = int(8 + 12 * t)
        g = int(14 + 18 * t)
        b = int(28 + 30 * t)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b, 255))

    # Aurora reflection on the water — faint green shimmer
    for i in range(8):
        x_center = WIDTH // 2 + (i - 4) * 160
        y_center = fjord_top + 80 + i * 20
        for radius in range(60, 0, -10):
            alpha = max(0, 20 - radius // 4)
            draw.ellipse(
                [x_center - radius * 3, y_center - radius // 4,
                 x_center + radius * 3, y_center + radius // 4],
                fill=(30, 140, 60, alpha)
            )


def draw_longhouse(draw: ImageDraw.Draw) -> None:
    """Draw a Norse longhouse silhouette on the left side of the horizon."""
    # Longhouse sits at the left, horizon line around 62% of art height
    horizon_y = int(ART_HEIGHT * 0.62)
    lh_x = 80
    lh_w = 380
    lh_h = 110
    lh_y = horizon_y - lh_h

    # Main longhouse body
    draw.rectangle([lh_x, lh_y, lh_x + lh_w, horizon_y], fill=(12, 10, 15, 255))

    # Roof — steep pitched roof typical of Norse longhouses
    roof_pts = [
        (lh_x - 10, lh_y),
        (lh_x + lh_w // 2, lh_y - 70),
        (lh_x + lh_w + 10, lh_y),
    ]
    draw.polygon(roof_pts, fill=(10, 8, 12, 255))

    # Dragon-head gable finials (simplified shapes)
    draw.ellipse([lh_x - 20, lh_y - 85, lh_x, lh_y - 60], fill=(10, 8, 12, 255))
    draw.ellipse([lh_x + lh_w, lh_y - 85, lh_x + lh_w + 20, lh_y - 60], fill=(10, 8, 12, 255))

    # Small smoke wisp from center
    for i in range(5):
        sx = lh_x + lh_w // 2 + i * 3
        sy_start = lh_y - 70 - i * 12
        draw.ellipse([sx - 4, sy_start - 8, sx + 4, sy_start], fill=(30, 28, 35, 60))

    # Faint orange glow from window/door
    draw.rectangle(
        [lh_x + lh_w // 2 - 15, lh_y + 30, lh_x + lh_w // 2 + 15, horizon_y - 5],
        fill=(80, 40, 10, 180)
    )


def draw_cliff_and_land(draw: ImageDraw.Draw) -> None:
    """Draw rocky landscape and a promontory on the right side."""
    horizon_y = int(ART_HEIGHT * 0.62)

    # Right-side land mass / promontory
    land_pts = [
        (WIDTH, ART_HEIGHT),
        (WIDTH, horizon_y + 20),
        (1380, horizon_y - 10),
        (1250, horizon_y - 40),
        (1180, horizon_y + 15),
        (1100, horizon_y - 5),
        (950, horizon_y + 30),
        (700, horizon_y + 20),
        (400, horizon_y),
        (0, horizon_y),
        (0, ART_HEIGHT),
    ]
    draw.polygon(land_pts, fill=(15, 13, 20, 255))

    # Left-side rocky terrain
    left_terrain = [
        (0, ART_HEIGHT),
        (0, horizon_y),
        (80, horizon_y - 10),
        (160, horizon_y + 5),
        (300, horizon_y - 5),
        (400, horizon_y),
        (400, ART_HEIGHT),
    ]
    draw.polygon(left_terrain, fill=(15, 13, 20, 255))

    # Cliff promontory where the woman stands (right of center)
    cliff_pts = [
        (980, ART_HEIGHT),
        (980, int(ART_HEIGHT * 0.54)),
        (1020, int(ART_HEIGHT * 0.52)),
        (1070, int(ART_HEIGHT * 0.53)),
        (1100, int(ART_HEIGHT * 0.555)),
        (1100, ART_HEIGHT),
    ]
    draw.polygon(cliff_pts, fill=(18, 14, 22, 255))


def draw_rune_stone(draw: ImageDraw.Draw) -> None:
    """Draw a rune-scratched standing stone in the left foreground."""
    # Large standing stone, bottom-left area
    stone_x = 120
    stone_y_top = int(ART_HEIGHT * 0.72)
    stone_w = 90
    stone_h = int(ART_HEIGHT * 0.26)

    # Stone body — slightly irregular quadrilateral
    stone_pts = [
        (stone_x + 5, stone_y_top),
        (stone_x + stone_w - 10, stone_y_top + 15),
        (stone_x + stone_w, stone_y_top + stone_h),
        (stone_x, stone_y_top + stone_h),
    ]
    draw.polygon(stone_pts, fill=(28, 24, 34, 255))

    # Rune scratches — simplified Elder Futhark-like marks in silver-grey
    rune_color = (120, 130, 155, 200)
    rune_data = [
        # Each rune: list of line segments [(x1,y1),(x2,y2)]
        # ᚱ (Raido)
        [(stone_x + 28, stone_y_top + 35), (stone_x + 28, stone_y_top + 75)],
        [(stone_x + 28, stone_y_top + 35), (stone_x + 45, stone_y_top + 50)],
        [(stone_x + 45, stone_y_top + 50), (stone_x + 28, stone_y_top + 55)],
        [(stone_x + 28, stone_y_top + 55), (stone_x + 45, stone_y_top + 70)],
        # ᚠ (Fehu)
        [(stone_x + 28, stone_y_top + 90), (stone_x + 28, stone_y_top + 130)],
        [(stone_x + 28, stone_y_top + 95), (stone_x + 45, stone_y_top + 103)],
        [(stone_x + 28, stone_y_top + 110), (stone_x + 45, stone_y_top + 118)],
        # ᚾ (Naudiz)
        [(stone_x + 28, stone_y_top + 145), (stone_x + 28, stone_y_top + 185)],
        [(stone_x + 45, stone_y_top + 145), (stone_x + 45, stone_y_top + 185)],
        [(stone_x + 28, stone_y_top + 148), (stone_x + 45, stone_y_top + 180)],
        # ᛁ (Isa)
        [(stone_x + 36, stone_y_top + 200), (stone_x + 36, stone_y_top + 235)],
    ]
    for segment in rune_data:
        draw.line(segment, fill=rune_color, width=2)


def draw_longship_prow(draw: ImageDraw.Draw) -> None:
    """Draw the prow of a longship just visible in the fjord below left."""
    fjord_top = int(ART_HEIGHT * 0.62)
    # Prow rises from the water — silhouette only
    prow_base_x = 240
    prow_base_y = fjord_top + 60

    # Hull — low, angled
    hull_pts = [
        (prow_base_x - 60, prow_base_y + 50),
        (prow_base_x + 80, prow_base_y + 50),
        (prow_base_x + 60, prow_base_y + 30),
        (prow_base_x - 80, prow_base_y + 30),
    ]
    draw.polygon(hull_pts, fill=(14, 11, 18, 255))

    # Prow neck — rising curved element
    for i in range(30):
        t = i / 30
        x = prow_base_x - 60 - int(t * 30)
        y = prow_base_y + 30 - int(t * 70)
        draw.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(14, 11, 18, 255))

    # Dragon head tip
    tip_x = prow_base_x - 90
    tip_y = prow_base_y - 40
    head_pts = [
        (tip_x, tip_y),
        (tip_x + 20, tip_y + 10),
        (tip_x + 15, tip_y + 25),
        (tip_x - 5, tip_y + 20),
    ]
    draw.polygon(head_pts, fill=(14, 11, 18, 255))


def draw_woman_silhouette(draw: ImageDraw.Draw) -> None:
    """Draw the silhouette of a woman standing on the cliff promontory."""
    # Woman stands on the cliff at about x=1040, feet at ~52% of art height
    feet_y = int(ART_HEIGHT * 0.53)
    cx = 1040

    # Legs
    draw.polygon([
        (cx - 8, feet_y),
        (cx + 8, feet_y),
        (cx + 10, feet_y - 70),
        (cx - 10, feet_y - 70),
    ], fill=(8, 6, 12, 255))

    # Dress/skirt flowing in wind — slightly to the right
    skirt_pts = [
        (cx - 18, feet_y - 70),
        (cx + 18, feet_y - 70),
        (cx + 35, feet_y - 20),
        (cx + 10, feet_y),
        (cx - 8, feet_y),
        (cx - 25, feet_y - 20),
    ]
    draw.polygon(skirt_pts, fill=(8, 6, 12, 255))

    # Torso
    draw.polygon([
        (cx - 12, feet_y - 140),
        (cx + 12, feet_y - 140),
        (cx + 14, feet_y - 70),
        (cx - 14, feet_y - 70),
    ], fill=(8, 6, 12, 255))

    # Cloak — blowing slightly to right
    cloak_pts = [
        (cx - 12, feet_y - 140),
        (cx + 12, feet_y - 140),
        (cx + 50, feet_y - 90),
        (cx + 55, feet_y - 50),
        (cx + 20, feet_y - 60),
        (cx + 14, feet_y - 70),
        (cx - 14, feet_y - 70),
        (cx - 30, feet_y - 80),
        (cx - 35, feet_y - 110),
    ]
    draw.polygon(cloak_pts, fill=(10, 8, 15, 255))

    # Head
    head_y = feet_y - 165
    draw.ellipse([cx - 12, head_y, cx + 12, head_y + 25], fill=(8, 6, 12, 255))

    # Hair blowing to the right
    hair_pts = [
        (cx - 5, head_y + 5),
        (cx + 12, head_y + 8),
        (cx + 45, head_y + 2),
        (cx + 60, head_y + 12),
        (cx + 40, head_y + 20),
        (cx + 12, head_y + 18),
    ]
    draw.polygon(hair_pts, fill=(8, 6, 12, 255))

    # Arm extended — holding a staff
    arm_pts = [
        (cx - 12, feet_y - 130),
        (cx - 5, feet_y - 130),
        (cx - 10, feet_y - 200),
        (cx - 17, feet_y - 200),
    ]
    draw.polygon(arm_pts, fill=(8, 6, 12, 255))

    # Staff
    draw.line(
        [(cx - 13, feet_y - 200), (cx - 13, feet_y - 10)],
        fill=(18, 16, 25, 255), width=3
    )


def draw_horizon_glow(draw: ImageDraw.Draw) -> None:
    """Faint cold glow along the horizon line."""
    horizon_y = int(ART_HEIGHT * 0.62)
    for thickness in range(25, 0, -1):
        alpha = int(35 * (1 - thickness / 25))
        # Cold silver-blue glow
        draw.line(
            [(0, horizon_y - thickness), (WIDTH, horizon_y - thickness)],
            fill=(140, 170, 210, alpha)
        )


def create_cover(metadata_path: str, output_path: str) -> None:
    metadata = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = metadata.get("title", "The Norsewoman")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    rng = random.Random(42)  # fixed seed for reproducibility

    image = Image.new("RGBA", (WIDTH, HEIGHT), (6, 5, 10, 255))

    # Sky gradient
    image = draw_sky_gradient(image)

    draw = ImageDraw.Draw(image, "RGBA")

    # Stars (below aurora)
    draw_stars(draw, rng)

    # Aurora borealis ribbons
    draw_aurora(draw, rng)

    # Horizon glow
    draw_horizon_glow(draw)

    # Landforms
    draw_cliff_and_land(draw)
    draw_fjord(draw)

    # Longhouse
    draw_longhouse(draw)

    # Rune stone
    draw_rune_stone(draw)

    # Longship prow
    draw_longship_prow(draw)

    # Woman silhouette on cliff
    draw_woman_silhouette(draw)

    # Soft blur to blend layers
    art_region = image.crop((0, 0, WIDTH, ART_HEIGHT))
    art_blurred = art_region.filter(ImageFilter.GaussianBlur(radius=0.8))
    image.paste(art_blurred, (0, 0))

    # Re-draw sharp silhouettes on top after blur
    draw2 = ImageDraw.Draw(image, "RGBA")
    draw_cliff_and_land(draw2)
    draw_woman_silhouette(draw2)
    draw_rune_stone(draw2)
    draw_longhouse(draw2)
    draw_longship_prow(draw2)

    # Convert to RGB for final save
    final = image.convert("RGB")

    # Draw title panel
    _draw_standard_cover_title_panel(final, title=title, author=author, model=model)

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    final.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


# ---------------------------------------------------------------------------
# Standard cover helpers (required by project conventions)
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
    draw.rectangle((0, py, 1600, 2560), fill=(12, 10, 8, 255))
    draw.line((180, py + 17, 1420, py + 17), fill=(120, 140, 195, 125), width=3)
    title_font, lines, gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 52)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in lines) + max(0, len(lines) - 1) * gap
    author_height = draw.textbbox((0, 0), author, font=author_font)[3] - draw.textbbox((0, 0), author, font=author_font)[1]
    y = py + 120 + max(0, (2560 - py - 230 - (title_height + 118 + author_height)) // 2)
    y = _standard_cover_center(draw, y, lines, title_font, (220, 215, 200), gap, 1600) + 118
    _standard_cover_center(draw, y, [author], author_font, (180, 170, 160), 12, 1600)
    if model:
        model_font = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, 2560 - 110, [model], model_font, (130, 120, 140), 12, 1600)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate cover for The Norsewoman")
    parser.add_argument("--metadata", required=True, help="Path to metadata JSON")
    parser.add_argument("--out", required=True, help="Output PNG path")
    args = parser.parse_args()
    create_cover(args.metadata, args.out)
