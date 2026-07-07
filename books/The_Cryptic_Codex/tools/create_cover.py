#!/usr/bin/env python3
"""Generate book cover."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel
from PIL import Image, ImageDraw, ImageFont
import hashlib, random, os

BOOK_TITLE = "The Cryptic Codex"
AUTHOR = "Baris Kisir"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "covers", "The_Cryptic_Codex.png")

def generate_cover():
    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), "#f5f0eb")
    seed = int(hashlib.md5(BOOK_TITLE.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)
    draw = ImageDraw.Draw(img)
    for _ in range(60):
        x = rng.randint(0, W)
        y = rng.randint(0, H)
        s = rng.randint(40, 400)
        hue = rng.randint(0, 360)
        sat = rng.randint(30, 70)
        lig = rng.randint(40, 80)
        color = f"hsl({hue},{sat}%,{lig}%)"
        shape = rng.choice(["rect", "ellipse", "triangle"])
        if shape == "rect":
            draw.rectangle([x, y, x + s, y + s], fill=color, outline=None)
        elif shape == "ellipse":
            draw.ellipse([x, y, x + s, y + s], fill=color, outline=None)
        else:
            draw.polygon([(x, y), (x + s, y), (x + s // 2, y - s)], fill=color, outline=None)
    _draw_standard_cover_title_panel(img, BOOK_TITLE, AUTHOR, "deepseek-v4-flash")
    img.save(OUTPUT, "PNG")
    print(f"Cover saved: {OUTPUT}")

if __name__ == "__main__":
    generate_cover()
