#!/usr/bin/env python3
"""Create a 1600x2560 PNG cover for The Bridge of Sighs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("Install Pillow: pip install Pillow")


WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920
BG_COLOR_TOP = (20, 60, 80)       # dark teal
BG_COLOR_BOT = (180, 150, 50)     # Venetian gold
PANEL_COLOR = (10, 20, 30)        # near-black for bottom panel


def find_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arialbd.ttf",
        "C:/Windows/Fonts/Arial Bold.ttf",
        "/usr/share/fonts/truetype/msttcorefonts/Arial_Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "arialbd.ttf",
        "Arial.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def draw_gradient(draw: ImageDraw.ImageDraw) -> None:
    """Draw a vertical gradient from BG_COLOR_TOP to BG_COLOR_BOT."""
    for y in range(TITLE_PANEL_TOP):
        ratio = y / TITLE_PANEL_TOP
        r = int(BG_COLOR_TOP[0] + (BG_COLOR_BOT[0] - BG_COLOR_TOP[0]) * ratio)
        g = int(BG_COLOR_TOP[1] + (BG_COLOR_BOT[1] - BG_COLOR_TOP[1]) * ratio)
        b = int(BG_COLOR_TOP[2] + (BG_COLOR_BOT[2] - BG_COLOR_TOP[2]) * ratio)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_canal(draw: ImageDraw.ImageDraw) -> None:
    """Draw a stylized canal with reflections."""
    canal_y = 700
    canal_h = 300
    # Canal water
    water_color = (30, 80, 60, 180)
    for y in range(canal_y, canal_y + canal_h):
        alpha = int(180 * (1 - abs(y - canal_y - canal_h // 2) / (canal_h // 2)))
        r = max(0, 20 - alpha // 10)
        g = min(255, 80 + alpha // 4)
        b = max(0, 60 - alpha // 10)
        draw.line([(100, y), (WIDTH - 100, y)], fill=(r, g, b))

    # Ripples
    for i in range(6):
        rx = 200 + i * 220
        ry = canal_y + 40 + i * 40
        draw.ellipse([rx - 30, ry - 5, rx + 30, ry + 5], outline=(180, 200, 150, 100), width=2)

    # Gondola silhouette
    gx, gy = 700, canal_y + canal_h // 2 + 20
    draw.ellipse([gx - 60, gy, gx + 60, gy + 12], fill=(40, 40, 50))
    draw.polygon([(gx - 55, gy), (gx + 55, gy), (gx + 30, gy - 30), (gx - 20, gy - 30)], fill=(50, 50, 60))
    # Gondolier
    draw.ellipse([gx + 10, gy - 55, gx + 30, gy - 38], fill=(200, 180, 160))
    draw.rectangle([gx + 12, gy - 38, gx + 28, gy - 5], fill=(180, 160, 140))
    # Oar
    draw.line([(gx - 40, gy - 10), (gx - 80, gy - 60)], fill=(120, 100, 80), width=4)


def draw_palace(draw: ImageDraw.ImageDraw) -> None:
    """Draw a stylized Doge's Palace silhouette."""
    px, py = 250, 300
    pw, ph = 1100, 450

    # Palace base
    draw.rectangle([px, py + 100, px + pw, py + ph], fill=(200, 170, 130))

    # Arcade (lower level)
    for i in range(18):
        ax = px + 30 + i * 60
        draw.rectangle([ax, py + 300, ax + 40, py + ph], fill=(160, 130, 90))
        draw.arc([ax - 5, py + 300, ax + 5, py + 320], 180, 0, fill=(140, 110, 70), width=2)

    # Upper facade - Gothic windows
    for i in range(12):
        wx = px + 50 + i * 92
        wy = py + 120
        draw.polygon([(wx + 10, wy + 100), (wx + 10, wy + 20),
                       (wx + 40, wy), (wx + 70, wy + 20),
                       (wx + 70, wy + 100)], fill=(100, 80, 50))
        draw.rectangle([wx + 15, wy + 30, wx + 65, wy + 100], fill=(40, 60, 80))

    # Roofline - crenellations
    for i in range(30):
        cx = px + i * 37
        cy = py + 40
        draw.rectangle([cx, cy - 20, cx + 20, cy], fill=(180, 150, 110))
        # Pointed merlons
        if i % 2 == 0:
            draw.polygon([(cx, cy - 20), (cx + 10, cy - 40), (cx + 20, cy - 20)], fill=(160, 130, 90))

    # Center rosette
    draw.ellipse([px + pw // 2 - 40, py + 140, px + pw // 2 + 40, py + 220], fill=(180, 120, 50))
    draw.ellipse([px + pw // 2 - 30, py + 150, px + pw // 2 + 30, py + 210], fill=(100, 70, 40))
    # Cross on rosette
    draw.line([(px + pw // 2, py + 140), (px + pw // 2, py + 120)], fill=(200, 170, 100), width=4)
    draw.line([(px + pw // 2 - 15, py + 130), (px + pw // 2 + 15, py + 130)], fill=(200, 170, 100), width=4)


def draw_paintings(draw: ImageDraw.ImageDraw) -> None:
    """Draw stylized framed paintings floating near the palace."""
    frames = [
        (900, 200, 200, 160),
        (1180, 280, 180, 140),
        (150, 450, 160, 130),
    ]
    colors = [
        (140, 100, 60),
        (180, 140, 80),
        (120, 90, 50),
    ]
    paints = [
        [(160, 120, 80), (100, 80, 50), (200, 180, 140)],
        [(120, 90, 60), (180, 140, 100), (80, 60, 40)],
        [(140, 110, 70), (100, 70, 40), (190, 160, 120)],
    ]
    for idx, (fx, fy, fw, fh) in enumerate(frames):
        # Frame
        draw.rectangle([fx, fy, fx + fw, fy + fh], outline=(160, 130, 80), width=6)
        draw.rectangle([fx + 8, fy + 8, fx + fw - 8, fy + fh - 8], fill=colors[idx])
        # Abstract painting content
        for _ in range(5):
            sx = fx + 20 + (_ * 30) % (fw - 40)
            sy = fy + 20 + (_ * 25) % (fh - 40)
            c = paints[idx][_ % len(paints[idx])]
            draw.ellipse([sx, sy, sx + 30, sy + 25], fill=c, outline=None)
        # Star of the cipher floating over one painting
        if idx == 0:
            star_cx = fx + fw // 2
            star_cy = fy - 20
            for pt in range(7):
                angle = pt * (360 / 7) - 90
                import math
                ang_rad = math.radians(angle)
                sx2 = star_cx + int(25 * math.cos(ang_rad))
                sy2 = star_cy + int(25 * math.sin(ang_rad))
                nx = star_cx + int(30 * math.cos(ang_rad))
                ny = star_cy + int(30 * math.sin(ang_rad))
                draw.line([(sx2, sy2), (nx, ny)], fill=(220, 200, 100), width=3)


def draw_title_panel(draw: ImageDraw.ImageDraw) -> None:
    """Draw the dark bottom panel with title and author."""
    # Panel background
    draw.rectangle([(0, TITLE_PANEL_TOP), (WIDTH, HEIGHT)], fill=PANEL_COLOR)

    # Gold accent line at top of panel
    draw.rectangle([(200, TITLE_PANEL_TOP), (WIDTH - 200, TITLE_PANEL_TOP + 4)], fill=(180, 150, 50))

    # Title
    title_font = find_font(72)
    title = "The Bridge"
    subtitle = "of Sighs"
    author_font = find_font(36)

    # Center the title
    try:
        tb = title_font.getbbox(title)
        tw = tb[2] - tb[0]
    except AttributeError:
        tw, _ = title_font.getsize(title)
    tx = (WIDTH - tw) // 2
    draw.text((tx, TITLE_PANEL_TOP + 50), title, fill=(255, 255, 255), font=title_font)

    try:
        tb = title_font.getbbox(subtitle)
        sw = tb[2] - tb[0]
    except AttributeError:
        sw, _ = title_font.getsize(subtitle)
    sx = (WIDTH - sw) // 2
    draw.text((sx, TITLE_PANEL_TOP + 140), subtitle, fill=(255, 255, 255), font=title_font)

    # Author
    author = "Barış Kısır"
    try:
        ab = author_font.getbbox(author)
        aw = ab[2] - ab[0]
    except AttributeError:
        aw, _ = author_font.getsize(author)
    ax = (WIDTH - aw) // 2
    draw.text((ax, TITLE_PANEL_TOP + 260), author, fill=(180, 150, 50), font=author_font)

    # Bottom gold accent
    draw.rectangle([(400, HEIGHT - 60), (WIDTH - 400, HEIGHT - 56)], fill=(180, 150, 50))

    # Small decorative elements at bottom corners
    for cx, cy in [(80, HEIGHT - 100), (WIDTH - 80, HEIGHT - 100)]:
        draw.polygon([(cx, cy), (cx + 10, cy - 30), (cx + 20, cy)], fill=(180, 150, 50))
        draw.polygon([(cx, cy), (cx + 10, cy + 30), (cx + 20, cy)], fill=(180, 150, 50))


def generate(metadata_path: Path, output_path: Path) -> None:
    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Build layers
    draw_gradient(draw)
    draw_palace(draw)
    draw_canal(draw)
    draw_paintings(draw)
    draw_title_panel(draw)

    # Save
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
    parser.add_argument("--metadata", type=Path, default=None, help="Metadata JSON path (unused but accepted)")
    parser.add_argument("--out", type=Path, default=Path("The_Bridge_of_Sighs/covers/The_Bridge_of_Sighs.png"))
    args = parser.parse_args()

    out = args.out
    meta = args.metadata

    if meta and meta.exists():
        with open(meta) as f:
            data = json.load(f)
            # Override output from metadata if provided
            cover_path = data.get("paths", {}).get("cover_path")
            if cover_path and not args.out:
                out = Path(cover_path)

    generate(meta if meta else Path(), out)


if __name__ == "__main__":
    main()