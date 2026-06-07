#!/usr/bin/env python3
"""
Cover generator for The Thousand Faces.

Scene: A clinical observation room with a one-way mirror. The viewer
stands at the glass. On the far side, visible through the mirror,
a room packed with identical calm faces — all looking directly back.
Faces are multiplied, refracted, arrayed in clinical rows. Cold
institutional white and grey palette with unsettling blue fluorescent light.
"""

from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Canvas dimensions
# ---------------------------------------------------------------------------
WIDTH = 1600
HEIGHT = 2560
ART_HEIGHT = 1765  # panel starts below here


# ---------------------------------------------------------------------------
# Standard cover helpers (required by AGENTS.md)
# ---------------------------------------------------------------------------

def _standard_cover_font(name, size):
    candidates = [name, "arial.ttf", "Arial.ttf", "DejaVuSans.ttf"]
    if "bd" in name.lower() or "bold" in name.lower():
        candidates = [name, "arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf", "DejaVuSans.ttf"]
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()

def _standard_cover_repair_text(text):
    try:
        return text.encode("latin1").decode("utf-8")
    except Exception:
        return text

def _standard_cover_wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = []
    for word in words:
        trial = " ".join(current + [word])
        box = draw.textbbox((0, 0), trial, font=font)
        if current and box[2] - box[0] > max_width:
            lines.append(" ".join(current))
            current = [word]
        else:
            current.append(word)
    if current:
        lines.append(" ".join(current))
    return lines or [text]

def _standard_cover_center(draw, y, lines, font, fill, gap, width):
    for line in lines:
        box = draw.textbbox((0, 0), line, font=font)
        draw.text(((width - (box[2] - box[0])) // 2, y), line, font=font, fill=fill)
        y += box[3] - box[1] + gap
    return y

def _standard_cover_title_font(draw, title, max_width):
    for size in (116, 104, 96, 88, 80, 72, 66, 60):
        font = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), font, max_width)
        heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]
        if len(lines) <= 4 and sum(heights) + max(0, len(lines) - 1) * 18 <= 430:
            return font, lines, 18
    font = _standard_cover_font("arialbd.ttf", 58)
    return font, _standard_cover_wrap(draw, title.upper(), font, max_width), 14

