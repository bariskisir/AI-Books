#!/usr/bin/env python3
"""Cover: The Riverboat Codex — seven worn clay poker chips with cipher symbols on dark green felt, riverboat silhouette on Mississippi."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel
from PIL import Image, ImageDraw, ImageFilter, ImageFont
import hashlib, random, os

BOOK_TITLE = "The Riverboat Codex"
AUTHOR = "Baris Kisir"
OUTPUT = os.path.join(os.path.dirname(__file__), "..", "covers", "The_Riverboat_Codex.png")

def generate_cover():
    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), (20, 40, 20))
    rng = random.Random(7)
    draw = ImageDraw.Draw(img)

    # Dark green felt table
    draw.rectangle([0, 500, W, 1500], fill=(25, 50, 25))
    for _ in range(30):
        fx = rng.randint(0, W)
        fy = rng.randint(500, 1500)
        draw.ellipse([fx, fy, fx + rng.randint(10, 50), fy + rng.randint(3, 8)], fill=(30, 60, 30, 100))

    # Felt edge
    draw.rectangle([0, 495, W, 505], fill=(45, 75, 45))
    draw.rectangle([0, 495, W, 500], fill=(60, 90, 60), width=3)

    # Seven clay poker chips with cipher symbols
    chip_positions = [(300, 850), (500, 780), (700, 720), (900, 760), (600, 980), (800, 920), (1100, 850)]
    cipher_symbols = ["◈", "△", "✧", "◉", "▣", "⟡", "◭"]
    for i, (cx, cy) in enumerate(chip_positions):
        # Clay chip body
        draw.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=(200, 170, 120))
        draw.ellipse([cx - 42, cy - 42, cx + 42, cy + 42], fill=(180, 150, 100))
        draw.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=(210, 180, 130))
        # Inner ring
        draw.ellipse([cx - 28, cy - 28, cx + 28, cy + 28], outline=(160, 130, 80), width=2)
        draw.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], outline=(140, 110, 70), width=1)
        # Worn edge effect
        for _ in range(6):
            wx = cx + rng.randint(-44, 44)
            wy = cy + rng.randint(-44, 44)
            if (wx - cx) ** 2 + (wy - cy) ** 2 > 1600:
                draw.ellipse([wx - 3, wy - 3, wx + 3, wy + 3], fill=(160, 130, 90))
        # Cipher symbol
        try:
            sf = ImageFont.truetype("C:/Windows/Fonts/seguiemj.ttf", 28)
        except:
            sf = ImageFont.load_default()
        bb = draw.textbbox((0, 0), cipher_symbols[i], font=sf)
        draw.text((cx - (bb[2] - bb[0]) // 2, cy - (bb[3] - bb[1]) // 2), cipher_symbols[i], font=sf, fill=(80, 50, 30))

    # Riverboat silhouette in background
    draw.polygon([(300, 480), (500, 480), (530, 420), (520, 500), (280, 500)], fill=(15, 20, 25, 150))
    draw.rectangle([(450, 430), (500, 480)], fill=(15, 20, 25, 150))
    draw.line([(300, 480), (1300, 480)], fill=(15, 20, 25, 120), width=4)

    # River and reflection
    draw.rectangle([0, 480, W, 500], fill=(60, 80, 100, 100))
    for _ in range(20):
        rx = rng.randint(0, W)
        draw.line([(rx, 485), (rx + rng.randint(20, 60), 488)], fill=(100, 120, 140, 60), width=1)

    # Lamp glow (riverboat lamp)
    lamp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ld = ImageDraw.Draw(lamp)
    ld.ellipse([400, 420, 440, 460], fill=(255, 200, 80, 150))
    ld.ellipse([380, 410, 460, 470], fill=(255, 200, 80, 60))
    lamp = lamp.filter(ImageFilter.GaussianBlur(10))
    img = Image.alpha_composite(img.convert("RGBA"), lamp).convert("RGB")

    _draw_standard_cover_title_panel(img, BOOK_TITLE, AUTHOR, "deepseek-v4-flash")
    img.save(OUTPUT, "PNG")
    print(f"Cover saved: {OUTPUT}")

if __name__ == "__main__":
    generate_cover()
