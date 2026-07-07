#!/usr/bin/env python3
"""Cover: The Last Cowboy — Old cowboy with bull rope silhouetted against Nevada sunset over sagebrush plains."""

from __future__ import annotations

import argparse
import json
import math
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
    """Sunset gold to deep rust to near-black desert night gradient."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((180, 100, 40), (210, 130, 60), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((210, 130, 60), (120, 50, 30), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((120, 50, 30), (20, 10, 5), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_mountains(draw: ImageDraw, width: int, height: int) -> None:
    """Draw distant Nevada mountain silhouettes."""
    import random
    rng = random.Random(3)

    colors = [(80, 45, 35), (60, 35, 25), (40, 25, 18)]
    base_y = int(height * 0.35)

    for layer, color in enumerate(colors):
        offset_y = base_y + layer * 15
        points = []
        for x in range(0, width + 10, 10):
            h = rng.randint(30, 120) + layer * 20
            y = offset_y - h
            points.append((x, y))
        points.append((width, height))
        points.append((0, height))
        draw.polygon(points, fill=color)


def draw_arena(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a rodeo arena silhouette at the base of the mountains."""
    arena_y = int(height * 0.55)
    arena_color = (70, 40, 25)

    # Fence line
    draw.rectangle([(200, arena_y), (width - 200, arena_y + 8)], fill=arena_color)

    # Fence posts
    for x in range(220, width - 200, 60):
        draw.rectangle([(x, arena_y - 30), (x + 8, arena_y + 8)], fill=arena_color)

    # Rail
    draw.rectangle([(200, arena_y - 25), (width - 200, arena_y - 18)], fill=arena_color)
    draw.rectangle([(200, arena_y - 12), (width - 200, arena_y - 5)], fill=arena_color)


