#!/usr/bin/env python3
"""Validate book directory structure and metadata completeness."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_META = {"title", "author", "model", "language", "status", "TXT_path", "EPUB_path", "cover_path"}
SERIES_META = {"number"} | REQUIRED_META
IGNORE_ORPHANS = {"README.md", "prompt.txt", "reports", "chapters"}
EXPECTED_SUBDIRS = {"metadata", "txt", "epub", "covers"}
EXPECTED_OPTIONAL = {"tools", "planning"}


def scan_meta() -> list[tuple[Path, dict, str, Path]]:
    results: list[tuple[Path, dict, str, Path]] = []
    for base_name, is_series in [("books", False), ("series", True)]:
        base = ROOT / base_name
        if not base.exists():
            continue
        for child in sorted(base.iterdir()):
            if not child.is_dir() or child.name == "Sample_Book":
                continue
            meta_dir = child / "metadata"
            if not meta_dir.exists():
                results.append((None, {}, f"{base_name}/{child.name}", child))
                continue
            for meta_file in sorted(meta_dir.glob("*.json")):
                try:
                    meta = json.loads(meta_file.read_text(encoding="utf-8-sig"))
                except Exception as e:
                    results.append((meta_file, {"_parse_error": str(e)}, f"{base_name}/{child.name}", child))
                    continue
                results.append((meta_file, meta, f"{base_name}/{child.name}", child))
    return results


def check_book(meta: dict, label: str, child: Path) -> list[str]:
    issues: list[str] = []

    if "_parse_error" in meta:
        issues.append(f"metadata JSON parse error: {meta['_parse_error']}")
        return issues

    required = SERIES_META if label.startswith("series") else REQUIRED_META
    missing = required - set(meta.keys())
    if missing:
        issues.append(f"missing metadata fields: {', '.join(sorted(missing))}")

    if not meta.get("model", ""):
        issues.append("model is empty")

    # Check expected subdirectories exist
    for sub in EXPECTED_SUBDIRS:
        subdir = child / sub
        if not subdir.exists():
            issues.append(f"missing folder: {sub}/")
        elif not any(subdir.iterdir()):
            issues.append(f"empty folder: {sub}/")

    # Verify referenced path files exist
    for key, subdir in (("TXT_path", "txt"), ("EPUB_path", "epub"), ("cover_path", "covers")):
        path_str = meta.get(key, "")
        if not path_str:
            continue
        full = ROOT / path_str

        if key == "EPUB_path" and not full.exists():
            continue

        if not full.exists():
            issues.append(f"{key} not found: {path_str}")

    return issues


def check_orphans(child: Path) -> list[str]:
    issues: list[str] = []
    allowed = EXPECTED_SUBDIRS | EXPECTED_OPTIONAL
    for entry in child.iterdir():
        if entry.name.startswith("."):
            continue
        if entry.name in allowed or entry.name in IGNORE_ORPHANS:
            continue
        if entry.suffix == ".py" and entry.parent.name == "tools":
            continue
        issues.append(f"unexpected file/folder: {entry.name}")
    return issues


def main() -> None:
    entries = scan_meta()
    total = len(entries)
    issues_list: list[str] = []
    checked_dirs: set[Path] = set()

    for meta_path, meta, label, child in entries:
        issues = check_book(meta, label, child)
        if issues:
            for issue in issues:
                tag = "ERR" if issue.startswith("missing metadata") or issue.startswith("metadata JSON") else "WARN"
                issues_list.append(f"  {tag}   {label}: {issue}")

        if child not in checked_dirs:
            checked_dirs.add(child)
            orphan_issues = check_orphans(child)
            for issue in orphan_issues:
                issues_list.append(f"  WARN  {label}: {issue}")

    print(f"Checked {total} book(s)\n")

    err_count = sum(1 for w in issues_list if w.startswith("  ERR"))
    warn_count = sum(1 for w in issues_list if w.startswith("  WARN"))

    if issues_list:
        print("Issues:\n")
        for w in issues_list:
            print(w)
        print()

    print(f"Total: {total}  |  ERR: {err_count}  |  WARN: {warn_count}")


if __name__ == "__main__":
    main()
