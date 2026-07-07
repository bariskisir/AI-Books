# AGENTS.md — AI Books

## Project Overview

AI-generated fiction repository. Each book has a directory with TXT manuscript, EPUB, cover image, and metadata JSON. The README is auto-generated from metadata. All build/check/fix operations are automated via Python scripts in `tools/`.

## Directory Structure

```
ai-books/
  books/                          # Standalone books
    <Book_Name>/
      metadata/<Book_Name>_metadata.json
      txt/<Book_Name>.txt
      epub/<Book_Name>.epub
      covers/<Book_Name>.png
      tools/create_cover.py       # (optional, per-book)
      planning/                   # (optional) outlines, notes
      reports/                    # (optional) generation reports
  series/                         # Series (grouped books)
    <Series_Name>/
      metadata/Book<N>_<Book_Name>_metadata.json   # per-book metadata
      txt/                        # shared folder for all books in series
      epub/
      covers/
      tools/create_cover.py       # shared per-series
      planning/
  tools/                          # Automation scripts
    build_readme.py               # Generate README.md from metadata
    build_epub.py                 # Build EPUBs from TXT files
    build_covers.py               # Generate cover images in parallel
    check_books.py                # Validate structure and metadata
    fix_metadata.py               # Repair common metadata issues
    cover_utils.py                # Shared cover-generation helpers
```

## Metadata Format (metadata/*.json)

Required fields: `title`, `author`, `model`, `language`, `status`, `TXT_path`, `EPUB_path`, `cover_path`
Series books also require: `number`

All paths are relative to repo root (e.g. `books/Foo/txt/Foo.txt`).
Model is stored directly in metadata (e.g. `deepseek-v4-flash`, `gpt-5.5`).
`status` is always `"completed"` for published books.

## Tool Scripts — Usage

### `tools/build_readme.py`
- Scans `books/` and `series/` directories, reads metadata JSONs
- Generates `README.md` with:
  - Catalog grids (Series + Books) — `<details open>` tables with cover thumbnails
  - Series accordion — nested `<details>`: Series > Series_Name > Book N — Title
  - Books accordion — flat `<details>` per standalone book
- Run: `python3 tools/build_readme.py`

### `tools/build_epub.py`
Two modes:
- **Auto-scan** (no args): scans all metadata JSONs, builds EPUBs in parallel via `ProcessPoolExecutor`
- **Single-book** (`--metadata`, `--cover`, `--out`): legacy mode
- `--force` to overwrite existing EPUBs

### `tools/build_covers.py`
- Scans all book/series directories, runs each book's `tools/create_cover.py` via subprocess in parallel
- `--force` to overwrite, `-j N` for worker count (default: CPU count)
- Each book has its own `create_cover.py` with unique artwork logic

### `tools/check_books.py`
- Validates all 400+ books: metadata fields, folder existence (`txt/`, `epub/`, `covers/`, `metadata/`), file path correctness
- WARN for empty folders or missing files, ERR for missing required metadata fields
- Run: `python3 tools/check_books.py`

### `tools/fix_metadata.py`
- Repairs empty models (defaults to `deepseek-v4-flash`) and missing `cover_path`/`TXT_path`/`EPUB_path` fields
- Run: `python3 tools/fix_metadata.py`

## Conventions

- **Book directory names**: `Snake_Case` matching title (e.g. `The_Clockmakers_Daughter`)
- **Filenames**: same snake_case as directory (no spaces in paths)
- **Series naming**: `series/<Series_Name>/metadata/Book<N>_<Book_Name>_metadata.json`
- **Cover image path**: `covers/<Book_Name>.png`
- **EPUB reader URL**: `https://epub-reader-omega.vercel.app/?epub={GITHUB_RAW}/{EPUB_path}`
- **GitHub raw base**: `https://github.com/bariskisir/AI-Books/raw/refs/heads/master`
- **All paths in metadata are relative**, repo-root-relative

## Workflows

### Add a new book
1. Create `books/<Book_Name>/` with `metadata/`, `txt/`, `epub/`, `covers/` folders
2. Write metadata JSON with at least the required fields (use an existing book as template)
3. (Optional) Write `tools/create_cover.py` for custom cover generation
4. Run `tools/build_epub.py` to generate EPUB
5. Run `tools/build_covers.py` to generate cover
6. Run `tools/build_readme.py` to regenerate README

### Add a new series
1. Create `series/<Series_Name>/` directory
2. Add books as `metadata/Book<N>_<Book_Name>_metadata.json` with `number` field
3. `txt/`, `epub/`, `covers/` are shared folders for all books in the series
4. Run same build scripts as standalone books

### Before committing
Scripts are only run when explicitly requested. Do not run them unless told to.
