#!/usr/bin/env python3
"""Cover: generic genre-themed cover for AI-Books.

Reads the book's metadata (genre/subgenre/title) and renders a matching
artwork: space for SF, runes/stone for fantasy, neon for cyberpunk,
candle/wax for mystery, dark tones for horror, period for historical,
warm for romance/literary, bright for YA/MG, desert for western.
"""
from __future__ import annotations
import argparse, json, math, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from tools.cover_utils import _draw_standard_cover_title_panel

ROOT = Path(__file__).resolve().parents[3]
W, H = 1600, 2560

rng = random.Random()
rng.seed(20260802)

# ── palette sets per genre family ───────────────────────────────────────────
PALETTES = {
    "sf":       {"top": (8, 14, 30),  "bot": (16, 24, 44),  "acc": (120, 190, 230), "acc2": (216, 180, 96),  "dark": (6, 8, 16)},
    "fantasy":  {"top": (40, 34, 60), "bot": (70, 58, 88),  "acc": (216, 176, 96),  "acc2": (150, 120, 190), "dark": (24, 18, 34)},
    "mystery":  {"top": (60, 52, 44), "bot": (92, 80, 66),  "acc": (226, 186, 110), "acc2": (140, 110, 70),  "dark": (30, 24, 18)},
    "thriller": {"top": (28, 30, 38), "bot": (46, 48, 58),  "acc": (200, 60, 50),   "acc2": (150, 160, 175), "dark": (14, 14, 20)},
    "horror":   {"top": (22, 16, 26), "bot": (40, 30, 44),  "acc": (190, 150, 90),  "acc2": (120, 90, 130),  "dark": (10, 8, 14)},
    "historical":{"top": (150, 122, 84), "bot": (112, 88, 58), "acc": (226, 196, 130), "acc2": (96, 74, 48), "dark": (46, 36, 24)},
    "literary": {"top": (120, 128, 130), "bot": (84, 92, 96), "acc": (226, 210, 178), "acc2": (140, 120, 90), "dark": (32, 36, 40)},
    "romance":  {"top": (196, 120, 100), "bot": (150, 84, 70), "acc": (250, 224, 190), "acc2": (120, 60, 60), "dark": (60, 30, 30)},
    "ya":       {"top": (52, 76, 120), "bot": (30, 46, 78), "acc": (240, 210, 120), "acc2": (150, 200, 230), "dark": (14, 22, 40)},
    "mg":       {"top": (120, 160, 120), "bot": (70, 100, 70), "acc": (250, 230, 160), "acc2": (200, 140, 70), "dark": (30, 44, 30)},
    "western":  {"top": (222, 176, 110), "bot": (176, 128, 72), "acc": (232, 210, 170), "acc2": (110, 70, 40), "dark": (52, 36, 24)},
    "adventure":{"top": (60, 110, 80), "bot": (34, 64, 48), "acc": (230, 200, 130), "acc2": (140, 190, 160), "dark": (18, 32, 26)},
    "nonfiction":{"top": (70, 74, 84), "bot": (44, 48, 58), "acc": (226, 190, 110), "acc2": (170, 150, 110), "dark": (20, 22, 28)},
    "default":  {"top": (90, 96, 110), "bot": (60, 66, 78), "acc": (226, 200, 150), "acc2": (140, 150, 160), "dark": (28, 30, 36)},
}

def _family(meta):
    g = (meta.get("genre") or "").lower()
    s = (meta.get("subgenre") or "").lower()
    if "science" in g or "cyber" in g or "techno" in s: return "sf"
    if "fantasy" in g or "magic" in s or "myth" in s: return "fantasy"
    if "mystery" in g or "detective" in s or "cozy" in s: return "mystery"
    if "thriller" in g or "suspense" in s: return "thriller"
    if "horror" in g or "ghost" in s: return "horror"
    if "historical" in g or "war" in s or "victorian" in s: return "historical"
    if "romance" in g or "love" in s: return "romance"
    if "young adult" in g: return "ya"
    if "middle grade" in g or "children" in g: return "mg"
    if "western" in g or "frontier" in s: return "western"
    if "adventure" in g or "expedition" in s: return "adventure"
    if "non" in g or "essay" in s: return "nonfiction"
    if "literary" in g: return "literary"
    return "default"

