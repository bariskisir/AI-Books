#!/usr/bin/env python3
"""Create a cover image for The Mermaid of Monhegan using PIL."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

WIDTH = 1600
HEIGHT = 2560
PANEL_TOP = 1920
PANEL_HEIGHT = HEIGHT - PANEL_TOP  # 640


def draw_gradient(draw: ImageDraw.Draw) -> None:
    """Draw a vertical gradient from dark gray-blue to sea-foam green."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(40 + ratio * 120)
        g = int(60 + ratio * 140)
        b = int(80 + ratio * 130)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_rocks(draw: ImageDraw.Draw) -> None:
    """Draw rocky Maine coastline at the horizon."""
    base_y = 700
    colors = [(60, 55, 50), (75, 70, 65), (50, 45, 40)]
    # Foreground rocks
    points = [
        [(0, HEIGHT), (50, 900), (120, 880), (180, 920), (250, 860), (300, 950), (400, base_y + 100),
         (500, base_y + 40), (580, base_y + 80), (650, base_y + 20), (720, base_y + 60),
         (800, base_y + 10), (880, base_y + 50), (950, base_y), (1020, base_y + 30),
         (1100, base_y + 70), (1180, base_y + 15), (1250, base_y + 55), (1320, base_y + 10),
         (1400, base_y + 40), (1480, base_y + 20), (1550, base_y + 50), (1600, base_y + 30), (WIDTH, HEIGHT)],
        [(-50, HEIGHT), (0, 1050), (80, 1000), (160, 1040), (240, 980), (320, 1060),
         (400, 960), (480, 1020), (560, 940), (640, 1000), (720, 920),
         (800, 980), (880, 900), (960, 960), (1040, 880), (1120, 940),
         (1200, 860), (1280, 920), (1360, 840), (1440, 900), (1520, 820), (1600, 880), (1650, HEIGHT)],
    ]
    for i, pts in enumerate(points):
        draw.polygon(pts, fill=colors[i % len(colors)])
    # Distant island silhouette
    island = [(200, base_y - 20), (280, base_y - 80), (360, base_y - 100), (440, base_y - 60),
              (520, base_y - 90), (600, base_y - 35), (680, base_y - 70), (760, base_y - 25),
              (500, base_y + 20), (300, base_y + 15)]
    draw.polygon(island, fill=(45, 50, 55))


def draw_lighthouse(draw: ImageDraw.Draw) -> None:
    """Draw a lighthouse on the distant island."""
    # Tower
    lx, ly = 420, 520
    draw.rectangle([lx - 8, ly, lx + 8, ly + 150], fill=(200, 195, 190))
    # Light house top
    draw.rectangle([lx - 12, ly - 5, lx + 12, ly + 5], fill=(180, 50, 50))
    draw.rectangle([lx - 14, ly - 10, lx + 14, ly - 5], fill=(150, 40, 40))
    # Light beam
    draw.ellipse([lx - 20, ly - 20, lx + 20, ly + 20], fill=(255, 240, 180))
    draw.ellipse([lx - 10, ly - 10, lx + 10, ly + 10], fill=(255, 255, 200))


def draw_mermaid_silhouette(draw: ImageDraw.Draw) -> None:
    """Draw a mermaid silhouette on a rock in the foreground."""
    # Rock
    rock = [(900, 1300), (980, 1240), (1060, 1250), (1120, 1280), (1080, 1350), (920, 1340)]
    draw.polygon(rock, fill=(35, 35, 35))

    # Mermaid silhouette sitting on rock
    # Head
    cx, cy = 1020, 1140
    draw.ellipse([cx - 18, cy - 18, cx + 18, cy + 18], fill=(20, 20, 25))
    # Torso
    torso = [(cx - 12, cy + 18), (cx + 12, cy + 18), (cx + 15, cy + 60), (cx - 15, cy + 60)]
    draw.polygon(torso, fill=(20, 20, 25))
    # Tail curving down
    tail_pts = [(cx - 15, cy + 60), (cx + 15, cy + 60), (cx + 25, cy + 80), (cx + 40, cy + 95),
                (cx + 30, cy + 110), (cx + 10, cy + 105), (cx - 5, cy + 90),
                (cx - 15, cy + 80), (cx - 20, cy + 70), (cx - 15, cy + 60)]
    draw.polygon(tail_pts, fill=(20, 20, 25))
    # Tail fin
    fin = [(cx + 10, cy + 105), (cx + 35, cy + 110), (cx + 45, cy + 120),
           (cx + 30, cy + 130), (cx + 15, cy + 125), (cx + 5, cy + 115)]
    draw.polygon(fin, fill=(20, 20, 25))
    # Arm reaching out
    arm = [(cx - 12, cy + 25), (cx - 35, cy + 15), (cx - 45, cy + 20)]
    draw.line(arm, fill=(20, 20, 25), width=4)
    # Hair (flowing back)
    hair = [(cx + 15, cy - 5), (cx + 25, cy + 5), (cx + 30, cy + 20),
            (cx + 28, cy + 35), (cx + 20, cy + 45)]
    draw.line(hair, fill=(20, 20, 25), width=6)


