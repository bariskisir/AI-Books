#!/usr/bin/env python3
"""Generate the cover for The Unwritten City — a vast circular assembly hall under a glass dome."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560

# Colors
SKY_TOP = (10, 15, 30)
SKY_MID = (20, 30, 55)
SKY_BOTTOM = (40, 50, 75)
DOME_GLASS = (140, 170, 210)
DOME_FRAME = (60, 70, 90)
HALL_FLOOR = (30, 35, 45)
HALL_WALLS = (50, 55, 70)
CROWD_COLOR = (80, 90, 110)
CROWD_LIGHT = (220, 200, 150)
WINDOW_GLOW = (255, 220, 120)
LAMP_GLOW = (240, 200, 80)
SNOW_COLOR = (200, 210, 230)


def _draw_gradient(draw, y_start, y_end, color_top, color_bot):
    for y in range(y_start, y_end):
        ratio = (y - y_start) / max(1, y_end - y_start - 1)
        r = int(color_top[0] + (color_bot[0] - color_top[0]) * ratio)
        g = int(color_top[1] + (color_bot[1] - color_top[1]) * ratio)
        b = int(color_top[2] + (color_bot[2] - color_top[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_dome(draw):
    # Glass dome - large ellipse at top
    cx = WIDTH // 2
    dome_top_y = 120
    dome_bot_y = 800
    dome_w = 1400
    dome_h = 680

    # Outer frame
    draw.ellipse(
        [cx - dome_w // 2, dome_top_y, cx + dome_w // 2, dome_bot_y],
        fill=None,
        outline=DOME_FRAME,
        width=4,
    )

    # Glass fill with gradient
    for y in range(dome_top_y, dome_bot_y):
        ratio = (y - dome_top_y) / max(1, dome_bot_y - dome_top_y - 1)
        # Calculate horizontal span at this y
        span_ratio = math.sqrt(1 - ((y - (dome_top_y + dome_bot_y) / 2) / ((dome_bot_y - dome_top_y) / 2)) ** 2)
        span = int(dome_w / 2 * span_ratio)
        if span < 1:
            continue
        alpha = int(30 + 40 * ratio)
        glass_color = (DOME_GLASS[0], DOME_GLASS[1], DOME_GLASS[2], alpha)
        draw.line([(cx - span, y), (cx + span, y)], fill=glass_color)

    # Dome frame ribs
    for angle_deg in range(-60, 70, 15):
        angle = math.radians(angle_deg)
        ex = cx + int(math.cos(angle) * dome_w // 2)
        ey = dome_bot_y + int(math.sin(angle) * dome_h // 2)
        draw.arc(
            [cx - dome_w // 2, dome_top_y, cx + dome_w // 2, dome_bot_y],
            start=angle_deg,
            end=angle_deg + 1,
            fill=DOME_FRAME,
            width=2,
        )
        # Draw rib line from top to bottom at this angle
        line_end_x = cx + int(math.sin(angle) * dome_w // 2 * 0.8)
        line_end_y = dome_bot_y + 50
        draw.line([(cx, dome_top_y + 50), (line_end_x, line_end_y)], fill=DOME_FRAME, width=2)

    # Cross ribs
    for y in range(dome_top_y + 100, dome_bot_y, 80):
        span_ratio = math.sqrt(1 - ((y - (dome_top_y + dome_bot_y) / 2) / ((dome_bot_y - dome_top_y) / 2)) ** 2)
        span = int(dome_w / 2 * span_ratio * 0.85)
        if span < 20:
            continue
        draw.line([(cx - span, y), (cx + span, y)], fill=DOME_FRAME, width=1)

    # Highlight/glow on dome
    highlight = (200, 220, 250, 30)
    for y in range(dome_top_y + 80, dome_top_y + 250):
        span_ratio = math.sqrt(1 - ((y - (dome_top_y + dome_bot_y) / 2) / ((dome_bot_y - dome_top_y) / 2)) ** 2)
        span = int(dome_w / 2 * span_ratio * 0.7)
        if span < 40:
            continue
        light_alpha = max(0, 40 - int((y - dome_top_y - 80) * 0.3))
        if light_alpha > 0:
            draw.line([(cx - span // 2, y), (cx + span // 2, y)], fill=(200, 220, 250, light_alpha))


def _draw_assembly_hall(draw):
    # Interior of the hall - visible through the dome
    cx = WIDTH // 2
    floor_y = 1050

    # Warm glow from inside
    for y in range(floor_y - 300, floor_y):
        alpha = max(0, 60 - (floor_y - y) // 5)
        draw.line([(200, y), (WIDTH - 200, y)], fill=(180, 140, 80, alpha))

    # Circular seating - concentric ellipses
    for i, radius in enumerate(range(300, 650, 30)):
        alpha = max(100, 200 - i * 8)
        seat_color = (60 + i * 3, 65 + i * 3, 80 + i * 2)
        draw.ellipse(
            [cx - radius, floor_y - radius // 2, cx + radius, floor_y + radius // 3],
            fill=None,
            outline=seat_color,
            width=2,
        )

    # Citizens as dots around the seating
    random.seed(42)
    for _ in range(800):
        angle = random.uniform(0, math.pi * 2)
        dist = random.randint(320, 640)
        px = cx + int(math.cos(angle) * dist)
        py = floor_y + int(math.sin(angle) * dist // 3)
        if py < floor_y - 150 or py > floor_y + 50:
            continue
        if px < 100 or px > WIDTH - 100:
            continue
        size = random.randint(2, 5)
        dark = random.randint(60, 100)
        citizen_color = (dark, dark + 10, dark + 20)
        draw.ellipse([px - size, py - size, px + size, py + size], fill=citizen_color)

    # Central podium
    podium_cx = cx
    podium_y = floor_y
    draw.rectangle(
        [podium_cx - 40, podium_y - 60, podium_cx + 40, podium_y],
        fill=(70, 70, 85),
    )
    # Podium light
    draw.ellipse(
        [podium_cx - 25, podium_y - 100, podium_cx + 25, podium_y - 60],
        fill=(200, 180, 120),
    )

    # Warm lamp glow from ceiling
    for _ in range(12):
        lx = random.randint(200, WIDTH - 200)
        ly = random.randint(floor_y - 300, floor_y - 200)
        for r in range(3, 12):
            alpha = max(0, 40 - r * 3)
            draw.ellipse([lx - r * 5, ly - r * 5, lx + r * 5, ly + r * 5], fill=(LAMP_GLOW[0], LAMP_GLOW[1], LAMP_GLOW[2], alpha))


def _draw_buildings(draw):
    # City buildings outside the dome
    base_y = 1050
    for i in range(30):
        x = random.randint(0, WIDTH)
        w = random.randint(30, 80)
        h = random.randint(100, 350)
        if abs(x - WIDTH // 2) < 700:  # Don't overlap dome
            continue
        build_color = (
            random.randint(30, 55),
            random.randint(35, 60),
            random.randint(45, 70),
        )
        draw.rectangle([x, base_y - h, x + w, base_y], fill=build_color)

        # Windows
        for wy in range(base_y - h + 15, base_y - 10, 25):
            for wx in range(x + 8, x + w - 8, 15):
                if random.random() < 0.6:
                    glow = random.randint(60, 180)
                    draw.rectangle(
                        [wx, wy, wx + 8, wy + 12],
                        fill=(glow, glow + 20, glow + 40),
                    )


def _draw_street_lights(draw):
    for i in range(10):
        x = random.randint(50, WIDTH - 50)
        if abs(x - WIDTH // 2) < 600:
            continue
        base_y = 1050
        pole_h = random.randint(60, 100)
        # Pole
        draw.rectangle([x - 2, base_y - pole_h, x + 2, base_y], fill=(60, 60, 70))
        # Light glow
        alpha = random.randint(30, 60)
        for r in range(5, 15):
            a = max(0, alpha - r * 3)
            draw.ellipse([x - r, base_y - pole_h - r, x + r, base_y - pole_h + r], fill=(240, 220, 140, a))


def _draw_snow(draw):
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, 1200)
        r = random.randint(1, 3)
        alpha = random.randint(30, 120)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(SNOW_COLOR[0], SNOW_COLOR[1], SNOW_COLOR[2], alpha))


def _draw_stars(draw):
    for _ in range(80):
        x = random.randint(0, WIDTH)
        y = random.randint(0, 400)
        r = random.randint(1, 2)
        alpha = random.randint(60, 180)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=(200, 210, 240, alpha))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=str, default="")
    parser.add_argument("--out", type=str, default="")
    args = parser.parse_args()

    image = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(image, "RGBA")

    # Night sky gradient
    _draw_gradient(draw, 0, 900, SKY_TOP, SKY_BOTTOM)

    # Stars
    random.seed(7)
    _draw_stars(draw)

    # City buildings outside the dome
    random.seed(13)
    _draw_buildings(draw)

    # Street lights
    random.seed(21)
    _draw_street_lights(draw)

    # Ground / lower gradient
    _draw_gradient(draw, 900, HEIGHT, (35, 40, 55), (15, 18, 25))

    # Interior of assembly hall (visible through dome)
    _draw_assembly_hall(draw)

    # The glass dome
    _draw_dome(draw)

    # Snow
    random.seed(8)
    _draw_snow(draw)

    # Title/author panel via standard helpers
    metadata = {}
    if args.metadata:
        try:
            with open(args.metadata, "r", encoding="utf-8") as f:
                metadata = json.load(f)
        except Exception:
            pass

    title = metadata.get("title", "The Unwritten City")
    author = metadata.get("author", "Barış Kısır")

    _draw_standard_cover_title_panel(image, title=title, author=author)

    output_path = args.out or "covers/The_Unwritten_City.png"
    image.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")


# ----- Standard helper functions (must be included in every cover script) -----

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
    th = sum(draw.textbbox((0, 0), l, font=tf)[3] - draw.textbbox((0, 0), l, font=tf)[1] for l in lines) + max(0, len(lines) - 1) * tg
    ab = draw.textbbox((0, 0), author, font=af)
    ah = ab[3] - ab[1]
    y = PY + 120 + max(0, (H - PY - 210 - (th + 120 + ah)) // 2)
    y = _standard_cover_center(draw, y, lines, tf, (244, 249, 238), tg, W)
    y += 120
    _standard_cover_center(draw, y, [author], af, (210, 229, 221), 12, W)


if __name__ == "__main__":
    main()
