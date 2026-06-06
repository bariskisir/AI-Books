#!/usr/bin/env python3
"""Generate a 1600x2560 PNG cover for The Eighth Summit."""

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
    """Thin cold high-altitude sky: deep steel-blue at the zenith down to a pale
    band, with a high band of pink alpenglow low in the sky."""
    for y in range(height):
        if y < height * 0.30:
            t = y / (height * 0.30)
            c = lerp_color((18, 34, 58), (40, 70, 104), t)
        elif y < height * 0.50:
            t = (y - height * 0.30) / (height * 0.20)
            c = lerp_color((40, 70, 104), (96, 126, 158), t)
        elif y < height * 0.60:
            # band of high pink alpenglow
            t = (y - height * 0.50) / (height * 0.10)
            c = lerp_color((96, 126, 158), (214, 156, 162), t)
        elif y < height * 0.70:
            t = (y - height * 0.60) / (height * 0.10)
            c = lerp_color((214, 156, 162), (196, 200, 214), t)
        else:
            t = (y - height * 0.70) / (height * 0.30)
            c = lerp_color((196, 200, 214), (228, 234, 240), t)
        draw.line([(0, y), (width, y)], fill=c)


def draw_high_clouds(draw: ImageDraw, width: int, height: int) -> None:
    """Thin streaks of high cirrus, lit cold pink, drawn on an overlay."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    streaks = [
        (height * 0.18, 0.0020, 120),
        (height * 0.24, 0.0016, 90),
        (height * 0.40, 0.0024, 70),
        (height * 0.46, 0.0018, 60),
    ]
    for base_y, freq, alpha in streaks:
        for x in range(0, width, 2):
            wave = math.sin(x * freq) * height * 0.012
            y = int(base_y + wave)
            thickness = 2 + int(abs(math.sin(x * 0.001)) * 4)
            a = max(0, min(255, int(alpha - abs(x - width // 2) / 30)))
            if a > 4:
                od.line([(x, y), (x, y + thickness)], fill=(232, 210, 214, a))
    draw._image.paste(overlay, (0, 0), overlay)


def draw_distant_peaks(draw: ImageDraw, width: int, height: int) -> None:
    """A row of distant, hazy snow peaks ranked along the horizon, blue-grey."""
    horizon = height * 0.66
    rng_peaks = [
        (0, horizon + 30), (140, horizon - 60), (300, horizon + 10),
        (440, horizon - 90), (600, horizon - 30), (760, horizon - 120),
        (920, horizon - 40), (1080, horizon - 80), (1240, horizon - 20),
        (1400, horizon - 70), (width, horizon + 20),
    ]
    poly = [(0, height)] + rng_peaks + [(width, height)]
    draw.polygon(poly, fill=(120, 140, 168))
    # faint snow on the distant tops
    for i in range(1, len(rng_peaks) - 1):
        x, y = rng_peaks[i]
        draw.polygon(
            [(x - 40, y + 40), (x, y), (x + 40, y + 40)],
            fill=(186, 198, 214),
        )


def draw_main_summit(draw: ImageDraw, width: int, height: int) -> None:
    """The dominant peak: a sheer snow-and-rock summit ridge rising on the right,
    granite-grey rock under wind-scoured white, against the thin sky."""
    # The great pyramid of the mountain, filling the right and center.
    apex = (int(width * 0.60), int(height * 0.12))
    base_left = (int(width * 0.05), int(height * 0.72))
    base_right = (width + 80, int(height * 0.82))
    draw.polygon([apex, base_left, base_right], fill=(214, 222, 232))

    # Granite-grey rock bands and buttresses on the steep face (left side of apex).
    rock = (84, 90, 102)
    rock_dark = (60, 64, 74)
    draw.polygon(
        [apex, (int(width * 0.30), int(height * 0.40)),
         (int(width * 0.20), int(height * 0.58)), (int(width * 0.42), int(height * 0.34))],
        fill=rock,
    )
    draw.polygon(
        [(int(width * 0.34), int(height * 0.30)), (int(width * 0.46), int(height * 0.46)),
         (int(width * 0.30), int(height * 0.52)), (int(width * 0.26), int(height * 0.40))],
        fill=rock_dark,
    )
    draw.polygon(
        [(int(width * 0.12), int(height * 0.60)), (int(width * 0.26), int(height * 0.50)),
         (int(width * 0.22), int(height * 0.68)), (int(width * 0.08), int(height * 0.70))],
        fill=rock,
    )

    # Shadowed snow on the right flank to give the face volume.
    draw.polygon(
        [apex, base_right, (int(width * 0.66), int(height * 0.50))],
        fill=(186, 196, 210),
    )

    # The summit ridge: a thin saw-toothed crest running up to the apex.
    ridge_x0, ridge_y0 = int(width * 0.18), int(height * 0.58)
    rx, ry = ridge_x0, ridge_y0
    segs = 22
    for i in range(segs):
        t = i / segs
        nx = int(ridge_x0 + (apex[0] - ridge_x0) * t)
        ny = int(ridge_y0 + (apex[1] - ridge_y0) * t)
        jag = (i % 2) * int(14 * (1 - t)) - int(6 * (1 - t))
        draw.line([(rx, ry), (nx, ny + jag)], fill=(238, 244, 250), width=max(2, int(7 * (1 - t)) + 2))
        rx, ry = nx, ny + jag

    # Wind-lit edge highlight along the ridge.
    draw.line([(ridge_x0, ridge_y0), apex], fill=(250, 244, 236), width=2)


def draw_spindrift(draw: ImageDraw, width: int, height: int) -> None:
    """Blowing spindrift streaming off the summit ridge in the wind, on overlay."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    apex = (int(width * 0.60), int(height * 0.12))
    import random

    rng = random.Random(41)
    # plumes tearing off to the right (lee side) of the apex and upper ridge
    for _ in range(900):
        # origin somewhere along the upper ridge
        t = rng.random()
        ox = int(width * 0.18 + (apex[0] - width * 0.18) * t)
        oy = int(height * 0.58 + (apex[1] - height * 0.58) * t) + rng.randint(-10, 10)
        # stream rightward and slightly up
        length = rng.randint(20, 140)
        ex = ox + length
        ey = oy - rng.randint(-6, 30)
        alpha = rng.randint(20, 90)
        od.line([(ox, oy), (ex, ey)], fill=(244, 248, 252, alpha), width=1)
    overlay = overlay.filter(ImageFilter.GaussianBlur(1.2))
    draw._image.paste(overlay, (0, 0), overlay)


