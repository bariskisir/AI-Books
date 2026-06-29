#!/usr/bin/env python3
"""Cover: The Silent Vowels - courtroom listening room, spectrogram river, vowel chart, microphone, quay windows."""
from __future__ import annotations
import argparse, json, random, math
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import (
    _standard_cover_font,
    _standard_cover_repair_text,
    _standard_cover_wrap,
    _standard_cover_center,
    _standard_cover_title_font,
    _standard_cover_metadata_from_locals,
    _standard_cover_resolve_title,
    _standard_cover_resolve_author,
    _draw_standard_cover_title_panel,
)

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
    model = metadata.get("model", "")
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


def main():
    p=argparse.ArgumentParser(); p.add_argument("--metadata", required=True, type=Path); p.add_argument("--out", required=True, type=Path); a=p.parse_args()
    make_cover(ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata, ROOT / a.out if not a.out.is_absolute() else a.out)
if __name__ == "__main__": main()
