#!/usr/bin/env python3
"""Cover: The Music Box — dark burgundy/violet gradient, ornate rosewood-and-gold music box, ivy vines, floating golden notes."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

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



WIDTH = 1600
HEIGHT = 2560


def gradient(
    draw: ImageDraw.ImageDraw,
    width: int,
    height: int,
    color_top: tuple[int, int, int],
    color_bottom: tuple[int, int, int],
) -> None:
    for y in range(height):
        r = int(color_top[0] + (color_bottom[0] - color_top[0]) * y / height)
        g = int(color_top[1] + (color_bottom[1] - color_top[1]) * y / height)
        b = int(color_top[2] + (color_bottom[2] - color_top[2]) * y / height)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def draw_music_box(draw: ImageDraw.ImageDraw, cx: int, cy: int, size: int) -> None:
    """Draw an ornate music box at center (cx, cy) with given size."""
    half = size // 2
    # Box body - rosewood color
    box_color = (65, 35, 20)  # dark rosewood
    gold_color = (212, 175, 55)
    lid_color = (80, 45, 25)

    # Main body (rectangle)
    draw.rounded_rectangle(
        [(cx - half, cy - half // 2), (cx + half, cy + half // 2)],
        radius=8,
        fill=box_color,
        outline=gold_color,
        width=3,
    )

    # Lid (slightly elevated, trapezoid-like via rounded rect)
    lid_top = cy - half // 2 - size // 6
    draw.rounded_rectangle(
        [(cx - half + 10, lid_top), (cx + half - 10, cy - half // 2)],
        radius=6,
        fill=lid_color,
        outline=gold_color,
        width=2,
    )

    # Gold keyhole / winding key detail
    key_x = cx
    key_y = lid_top - 8
    draw.ellipse(
        [(key_x - 6, key_y - 6), (key_x + 6, key_y + 6)],
        fill=gold_color,
        outline=(180, 140, 30),
        width=1,
    )
    # Key stem
    draw.line([(key_x, key_y - 6), (key_x, key_y - 20)], fill=gold_color, width=3)
    draw.ellipse(
        [(key_x - 4, key_y - 24), (key_x + 4, key_y - 18)],
        fill=gold_color,
    )

    # Gold inlay lines on body
    inset = 15
    draw.line(
        [(cx - half + inset, cy - 10), (cx + half - inset, cy - 10)],
        fill=gold_color,
        width=1,
    )
    draw.line(
        [(cx - half + inset, cy + 10), (cx + half - inset, cy + 10)],
        fill=gold_color,
        width=1,
    )

    # Brass drum visible (partial circle at top of body)
    drum_cy = cy - half // 4
    draw.ellipse(
        [(cx - half // 3, drum_cy - 12), (cx + half // 3, drum_cy + 12)],
        fill=(180, 160, 100),
        outline=gold_color,
        width=1,
    )
    # Teeth on drum
    for i in range(-4, 5):
        tx = cx + i * 12
        draw.line(
            [(tx, drum_cy - 14), (tx, drum_cy + 14)],
            fill=(140, 120, 70),
            width=2,
        )


def draw_sheet_music(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, height: int) -> None:
    """Draw a sheet music page."""
    # Page
    draw.rectangle(
        [(x, y), (x + width, y + height)],
        fill=(245, 240, 230),
        outline=(180, 170, 150),
        width=1,
    )
    # Staff lines
    staff_y = y + 20
    staff_spacing = 6
    note_color = (40, 35, 30)
    for staff in range(3):
        for line in range(5):
            ly = staff_y + line * staff_spacing
            draw.line(
                [(x + 15, ly), (x + width - 15, ly)],
                fill=(120, 110, 90),
                width=1,
            )
        # Treble clef (simplified)
        clef_x = x + 20
        clef_y = staff_y + 8
        draw.text((clef_x, clef_y - 10), "\U0001d11e", fill=note_color, font_size=20)
        # Some note dots
        for ni, nx in enumerate([x + 50, x + 100, x + 150, x + 200]):
            ny = staff_y + staff_spacing * (ni % 5)
            draw.ellipse([(nx, ny - 3), (nx + 6, ny + 3)], fill=note_color)
            # Stem
            draw.line([(nx + 6, ny), (nx + 6, ny - 18)], fill=note_color, width=1)
        staff_y += 40


def draw_piano_keys(draw: ImageDraw.ImageDraw, x: int, y: int, num_keys: int, key_width: int, key_height: int) -> None:
    """Draw piano keyboard section."""
    white_key_color = (245, 242, 235)
    black_key_color = (25, 20, 15)
    outline_color = (100, 95, 85)

    for i in range(num_keys):
        kx = x + i * key_width
        draw.rectangle(
            [(kx, y), (kx + key_width - 1, y + key_height)],
            fill=white_key_color,
            outline=outline_color,
            width=1,
        )
        # Black keys (simplified pattern)
        if i % 7 not in (2, 6):
            draw.rectangle(
                [(kx + key_width - key_width // 3, y),
                 (kx + key_width + key_width // 3, y + key_height * 3 // 5)],
                fill=black_key_color,
            )


def draw_therapy_room_elements(draw: ImageDraw.ImageDraw) -> None:
    """Draw subtle therapy room elements in the background."""
    # A window with soft light
    win_x, win_y = 1200, 300
    win_w, win_h = 250, 350
    draw.rectangle(
        [(win_x, win_y), (win_x + win_w, win_y + win_h)],
        fill=(100, 110, 140),
        outline=(80, 85, 100),
        width=2,
    )
    # Window cross
    draw.line(
        [(win_x + win_w // 2, win_y), (win_x + win_w // 2, win_y + win_h)],
        fill=(60, 65, 80),
        width=2,
    )
    draw.line(
        [(win_x, win_y + win_h // 2), (win_x + win_w, win_y + win_h // 2)],
        fill=(60, 65, 80),
        width=2,
    )
    # Soft light glow
    glow = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow)
    for r in range(80, 0, -4):
        alpha = max(0, 20 - r // 4)
        glow_draw.ellipse(
            [(win_x + win_w // 2 - r, win_y + win_h // 2 - r),
             (win_x + win_w // 2 + r, win_y + win_h // 2 + r)],
            fill=(200, 210, 240, alpha),
        )
    draw._image.paste(glow, (0, 0), glow)



def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", type=Path)
    parser.add_argument("--out", type=Path, default=Path("The_Music_Box/covers/The_Music_Box.png"))
    args = parser.parse_args()

    title = "The Music Box"
    author = "Barış Kısır"

    if args.metadata:
        meta = json.loads(args.metadata.read_text(encoding="utf-8"))
        title = meta.get("title", title)
        author = meta.get("author", author)
    model = meta.get("model", "")

    img = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 255))
    draw = ImageDraw.Draw(img)

    # Dark burgundy/violet gradient
    for y in range(HEIGHT):
        t=y/HEIGHT
        r=int(40+20*t); g=int(10+8*t); b=int(30+15*t)
        draw.line([(0,y),(WIDTH,y)], fill=(r,g,b))
    # Deeper burgundy lower section
    for y in range(1200, HEIGHT):
        t=(y-1200)/(HEIGHT-1200)
        r=int(60+30*t); g=int(18-8*t); b=int(45+10*t)
        draw.line([(0,y),(WIDTH,y)], fill=(r,g,b))

    # Ornate rosewood-and-gold music box — center
    cx, cy = WIDTH//2, 600
    # Rosewood body
    draw.rounded_rectangle([cx-180,cy-120,cx+180,cy+120], radius=12, fill=(55,30,18), outline=(180,150,60), width=4)
    # Gold inlay border
    draw.rounded_rectangle([cx-165,cy-105,cx+165,cy+105], radius=8, fill=None, outline=(180,150,60), width=2)
    # Lid
    draw.rounded_rectangle([cx-170,cy-135,cx+170,cy-120], radius=6, fill=(70,40,25), outline=(180,150,60), width=3)
    # Key winding
    draw.ellipse([cx-6,cy-142,cx+6,cy-130], fill=(200,170,80))
    draw.line([(cx,cy-142),(cx,cy-155)], fill=(200,170,80), width=3)
    draw.ellipse([cx-4,cy-160,cx+4,cy-155], fill=(200,170,80))
    # Gold ornamental scroll
    draw.arc([cx-80,cy-80,cx+80,cy+80], 0, 180, fill=(180,150,60,120), width=3)
    draw.arc([cx-60,cy-60,cx+60,cy+60], 180, 360, fill=(180,150,60,100), width=2)
    # Sequinned drum visible
    draw.ellipse([cx-70,cy-20,cx+70,cy+20], fill=(160,140,90), outline=(200,170,80), width=2)
    for i in range(-10, 11):
        tx=cx+i*12
        draw.line([(tx,cy-22),(tx,cy+22)], fill=(130,110,60), width=2)

    # Ivy vines wrapping around box
    for angle in range(0, 360, 20):
        rad=math.radians(angle)
        vx=cx+int(220*math.cos(rad))
        vy=cy+int(200*math.sin(rad))
        draw.ellipse([vx-6,vy-10,vx+6,vy], fill=(30,70,35))
        if angle%40==0:
            draw.ellipse([vx-8,vy-8,vx+8,vy+8], fill=(140,35,40))

    # Floating golden musical notes
    for i in range(25):
        nx=cx+int((i-12)*20)+int(math.sin(i*0.7)*60)
        ny=cy-250+int(math.cos(i*1.1)*80)-i*8
        draw.ellipse([nx-4,ny-4,nx+4,ny+4], fill=(200,180,80,150+int(math.sin(i)*50)))
        draw.line([(nx+4,ny),(nx+4,ny-12)], fill=(200,180,80,120), width=1)

    # Save
    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()