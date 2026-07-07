#!/usr/bin/env python3
"""Build README.md by scanning books/ and series/ directories."""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
GITHUB_RAW = "https://github.com/bariskisir/AI-Books/raw/refs/heads/master"
EPUB_READER = "https://epub-reader-omega.vercel.app"
PER_ROW = 5


def read_metadata(path):
    with open(path, encoding="utf-8") as f:
        meta = json.load(f)
    if "EPUB_path" not in meta and "epub" in meta:
        meta["EPUB_path"] = meta["epub"]
    if "EPUB_path" not in meta:
        meta["EPUB_path"] = ""
    if "cover_path" not in meta and "cover" in meta:
        meta["cover_path"] = meta["cover"]
    if "cover_path" not in meta:
        meta["cover_path"] = ""
    return meta


def infer_metadata_from_dir(book_dir):
    name = book_dir.name
    title = name.replace("_", " ")
    meta = {
        "title": title,
        "author": "Barış Kısır",
        "language": "en",
        "status": "complete_txt_epub_available",
        "TXT_path": f"books/{name}/txt/{name}.txt",
        "EPUB_path": f"books/{name}/epub/{name}.epub",
        "cover_path": f"books/{name}/covers/{name}.png",
    }
    return meta


def cover_cell(meta):
    epub_path = meta.get("EPUB_path", "")
    cover_path = meta.get("cover_path", "")
    title = meta.get("title", "")
    epub_url = f"{EPUB_READER}?epub={GITHUB_RAW}/{epub_path}"
    return (
        '<td align="center" style="padding:0;line-height:0;vertical-align:top;">'
        f'<a href="{epub_url}" target="_blank" title="{title}">'
        f'<img src="{cover_path}" alt="{title}" width="150" '
        'loading="lazy" style="display:block;margin:0;border-radius:0;box-shadow:none;">'
        "</a></td>"
    )


def grid_rows(cells):
    rows = []
    for i in range(0, len(cells), PER_ROW):
        chunk = cells[i : i + PER_ROW]
        rows.append("<tr>" + "".join(chunk) + "</tr>")
    return "\n".join(rows)


def book_accordion(meta, summary=None):
    title = meta.get("title", "")
    epub_path = meta.get("EPUB_path", "")
    cover_path = meta.get("cover_path", "")
    epub_url = f"{EPUB_READER}?epub={GITHUB_RAW}/{epub_path}"
    epub_download = f"{GITHUB_RAW}/{epub_path}"
    model = meta.get("model", "")
    label = summary if summary else title
    lines = [
        "<details>",
        f"<summary><strong>{label}</strong></summary>",
        "",
        "<p>",
        f'  <a href="{epub_url}">'
        f'<img src="{cover_path}" alt="Cover for {title}" width="240">'
        "</a>",
        "</p>",
        "",
        f"- [Read or listen online]({epub_url})",
        f"- [Download EPUB]({epub_download})",
    ]
    if model:
        lines.append(f"- Model: {model}")
    lines.extend(["", "</details>"])
    return "\n".join(lines)


def collect_books(directory):
    results = []
    for child in sorted(directory.iterdir()):
        if not child.is_dir():
            continue
        if child.name == "Sample_Book":
            continue
        meta_dir = child / "metadata"
        meta_files = list(meta_dir.glob("*.json")) if meta_dir.exists() else []
        if meta_files:
            for mf in sorted(meta_files):
                meta = read_metadata(mf)
                meta["_dir"] = child.name
                results.append(meta)
        else:
            meta = infer_metadata_from_dir(child)
            meta["_dir"] = child.name
            meta_dir.mkdir(exist_ok=True)
            meta_path = meta_dir / f"{child.name}_metadata.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            results.append(meta)
    results.sort(key=lambda m: m.get("title", "").lower())
    return results


def collect_series(series_dir):
    """Return dict: series_title -> list of meta dicts."""
    groups = {}
    for child in sorted(series_dir.iterdir()):
        if not child.is_dir():
            continue
        series_name = child.name.replace("_", " ")
        meta_dir = child / "metadata"
        books = []
        if meta_dir.exists():
            for mf in sorted(meta_dir.glob("*.json")):
                meta = read_metadata(mf)
                meta["_dir"] = child.name
                books.append(meta)
        if books:
            books.sort(key=lambda m: m.get("number", 0))
            groups[series_name] = books
    return groups


def main():
    repo = REPO_ROOT

    series_dir = repo / "series"
    books_dir = repo / "books"

    series_groups = collect_series(series_dir) if series_dir.exists() else {}
    standalone_books = collect_books(books_dir) if books_dir.exists() else []

    all_series_books = []
    for books in series_groups.values():
        all_series_books.extend(books)
    series_grid = grid_rows([cover_cell(m) for m in all_series_books])
    books_grid = grid_rows([cover_cell(m) for m in standalone_books])

    series_sections = []
    for series_name, books in series_groups.items():
        book_accs = []
        for m in books:
            num = m.get("number", "")
            title = m.get("title", "")
            label = f"Book {num} — {title}"
            book_accs.append(book_accordion(m, summary=label))
        inner = "\n\n".join(book_accs)
        section = (
            "<details>\n"
            f"<summary><strong>{series_name}</strong></summary>\n\n"
            f"{inner}\n\n"
            "</details>"
        )
        series_sections.append(section)
    series_accordion_nested = "\n\n".join(series_sections)

    book_accs = "\n\n".join(book_accordion(m) for m in standalone_books)

    content = f"""# AI Books

AI Books is a proprietary repository for AI-generated original fiction projects.

<details open>
<summary>Catalog &mdash; Series</summary>

Click a cover to read online

<table cellspacing="4" cellpadding="0" style="border-collapse:separate;border-spacing:4px;width:auto;line-height:0;">
{series_grid}
</table>
</details>

<details open>
<summary>Catalog &mdash; Books</summary>

Click a cover to read online

<table cellspacing="4" cellpadding="0" style="border-collapse:separate;border-spacing:4px;width:auto;line-height:0;">
{books_grid}
</table>
</details>

<details>
<summary><strong>Series</strong></summary>

{series_accordion_nested}

</details>
<details>
<summary><strong>Books</strong></summary>

{book_accs}

</details>

## License

This repository is proprietary. All rights are reserved.

The contents are publicly available only for viewing, reading, and reference through GitHub. No part of this repository may be used, copied, modified, distributed, published, translated, sold, included in datasets, or used for AI or machine-learning training without prior written permission.

See [LICENSE](LICENSE) for the full terms.
"""

    readme_path = repo / "README.md"
    readme_path.write_text(content, encoding="utf-8")
    print(
        f"Written {readme_path} "
        f"({len(standalone_books)} standalone + {len(all_series_books)} series)"
    )


if __name__ == "__main__":
    main()
