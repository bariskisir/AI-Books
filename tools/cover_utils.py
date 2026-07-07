#!/usr/bin/env python3
"""Shared cover utilities for AI-Books.

Import in per-book create_cover.py via:

    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from tools.cover_utils import (
        _standard_cover_font,
        _standard_cover_repair_text,
        _standard_cover_wrap,
        _standard_cover_center,
        _standard_cover_title_font,
        _draw_standard_cover_title_panel,
    )
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import ImageDraw, ImageFont

# ── constants ──────────────────────────────────────────────────────────────
W = 1600
H = 2560
PANEL_Y = 1765
FONT_DIR = Path("C:/Windows/Fonts")

# ── cream panel colors ─────────────────────────────────────────────────────
CREAM_BG = (235, 229, 214, 255)      # panel background
CREAM_LINE = (94, 82, 66, 170)       # divider line
CREAM_TITLE = (50, 48, 42)           # title text
CREAM_AUTHOR = (88, 76, 58)          # author text
CREAM_MODEL = (112, 102, 84)         # model text


# ── standard helpers ───────────────────────────────────────────────────────

def _standard_cover_font(name: str, size: int) -> ImageFont.FreeTypeFont:
    """Resolve a TrueType font, falling back through common candidates."""
    candidates = [
        FONT_DIR / name,
        FONT_DIR / "arialbd.ttf",
        FONT_DIR / "arial.ttf",
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def _standard_cover_repair_text(text: str) -> str:
    """Fix mojibake from Latin-1 mis-decoded as UTF-8."""
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def _standard_cover_wrap(
    draw: ImageDraw.ImageDraw,
    text: str,
    selected_font: ImageFont.FreeTypeFont,
    max_width: int,
) -> list[str]:
    """Word-wrap *text* to fit within *max_width* pixels."""
    words = text.split()
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        proposed = " ".join([*current, word])
        if draw.textbbox((0, 0), proposed, font=selected_font)[2] <= max_width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def _standard_cover_center(
    draw: ImageDraw.ImageDraw,
    y: int,
    lines: list[str],
    selected_font: ImageFont.FreeTypeFont,
    fill: tuple[int, int, int],
    line_gap: int,
    width: int,
) -> int:
    """Draw *lines* centred horizontally; return the y coordinate after the last line."""
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=selected_font)
        x = (width - (bbox[2] - bbox[0])) // 2
        draw.text((x, y), line, font=selected_font, fill=fill)
        y += bbox[3] - bbox[1] + line_gap
    return y


def _standard_cover_title_font(
    draw: ImageDraw.ImageDraw,
    title: str,
    max_width: int,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    """Return (font, wrapped_lines, line_gap) that fits the title block."""
    for size in (116, 104, 96, 88, 80, 72):
        selected = _standard_cover_font("arialbd.ttf", size)
        lines = _standard_cover_wrap(draw, title.upper(), selected, max_width)
        heights = [
            draw.textbbox((0, 0), line, font=selected)[3]
            - draw.textbbox((0, 0), line, font=selected)[1]
            for line in lines
        ]
        total = sum(heights) + max(0, len(lines) - 1) * 18
        if len(lines) <= 4 and total <= 430:
            return selected, lines, 18
    selected = _standard_cover_font("arialbd.ttf", 68)
    return selected, _standard_cover_wrap(draw, title.upper(), selected, max_width), 16


def _standard_cover_metadata_from_locals(local_vars: dict) -> dict:
    """Extract metadata dict from a function's local variables."""
    for key in ("metadata", "meta", "data", "m", "book", "book_data"):
        value = local_vars.get(key)
        if isinstance(value, dict):
            return value

    candidates: list[str | None] = []
    args = local_vars.get("args")
    if args is not None:
        candidates.append(getattr(args, "metadata", None))
    for key in ("metadata_path", "meta_path", "mp"):
        candidates.append(local_vars.get(key))

    for metadata_path in candidates:
        if not metadata_path:
            continue
        try:
            return json.loads(Path(str(metadata_path)).read_text(encoding="utf-8"))
        except Exception:
            continue
    return {}


def _standard_cover_resolve_title(local_vars: dict) -> str:
    """Resolve book title from local variables, metadata, or output path."""
    for key in ("title", "ti", "book_title", "TITLE"):
        value = local_vars.get(key)
        if value:
            return str(value)

    metadata = _standard_cover_metadata_from_locals(local_vars)
    for key in ("title", "book_title", "name"):
        value = metadata.get(key)
        if value:
            return str(value)

    args = local_vars.get("args")
    candidates: list[str | None] = []
    if args is not None:
        candidates.append(getattr(args, "out", None))
    for key in ("output_path", "out_path", "op", "out"):
        candidates.append(local_vars.get(key))

    for output_path in candidates:
        if not output_path:
            continue
        try:
            stem = Path(str(output_path)).stem.replace("_", " ").strip()
            if stem:
                return stem
        except Exception:
            continue
    return ""


def _standard_cover_resolve_author(local_vars: dict) -> str:
    """Resolve author from local variables or metadata; fall back to Barış Kısır."""
    for key in ("author", "au", "AUTHOR"):
        value = local_vars.get(key)
        if value:
            return str(value)

    metadata = _standard_cover_metadata_from_locals(local_vars)
    value = metadata.get("author")
    if value:
        return str(value)
    return "Barış Kısır"


# ── title panel ────────────────────────────────────────────────────────────

def _draw_standard_cover_title_panel(
    image,
    title: str = "",
    author: str = "",
    model: str = "",
) -> None:
    """Draw the standard cream title/author/model panel at the bottom of *image*.

    Reads *W*, *H*, and *PANEL_Y* from this module's constants.
    """
    width = W
    height = H
    panel_y = PANEL_Y

    title = _standard_cover_repair_text(str(title or "")).strip()
    author = _standard_cover_repair_text(str(author or "Barış Kısır")).strip()
    model = _standard_cover_repair_text(str(model or "")).strip()

    draw = ImageDraw.Draw(image, "RGBA")
    draw.rectangle((0, panel_y, width, height), fill=CREAM_BG)
    draw.line((180, panel_y + 17, width - 180, panel_y + 17), fill=CREAM_LINE, width=3)

    title_font, title_lines, title_gap = _standard_cover_title_font(draw, title, 1260)
    author_font = _standard_cover_font("arialbd.ttf", 50)
    model_font = _standard_cover_font("arial.ttf", 24)

    title_height = sum(
        draw.textbbox((0, 0), line, font=title_font)[3]
        - draw.textbbox((0, 0), line, font=title_font)[1]
        for line in title_lines
    )
    title_height += max(0, len(title_lines) - 1) * title_gap

    author_bbox = draw.textbbox((0, 0), author, font=author_font)
    author_height = author_bbox[3] - author_bbox[1]
    block_height = title_height + 120 + author_height

    y = panel_y + 120 + max(0, (height - panel_y - 210 - block_height) // 2)
    y = _standard_cover_center(draw, y, title_lines, title_font, CREAM_TITLE, title_gap, width)
    y += 120
    _standard_cover_center(draw, y, [author], author_font, CREAM_AUTHOR, 12, width)
    if model:
        _standard_cover_center(draw, height - 80, [model], model_font, CREAM_MODEL, 6, width)
