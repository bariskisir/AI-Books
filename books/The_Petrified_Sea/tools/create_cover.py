#!/usr/bin/env python3
"""Cover: The Petrified Sea — Kansas chalk bluff at dusk, embedded mosasaur skeleton,
jaws closed on a plesiosaur paddle, strata bands, prairie, swallows, ammonite."""

from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560
PANEL_Y = 1765


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists():
            return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()


def lerp(a, b, t):
    return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))


def make_cover(mp, op):
    m = json.loads(mp.read_text(encoding="utf-8"))
    title = m.get("title", "The Petrified Sea")
    author = m.get("author", "Barış Kısır")
    model = m.get("model", "")

    random.seed("petrified-sea")
    img = Image.new("RGBA", (W, H), (20, 24, 40, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # ---- Dusk sky: deep indigo down to rose-amber at the horizon ----
    horizon = 1040
    sky_top = (24, 28, 58)
    sky_mid = (96, 74, 102)
    sky_low = (224, 142, 92)
    for y in range(0, horizon):
        t = y / horizon
        c = lerp(sky_top, sky_mid, t / 0.62) if t < 0.62 else lerp(sky_mid, sky_low, (t - 0.62) / 0.38)
        draw.line((0, y, W, y), fill=(*c, 255))

    # Thin evening cloud bands catching the last light
    for cy, cw, alpha in [(330, 520, 38), (430, 760, 46), (560, 980, 54), (700, 1240, 62), (840, 1420, 70)]:
        band = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        bd = ImageDraw.Draw(band)
        cx = W // 2 + random.randint(-260, 260)
        bd.ellipse((cx - cw, cy - 16, cx + cw, cy + 16), fill=(244, 176, 128, alpha))
        band = band.filter(ImageFilter.GaussianBlur(12))
        img = Image.alpha_composite(img, band)
    draw = ImageDraw.Draw(img, "RGBA")

    # First stars high in the dusk
    for _ in range(70):
        sx = random.randint(20, W - 20)
        sy = random.randint(20, 460)
        r = random.choice([1, 1, 1, 2])
        a = random.randint(90, 200)
        draw.ellipse((sx - r, sy - r, sx + r, sy + r), fill=(235, 238, 250, a))
    # One bright evening star
    ex, ey = 1180, 200
    draw.ellipse((ex - 3, ey - 3, ex + 3, ey + 3), fill=(255, 255, 245, 255))
    draw.line((ex - 12, ey, ex + 12, ey), fill=(255, 255, 245, 130), width=1)
    draw.line((ex, ey - 12, ex, ey + 12), fill=(255, 255, 245, 130), width=1)

    # Swallows stitching the air
    for bx, by, s in [(420, 560, 13), (520, 610, 10), (980, 470, 15), (1110, 530, 11), (700, 380, 9)]:
        draw.arc((bx - s, by - s // 2, bx, by + s // 2), 200, 340, fill=(40, 32, 44, 220), width=3)
        draw.arc((bx, by - s // 2, bx + s, by + s // 2), 200, 340, fill=(40, 32, 44, 220), width=3)

    # ---- Distant prairie flats behind the river ----
    draw.rectangle((0, horizon, W, horizon + 90), fill=(92, 70, 70, 255))
    for y in range(horizon, horizon + 90, 4):
        t = (y - horizon) / 90
        draw.line((0, y, W, y), fill=(*lerp((118, 88, 82), (70, 56, 60), t), 255))
    # The Smoky Hill river: a pale band catching the sky
    draw.rectangle((0, horizon + 56, W, horizon + 78), fill=(214, 150, 116, 255))
    draw.line((0, horizon + 56, W, horizon + 56), fill=(238, 178, 134, 255), width=2)

    # ---- The chalk bluff: great white face filling the middle ground ----
    bluff_top = horizon + 130
    bluff_bot = PANEL_Y
    # Fluted skyline of the bluff cap
    cap = [(0, bluff_top + 60)]
    x = 0
    while x < W:
        step = random.randint(70, 150)
        x = min(W, x + step)
        cap.append((x, bluff_top + random.randint(0, 86)))
    face_poly = cap + [(W, bluff_bot), (0, bluff_bot)]
    draw.polygon(face_poly, fill=(222, 214, 196, 255))

    # Sod cap on top of the chalk
    for i in range(len(cap) - 1):
        (x0, y0), (x1, y1) = cap[i], cap[i + 1]
        draw.line((x0, y0 - 4, x1, y1 - 4), fill=(74, 62, 52, 255), width=14)
        draw.line((x0, y0 - 14, x1, y1 - 14), fill=(96, 84, 60, 255), width=8)

    # Strata bands: the ledger of the old sea
    bands = [
        (1255, 16, (196, 184, 158)), (1300, 8, (178, 162, 138)), (1352, 22, (206, 194, 170)),
        (1430, 12, (184, 168, 142)), (1488, 26, (212, 200, 178)), (1560, 10, (176, 158, 134)),
        (1610, 18, (200, 188, 164)), (1680, 12, (186, 170, 146)), (1730, 20, (208, 196, 172)),
    ]
    for by, bh, bc in bands:
        wob = random.randint(-6, 6)
        draw.rectangle((0, by + wob, W, by + bh + wob), fill=(*bc, 255))

    # Weathering flutes: vertical rain-cut shadows down the face
    for _ in range(46):
        fx = random.randint(10, W - 10)
        fy0 = bluff_top + random.randint(40, 120)
        fy1 = bluff_bot - random.randint(0, 60)
        fa = random.randint(14, 38)
        fw = random.choice([2, 3, 4, 6])
        draw.line((fx, fy0, fx + random.randint(-8, 8), fy1), fill=(140, 124, 104, fa), width=fw)

    # Fresh spall scar: the storm-opened panel where the fossil shows
    scar = (170, 1290, 1430, 1700)
    draw.rounded_rectangle(scar, radius=46, fill=(238, 232, 216, 255))
    draw.rounded_rectangle(scar, radius=46, outline=(168, 152, 128, 200), width=4)
    # Faint bedding inside the scar
    for sy in range(scar[1] + 36, scar[3] - 20, 46):
        draw.line((scar[0] + 18, sy, scar[2] - 18, sy), fill=(206, 196, 176, 120), width=3)

    # ---- The fossil: skull in profile, jaws closed on a fanned paddle ----
    bone = (122, 88, 56)
    bone_dk = (88, 60, 36)
    stain = (180, 160, 132)
    sx0, sy0 = 280, 1430  # snout reference point

    # Decay stain halo around the skeleton
    halo = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    hd = ImageDraw.Draw(halo)
    hd.ellipse((sx0 - 80, sy0 - 110, sx0 + 700, sy0 + 130), fill=(*stain, 70))
    hd.ellipse((sx0 + 600, sy0 - 90, scar[2] + 40, sy0 + 100), fill=(*stain, 55))
    halo = halo.filter(ImageFilter.GaussianBlur(22))
    img = Image.alpha_composite(img, halo)
    draw = ImageDraw.Draw(img, "RGBA")

    # Skull: long low wedge, facing left
    skull = [
        (sx0, sy0),                      # snout tip
        (sx0 + 150, sy0 - 58),           # top of snout
        (sx0 + 320, sy0 - 84),           # forehead
        (sx0 + 430, sy0 - 66),           # orbit ridge
        (sx0 + 520, sy0 - 18),           # rear skull
        (sx0 + 470, sy0 + 40),           # jaw joint
        (sx0 + 120, sy0 + 52),           # lower jaw line
    ]
    draw.polygon(skull, fill=bone, outline=bone_dk)
    # Orbit (eye ring)
    ox, oy = sx0 + 380, sy0 - 38
    draw.ellipse((ox - 26, oy - 26, ox + 26, oy + 26), fill=(238, 232, 216, 255), outline=bone_dk, width=4)
    draw.ellipse((ox - 11, oy - 11, ox + 11, oy + 11), fill=bone_dk)
    # Jaw seam
    draw.line((sx0 + 8, sy0 + 6, sx0 + 470, sy0 + 30), fill=bone_dk, width=5)
    # Teeth: conical, recurved, along the gape
    for i in range(13):
        t = i / 12
        tx = sx0 + 16 + t * 420
        ty = sy0 + 8 + t * 22
        th = 26 - 10 * abs(t - 0.4)
        draw.polygon([(tx, ty - 4), (tx + 9, ty - 4), (tx + 3, ty + th)], fill=(232, 224, 204, 255), outline=bone_dk)
    # Skull sutures
    draw.line((sx0 + 150, sy0 - 58, sx0 + 190, sy0 - 6), fill=bone_dk, width=3)
    draw.line((sx0 + 320, sy0 - 84, sx0 + 330, sy0 - 16), fill=bone_dk, width=3)

    # The paddle held crosswise in the jaws: five fanned files of small square bones
    px, py = sx0 + 150, sy0 + 26
    for f in range(5):
        ang = math.radians(116 + f * 17)
        for k in range(7):
            r = 26 + k * 21
            bxx = px + r * math.cos(ang)
            byy = py + r * math.sin(ang)
            s = 9 - k * 0.7
            draw.rectangle((bxx - s, byy - s, bxx + s, byy + s), fill=(214, 196, 162, 255), outline=bone_dk)

    # Vertebral column running aft into the unbroken chalk
    vx = sx0 + 540
    vy = sy0 - 6
    for i in range(14):
        r = 30 if i < 9 else 30 - (i - 8) * 2
        gap = 70 if i < 9 else 64
        cx = vx + i * gap
        cy = vy + int(10 * math.sin(i * 0.55))
        if cx - r > scar[2] - 26:
            # beyond the scar: ghost disks fading into the face
            a = max(40, 160 - (cx - scar[2]) // 2)
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(*bone_dk, a), width=5)
            continue
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=bone, outline=bone_dk, width=3)
        draw.ellipse((cx - r // 2.4, cy - r // 2.4, cx + r // 2.4, cy + r // 2.4), fill=(150, 112, 74, 255))
        # Neural spine
        draw.polygon([(cx - 8, cy - r), (cx + 8, cy - r), (cx + 2, cy - r - 34)], fill=bone, outline=bone_dk)
        # Rib arcing down
        if 1 < i < 11:
            draw.arc((cx - 56, cy + 4, cx + 24, cy + 150), 300, 420, fill=(*bone_dk, 230), width=7)

    # Ammonite coiled in the lower corner of the scar
    ax, ay = 1280, 1622
    for k in range(40):
        th = k * 0.42
        r = 4 + k * 1.35
        x1 = ax + r * math.cos(th)
        y1 = ay + r * math.sin(th)
        draw.ellipse((x1 - 3, y1 - 3, x1 + 3, y1 + 3), fill=(150, 122, 88, 235))

    # ---- Foreground: spall pile, grass, the small figure for scale ----
    draw.polygon([(0, PANEL_Y), (0, 1690), (240, 1700), (430, 1726), (640, 1712),
                  (900, 1734), (1180, 1716), (1420, 1732), (W, 1704), (W, PANEL_Y)],
                 fill=(168, 152, 128, 255))
    for _ in range(110):
        gx = random.randint(0, W)
        gy = random.randint(1700, PANEL_Y - 6)
        draw.ellipse((gx - 5, gy - 3, gx + 5, gy + 3), fill=(196, 184, 160, random.randint(90, 200)))
    # Dry bunch grass tufts
    for _ in range(46):
        gx = random.randint(8, W - 8)
        gy = random.randint(1708, PANEL_Y - 4)
        for b in range(5):
            draw.line((gx, gy, gx + random.randint(-12, 12), gy - random.randint(10, 24)),
                      fill=(110, 92, 62, 220), width=2)

    # Nell: small dark figure with a long skirt, sketchbook in hand, before the scar
    fx, fy = 760, 1718
    draw.polygon([(fx - 14, fy), (fx + 14, fy), (fx + 8, fy - 52), (fx - 8, fy - 52)], fill=(38, 30, 34, 255))
    draw.rectangle((fx - 7, fy - 78, fx + 7, fy - 50), fill=(38, 30, 34, 255))
    draw.ellipse((fx - 8, fy - 96, fx + 8, fy - 80), fill=(38, 30, 34, 255))
    draw.line((fx - 12, fy - 88, fx + 14, fy - 92), fill=(38, 30, 34, 255), width=4)  # bonnet brim
    draw.rectangle((fx + 7, fy - 66, fx + 22, fy - 56), fill=(58, 46, 40, 255))      # sketchbook
    # Her long shadow toward the viewer
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse((fx - 60, fy - 6, fx + 60, fy + 14), fill=(50, 40, 36, 90))
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    img = Image.alpha_composite(img, sh)
    draw = ImageDraw.Draw(img, "RGBA")

    # Descriptor line in the clear amber sky above the horizon
    sf = font("georgia.ttf", 36)
    desc = "THE NIOBRARA CHALK · KANSAS · 1876"
    bb = draw.textbbox((0, 0), desc, font=sf)
    draw.text(((W - (bb[2] - bb[0])) // 2, 944), desc, font=sf, fill=(58, 42, 38, 255))

    # ---- Standard title panel ----
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
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


def _draw_standard_cover_title_panel(image, title: str = "", author: str = "", model: str = "") -> None:
    width = int(globals().get("W", globals().get("WIDTH", 1600)))
    height = int(globals().get("H", globals().get("HEIGHT", 2560)))
    panel_y = 1765
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    model = _standard_cover_repair_text(str(model or "")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=(236, 230, 216, 255))
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(110, 84, 56, 170), width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (74, 56, 40), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (108, 80, 52), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (124, 104, 82), 6, width)


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
