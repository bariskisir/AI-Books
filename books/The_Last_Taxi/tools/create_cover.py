#!/usr/bin/env python3
"""Create a project-local raster cover for The Last Taxi — Istanbul dusk with taxi and minaret."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for candidate in [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw.ImageDraw, text: str, selected_font: ImageFont.FreeTypeFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
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


def centered(draw: ImageDraw.ImageDraw, y: int, lines: list[str], selected_font: ImageFont.FreeTypeFont,
             fill: tuple[int, int, int], gap: int) -> int:
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (W - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata.get("author", "Barış Kısır")
    rng = random.Random(title)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Dusk gradient: deep warm orange at horizon rising to deep indigo at top.
    for y in range(H):
        t = y / (H - 1)
        if t < 0.6:
            # Upper sky: indigo to deep blue
            u = t / 0.6
            r = int(15 + 25 * u)
            g = int(10 + 35 * u)
            b = int(45 + 30 * u)
        else:
            # Lower sky: blue to gold-orange dusk
            u = (t - 0.6) / 0.4
            r = int(40 + 180 * u)
            g = int(45 + 130 * u)
            b = int(75 - 55 * u)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    # Sun glow near horizon
    glow_center_y = int(H * 0.65)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((W // 2 - 300, glow_center_y - 200, W // 2 + 300, glow_center_y + 150),
               fill=(255, 200, 100, 80))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    img = Image.alpha_composite(img, glow)

    # Faint stars in upper sky
    draw = ImageDraw.Draw(img, "RGBA")
    for _ in range(180):
        sx = rng.randrange(0, W)
        sy = rng.randrange(0, int(H * 0.4))
        s = rng.choice([1, 1, 2])
        b = rng.randrange(100, 200)
        draw.ellipse((sx, sy, sx + s, sy + s), fill=(b, b, b, 180))

    # Minaret silhouettes on the horizon
    horizon_y = int(H * 0.65)
    minarets_data = [
        (120, horizon_y, 22, 340),    # left minaret
        (280, horizon_y, 18, 280),     # shorter minaret
        (W - 200, horizon_y, 22, 360), # right minaret
        (W - 80, horizon_y, 16, 220),  # small right minaret
    ]
    for mx, my, mw, mh in minarets_data:
        # Main shaft
        draw.rectangle((mx - mw // 2, my - mh, mx + mw // 2, my), fill=(10, 8, 12, 255))
        # Cone top
        draw.polygon([(mx - mw // 2 - 4, my - mh), (mx, my - mh - 40), (mx + mw // 2 + 4, my - mh)],
                     fill=(10, 8, 12, 255))
        # Balcony ledge
        draw.rectangle((mx - mw // 2 - 8, my - mh + 20, mx + mw // 2 + 8, my - mh + 30),
                       fill=(10, 8, 12, 255))

    # Mosque dome silhouette between minarets
    dome_cx = 200
    dome_base = horizon_y
    draw.pieslice((dome_cx - 120, dome_base - 130, dome_cx + 120, dome_base + 20),
                  180, 360, fill=(10, 8, 12, 255))

    # City skyline silhouette — buildings along the horizon
    skyline = [(0, horizon_y)]
    x = 0
    while x <= W:
        bh = rng.randint(30, 120)
        bw = rng.randint(30, 90)
        # Skip where minarets already are
        if not (80 < x < 350 or W - 250 < x < W - 50):
            skyline.append((x, horizon_y - bh))
            skyline.append((x + bw, horizon_y - bh))
        else:
            skyline.append((x, horizon_y))
        x += bw + rng.randint(5, 20)
    skyline.append((W, horizon_y))
    skyline.append((W, H))
    skyline.append((0, H))
    draw.polygon(skyline, fill=(10, 8, 12, 255))

    # Draw silhouette dome of Süleymaniye (large central)
    draw.pieslice((W // 2 - 200, horizon_y - 220, W // 2 + 200, horizon_y + 20),
                  180, 360, fill=(10, 8, 12, 255))
    # Central minarets
    for offset in [-130, 130]:
        draw.rectangle((W // 2 + offset - 14, horizon_y - 400, W // 2 + offset + 14, horizon_y),
                       fill=(10, 8, 12, 255))
        draw.polygon([(W // 2 + offset - 18, horizon_y - 400), (W // 2 + offset, horizon_y - 440),
                       (W // 2 + offset + 18, horizon_y - 400)], fill=(10, 8, 12, 255))

    # Bosphorus water below horizon
    water_y = horizon_y + 10
    for y in range(water_y, int(H * 0.78)):
        t = (y - water_y) / (int(H * 0.78) - water_y)
        r = int(40 + 15 * t)
        g = int(52 + 20 * t)
        b = int(70 + 15 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 200))

    # Water reflection lines
    for _ in range(40):
        rx = rng.randrange(0, W)
        ry = rng.randrange(water_y, int(H * 0.77))
        rw = rng.randrange(20, 120)
        alpha = rng.randrange(30, 80)
        draw.line((rx, ry, rx + rw, ry), fill=(255, 200, 100, alpha), width=1)

    # Moon crescent
    moon_cx = 1100
    moon_cy = 200
    moon_r = 45
    draw.ellipse((moon_cx - moon_r, moon_cy - moon_r, moon_cx + moon_r, moon_cy + moon_r),
                 fill=(240, 230, 200, 200))
    # Shadow to create crescent
    draw.ellipse((moon_cx + 15, moon_cy - moon_r - 10, moon_cx + moon_r + 25, moon_cy + moon_r + 10),
                 fill=(20, 18, 40, 255))

    # Road / street in foreground
    road_y = int(H * 0.78)
    for y in range(road_y, int(H * 0.85)):
        t = (y - road_y) / (int(H * 0.85) - road_y)
        r = int(30 - 15 * t)
        g = int(30 - 15 * t)
        b = int(35 - 18 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Road lane markings
    for lx in range(50, W - 50, 80):
        draw.rectangle((lx, road_y + 60, lx + 30, road_y + 66), fill=(80, 85, 60, 120))

    # TAXI — a yellow taxi silhouette on the road
    taxi_y = road_y - 30
    taxi_x = W // 2 - 60

    # Taxi body
    draw.rectangle((taxi_x, taxi_y + 15, taxi_x + 120, taxi_y + 55), fill=(220, 185, 40, 240))
    # Taxi roof
    draw.rectangle((taxi_x + 20, taxi_y, taxi_x + 100, taxi_y + 15), fill=(210, 175, 35, 240))
    # Taxi sign on roof (Taksi)
    draw.rectangle((taxi_x + 40, taxi_y - 12, taxi_x + 80, taxi_y - 2), fill=(40, 180, 60, 255))
    # Windows
    draw.rectangle((taxi_x + 25, taxi_y + 2, taxi_x + 48, taxi_y + 14), fill=(60, 80, 120, 200))
    draw.rectangle((taxi_x + 72, taxi_y + 2, taxi_x + 95, taxi_y + 14), fill=(60, 80, 120, 200))
    # Front windshield
    draw.rectangle((taxi_x + 100, taxi_y + 2, taxi_x + 115, taxi_y + 14), fill=(60, 80, 120, 200))
    # Wheels
    draw.ellipse((taxi_x + 15, taxi_y + 45, taxi_x + 35, taxi_y + 65), fill=(20, 20, 20, 255))
    draw.ellipse((taxi_x + 85, taxi_y + 45, taxi_x + 105, taxi_y + 65), fill=(20, 20, 20, 255))
    # Headlights
    draw.ellipse((taxi_x + 115, taxi_y + 18, taxi_x + 125, taxi_y + 28), fill=(255, 240, 200, 250))
    # Headlight beam
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam)
    bd.polygon([(taxi_x + 125, taxi_y + 18), (W, taxi_y - 80), (W, taxi_y + 80), (taxi_x + 125, taxi_y + 28)],
               fill=(255, 240, 200, 25))
    beam = beam.filter(ImageFilter.GaussianBlur(15))
    img = Image.alpha_composite(img, beam)

    # Street lamps along road
    for lamppost_x in [150, 450, 750, 1050, 1350]:
        draw.line((lamppost_x, road_y, lamppost_x, road_y - 60), fill=(50, 50, 50, 200), width=4)
        draw.ellipse((lamppost_x - 8, road_y - 70, lamppost_x + 8, road_y - 56), fill=(255, 220, 120, 200))
        # Lamp glow
        lp_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        lg = ImageDraw.Draw(lp_glow)
        lg.ellipse((lamppost_x - 40, road_y - 110, lamppost_x + 40, road_y - 20),
                   fill=(255, 220, 120, 30))
        lp_glow = lp_glow.filter(ImageFilter.GaussianBlur(20))
        img = Image.alpha_composite(img, lp_glow)

    # --- Bottom panel for title ---
    draw = ImageDraw.Draw(img, "RGBA")
    panel_y = 1920
    draw.rectangle((0, panel_y, W, H), fill=(8, 6, 10, 235))
    # Gold accent line
    draw.line((300, panel_y + 18, W - 300, panel_y + 18), fill=(200, 170, 70, 180), width=2)

    # Title
    title_font = font("arialbd.ttf", 100)
    author_font = font("arialbd.ttf", 40)

    y = panel_y + 80
    title_lines = wrap(draw, title.upper(), title_font, 1300)
    y = centered(draw, y, title_lines, title_font, (255, 255, 255), 12)
    y += 60
    centered(draw, y, [author], author_font, (200, 180, 100), 8)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(output_path, "PNG", optimize=True)



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
    metadata_path = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    output_path = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(metadata_path, output_path)


if __name__ == "__main__":
    main()