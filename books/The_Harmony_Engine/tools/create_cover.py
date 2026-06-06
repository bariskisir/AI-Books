#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Harmony Engine (Algorithmic Utopia)."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Harmony Engine")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # --- Dark tech background gradient ---
    for y in range(0, HEIGHT):
        t = y / HEIGHT
        r = int(8 + t * 18)
        g = int(10 + t * 22)
        b = int(20 + t * 35)
        draw.line((0, y, WIDTH, y), fill=(r, g, b))

    # --- Data center server racks (background) ---
    rack_color = (25, 30, 45)
    rack_highlight = (40, 48, 65)
    for rx in [80, 240, 400, 560, 720, 880, 1040, 1200, 1360, 1520]:
        draw.rectangle((rx, 200, rx + 60, 1400), fill=rack_color)
        draw.rectangle((rx + 5, 200, rx + 55, 1400), fill=rack_highlight)
        # Server unit lines
        for sy in range(230, 1400, 35):
            draw.rectangle((rx + 8, sy, rx + 52, sy + 25), fill=(30, 36, 55))
            # Blinking LED dots
            if random.random() < 0.6:
                led_color = (0, 200, 100) if random.random() < 0.8 else (255, 200, 50)
                draw.ellipse((rx + 12, sy + 8, rx + 18, sy + 14), fill=led_color)

    # --- Central data core / glowing server ---
    center_x = WIDTH // 2
    core_y = 500

    # Radiant glow behind core
    for r in range(350, 50, -20):
        alpha = max(0, 25 - (350 - r) // 15)
        draw.ellipse((center_x - r, core_y - r, center_x + r, core_y + r),
                     fill=(60, 140, 255, alpha))

    # Central core cube
    cube_size = 160
    draw.rounded_rectangle(
        (center_x - cube_size, core_y - cube_size, center_x + cube_size, core_y + cube_size),
        radius=20, fill=(15, 20, 40)
    )
    draw.rounded_rectangle(
        (center_x - cube_size + 5, core_y - cube_size + 5, center_x + cube_size - 5, core_y + cube_size - 5),
        radius=18, fill=(30, 50, 90, 200)
    )

    # Inner glowing square
    inner = cube_size - 40
    draw.rounded_rectangle(
        (center_x - inner, core_y - inner, center_x + inner, core_y + inner),
        radius=12, fill=(50, 100, 200, 100)
    )

    # Pulsing light at center
    draw.ellipse((center_x - 40, core_y - 40, center_x + 40, core_y + 40),
                 fill=(100, 180, 255, 150))
    draw.ellipse((center_x - 15, core_y - 15, center_x + 15, core_y + 15),
                 fill=(200, 230, 255, 220))

    # --- Holographic wellbeing metrics floating upward ---
    metrics_font = _standard_cover_font("arial.ttf", 16)
    bold_font = _standard_cover_font("arialbd.ttf", 14)

    # Left-side metrics
    left_metrics = [
        ("WELLBEING INDEX", "94.2", (100, 180, 255)),
        ("HAPPINESS SCORE", "+12.4%", (100, 220, 180)),
        ("DEPRESSION RATE", "0.03%", (180, 200, 255)),
        ("LONELINESS", "SOLVED", (150, 230, 210)),
    ]
    for i, (label, value, color) in enumerate(left_metrics):
        y_pos = 760 + i * 70
        draw.text((center_x - 350, y_pos), label, font=metrics_font, fill=(color[0], color[1], color[2], 120))
        draw.text((center_x - 350, y_pos + 22), value, font=bold_font, fill=(color[0], color[1], color[2], 180))
        # Horizontal line
        draw.line((center_x - 350, y_pos + 48, center_x - 100, y_pos + 48), fill=(color[0], color[1], color[2], 60), width=1)

    # Right-side metrics
    right_metrics = [
        ("LIFE SATISFACTION", "8.7/10", (100, 200, 255)),
        ("SOCIAL HARMONY", "96.8%", (120, 220, 190)),
        ("TRUST INDEX", "RISING", (140, 190, 255)),
        ("AI OPTIMIZATION", "ACTIVE", (160, 210, 230)),
    ]
    for i, (label, value, color) in enumerate(right_metrics):
        y_pos = 760 + i * 70
        draw.text((center_x + 80, y_pos), label, font=metrics_font, fill=(color[0], color[1], color[2], 120))
        draw.text((center_x + 80, y_pos + 22), value, font=bold_font, fill=(color[0], color[1], color[2], 180))
        draw.line((center_x + 80, y_pos + 48, center_x + 330, y_pos + 48), fill=(color[0], color[1], color[2], 60), width=1)

    # --- Floating data lines / particles ---
    for _ in range(30):
        px = random.randint(50, WIDTH - 50)
        py = random.randint(200, 1400)
        draw.ellipse((px, py, px + 2, py + 2), fill=(100, 200, 255, random.randint(20, 80)))

    # --- Human silhouettes (citizens) ---
    def draw_human(cx, cy, scale=1.0, color=(20, 30, 55)):
        s = scale
        r = 10 * s
        draw.ellipse((cx - r, cy - r * 2.5, cx + r, cy), fill=color)
        body_top = cy
        body_bot = cy + 35 * s
        draw.polygon([(cx - 8 * s, body_top), (cx + 8 * s, body_top), (cx + 12 * s, body_bot), (cx - 12 * s, body_bot)], fill=color)
        draw.line((cx, body_top + 8 * s, cx - 10 * s, body_top + 20 * s), fill=color, width=int(2 * s))
        draw.line((cx, body_top + 8 * s, cx + 10 * s, body_top + 20 * s), fill=color, width=int(2 * s))
        draw.line((cx - 5 * s, body_bot, cx - 7 * s, body_bot + 12 * s), fill=color, width=int(3 * s))
        draw.line((cx + 5 * s, body_bot, cx + 7 * s, body_bot + 12 * s), fill=color, width=int(3 * s))

    # Row of human silhouettes in foreground
    for i in range(9):
        hx = 200 + i * 150
        hy = 1450
        draw_human(hx, hy, 1.0)
        # Connection lines between people and the core
        draw.line((hx, hy - 30, center_x, core_y + cube_size + 20),
                  fill=(60, 140, 255, 40), width=1)

    # --- Data streams (flowing lines from humans to core) ---
    stream = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    sdraw = ImageDraw.Draw(stream)
    for i in range(15):
        start_x = random.randint(100, WIDTH - 100)
        start_y = random.randint(1300, 1500)
        end_x = center_x + random.randint(-80, 80)
        end_y = core_y + random.randint(-40, 40)
        steps = 20
        for s in range(steps):
            t = s / steps
            x = start_x + (end_x - start_x) * t
            y = start_y + (end_y - start_y) * t
            alpha = max(0, int(60 * (1 - t)))
            sdraw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(80, 180, 255, alpha))
    img = Image.alpha_composite(img, stream)

    # --- Floor reflection line ---
    draw.line((0, 1550, WIDTH, 1550), fill=(40, 60, 100, 80), width=2)
    for fx in range(0, WIDTH, 40):
        draw.line((fx, 1550, fx + 20, 1550), fill=(60, 100, 180, 60), width=1)

    # --- "HARMONY ENGINE" text in glow above core ---
    title_font = _standard_cover_font("arialbd.ttf", 28)
    title_text = "THE HARMONY ENGINE"
    bb = draw.textbbox((0, 0), title_text, font=title_font)
    draw.text((WIDTH // 2 - (bb[2] - bb[0]) // 2, core_y - cube_size - 60),
              title_text, font=title_font, fill=(100, 180, 255, 80))

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
