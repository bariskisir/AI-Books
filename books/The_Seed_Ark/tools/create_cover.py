#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Seed Ark."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560


def _hex(r, g, b):
    return (r, g, b)


def _gradient(draw, w, h, top_color, bottom_color):
    for y in range(h):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / h)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / h)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_starfield(draw, w, h, density, seed):
    """Draw a starfield background."""
    rng = random.Random(seed)
    for _ in range(density):
        x = rng.randint(0, w)
        y = rng.randint(0, h)
        size = rng.randint(1, 3)
        brightness = rng.randint(100, 255)
        draw.ellipse([x - size, y - size, x + size, y + size], fill=(brightness, brightness, brightness))


def _draw_cylindrical_ship(draw, cx, cy, length, radius, angle, colors, seed):
    """Draw a cylindrical generation ship at the given angle."""
    rng = random.Random(seed)
    rad = math.radians(angle)

    # Calculate endpoints
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    half_len = length // 2

    x1 = cx - int(half_len * cos_a)
    y1 = cy - int(half_len * sin_a)
    x2 = cx + int(half_len * cos_a)
    y2 = cy + int(half_len * sin_a)

    # Main cylinder body - draw as a rotated rectangle by drawing segments
    perp_rad = rad + math.pi / 2
    perp_cos = math.cos(perp_rad)
    perp_sin = math.sin(perp_rad)

    steps = max(length // 4, 20)
    for i in range(steps):
        t = i / steps
        sx = int(x1 + (x2 - x1) * t)
        sy = int(y1 + (y2 - y1) * t)
        color_variant = rng.randint(-15, 15)
        c = (
            min(255, max(0, colors[0][0] + color_variant)),
            min(255, max(0, colors[0][1] + color_variant)),
            min(255, max(0, colors[0][2] + color_variant)),
        )

        # Draw cross-section ellipse at this point
        w = radius
        h = int(radius * abs(perp_cos)) + int(radius * 0.3)
        draw.ellipse([sx - w, sy - h // 2, sx + w, sy + h // 2], fill=c, outline=(80, 140, 200, 100))

    # Hull outline - top and bottom edges
    for sign in (-1, 1):
        ox = int(perp_cos * radius * sign)
        oy = int(perp_sin * radius * sign)
        points = []
        for i in range(steps):
            t = i / steps
            sx = x1 + int((x2 - x1) * t) + ox
            sy = y1 + int((y2 - y1) * t) + oy
            points.append((sx, sy))
        for i in range(len(points) - 1):
            draw.line([points[i], points[i + 1]], fill=(100, 180, 230, 150), width=2)

    # Ring structures along the cylinder
    for i in range(5):
        t = 0.15 + i * 0.175
        rx = int(x1 + (x2 - x1) * t)
        ry = int(y1 + (y2 - y1) * t)
        ring_r = radius + 20
        draw.ellipse(
            [rx - ring_r, ry - int(ring_r * 0.3), rx + ring_r, ry + int(ring_r * 0.3)],
            outline=(120, 190, 230, 180),
            width=2,
        )

    # Glow at the aft end (engine)
    aft_x = x1
    aft_y = y1
    for r in range(60, 0, -5):
        alpha = int(30 * (1 - r / 60))
        draw.ellipse([aft_x - r, aft_y - r, aft_x + r, aft_y + r], fill=(50, 150, 255, alpha))

    # Solar panel arrays on sides
    for sign in (-1, 1):
        px = cx + int(perp_cos * (radius + 30) * sign)
        py = cy + int(perp_sin * (radius + 30) * sign)
        panel_len = length * 0.3
        p_x1 = px - int(panel_len * cos_a / 2)
        p_y1 = py - int(panel_len * sin_a / 2)
        p_x2 = px + int(panel_len * cos_a / 2)
        p_y2 = py + int(panel_len * sin_a / 2)
        draw.line([(p_x1, p_y1), (p_x2, p_y2)], fill=(60, 120, 200, 100), width=8)


def _draw_planet(draw, cx, cy, radius, colors, seed):
    """Draw a habitable planet."""
    rng = random.Random(seed)

    # Planet body
    for r in range(radius, 0, -1):
        t = 1 - r / radius
        ci = min(len(colors) - 1, int(t * (len(colors) - 1)))
        next_ci = min(len(colors) - 1, ci + 1)
        ct = (t * (len(colors) - 1)) - ci
        c = (
            int(colors[ci][0] + (colors[next_ci][0] - colors[ci][0]) * ct),
            int(colors[ci][1] + (colors[next_ci][1] - colors[ci][1]) * ct),
            int(colors[ci][2] + (colors[next_ci][2] - colors[ci][2]) * ct),
        )
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)

    # Atmosphere glow
    for r in range(radius + 20, radius, -1):
        alpha = int(40 * (1 - (r - radius) / 20))
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(100, 180, 255, alpha), width=1)

    # Surface features (clouds/continents)
    for _ in range(12):
        angle = rng.uniform(0, 360)
        dist = rng.uniform(0.2, 0.8) * radius
        spot_x = cx + int(dist * math.cos(math.radians(angle)))
        spot_y = cy + int(dist * math.sin(math.radians(angle)))
        spot_r = rng.randint(10, 40)
        draw.ellipse(
            [spot_x - spot_r, spot_y - spot_r, spot_x + spot_r, spot_y + spot_r],
            fill=(30, 90, 60, 60),
        )

    # Highlight crescent
    for r in range(int(radius * 0.6), 0, -2):
        alpha = int(15 * (1 - r / (radius * 0.6)))
        draw.arc(
            [cx - radius + 20, cy - radius + 20, cx + radius - 20, cy + radius - 20],
            300,
            340,
            fill=(180, 220, 255, alpha),
            width=r // 10 + 1,
        )


def create_cover(metadata_path: str, output_path: str) -> None:
    """Create the cover image."""
    meta = {}
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = meta.get("title", "The Seed Ark")
    author = meta.get("author", "Barış Kısır")

    img = Image.new("RGB", (WIDTH, HEIGHT), (3, 5, 15))
    draw = ImageDraw.Draw(img)

    # Deep space gradient
    _gradient(draw, WIDTH, HEIGHT, (3, 5, 15), (8, 10, 30))

    # Starfield
    _draw_starfield(draw, WIDTH, HEIGHT, 800, 42)

    # Nebula glow
    for i in range(3):
        nx = 300 + i * 500 + random.randint(-100, 100)
        ny = 600 + i * 200 + random.randint(-50, 50)
        for r in range(250, 0, -5):
            alpha = int(3 * (1 - r / 250))
            color = [(60, 30, 100), (40, 60, 120), (80, 40, 80)][i]
            draw.ellipse([nx - r, ny - r, nx + r, ny + r], fill=(color[0], color[1], color[2], alpha))

    # Distant planet (small, appearing far away)
    planet_cx = 500
    planet_cy = 700
    planet_r = 130
    planet_colors = [(20, 60, 100), (30, 90, 120), (50, 120, 80), (60, 100, 60)]
    _draw_planet(draw, planet_cx, planet_cy, planet_r, planet_colors, 101)

    # The generation ship - large, dominating the cover
    ship_cx = WIDTH // 2
    ship_cy = 1200
    ship_length = 600
    ship_radius = 80
    ship_colors = [(50, 80, 120), (60, 100, 140), (70, 120, 160)]
    _draw_cylindrical_ship(draw, ship_cx, ship_cy, ship_length, ship_radius, -15, ship_colors, 1)

    # A second ship segment (background, smaller)
    _draw_cylindrical_ship(draw, WIDTH // 2 + 300, 1100, 200, 30, -10, [(30, 50, 80)], 2)

    # Light bridge between ship and planet (visual connection)
    draw.line([(ship_cx, ship_cy), (planet_cx + planet_r, planet_cy - planet_r // 2)],
              fill=(100, 150, 255, 30), width=1)

    # Draw standard title panel
    _draw_standard_cover_title_panel(img, title, author)

    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


# ---- Standard helper functions ----


def _standard_cover_font(name, size):
    font_dir = "C:/Windows/Fonts"
    candidates = [
        Path(font_dir) / name,
        Path("C:/Windows/Fonts") / "arialbd.ttf",
        Path("C:/Windows/Fonts") / "arial.ttf",
    ]
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
        heights = [
            draw.textbbox((0, 0), l, font=f)[3] - draw.textbbox((0, 0), l, font=f)[1] for l in lines
        ]
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
    import json
    import pathlib

    mp = local_vars.get("args")
    if mp and getattr(mp, "metadata", None):
        try:
            return json.loads(pathlib.Path(mp.metadata).read_text(encoding="utf-8")).get("title", "")
        except Exception:
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
    import json
    import pathlib

    mp = local_vars.get("args")
    if mp and getattr(mp, "metadata", None):
        try:
            return json.loads(pathlib.Path(mp.metadata).read_text(encoding="utf-8")).get("author", "Barış Kısır")
        except Exception:
            pass
    return "Barış Kısır"


def _draw_standard_cover_title_panel(image, title="", author=""):
    W = int(globals().get("WIDTH", 1600))
    H = int(globals().get("HEIGHT", 2560))
    PY = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, PY, W, H), fill=(3, 5, 8, 255))
    draw.line((180, PY + 17, W - 180, PY + 17), fill=(160, 225, 209, 105), width=3)
    tf, lines, tg = _standard_cover_title_font(draw, title, 1260)
    af = _standard_cover_font("arialbd.ttf", 50)
    th = sum(
        draw.textbbox((0, 0), l, font=tf)[3] - draw.textbbox((0, 0), l, font=tf)[1] for l in lines
    ) + max(0, len(lines) - 1) * tg
    ab = draw.textbbox((0, 0), author, font=af)
    ah = ab[3] - ab[1]
    y = PY + 120 + max(0, (H - PY - 210 - (th + 120 + ah)) // 2)
    y = _standard_cover_center(draw, y, lines, tf, (244, 249, 238), tg, W)
    y += 120
    _standard_cover_center(draw, y, [author], af, (210, 229, 221), 12, W)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