def draw_bull_chute(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a bucking chute on the left side of the arena."""
    cx, cy = int(width * 0.3), int(height * 0.48)
    chute_color = (50, 30, 20)

    # Chute frame
    draw.rectangle([(cx - 60, cy - 80), (cx + 60, cy + 20)], fill=None, outline=chute_color, width=6)

    # Chute bars
    for i in range(5):
        x = cx - 50 + i * 25
        draw.line([(x, cy - 75), (x, cy + 15)], fill=chute_color, width=4)

    # Gate
    draw.rectangle([(cx + 55, cy - 75), (cx + 65, cy + 15)], fill=(60, 35, 20))


def draw_bull(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a bull shape emerging from the chute."""
    bx, by = int(width * 0.45), int(height * 0.44)
    bull_color = (25, 15, 10)

    # Body
    draw.ellipse([(bx - 80, by - 60), (bx + 60, by + 40)], fill=bull_color)

    # Head
    draw.ellipse([(bx + 50, by - 45), (bx + 100, by)], fill=bull_color)

    # Horns
    draw.line([(bx + 75, by - 45), (bx + 95, by - 75)], fill=(40, 25, 15), width=6)
    draw.line([(bx + 85, by - 45), (bx + 105, by - 70)], fill=(40, 25, 15), width=6)

    # Eye
    draw.ellipse([(bx + 80, by - 30), (bx + 86, by - 24)], fill=(200, 50, 30))

    # Legs
    for lx in [bx - 50, bx - 20, bx + 10, bx + 30]:
        draw.rectangle([(lx, by + 30), (lx + 12, by + 70)], fill=bull_color)

    # Dust cloud
    dust_color = (180, 150, 100, 80)
    for _d in range(20):
        import random
        rng = random.Random(_d)
        dx = bx + rng.randint(-100, 100)
        dy = by + rng.randint(30, 80)
        ds = rng.randint(10, 40)
        draw.ellipse([(dx, dy), (dx + ds, dy + ds // 2)], fill=dust_color)


def draw_rodeo_lighting(draw: ImageDraw, width: int, height: int) -> None:
    """Draw arena lights beaming down from above."""
    light_color = (255, 220, 150, 30)

    # Light poles
    for lx in [200, width - 200]:
        draw.line([(lx, 50), (lx, 100)], fill=(80, 80, 80), width=6)
        draw.rectangle([(lx - 20, 80), (lx + 20, 100)], fill=(60, 60, 60))

        # Light beam (semi-transparent)
        for x in range(0, width, 4):
            beam_bottom = int(100 + (x - lx) * 0.5)
            if beam_bottom < height:
                draw.point((x, beam_bottom), fill=(255, 220, 150, 20))


def draw_sunset_sun(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a large setting sun behind the mountains."""
    sun_x, sun_y = width // 2, int(height * 0.28)
    sun_r = 100

    # Sun glow
    for r in range(sun_r + 40, sun_r - 1, -1):
        t = (r - sun_r) / 40
        alpha = max(0, int(60 * (1 - t)))
        color = (255, 200, 80, alpha)
        if r > sun_r:
            draw.ellipse([(sun_x - r, sun_y - r), (sun_x + r, sun_y + r)], fill=color)

    # Sun disc
    draw.ellipse([(sun_x - sun_r, sun_y - sun_r), (sun_x + sun_r, sun_y + sun_r)], fill=(255, 180, 60))

    # Sun highlight
    draw.ellipse([(sun_x - 60, sun_y - 60), (sun_x + 60, sun_y + 60)], fill=(255, 220, 120))


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with white text."""
    panel_top = TITLE_PANEL_TOP

    # Panel background - dark semi-transparent
    draw.rectangle([(0, panel_top), (width, height)], fill=(20, 10, 5, 220))
    draw.line([(0, panel_top), (width, panel_top)], fill=(180, 130, 60), width=3)

    # Title text
    title = "The Last\nCowboy"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    lines = title.split("\n")
    y_offset = panel_top + 70
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx, y_offset), line, fill=(255, 255, 255), font=title_font)
        y_offset += 100

    # Author name
    author = "Barış Kısır"
    author_font_size = 36
    try:
        author_font = ImageFont.truetype(str(font_paths["author"]), author_font_size)
    except Exception:
        author_font = ImageFont.load_default()

    try:
        abbox = draw.textbbox((0, 0), author, font=author_font)
        aw = abbox[2] - abbox[0]
    except Exception:
        aw = 0
    ax = (width - aw) // 2
    ay = y_offset + 40
    draw.text((ax, ay), author, fill=(220, 180, 120), font=author_font)

    # Subtitle line
    subtitle = "A CONTEMPORARY WESTERN"
    subtitle_font_size = 20
    try:
        sub_font = ImageFont.truetype(str(font_paths["author"]), subtitle_font_size)
    except Exception:
        sub_font = ImageFont.load_default()
    try:
        sbbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        sw = sbbox[2] - sbbox[0]
    except Exception:
        sw = 0
    sx = (width - sw) // 2
    draw.text((sx, ay + 45), subtitle, fill=(180, 150, 100), font=sub_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Last Cowboy")
    author = metadata.get("author", "Barış Kısır")
    model = metadata.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    rng = __import__("random").Random(11)

    # Nevada sunset: orange to sage green to black
    for y in range(HEIGHT):
        t = y / HEIGHT
        if t < 0.35:
            r, g, b = 180 + 75 * (t / 0.35), 100 + 60 * (t / 0.35), 40 + 30 * (t / 0.35)
        elif t < 0.6:
            r, g, b = 255 - 90 * ((t - 0.35) / 0.25), 160 - 80 * ((t - 0.35) / 0.25), 70 - 40 * ((t - 0.35) / 0.25)
        else:
            r, g, b = 165 - 150 * ((t - 0.6) / 0.4), 80 - 70 * ((t - 0.6) / 0.4), 30 - 25 * ((t - 0.6) / 0.4)
        draw.line([(0, y), (WIDTH, y)], fill=(max(0, int(r)), max(0, int(g)), max(0, int(b)), 255))

    # Distant Nevada mountain silhouettes
    for layer in range(3):
        offset_y = int(HEIGHT * 0.32) + layer * 12
        color = (70 - layer * 15, 40 - layer * 10, 30 - layer * 8)
        pts = [(0, HEIGHT)]
        for x in range(0, WIDTH + 10, 10):
            h = rng.randint(40, 120) + layer * 15
            pts.append((x, offset_y - h))
        pts.append((WIDTH, HEIGHT))
        draw.polygon(pts, fill=color)

    # Setting sun
    sun_x, sun_y = WIDTH // 2, int(HEIGHT * 0.26)
    for rr in range(90, 0, -3):
        draw.ellipse([sun_x - rr, sun_y - rr, sun_x + rr, sun_y + rr], fill=(255, 200 + int(55 * (1 - rr / 90)), 80, max(0, 55 - rr)))
    draw.ellipse([sun_x - 55, sun_y - 55, sun_x + 55, sun_y + 55], fill=(255, 220, 100))

    # Sagebrush plain
    draw.rectangle([(0, int(HEIGHT * 0.50)), (WIDTH, int(HEIGHT * 0.55))], fill=(60, 70, 40, 180))
    # Sagebrush clumps
    for _ in range(30):
        bx = int(rng.random() * WIDTH)
        by = int(HEIGHT * 0.50 + rng.random() * 100)
        br = 8 + int(rng.random() * 20)
        bs = int(60 + rng.random() * 40)
        draw.ellipse([bx - br, by - br // 2, bx + br, by + br // 2], fill=(40 + bs // 4, bs, 30 + bs // 6, 150))

    # Barbed wire fence
    fence_y = int(HEIGHT * 0.50)
    for fx in range(0, WIDTH, 80):
        draw.rectangle([fx, fence_y - 30, fx + 4, fence_y + 15], fill=(50, 40, 30, 200))
        draw.line([(fx, fence_y - 15), (fx + 60, fence_y - 15)], fill=(60, 50, 40, 180), width=1)
        draw.line([(fx, fence_y - 5), (fx + 60, fence_y - 5)], fill=(60, 50, 40, 180), width=1)
        draw.line([(fx, fence_y + 5), (fx + 60, fence_y + 5)], fill=(60, 50, 40, 180), width=1)
    # Barbed wire dots
    for bx in range(0, WIDTH, 20):
        draw.ellipse([bx - 1, fence_y - 16, bx + 1, fence_y - 14], fill=(80, 70, 60, 180))

    # Old cowboy silhouette with bull rope
    cw = WIDTH // 3
    cy = int(HEIGHT * 0.48)
    # Body
    draw.polygon([(cw - 20, cy), (cw + 20, cy), (cw + 15, cy + 80), (cw - 15, cy + 80)], fill=(5, 5, 5, 220))
    # Head
    draw.ellipse([cw - 12, cy - 30, cw + 12, cy - 6], fill=(5, 5, 5, 220))
    # Hat
    draw.ellipse([cw - 22, cy - 36, cw + 22, cy - 26], fill=(5, 5, 5, 220))
    draw.rectangle([cw - 14, cy - 48, cw + 14, cy - 34], fill=(5, 5, 5, 220))
    # Bull rope (coiled)
    for i in range(4):
        draw.ellipse([cw - 20 - i * 5, cy + 40 + i * 8, cw, cy + 50 + i * 8], fill=None, outline=(40, 35, 30, 200), width=3)
    # Arm holding rope
    draw.line([cw + 18, cy + 20, cw + 30, cy + 50], fill=(5, 5, 5, 220), width=5)

    # Dust particles
    for _ in range(40):
        dx = int(rng.random() * WIDTH)
        dy = int(HEIGHT * 0.45 + rng.random() * 100)
        ds = rng.randint(2, 6)
        draw.ellipse([dx - ds, dy - ds // 2, dx + ds, dy + ds // 2], fill=(180, 150, 100, rng.randint(20, 50)))

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