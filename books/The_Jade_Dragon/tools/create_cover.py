#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Jade Dragon."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


WIDTH = 1600
HEIGHT = 2560
TITLE_PANEL_Y = 1920
FONTS_DIR = Path("C:/Windows/Fonts")


def load_font(name: str, size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(FONTS_DIR / name), size)
    except (IOError, OSError):
        return ImageFont.load_default()


def lerp_color(c1: tuple[int, int, int], c2: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a + (b - a) * t) for a, b in zip(c1, c2))


def draw_gradient_bg(draw: ImageDraw.ImageDraw) -> None:
    """Celadon to deep jade to crimson-black gradient for wuxia mood."""
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        if ratio < 0.4:
            t = ratio / 0.4
            c = lerp_color((180, 195, 170), (100, 140, 110), t)
        elif ratio < 0.7:
            t = (ratio - 0.4) / 0.3
            c = lerp_color((100, 140, 110), (60, 30, 35), t)
        else:
            t = (ratio - 0.7) / 0.3
            c = lerp_color((60, 30, 35), (25, 10, 15), t)
        draw.line([(0, y), (WIDTH, y)], fill=c)


def draw_bamboo(draw: ImageDraw.ImageDraw) -> None:
    """Draw bamboo stalks and leaves framing the sides."""
    # Left-side bamboo
    stalks_left = [
        (80, 0.1, 0.95, 12),
        (140, 0.15, 0.85, 10),
        (200, 0.05, 0.90, 14),
        (40, 0.2, 0.75, 8),
    ]
    for x, top_r, bot_r, width in stalks_left:
        top_y = int(HEIGHT * top_r)
        bot_y = int(HEIGHT * bot_r)
        # Stalk
        draw.line([(x, top_y), (x, bot_y)], fill=(50, 70, 55), width=width)
        # Nodes (horizontal segments)
        for ny in range(top_y, bot_y, int(HEIGHT * 0.08)):
            draw.line([(x - 6, ny), (x + 6, ny)], fill=(60, 85, 65), width=3)
        # Leaves
        for lx in range(-1, 2, 2):
            lx_off = x + lx * 10
            ly = top_y + int(HEIGHT * 0.1)
            draw.line([(x, ly), (lx_off + lx * 60, ly - 30)], fill=(40, 65, 45), width=3)
            draw.line([(x, ly + 30), (lx_off + lx * 55, ly + 5)], fill=(40, 65, 45), width=2)

    # Right-side bamboo
    stalks_right = [
        (WIDTH - 80, 0.08, 0.93, 12),
        (WIDTH - 140, 0.12, 0.88, 10),
        (WIDTH - 200, 0.03, 0.92, 14),
    ]
    for x, top_r, bot_r, width in stalks_right:
        top_y = int(HEIGHT * top_r)
        bot_y = int(HEIGHT * bot_r)
        draw.line([(x, top_y), (x, bot_y)], fill=(50, 70, 55), width=width)
        for ny in range(top_y, bot_y, int(HEIGHT * 0.08)):
            draw.line([(x - 6, ny), (x + 6, ny)], fill=(60, 85, 65), width=3)
        for lx in range(-1, 2, 2):
            lx_off = x + lx * 10
            ly = top_y + int(HEIGHT * 0.08)
            draw.line([(x, ly), (lx_off + lx * 60, ly - 25)], fill=(40, 65, 45), width=3)