def _gradient(img, top, bot):
    d = ImageDraw.Draw(img, "RGBA")
    for y in range(H):
        t = y / H
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        d.line((0, y, W, y), fill=(r, g, b, 255))
    del d

def _stars(img, pal, n=160):
    d = ImageDraw.Draw(img, "RGBA")
    for k in range(n):
        x = int(rng.uniform(0, W)); y = int(rng.uniform(0, H))
        r = int(rng.uniform(1, 3))
        d.ellipse((x - r, y - r, x + r, y + r), fill=(240, 244, 250, int(rng.uniform(50, 200))))
    del d

def _rings(img, pal):
    """Two perspective rings (orbit) for SF."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, int(H * 0.44)
    for off, rad, thick in [(0, 330, 22), (0, 380, 10)]:
        d.ellipse((cx - rad, cy - 150 + off - thick, cx + rad, cy - 150 + off + thick), outline=(*pal["acc"], 200), width=thick)
        d.ellipse((cx - rad, cy + 110 - off - thick, cx + rad, cy + 110 + off + thick), outline=(*pal["acc2"], 180), width=thick)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _moon(img, pal):
    d = ImageDraw.Draw(img, "RGBA")
    mx, my, mr = int(W * 0.72), int(H * 0.16), 90
    d.ellipse((mx - mr, my - mr, mx + mr, my + mr), fill=(*pal["acc"], 220))
    d.ellipse((mx - 30, my - 20, mx + 14, my + 24), fill=(*pal["acc2"], 130))
    d.ellipse((mx + 40, my + 30, mx + 70, my + 54), fill=(*pal["acc2"], 130))
    del d

def _book_motif(img, pal):
    """An open book silhouette (literary)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, int(H * 0.50)
    d.polygon([(cx - 260, cy - 140), (cx, cy - 60), (cx + 260, cy - 140), (cx + 260, cy + 100), (cx, cy + 40), (cx - 260, cy + 100)], fill=(*pal["acc"], 180))
    d.line((cx, cy - 60, cx, cy + 40), fill=(*pal["dark"], 200), width=4)
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _castle(img, pal):
    """Stone tower silhouette (fantasy/horror)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y0 = int(H * 0.80)
    d.rectangle((int(W * 0.30), y0 - int(H * 0.34), int(W * 0.70), y0), fill=(*pal["dark"], 230))
    d.polygon([(int(W * 0.30), y0 - int(H * 0.34)), (int(W * 0.42), y0 - int(H * 0.44)), (int(W * 0.42), y0 - int(H * 0.34))], fill=(*pal["dark"], 230))
    d.polygon([(int(W * 0.58), y0 - int(H * 0.34)), (int(W * 0.58), y0 - int(H * 0.44)), (int(W * 0.70), y0 - int(H * 0.34))], fill=(*pal["dark"], 230))
    # lit windows
    for k in range(4):
        wx = int(W * 0.34) + k * int(W * 0.09)
        wy = y0 - int(H * 0.28) + k * int(H * 0.05)
        d.rectangle((wx, wy, wx + 24, wy + 34), fill=(*pal["acc"], 220))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _candle(img, pal):
    """A candle with a warm flame (mystery)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, int(H * 0.60)
    d.rounded_rectangle((cx - 40, cy, cx + 40, cy + 340), radius=16, fill=(*pal["acc2"], 230))
    d.ellipse((cx - 46, cy - 6, cx + 46, cy + 30), fill=(*pal["acc2"], 200))
    d.ellipse((cx - 30, cy - 90, cx + 30, cy - 20), fill=(*pal["acc"], 235))
    d.ellipse((cx - 18, cy - 110, cx + 18, cy - 60), fill=(255, 240, 200, 235))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _train(img, pal):
    """A steam train silhouette (MG/historical)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y0 = int(H * 0.74)
    d.rounded_rectangle((int(W * 0.18), y0, int(W * 0.82), y0 + 90), radius=20, fill=(*pal["dark"], 230))
    d.rectangle((int(W * 0.64), y0 - 60, int(W * 0.80), y0 + 20), fill=(*pal["dark"], 230))
    d.rectangle((int(W * 0.68), y0 - 34, int(W * 0.76), y0 - 8), fill=(*pal["acc"], 220))
    # wheels
    for k in range(4):
        wx = int(W * 0.24) + k * int(W * 0.15)
        d.ellipse((wx - 26, y0 + 90, wx + 26, y0 + 142), fill=(*pal["acc2"], 200), outline=(*pal["dark"], 220), width=4)
    # steam
    for k in range(5):
        sx = int(W * 0.70) + k * 20
        sy = y0 - 70 - k * 24
        d.ellipse((sx - 24 - k * 6, sy, sx + 24 + k * 6, sy + 40), fill=(*pal["acc"], 90))
    layer = layer.filter(ImageFilter.GaussianBlur(1))
    return Image.alpha_composite(img, layer)

def _sunset_ridge(img, pal):
    """Ridge silhouette at sunset (western/adventure)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    y0 = int(H * 0.62)
    pts = [(0, y0)]
    for x in range(0, W + 60, 60):
        y = y0 + int(70 * math.sin(x * 0.004 + 1.2)) + int(20 * math.sin(x * 0.015))
        pts.append((x, y))
    pts += [(W, H), (0, H)]
    d.polygon(pts, fill=(*pal["dark"], 220))
    # sun
    d.ellipse((int(W * 0.40), int(H * 0.30), int(W * 0.60), int(H * 0.50)), fill=(*pal["acc"], 200))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(img, layer)

