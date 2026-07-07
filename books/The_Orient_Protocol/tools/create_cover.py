#!/usr/bin/env python3
"""Cover: The Orient Protocol — Orient Express interior, locked-room murder scene, Istanbul backdrop."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel, _standard_cover_resolve_title, _standard_cover_resolve_author
from PIL import Image, ImageDraw, ImageFilter
import json
import math

BOOK_TITLE = "The Orient Protocol"
AUTHOR = "Baris Kisir"

def generate_cover(metadata_path=None, output_path=None):
    W, H = 1600, 2560
    model = ""
    if metadata_path:
        meta = json.loads(Path(metadata_path).read_text(encoding="utf-8"))
        model = meta.get("model", "")
    if output_path is None:
        output_path = Path(__file__).resolve().parents[2] / "covers" / "The_Orient_Protocol.png"
    else:
        output_path = Path(output_path)

    img = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img, "RGBA")

    # Orient Express interior — warm mahogany, brass, velvet
    for y in range(H):
        t = y / H
        r = int(45 + 20 * t); g = int(18 + 10 * t); b = int(12 + 8 * t)
        draw.line((0, y, W, y), fill=(r, g, b, 255))

    # Wood-paneled carriage walls
    draw.rectangle((0, 200, W, 900), fill=(55, 25, 18, 200))
    for i in range(8):
        px = i * 220
        draw.rectangle((px, 200, px + 4, 900), fill=(80, 40, 28, 180))
    # Brass fixtures
    for bx in [100, 400, 700, 1000, 1300]:
        draw.ellipse((bx - 12, 895, bx + 12, 915), fill=(180, 150, 70, 200))

    # Compartment windows showing Istanbul backdrop
    for i, wx in enumerate([120, 450, 780, 1110]):
        draw.rectangle((wx, 240, wx + 130, 380), fill=(180, 160, 140, 100))
        draw.rectangle((wx, 240, wx + 130, 380), outline=(180, 150, 70), width=3)
        # Istanbul skyline through window
        draw.polygon([(wx+10,370),(wx+30,310),(wx+50,350),(wx+70,280),(wx+90,340),(wx+120,300),(wx+125,370)], fill=(60,50,40,120))
        # Minaret silhouettes
        draw.rectangle((wx+40,280,wx+44,350), fill=(50,45,40,100))
        draw.polygon([(wx+40,280),(wx+42,265),(wx+44,280)], fill=(50,45,40,100))
        draw.rectangle((wx+90,300,wx+94,360), fill=(50,45,40,100))
        draw.polygon([(wx+90,300),(wx+92,285),(wx+94,300)], fill=(50,45,40,100))
        # Sunset sky in window
        for wy in range(240, 380):
            t = (wy-240)/140
            draw.line((wx, wy, wx+130, wy), fill=(int(200-100*t), int(120-80*t), int(60-40*t), 60))

    # Locked-room murder scene — body silhouette on floor
    body_x, body_y = W//2, 1000
    draw.polygon([(body_x-60,body_y),(body_x+60,body_y),(body_x+50,body_y+60),(body_x-50,body_y+60)], fill=(20,12,10,200))
    draw.ellipse((body_x-15,body_y-40,body_x+15,body_y-10), fill=(18,10,8,200))
    # Red stain
    draw.ellipse((body_x-20,body_y+50,body_x+20,body_y+75), fill=(120,15,10,150))

    # Train seats — velvet upholstery
    for sx in [100, 500, 900, 1300]:
        draw.rectangle((sx, 700, sx+120, 880), fill=(90,25,30,200))
        draw.rectangle((sx+5, 705, sx+115, 875), fill=(100,30,35,180))

    # Brass lamp glow
    for lx in [200, 600, 1000, 1400]:
        lamp_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ld = ImageDraw.Draw(lamp_glow)
        ld.ellipse((lx-60, 500-40, lx+60, 500+40), fill=(255, 200, 100, 40))
        lamp_glow = lamp_glow.filter(ImageFilter.GaussianBlur(20))
        img = Image.alpha_composite(img, lamp_glow)
        draw = ImageDraw.Draw(img, "RGBA")

    # Title
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(str(output_path), "PNG", optimize=True)
    print(f"Cover saved: {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path, default=None)
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()
    generate_cover(args.metadata, args.out)
