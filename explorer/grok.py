import os
import csv
from datetime import datetime
import pathlib
from collections import defaultdict
import sys

# Gemini Review: This script is excellent for collecting detailed file and directory metadata into a flat list,
# which is highly suitable for implementing fuzzy file searching.
# Strengths:
# - Uses os.walk() for robust directory traversal.
# - Comprehensive get_file_metadata function.
# - Builds a flat list (file_data) of dictionaries, each containing full path and metadata.
#   This is a key strength for fuzzy searching.
# - Good error handling for file access.
# - Detailed analysis of collected data (extensions, sizes, depth).
# - Outputs both CSV and human-readable summary reports.
# - Well-structured with good separation of concerns.
# Weaknesses:
# - Calls os.stat() for every item; could potentially be optimized by using scandir-like approaches for very large directories if performance is critical.
# - file_data includes both files and directories; may need filtering depending on search target, but also allows searching for directories.
# Relevance to fuzzy file searching:
# - Excellent. The file_data list (containing item['path']) is a perfect input for a fuzzy search algorithm.
# - Collected metadata can be used to refine/rank search results.
# - While it doesn't implement fuzzy search, it provides the ideal data preparation.


def get_file_metadata(file_path):
    """Extract metadata for a single file."""
    # Gemini Review: Strong - Comprehensive metadata collection for each entry.
    try:
        stats = os.stat(file_path)
        path = pathlib.Path(file_path)
        return {
            "path": str(path),
            "name": path.name,
            "extension": path.suffix.lower() or ".none",
            "size_bytes": stats.st_size,
            "size_mb": stats.st_size / (1024 * 1024),
            "modified": datetime.fromtimestamp(stats.st_mtime).strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
            "is_dir": path.is_dir(),
        }
    except (OSError, PermissionError) as e:
        return {
            "path": file_path,
            "name": pathlib.Path(file_path).name,
            "extension": ".error",
            "size_bytes": 0,
            "size_mb": 0,
            "modified": "N/A",
            "is_dir": False,
            "error": str(e),
        }


def scan_directory(root_path):
    """Recursively scan directory and collect file metadata."""
    file_data = []
    # Gemini Review: Strong - Storing all file/directory metadata in a flat list like 'file_data' is ideal for fuzzy searching over paths.
    dir_count = 0
    file_count = 0
    errors = []

    for root, dirs, files in os.walk(root_path, followlinks=False):
        # Process directories
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            metadata = get_file_metadata(dir_path)
            file_data.append(metadata)
            dir_count += 1

        # Process files
        for file_name in files:
            file_path = os.path.join(root, file_name)
            metadata = get_file_metadata(file_path)
            if "error" in metadata:
                errors.append(f"Error accessing {file_path}: {metadata['error']}")
            else:
                file_data.append(metadata)
                file_count += 1

    return file_data, dir_count, file_count, errors


def analyze_file_data(file_data):
    """Analyze file data for organizational insights."""
    ext_counts = defaultdict(int)
    size_by_ext = defaultdict(float)
    depth_counts = defaultdict(int)

    for item in file_data:
        if not item["is_dir"]:
            ext_counts[item["extension"]] += 1
            size_by_ext[item["extension"]] += item["size_mb"]
            depth = len(pathlib.Path(item["path"]).parts)
            depth_counts[depth] += 1

    return {
        "extension_counts": dict(ext_counts),
        "size_by_extension_mb": dict(size_by_ext),
        "depth_distribution": dict(depth_counts),
    }


def write_csv_report(file_data, output_path):
    """Write file metadata to CSV."""
    headers = [
        "path",
        "name",
        "extension",
        "size_bytes",
        "size_mb",
        "modified",
        "is_dir",
    ]
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(file_data)


def write_summary_report(analysis, dir_count, file_count, errors, output_path):
    """Write human-readable summary report."""
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(
            f"Directory Analysis Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        f.write("=" * 80 + "\n\n")

        f.write(f"Total Directories: {dir_count}\n")
        f.write(f"Total Files: {file_count}\n")
        f.write(f"Total Errors: {len(errors)}\n\n")

        f.write("File Extension Distribution:\n")
        for ext, count in sorted(
            analysis["extension_counts"].items(), key=lambda x: x[1], reverse=True
        ):
            f.write(
                f"  {ext or '.none'}: {count} files ({analysis['size_by_extension_mb'].get(ext, 0):.2f} MB)\n"
            )

        f.write("\nFolder Depth Distribution:\n")
        for depth, count in sorted(analysis["depth_distribution"].items()):
            f.write(f"  Depth {depth}: {count} items\n")

        if errors:
            f.write("\nErrors Encountered:\n")
            for error in errors[:10]:  # Limit to first 10 errors
                f.write(f"  {error}\n")
            if len(errors) > 10:
                f.write(f"  ... and {len(errors) - 10} more errors\n")


def main(root_path):
    """Main function to run the analysis."""
    root_path = os.path.abspath(root_path)
    if not os.path.exists(root_path):
        print(f"Error: Path {root_path} does not exist.")
        return

    print(f"Scanning directory: {root_path}")
    file_data, dir_count, file_count, errors = scan_directory(root_path)

    print("Analyzing data...")
    analysis = analyze_file_data(file_data)

    output_dir = os.path.join(os.path.dirname(root_path), "folder_analysis")
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "file_report.csv")
    summary_path = os.path.join(output_dir, "summary_report.txt")

    print(f"Writing reports to {output_dir}")
    write_csv_report(file_data, csv_path)
    write_summary_report(analysis, dir_count, file_count, errors, summary_path)

    print("\nBasic Recommendations for Automation:")
    print("- Group files by extension (e.g., separate media, documents, code)")
    print("- Archive old files based on modification date")
    print("- Consolidate shallow folders to reduce depth")
    print(f"See {summary_path} for detailed insights.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python folder_analyzer.py <directory_path>")
        sys.exit(1)
    main(sys.argv[1])
