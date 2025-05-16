#!/usr/bin/env python3
"""
folder_reporter.py

A simple script to scan a directory tree, summarize file counts, sizes, and types,
and output a JSON report along with a quick console summary.
"""
import os
import argparse
import json
from collections import defaultdict

# Gemini Review: This script focuses on summarizing directory contents rather than collecting individual file paths.
# Strengths:
# - Uses os.walk() for directory traversal.
# - Collects per-folder summaries (path, num_files, size).
# - Aggregates overall file/directory counts and file extensions.
# - Outputs a JSON report and console summary.
# - Uses argparse for CLI arguments.
# Weaknesses:
# - Does NOT collect or store individual full file paths. This is a major limitation for fuzzy file searching.
# - The report is structured around folder summaries, not a list of all files.
# - Uses os.path.getsize() for each file; could be less performant than entry.stat() if direntries from os.walk were used.
# Relevance to fuzzy file searching:
# - Low direct relevance for fuzzy *file* searching due to the lack of a comprehensive list of file paths.
# - Could potentially be used to fuzzy search for directory paths based on its 'folder_reports'.
# - Would require significant modification to be a data source for fuzzy file searching.


def get_folder_report(root_path):
    report = {
        "root": os.path.abspath(root_path),
        "total_dirs": 0,
        "total_files": 0,
        "by_extension": {},
        "folders": [],
    }
    ext_counts = defaultdict(int)
    folder_reports = []

    for dirpath, dirnames, filenames in os.walk(root_path):
        report["total_dirs"] += 1
        folder_size = 0

        # Count files and sizes in this folder
        for filename in filenames:
            report["total_files"] += 1
            ext = os.path.splitext(filename)[1].lower() or "<no_ext>"
            ext_counts[ext] += 1
            filepath = os.path.join(dirpath, filename)
            # Gemini Review: Note - Individual filepaths are constructed here but not stored in the final report
            # for all files, which is needed for a general fuzzy file searcher.
            try:
                size = os.path.getsize(filepath)
            except OSError:
                size = 0
            folder_size += size

        folder_reports.append(
            {
                "path": os.path.abspath(dirpath),
                "num_files": len(filenames),
                "size_bytes": folder_size,
            }
        )

    # Sort extensions by count descending
    report["by_extension"] = dict(
        sorted(ext_counts.items(), key=lambda x: x[1], reverse=True)
    )
    report["folders"] = folder_reports
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Explore folders and generate a report on file organization."
    )
    parser.add_argument("root", help="Root directory to scan")
    parser.add_argument(
        "-o", "--output", help="Output JSON report file", default="folder_report.json"
    )
    args = parser.parse_args()

    report = get_folder_report(args.root)
    with open(args.output, "w") as f:
        json.dump(report, f, indent=4)

    # Console summary
    print(f"Scan complete! Report saved to {args.output}")
    print(f"Total directories: {report['total_dirs']}")
    print(f"Total files: {report['total_files']}")
    print("Top file types by count:")
    for ext, count in list(report["by_extension"].items())[:10]:
        print(f"  {ext}: {count}")

    print("\nMay the automation be ever in your favor.")


if __name__ == "__main__":
    main()
