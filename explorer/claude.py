import os
import sys
import time
from datetime import datetime
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Gemini Review: A comprehensive, class-based folder analysis tool with detailed reporting and visualization.
# Strengths:
# - Object-oriented design (FolderAnalyzer class).
# - Extensive metadata collection (extensions, sizes, depths, large/empty/deep/recent/old files).
# - Supports exclusions and max scan depth.
# - Generates detailed text reports, CSVs (via pandas), and plots (via matplotlib).
# - Good error handling and interactive CLI.
# - Stores file paths in categorized lists (e.g., self.large_files, self.recent_files).
# Weaknesses:
# - Does NOT maintain a single, consolidated list of ALL file paths encountered. This is a key missing piece for a general fuzzy file searcher.
# - Focus is on detailed auditing rather than preparing a simple, flat list of all file paths for searching.
# - Uses os.path.getsize()/getmtime() repeatedly; could be optimized for very large datasets (e.g. using os.scandir style).
# Relevance to fuzzy file searching:
# - Partially relevant with strong potential. It processes all file paths.
# - To be used for general fuzzy file search, the 'analyze' method would need modification to store all file_path values
#   into a dedicated master list (e.g., self.all_file_paths = []).
# - Existing categorized lists of paths (large_files, etc.) could support targeted fuzzy searches.
# - Rich metadata could be used to rank/filter fuzzy search results if a full path list was available.


