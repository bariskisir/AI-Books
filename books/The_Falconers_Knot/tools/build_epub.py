#!/usr/bin/env python3
"""Build a simple EPUB 3 file from a book TXT manuscript and metadata."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import mimetypes
import re
import uuid
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CHAPTER_RE = re.compile(r"^Chapter\s+(\d+):\s+(.+)$", re.MULTILINE)


def rel(path: Path) -> Path:
    return ROOT / path if not path.is_absolute() else path


def repair_mojibake(text: str) -> str:
    try:
        return text.encode("latin1").decode("utf-8")
    except UnicodeError:
        return text


def paragraphize(text: str) -> str:
    blocks = [block.strip() for block in re.split(r"\n\s*\n", text.strip()) if block.strip()]
    return "\n".join(f"<p>{html.escape(' '.join(block.split()))}</p>" for block in blocks)


def xhtml(title: str, body: str, language: str = "en") -> str:
    return f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="{html.escape(language)}">
<head>
  <meta charset="utf-8"/>
  <title>{html.escape(title)}</title>
  <link rel="stylesheet" type="text/css" href="../styles/stylesheet.css"/>
</head>
<body>
{body}
</body>
</html>
"""


def split_chapters(text: str) -> tuple[str, list[tuple[int, str, str]]]:
    matches = list(CHAPTER_RE.finditer(text))
    if not matches:
        raise ValueError("No chapter headings found.")

    front = text[: matches[0].start()].strip()
    chapters: list[tuple[int, str, str]] = []
    for index, match in enumerate(matches):
        number = int(match.group(1))
        title = match.group(2).strip()
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        chapters.append((number, title, text[start:end].strip()))
    return front, chapters


