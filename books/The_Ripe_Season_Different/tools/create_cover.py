#!/usr/bin/env python3
"""Cover: The Ripe Season (Different) — robin's-egg blue farmhouse door, cutting board with heirloom tomatoes, basil, coastal mist."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel
from PIL import Image, ImageDraw, ImageFilter
import hashlib, random, os

BOOK_TITLE = "The Ripe Season (Alternate Draft)"
AUTHOR = "Baris Kisir"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "covers", "The_Ripe_Season_Different.png")

def generate_cover():
    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), (178, 210, 225))
    rng = random.Random(17)
    draw = ImageDraw.Draw(img)

    # Robin's-egg blue farmhouse door
    door_x, door_y = W // 2 - 120, 200
    door_w, door_h = 240, 500
    draw.rectangle([door_x, door_y, door_x + door_w, door_y + door_h], fill=(120, 170, 200))
    draw.rectangle([door_x - 6, door_y - 6, door_x + door_w + 6, door_y + door_h + 6], outline=(90, 140, 170), width=4)
    # Door panels
    draw.rectangle([door_x + 20, door_y + 30, door_x + door_w - 20, door_y + 150], outline=(100, 155, 185), width=3)
    draw.rectangle([door_x + 20, door_y + 180, door_x + door_w - 20, door_y + 300], outline=(100, 155, 185), width=3)
    draw.rectangle([door_x + 20, door_y + 330, door_x + door_w - 20, door_y + 440], outline=(100, 155, 185), width=3)
    # Door knob
    draw.ellipse([door_x + door_w - 40, door_y + door_h // 2, door_x + door_w - 25, door_y + door_h // 2 + 15], fill=(180, 160, 80))
    # Window on door
    draw.rectangle([door_x + 35, door_y + 40, door_x + door_w - 35, door_y + 130], fill=(200, 225, 235, 180))

    # Cutting board below
    cb_x, cb_y = W // 2 - 100, 780
    cb_w, cb_h = 200, 50
    draw.rounded_rectangle([cb_x, cb_y, cb_x + cb_w, cb_y + cb_h], radius=8, fill=(180, 140, 80))
    draw.rounded_rectangle([cb_x + 3, cb_y + 3, cb_x + cb_w - 3, cb_y + cb_h - 3], radius=6, fill=(200, 160, 100))

    # Heirloom tomatoes on cutting board
    for i in range(5):
        tx = cb_x + 30 + i * 35 + rng.randint(-5, 5)
        ty = cb_y - 15 + rng.randint(-5, 5)
        tr = 18 + rng.randint(0, 8)
        r_shade = rng.randint(180, 220)
        draw.ellipse([tx - tr, ty - tr, tx + tr, ty + tr], fill=(r_shade, 40, 30))
        draw.ellipse([tx - tr + 3, ty - tr + 3, tx + tr - 3, ty + tr - 3], fill=(min(255, r_shade + 20), 50, 35))
        # Stem
        draw.line([(tx, ty - tr), (tx, ty - tr - 6)], fill=(50, 80, 30), width=2)

    # Basil leaves scattered
    for _ in range(8):
        bx = cb_x + rng.randint(20, cb_w - 20)
        by = cb_y + rng.randint(-25, 10)
        draw.ellipse([bx - 8, by - 4, bx + 8, by + 4], fill=(60, 120, 40))
        draw.ellipse([bx - 5, by - 2, bx + 5, by + 2], fill=(80, 150, 55))

    # Coastal mist at bottom
    mist = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    md = ImageDraw.Draw(mist)
    md.ellipse([-100, 1100, W + 100, 1400], fill=(200, 220, 230, 60))
    mist = mist.filter(ImageFilter.GaussianBlur(30))
    img = Image.alpha_composite(img.convert("RGBA"), mist).convert("RGB")

    _draw_standard_cover_title_panel(img, BOOK_TITLE, AUTHOR, "deepseek-v4-flash")
    img.save(OUTPUT, "PNG")
    print(f"Cover saved: {OUTPUT}")
if __name__ == "__main__": generate_cover()