class FolderAnalyzer:
    def __init__(self, root_path=None):
        """Initialize the folder analyzer with a root path."""
        if root_path is None:
            self.root_path = os.getcwd()  # Default to current directory
        else:
            self.root_path = os.path.abspath(root_path)

        self.file_extensions = defaultdict(int)
        self.file_sizes = defaultdict(list)
        self.folder_counts = defaultdict(int)
        self.large_files = []
        self.empty_folders = []
        self.deep_paths = []
        self.recent_files = []
        self.old_files = []
        self.stats = {
            "total_files": 0,
            "total_folders": 0,
            "total_size": 0,
            "max_depth": 0,
        }

    def analyze(self, max_depth=None, exclude_dirs=None):
        """Analyze the folder structure."""
        # Gemini Review: Suggestion for fuzzy search enhancement:
        # Initialize a list here: self.all_file_paths = []
        if exclude_dirs is None:
            exclude_dirs = []

        print(f"\nAnalyzing directory: {self.root_path}")
        print("=" * 50)
        print("Scanning folders and files... This may take a while.")

        start_time = time.time()

        # Walk through directory structure
        for root, dirs, files in os.walk(self.root_path):
            # Skip excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            # Calculate current depth
            rel_path = os.path.relpath(root, self.root_path)
            depth = 0 if rel_path == "." else rel_path.count(os.sep) + 1

            # Check if we've exceeded max depth
            if max_depth is not None and depth > max_depth:
                dirs[:] = []  # Don't go deeper
                continue

            # Update max depth
            self.stats["max_depth"] = max(self.stats["max_depth"], depth)

            # Update folder count
            self.stats["total_folders"] += 1
            self.folder_counts[depth] += 1

            # Check for empty folders
            if not dirs and not files:
                self.empty_folders.append(root)

            # Check for deep paths
            if depth >= 5:  # Consider paths with depth >= 5 as deep
                self.deep_paths.append((depth, root))

            # Process files in current directory
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    # Gemini Review: Suggestion for fuzzy search enhancement:
                    # Add to a master list: self.all_file_paths.append(file_path)

                    # Skip if not a file (symlinks, etc.)
                    if not os.path.isfile(file_path):
                        continue

                    # Get file stats
                    file_size = os.path.getsize(file_path)
                    file_ext = os.path.splitext(file)[1].lower() or "(no extension)"
                    mod_time = os.path.getmtime(file_path)
                    mod_date = datetime.fromtimestamp(mod_time)

                    # Update counters
                    self.stats["total_files"] += 1
                    self.stats["total_size"] += file_size
                    self.file_extensions[file_ext] += 1
                    self.file_sizes[file_ext].append(file_size)

                    # Track large files (> 100MB)
                    if file_size > 100 * 1024 * 1024:
                        self.large_files.append((file_size, file_path))

                    # Track recent files (modified in the last 7 days)
                    days_old = (datetime.now() - mod_date).days
                    if days_old <= 7:
                        self.recent_files.append((days_old, file_path))

                    # Track old files (not modified in over a year)
                    if days_old > 365:
                        self.old_files.append((days_old, file_path))

                except (PermissionError, FileNotFoundError) as e:
                    print(f"Error accessing {os.path.join(root, file)}: {e}")

        elapsed_time = time.time() - start_time
        print(f"Analysis complete in {elapsed_time:.2f} seconds.")

    def generate_report(self, output_dir=None):
        """Generate a detailed report of the analysis."""
        if output_dir is None:
            output_dir = os.getcwd()

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        report_path = os.path.join(
            output_dir, f"folder_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        )
        os.makedirs(report_path, exist_ok=True)

        # Summary text report
        with open(os.path.join(report_path, "summary_report.txt"), "w") as f:
            f.write("=" * 50 + "\n")
            f.write("FOLDER STRUCTURE ANALYSIS REPORT\n")
            f.write("=" * 50 + "\n\n")

            f.write(f"Root directory: {self.root_path}\n")
            f.write(
                f"Analysis date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            )

            f.write("SUMMARY STATISTICS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total files: {self.stats['total_files']:,}\n")
            f.write(f"Total folders: {self.stats['total_folders']:,}\n")
            f.write(f"Total size: {self.format_size(self.stats['total_size'])}\n")
            f.write(f"Maximum folder depth: {self.stats['max_depth']}\n\n")

            # File type distribution
            f.write("FILE TYPE DISTRIBUTION\n")
            f.write("-" * 30 + "\n")
            sorted_extensions = sorted(
                self.file_extensions.items(), key=lambda x: x[1], reverse=True
            )
            for ext, count in sorted_extensions[:20]:  # Top 20 extensions
                avg_size = sum(self.file_sizes[ext]) / count if count > 0 else 0
                f.write(
                    f"{ext:<15} {count:>6,} files    Avg size: {self.format_size(avg_size)}\n"
                )
            if len(sorted_extensions) > 20:
                f.write("... and more\n")
            f.write("\n")

            # Directory depth
            f.write("DIRECTORY DEPTH DISTRIBUTION\n")
            f.write("-" * 30 + "\n")
            for depth in sorted(self.folder_counts.keys()):
                f.write(f"Depth {depth}: {self.folder_counts[depth]:,} folders\n")
            f.write("\n")

            # Large files
            if self.large_files:
                f.write("LARGE FILES (>100MB)\n")
                f.write("-" * 30 + "\n")
                for size, path in sorted(self.large_files, reverse=True)[:20]:
                    f.write(f"{self.format_size(size):<10} {path}\n")
                if len(self.large_files) > 20:
                    f.write(f"... and {len(self.large_files) - 20} more large files\n")
                f.write("\n")

            # Empty folders
            if self.empty_folders:
                f.write("EMPTY FOLDERS\n")
                f.write("-" * 30 + "\n")
                for folder in self.empty_folders[:20]:
                    f.write(f"{folder}\n")
                if len(self.empty_folders) > 20:
                    f.write(
                        f"... and {len(self.empty_folders) - 20} more empty folders\n"
                    )
                f.write("\n")

            # Deep paths
            if self.deep_paths:
                f.write("DEEP PATHS (depth >= 5)\n")
                f.write("-" * 30 + "\n")
                for depth, path in sorted(self.deep_paths, reverse=True)[:20]:
                    f.write(f"Depth {depth}: {path}\n")
                if len(self.deep_paths) > 20:
                    f.write(f"... and {len(self.deep_paths) - 20} more deep paths\n")
                f.write("\n")

            # Recent files
            if self.recent_files:
                f.write("RECENTLY MODIFIED FILES (last 7 days)\n")
                f.write("-" * 30 + "\n")
                for days, path in sorted(self.recent_files)[:20]:
                    f.write(f"{days} day{'s' if days != 1 else ''} ago: {path}\n")
                if len(self.recent_files) > 20:
                    f.write(
                        f"... and {len(self.recent_files) - 20} more recent files\n"
                    )
                f.write("\n")

            # Old files
            if self.old_files:
                f.write("OLD FILES (not modified in over a year)\n")
                f.write("-" * 30 + "\n")
                for days, path in sorted(self.old_files, reverse=True)[:20]:
                    years = days / 365
                    f.write(f"{years:.1f} years old: {path}\n")
                if len(self.old_files) > 20:
                    f.write(f"... and {len(self.old_files) - 20} more old files\n")

            f.write("\n")
            f.write("=" * 50 + "\n")
            f.write("End of Report\n")

        # Generate CSV data
        self._generate_csv_data(report_path)

        # Generate visualizations
        self._generate_visualizations(report_path)

        print(f"\nReport generated at: {report_path}")
        return report_path

    def _generate_csv_data(self, report_path):
        """Generate CSV files with detailed data."""
        # File extensions data
        ext_data = []
        for ext, count in self.file_extensions.items():
            total_size = sum(self.file_sizes[ext])
            avg_size = total_size / count if count > 0 else 0
            ext_data.append(
                {
                    "Extension": ext,
                    "Count": count,
                    "Total Size (bytes)": total_size,
                    "Average Size (bytes)": avg_size,
                    "Percentage": (
                        (count / self.stats["total_files"]) * 100
                        if self.stats["total_files"] > 0
                        else 0
                    ),
                }
            )
        pd.DataFrame(ext_data).to_csv(
            os.path.join(report_path, "file_extensions.csv"), index=False
        )

        # Folder depth data
        depth_data = []
        for depth, count in self.folder_counts.items():
            depth_data.append(
                {
                    "Depth": depth,
                    "Count": count,
                    "Percentage": (
                        (count / self.stats["total_folders"]) * 100
                        if self.stats["total_folders"] > 0
                        else 0
                    ),
                }
            )
        pd.DataFrame(depth_data).to_csv(
            os.path.join(report_path, "folder_depths.csv"), index=False
        )

        # Large files data
        if self.large_files:
            large_files_data = []
            for size, path in self.large_files:
                name = os.path.basename(path)
                directory = os.path.dirname(path)
                extension = os.path.splitext(name)[1].lower() or "(no extension)"
                large_files_data.append(
                    {
                        "Name": name,
                        "Path": path,
                        "Directory": directory,
                        "Extension": extension,
                        "Size (bytes)": size,
                        "Size (formatted)": self.format_size(size),
                    }
                )
            pd.DataFrame(large_files_data).to_csv(
                os.path.join(report_path, "large_files.csv"), index=False
            )

    def _generate_visualizations(self, report_path):
        """Generate visualizations of the data."""
        plt.figure(figsize=(10, 6))

        # Top file extensions pie chart
        plt.figure(figsize=(12, 8))
        extensions = dict(
            sorted(self.file_extensions.items(), key=lambda x: x[1], reverse=True)[:10]
        )
        if len(self.file_extensions) > 10:
            extensions["Others"] = sum(
                count
                for ext, count in self.file_extensions.items()
                if ext
                not in dict(
                    sorted(
                        self.file_extensions.items(), key=lambda x: x[1], reverse=True
                    )[:10]
                )
            )
        plt.pie(
            extensions.values(),
            labels=extensions.keys(),
            autopct="%1.1f%%",
            shadow=True,
            startangle=140,
        )
        plt.axis("equal")
        plt.title("Top File Extensions")
        plt.savefig(
            os.path.join(report_path, "file_extensions_pie.png"), bbox_inches="tight"
        )
        plt.close()

        # Folder depth bar chart
        plt.figure(figsize=(12, 8))
        depths = sorted(self.folder_counts.keys())
        counts = [self.folder_counts[d] for d in depths]
        plt.bar(depths, counts)
        plt.xlabel("Folder Depth")
        plt.ylabel("Number of Folders")
        plt.title("Folder Depth Distribution")
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.savefig(os.path.join(report_path, "folder_depths.png"), bbox_inches="tight")
        plt.close()

    @staticmethod
    def format_size(size_bytes):
        """Format file size in human readable format."""
        if size_bytes == 0:
            return "0 B"
        size_names = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while size_bytes >= 1024 and i < len(size_names) - 1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.2f} {size_names[i]}"


def main():
    """Main function to run the folder analyzer."""
    print("Folder Structure Analyzer")
    print("=" * 50)

    # Get root directory
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        root_dir = input(
            "Enter the root directory to analyze [Enter for current directory]: "
        )
        if not root_dir:
            root_dir = os.getcwd()

    # Validate directory
    if not os.path.isdir(root_dir):
        print(f"Error: '{root_dir}' is not a valid directory.")
        return

    # Get max depth
    try:
        max_depth_input = input(
            "Maximum folder depth to analyze [Enter for unlimited]: "
        )
        max_depth = int(max_depth_input) if max_depth_input else None
    except ValueError:
        print("Invalid input. Using unlimited depth.")
        max_depth = None

    # Get excluded directories
    exclude_input = input("Directories to exclude (comma-separated) [Enter for none]: ")
    exclude_dirs = (
        [d.strip() for d in exclude_input.split(",")] if exclude_input else []
    )

    # Initialize and run analyzer
    analyzer = FolderAnalyzer(root_dir)
    analyzer.analyze(max_depth=max_depth, exclude_dirs=exclude_dirs)

    # Generate report
    output_dir = input("Output directory for report [Enter for current directory]: ")
    if not output_dir:
        output_dir = os.getcwd()

    report_path = analyzer.generate_report(output_dir)

    print("\nAnalysis complete!")
    print(f"Report files saved to: {report_path}")
    print("\nOrganization Insights:")
    print("-" * 50)

    # Provide insights
    if analyzer.empty_folders:
        print(
            f"- Found {len(analyzer.empty_folders)} empty folders that could be removed"
        )

    if analyzer.deep_paths:
        print(
            f"- Found {len(analyzer.deep_paths)} deeply nested folders (depth ≥ 5) that might benefit from restructuring"
        )

    if analyzer.large_files:
        print(
            f"- Found {len(analyzer.large_files)} large files (>100MB) that could be archived or moved"
        )

    if analyzer.old_files:
        print(
            f"- Found {len(analyzer.old_files)} files not modified in over a year that might be obsolete"
        )

    # Most common file types
    top_exts = sorted(
        analyzer.file_extensions.items(), key=lambda x: x[1], reverse=True
    )[:3]
    if top_exts:
        print(
            f"- Most common file types: {', '.join(f'{ext} ({count} files)' for ext, count in top_exts)}"
        )

    print(
        "\nUse this information to identify patterns and areas for improvement in your file organization."
    )


if __name__ == "__main__":
    main()
