#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for Paper Tigers (Contemporary Fiction)."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


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
    """Warm fog-to-night gradient — dusky orange sky fading to dark warm gray."""
    for y in range(height):
        if y < height * 0.4:
            t = y / (height * 0.4)
            c = lerp_color((200, 170, 140), ((180, 120, 80)), t)
        elif y < height * 0.7:
            t = (y - height * 0.4) / (height * 0.3)
            c = lerp_color((180, 120, 80), ((100, 70, 60)), t)
        else:
            t = (y - height * 0.7) / (height * 0.3)
            c = lerp_color((100, 70, 60), ((40, 25, 25)), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_golden_gate(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a stylized Golden Gate Bridge receding into fog in the upper half."""
    import random

    rng = random.Random(17)

    bridge_y = int(height * 0.28)
    tower_x = width // 2

    # Fog layer (background)
    for i in range(3):
        fog_y = bridge_y - 20 + i * 60
        draw.ellipse(
            [tower_x - 400 - i * 50, fog_y, tower_x + 400 + i * 50, fog_y + 80],
            fill=(220, 200, 180, 30 + i * 10),
        )

    # Bridge towers
    tower_colors = [(140, 50, 40), (160, 60, 50), (150, 55, 45)]
    for offset_x, tc in zip([-250, 250], tower_colors[:2]):
        # Tower structure
        draw.rectangle([tower_x + offset_x - 12, bridge_y - 120, tower_x + offset_x + 12, bridge_y], fill=tc)
        # Cross beams
        draw.rectangle(
            [tower_x + offset_x - 25, bridge_y - 80, tower_x + offset_x + 25, bridge_y - 75], fill=(180, 70, 55)
        )
        draw.rectangle(
            [tower_x + offset_x - 25, bridge_y - 40, tower_x + offset_x + 25, bridge_y - 35], fill=(180, 70, 55)
        )
        # Top of tower
        draw.rectangle(
            [tower_x + offset_x - 18, bridge_y - 130, tower_x + offset_x + 18, bridge_y - 120], fill=(160, 60, 50)
        )

    # Suspension cables (arcs)
    for side in [-1, 1]:
        points = []
        cx = tower_x + side * 250
        for t_f in range(21):
            t = t_f / 20
            x = tower_x + side * (250 - 250 * t)
            y = bridge_y - 100 + t * (1 - t) * 200
            points.append((int(x), int(y)))
        draw.line(points, fill=(180, 120, 100, 120), width=3)

    # Vertical cables
    for i in range(8):
        x = tower_x - 240 + i * 70
        if abs(x - tower_x) < 50:
            continue
        draw.line([(x, bridge_y - 90), (x, bridge_y)], fill=(180, 120, 100, 80), width=1)

    # Fog in front of bridge
    for i in range(5):
        y = rng.randint(bridge_y - 60, bridge_y + 40)
        x0 = rng.randint(100, width - 400)
        x1 = rng.randint(x0 + 100, min(x0 + 500, width - 100))
        h = rng.randint(30, 80)
        draw.ellipse([x0, y, x1, y + h], fill=(230, 215, 195, 20 + i * 5))


def draw_chinatown_street(draw: ImageDraw, width: int, height: int) -> None:
    """Draw a Chinatown street scene with rows of buildings and shops."""
    import random

    rng = random.Random(42)

    street_y = int(height * 0.55)

    # Street / roadway
    draw.rectangle([(0, street_y), (width, height)], fill=(50, 45, 40))

    # Sidewalk
    draw.rectangle([(0, street_y - 8), (width, street_y)], fill=(80, 75, 70))

    # Building row — left side
    for i in range(6):
        bx = i * 280 + 20
        bw = 260
        bh = rng.randint(300, 450)
        by = street_y - bh

        # Building body (warm tones)
        colors = [(120, 70, 50), (140, 80, 55), (110, 60, 45), (130, 75, 52), (100, 55, 40)]
        color = colors[i % len(colors)]
        draw.rectangle([bx, by, bx + bw, street_y - 8], fill=color)

        # Roof / parapet
        draw.rectangle([bx, by - 8, bx + bw, by], fill=(80, 45, 35))

        # Windows
        for row in range(4):
            for col in range(4):
                wx = bx + 30 + col * 55
                wy = by + 40 + row * 80
                if rng.random() < 0.6:
                    # Window lit (warm yellow)
                    draw.rectangle([wx, wy, wx + 35, wy + 45], fill=(255, 220, 140))
                    draw.rectangle([wx, wy, wx + 35, wy + 45], fill=(255, 200, 100, 60))
                else:
                    # Window dark
                    draw.rectangle([wx, wy, wx + 35, wy + 45], fill=(60, 50, 45))

    # Building row — right side
    for i in range(6):
        bx = width - (i * 260 + 40) - 240
        bw = 240
        bh = rng.randint(350, 480)
        by = street_y - bh

        colors = [(130, 75, 50), (100, 58, 42), (140, 85, 58), (115, 65, 48)]
        color = colors[i % len(colors)]
        draw.rectangle([bx, by, bx + bw, street_y - 8], fill=color)

        # Roof pagoda-style edge
        draw.polygon(
            [(bx - 10, by), (bx + bw // 2, by - 25), (bx + bw + 10, by)], fill=(90, 50, 38)
        )

        # Shop sign (Chinese-style banner)
        sign_y = by + 60
        draw.rectangle([bx + 20, sign_y, bx + bw - 20, sign_y + 35], fill=(180, 40, 30))
        # Shop text placeholder (gold bars)
        for _ in range(3):
            sx = bx + 35 + rng.randint(0, 120)
            draw.rectangle([sx, sign_y + 8, sx + 20, sign_y + 24], fill=(255, 200, 50))

        # Windows
        for row in range(3):
            for col in range(3):
                wx = bx + 30 + col * 65
                wy = sign_y + 60 + row * 75
                if rng.random() < 0.5:
                    draw.rectangle([wx, wy, wx + 40, wy + 50], fill=(255, 210, 130))
                    draw.rectangle([wx, wy, wx + 40, wy + 50], fill=(255, 190, 100, 50))
                else:
                    draw.rectangle([wx, wy, wx + 40, wy + 50], fill=(55, 45, 40))


def draw_lanterns(draw: ImageDraw, width: int, height: int) -> None:
    """Draw rows of hanging red lanterns across the top of the street."""
    import random

    rng = random.Random(23)

    street_y = int(height * 0.55)

    # Lanterns hanging from strings across the street
    for row in range(2):
        string_y = street_y - rng.randint(480, 520) - row * 120
        # The string itself
        draw.line([(0, string_y), (width, string_y)], fill=(60, 40, 30), width=2)

        # Lanterns along the string
        for i in range(12):
            lx = 80 + i * 130 + rng.randint(-20, 20)
            ly = string_y + rng.randint(5, 20)
            lw = rng.randint(35, 50)
            lh = rng.randint(45, 60)

            # Lantern body (red ellipse)
            draw.ellipse([lx - lw // 2, ly, lx + lw // 2, ly + lh], fill=(200, 40, 30))
            # Gold bands top and bottom
            draw.rectangle([lx - lw // 2 + 4, ly, lx + lw // 2 - 4, ly + 6], fill=(255, 200, 50))
            draw.rectangle([lx - lw // 2 + 4, ly + lh - 6, lx + lw // 2 - 4, ly + lh], fill=(255, 200, 50))
            # Inner glow
            draw.ellipse([lx - lw // 4, ly + lh // 4, lx + lw // 4, ly + lh * 3 // 4], fill=(255, 180, 60, 100))
            # Tassel
            draw.line([(lx, ly + lh), (lx, ly + lh + 15)], fill=(200, 40, 30), width=2)
            draw.ellipse([lx - 3, ly + lh + 10, lx + 3, ly + lh + 18], fill=(200, 40, 30))

    # Scattered lanterns on buildings
    for i in range(6):
        lx = rng.randint(100, width - 100)
        ly = rng.randint(int(height * 0.15), int(height * 0.45))
        lw = 25
        lh = 32
        draw.ellipse([lx - lw // 2, ly, lx + lw // 2, ly + lh], fill=(180, 35, 25, 180))
        draw.ellipse([lx - lw // 4, ly + lh // 4, lx + lw // 4, ly + lh * 3 // 4], fill=(255, 170, 50, 80))


def draw_fog_and_atmosphere(draw: ImageDraw, width: int, height: int) -> None:
    """Add fog banks and atmospheric haze."""
    import random

    rng = random.Random(13)

    # Fog banks across the scene
    for i in range(8):
        fy = rng.randint(int(height * 0.1), int(height * 0.65))
        fw = rng.randint(300, 800)
        fh = rng.randint(40, 120)
        alpha = rng.randint(15, 40)
        x0 = rng.randint(-100, width - fw + 100)
        draw.ellipse(
            [x0, fy, x0 + fw, fy + fh],
            fill=(220, 210, 195, alpha),
        )


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark rectangular title panel at the bottom with WHITE text."""
    panel_top = TITLE_PANEL_TOP

    # Dark panel background — semi-transparent dark rectangle
    draw.rectangle([(0, panel_top), (width, height)], fill=(25, 20, 18, 220))

    # Gold accent line at top of panel
    draw.line([(80, panel_top + 10), (width - 80, panel_top + 10)], fill=(200, 160, 60), width=2)

    # Title text
    title = "Paper Tigers"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    # Draw title centered
    try:
        tbbox = draw.textbbox((0, 0), title, font=title_font)
        tw = tbbox[2] - tbbox[0]
    except Exception:
        tw = 0
    tx = (width - tw) // 2
    ty = panel_top + 80
    draw.text((tx, ty), title, fill=(255, 255, 255), font=title_font)

    # Subtitle / tagline
    tagline = "A Novel"
    tagline_font_size = 24
    try:
        tag_font = ImageFont.truetype(str(font_paths["small"]), tagline_font_size)
    except Exception:
        tag_font = ImageFont.load_default()
    try:
        tag_bbox = draw.textbbox((0, 0), tagline, font=tag_font)
        tag_w = tag_bbox[2] - tag_bbox[0]
    except Exception:
        tag_w = 0
    draw.text(((width - tag_w) // 2, ty + 100), tagline, fill=(200, 160, 60), font=tag_font)

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
    ay = ty + 165
    draw.text((ax, ay), author, fill=(255, 255, 255), font=author_font)

    # Bottom gold accent line
    draw.line([(80, height - 30), (width - 80, height - 30)], fill=(200, 160, 60), width=1)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "Paper Tigers")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Font paths — use arialbd.ttf for title (georgiab.ttf unavailable)
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }

    # Step 1: Warm foggy gradient background
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Golden Gate Bridge in fog
    draw_golden_gate(draw, WIDTH, HEIGHT)

    # Step 3: Chinatown building row
    draw_chinatown_street(draw, WIDTH, HEIGHT)

    # Step 4: Red lanterns across the scene
    draw_lanterns(draw, WIDTH, HEIGHT)

    # Step 5: Atmospheric fog
    draw_fog_and_atmosphere(draw, WIDTH, HEIGHT)

    # Step 6: Title panel (dark with white text)
    draw_title_panel(draw, WIDTH, HEIGHT, font_paths)

    # Soften slightly
    img = img.filter(ImageFilter.SMOOTH)

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

    metadata_path = rel(args.metadata)
    output_path = rel(args.out)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()