def draw_martial_artist_silhouette(draw: ImageDraw.ImageDraw) -> None:
    """Draw a martial artist silhouette in a dynamic pose."""
    cx, cy = WIDTH // 2, int(HEIGHT * 0.35)
    scale = 1.0

    # Head
    head_r = int(22 * scale)
    draw.ellipse([cx - head_r, cy - head_r - 60, cx + head_r, cy + head_r - 60], fill=(15, 10, 12))

    # Topknot / hair
    draw.polygon([
        (cx - 5, cy - 60 - head_r - 10),
        (cx + 5, cy - 60 - head_r - 10),
        (cx, cy - 60 - head_r - 25),
    ], fill=(15, 10, 12))

    # Torso
    body_pts = [
        (cx - 25, cy - 35),   # left shoulder
        (cx - 30, cy + 60),   # left hip
        (cx + 30, cy + 60),   # right hip
        (cx + 25, cy - 35),   # right shoulder
    ]
    draw.polygon(body_pts, fill=(15, 10, 12))

    # Left arm - raised in crane form
    arm_pts = [
        (cx - 25, cy - 30),
        (cx - 65, cy - 60),
        (cx - 80, cy - 85),
        (cx - 75, cy - 90),
        (cx - 60, cy - 65),
        (cx - 22, cy - 35),
    ]
    draw.polygon(arm_pts, fill=(15, 10, 12))

    # Right arm - extended forward
    arm_pts2 = [
        (cx + 25, cy - 30),
        (cx + 60, cy - 25),
        (cx + 90, cy - 15),
        (cx + 92, cy - 10),
        (cx + 62, cy - 20),
        (cx + 22, cy - 28),
    ]
    draw.polygon(arm_pts2, fill=(15, 10, 12))

    # Right leg - kicking stance
    leg_pts = [
        (cx - 20, cy + 58),
        (cx - 28, cy + 110),
        (cx - 22, cy + 115),
        (cx - 14, cy + 62),
    ]
    draw.polygon(leg_pts, fill=(15, 10, 12))

    # Left leg - bent, raised
    leg_pts2 = [
        (cx + 20, cy + 58),
        (cx + 55, cy + 45),
        (cx + 65, cy + 50),
        (cx + 35, cy + 60),
    ]
    draw.polygon(leg_pts2, fill=(15, 10, 12))

    # Foot detail on raised leg
    draw.polygon([
        (cx + 55, cy + 45),
        (cx + 70, cy + 42),
        (cx + 72, cy + 48),
        (cx + 65, cy + 50),
    ], fill=(15, 10, 12))

    # Robe/sword sash
    draw.polygon([
        (cx - 28, cy + 10),
        (cx + 28, cy + 10),
        (cx + 32, cy + 25),
        (cx - 32, cy + 25),
    ], fill=(25, 18, 20))

    # Glow aura around silhouette (dragon qi)
    aura = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    aura_draw = ImageDraw.Draw(aura)
    aura_draw.ellipse(
        [cx - 120, cy - 140, cx + 120, cy + 100],
        fill=(100, 200, 150, 30),
    )
    aura_draw.ellipse(
        [cx - 90, cy - 110, cx + 90, cy + 70],
        fill=(120, 220, 160, 20),
    )
    aura = aura.filter(ImageFilter.GaussianBlur(radius=15))
    draw.bitmap((0, 0), aura, fill=None)


def draw_jade_amulet(draw: ImageDraw.ImageDraw) -> None:
    """Draw a jade amulet hanging from the silhouette's waist."""
    cx, cy = WIDTH // 2 - 28, int(HEIGHT * 0.35) + 40

    # Cord
    draw.line([(cx, cy - 15), (cx, cy + 5)], fill=(80, 50, 40), width=2)

    # Amulet disc
    draw.ellipse([cx - 12, cy - 5, cx + 12, cy + 25], fill=(120, 180, 130))
    draw.ellipse([cx - 8, cy - 1, cx + 8, cy + 21], fill=(140, 200, 150))

    # Dragon character on amulet
    char_font = load_font("arial.ttf", 16)
    draw.text((cx - 5, cy + 4), "龍", fill=(50, 90, 60), font=char_font)

    # Glow
    for r in range(3):
        glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gdraw = ImageDraw.Draw(glow)
        gdraw.ellipse(
            [cx - 20 - r * 5, cy - 12 - r * 5, cx + 20 + r * 5, cy + 32 + r * 5],
            fill=(100, 200, 120, 25 - r * 5),
        )
        glow = glow.filter(ImageFilter.GaussianBlur(radius=5))
        draw.bitmap((0, 0), glow, fill=None)


def draw_dragon_mist(draw: ImageDraw.ImageDraw) -> None:
    """Draw faint misty dragon shapes in the upper background."""
    cx, cy = WIDTH // 2 + 150, int(HEIGHT * 0.15)

    # Misty dragon body - serpentine curve
    pts = []
    for t in range(0, 360, 10):
        rad = math.radians(t)
        r = 80 + math.sin(rad * 3) * 20
        px = cx + math.cos(rad) * r * 0.4
        py = cy + math.sin(rad) * r * 0.3 - 20
        pts.append((int(px), int(py)))

    mist = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(mist)
    if len(pts) > 1:
        mdraw.line(pts, fill=(140, 200, 160, 40), width=8)
        mdraw.line(pts, fill=(160, 220, 170, 20), width=15)
    mist = mist.filter(ImageFilter.GaussianBlur(radius=6))
    draw.bitmap((0, 0), mist, fill=None)

    # Second smaller dragon on the left
    cx2, cy2 = WIDTH // 2 - 180, int(HEIGHT * 0.12)
    pts2 = []
    for t in range(0, 360, 10):
        rad = math.radians(t)
        r = 50 + math.sin(rad * 2) * 15
        px = cx2 + math.cos(rad) * r * 0.4
        py = cy2 + math.sin(rad) * r * 0.3
        pts2.append((int(px), int(py)))

    mist2 = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    mdraw2 = ImageDraw.Draw(mist2)
    if len(pts2) > 1:
        mdraw2.line(pts2, fill=(100, 200, 150, 35), width=6)
    mist2 = mist2.filter(ImageFilter.GaussianBlur(radius=4))
    draw.bitmap((0, 0), mist2, fill=None)


