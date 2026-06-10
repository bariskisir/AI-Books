#!/usr/bin/env python3
"""Cover: The Silent Vowels - courtroom listening room, spectrogram river, vowel chart, microphone, quay windows."""
from __future__ import annotations
import argparse, json, random, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont
ROOT = Path(__file__).resolve().parents[3]
FONT_DIR = Path("C:/Windows/Fonts")
W, H = 1600, 2560
PANEL_Y = 1765

def font(name, size):
    for c in [FONT_DIR / name, FONT_DIR / "georgia.ttf", FONT_DIR / "arial.ttf"]:
        if c.exists(): return ImageFont.truetype(str(c), size)
    return ImageFont.load_default()

def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))

def make_cover(mp, op):
    metadata=json.loads(mp.read_text(encoding="utf-8"))
    title=metadata.get("title", "The Silent Vowels")
    author=metadata.get("author", "Barış Kısır")
    model=metadata.get("model", "")
    random.seed("silent-vowels-cover-redesign")
    img=Image.new("RGBA",(W,H),(14,18,24,255))
    draw=ImageDraw.Draw(img,"RGBA")

    # A dark listening room, not a courtroom window tableau.
    for y in range(PANEL_Y):
        t=y/PANEL_Y
        c=lerp((10,22,34),(42,42,54),t) if t<.55 else lerp((42,42,54),(20,24,30),(t-.55)/.45)
        draw.line((0,y,W,y),fill=(*c,255))

    # Oversized cassette as the physical evidence.
    cassette = (180, 390, 1420, 1140)
    draw.rounded_rectangle(cassette, radius=48, fill=(226, 218, 190, 245), outline=(46, 50, 56, 255), width=10)
    draw.rounded_rectangle((260, 500, 1340, 730), radius=22, fill=(28, 34, 42, 255), outline=(93, 98, 102, 180), width=4)
    draw.rectangle((420, 760, 1180, 995), fill=(205, 197, 171, 255), outline=(76, 70, 58, 180), width=4)
    draw.text((505, 805), "EXHIBIT 14B", font=font("arialbd.ttf", 54), fill=(42, 44, 48, 240))
    draw.text((510, 875), "RAW CALL - DO NOT SUMMARIZE", font=font("arial.ttf", 34), fill=(74, 68, 58, 230))

    # Reels and magnetic tape.
    for cx, cy in [(470, 615), (1130, 615)]:
        draw.ellipse((cx-145, cy-145, cx+145, cy+145), fill=(34, 40, 48, 255), outline=(222, 216, 188, 220), width=8)
        for a in range(0, 360, 60):
            rad = math.radians(a)
            draw.ellipse((cx + 74*math.cos(rad)-20, cy + 74*math.sin(rad)-20, cx + 74*math.cos(rad)+20, cy + 74*math.sin(rad)+20), fill=(214, 206, 176, 240))
        draw.ellipse((cx-32, cy-32, cx+32, cy+32), fill=(224, 218, 190, 255))
    draw.arc((470, 540, 1130, 840), 190, 350, fill=(54, 42, 38, 230), width=16)

    # Spectrogram strip as a torn piece of analysis paper.
    strip = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(strip, "RGBA")
    sd.polygon([(95, 1190), (1505, 1070), (1515, 1360), (110, 1515)], fill=(10, 15, 22, 238), outline=(218, 218, 192, 190))
    for i in range(150):
        x = 135 + i * 9
        y = 1342 - i * 0.75
        amp = 34 + 52 * abs(math.sin(i * 0.19)) + random.randint(-14, 14)
        color = random.choice([(56, 190, 184, 150), (236, 192, 76, 140), (203, 74, 96, 135), (122, 216, 144, 130)])
        sd.line((x, y - amp, x, y + amp), fill=color, width=5)
    sd.rectangle((760, 1130, 835, 1450), fill=(4, 7, 12, 245), outline=(238, 230, 180, 220), width=3)
    img = Image.alpha_composite(img, strip)
    draw = ImageDraw.Draw(img, "RGBA")

    # Mouth profile and the missing vowel dot.
    profile = [(300, 1535), (515, 1445), (665, 1480), (600, 1535), (705, 1595), (560, 1625), (390, 1600)]
    draw.polygon(profile, fill=(188, 150, 126, 235), outline=(58, 42, 40, 180))
    draw.line((520, 1538, 690, 1538), fill=(78, 48, 46, 220), width=5)
    draw.ellipse((770, 1518, 810, 1558), fill=(184, 30, 52, 255))
    draw.line((790, 1538, 930, 1438), fill=(184, 30, 52, 210), width=5)
    draw.text((950, 1400), "missing vowel", font=font("georgia.ttf", 46), fill=(232, 222, 190, 235))

    # Court transcript lines are present, but dim and secondary.
    for i in range(7):
        y = 170 + i * 38
        draw.line((185, y, 1415 - i * 60, y), fill=(210, 212, 190, 45), width=4)
    sf=font("georgia.ttf",34); desc="AUDIO EVIDENCE · DIALECT · DOUBT"
    bb=draw.textbbox((0,0),desc,font=sf); draw.text(((W-(bb[2]-bb[0]))//2,300),desc,font=sf,fill=(230,220,188,235))
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.convert("RGB").save(op,"PNG", optimize=True)

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
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=(88, 92, 82, 170), width=3)
    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in title_lines)
    title_height += max(0, len(title_lines) - 1) * title_gap
    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height
    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, (52, 58, 52), title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, (86, 88, 74), 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, (112, 112, 94), 6, width)


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path); a=p.parse_args()
    make_cover(ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT / a.out if not a.out.is_absolute() else a.out)
if __name__ == "__main__": main()
