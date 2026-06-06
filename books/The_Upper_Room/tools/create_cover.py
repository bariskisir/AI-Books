#!/usr/bin/env python3
"""Cover: The Upper Room — a Victorian apartment building with a lit window and fog."""

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
    for candidate in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
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


def centered(draw: ImageDraw.ImageDraw, y: int, lines: list[str], selected_font: ImageFont.FreeTypeFont, fill: tuple[int, int, int], gap: int) -> int:
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

    # Night sky gradient — deep navy at zenith to dark grey-purple at horizon.
    for y in range(H):
        t = y / (H - 1)
        if t < 0.6:
            # Dark navy top
            r = int(8 + 4 * t / 0.6)
            g = int(6 + 8 * t / 0.6)
            b = int(22 + 20 * t / 0.6)
        else:
            # Transition to murky grey-purple
            s = (t - 0.6) / 0.4
            r = int(12 + 30 * s)
            g = int(14 + 22 * s)
            b = int(42 - 10 * s)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Faint stars scattered in the upper half.
    star_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(star_layer)
    for _ in range(180):
        sx = rng.randrange(0, W)
        sy = rng.randrange(0, 900)
        s = rng.choice([1, 1, 2])
        b = rng.randrange(60, 130)
        sd.ellipse((sx, sy, sx + s, sy + s), fill=(b, b, min(255, b + 30), 160))
    star_layer = star_layer.filter(ImageFilter.GaussianBlur(0.4))
    img = Image.alpha_composite(img, star_layer)
    draw = ImageDraw.Draw(img, "RGBA")

    # Moon behind fog — pale disc near upper right.
    moon_cx, moon_cy = 1280, 340
    moon = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(moon)
    md.ellipse((moon_cx - 70, moon_cy - 70, moon_cx + 70, moon_cy + 70), fill=(200, 210, 230, 90))
    moon = moon.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, moon)
    draw = ImageDraw.Draw(img, "RGBA")
    draw.ellipse((moon_cx - 35, moon_cy - 35, moon_cx + 35, moon_cy + 35), fill=(220, 225, 240, 180))

    # Victorian apartment building silhouette.
    building_base = 1850
    building_left = 250
    building_right = 1350
    building_width = building_right - building_left

    # Main building body.
    draw.rectangle((building_left, 500, building_right, building_base),
                   fill=(12, 10, 15, 240))

    # Roof line with cornice and parapet details.
    draw.rectangle((building_left - 20, 490, building_right + 20, 520),
                   fill=(15, 12, 18, 245))
    draw.rectangle((building_left - 10, 470, building_right + 10, 490),
                   fill=(14, 11, 17, 245))

    # Upper decorative cornice.
    for cx in range(building_left, building_right, 60):
        draw.polygon([(cx, 470), (cx + 30, 440), (cx + 60, 470)],
                     fill=(18, 15, 22, 240))

    # Bay windows — three vertical rows.
    window_w, window_h = 70, 100
    window_gap_x = 120
    window_gap_y = 160
    start_x = building_left + 80
    start_y = 580

    for row in range(7):
        for col in range(3):
            wx = start_x + col * window_gap_x
            wy = start_y + row * window_gap_y
            if row == 6:
                # Ground floor taller windows
                wh = 140
            else:
                wh = window_h

            # Window frame
            draw.rectangle((wx, wy, wx + window_w, wy + wh),
                           fill=(8, 7, 12, 240))
            # Window panes (cross)
            draw.line((wx + window_w // 2, wy, wx + window_w // 2, wy + wh),
                      fill=(20, 18, 26, 200), width=2)
            draw.line((wx, wy + wh // 2, wx + window_w, wy + wh // 2),
                      fill=(20, 18, 26, 200), width=2)

    # One lit window — third row, center column.
    lit_wx = start_x + 1 * window_gap_x
    lit_wy = start_y + 2 * window_gap_y
    # Warm glow inside
    draw.rectangle((lit_wx + 2, lit_wy + 2, lit_wx + window_w - 2, lit_wy + window_h - 2),
                   fill=(230, 196, 120, 220))
    draw.line((lit_wx + window_w // 2, lit_wy + 2, lit_wx + window_w // 2, lit_wy + window_h - 2),
              fill=(40, 35, 20, 200), width=2)
    draw.line((lit_wx + 2, lit_wy + window_h // 2, lit_wx + window_w - 2, lit_wy + window_h // 2),
              fill=(40, 35, 20, 200), width=2)

    # Light spill around the lit window.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gd.ellipse((lit_wx - 40, lit_wy - 40, lit_wx + window_w + 40, lit_wy + window_h + 40),
               fill=(230, 200, 140, 60))
    glow = glow.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, glow)
    draw = ImageDraw.Draw(img, "RGBA")

    # Entrance door at ground level.
    door_x = building_left + building_width // 2 - 40
    door_y = building_base - 140
    draw.rectangle((door_x, door_y, door_x + 80, building_base),
                   fill=(8, 6, 12, 245))
    # Door arch
    draw.arc((door_x, door_y - 40, door_x + 80, door_y + 40), 180, 360,
             fill=(8, 6, 12, 245), width=80)
    # Door light
    draw.ellipse((door_x + 30, door_y + 20, door_x + 50, door_y + 50),
                 fill=(200, 190, 170, 60))

    # Street lamps on each side.
    for lamp_x in [building_left - 60, building_right + 60]:
        draw.rectangle((lamp_x - 3, building_base - 100, lamp_x + 3, building_base + 20),
                       fill=(25, 22, 30, 240))
        glow2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g2d = ImageDraw.Draw(glow2)
        g2d.ellipse((lamp_x - 25, building_base - 130, lamp_x + 25, building_base - 80),
                    fill=(255, 220, 150, 50))
        glow2 = glow2.filter(ImageFilter.GaussianBlur(15))
        img = Image.alpha_composite(img, glow2)
        draw = ImageDraw.Draw(img, "RGBA")
        draw.ellipse((lamp_x - 6, building_base - 120, lamp_x + 6, building_base - 100),
                     fill=(255, 220, 150, 180))

    # Fog layers.
    fog = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    fd = ImageDraw.Draw(fog)
    for _ in range(40):
        fx = rng.randrange(0, W)
        fy = rng.randrange(400, 1800)
        fr = rng.randrange(60, 200)
        fa = rng.randrange(12, 30)
        fd.ellipse((fx - fr, fy - fr // 2, fx + fr, fy + fr // 2),
                   fill=(180, 190, 210, fa))
    fog = fog.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, fog)
    draw = ImageDraw.Draw(img, "RGBA")

    # Lower fog bank near ground.
    fog2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    f2d = ImageDraw.Draw(fog2)
    for _ in range(25):
        fx = rng.randrange(0, W)
        fy = rng.randrange(1600, 2000)
        fr = rng.randrange(120, 300)
        fa = rng.randrange(15, 35)
        f2d.ellipse((fx - fr, fy - fr // 3, fx + fr, fy + fr // 3),
                    fill=(200, 210, 230, fa))
    fog2 = fog2.filter(ImageFilter.GaussianBlur(25))
    img = Image.alpha_composite(img, fog2)
    draw = ImageDraw.Draw(img, "RGBA")

    # Title panel at bottom.
    draw.rectangle((0, 1920, W, H), fill=(10, 8, 14, 240))
    # Subtle decorative line above panel.
    draw.line((200, 1920, W - 200, 1920), fill=(100, 90, 130, 60), width=2)
    # Decorative line below panel area.
    draw.line((200, H - 160, W - 200, H - 160), fill=(100, 90, 130, 40), width=1)

    title_font = font("georgiab.ttf", 100)
    author_font = font("arialbd.ttf", 40)
    tag_font = font("arial.ttf", 26)

    y = 1990
    y = centered(draw, y, ["A GHOST STORY"], tag_font, (150, 140, 170), 6)
    y += 40
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1100), title_font, (210, 200, 220), 14)
    y += 80
    centered(draw, y, [author], author_font, (170, 160, 190), 6)

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