def draw_roped_climber(draw: ImageDraw, width: int, height: int) -> None:
    """A tiny lone roped climber high on the summit ridge — sense of scale."""
    cx, cy = int(width * 0.40), int(height * 0.40)

    # the rope trailing down the ridge behind the climber
    draw.line(
        [(cx - 70, cy + 46), (cx - 30, cy + 28), (cx - 8, cy + 14)],
        fill=(196, 70, 60),
        width=2,
    )

    # legs
    draw.line([(cx - 4, cy + 14), (cx - 8, cy + 26)], fill=(20, 24, 30), width=3)
    draw.line([(cx + 2, cy + 14), (cx + 5, cy + 26)], fill=(20, 24, 30), width=3)
    # torso (dark climbing suit)
    draw.line([(cx - 1, cy - 2), (cx, cy + 14)], fill=(24, 30, 40), width=5)
    # arm with ice axe raised
    draw.line([(cx, cy + 2), (cx + 9, cy - 8)], fill=(24, 30, 40), width=3)
    draw.line([(cx + 9, cy - 8), (cx + 13, cy - 20)], fill=(150, 150, 156), width=2)  # axe shaft
    draw.line([(cx + 13, cy - 20), (cx + 7, cy - 22)], fill=(150, 150, 156), width=2)  # axe head
    # other arm
    draw.line([(cx - 1, cy + 2), (cx - 8, cy + 6)], fill=(24, 30, 40), width=3)
    # head with a small warm-toned hood
    draw.ellipse([cx - 4, cy - 9, cx + 4, cy - 1], fill=(214, 96, 72))
    # tiny pack hump
    draw.ellipse([cx - 6, cy - 1, cx + 1, cy + 8], fill=(40, 48, 60))