def _standard_cover_resolve_title(local_vars):
    for key in ("title", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return value
    return ""

def _standard_cover_resolve_author(local_vars):
    for key in ("author", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return value
    return "Barış Kısır"

def _draw_standard_cover_title_panel(image, title="", author="", model=""):
    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    draw = ImageDraw.Draw(image, "RGBA")
    py = 1765
    draw.rectangle((0, py, 1600, 2560), fill=(12, 18, 32, 255))
    draw.line((180, py + 17, 1420, py + 17), fill=(60, 100, 160, 125), width=3)
    title_font, lines, gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 52)
    title_height = sum(draw.textbbox((0, 0), line, font=title_font)[3] - draw.textbbox((0, 0), line, font=title_font)[1] for line in lines) + max(0, len(lines) - 1) * gap
    author_height = draw.textbbox((0, 0), author, font=author_font)[3] - draw.textbbox((0, 0), author, font=author_font)[1]
    y = py + 120 + max(0, (2560 - py - 230 - (title_height + 118 + author_height)) // 2)
    y = _standard_cover_center(draw, y, lines, title_font, (220, 225, 235), gap, 1600) + 118
    _standard_cover_center(draw, y, [author], author_font, (160, 180, 210), 12, 1600)
    if model:
        model_font = _standard_cover_font("arial.ttf", 36)
        _standard_cover_center(draw, 2560 - 110, [model], model_font, (80, 100, 130), 12, 1600)


# ---------------------------------------------------------------------------
# Book-specific art: one-way mirror with massed faces
# ---------------------------------------------------------------------------

def _draw_background(draw: ImageDraw.ImageDraw) -> None:
    """Institutional grey-white gradient background."""
    for y in range(ART_HEIGHT):
        t = y / ART_HEIGHT
        # Cold blue-grey gradient from near-white top to deeper grey-blue
        r = int(210 - t * 60)
        g = int(215 - t * 55)
        b = int(225 - t * 40)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def _draw_ceiling_fluorescent(draw: ImageDraw.ImageDraw) -> None:
    """Fluorescent tube lighting strip along the ceiling of the far room."""
    # Light bar body
    bar_y = 28
    bar_h = 22
    draw.rectangle([(140, bar_y), (WIDTH - 140, bar_y + bar_h)], fill=(230, 235, 255))
    # Glow halo
    for spread in range(1, 18):
        alpha = int(60 * (1 - spread / 18))
        glow_color = (200, 210, 255, alpha)
        # Draw with decreasing opacity approximation
        fade = int(230 - spread * 10)
        draw.rectangle(
            [(140 - spread * 3, bar_y - spread * 2),
             (WIDTH - 140 + spread * 3, bar_y + bar_h + spread * 2)],
            outline=(fade, fade + 5, min(255, fade + 25))
        )


def _draw_room_walls(draw: ImageDraw.ImageDraw) -> None:
    """Draw the far room visible through the mirror: walls, floor, ceiling lines."""
    # Floor line at bottom of art area
    floor_y = ART_HEIGHT - 60
    draw.rectangle([(0, floor_y), (WIDTH, ART_HEIGHT)], fill=(175, 180, 192))
    # Baseboard
    draw.rectangle([(0, floor_y - 8), (WIDTH, floor_y)], fill=(155, 160, 172))
    # Wall panel lines (vertical)
    for x in range(0, WIDTH + 1, 200):
        draw.line([(x, 0), (x, floor_y)], fill=(195, 200, 210), width=1)
    # Horizontal panel division midway up
    mid_y = ART_HEIGHT // 2 - 80
    draw.line([(0, mid_y), (WIDTH, mid_y)], fill=(190, 195, 208), width=2)


def _draw_mirror_frame(draw: ImageDraw.ImageDraw) -> None:
    """
    The one-way mirror itself: a large rectangular frame centered in the art.
    The 'observer' side is this room. The far side shows the face array.
    """
    # Mirror outer frame
    mx, my = 100, 80
    mw, mh = WIDTH - 200, ART_HEIGHT - 220
    frame_thick = 14

    # Dark institutional frame
    draw.rectangle([(mx - frame_thick, my - frame_thick),
                    (mx + mw + frame_thick, my + mh + frame_thick)],
                   fill=(55, 60, 72))
    # Inner frame highlight
    draw.rectangle([(mx - 4, my - 4), (mx + mw + 4, my + mh + 4)],
                   outline=(100, 110, 130), width=3)
    # The mirror surface (filled by the face-drawing later; set a base color)
    draw.rectangle([(mx, my), (mx + mw, my + mh)], fill=(185, 192, 205))


def _draw_face(draw: ImageDraw.ImageDraw, cx: int, cy: int, scale: float,
               alpha_factor: float = 1.0) -> None:
    """
    Draw a single clinical, calm face at center (cx, cy) with given scale.
    Face is minimalist: oval head, eyes, minimal features.
    Color: near-monochrome, slightly warm grey.
    """
    # Base skin tone — cold institutional pallor
    skin_base = int(195 * alpha_factor + 200 * (1 - alpha_factor))
    skin_mid = int(185 * alpha_factor + 200 * (1 - alpha_factor))
    skin_shadow = int(160 * alpha_factor + 200 * (1 - alpha_factor))
    skin = (skin_base, skin_mid + 2, skin_mid + 8)
    dark = (skin_shadow - 20, skin_shadow - 15, skin_shadow)

    rw = int(38 * scale)
    rh = int(50 * scale)
    # Head oval
    draw.ellipse([(cx - rw, cy - rh), (cx + rw, cy + rh)], fill=skin, outline=dark, width=max(1, int(scale)))

    # Eyes
    eye_y = cy - int(12 * scale)
    eye_dx = int(14 * scale)
    eye_rw = int(7 * scale)
    eye_rh = int(5 * scale)
    eye_color = (50, 52, 65)
    pupil_color = (20, 20, 30)
    for ex in [cx - eye_dx, cx + eye_dx]:
        draw.ellipse([(ex - eye_rw, eye_y - eye_rh), (ex + eye_rw, eye_y + eye_rh)],
                     fill=eye_color)
        # Pupil
        pr = max(1, int(3 * scale))
        draw.ellipse([(ex - pr, eye_y - pr), (ex + pr, eye_y + pr)], fill=pupil_color)
        # Catchlight
        cl = max(1, int(1.5 * scale))
        draw.ellipse([(ex + pr - cl, eye_y - pr), (ex + pr + cl, eye_y - pr + cl * 2)],
                     fill=(230, 235, 245))

    # Nose: two small dots
    nose_y = cy + int(6 * scale)
    nd = int(5 * scale)
    nr = max(1, int(2 * scale))
    for nx in [cx - nd, cx + nd]:
        draw.ellipse([(nx - nr, nose_y - nr), (nx + nr, nose_y + nr)], fill=dark)

    # Mouth: flat, closed line — calm
    mouth_y = cy + int(22 * scale)
    mouth_w = int(18 * scale)
    mouth_thick = max(1, int(1.5 * scale))
    draw.line([(cx - mouth_w, mouth_y), (cx + mouth_w, mouth_y)],
              fill=dark, width=mouth_thick)


def _draw_face_array(image: Image.Image) -> None:
    """
    Fill the mirror rectangle with dozens of identical calm faces,
    arranged in neat clinical rows. Faces decrease in size toward the back
    (perspective effect). Front rows are clearer, back rows hazier.
    """
    draw = ImageDraw.Draw(image)

    mx, my = 100, 80
    mw, mh = WIDTH - 200, ART_HEIGHT - 220

    # Number of rows and columns
    rows = 9
    cols = 8

    for row in range(rows):
        # Perspective: rows further away are higher up and smaller
        t = row / (rows - 1)  # 0 = front row (bottom of mirror), 1 = back (top)
        # Scale decreases as we go further back
        scale = 1.0 - t * 0.58
        # Alpha (clarity) decreases with distance
        alpha = 1.0 - t * 0.55

        face_h = int(100 * scale)
        face_w = int(76 * scale)

        # Y position: front row near bottom of mirror, back near top
        row_y = my + mh - int(face_h * 0.6) - int((mh - face_h) * (row / (rows - 1)) * 0.88)

        # Horizontal spacing
        col_spacing = mw / (cols + 0.5)

        for col in range(cols):
            # Slight horizontal offset alternating rows for naturalistic packing
            offset = int(col_spacing * 0.25) if row % 2 == 1 else 0
            cx = mx + int(col_spacing * (col + 0.75)) + offset
            cy = row_y

            # Clip to mirror bounds
            if cx - int(face_w // 2) < mx or cx + int(face_w // 2) > mx + mw:
                continue
            if cy - int(face_h // 2) < my or cy + int(face_h // 2) > my + mh:
                continue

            _draw_face(draw, cx, cy, scale * 1.1, alpha)


def _draw_mirror_glare(draw: ImageDraw.ImageDraw) -> None:
    """
    Add a faint glass-like sheen to the mirror surface — suggests
    the reflective property of one-way glass.
    """
    mx, my = 100, 80
    mw = WIDTH - 200

    # Diagonal glare strip
    for i in range(0, 60):
        t = i / 60
        alpha_approx = int(25 * (1 - abs(t - 0.5) * 2))
        x1 = mx + int(mw * 0.05) + i * 5
        x2 = mx + int(mw * 0.15) + i * 5
        y1 = my
        y2 = my + int((ART_HEIGHT - 220) * 0.45)
        c = min(255, 220 + alpha_approx)
        draw.line([(x1, y1), (x2, y2)], fill=(c, c, min(255, c + 10)), width=2)


def _draw_foreground_frame(draw: ImageDraw.ImageDraw) -> None:
    """
    Suggest the viewer's side: dark foreground framing, like standing
    in a dim monitoring room looking at the lit mirror.
    """
    # Left and right foreground pillars (dark, close to viewer)
    pillar_w = 88
    pillar_color = (38, 40, 52)
    draw.rectangle([(0, 0), (pillar_w, ART_HEIGHT)], fill=pillar_color)
    draw.rectangle([(WIDTH - pillar_w, 0), (WIDTH, ART_HEIGHT)], fill=pillar_color)

    # Bottom foreground shadow (observer is slightly lower than the mirror)
    for d in range(0, 55):
        t = d / 55
        grey = int(40 + t * 30)
        draw.line([(pillar_w, ART_HEIGHT - d - 1), (WIDTH - pillar_w, ART_HEIGHT - d - 1)],
                  fill=(grey, grey + 2, grey + 8))

    # Top vignette from the monitoring room ceiling
    for d in range(0, 40):
        t = d / 40
        grey = int(45 - t * 15)
        draw.line([(pillar_w, d), (WIDTH - pillar_w, d)],
                  fill=(grey, grey + 2, grey + 8))


def _draw_blue_fluorescent_tint(image: Image.Image) -> None:
    """
    Apply a cold blue fluorescent tint over the entire art area
    using a multiply-style overlay.
    """
    overlay = Image.new("RGBA", (WIDTH, ART_HEIGHT), (140, 155, 210, 18))
    image.paste(overlay, (0, 0), overlay)


def _draw_clinical_label(draw: ImageDraw.ImageDraw) -> None:
    """
    Small institutional label in the corner of the mirror frame —
    the kind of text found on observation room equipment.
    """
    label_font = _standard_cover_font("arial.ttf", 22)
    label_text = "OBSERVATION SUITE A  |  ONE-WAY GLASS"
    label_color = (130, 140, 160)
    draw.text((116, ART_HEIGHT - 52), label_text, font=label_font, fill=label_color)


def generate_cover(metadata: dict, out_path: Path) -> None:
    title = _standard_cover_resolve_title(metadata)
    author = _standard_cover_resolve_author(metadata)
    model = metadata.get("model", "")

    image = Image.new("RGB", (WIDTH, HEIGHT), (200, 205, 215))
    draw = ImageDraw.Draw(image)

    # Build the art layer
    _draw_background(draw)
    _draw_room_walls(draw)
    _draw_ceiling_fluorescent(draw)
    _draw_mirror_frame(draw)
    _draw_face_array(image)
    _draw_mirror_glare(draw)
    _draw_foreground_frame(draw)
    _draw_clinical_label(draw)

    # Convert to RGBA for tint overlay, then back to RGB
    image = image.convert("RGBA")
    _draw_blue_fluorescent_tint(image)
    image = image.convert("RGB")

    # Subtle blur pass for the face array region (mimics seeing through glass)
    mirror_region = image.crop((100, 80, WIDTH - 100, ART_HEIGHT - 140))
    mirror_blurred = mirror_region.filter(ImageFilter.GaussianBlur(radius=0.8))
    image.paste(mirror_blurred, (100, 80))

    # Draw the title panel
    _draw_standard_cover_title_panel(image, title=title, author=author, model=model)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(str(out_path), "PNG")
    print(f"Cover saved: {out_path}  ({out_path.stat().st_size:,} bytes)")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cover for The Thousand Faces")
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    generate_cover(metadata, args.out)


if __name__ == "__main__":
    main()
