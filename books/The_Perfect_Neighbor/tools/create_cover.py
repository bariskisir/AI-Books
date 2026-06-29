#!/usr/bin/env python3
"""Generate a 1600x2560 cover image for The Perfect Neighbor."""

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageFilter

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



def create_cover(metadata_path: Path, output_path: Path) -> None:
    with open(metadata_path, encoding="utf-8") as f:
        metadata = json.load(f)

    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    W, H = 1600, 2560
    img = Image.new("RGB", (W, H), "#1a1a2e")
    draw = ImageDraw.Draw(img)

    # Gradient background: dark blue at top, purple in middle, dark teal at bottom
    for y in range(H):
        ratio = y / H
        if ratio < 0.5:
            r = int(26 + (40 - 26) * (ratio / 0.5))
            g = int(26 + (30 - 26) * (ratio / 0.5))
            b = int(46 + (60 - 46) * (ratio / 0.5))
        else:
            r = int(40 + (20 - 40) * ((ratio - 0.5) / 0.5))
            g = int(30 + (45 - 30) * ((ratio - 0.5) / 0.5))
            b = int(60 + (55 - 60) * ((ratio - 0.5) / 0.5))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # Draw suburban street scene in upper 75%
    # Horizon at y = 1400
    horizon = 1400

    # Sky glow - a subtle lighter band near horizon
    for y in range(horizon - 200, horizon):
        glow = int(20 * (1 - abs(y - (horizon - 100)) / 100))
        draw.line([(0, y), (W, y)], fill=(40 + glow, 45 + glow, 55 + glow))

    # Distant trees silhouette along horizon
    tree_color = (25, 28, 40)
    for x in range(0, W, 4):
        # Random tree height using sin for natural look
        tree_h = int(30 + 20 * (x * 0.003 % 7))
        draw.line([(x, horizon - tree_h), (x, horizon)], fill=tree_color)

    # Street / road at horizon
    draw.rectangle([(0, horizon), (W, horizon + 80)], fill=(35, 35, 45))

    # Sidewalk
    draw.rectangle([(0, horizon + 80), (W, horizon + 100)], fill=(60, 60, 70))

    # Lawn area
    draw.rectangle([(0, horizon + 100), (W, 1600)], fill=(35, 50, 35))

    # === Houses ===

    # House 1 - Perfect house (Becca's), left side, well-lit
    h1_x, h1_y = 100, horizon - 250
    h1_w, h1_h = 350, 250
    # House body
    draw.rectangle([(h1_x, h1_y), (h1_x + h1_w, h1_y + h1_h)], fill=(70, 65, 55))
    # Roof
    draw.polygon([(h1_x - 20, h1_y), (h1_x + h1_w // 2, h1_y - 60), (h1_x + h1_w + 20, h1_y)], fill=(55, 50, 40))
    # Front door
    draw.rectangle([(h1_x + 120, h1_y + 160), (h1_x + 180, h1_y + h1_h)], fill=(90, 60, 40))
    # Warm lit windows
    draw.rectangle([(h1_x + 30, h1_y + 60), (h1_x + 100, h1_y + 120)], fill=(255, 220, 150))
    draw.rectangle([(h1_x + 200, h1_y + 60), (h1_x + 270, h1_y + 120)], fill=(255, 220, 150))
    # Upper window lit
    draw.rectangle([(h1_x + 120, h1_y + 30), (h1_x + 180, h1_y + 70)], fill=(255, 220, 150))
    # Garage
    draw.rectangle([(h1_x + h1_w + 20, h1_y + 50), (h1_x + h1_w + 130, h1_y + h1_h)], fill=(55, 50, 45))
    draw.rectangle([(h1_x + h1_w + 30, h1_y + 80), (h1_x + h1_w + 120, h1_y + h1_h - 20)], fill=(45, 40, 35))
    # Garage door lines
    for gy in range(h1_y + 80, h1_y + h1_h - 10, 25):
        draw.line([(h1_x + h1_w + 30, gy), (h1_x + h1_w + 120, gy)], fill=(55, 50, 45))

    # House 2 - Claire's house, center, darker
    h2_x, h2_y = 600, horizon - 230
    h2_w, h2_h = 380, 230
    draw.rectangle([(h2_x, h2_y), (h2_x + h2_w, h2_y + h2_h)], fill=(60, 55, 45))
    # Roof
    draw.polygon([(h2_x - 15, h2_y), (h2_x + h2_w // 2, h2_y - 50), (h2_x + h2_w + 15, h2_y)], fill=(45, 40, 35))
    # Front door
    draw.rectangle([(h2_x + 150, h2_y + 140), (h2_x + 210, h2_y + h2_h)], fill=(80, 50, 35))
    # Windows - one lit, one dark
    draw.rectangle([(h2_x + 30, h2_y + 50), (h2_x + 100, h2_y + 110)], fill=(255, 180, 100))
    draw.rectangle([(h2_x + 240, h2_y + 50), (h2_x + 310, h2_y + 110)], fill=(30, 25, 35))
    # Upper window - dim
    draw.rectangle([(h2_x + 150, h2_y + 25), (h2_x + 210, h2_y + 60)], fill=(80, 60, 70))
    # Garage
    draw.rectangle([(h2_x + h2_w + 10, h2_y + 50), (h2_x + h2_w + 120, h2_y + h2_h)], fill=(50, 45, 40))

    # House 3 - Distant background house, right side
    h3_x, h3_y = 1100, horizon - 200
    h3_w, h3_h = 300, 200
    draw.rectangle([(h3_x, h3_y), (h3_x + h3_w, h3_y + h3_h)], fill=(55, 50, 42))
    draw.polygon([(h3_x - 10, h3_y), (h3_x + h3_w // 2, h3_y - 40), (h3_x + h3_w + 10, h3_y)], fill=(40, 35, 30))
    # One lit window
    draw.rectangle([(h3_x + 30, h3_y + 45), (h3_x + 85, h3_y + 95)], fill=(255, 210, 140))
    # Dark window - THE DARK WINDOW
    draw.rectangle([(h3_x + 160, h3_y + 45), (h3_x + 215, h3_y + 95)], fill=(20, 18, 25))

    # Mailboxes
    draw.rectangle([(480, horizon - 40), (490, horizon)], fill=(60, 55, 50))
    draw.rectangle([(980, horizon - 40), (990, horizon)], fill=(60, 55, 50))

    # Street lamp
    lamp_x, lamp_y = 780, horizon - 180
    draw.rectangle([(lamp_x - 3, lamp_y), (lamp_x + 3, horizon)], fill=(40, 40, 45))
    draw.ellipse([(lamp_x - 8, lamp_y - 8), (lamp_x + 8, lamp_y + 8)], fill=(255, 240, 200))
    # Light glow
    lamp_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(lamp_glow)
    for r in range(60, 0, -2):
        alpha = max(0, 15 - r // 4)
        glow_draw.ellipse([(lamp_x - r, lamp_y - r), (lamp_x + r, lamp_y + r)], fill=(255, 240, 200, alpha))
    img = Image.alpha_composite(img.convert("RGBA"), lamp_glow).convert("RGB")
    draw = ImageDraw.Draw(img)

    # === Title Panel (bottom) ===
    panel_y = 1920
    # Dark semi-transparent panel
    panel_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel_overlay)
    pdraw.rectangle([(0, panel_y), (W, H)], fill=(15, 15, 25, 220))
    # Top border accent line
    pdraw.rectangle([(100, panel_y), (W - 100, panel_y + 4)], fill=(180, 140, 80))
    img = Image.alpha_composite(img.convert("RGBA"), panel_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # Load fonts
    font_dir = Path("C:/Windows/Fonts")
    try:
        title_font = ImageFont.truetype(str(font_dir / "georgiab.ttf"), 72)
        author_font = ImageFont.truetype(str(font_dir / "arialbd.ttf"), 36)
        tagline_font = ImageFont.truetype(str(font_dir / "arial.ttf"), 22)
    except (IOError, OSError):
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        tagline_font = ImageFont.load_default()

    # Wrap title if needed
    title_text = title.upper()
    words = title_text.split()
    if len(words) > 2:
        half = len(words) // 2
        line1 = " ".join(words[:half])
        line2 = " ".join(words[half:])
    else:
        line1 = words[0]
        line2 = words[1] if len(words) > 1 else ""

    # Draw title lines
    if line2:
        bbox1 = draw.textbbox((0, 0), line1, font=title_font)
        bbox2 = draw.textbbox((0, 0), line2, font=title_font)
        tw1 = bbox1[2] - bbox1[0]
        tw2 = bbox2[2] - bbox2[0]
        title_center_y = panel_y + (H - panel_y) // 2 - 50
        draw.text(((W - tw1) // 2, title_center_y), line1, fill=(220, 210, 190), font=title_font)
        draw.text(((W - tw2) // 2, title_center_y + 80), line2, fill=(220, 210, 190), font=title_font)
    else:
        bbox = draw.textbbox((0, 0), line1, font=title_font)
        tw = bbox[2] - bbox[0]
        draw.text(((W - tw) // 2, panel_y + (H - panel_y) // 2 - 40), line1, fill=(220, 210, 190), font=title_font)

    # Author name
    author_text = f"by {author}"
    abbox = draw.textbbox((0, 0), author_text, font=author_font)
    aw = abbox[2] - abbox[0]
    draw.text(((W - aw) // 2, panel_y + 500), author_text, fill=(180, 140, 80), font=author_font)

    # Genre tagline at very bottom
    tagline = "A Domestic Thriller"
    tbbox = draw.textbbox((0, 0), tagline, font=tagline_font)
    tw = tbbox[2] - tbbox[0]
    draw.text(((W - tw) // 2, H - 60), tagline, fill=(120, 120, 130), font=tagline_font)

    # Subtle vignette overlay
    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    for r in range(800, 0, -10):
        alpha = max(0, 30 - r // 30)
        vdraw.ellipse([(W // 2 - r, H // 2 - r), (W // 2 + r, H // 2 + r)], outline=(0, 0, 0, alpha), width=10)
    img = Image.alpha_composite(img.convert("RGBA"), vignette).convert("RGB")

    # Slight gaussian blur for a more painterly feel
    img = img.filter(ImageFilter.SMOOTH)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(output_path, "PNG")
    print(f"Cover saved to {output_path}")



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    create_cover(args.metadata, args.out)


if __name__ == "__main__":
    main()