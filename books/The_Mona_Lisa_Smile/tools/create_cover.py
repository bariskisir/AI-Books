#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Mona Lisa Smile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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



ROOT = Path(__file__).resolve().parents[3]
FONTS_DIR = Path("C:/Windows/Fonts")

WIDTH, HEIGHT = 1600, 2560
TITLE_PANEL_TOP = 1920


def rel(path: str | Path) -> Path:
    p = Path(path)
    return ROOT / p if not p.is_absolute() else p


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient(draw: ImageDraw, width: int, height: int) -> None:
    """Rich burgundy-to-gold-to-black gradient for Louvre gallery atmosphere."""
    for y in range(height):
        if y < height * 0.3:
            t = y / (height * 0.3)
            c = lerp_color((15, 8, 12), ((60, 25, 30)), t)
        elif y < height * 0.6:
            t = (y - height * 0.3) / (height * 0.3)
            c = lerp_color((60, 25, 30), ((90, 60, 35)), t)
        elif y < height * 0.85:
            t = (y - height * 0.6) / (height * 0.25)
            c = lerp_color((90, 60, 35), ((40, 25, 20)), t)
        else:
            t = (y - height * 0.85) / (height * 0.15)
            c = lerp_color((40, 25, 20), ((10, 5, 8)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_museum_wall(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the burgundy fabric wall of the Salle des Etats with paneling."""
    # Wall panels
    panel_colors = [(80, 30, 35), (90, 35, 40), (75, 28, 32)]
    for i, color in enumerate(panel_colors):
        panel_x = 80 + i * 480
        draw.rectangle([panel_x, 60, panel_x + 420, 1400], fill=color, outline=(60, 20, 25), width=2)

    # Horizontal moulding
    draw.rectangle([20, 1400, width - 20, 1420], fill=(50, 18, 22))
    draw.rectangle([20, 1420, width - 20, 1425], fill=(100, 60, 45))

    # Wainscoting below
    for i in range(8):
        w_x = 40 + i * 200
        w_h = 200
        draw.rectangle([w_x, 1460, w_x + 180, 1460 + w_h], fill=(40, 20, 18), outline=(55, 28, 25), width=1)


def draw_frame(draw: ImageDraw, width: int, height: int) -> None:
    """Draw an ornate gold frame around the painting area."""
    cx, cy = width // 2, 420
    fw, fh = 420, 560

    # Frame shadow
    draw.rectangle([cx - fw // 2 - 15, cy - fh // 2 - 15, cx + fw // 2 + 15, cy + fh // 2 + 15],
                   fill=(20, 10, 8))

    # Outer frame
    draw.rectangle([cx - fw // 2 - 8, cy - fh // 2 - 8, cx + fw // 2 + 8, cy + fh // 2 + 8],
                   fill=(120, 90, 50))
    draw.rectangle([cx - fw // 2 - 5, cy - fh // 2 - 5, cx + fw // 2 + 5, cy + fh // 2 + 5],
                   fill=(160, 130, 70))
    draw.rectangle([cx - fw // 2 - 2, cy - fh // 2 - 2, cx + fw // 2 + 2, cy + fh // 2 + 2],
                   fill=(200, 170, 100))

    # Inner frame
    draw.rectangle([cx - fw // 2, cy - fh // 2, cx + fw // 2, cy + fh // 2],
                   fill=(180, 150, 80))

    # Frame corner ornaments
    corners = [
        (cx - fw // 2 - 8, cy - fh // 2 - 8),
        (cx + fw // 2 - 8, cy - fh // 2 - 8),
        (cx - fw // 2 - 8, cy + fh // 2 - 8),
        (cx + fw // 2 - 8, cy + fh // 2 - 8),
    ]
    for cx2, cy2 in corners:
        draw.ellipse([cx2 - 6, cy2 - 6, cx2 + 6, cy2 + 6], fill=(220, 190, 120))

    # Museum label plaque
    plaque_y = cy + fh // 2 + 40
    draw.rectangle([cx - 100, plaque_y, cx + 100, plaque_y + 40], fill=(50, 30, 25), outline=(100, 70, 50))
    try:
        label_font = ImageFont.truetype(str(FONTS_DIR / "arial.ttf"), 14)
        draw.text((cx, plaque_y + 10), "M U S E E   D U   L O U V R E", fill=(180, 160, 120), font=label_font, anchor="mt")
    except Exception:
        pass


def draw_mona_lisa(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized Mona Lisa silhouette inside the frame."""
    cx, cy = width // 2, 420
    fw, fh = 420, 560

    # Dark background of the painting
    paint_x1 = cx - fw // 2 + 15
    paint_y1 = cy - fh // 2 + 15
    paint_x2 = cx + fw // 2 - 15
    paint_y2 = cy + fh // 2 - 15
    draw.rectangle([paint_x1, paint_y1, paint_x2, paint_y2], fill=(40, 50, 30))

    # Background landscape suggestion
    # Sky area
    sky_h = int(fh * 0.5)
    for y in range(sky_h):
        t = y / sky_h
        c = lerp_color((55, 65, 45), (70, 80, 55), t)
        draw.line([(paint_x1, paint_y1 + y), (paint_x2, paint_y1 + y)], fill=c)

    # Path/road winding in background
    path_color = (90, 75, 50)
    draw.arc([paint_x1 + 60, paint_y1 + 60, paint_x2 - 60, paint_y1 + fh // 2],
             start=200, end=340, fill=path_color, width=6)
    draw.arc([paint_x1 + 100, paint_y1 + 80, paint_x2 - 40, paint_y1 + fh // 2 + 40],
             start=200, end=340, fill=path_color, width=4)

    # Figure silhouette - dress/shoulders
    fig_cx = cx
    fig_cy = paint_y1 + int(fh * 0.75)

    # Body / dress
    draw.polygon([
        (fig_cx - 45, fig_cy - 20),
        (fig_cx + 45, fig_cy - 20),
        (fig_cx + 55, fig_cy + 100),
        (fig_cx - 55, fig_cy + 100),
    ], fill=(60, 40, 25))

    # Head silhouette
    draw.ellipse([fig_cx - 20, fig_cy - 65, fig_cx + 20, fig_cy - 20], fill=(70, 55, 40))

    # Hair
    draw.ellipse([fig_cx - 24, fig_cy - 62, fig_cx + 24, fig_cy - 18], fill=(50, 35, 20))

    # Hands crossed
    draw.ellipse([fig_cx - 20, fig_cy + 15, fig_cx - 5, fig_cy + 30], fill=(75, 60, 45))
    draw.ellipse([fig_cx + 5, fig_cy + 15, fig_cx + 20, fig_cy + 30], fill=(75, 60, 45))

    # Veil over head
    draw.polygon([
        (fig_cx - 22, fig_cy - 55),
        (fig_cx - 30, fig_cy - 30),
        (fig_cx - 28, fig_cy + 10),
        (fig_cx - 15, fig_cy - 15),
    ], fill=(55, 50, 40, 80))

    # Varnish cracks (subtle lines)
    import random
    rng = random.Random(42)
    for _ in range(20):
        x1 = rng.randint(paint_x1 + 10, paint_x2 - 10)
        y1 = rng.randint(paint_y1 + 10, paint_y2 - 10)
        x2 = x1 + rng.randint(-15, 15)
        y2 = y1 + rng.randint(-5, 10)
        draw.line([(x1, y1), (x2, y2)], fill=(20, 20, 15, 40), width=1)


def draw_glass_barrier(draw: ImageDraw, width: int, height: int) -> None:
    """Draw the glass barrier and ropes in front of the painting."""
    cx = width // 2

    # Rope barriers - left
    for i in range(3):
        post_x = cx - 300 + i * 60
        draw.rectangle([post_x, 680, post_x + 8, 720], fill=(60, 40, 35))
        draw.ellipse([post_x - 4, 675, post_x + 12, 690], fill=(80, 55, 45))

    # Rope barriers - right
    for i in range(3):
        post_x = cx + 300 - i * 60
        draw.rectangle([post_x, 680, post_x + 8, 720], fill=(60, 40, 35))
        draw.ellipse([post_x - 4, 675, post_x + 12, 690], fill=(80, 55, 45))

    # Ropes connecting posts
    draw.line([(cx - 300, 690), (cx + 300, 690)], fill=(160, 130, 80), width=3)
    draw.line([(cx - 240, 690), (cx + 240, 690)], fill=(160, 130, 80), width=2)

    # Glass barrier (subtle reflection)
    draw.rectangle([cx - 220, 710, cx + 220, 720], fill=(150, 160, 170, 30))
    draw.line([(cx - 220, 715), (cx + 220, 715)], fill=(180, 190, 200, 40), width=1)


def draw_crowd_silhouettes(draw: ImageDraw, width: int, height: int) -> None:
    """Draw abstract crowd silhouettes suggesting museum visitors."""
    import random
    rng = random.Random(7)

    # Silhouette heads and shoulders in the lower-middle area
    base_y = 750
    for i in range(16):
        x = 200 + i * 80 + rng.randint(-15, 15)
        y_offset = rng.randint(0, 30)

        # Head
        head_size = rng.randint(10, 18)
        draw.ellipse([x - head_size // 2, base_y + y_offset - head_size,
                      x + head_size // 2, base_y + y_offset],
                     fill=(25, 20, 22))

        # Shoulders
        shoulder_w = rng.randint(20, 35)
        draw.ellipse([x - shoulder_w // 2, base_y + y_offset,
                      x + shoulder_w // 2, base_y + y_offset + 25],
                     fill=(20, 18, 20))

        # Raised phone/camera hands
        if rng.random() < 0.4:
            hx = x + rng.randint(5, 15)
            hy = base_y + y_offset - head_size - rng.randint(5, 15)
            draw.rectangle([hx - 3, hy - 8, hx + 3, hy], fill=(30, 28, 30))
            draw.rectangle([hx - 5, hy - 10, hx + 5, hy - 8], fill=(15, 15, 20))


def draw_spotlight(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a spotlight effect from above onto the painting."""
    cx = width // 2
    # Create a radial-like effect with layered translucent lines
    for y in range(0, 400, 4):
        spread = int(y * 0.4)
        alpha = max(0, 60 - int(y * 0.12))
        if alpha <= 0:
            continue
        draw.line([(cx - spread, y), (cx + spread, y)], fill=(200, 180, 140, alpha))


def draw_title_panel(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a dark title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background
    draw.rectangle([(0, panel_top), (width, height)], fill=(12, 8, 15, 230))

    # Gold accent line at top of panel
    draw.line([(80, panel_top), (width - 80, panel_top)], fill=(160, 130, 70), width=3)

    # Decorative corner marks on the accent line
    draw.rectangle([(70, panel_top - 3), (85, panel_top + 3)], fill=(180, 150, 80))
    draw.rectangle([(width - 85, panel_top - 3), (width - 70, panel_top + 3)], fill=(180, 150, 80))

    # Title text
    title = "The Mona Lisa\nSmile"
    title_font_size = 74
    title_font_path = str(FONTS_DIR / "arialbd.ttf")
    try:
        title_font = ImageFont.truetype(title_font_path, title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 60
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 85

    # Thin decorative line
    line_y = y_offset + 10
    draw.line([(width // 2 - 120, line_y), (width // 2 + 120, line_y)], fill=(160, 130, 70), width=1)

    # Author name
    author = "Barış Kısır"
    author_font_size = 34
    try:
        author_font = ImageFont.truetype(str(FONTS_DIR / "arialbd.ttf"), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    ay = line_y + 25
    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    draw.text((ax, ay), author, fill=(200, 190, 180), font=author_font)

    # Bottom decorative line
    draw.line([(80, height - 30), (width - 80, height - 30)], fill=(100, 80, 60), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Museum wall with paneling
    draw_museum_wall(draw, WIDTH, HEIGHT)

    # Step 3: Spotlight effect from ceiling
    draw_spotlight(draw, WIDTH, HEIGHT)

    # Step 4: Ornate picture frame
    draw_frame(draw, WIDTH, HEIGHT)

    # Step 5: Stylized Mona Lisa inside the frame
    draw_mona_lisa(draw, WIDTH, HEIGHT)

    # Step 6: Glass barrier and rope
    draw_glass_barrier(draw, WIDTH, HEIGHT)

    # Step 7: Crowd silhouettes
    draw_crowd_silhouettes(draw, WIDTH, HEIGHT)

    # Step 8: Title panel at bottom
    draw_title_panel(draw, WIDTH, HEIGHT)

    # Soften slightly
    img = img.filter(ImageFilter.SMOOTH)

    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()