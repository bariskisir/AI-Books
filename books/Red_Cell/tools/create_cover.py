#!/usr/bin/env python3
"""Cover: Red Cell — five shadow silhouettes against a dark network node graph, crimson/black palette, a circular bank-vault motif being breached."""

from __future__ import annotations

import argparse
import json
import math
import random
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



FONT_DIR = Path("C:/Windows/Fonts")
WIDTH, HEIGHT = 1600, 2560
PANEL_Y = 1920

COLORS = {
    "bg_top": (20, 5, 8),
    "bg_mid": (40, 8, 12),
    "bg_bot": (5, 2, 3),
    "accent_crimson": (190, 20, 35),
    "accent_dark_red": (110, 8, 18),
    "node": (220, 40, 50),
    "edge": (140, 20, 30),
    "edge_dim": (70, 12, 20),
    "silhouette": (8, 4, 6),
    "vault_ring": (200, 30, 45),
    "panel_bg": (240, 240, 248),
    "title_text": (20, 5, 8),
    "author_text": (60, 40, 50),
}


def make_gradient(draw: ImageDraw.ImageDraw) -> None:
    for y in range(PANEL_Y):
        t = y / PANEL_Y
        if t < 0.5:
            t2 = t * 2
            r = int(COLORS["bg_top"][0] + (COLORS["bg_mid"][0] - COLORS["bg_top"][0]) * t2)
            g = int(COLORS["bg_top"][1] + (COLORS["bg_mid"][1] - COLORS["bg_top"][1]) * t2)
            b = int(COLORS["bg_top"][2] + (COLORS["bg_mid"][2] - COLORS["bg_top"][2]) * t2)
        else:
            t2 = (t - 0.5) * 2
            r = int(COLORS["bg_mid"][0] + (COLORS["bg_bot"][0] - COLORS["bg_mid"][0]) * t2)
            g = int(COLORS["bg_mid"][1] + (COLORS["bg_bot"][1] - COLORS["bg_mid"][1]) * t2)
            b = int(COLORS["bg_mid"][2] + (COLORS["bg_bot"][2] - COLORS["bg_mid"][2]) * t2)
        draw.line([(0, y), (WIDTH, y)], fill=(r, g, b))


def draw_node_graph(draw: ImageDraw.ImageDraw) -> None:
    """Random network node graph across the upper panel."""
    nodes = []
    for _ in range(26):
        x = random.randint(60, WIDTH - 60)
        y = random.randint(80, PANEL_Y - 320)
        nodes.append((x, y))
    for i, (x1, y1) in enumerate(nodes):
        for (x2, y2) in nodes[i + 1:]:
            d = math.hypot(x2 - x1, y2 - y1)
            if d < 260 and random.random() < 0.5:
                color = random.choice([COLORS["edge"], COLORS["edge_dim"], COLORS["edge"]])
                draw.line([(x1, y1), (x2, y2)], fill=color, width=random.choice([1, 2]))
    for (x, y) in nodes:
        r = random.randint(3, 8)
        draw.ellipse([x - r, y - r, x + r, y + r], fill=COLORS["node"])
        if random.random() < 0.4:
            ring = r + random.randint(6, 14)
            draw.ellipse([x - ring, y - ring, x + ring, y + ring], outline=COLORS["edge_dim"], width=1)


def draw_server_verticals(draw: ImageDraw.ImageDraw) -> None:
    """Server-room vertical rack silhouettes."""
    for _ in range(12):
        w = random.randint(50, 130)
        h = random.randint(300, 900)
        x = random.randint(0, WIDTH - w)
        y = PANEL_Y - h
        draw.rectangle([x, y, x + w, PANEL_Y], fill=(12, 5, 8), outline=COLORS["edge_dim"], width=1)
        for sy in range(y + 20, PANEL_Y - 20, 26):
            draw.rectangle([x + 8, sy, x + w - 8, sy + 6], fill=COLORS["edge_dim"])
            if random.random() < 0.5:
                draw.ellipse([x + w - 18, sy - 1, x + w - 12, sy + 5], fill=COLORS["node"])


