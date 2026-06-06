#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Whispering Gallery."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560


def _draw_gradient(draw, w, h, top_color, bottom_color):
    for y in range(h):
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * y / h)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * y / h)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * y / h)
        draw.line([(0, y), (w, y)], fill=(r, g, b))


def _draw_archway(draw, cx, cy_base, w_arch, h_arch, stroke_color, fill_color):
    """Draw a gothic pointed archway."""
    # Top arch is formed by two intersecting circles
    # Bottom is vertical lines
    r = w_arch
    # Left curve center is cx + w_arch//2 - r = cx - w_arch//2
    # Right curve center is cx - w_arch//2 + r = cx + w_arch//2
    # Let's draw it as a polygon/outline
    points = []
    # Left base
    x_left = cx - w_arch // 2
    x_right = cx + w_arch // 2
    y_straight = cy_base - h_arch + w_arch // 2

    # Draw vertical walls
    for y in range(cy_base, y_straight, -5):
        points.append((x_left, y))

    # Pointed arch curves
    # Left side curve: (x - (cx - w_arch/2))^2 + (y - y_straight)^2 = r^2
    # Right side curve: (x - (cx + w_arch/2))^2 + (y - y_straight)^2 = r^2
    # We trace from left wall top up to the point, then down to right wall top
    steps = 40
    # Left curve: x goes from cx - w_arch/2 to cx
    for i in range(steps + 1):
        x = x_left + (w_arch // 2) * i // steps
        # y = y_straight - sqrt(r^2 - (x - (cx - w_arch/2))^2)
        dx = x - (cx - w_arch // 2)
        dy = math.sqrt(max(0.0, r * r - dx * dx))
        points.append((x, int(y_straight - dy)))

    # Right curve: x goes from cx to cx + w_arch/2
    for i in range(1, steps + 1):
        x = cx + (w_arch // 2) * i // steps
        dx = x - (cx + w_arch // 2)
        dy = math.sqrt(max(0.0, r * r - dx * dx))
        points.append((x, int(y_straight - dy)))

    for y in range(y_straight, cy_base + 1, 5):
        points.append((x_right, y))

    # Close the polygon at base
    points.append((x_right, cy_base))
    points.append((x_left, cy_base))

    # Draw background fill
    draw.polygon(points, fill=fill_color)

    # Draw thick stone border
    draw.polygon(points, outline=stroke_color, width=8)


def _draw_soundwaves(draw, cx, cy, num_waves, color):
    """Draw concentric ripples representing soundwaves (whispers)."""
    for i in range(num_waves):
        r_x = 100 + i * 80
        r_y = 50 + i * 40
        # Draw dotted/dashed ellipse
        # PIL doesn't do native dashed lines easily, so we draw small segments
        # or ellipses with decreasing alpha
        alpha = max(10, 160 - i * 30)
        draw.ellipse(
            [cx - r_x, cy - r_y, cx + r_x, cy + r_y],
            outline=(color[0], color[1], color[2], alpha),
            width=2,
        )


def _draw_candelabra(draw, cx, cy, scale, color, flame_color):
    """Draw a gothic candelabra with a glowing flame."""
    s = scale
    # Base
    draw.line([(cx - int(30 * s), cy), (cx + int(30 * s), cy)], fill=color, width=int(8 * s))
    # Shaft
    draw.line([(cx, cy), (cx, cy - int(100 * s))], fill=color, width=int(6 * s))
    # Arms
    draw.arc(
        [cx - int(40 * s), cy - int(80 * s), cx + int(40 * s), cy - int(40 * s)],
        0,
        180,
        fill=color,
        width=int(4 * s),
    )
    # Candles
    candle_positions = [cx - int(40 * s), cx, cx + int(40 * s)]
    for px in candle_positions:
        # Candle wax
        draw.rectangle(
            [px - int(4 * s), cy - int(95 * s), px + int(4 * s), cy - int(75 * s)],
            fill=(220, 210, 190),
        )
        # Flame glow
        for r in range(int(24 * s), 0, -4):
            alpha = max(0, int(25 * (1 - r / (24 * s))))
            draw.ellipse(
                [px - r, cy - int(105 * s) - r, px + r, cy - int(105 * s) + r],
                fill=(flame_color[0], flame_color[1], flame_color[2], alpha),
            )
        # Flame core
        draw.ellipse(
            [
                px - int(2 * s),
                cy - int(108 * s),
                px + int(2 * s),
                cy - int(98 * s),
            ],
            fill=(255, 240, 180),
        )


def create_cover(metadata_path: str, output_path: str) -> None:
    """Create the cover image."""
    meta = {}
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
    title = meta.get("title", "The Whispering Gallery")
    author = meta.get("author", "Barış Kısır")
    model = meta.get("model", "gemini-3.5-flash")

    img = Image.new("RGB", (WIDTH, HEIGHT), (6, 8, 14))
    draw = ImageDraw.Draw(img, "RGBA")

    # Deep vertical gothic gradient (midnight blue to deep charcoal black)
    _draw_gradient(draw, WIDTH, HEIGHT, (12, 16, 28), (4, 4, 8))

    # Draw vertical wall textures/pillars faintly in background
    for x in (200, 400, WIDTH - 400, WIDTH - 200):
        # A faint vertical line/shadow
        draw.rectangle([x - 10, 0, x + 10, int(HEIGHT * 0.75)], fill=(8, 10, 18, 50))
        draw.line(
            [(x, 0), (x, int(HEIGHT * 0.75))],
            fill=(30, 35, 50, 40),
            width=2,
        )

    # Floor plane at the bottom
    floor_y = int(HEIGHT * 0.72)
    draw.rectangle([0, floor_y, WIDTH, HEIGHT], fill=(8, 8, 12))
    draw.line([(0, floor_y), (WIDTH, floor_y)], fill=(45, 50, 68), width=3)

    # Perspective lines on floor
    rng = random.Random(42)
    for i in range(12):
        x_start = WIDTH // 2 + (i - 5.5) * 80
        x_end = WIDTH // 2 + (i - 5.5) * 320
        draw.line([(x_start, floor_y), (x_end, HEIGHT)], fill=(20, 24, 34, 120), width=2)

    # Dramatic large Gothic Archway in the center (representing the whispering corridor)
    arch_cx = WIDTH // 2
    arch_base_y = floor_y
    arch_w = 460
    arch_h = 920
    _draw_archway(
        draw,
        arch_cx,
        arch_base_y,
        arch_w,
        arch_h,
        stroke_color=(20, 26, 38),
        fill_color=(5, 6, 10),
    )

    # Inside the arch: a soft golden light emanating from the floor/background
    # representing the source of the mystery
    for r in range(250, 0, -10):
        alpha = max(0, int(15 * (1 - r / 250)))
        draw.ellipse(
            [arch_cx - r, arch_base_y - 120 - r, arch_cx + r, arch_base_y - 120 + r],
            fill=(230, 180, 100, alpha),
        )

    # Concentric acoustic waves / ripples expanding from the archway
    # representing the whispers carried across the masonry
    _draw_soundwaves(draw, arch_cx, arch_base_y - 450, num_waves=6, color=(160, 220, 240))

    # A delicate candelabra on a wooden stand in the foreground to the right
    _draw_candelabra(
        draw,
        cx=WIDTH // 2 + 380,
        cy=floor_y + 80,
        scale=1.6,
        color=(25, 20, 15),
        flame_color=(240, 180, 100),
    )

    # A faint, shadowy figure silhouette standing in the archway, looking away
    # head
    figure_cx = arch_cx - 20
    figure_base_y = arch_base_y - 40
    figure_h = 320
    head_r = int(figure_h * 0.08)
    draw.ellipse(
        [
            figure_cx - head_r,
            figure_base_y - figure_h + head_r,
            figure_cx + head_r,
            figure_base_y - figure_h + 3 * head_r,
        ],
        fill=(12, 10, 14),
    )
    # torso/cloak
    draw.polygon(
        [
            (figure_cx - 15, figure_base_y - figure_h + 3 * head_r),
            (figure_cx + 15, figure_base_y - figure_h + 3 * head_r),
            (figure_cx + 45, figure_base_y),
            (figure_cx - 45, figure_base_y),
        ],
        fill=(10, 8, 12),
    )

    # Faint atmospheric dust / light rays
    for _ in range(60):
        x = rng.randint(150, WIDTH - 150)
        y = rng.randint(100, floor_y)
        size = rng.choice([1, 1, 2, 3])
        alpha = rng.randint(15, 60)
        draw.ellipse(
            [x, y, x + size, y + size],
            fill=(220, 230, 255, alpha),
        )

    # Standard title panel at the bottom
    _draw_standard_cover_title_panel(img, title, author, model)

    output_path_p = Path(output_path)
    output_path_p.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path_p, "PNG")
    print(f"Cover saved to {output_path}")


# ---- Standard helper functions (required by AGENTS.md) ----


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


def _standard_cover_metadata_from_locals(local_vars):
    for key in ("metadata", "meta", "data", "m", "book", "book_data"):
        value = local_vars.get(key)
        if isinstance(value, dict):
            return value
    candidates = []
    args = local_vars.get("args")
    if args is not None:
        candidates.append(getattr(args, "metadata", None))
    for key in ("metadata_path", "meta_path", "mp"):
        candidates.append(local_vars.get(key))
    for metadata_path in candidates:
        if not metadata_path:
            continue
        try:
            json_mod = __import__("json")
            path_cls = __import__("pathlib").Path
            return json_mod.loads(path_cls(metadata_path).read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def _standard_cover_resolve_title(local_vars):
    for key in ("title", "ti", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value
    metadata = _standard_cover_metadata_from_locals(local_vars)
    for key in ("title", "book_title", "name"):
        value = metadata.get(key)
        if value:
            return value
    args = local_vars.get("args")
    candidates = []
    if args is not None:
        candidates.append(getattr(args, "out", None))
    for key in ("output_path", "out_path", "op", "out"):
        candidates.append(local_vars.get(key))
    for output_path in candidates:
        if not output_path:
            continue
        try:
            path_cls = __import__("pathlib").Path
            stem = path_cls(output_path).stem.replace("_", " ").strip()
            if stem:
                return stem
        except Exception:
            continue
    return ""


def _standard_cover_resolve_author(local_vars):
    for key in ("author", "au", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value
    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("author")
    if value:
        return value
    return "Barış Kısır"


def _standard_cover_resolve_model(local_vars):
    for key in ("model", "mo", "MODEL"):
        value = local_vars.get(key)
        if value:
            return value
    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("model")
    if value:
        return value
    return ""


def _draw_standard_cover_title_panel(image, title="", author="", model=""):
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
    if not model:
        model = _standard_cover_resolve_model(locals())
    if model:
        mf = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, H - 110, [model], mf, (140, 140, 160), 12, W)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()
