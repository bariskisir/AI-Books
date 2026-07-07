#!/usr/bin/env python3
"""Build cover images for all books by running each book's create_cover.py in parallel.

Usage:
    python3 tools/build_covers.py            # skip existing
    python3 tools/build_covers.py --force    # rebuild all
    python3 tools/build_covers.py -j 4       # 4 parallel workers
"""

from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def find_cover_jobs() -> list[tuple[str, Path, Path, Path]]:
    jobs: list[tuple[str, Path, Path, Path]] = []
    for base in [ROOT / "books", ROOT / "series"]:
        if not base.exists():
            continue
        for child in sorted(base.iterdir()):
            if not child.is_dir() or child.name == "Sample_Book":
                continue
            cover_script = child / "tools" / "create_cover.py"
            if not cover_script.exists():
                continue
            meta_dir = child / "metadata"
            if not meta_dir.exists():
                continue
            for meta_file in sorted(meta_dir.glob("*.json")):
                try:
                    metadata = json.loads(meta_file.read_text(encoding="utf-8-sig"))
                except Exception:
                    continue
                cover_path_str = metadata.get("cover_path", "")
                if cover_path_str:
                    cover_path = ROOT / cover_path_str
                else:
                    stem = meta_file.stem.replace("_metadata", "")
                    cover_path = child / "covers" / f"{stem}.png"
                label = metadata.get("title", meta_file.stem)
                jobs.append((label, meta_file, cover_path, cover_script))
    return jobs


def run_one(args: tuple[str, Path, Path, Path, bool]) -> str:
    label, meta_path, cover_path, cover_script, force = args
    if not force and cover_path.exists():
        return f"  EXISTS {label}"
    try:
        subprocess.run(
            [sys.executable, str(cover_script), "--metadata", str(meta_path), "--out", str(cover_path)],
            check=True, capture_output=True, text=True, cwd=ROOT,
        )
        return f"  OK    {label}"
    except subprocess.CalledProcessError as e:
        err = e.stderr.strip() or "unknown error"
        return f"  FAIL  {label}: {err}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Build covers for all books in parallel.")
    parser.add_argument("--force", action="store_true", help="Rebuild even if cover exists")
    parser.add_argument("-j", "--jobs", type=int, default=0, help="Parallel workers (0 = auto)")
    args = parser.parse_args()

    jobs = find_cover_jobs()
    print(f"Found {len(jobs)} cover script(s)")

    to_run = []
    skipped = 0
    for label, meta_path, cover_path, cover_script in jobs:
        if not args.force and cover_path.exists():
            skipped += 1
        else:
            to_run.append((label, meta_path, cover_path, cover_script, args.force))

    if skipped:
        print(f"  {skipped} already exist(s), use --force to rebuild")

    if not to_run:
        print("Nothing to build.")
        return

    workers = args.jobs or min(mp.cpu_count(), len(to_run))
    print(f"Building {len(to_run)} cover(s) with {workers} worker(s)...")

    with mp.Pool(workers) as pool:
        for result in pool.imap_unordered(run_one, to_run):
            print(result)

    print("Done.")


if __name__ == "__main__":
    main()