def draw_foreground_snow(draw: ImageDraw, width: int, height: int) -> None:
    """A wind-sculpted near foreground snow slope at the very bottom of the image."""
    import random

    rng = random.Random(7)
    base_y = height * 0.78
    points = []
    for x in range(0, width + 1, 12):
        y = base_y + math.sin(x * 0.004) * 22 + rng.randint(-6, 6)
        points.append((x, y))
    poly = [(0, height)] + points + [(width, height)]
    draw.polygon(poly, fill=(226, 232, 240))
    # bluish wind-shadow striations on the foreground snow
    for i in range(0, len(points) - 1, 3):
        x, y = points[i]
        draw.line([(x, int(y) + 8), (x + 60, int(y) + 40)], fill=(196, 206, 222), width=3)


def draw_cold_haze(draw: ImageDraw, width: int, height: int) -> None:
    """A thin cold haze at the base of the peaks to push them back in depth."""
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    top = int(height * 0.60)
    bot = int(height * 0.74)
    for y in range(top, bot):
        a = int(70 * (1 - (y - top) / (bot - top)))
        od.line([(0, y), (width, y)], fill=(206, 214, 226, max(0, a)))
    draw._image.paste(overlay, (0, 0), overlay)


def draw_title_panel(draw: ImageDraw, width: int, height: int, font_paths: dict) -> None:
    """Draw a dark title panel at the bottom (legacy panel; final panel is the
    standard helper called at the end of create_cover)."""
    panel_top = TITLE_PANEL_TOP

    draw.rectangle([(0, panel_top), (width, height)], fill=(10, 18, 30, 210))

    for i in range(3):
        draw.line(
            [(0, panel_top - i), (width, panel_top - i)],
            fill=(160, 190, 220, 80 - i * 20),
            width=1,
        )

    title = "The Eighth\nSummit"
    title_font_size = 80
    try:
        title_font = ImageFont.truetype(str(font_paths["title"]), title_font_size)
    except Exception:
        title_font = ImageFont.load_default()

    lines = title.split("\n")
    y_offset = panel_top + 70
    for line in lines:
        try:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            tw = bbox[2] - bbox[0]
        except Exception:
            tw = 0
        tx = (width - tw) // 2
        draw.text((tx + 2, y_offset + 2), line, fill=(5, 10, 15), font=title_font)
        draw.text((tx, y_offset), line, fill=(224, 230, 238), font=title_font)
        y_offset += 95

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
    draw.text((ax + 1, ay + 1), author, fill=(5, 10, 15), font=author_font)
    draw.text((ax, ay), author, fill=(190, 206, 222), font=author_font)


def create_cover(metadata_path: Path, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = metadata.get("title", "The Eighth Summit")
    author = metadata.get("author", "Barış Kısır")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Step 1: Cold thin-air sky gradient with high pink alpenglow band
    draw_gradient(draw, WIDTH, HEIGHT)

    # Step 2: Thin high cirrus
    draw_high_clouds(draw, WIDTH, HEIGHT)

    # Step 3: Distant ranked snow peaks
    draw_distant_peaks(draw, WIDTH, HEIGHT)

    # Step 4: Cold haze to set the distance back
    draw_cold_haze(draw, WIDTH, HEIGHT)

    # Step 5: The dominant summit and its snow-and-rock ridge
    draw_main_summit(draw, WIDTH, HEIGHT)

    # Step 6: Blowing spindrift off the ridge
    draw_spindrift(draw, WIDTH, HEIGHT)

    # Step 7: The tiny roped climber on the ridge
    draw_roped_climber(draw, WIDTH, HEIGHT)

    # Step 8: Foreground wind-sculpted snow
    draw_foreground_snow(draw, WIDTH, HEIGHT)

    # Step 9: Title panel
    font_paths = {
        "title": str(FONTS_DIR / "arialbd.ttf"),
        "author": str(FONTS_DIR / "arialbd.ttf"),
        "small": str(FONTS_DIR / "arial.ttf"),
    }
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
