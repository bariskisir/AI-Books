#!/usr/bin/env python3
"""Cover: The Noise Between Stars — deep space, starlight, observation deck, cosmic signal."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560

random.seed(42)


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "arialbd.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def make_gradient(draw):
    """Vertical gradient: deep space black at top, dark blue at bottom."""
    for y in range(H):
        t = y / H
        r = int(2 + 8 * t)
        g = int(2 + 12 * t)
        b = int(20 + 60 * t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))


def draw_stars(draw):
    """Draw field of stars with varying sizes and brightness."""
    for _ in range(600):
        x = random.randint(0, W)
        y = random.randint(0, H)
        size = random.choice([1, 1, 2, 2, 3])
        brightness = random.randint(100, 255)
        draw.ellipse(
            [x - size, y - size, x + size, y + size],
            fill=(brightness, brightness, brightness),
        )


def draw_planet(draw):
    """Draw a large distant planet in the upper-right quadrant."""
    cx, cy = W * 0.75, H * 0.25
    r = 180
    # Planet body
    for i in range(r * 2):
        for j in range(r * 2):
            dx, dy = i - r, j - r
            dist = math.sqrt(dx * dx + dy * dy)
            if dist <= r:
                # Gradient shading
                shade = 1.0 - (dist / r)
                rr = int(40 + 80 * shade)
                gg = int(30 + 60 * shade)
                bb = int(70 + 120 * shade)
                # Banding
                band = abs(int(dy * 0.05)) % 3
                if band == 1:
                    rr = max(0, rr - 20)
                    gg = max(0, gg - 15)
                    bb = max(0, bb - 30)
                draw.point((cx + dx, cy + dy), fill=(rr, gg, bb))
    # Crescent highlight
    for i in range(int(r * 0.8)):
        angle = math.radians(-30 + (i / (r * 0.8)) * 60)
        hx = cx + r * 0.6 * math.cos(angle)
        hy = cy + r * 0.6 * math.sin(angle)
        hr = random.randint(4, 8)
        draw.ellipse(
            [hx - hr, hy - hr, hx + hr, hy + hr],
            fill=(180, 160, 220),
        )


def draw_rings(draw):
    """Draw ring arcs around the planet."""
    cx, cy = W * 0.75, H * 0.25
    for angle_step in range(0, 360, 2):
        rad = math.radians(angle_step)
        x1 = cx + 220 * math.cos(rad)
        y1 = cy + 60 * math.sin(rad)
        x2 = cx + 260 * math.cos(rad + 0.02)
        y2 = cy + 75 * math.sin(rad + 0.02)
        x3 = cx + 260 * math.cos(rad + 0.04)
        y3 = cy + 75 * math.sin(rad + 0.04)
        alpha = random.randint(30, 80)
        draw.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(140, 130, 200, alpha))


def draw_observation_deck(draw):
    """Draw a stylized starship observation deck at the bottom of the upper section."""
    # Deck structure - a window frame
    deck_y = H * 0.55
    deck_w = W * 0.7
    deck_h = 220
    deck_x = (W - deck_w) / 2

    # Window frame (rectangular with rounded feel)
    frame_color = (40, 50, 60)
    draw.rectangle(
        [deck_x, deck_y - deck_h / 2, deck_x + deck_w, deck_y + deck_h / 2],
        outline=frame_color,
        width=6,
    )
    # Inner glow
    draw.rectangle(
        [deck_x + 6, deck_y - deck_h / 2 + 6, deck_x + deck_w - 6, deck_y + deck_h / 2 - 6],
        fill=(5, 10, 25),
        outline=(60, 70, 90),
        width=2,
    )

    # Deck floor / sill
    draw.rectangle(
        [deck_x - 30, deck_y + deck_h / 2 - 8, deck_x + deck_w + 30, deck_y + deck_h / 2 + 12],
        fill=(30, 35, 40),
    )

    # Support struts on the window
    strut_positions = [0.25, 0.5, 0.75]
    for sp in strut_positions:
        sx = deck_x + deck_w * sp
        draw.line(
            [(sx, deck_y - deck_h / 2 + 6), (sx, deck_y + deck_h / 2 - 8)],
            fill=(50, 55, 60),
            width=4,
        )

    # Figure silhouettes (two people at the window)
    fig_centers = [(deck_x + deck_w * 0.35, deck_y), (deck_x + deck_w * 0.65, deck_y)]
    for fcx, fcy in fig_centers:
        # Head
        draw.ellipse(
            [fcx - 10, fcy - 50, fcx + 10, fcy - 30],
            fill=(10, 12, 15),
        )
        # Body
        draw.rectangle(
            [fcx - 14, fcy - 30, fcx + 14, fcy + 15],
            fill=(10, 12, 15),
        )


def draw_cmb_map(draw):
    """Draw a stylized WMAP-style CMB map band across the middle."""
    band_y = H * 0.35
    band_h = 60
    # Draw a wavy band representing the CMB
    for x in range(0, W, 2):
        wave = math.sin(x * 0.01) * 10 + math.sin(x * 0.023) * 6 + math.sin(x * 0.047) * 3
        base_y = band_y + wave
        # Color varies by position (CMB temperature map style)
        t = x / W
        if t < 0.33:
            r, g, b = 220, 150, 80  # warm
        elif t < 0.66:
            r, g, b = 80, 120, 200  # cool
        else:
            r, g, b = 180, 80, 150  # purple
        draw.rectangle(
            [x, int(base_y - band_h / 2), x + 2, int(base_y + band_h / 2)],
            fill=(r, g, b),
        )


def draw_signal_waves(draw):
    """Draw concentric signal waves radiating from the CMB band."""
    cx, cy = W * 0.5, H * 0.38
    for radius in range(300, 900, 60):
        alpha = max(10, 40 - (radius - 300) // 20)
        draw.ellipse(
            [cx - radius, cy - radius, cx + radius, cy + radius],
            outline=(100, 180, 255, alpha),
            width=2,
        )


def draw_title_panel(draw):
    """Draw the dark title panel at the bottom with white text."""
    # Semi-transparent dark panel
    panel_y = 1920
    panel_h = H - panel_y  # 640 px
    for y in range(panel_y, H):
        t = (y - panel_y) / panel_h
        alpha = int(220 * (1.0 - t * 0.3))
        r = int(8 * (1.0 - t * 0.2))
        g = int(10 * (1.0 - t * 0.2))
        b = int(16 * (1.0 - t * 0.2))
        draw.line([(0, y), (W, y)], fill=(r, g, b, alpha))

    # Top accent line
    for x in range(0, W):
        brightness = 60 + int(30 * math.sin(x * 0.01))
        draw.point((x, panel_y), fill=(brightness, brightness, brightness))
        draw.point((x, panel_y + 1), fill=(brightness // 2, brightness // 2, brightness // 2))

    fnt_title = font("arialbd.ttf", 80)
    fnt_author = font("arial.ttf", 32)
    fnt_tagline = font("arial.ttf", 20)

    draw = draw  # already have it

    # Title
    title = "The Noise Between Stars"
    tw = draw.textbbox((0, 0), title, font=fnt_title)[2]
    tx = (W - tw) / 2
    ty = panel_y + 140
    # Drop shadow
    draw.text((tx + 3, ty + 3), title, fill=(0, 0, 0), font=fnt_title)
    draw.text((tx, ty), title, fill=(255, 255, 255), font=fnt_title)

    # Author
    author = "Barış Kısır"
    aw = draw.textbbox((0, 0), author, font=fnt_author)[2]
    ax = (W - aw) / 2
    ay = ty + 120
    draw.text((ax + 2, ay + 2), author, fill=(0, 0, 0), font=fnt_author)
    draw.text((ax, ay), author, fill=(200, 210, 230), font=fnt_author)

    # Tagline (like "A Hard Sci-Fi Novel" but not "A Novel of")
    tagline = "A Hard Sci-Fi Novel"
    tw2 = draw.textbbox((0, 0), tagline, font=fnt_tagline)[2]
    tx2 = (W - tw2) / 2
    ty2 = ay + 60
    draw.text((tx2 + 1, ty2 + 1), tagline, fill=(0, 0, 0), font=fnt_tagline)
    draw.text((tx2, ty2), tagline, fill=(120, 140, 180), font=fnt_tagline)



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
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    if args.metadata:
        meta = json.loads(Path(args.metadata).read_text(encoding="utf-8"))
        paths = meta.get("paths", {})
        out = ROOT / Path(args.out) if args.out else ROOT / Path(paths.get("cover", "cover.png"))
    else:
        out = ROOT / Path(args.out) if args.out else ROOT / "cover.png"

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Build layers
    make_gradient(draw)
    draw_stars(draw)
    draw_cmb_map(draw)
    draw_signal_waves(draw)
    draw_planet(draw)
    draw_rings(draw)
    draw_observation_deck(draw)
    draw_title_panel(draw)

    out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()))
    img.save(out)
    print(f"Cover saved to: {out}")


if __name__ == "__main__":
    main()