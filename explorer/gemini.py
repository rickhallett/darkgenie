import os
import datetime
import csv
from collections import Counter

# Gemini Review: A well-structured script that performs detailed directory analysis and collects comprehensive file metadata suitable for fuzzy searching.
# Strengths:
# - Uses os.walk() for traversal.
# - The 'analyze_directory' function creates 'file_details', a list of dictionaries, where each dictionary holds extensive metadata
#   (path, name, ext, size, mod_date) for EVERY file. This is ideal for fuzzy file searching.
# - Includes practical directory exclusion logic (e.g., .git, node_modules).
# - Skips symbolic links, preventing potential issues.
# - Good error handling during file processing.
# - Generates console summaries and detailed CSV reports for both files and folders.
# Weaknesses:
# - Calls os.stat() for each file/folder; potential for optimization in very high file count scenarios using scandir patterns, but generally robust.
# Relevance to fuzzy file searching:
# - Excellent. The 'file_details' list provides a direct and rich data source. Each item['path'] can be used for fuzzy matching.
# - Extensive metadata allows for sophisticated filtering/ranking of search results.
# - Directory exclusion helps in curating a relevant list of files for searching.


def get_human_readable_size(size_bytes):
    """Converts a size in bytes to a human-readable format."""
    if size_bytes == 0:
        return "0B"
    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024.0
        i += 1
    return f"{size_bytes:.2f}{size_name[i]}"


def analyze_directory(start_path):
    """
    Analyzes the directory structure starting from start_path.
    Returns lists of file details and folder details, and a summary.
    """
    file_details = []
    # Gemini Review: Strong - 'file_details' will store a dictionary of metadata for each file, including its full path.
    # This is an excellent structure for feeding a fuzzy search algorithm.
    folder_details = []

    total_files = 0
    total_folders = 0
    total_size_bytes = 0
    file_extensions = Counter()

    print(
        f"Starting analysis of: {start_path}\nThis might take a while for large directories...\n"
    )

    for root, dirs, files in os.walk(start_path, topdown=True):
        # Exclude common hidden/system folders to speed up and reduce noise
        # You can customize this list
        # Gemini Review: Strong - Practical feature to exclude irrelevant directories from the scan, improving focus for search.
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".")
            and d not in ["__pycache__", "node_modules", "venv", ".git"]
        ]

        current_folder_file_count = len(files)
        current_folder_subdir_count = len(dirs)

        folder_info = {
            "path": root,
            "name": os.path.basename(root),
            "file_count": current_folder_file_count,
            "subdir_count": current_folder_subdir_count,
            "last_modified_folder": datetime.datetime.fromtimestamp(
                os.path.getmtime(root)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }
        folder_details.append(folder_info)
        total_folders += 1

        for filename in files:
            try:
                file_path = os.path.join(root, filename)
                # Gemini Review: 'file_path' is the full path to the file, which will be stored. Perfect.

                # Skip symlinks to avoid errors or double counting if they point within the scanned tree
                if os.path.islink(file_path):
                    # Gemini Review: Good practice to handle symlinks explicitly.
                    print(f"Skipping symlink: {file_path}")
                    continue

                file_stat = os.stat(file_path)
                file_size = file_stat.st_size
                last_modified = datetime.datetime.fromtimestamp(
                    file_stat.st_mtime
                ).strftime("%Y-%m-%d %H:%M:%S")
                _, extension = os.path.splitext(filename)

                file_info = {
                    "path": file_path,
                    "name": filename,
                    "extension": extension.lower() if extension else "No Extension",
                    "size_bytes": file_size,
                    "size_readable": get_human_readable_size(file_size),
                    "last_modified": last_modified,
                    "parent_folder": root,
                }
                file_details.append(file_info)

                total_files += 1
                total_size_bytes += file_size
                if extension:
                    file_extensions[extension.lower()] += 1
                else:
                    file_extensions["No Extension"] += 1

            except FileNotFoundError:
                print(
                    f"Warning: File not found during scan (might be a temporary file or deleted): {file_path}"
                )
            except PermissionError:
                print(f"Warning: Permission denied for: {file_path}")
            except Exception as e:
                print(f"Warning: An unexpected error occurred with {file_path}: {e}")

    summary = {
        "start_path": start_path,
        "total_files_scanned": total_files,
        "total_folders_scanned": total_folders
        - 1,  # -1 because start_path itself is counted as a folder
        "total_size_bytes": total_size_bytes,
        "total_size_readable": get_human_readable_size(total_size_bytes),
        "file_type_distribution": file_extensions,
    }

    return file_details, folder_details, summary


def generate_console_report(summary, file_details):
    """Prints a summary report to the console."""
    print("\n--- Analysis Summary ---")
    print(f"Scanned Path: {summary['start_path']}")
    print(f"Total Files Scanned: {summary['total_files_scanned']}")
    print(f"Total Folders Scanned: {summary['total_folders_scanned']}")
    print(
        f"Total Size of All Files: {summary['total_size_readable']} ({summary['total_size_bytes']} bytes)"
    )

    print("\nTop 10 File Types by Count:")
    for ext, count in summary["file_type_distribution"].most_common(10):
        print(f"  {ext if ext else 'No Extension'}: {count}")

    if file_details:
        print("\nTop 5 Largest Files:")
        largest_files = sorted(
            file_details, key=lambda x: x["size_bytes"], reverse=True
        )[:5]
        for f_info in largest_files:
            print(f"  {f_info['path']} ({f_info['size_readable']})")

        print("\nTop 5 Oldest Files (by modification date):")
        # Ensure last_modified is a datetime object for proper sorting if needed, though string sort YYYY-MM-DD works
        oldest_files = sorted(file_details, key=lambda x: x["last_modified"])[:5]
        for f_info in oldest_files:
            print(f"  {f_info['path']} (Modified: {f_info['last_modified']})")
    print("--- End of Summary ---")


def generate_csv_report(
    file_details, folder_details, output_filename_base="folder_analysis"
):
    """Generates CSV reports for files and folders."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    # File Report
    file_report_name = f"{output_filename_base}_files_{timestamp}.csv"
    if file_details:
        file_keys = file_details[0].keys()
        with open(file_report_name, "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=file_keys)
            dict_writer.writeheader()
            dict_writer.writerows(file_details)
        print(f"\nDetailed file report saved to: {os.path.abspath(file_report_name)}")
    else:
        print("\nNo file details to write to CSV.")

    # Folder Report
    folder_report_name = f"{output_filename_base}_folders_{timestamp}.csv"
    if folder_details:
        folder_keys = folder_details[0].keys()
        with open(folder_report_name, "w", newline="", encoding="utf-8") as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=folder_keys)
            dict_writer.writeheader()
            dict_writer.writerows(folder_details)
        print(f"Detailed folder report saved to: {os.path.abspath(folder_report_name)}")
    else:
        print("No folder details to write to CSV.")


if __name__ == "__main__":
    start_directory = input("Enter the full path of the directory to analyze: ")

    if not os.path.isdir(start_directory):
        print(
            f"Error: The path '{start_directory}' is not a valid directory or does not exist."
        )
    else:
        try:
            files, folders, summary_data = analyze_directory(start_directory)
            generate_console_report(summary_data, files)
            generate_csv_report(files, folders)
            print("\nAnalysis complete.")
        except Exception as e:
            print(f"An unexpected error occurred during the process: {e}")
            import traceback

            traceback.print_exc()
