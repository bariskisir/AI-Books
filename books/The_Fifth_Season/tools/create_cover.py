#!/usr/bin/env python3
"""Cover: The Fifth Season — Literary Romance on a Greek island."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    candidates = [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]
    for c in candidates:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw: ImageDraw, text: str, font: ImageFont, max_w: int) -> list[str]:
    words = text.split()
    lines, current = [], []
    for w in words:
        test = " ".join([*current, w])
        if draw.textbbox((0, 0), test, font=font)[2] <= max_w:
            current.append(w)
        else:
            if current:
                lines.append(" ".join(current))
            current = [w]
    if current:
        lines.append(" ".join(current))
    return lines


def centered(
    draw: ImageDraw, y: int, lines: list[str], font: ImageFont, fill, gap: int
) -> int:
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=font)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=font, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(metadata_path: Path, output_path: Path) -> None:
    meta = json.loads(metadata_path.read_text(encoding="utf-8"))
    title = meta["title"]
    author = meta.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Gradient sky: Aegean blue at top, warm terracotta near horizon
    for y in range(H):
        t = y / H
        if y < 1200:
            # Sky: deep blue to pale azure
            r = int(30 + 60 * (y / 1200))
            g = int(80 + 100 * (y / 1200))
            b = int(180 - 30 * (y / 1200))
        else:
            # Horizon to sea: warm peach to deep teal
            t2 = (y - 1200) / 1360
            r = int(90 - 50 * t2)
            g = int(180 - 120 * t2)
            b = int(150 - 40 * t2)
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Sun glow near horizon
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse((W // 2 - 250, 1050, W // 2 + 250, 1450), fill=(240, 180, 100, 40))
    sd.ellipse((W // 2 - 150, 1100, W // 2 + 150, 1400), fill=(255, 200, 120, 50))
    sun = sun.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, sun)
    draw = ImageDraw.Draw(img)

    # Sea with wave lines
    for w in range(8):
        wy = 1400 + w * 25
        wax = math.sin(w * 0.7) * 60
        for x in range(0, W, 8):
            px = x + int(math.sin(x * 0.02 + w * 1.2) * 15)
            if 0 <= px < W:
                draw.point((px, wy), fill=(200, 220, 240, 60 + w * 5))

    # Distant island silhouette
    draw.polygon(
        [(100, 1350), (200, 1200), (350, 1150), (500, 1180), (650, 1120),
         (800, 1150), (950, 1100), (1100, 1130), (1250, 1080), (1400, 1110),
         (1500, 1140), (1550, 1350)],
        fill=(60, 80, 95, 180),
    )

    # Whitewashed buildings on the island
    # Church with blue dome
    bx, by = 700, 1080
    draw.rectangle((bx - 40, by - 80, bx + 40, by), fill=(230, 235, 240, 220))
    draw.ellipse((bx - 30, by - 110, bx + 30, by - 70), fill=(30, 100, 160, 200))
    draw.polygon(
        [(bx - 5, by - 110), (bx + 5, by - 110), (bx, by - 130)],
        fill=(220, 225, 230, 200),
    )

    # Buildings cluster left
    for i, (bdx, bdy, bw, bh) in enumerate([
        (560, 1090, 60, 50), (580, 1060, 50, 80), (530, 1080, 45, 60),
        (780, 1080, 55, 55), (810, 1050, 60, 85), (840, 1070, 40, 65),
    ]):
        draw.rectangle((bdx, bdy - bh, bdx + bw, bdy), fill=(210 + i * 3, 215 + i * 3, 220 + i * 3, 200))
        # Blue window
        draw.rectangle((bdx + 10, bdy - bh + 15, bdx + bw - 10, bdy - bh + 30), fill=(40, 120, 180, 150))

    # Second church or bell tower
    draw.rectangle((500, 1060, 520, 1120), fill=(225, 230, 235, 190))
    draw.polygon([(495, 1060), (525, 1060), (510, 1040)], fill=(220, 225, 230, 190))

    # Steps / stairs on hillside
    for s in range(6):
        sx = 640 + s * 25
        sy = 1130 - s * 8
        draw.line((sx, sy, sx + 60, sy), fill=(180, 190, 200, 120), width=2)

    # Terracotta roof tiles
    for rx, rw in [(540, 80), (600, 70), (720, 90), (790, 80), (840, 60)]:
        draw.polygon(
            [(rx, 1120), (rx + rw, 1120), (rx + rw // 2, 1105)],
            fill=(180, 100, 60, 150),
        )

    # Rocky cliff edge
    draw.polygon(
        [(0, 1350), (50, 1300), (120, 1320), (200, 1270), (300, 1300),
         (400, 1280), (W, 1350), (W, H), (0, H)],
        fill=(180, 165, 140, 200),
    )
    draw.polygon(
        [(0, 1380), (80, 1320), (180, 1340), (280, 1300), (400, 1330), (W, 1380), (W, H), (0, H)],
        fill=(200, 185, 160, 180),
    )

    # Olive tree silhouette on cliff
    draw.line((320, 1330, 340, 1280), fill=(100, 80, 50, 180), width=4)
    draw.ellipse((310, 1240, 370, 1290), fill=(80, 100, 60, 120))

    # Small boat in distance
    draw.ellipse((250, 1380, 280, 1395), fill=(140, 80, 60, 150))
    draw.line((260, 1370, 260, 1390), fill=(60, 60, 60, 120), width=1)

    # Soft mist layer over the island
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    md.ellipse((100, 1100, W - 100, 1450), fill=(210, 210, 220, 15))
    mist = mist.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img)

    # Bottom title panel
    draw.rectangle((0, 1960, W, H), fill=(20, 25, 40, 245))
    # Decorative lines
    draw.line((200, 2000, W - 200, 2000), fill=(180, 200, 220, 150), width=2)
    draw.line((200, H - 100, W - 200, H - 100), fill=(180, 200, 220, 80), width=1)

    # Title in white using arialbd.ttf
    tf = font("arialbd.ttf", 100)
    af = font("arialbd.ttf", 38)
    sf = font("arial.ttf", 28)

    wrapped = wrap(draw, title.upper(), tf, 1300)
    y = centered(draw, 2040, wrapped, tf, (255, 255, 255), 10)

    # Author in white
    y = centered(draw, y + 50, [author], af, (220, 225, 235), 6)

    # Genre line in white
    centered(draw, y + 55, ["LITERARY ROMANCE"], sf, (180, 210, 240), 0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(str(output_path), "PNG", optimize=True)



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
    parser.add_argument("--metadata", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    mp = ROOT / args.metadata if not args.metadata.is_absolute() else args.metadata
    op = ROOT / args.out if not args.out.is_absolute() else args.out
    make_cover(mp, op)


if __name__ == "__main__":
    main()