def draw_title_panel(draw: ImageDraw.Draw) -> None:
    """Draw the dark title panel at the bottom of the cover."""
    # Dark semi-transparent panel
    draw.rectangle([(0, PANEL_TOP), (WIDTH, HEIGHT)], fill=(15, 20, 30, 220))
    # Add a dark rectangle that's fully opaque
    draw.rectangle([(0, PANEL_TOP), (WIDTH, HEIGHT)], fill=(15, 20, 30))

    # Top accent line
    draw.line([(300, PANEL_TOP + 10), (WIDTH - 300, PANEL_TOP + 10)], fill=(180, 200, 210), width=2)

    # Load font
    try:
        title_font = ImageFont.truetype("arialbd.ttf", 80)
        author_font = ImageFont.truetype("arialbd.ttf", 36)
    except Exception:
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()

    # Title
    title = "The Mermaid"
    subtitle = "of Monhegan"
    bbox_t = draw.textbbox((0, 0), title, font=title_font)
    bbox_s = draw.textbbox((0, 0), subtitle, font=title_font)
    tw_t = bbox_t[2] - bbox_t[0]
    tw_s = bbox_s[2] - bbox_s[0]

    title_y = PANEL_TOP + 80
    draw.text(((WIDTH - tw_t) // 2, title_y), title, fill=(255, 255, 255), font=title_font)
    draw.text(((WIDTH - tw_s) // 2, title_y + 95), subtitle, fill=(255, 255, 255), font=title_font)

    # Author
    author = "Barış Kısır"
    bbox_a = draw.textbbox((0, 0), author, font=author_font)
    aw = bbox_a[2] - bbox_a[0]
    draw.text(((WIDTH - aw) // 2, PANEL_TOP + 260), author, fill=(180, 200, 210), font=author_font)

    # Bottom accent line
    draw.line([(400, PANEL_TOP + 320), (WIDTH - 400, PANEL_TOP + 320)], fill=(180, 200, 210), width=1)


def add_atmosphere(draw: ImageDraw.Draw) -> None:
    """Add mist, stars, and atmospheric effects."""
    # Moon
    draw.ellipse([(1100, 150), (1180, 230)], fill=(220, 220, 210, 180))
    draw.ellipse([(1120, 170), (1180, 230)], fill=(240, 240, 230, 200))

    # Mist layers
    for y in range(600, 800, 5):
        alpha = max(0, 30 - abs(y - 700) // 5)
        draw.line([(0, y), (WIDTH, y)], fill=(200, 210, 215, alpha))

    # Stars
    stars = [(100, 80), (300, 50), (600, 100), (900, 60), (1200, 40),
             (1400, 90), (200, 180), (700, 140), (1100, 120), (1500, 70)]
    for sx, sy in stars:
        draw.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(255, 255, 250))


def create_cover(metadata_path: Path, output_path: Path) -> None:
    img = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(img)

    draw_gradient(draw)
    add_atmosphere(draw)
    draw_lighthouse(draw)
    draw_rocks(draw)
    draw_mermaid_silhouette(draw)
    draw_title_panel(draw)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def _standard_cover_font(name: str, size: int):
    font_dir = globals().get("FONT_DIR", globals().get("FONTS_DIR", None))
    candidates = []
    if font_dir is not None:
        candidates.append(Path(font_dir) / name)
    candidates.extend([
        Path("C:/Windows/Fonts") / name,
        Path("C:/Windows/Fonts") / "arialbd.ttf",
        Path("C:/Windows/Fonts") / "arial.ttf",
    ])
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _standard_cover_repair_text(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def _standard_cover_wrap(draw, text: str, selected_font, max_width: int) -> list[str]:
    words = text.split()
    lines = []
    current = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=selected_font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _standard_cover_center(draw, y: int, lines: list[str], selected_font, fill, line_gap: int, width: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _standard_cover_title_font(draw, title: str, max_width: int):
    for size in (116, 104, 96, 88, 80, 72):
        selected = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), selected, max_width)
        heights = [draw.textbbox((0, 0), line, font=selected)[3] - draw.textbbox((0, 0), line, font=selected)[1] for line in lines]
        total = sum(heights) + max(0, len(lines) - 1) * 18
        if len(lines) <= 4 and total <= 430:
            return selected, lines, 18
    selected = _standard_cover_font("arialbd.ttf", 68)
    return selected, _standard_cover_wrap(draw, title.upper(), selected, max_width), 16


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

def _draw_standard_cover_title_panel(image, title: str = "", author: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(3, 5, 8, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(160, 225, 209, 105), width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (244, 249, 238), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (210, 229, 221), 12, width)
def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()