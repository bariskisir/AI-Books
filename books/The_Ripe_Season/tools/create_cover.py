#!/usr/bin/env python3
"""Cover: The Ripe Season — abstract geometric, warm off-white with scattered colored shapes, minimalist."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel
from PIL import Image, ImageDraw
import hashlib, random, os

BOOK_TITLE = "The Ripe Season"
AUTHOR = "Baris Kisir"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "covers", "The_Ripe_Season.png")

def generate_cover():
    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), "#f5f0eb")
    seed = int(hashlib.md5(BOOK_TITLE.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    draw = ImageDraw.Draw(img)

    # Scattered colored shapes on warm off-white
    for _ in range(30):
        x = rng.randint(0, W)
        y = rng.randint(0, 1800)
        s = rng.randint(30, 250)
        shape = rng.choice(["rect", "ellipse", "triangle"])
        color_hsl = "hsl(" + f"{rng.randint(0, 360)},{rng.randint(25, 60)}%,{rng.randint(45, 75)}%)"
        if shape == "rect":
            draw.rectangle([x, y, x + s, y + s], fill=color_hsl)
        elif shape == "ellipse":
            draw.ellipse([x, y, x + s, y + s], fill=color_hsl)
        else:
            draw.polygon([(x, y), (x + s, y), (x + s // 2, y - s)], fill=color_hsl)

    # A few smaller accent shapes
    for _ in range(15):
        x = rng.randint(0, W)
        y = rng.randint(0, 1800)
        sz = rng.randint(10, 50)
        draw.ellipse([x, y, x + sz, y + sz], fill="hsl(" + f"{rng.randint(0, 360)},{rng.randint(50, 80)}%,{rng.randint(30, 60)}%)")

    _draw_standard_cover_title_panel(img, BOOK_TITLE, AUTHOR, "deepseek-v4-flash")
    img.save(OUTPUT, "PNG")
    print(f"Cover saved: {OUTPUT}")
if __name__ == "__main__": generate_cover()
