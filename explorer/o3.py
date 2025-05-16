#!/usr/bin/env python3
"""
folder_scan.py

A pragmatic, mildly witty reconnaissance tool for your filesystem.
Run it on a directory and it will produce a JSON report plus a
console overview so you can finally see where all that digital lint
has been piling up.

Features
--------
* Counts and total size per file extension (".py", ".jpg", etc.)
* Top N largest files
* Top N heaviest directories
* Optional duplicate detection via SHA‑256 (size pre‑filter)
* Most recently modified files
* Outputs a timestamped JSON report (default: ./folder_scan_YYYYMMDD_HHMMSS.json)

Usage
-----
    python folder_scan.py ~/Documents --top 15 --dupes --out ./my_report.json

The script is designed to be dependency‑light: only Python ≥3.8 from the
standard library. It should run on macOS, Linux, and Windows.

Pro‑Tip
-------
Start with a dry‑run on a small folder before unleashing it on the
whole drive. You've been warned.

Gemini Review: A robust and feature-rich script for filesystem analysis, with excellent data collection for fuzzy search.
Strengths:
- Uses os.walk() and pathlib for effective file system traversal and path manipulation.
- The 'scan' function collects 'file_sizes', a list of (size, Path_object) for EVERY file. This is ideal for fuzzy search.
- Efficiently calculates directory sizes.
- Includes advanced features like duplicate file detection.
- Generates comprehensive JSON reports and a pretty console summary.
- Good CLI argument handling with argparse.
Weaknesses:
- For fuzzy search, paths would need to be str(Path_object). Minor point.
- mtime for recent files is re-read via .stat() instead of being collected in the initial scan (minor performance point, possibly mitigated by OS caching).
Relevance to fuzzy file searching:
- Excellent. The 'file_sizes' list from 'scan()' (specifically, the Path objects in it) provides a direct source of all file paths.
  A simple transformation [str(p.resolve()) for size, p in file_sizes] would yield the list of path strings needed for fuzzy matching.
- The overall structure is well-suited for adaptation into a fuzzy search data provider.
"""

import argparse
import datetime as _dt
import hashlib
import json
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


def human_size(num_bytes: int) -> str:
    """Convert a size in bytes to a human‑friendly string."""
    for unit in ["B", "KB", "MB", "GB", "TB", "PB"]:
        if num_bytes < 1024:
            return f"{num_bytes:.1f}\u00a0{unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f}\u00a0EB"


def sha256_for_file(path: Path, block_size: int = 65536) -> str:
    """Return SHA‑256 hex digest of a file."""
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(block_size), b""):
            h.update(block)
    return h.hexdigest()


def scan(
    root: Path, follow_symlinks: bool = False
) -> Tuple[Counter, Dict[str, int], List[Tuple[int, Path]], List[Tuple[int, Path]]]:
    """Walk directory tree and collect raw stats."""
    ext_counter: Counter[str] = Counter()
    ext_size: Dict[str, int] = defaultdict(int)
    file_sizes: List[Tuple[int, Path]] = []
    dir_sizes: Dict[Path, int] = defaultdict(int)

    for dirpath, dirnames, filenames in os.walk(root, followlinks=follow_symlinks):
        dp = Path(dirpath)
        for fname in filenames:
            path = dp / fname
            try:
                size = path.stat().st_size
            except (FileNotFoundError, PermissionError):
                continue
            ext = path.suffix.lower() or "<no‑ext>"
            ext_counter[ext] += 1
            ext_size[ext] += size
            file_sizes.append((size, path))

            # Propagate size up directory chain for directory sizes
            for parent in [dp, *dp.parents]:
                dir_sizes[parent] += size

    # Convert dir_sizes dict to list of tuples
    dir_size_list = [(size, d) for d, size in dir_sizes.items()]

    return ext_counter, ext_size, file_sizes, dir_size_list


def detect_duplicates(file_sizes: List[Tuple[int, Path]]) -> Dict[str, List[str]]:
    """Detect duplicate files by comparing SHA‑256 of files with same size."""
    # Group by size to avoid hashing everything
    size_buckets: Dict[int, List[Path]] = defaultdict(list)
    for size, path in file_sizes:
        size_buckets[size].append(path)

    dupes: Dict[str, List[str]] = defaultdict(list)
    for same_size_paths in size_buckets.values():
        if len(same_size_paths) < 2:
            continue
        hashes: Dict[str, List[str]] = defaultdict(list)
        for p in same_size_paths:
            try:
                digest = sha256_for_file(p)
            except (FileNotFoundError, PermissionError):
                continue
            hashes[digest].append(str(p))
        for digest, paths in hashes.items():
            if len(paths) > 1:
                dupes[digest] = paths
    return dupes


