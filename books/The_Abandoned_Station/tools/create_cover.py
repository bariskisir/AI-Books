#!/usr/bin/env python3
"""Cover: The Abandoned Station — Research station in blizzard, frozen figures, ice blue and white."""

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


def wrap(draw, text, fnt, mw):
    """Wrap text to fit within mw pixels."""
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
    """Draw each line centered horizontally, return final y."""
    for line in lines:
        bb = draw.textbbox((0, 0), line, font=fnt)
        x = (W - (bb[2] - bb[0])) // 2
        draw.text((x, y), line, font=fnt, fill=fill)
        y += bb[3] - bb[1] + gap
    return y


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title, author = m["title"], m.get("author", "Barış Kısır")

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Gradient background: deep ice blue at top to pale white at bottom ----
    for y in range(H):
        t = y / H
        if t < 0.5:
            # Deep ice blue to steel blue
            r = int(20 + 80 * (t / 0.5))
            g = int(60 + 100 * (t / 0.5))
            b = int(120 + 80 * (t / 0.5))
        else:
            # Steel blue to pale ice white
            t2 = (t - 0.5) / 0.5
            r = int(100 + 140 * t2)
            g = int(160 + 80 * t2)
            b = int(200 + 50 * t2)
        draw.line((0, y, W, y), fill=(min(255, r), min(255, g), min(255, b), 255))

    # ---- Blizzard / snow streaks in upper sky ----
    blizzard = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    bd = ImageDraw.Draw(blizzard)

    for i in range(350):
        sx = int(random.random() * W * 1.3) - 100
        sy = int(random.random() * 1400)
        sl = int(30 + random.random() * 120)
        angle = random.random() * 0.6 - 0.3  # slight diagonal
        ex = sx + int(sl * (0.8 + angle))
        ey = sy + int(sl * 0.15)
        alpha = int(40 + 80 * random.random())
        width = 1 + int(2 * random.random())
        bd.line((sx, sy, ex, ey), fill=(255, 255, 255, alpha), width=width)

    blizzard = blizzard.filter(ImageFilter.GaussianBlur(2))
    img = Image.alpha_composite(img, blizzard)
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Ice formations / crystalline shapes in mid-ground ----
    for i in range(12):
        ix = int(100 + random.random() * (W - 200))
        iy = int(600 + random.random() * 400)
        ih = int(40 + random.random() * 120)
        iw = int(20 + random.random() * 60)
        # Crystal shape: series of triangles
        alpha = int(30 + 50 * random.random())
        for j in range(5):
            cx = ix + random.randint(-20, 20)
            cy = iy + j * ih // 5
            cw = iw - j * 4
            points = [
                (cx, cy - cw),
                (cx + cw // 2, cy),
                (cx, cy + cw // 2),
                (cx - cw // 2, cy),
            ]
            draw.polygon(points, fill=(180, 220, 255, alpha), outline=(200, 235, 255, alpha + 20))
        # Connecting ice lines
        draw.line((ix, iy - ih, ix, iy + ih), fill=(200, 230, 255, alpha - 10), width=2)

    # ---- Frozen figures (silhouettes in the ice) ----
    figures = [(W // 2 - 200, 780), (W // 2 + 80, 750), (W // 2 - 80, 720), (W // 2 + 200, 770)]
    for fx, fy in figures:
        # Body
        draw.ellipse((fx - 20, fy - 60, fx + 20, fy + 10), fill=(100, 140, 190, 120))
        # Head
        draw.ellipse((fx - 12, fy - 80, fx + 12, fy - 58), fill=(90, 130, 180, 130))
        # Ice encasing
        draw.ellipse((fx - 25, fy - 85, fx + 25, fy + 15), fill=None, outline=(180, 210, 240, 80), width=3)
        # Arm reaching
        draw.line((fx + 15, fy - 40, fx + 45, fy - 70), fill=(100, 140, 190, 100), width=4)

    # ---- Research station silhouette ----
    station_x = W // 2 - 160
    station_y = 950
    # Main building
    draw.rectangle(
        (station_x, station_y, station_x + 320, station_y + 70),
        fill=(15, 20, 35, 200),
    )
    # Dome
    draw.ellipse(
        (station_x + 80, station_y - 50, station_x + 240, station_y + 10),
        fill=(15, 20, 35, 190),
    )
    # Side wing
    draw.rectangle(
        (station_x - 40, station_y + 10, station_x, station_y + 70),
        fill=(15, 20, 35, 190),
    )
    # Antenna tower
    draw.line(
        (station_x + 280, station_y, station_x + 280, station_y - 80),
        fill=(20, 25, 40, 200),
        width=4,
    )
    # Antenna dish
    draw.ellipse(
        (station_x + 265, station_y - 105, station_x + 295, station_y - 75),
        fill=None, outline=(20, 25, 40, 200), width=3,
    )
    # Red beacon light
    draw.ellipse(
        (station_x + 278, station_y - 83, station_x + 282, station_y - 79),
        fill=(255, 40, 40, 200),
    )
    # Lit windows
    for wx in range(station_x + 20, station_x + 300, 35):
        for wy in range(station_y + 12, station_y + 60, 18):
            draw.rectangle((wx, wy, wx + 18, wy + 10), fill=(255, 200, 80, 90))

    # ---- Snowy ground / drifts ----
    for x in range(0, W, 4):
        drift = int(math.sin(x * 0.008) * 20 + math.sin(x * 0.02) * 10)
        ground_y = 1050 + drift + int(math.sin(x * 0.04) * 8)
        draw.rectangle(
            (x, ground_y, x + 4, H),
            fill=(220, 230, 245, int(100 + 60 * abs(math.sin(x * 0.01)))),
        )

    # ---- Ice cracks in foreground ----
    for i in range(15):
        fx = int(50 + random.random() * (W - 100))
        fy = int(1100 + random.random() * 400)
        crack_len = int(40 + random.random() * 180)
        end_x = fx + int((random.random() - 0.5) * crack_len)
        end_y = fy + int(crack_len * 0.2)
        draw.line(
            (fx, fy, end_x, end_y),
            fill=(180, 210, 240, int(30 + 50 * random.random())),
            width=2,
        )
        # Branch crack
        if random.random() > 0.6:
            bx = (fx + end_x) // 2
            by = (fy + end_y) // 2
            bex = bx + int((random.random() - 0.5) * crack_len * 0.5)
            bey = by + int(crack_len * 0.15)
            draw.line((bx, by, bex, bey), fill=(180, 210, 240, int(15 + 35 * random.random())), width=1)

    # ---- Snow particles (falling) ----
    for _ in range(300):
        px = int(random.random() * W)
        py = int(random.random() * H)
        pr = 1 + int(3 * random.random())
        pa = int(60 + 140 * random.random())
        draw.ellipse((px - pr, py - pr, px + pr, py + pr), fill=(255, 255, 255, pa))

    # ---- Title panel at bottom (y=1920-2560) ----
    panel_top = 1920
    # Dark semi-transparent panel
    draw.rectangle((0, panel_top, W, H), fill=(8, 12, 25, 230))
    # Subtle ice-blue border at top of panel
    draw.line((80, panel_top, W - 80, panel_top), fill=(100, 180, 230, 150), width=3)
    # Thin accent below
    draw.line((200, panel_top + 8, W - 200, panel_top + 8), fill=(60, 120, 180, 80), width=1)

    # Genre / tagline
    gf = font("arial.ttf", 28)
    gfl = ["POST-APOCALYPTIC ARCTIC"]
    y = centered(draw, panel_top + 40, gfl, gf, (120, 200, 240, 200), 6)

    # Title — use arialbd.ttf per instructions
    tf = font("arialbd.ttf", 90)
    title_lines = wrap(draw, title.upper(), tf, 1200)
    y = centered(draw, y + 60, title_lines, tf, (255, 255, 255, 255), 8)

    # Author
    af = font("arial.ttf", 36)
    y = centered(draw, y + 80, [author], af, (180, 200, 220, 255), 6)

    # Bottom accent line
    draw.line((300, H - 50, W - 300, H - 50), fill=(100, 180, 230, 100), width=1)

    # ---- Save ----
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