def draw_vault(draw: ImageDraw.ImageDraw) -> None:
    """Circular bank-vault motif being breached at center."""
    cx, cy = WIDTH // 2, PANEL_Y // 2 - 60
    for radius, color, width in [(170, COLORS["vault_ring"], 6), (140, COLORS["accent_dark_red"], 3), (110, COLORS["accent_crimson"], 2), (80, COLORS["edge_dim"], 4)]:
        draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius], outline=color, width=width)
    # Vault spokes
    for i in range(8):
        ang = math.radians(i * 45)
        x1 = cx + int(110 * math.cos(ang))
        y1 = cy + int(110 * math.sin(ang))
        x2 = cx + int(170 * math.cos(ang))
        y2 = cy + int(170 * math.sin(ang))
        draw.line([(x1, y1), (x2, y2)], fill=COLORS["accent_dark_red"], width=3)
    # Breach crack: jagged red lines from vault to edge
    points = [(cx, cy)]
    px, py = cx, cy
    for _ in range(7):
        px += random.randint(-90, 90)
        py += random.randint(-40, 60)
        points.append((px, py))
    for i in range(len(points) - 1):
        draw.line([points[i], points[i + 1]], fill=COLORS["accent_crimson"], width=random.randint(2, 5))
    # Burst
    for _ in range(18):
        ang = random.random() * 2 * math.pi
        length = random.randint(20, 90)
        sx = cx + int(10 * math.cos(ang))
        sy = cy + int(10 * math.sin(ang))
        ex = cx + int((10 + length) * math.cos(ang))
        ey = cy + int((10 + length) * math.sin(ang))
        draw.line([(sx, sy), (ex, ey)], fill=(230, 60, 70), width=2)


def draw_silhouettes(draw: ImageDraw.ImageDraw) -> None:
    """Five red-team silhouettes along the bottom of the art panel."""
    base_y = PANEL_Y - 40
    xs = [WIDTH // 2 - 360, WIDTH // 2 - 180, WIDTH // 2, WIDTH // 2 + 180, WIDTH // 2 + 360]
    for i, x in enumerate(xs):
        h = 150 + (i % 3) * 25
        head_r = 22
        # head
        draw.ellipse([x - head_r, base_y - h - head_r * 2, x + head_r, base_y - h], fill=COLORS["silhouette"])
        # shoulders / torso
        draw.polygon(
            [(x - 45, base_y), (x - 38, base_y - h + 20), (x + 38, base_y - h + 20), (x + 45, base_y)],
            fill=COLORS["silhouette"],
        )
        # hood/equipment hints
        draw.polygon(
            [(x - 28, base_y - h + 10), (x, base_y - h - 8), (x + 28, base_y - h + 10)],
            fill=COLORS["silhouette"],
        )
        if i == 2:
            # leader holds a laptop up
            draw.rectangle([x - 34, base_y - h - 40, x + 34, base_y - h - 8], fill=COLORS["silhouette"])
            draw.rectangle([x - 34, base_y - h - 40, x + 34, base_y - h - 8], outline=COLORS["accent_crimson"], width=2)


def draw_glitch(draw: ImageDraw.ImageDraw) -> None:
    for _ in range(14):
        y = random.randint(200, PANEL_Y - 100)
        x_start = random.randint(0, WIDTH - 200)
        x_end = x_start + random.randint(40, 300)
        glitch_color = random.choice([COLORS["accent_crimson"], COLORS["node"], (255, 255, 255)])
        draw.line([(x_start, y), (x_end, y)], fill=glitch_color, width=random.randint(1, 3))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    metadata = json.loads(args.metadata.read_text(encoding="utf-8"))
    title = metadata["title"]
    author = metadata["author"]
    model = metadata.get("model", "")

    img = Image.new("RGB", (WIDTH, HEIGHT), COLORS["bg_top"])
    draw = ImageDraw.Draw(img, "RGBA")

    make_gradient(draw)
    draw_node_graph(draw)
    draw_server_verticals(draw)
    draw_vault(draw)
    draw_silhouettes(draw)
    draw_glitch(draw)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, _standard_cover_resolve_title(locals()), _standard_cover_resolve_author(locals()), model)
    img.save(args.out, "PNG")
    print(f"Cover saved to {args.out}")


if __name__ == "__main__":
    main()