def draw_mountains(draw: ImageDraw.ImageDraw) -> None:
    """Draw distant mountain silhouettes in the background."""
    layers = [
        (int(HEIGHT * 0.65), (60, 80, 65, 60)),
        (int(HEIGHT * 0.70), (45, 60, 50, 80)),
        (int(HEIGHT * 0.75), (30, 40, 35, 100)),
    ]

    for base_y, color in layers:
        pts = [(0, base_y)]
        for x in range(0, WIDTH + 30, 30):
            h = math.sin(x / 300) * 80 + math.sin(x / 150) * 30 + math.sin(x / 50) * 10
            pts.append((x, base_y - abs(h)))
        pts.append((WIDTH, HEIGHT))
        pts.append((0, HEIGHT))
        draw.polygon(pts, fill=color)


def draw_title_panel(draw: ImageDraw.ImageDraw, title: str, author: str) -> None:
    """Draw dark title panel at bottom with white text."""
    # Dark panel background
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, HEIGHT], fill=(20, 15, 18))

    # Subtle border line at top
    draw.rectangle([0, TITLE_PANEL_Y, WIDTH, TITLE_PANEL_Y + 2], fill=(60, 50, 45))

    # Decorative line
    line_y = TITLE_PANEL_Y + 55
    draw.line([(WIDTH // 4, line_y), (WIDTH * 3 // 4, line_y)], fill=(120, 180, 130, 150), width=1)

    # Title font - use arialbd.ttf
    title_font = load_font("arialbd.ttf", 72)
    subtitle_font = load_font("arialbd.ttf", 52)
    author_font = load_font("arial.ttf", 36)

    # Title rendering - handle potential wrapping
    lines = title.split(" ")
    if len(lines) <= 2:
        line1 = title
        line2 = None
    else:
        mid = len(lines) // 2
        line1 = " ".join(lines[:mid])
        line2 = " ".join(lines[mid:])

    if line2:
        bbox1 = draw.textbbox((0, 0), line1, font=subtitle_font)
        tw1 = bbox1[2] - bbox1[0]
        tx1 = (WIDTH - tw1) // 2
        draw.text((tx1, TITLE_PANEL_Y + 70), line1, fill=(255, 255, 255), font=subtitle_font)

        bbox2 = draw.textbbox((0, 0), line2, font=subtitle_font)
        tw2 = bbox2[2] - bbox2[0]
        tx2 = (WIDTH - tw2) // 2
        draw.text((tx2, TITLE_PANEL_Y + 130), line2, fill=(255, 255, 255), font=subtitle_font)
        author_y = TITLE_PANEL_Y + 210
    else:
        bbox = draw.textbbox((0, 0), title, font=title_font)
        tw = bbox[2] - bbox[0]
        tx = (WIDTH - tw) // 2
        draw.text((tx, TITLE_PANEL_Y + 75), title, fill=(255, 255, 255), font=title_font)
        author_y = TITLE_PANEL_Y + 200

    # Decorative line below title
    line2_y = author_y - 15
    draw.line([(WIDTH // 3, line2_y), (WIDTH * 2 // 3, line2_y)], fill=(120, 180, 130, 120), width=1)

    # Author
    abbox = draw.textbbox((0, 0), author, font=author_font)
    aw = abbox[2] - abbox[0]
    ax = (WIDTH - aw) // 2
    draw.text((ax, author_y), author, fill=(180, 200, 180), font=author_font)

    # Genre text at very bottom
    genre_font = load_font("arial.ttf", 20)
    genre_text = "Wuxia Fantasy"
    gbbox = draw.textbbox((0, 0), genre_text, font=genre_font)
    gw = gbbox[2] - gbbox[0]
    gx = (WIDTH - gw) // 2
    draw.text((gx, TITLE_PANEL_Y + 530), genre_text, fill=(120, 150, 130), font=genre_font)



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

    with open(args.metadata, encoding="utf-8") as f:
        meta = json.load(f)

    title = meta.get("title", "The Jade Dragon")
    author = meta.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # 1. Gradient background
    draw_gradient_bg(draw)

    # 2. Distant mountains
    draw_mountains(draw)

    # 3. Misty dragon shapes
    draw_dragon_mist(draw)

    # 4. Bamboo forest framing
    draw_bamboo(draw)

    # 5. Martial artist silhouette
    draw_martial_artist_silhouette(draw)

    # 6. Jade amulet
    draw_jade_amulet(draw)

    # 7. Soften image slightly
    img = img.filter(ImageFilter.SMOOTH)

    # 8. Title panel (drawn on top, sharp)
    draw = ImageDraw.Draw(img)
    draw_title_panel(draw, title, author)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()