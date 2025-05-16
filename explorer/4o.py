import os
import json
import time
from collections import defaultdict

# Gemini Review: This script is very similar to quen-30b-4q.py and provides a good foundation for directory scanning.
# Strengths:
# - Collects comprehensive metadata (file/dir counts, extensions, largest/recent files).
# - Builds a directory_tree, representing the hierarchical structure.
# - Includes max_depth to prevent excessive recursion.
# - Gracefully handles PermissionError.
# - Outputs a clear summary and saves a JSON report.
# Weaknesses:
# - Uses os.path.getsize() and os.path.getmtime() instead of entry.stat(), which can be slightly less efficient as os.scandir() already provides a stat object.
# - The 'directory_tree' only stores directory names, not files within the tree structure itself. File info is aggregated separately.
#   This makes it less direct for path-based fuzzy searching.
# - The primary data structures are geared towards auditing rather than optimized fuzzy searching of file paths.
# Relevance to fuzzy file searching:
# - The core scanning logic is a good starting point for collecting file paths.
# - The list of full file paths (available through 'largest_files', 'recent_files', or by modifying 'scan' to collect all paths)
#   could be fed into a separate fuzzy search algorithm.
# - To be more directly useful for fuzzy search, the 'scan' function could build a flat list of all file paths
#   or a tree structure that includes files at each node.


def scan_directory(base_path, max_depth=5):
    report = {
        "total_files": 0,
        "total_dirs": 0,
        "file_extensions": defaultdict(int),
        "largest_files": [],
        "recent_files": [],
        "directory_tree": {},
    }

    def scan(path, depth):
        if depth > max_depth:
            return {}

        tree = {}
        try:
            with os.scandir(path) as it:
                for entry in it:
                    full_path = os.path.join(path, entry.name)
                    if entry.is_dir(follow_symlinks=False):
                        report["total_dirs"] += 1
                        # Gemini Review: Suggestion - For fuzzy search, the tree could also store file entries here.
                        tree[entry.name] = scan(full_path, depth + 1)
                    elif entry.is_file(follow_symlinks=False):
                        report["total_files"] += 1
                        ext = os.path.splitext(entry.name)[1].lower()
                        report["file_extensions"][ext] += 1

                        # Gemini Review: Note - quen-30b-4q.py uses entry.stat() here, which is generally more efficient.
                        size = os.path.getsize(full_path)
                        mtime = os.path.getmtime(full_path)

                        report["largest_files"].append((size, full_path))
                        report["recent_files"].append((mtime, full_path))
                        # Gemini Review: Suggestion - Consider collecting all file paths into a single list
                        # within the 'report' object for easier access by a fuzzy search function.
        except PermissionError:
            # Gemini Review: Strong - Good error handling.
            tree["<PermissionDenied>"] = {}
        return tree

    report["directory_tree"] = scan(base_path, 0)
    # Gemini Review: The 'directory_tree' currently only contains directories.
    # For a fuzzy file search, this tree would be more useful if it also contained file entries,
    # or if a separate flat list of all file paths was generated.

    # Top N insights
    report["largest_files"] = sorted(report["largest_files"], reverse=True)[:10]
    report["recent_files"] = sorted(report["recent_files"], reverse=True)[:10]
    report["file_extensions"] = dict(
        sorted(report["file_extensions"].items(), key=lambda x: -x[1])
    )

    return report


def summarize_report(report):
    print("\n🧾 Folder Audit Summary")
    print(f"Total directories: {report['total_dirs']}")
    print(f"Total files: {report['total_files']}")
    print("\nTop 10 File Types:")
    for ext, count in list(report["file_extensions"].items())[:10]:
        print(f"  {ext or '[no ext]'}: {count} files")

    print("\nTop 10 Largest Files:")
    for size, path in report["largest_files"]:
        print(f"  {size / 1024 / 1024:.2f} MB - {path}")

    print("\nTop 10 Most Recently Modified Files:")
    for mtime, path in report["recent_files"]:
        print(f"  {time.ctime(mtime)} - {path}")


if __name__ == "__main__":
    base_path = input("Enter the directory path to scan: ").strip()
    if not os.path.isdir(base_path):
        print("Invalid path. Please check and try again.")
    else:
        report = scan_directory(base_path)
        summarize_report(report)

        # Optional: save to JSON
        with open("folder_audit_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)

        print("\n✅ Report saved to 'folder_audit_report.json'")
