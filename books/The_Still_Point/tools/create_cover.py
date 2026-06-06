#!/usr/bin/env python3
"""Cover: The Still Point — a Scottish lighthouse in a storm."""

from __future__ import annotations
import argparse, json, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def wrap(draw, text, fnt, mw):
    words, lines, cur = text.split(), [], []
    for w in words:
        p = " ".join([*cur, w])
        if draw.textbbox((0, 0), p, font=fnt)[2] <= mw:
            cur.append(w)
        else:
            lines.append(" ".join(cur))
            cur = [w]
    if cur:
        lines.append(" ".join(cur))
    return lines


def centered(draw, y, lines, fnt, fill, gap):
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        draw.text(((W - (bb[2] - bb[0])) // 2, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Storm sky gradient: dark slate to deep navy to pale gray horizon
    for y in range(H):
        t = y / H
        if t < 0.7:
            r = int(15 + 30 * (t / 0.7))
            g = int(15 + 40 * (t / 0.7))
            b = int(40 + 60 * (t / 0.7))
        else:
            r = int(45 + 80 * ((t - 0.7) / 0.3))
            g = int(55 + 90 * ((t - 0.7) / 0.3))
            b = int(100 + 100 * ((t - 0.7) / 0.3))
        draw.line((0, y, W, y), fill=(max(0, min(255, r)), max(0, min(255, g)), max(0, min(255, b)), 255))

    # Storm clouds in upper portion
    cloud_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cloud_layer, "RGBA")
    cloud_colors = [(30, 35, 50, 180), (50, 55, 70, 150), (20, 25, 40, 200)]
    for i in range(18):
        cx = int(W * (i / 18) + math.sin(i * 1.7) * 80)
        cy = int(100 + math.cos(i * 2.3) * 120 + i * 15)
        rx = 120 + int(math.sin(i * 1.1) * 60)
        ry = 40 + int(math.cos(i * 0.7) * 20)
        col = cloud_colors[i % 3]
        cd.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=col)
    cloud_layer = cloud_layer.filter(ImageFilter.GaussianBlur(20))
    img = Image.alpha_composite(img, cloud_layer)

    # Sea / ocean
    sea_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sea_layer, "RGBA")
    ocean_y = 1200
    for y in range(ocean_y, H):
        t = (y - ocean_y) / (H - ocean_y)
        wave = math.sin(y * 0.03) * 20 + math.sin(y * 0.07) * 10
        r = int(20 + 30 * t)
        g = int(40 + 50 * t)
        b = int(70 + 40 * t)
        a = 180 + int(40 * t)
        sd.line((0, y, W, y), fill=(r, g, b, min(a, 255)))
    # Wave crests (whitecaps)
    for i in range(30):
        wx = int(W * (i / 30) + math.sin(i * 4.1) * 80)
        wy = int(ocean_y + 100 + math.sin(i * 2.3) * 60 + i * 8)
        wr = 3 + int(math.sin(i * 1.7) * 4)
        sd.ellipse((wx - wr, wy - wr, wx + wr, wy + wr), fill=(200, 210, 220, 120))
    img = Image.alpha_composite(img, sea_layer)

    # Spray / mist at cliff line
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist, "RGBA")
    for i in range(80):
        mx = int(W * (i / 80) + math.sin(i * 3.7) * 50)
        my = int(1150 + math.sin(i * 5.1) * 80)
        mr = 8 + int(math.sin(i * 2.9) * 6)
        md.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=(200, 210, 230, int(30 + 30 * math.sin(i * 1.3))))
    mist = mist.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, mist)

    # Cliff face
    cliff = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    cd2 = ImageDraw.Draw(cliff, "RGBA")
    points = []
    for x in range(0, W, 4):
        cliff_top = 1180 + math.sin(x * 0.002) * 60 + math.sin(x * 0.005) * 30
        cliff_base = H
        col = int(40 + 20 * math.sin(x * 0.003))
        cd2.line((x, cliff_top, x, cliff_base), fill=(col, col - 10, col - 15, 220))
    img = Image.alpha_composite(img, cliff)

    # Lighthouse tower
    lx, ly = W // 2, 0
    tower_base_y = 1180
    tower_w = 60
    tower_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    td = ImageDraw.Draw(tower_layer, "RGBA")
    # Main tower body (tapered)
    for y in range(200, tower_base_y):
        t = (y - 200) / (tower_base_y - 200)
        tw = int(tower_w * (1 - t * 0.35))
        x1 = lx - tw // 2
        x2 = lx + tw // 2
        # White tower with shadow
        shade = 220 - int(t * 40)
        td.line((x1, y, x2, y), fill=(shade, shade, shade, 240))
    # Red bands
    for band_y in range(350, tower_base_y, 120):
        for y in range(band_y, min(band_y + 25, tower_base_y)):
            t = (y - 200) / (tower_base_y - 200)
            tw = int(tower_w * (1 - t * 0.35))
            x1 = lx - tw // 2
            x2 = lx + tw // 2
            td.line((x1, y, x2, y), fill=(180, 40, 40, 230))
    # Lantern room
    lantern_y = 170
    lh = 30
    td.rectangle((lx - 35, lantern_y, lx + 35, lantern_y + lh), fill=(50, 50, 55, 240))
    # Glass panels
    td.rectangle((lx - 30, lantern_y + 2, lx + 30, lantern_y + lh - 2), fill=(200, 210, 230, 100))
    # Light beam
    beam = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(beam, "RGBA")
    beam_angle = 0.4
    for i in range(60):
        distance = i * 15
        bx = lx + math.cos(beam_angle) * distance
        by = lantern_y + lh // 2 + math.sin(beam_angle) * distance * 0.3
        br = max(2, 30 - i // 2)
        alpha = max(10, 80 - i)
        bd.ellipse((bx - br, by - br, bx + br, by + br), fill=(255, 230, 150, alpha))
    beam = beam.filter(ImageFilter.GaussianBlur(8))
    img = Image.alpha_composite(img, beam)
    img = Image.alpha_composite(img, tower_layer)

    # Title panel at bottom
    panel_y = 1920
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pd = ImageDraw.Draw(overlay, "RGBA")
    for y in range(panel_y, H):
        t = (y - panel_y) / (H - panel_y)
        a = int(200 + 55 * t)
        pd.line((0, y, W, y), fill=(8, 6, 12, min(a, 255)))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img, "RGBA")

    # Decorative lines
    draw.line((220, 1970, W - 220, 1970), fill=(180, 190, 210, 150), width=2)
    draw.line((220, H - 100, W - 220, H - 100), fill=(180, 190, 210, 100), width=1)

    # Title text
    tf = font("georgiab.ttf", 100)
    af = font("arialbd.ttf", 38)
    sf = font("arial.ttf", 22)

    # Subtitle line (genre)
    centered(draw, 1990, ["LITERARY FICTION"], sf, (150, 160, 200, 180), 4)

    # Title - wrap long title
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, 2060, title_lines, tf, (220, 225, 240, 255), 8)

    y += 30
    centered(draw, y, ["BY"], sf, (150, 155, 170, 160), 4)
    y += 24
    centered(draw, y, [author], af, (200, 205, 220, 230), 4)

    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.convert("RGB").save(op, "PNG", optimize=True)



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
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )


if __name__ == "__main__":
    main()