def _sunburst(img, pal):
    """Radiant sunburst (YA)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, int(H * 0.40)
    for k in range(16):
        ang = k * math.pi / 8
        x1 = cx + 500 * math.cos(ang); y1 = cy + 500 * math.sin(ang)
        d.line((cx, cy, x1, y1), fill=(*pal["acc"], 70), width=int(rng.uniform(8, 20)))
    d.ellipse((cx - 90, cy - 90, cx + 90, cy + 90), fill=(*pal["acc"], 220))
    d.ellipse((cx - 40, cy - 40, cx + 40, cy + 40), fill=(*pal["acc2"], 220))
    layer = layer.filter(ImageFilter.GaussianBlur(2))
    return Image.alpha_composite(img, layer)

def _hearth(img, pal):
    """A hearth glow (literary/romance)."""
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    cx, cy = W // 2, int(H * 0.62)
    d.ellipse((cx - 200, cy - 140, cx + 200, cy + 160), fill=(*pal["acc"], 90))
    d.ellipse((cx - 120, cy - 80, cx + 120, cy + 90), fill=(*pal["acc2"], 120))
    d.ellipse((cx - 60, cy - 40, cx + 60, cy + 40), fill=(255, 230, 190, 150))
    layer = layer.filter(ImageFilter.GaussianBlur(30))
    return Image.alpha_composite(img, layer)

def _make_cover(mp, op):
    m = json.loads(Path(mp).read_text(encoding="utf-8"))
    title = m["title"]; author = m.get("author", "Barış Kısır"); model = m.get("model", "")
    fam = _family(m)
    pal = PALETTES.get(fam, PALETTES["default"])
    img = Image.new("RGBA", (W, H), pal["bot"] + (255,))
    _gradient(img, pal["top"], pal["bot"])
    if fam == "sf":
        _stars(img, pal); img = _rings(img, pal)
    elif fam == "fantasy":
        img = _castle(img, pal); _moon(img, pal)
    elif fam == "mystery":
        img = _candle(img, pal)
    elif fam == "thriller":
        img = _castle(img, pal)
    elif fam == "horror":
        img = _castle(img, pal); _moon(img, pal)
    elif fam == "historical":
        img = _train(img, pal)
    elif fam == "literary":
        img = _hearth(img, pal)
    elif fam == "romance":
        img = _hearth(img, pal)
    elif fam == "ya":
        img = _sunburst(img, pal)
    elif fam == "mg":
        img = _train(img, pal)
    elif fam == "western":
        img = _sunset_ridge(img, pal)
    elif fam == "adventure":
        img = _sunset_ridge(img, pal)
    elif fam == "nonfiction":
        img = _book_motif(img, pal)
    else:
        img = _book_motif(img, pal)
    op.parent.mkdir(parents=True, exist_ok=True)
    _draw_standard_cover_title_panel(img, title, author, model)
    img.convert("RGB").save(op, "PNG", optimize=True)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--metadata", required=True, type=Path)
    p.add_argument("--out", required=True, type=Path)
    a = p.parse_args()
    _make_cover(
        ROOT / a.metadata if not a.metadata.is_absolute() else a.metadata,
        ROOT / a.out if not a.out.is_absolute() else a.out,
    )

if __name__ == "__main__":
    main()
