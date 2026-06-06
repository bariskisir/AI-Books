#!/usr/bin/env python3
"""Generate a 1600x2560 cover for The Fair Exchange (Economic Utopia)."""

from __future__ import annotations

import argparse
import json
import math
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
    title = metadata.get("title", "The Fair Exchange")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (255, 255, 255, 255))
    draw = ImageDraw.Draw(img)

    # --- Sky gradient background ---
    for y in range(0, 1100):
        t = y / 1100
        r = int(50 + t * 80)
        g = int(55 + t * 75)
        b = int(70 + t * 85)
        draw.line((0, y, WIDTH, y), fill=(r, g, b))

    # --- Ground / cobblestone area ---
    for y in range(1100, 1800):
        t = (y - 1100) / 700
        r = int(120 - t * 30)
        g = int(110 - t * 25)
        b = int(95 - t * 20)
        draw.line((0, y, WIDTH, y), fill=(r, g, b))

    # --- Distant buildings / skyline ---
    building_color = (90, 85, 75)
    roofs = [(100, 500, 220, 750), (260, 480, 380, 750), (420, 520, 540, 750),
             (580, 460, 700, 750), (740, 500, 860, 750), (900, 490, 1020, 750),
             (1060, 510, 1180, 750), (1220, 470, 1340, 750), (1380, 500, 1520, 750)]
    for x1, y1, x2, y2 in roofs:
        draw.rectangle((x1, y1, x2, y2), fill=building_color)
        draw.polygon([(x1 - 10, y1), ((x1 + x2) // 2, y1 - 60), (x2 + 10, y1)], fill=(130, 80, 60))

    # --- Market stalls (colorful awnings) ---
    stall_colors = [(180, 100, 60), (60, 130, 100), (160, 120, 50), (80, 100, 140), (140, 90, 110)]
    stall_positions = [(150, 1100, 280, 1350), (330, 1120, 460, 1370), (520, 1080, 650, 1330),
                       (710, 1110, 840, 1360), (900, 1090, 1030, 1340), (1090, 1100, 1220, 1350),
                       (1280, 1120, 1410, 1370)]
    for idx, (sx1, sy1, sx2, sy2) in enumerate(stall_positions):
        color = stall_colors[idx % len(stall_colors)]
        # Stall body
        draw.rectangle((sx1, sy1, sx2, sy2), fill=(160, 140, 110))
        # Awning
        awning_color = (color[0] + 40, color[1] + 40, color[2] + 40)
        draw.arc([(sx1 - 20, sy1 - 30), (sx2 + 20, sy1 + 20)], 0, 180, fill=awning_color, width=8)
        # Table top
        draw.rectangle((sx1 + 10, sy1 + 15, sx2 - 10, sy1 + 25), fill=(200, 180, 150))
        # Goods on table (small colored circles)
        for gx in range(sx1 + 20, sx2 - 10, 15):
            goods_color = (255, 220, 100) if idx % 2 == 0 else (200, 100, 80)
            draw.ellipse((gx, sy1 + 28, gx + 10, sy1 + 38), fill=goods_color)

    # --- Contribution board (large, central) ---
    board_left = (WIDTH - 400) // 2
    board_top = 800
    draw.rectangle((board_left, board_top, board_left + 400, board_top + 280), fill=(60, 50, 40))
    draw.rectangle((board_left + 10, board_top + 10, board_left + 390, board_top + 270), fill=(100, 90, 75))
    # Board text (scribbles)
    board_font = _standard_cover_font("arial.ttf", 14)
    entries = ["Tam - bread, 40 loaves", "Hesta - wool, 6 fleeces", "Eli - cart repair, 1 day",
               "Maron - well water, 8 hrs", "Orin - barley, 17 bush.", "Jory - archive, 6 hrs"]
    for i, entry in enumerate(entries):
        ey = board_top + 25 + i * 38
        draw.text((board_left + 20, ey), entry, font=board_font, fill=(220, 210, 190))
        # Checkmark
        draw.text((board_left + 350, ey), "/", font=board_font, fill=(160, 225, 160))

    # --- Clock tower / central landmark ---
    tower_x = WIDTH // 2
    draw.rectangle((tower_x - 15, 650, tower_x + 15, 800), fill=(160, 140, 120))
    draw.polygon([(tower_x - 25, 650), (tower_x, 610), (tower_x + 25, 650)], fill=(180, 80, 60))
    draw.ellipse((tower_x - 10, 670, tower_x + 10, 690), fill=(255, 230, 180))

    # --- People silhouettes (bartering) ---
    def draw_person(cx, cy, scale=1.0, color=(60, 55, 50)):
        s = scale
        r = 8 * s
        draw.ellipse((cx - r, cy - r * 2, cx + r, cy), fill=color)
        body_top = cy
        body_bot = cy + 30 * s
        draw.line((cx, body_top, cx, body_bot), fill=color, width=int(3 * s))
        arm_y = cy + 10 * s
        draw.line((cx, arm_y, cx - 12 * s, arm_y + 8 * s), fill=color, width=int(2 * s))
        draw.line((cx, arm_y, cx + 12 * s, arm_y + 8 * s), fill=color, width=int(2 * s))
        draw.line((cx, body_bot, cx - 6 * s, body_bot + 12 * s), fill=color, width=int(2 * s))
        draw.line((cx, body_bot, cx + 6 * s, body_bot + 12 * s), fill=color, width=int(2 * s))

    # People in the marketplace
    people = [(200, 1380, 0.9), (400, 1400, 0.8), (700, 1370, 1.0), (950, 1390, 0.85),
              (1150, 1360, 0.95), (1350, 1380, 0.9), (600, 1420, 0.75), (1050, 1410, 0.8)]
    for px, py, sc in people:
        draw_person(px, py, sc)

    # --- Stone pathway texture ---
    for sy in range(1350, 1500, 10):
        for sx in range(0, WIDTH, 60):
            if (sx // 60 + sy // 10) % 3 == 0:
                draw.ellipse((sx, sy, sx + 4, sy + 4), fill=(140, 130, 115, 80))

    # --- Warm glow overlay from marketplace lanterns ---
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    gdraw = ImageDraw.Draw(glow)
    for lx, ly in [(250, 1100), (550, 1080), (850, 1100), (1150, 1090)]:
        for r in range(150, 50, -10):
            alpha = max(0, 8 - (150 - r) // 12)
            gdraw.ellipse((lx - r, ly - r, lx + r, ly + r), fill=(255, 200, 120, alpha))
    img = Image.alpha_composite(img, glow)

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
