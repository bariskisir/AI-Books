#!/usr/bin/env python3
"""Cover: The River Mother — Magical Realism set on the Amazon."""

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


def centered(draw: ImageDraw, y: int, lines: list[str], font: ImageFont, fill, gap: int) -> int:
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

    # Gradient: jungle canopy green at top, river brown at bottom
    for y in range(H):
        t = y / H
        if y < 800:
            # Dense jungle canopy: deep green to lighter green
            r = int(15 + 25 * (y / 800))
            g = int(70 + 60 * (y / 800))
            b = int(20 + 15 * (y / 800))
        elif y < 1400:
            # Transition: green to river brown
            t2 = (y - 800) / 600
            r = int(40 + 80 * t2)
            g = int(130 - 60 * t2)
            b = int(35 - 10 * t2)
        else:
            # River: deep muddy brown
            t3 = (y - 1400) / 1160
            r = int(120 - 40 * t3)
            g = int(70 - 20 * t3)
            b = int(25 - 10 * t3)
        draw.line((0, y, W, y),
                  fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Mist layer over the transition zone
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    md.ellipse((0, 700, W, 1500), fill=(180, 200, 160, 30))
    mist = mist.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, mist)
    draw = ImageDraw.Draw(img)

    # Sunlight breaking through canopy
    sun = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sun)
    sd.ellipse((W // 2 - 300, 100, W // 2 + 300, 600), fill=(220, 210, 150, 30))
    sd.ellipse((W // 2 - 150, 200, W // 2 + 150, 450), fill=(240, 230, 170, 40))
    sun = sun.filter(ImageFilter.GaussianBlur(50))
    img = Image.alpha_composite(img, sun)
    draw = ImageDraw.Draw(img)

    # Light rays from sun through canopy
    for i in range(7):
        angle = -40 + i * 12
        rad = math.radians(angle)
        x_start = W // 2 + int(math.sin(rad) * 200)
        for j in range(20):
            t = j / 20
            x = x_start + int(t * 1600 * math.sin(rad + 0.03))
            y = 400 + int(t * 1200)
            if 0 <= x < W and 0 <= y < H:
                alpha = int(12 * (1 - t))
                draw.point((x, y), fill=(240, 235, 180, alpha))

    # Jungle canopy silhouette at top
    canopy = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(canopy)
    # Tree crowns along the top
    for cx in range(-50, W + 100, 80):
        cy = 150 + int(math.sin(cx * 0.03) * 60 + math.sin(cx * 0.07) * 30)
        r = 100 + int(math.sin(cx * 0.05) * 40)
        cd.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(10, 50, 15, 220))

    # Overlapping canopy layer
    for cx in range(0, W, 60):
        cy = 130 + int(math.cos(cx * 0.04) * 50)
        r2 = 80 + int(math.sin(cx * 0.06 + 1) * 30)
        cd.ellipse((cx - r2, cy - r2, cx + r2, cy + r2), fill=(8, 40, 12, 200))

    img = Image.alpha_composite(img, canopy)
    draw = ImageDraw.Draw(img)

    # Floating village on stilts
    village_y = 1500
    # Stilts
    for stilt_x in range(200, W - 100, 150):
        stilt_h = 60 + int(math.sin(stilt_x * 0.05) * 20)
        draw.rectangle((stilt_x - 4, village_y, stilt_x + 4, village_y + stilt_h),
                       fill=(80, 60, 40, 200))
        # House platform
        pw, ph = 80, 30
        draw.rectangle((stilt_x - pw // 2, village_y - ph, stilt_x + pw // 2, village_y),
                       fill=(120, 90, 60, 220))
        # House walls
        draw.rectangle((stilt_x - pw // 2 + 5, village_y - ph - 50, stilt_x + pw // 2 - 5, village_y - ph),
                       fill=(160, 130, 90, 220))
        # Roof (palm thatch)
        draw.polygon([(stilt_x - pw // 2 - 5, village_y - ph - 50),
                      (stilt_x + pw // 2 + 5, village_y - ph - 50),
                      (stilt_x + pw // 2 + 10, village_y - ph - 80),
                      (stilt_x - pw // 2 - 10, village_y - ph - 80)],
                     fill=(90, 70, 40, 220))
    # A larger house in center (Yara's blue house)
    stilt_x = W // 2
    draw.rectangle((stilt_x - 4, village_y, stilt_x + 4, village_y + 70), fill=(80, 60, 40, 200))
    draw.rectangle((stilt_x - 50, village_y - 20, stilt_x + 50, village_y), fill=(120, 90, 60, 220))
    draw.rectangle((stilt_x - 45, village_y - 80, stilt_x + 45, village_y - 20), fill=(60, 80, 140, 220))
    draw.polygon([(stilt_x - 55, village_y - 80),
                  (stilt_x + 55, village_y - 80),
                  (stilt_x + 60, village_y - 110),
                  (stilt_x - 60, village_y - 110)],
                 fill=(90, 75, 45, 220))

    # River reflections
    for rx in range(0, W, 4):
        ry = 1700 + int(math.sin(rx * 0.01 + 2) * 10)
        draw.point((rx, ry), fill=(180, 160, 100, 60))

    # Water ripples in foreground
    for r in range(30):
        ry = 1800 + r * 20
        for x in range(0, W, 6):
            px = x + int(math.sin(x * 0.015 + r * 0.4) * 8)
            if 0 <= px < W:
                alpha = 40 + int(math.sin(x * 0.02 + r) * 10)
                draw.point((px, ry), fill=(200, 180, 130, max(10, alpha)))

    # Victoria water lilies in foreground
    random.seed(42)
    for _ in range(6):
        lx = random.randint(100, W - 100)
        ly = random.randint(2100, 2400)
        lr = random.randint(30, 55)
        draw.ellipse((lx - lr, ly - lr // 2, lx + lr, ly + lr // 2),
                     fill=(40, 100, 60, 180))
        draw.ellipse((lx - lr + 5, ly - lr // 2 + 3, lx + lr - 5, ly + lr // 2 - 3),
                     fill=(50, 120, 70, 150))
        # Pink flower on some lilies
        if _ % 2 == 0:
            draw.ellipse((lx - 10, ly - 8, lx + 10, ly + 8), fill=(220, 160, 170, 180))

    # River dolphins surfacing
    dolphin_y = 1750
    for dx in [300, 800, 1200]:
        draw.ellipse((dx - 20, dolphin_y - 6, dx + 20, dolphin_y + 6), fill=(160, 140, 130, 120))
        draw.ellipse((dx - 25, dolphin_y - 4, dx + 25, dolphin_y + 4), fill=(150, 130, 120, 100))

    # Bottom title panel
    draw.rectangle((0, 1920, W, H), fill=(15, 20, 30, 245))
    # Decorative lines
    draw.line((200, 1960, W - 200, 1960), fill=(160, 200, 180, 150), width=2)
    draw.line((200, H - 80, W - 200, H - 80), fill=(160, 200, 180, 80), width=1)

    # Title in white using arialbd.ttf
    tf = font("arialbd.ttf", 100)
    af = font("arialbd.ttf", 38)
    sf = font("arial.ttf", 28)

    wrapped = wrap(draw, title.upper(), tf, 1300)
    y = centered(draw, 2020, wrapped, tf, (255, 255, 255), 10)

    # Author in white
    y = centered(draw, y + 50, [author], af, (200, 220, 230), 6)

    # Genre line in white
    centered(draw, y + 55, ["MAGICAL REALISM"], sf, (180, 210, 180), 0)

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