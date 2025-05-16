import os
import sys
import difflib  # Added for fuzzy matching

# Gemini Review: This file will combine the best path collection strategies and add fuzzy searching.
# Initial focus: Robustly collect all relevant file paths.


def collect_file_paths(start_path, exclude_dirs=None, follow_symlinks=False):
    """
    Recursively collects all file paths from a directory, applying exclusions.

    Args:
        start_path (str): The root directory to scan.
        exclude_dirs (list, optional): A list of directory names to exclude.
                                       Defaults to common system/dev folders.
        follow_symlinks (bool): Whether to follow symbolic links (default False).

    Returns:
        list: A list of absolute file path strings.
    """
    if exclude_dirs is None:
        exclude_dirs = [
            "__pycache__",
            "node_modules",
            "venv",
            ".git",
            ".svn",
            ".hg",
            "dist",
            "build",
            "target",
        ]

    collected_paths = []
    abs_start_path = os.path.abspath(start_path)

    if not os.path.isdir(abs_start_path):
        print(
            f"Error: Provided start_path '{start_path}' is not a valid directory.",
            file=sys.stderr,
        )
        return []

    for root, dirs, files in os.walk(
        abs_start_path, topdown=True, followlinks=follow_symlinks
    ):
        # Filter directories to exclude
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in exclude_dirs]

        for filename in files:
            file_path = os.path.join(root, filename)

            if not follow_symlinks and os.path.islink(file_path):
                # print(f"Skipping symlink: {file_path}", file=sys.stderr) # Optional: for debugging
                continue

            # Ensure it's a file (especially if follow_symlinks is True, dirs could yield links to files)
            if os.path.isfile(file_path):
                collected_paths.append(file_path)
            elif os.path.islink(file_path) and os.path.isfile(
                os.path.realpath(file_path)
            ):  # handles links to files
                collected_paths.append(os.path.realpath(file_path))

    return collected_paths


def fuzzy_match_paths(query, paths, cutoff=0.6, limit=20):
    """
    Finds and ranks file paths that fuzzy match the query.

    Args:
        query (str): The search query.
        paths (list): A list of file path strings to search within.
        cutoff (float): Similarity ratio cutoff (0.0 to 1.0).
                        Paths with a ratio below this will be ignored.
        limit (int): Maximum number of results to return.

    Returns:
        list: A list of tuples (score, path_string), sorted by score descending.
    """
    matches = []
    query_lower = query.lower()

    for path_str in paths:
        # For fuzzy matching, often matching against the filename itself is more relevant
        # than the whole path, or at least weighted more. We can also match against basename.
        path_basename_lower = os.path.basename(path_str).lower()

        # Using difflib.SequenceMatcher for ratio.
        # This can be slow for very large lists of paths and long queries.
        # Consider matching against basename first for relevance, then full path if needed, or combine scores.
        s_basename = difflib.SequenceMatcher(None, query_lower, path_basename_lower)
        ratio_basename = s_basename.ratio()

        # Optionally, also match against the full path or parts of it
        # For simplicity, let's prioritize basename match for now
        # s_fullpath = difflib.SequenceMatcher(None, query_lower, path_str.lower())
        # ratio_fullpath = s_fullpath.ratio()

        # Combine or choose ratio. For now, just use basename ratio.
        # A more advanced approach might weigh basename higher or combine scores.
        final_ratio = ratio_basename

        if final_ratio >= cutoff:
            matches.append((final_ratio, path_str))

    # Sort by score (ratio) in descending order
    matches.sort(key=lambda x: x[0], reverse=True)

    return matches[:limit]


if __name__ == "__main__":
    # Example Usage:
    target_directory = "."
    if len(sys.argv) > 1:
        target_directory = sys.argv[1]

    print(f"Scanning directory: {os.path.abspath(target_directory)}")
    all_files = collect_file_paths(target_directory)

    if all_files:
        print(f"\nFound {len(all_files)} files.")

        query = input("\nEnter a fuzzy search query: ").strip()
        if query:
            print(f"\nSearching for '{query}'...")

            # Use the new fuzzy_match_paths function
            # matched_paths = [p for p in all_files if query.lower() in p.lower()] # Old basic match
            matched_paths_with_scores = fuzzy_match_paths(query, all_files)

            if matched_paths_with_scores:
                print(
                    f"Found {len(matched_paths_with_scores)} matching paths (score >= 0.6):"
                )
                for score, match_path in matched_paths_with_scores:
                    print(f"  [{score:.2f}] {match_path}")
            else:
                print("No matches found with current fuzzy parameters.")
        else:
            print("No query entered. Listing top collected paths (up to 20):")
            for f_path in all_files[:20]:
                print(f"  {f_path}")
            if len(all_files) > 20:
                print(f"  ... and {len(all_files) - 20} more.")
    else:
        print("No files found or error in scanning.")

    print("\nGemini Review: Fuzzy matching with difflib added to maximized.py.")
    print(
        "Further improvements could include more sophisticated scoring (e.g., weighting filename vs full path), performance optimizations for very large lists, or using a dedicated fuzzy search library."
    )
