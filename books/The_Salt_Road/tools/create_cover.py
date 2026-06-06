#!/usr/bin/env python3
"""Create a project-local raster cover for The Salt Road — Anatolia landscape."""

from __future__ import annotations

import argparse
import json
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

    img = Image.new("RGBA", (W, H), (200, 175, 140, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Warm earth sky gradient — Anatolian sunset.
    for y in range(H):
        t = y / (H - 1)
        r = int(200 - 80 * t)
        g = int(175 - 90 * t)
        b = int(140 - 100 * t)
        draw.line((0, y, W, y), fill=(max(0, r), max(0, g), max(0, b), 255))

    # Distant mountain silhouette.
    for _ in range(8):
        mx = rng.randrange(-100, 1700)
        mh = rng.randrange(80, 250)
        mw = rng.randrange(200, 600)
        draw.polygon([(mx, 1100), (mx + mw // 2, 1100 - mh), (mx + mw, 1100)],
                     fill=(90, 65, 45, 60))

    # Fairy chimney rock formations.
    for _ in range(25):
        cx = rng.randrange(50, 1550)
        cy = rng.randrange(850, 1400)
        cw = rng.randrange(15, 50)
        ch = rng.randrange(60, 200)
        draw.polygon([(cx - cw // 2, cy), (cx, cy - ch), (cx + cw // 2, cy)],
                     fill=(160, 130, 95, 220))
        cap_w = cw + rng.randrange(4, 14)
        draw.ellipse((cx - cap_w // 2, cy - ch - 8, cx + cap_w // 2, cy - ch + 4),
                     fill=(110, 85, 60, 240))

    # Salt pan — white cracked earth.
    pan_y = 1700
    draw.rectangle((0, pan_y, W, H), fill=(230, 225, 210, 230))
    for _ in range(60):
        px = rng.randrange(0, W)
        py = rng.randrange(pan_y, H)
        pl = rng.randrange(20, 80)
        angle = rng.uniform(0, 6.28)
        ex = int(px + pl * rng.choice([-1, 1]) * 0.8)
        ey = int(py + pl * rng.choice([-1, 1]) * 0.3)
        draw.line((px, py, ex, ey), fill=(190, 182, 168, 140), width=2)

    # Dried grass tufts.
    for _ in range(40):
        gx = rng.randrange(0, W)
        gy = rng.randrange(pan_y + 20, H - 40)
        gh = rng.randrange(8, 20)
        draw.line((gx, gy, gx - 3, gy - gh), fill=(160, 145, 110, 120), width=2)
        draw.line((gx, gy, gx + 3, gy - gh), fill=(160, 145, 110, 120), width=2)

    # Stone bridge silhouette.
    bridge_x = rng.randrange(500, 1100)
    bridge_y = pan_y - rng.randrange(60, 120)
    for arch in range(3):
        ax = bridge_x + arch * 60
        draw.arc((ax, bridge_y - 30, ax + 60, bridge_y + 10), 180, 0,
                 fill=(100, 75, 55, 100), width=6)

    # Warm haze.
    haze = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(haze)
    for _ in range(20):
        hx = rng.randrange(-200, W + 200)
        hy = rng.randrange(1200, 1800)
        hd.ellipse((hx, hy, hx + rng.randrange(400, 1000), hy + rng.randrange(60, 150)),
                   fill=(210, 190, 160, rng.randrange(5, 15)))
    haze = haze.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, haze)

    draw = ImageDraw.Draw(img, "RGBA")

    # Lower panel.
    draw.rectangle((0, 2100, W, H), fill=(40, 30, 20, 220))
    draw.line((250, 2130, W - 250, 2130), fill=(180, 165, 140, 80), width=1)

    # Typography.
    title_font = font("georgiab.ttf", 115)
    author_font = font("arialbd.ttf", 42)
    subtitle_font = font("arial.ttf", 30)

    y = 2180
    y = centered(draw, y, ["AN ANATOLIAN ROAD"], subtitle_font, (170, 158, 140), 8)
    y += 60
    y = centered(draw, y, wrap(draw, title.upper(), title_font, 1200), title_font, (220, 215, 200), 18)
    y += 110
    centered(draw, y, [author], author_font, (190, 182, 168), 8)

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