def build_report(
    root: Path, top_n: int, include_dupes: bool, follow_symlinks: bool
) -> Dict:
    """Build the JSON‑serializable report."""
    ext_counter, ext_size, file_sizes, dir_size_list = scan(root, follow_symlinks)

    # Sort structures
    ext_stats = sorted(
        ((ext, count, ext_size[ext]) for ext, count in ext_counter.items()),
        key=lambda x: x[2],
        reverse=True,
    )
    largest_files = sorted(file_sizes, key=lambda x: x[0], reverse=True)[:top_n]
    heaviest_dirs = sorted(dir_size_list, key=lambda x: x[0], reverse=True)[:top_n]
    recent_files = sorted(
        file_sizes, key=lambda x: (Path(x[1]).stat().st_mtime), reverse=True
    )[:top_n]

    report = {
        "scanned_root": str(root.resolve()),
        "generated_at": _dt.datetime.now().isoformat(timespec="seconds"),
        "extension_stats": [
            {"extension": ext, "count": count, "total_bytes": size}
            for ext, count, size in ext_stats
        ],
        "largest_files": [
            {"bytes": size, "path": str(path)} for size, path in largest_files
        ],
        "heaviest_directories": [
            {"bytes": size, "path": str(path)} for size, path in heaviest_dirs
        ],
        "most_recent_files": [
            {
                "modified": _dt.datetime.fromtimestamp(
                    Path(path).stat().st_mtime
                ).isoformat(timespec="seconds"),
                "bytes": size,
                "path": str(path),
            }
            for size, path in recent_files
        ],
    }

    if include_dupes:
        report["duplicates"] = detect_duplicates(file_sizes)

    return report


def pretty_print(report: Dict, top_n: int):
    """Print a concise overview to stdout."""
    print("\n===== Folder Scan Summary =====")
    print(f"Root scanned : {report['scanned_root']}")
    print(f"Generated    : {report['generated_at']}")
    print("\n-- File types by size --")
    for ext_info in report["extension_stats"][:top_n]:
        ext, count, size = (
            ext_info["extension"],
            ext_info["count"],
            ext_info["total_bytes"],
        )
        print(f"{ext:>10} : {count:>7} files consuming {human_size(size)}")

    print("\n-- Largest files --")
    for item in report["largest_files"]:
        print(f"{human_size(item['bytes']):>10} : {item['path']}")
    print("\n-- Heaviest directories --")
    for item in report["heaviest_directories"]:
        print(f"{human_size(item['bytes']):>10} : {item['path']}")
    print("\n-- Most recent files --")
    for item in report["most_recent_files"]:
        ts = item["modified"]
        print(f"{ts} : {item['path']}")
    if "duplicates" in report:
        dup_count = sum(len(v) for v in report["duplicates"].values())
        print(
            f"\n-- Duplicates detected: {dup_count} files across {len(report['duplicates'])} groups --"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Traverse a folder tree and produce a structured report."
    )
    parser.add_argument(
        "path",
        type=Path,
        default=Path.cwd(),
        help="Root directory to scan (default: current working directory)",
    )
    parser.add_argument(
        "--top",
        "-t",
        type=int,
        default=10,
        help="How many items to show in 'largest', 'heaviest', 'recent' lists (default: 10)",
    )
    parser.add_argument(
        "--dupes", action="store_true", help="Enable duplicate file detection (slower)"
    )
    parser.add_argument(
        "--follow-symlinks",
        action="store_true",
        help="Follow symbolic links when walking directories",
    )
    parser.add_argument(
        "--out",
        "-o",
        type=Path,
        default=None,
        help="Path to JSON report file (default: ./folder_scan_<timestamp>.json)",
    )

    args = parser.parse_args()

    if not args.path.exists():
        sys.exit(f"Provided path does not exist: {args.path}")

    report = build_report(
        args.path,
        top_n=args.top,
        include_dupes=args.dupes,
        follow_symlinks=args.follow_symlinks,
    )

    # Determine output file
    if args.out is None:
        timestamp = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        args.out = Path.cwd() / f"folder_scan_{timestamp}.json"

    try:
        with args.out.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"\nJSON report written to {args.out}")
    except OSError as e:
        print(f"Failed to write JSON report: {e}", file=sys.stderr)

    pretty_print(report, top_n=args.top)


if __name__ == "__main__":
    main()