def build(metadata_path: Path, cover_path: Path | None, output_path: Path) -> None:
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    txt_path = rel(Path(metadata["TXT_path"]))
    text = txt_path.read_text(encoding="utf-8")
    front, chapters = split_chapters(text)

    title = repair_mojibake(metadata["title"])
    author = metadata.get("author", "Barış Kısır")
    author = repair_mojibake(author)
    language = metadata.get("language", "en")
    identifier = f"urn:uuid:{uuid.uuid5(uuid.NAMESPACE_URL, title + author)}"
    modified = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    description = metadata.get("long_description") or metadata.get("short_description", "")
    subjects = metadata.get("keywords", [])
    model = metadata.get("model", "")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cover_item = ""
    cover_manifest_item = ""
    cover_spine_item = ""
    cover_xhtml = ""
    cover_bytes = None
    cover_name = None
    media_type = None

    if cover_path:
        cover_path = rel(cover_path)
        cover_bytes = cover_path.read_bytes()
        suffix = cover_path.suffix.lower() or ".png"
        cover_name = f"cover{suffix}"
        media_type = mimetypes.types_map.get(suffix, "image/png")
        cover_item = '<meta name="cover" content="cover-image"/>\n    <meta property="schema:accessMode">visual</meta>'
        cover_manifest_item = f'    <item id="cover-image" href="images/{cover_name}" media-type="{media_type}" properties="cover-image"/>\n    <item id="cover" href="text/cover.xhtml" media-type="application/xhtml+xml"/>\n'
        cover_spine_item = '    <itemref idref="cover" linear="no"/>\n'
        cover_xhtml = xhtml(
            "Cover",
            f'<section class="cover"><img src="../images/{cover_name}" alt="Cover for {html.escape(title)}"/></section>',
            language,
        )

    title_page = xhtml(
        title,
        f"""<section class="title-page">
  <h1>{html.escape(title)}</h1>
  <p class="author">{html.escape(author)}</p>
  <p class="model">{html.escape(model)}</p>
</section>""",
        language,
    )

    chapter_files: list[tuple[str, str, str]] = []
    chapter_label = "Bölüm" if language.lower().startswith("tr") else "Chapter"
    for number, chapter_title, content in chapters:
        file_name = f"chapter-{number:03d}.xhtml"
        full_title = f"{chapter_label} {number}: {chapter_title}"
        body = f"<section>\n<h1>{html.escape(full_title)}</h1>\n{paragraphize(content)}\n</section>"
        chapter_files.append((file_name, full_title, xhtml(full_title, body, language)))

    nav_items = "\n".join(
        f'      <li><a href="text/{file_name}">{html.escape(chapter_title)}</a></li>'
        for file_name, chapter_title, _ in chapter_files
    )
    nav = xhtml(
        "Table of Contents",
        f"""<nav epub:type="toc" id="toc" xmlns:epub="http://www.idpf.org/2007/ops">
  <h1>Contents</h1>
  <ol>
{nav_items}
  </ol>
</nav>""",
        language,
    )

    subject_tags = "\n    ".join(f"<dc:subject>{html.escape(str(subject))}</dc:subject>" for subject in subjects)
    manifest_chapters = "\n".join(
        f'    <item id="chap-{index:03d}" href="text/{file_name}" media-type="application/xhtml+xml"/>'
        for index, (file_name, _, _) in enumerate(chapter_files, 1)
    )
    spine_chapters = "\n".join(f'    <itemref idref="chap-{index:03d}"/>' for index in range(1, len(chapter_files) + 1))

    opf = f"""<?xml version="1.0" encoding="utf-8"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="book-id">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:identifier id="book-id">{identifier}</dc:identifier>
    <dc:title>{html.escape(title)}</dc:title>
    <dc:creator>{html.escape(author)}</dc:creator>
    <dc:language>{language}</dc:language>
    <dc:description>{html.escape(description)}</dc:description>
    {subject_tags}
    <meta property="dcterms:modified">{modified}</meta>
    {cover_item}
  </metadata>
  <manifest>
    <item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="style" href="styles/stylesheet.css" media-type="text/css"/>
    <item id="title-page" href="text/title.xhtml" media-type="application/xhtml+xml"/>
{cover_manifest_item}{manifest_chapters}
  </manifest>
  <spine>
{cover_spine_item}    <itemref idref="title-page"/>
{spine_chapters}
  </spine>
</package>
"""

    container = """<?xml version="1.0" encoding="utf-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""

    css = """body {
  font-family: serif;
  line-height: 1.45;
  margin: 5%;
}
h1 {
  font-family: sans-serif;
  page-break-before: always;
  margin-bottom: 1.5em;
}
p {
  margin: 0 0 1em 0;
  text-indent: 1.2em;
}
.title-page {
  text-align: center;
  margin-top: 35%;
}
.title-page p {
  text-indent: 0;
}
.author {
  font-size: 1.25em;
}
.model {
  color: #555;
  font-size: 0.72em;
  margin-top: 3em;
}
.cover {
  margin: 0;
  text-align: center;
}
.cover img {
  max-width: 100%;
  max-height: 100%;
}
"""

    with zipfile.ZipFile(output_path, "w") as epub:
        epub.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        epub.writestr("META-INF/container.xml", container)
        epub.writestr("OEBPS/content.opf", opf)
        epub.writestr("OEBPS/nav.xhtml", nav)
        epub.writestr("OEBPS/styles/stylesheet.css", css)
        if cover_bytes and cover_name:
            epub.writestr(f"OEBPS/images/{cover_name}", cover_bytes)
            epub.writestr("OEBPS/text/cover.xhtml", cover_xhtml)
        epub.writestr("OEBPS/text/title.xhtml", title_page)
        for file_name, _, content in chapter_files:
            epub.writestr(f"OEBPS/text/{file_name}", content)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--cover", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    metadata_path = rel(args.metadata)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    output_path = rel(args.out) if args.out else rel(Path(metadata["EPUB_path"]))
    build(metadata_path, args.cover, output_path)


if __name__ == "__main__":
    main()
