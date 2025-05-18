# Product Requirements Document: Enhanced File Explorer & Analyzer (maximized.py)

## 1. Introduction

**Current State:** `maximized.py` is a Python utility designed to scan a directory, collect all file paths (with exclusions for common non-relevant directories and symlink handling), and perform fuzzy searching on these paths using `difflib`.

**Vision:** To evolve `maximized.py` into a more comprehensive command-line tool for filesystem exploration, analysis, and searching. It should not only find files efficiently but also provide insights into the directory structure, file distribution, suggest structural improvements, and help users understand and navigate their data hierarchy more effectively, reducing "hierarchical friction points."

**Goals of these Enhancements:**
*   Improve the accuracy, performance, and usability of the fuzzy search.
*   Introduce features for visualizing, understanding, and reporting on directory structures.
*   Provide valuable metrics and analytics about the scanned filesystem.
*   **NEW:** Enable the tool to analyze existing file structures, identify areas for improvement, and suggest more optimized, standardized alternative structures and naming conventions.
*   Optimize the tool for speed and resource efficiency.
*   Enhance overall user experience and configurability.

## 2. Target User / Audience

*   Developers, system administrators, data analysts, and any power users who frequently work with large or complex directory structures via the command line.
*   Users who need to quickly locate files based on partial or misspelled names.
*   Users who want to understand the composition and organization of their directories.
*   **NEW:** Users looking to reorganize their filesystems into more efficient and standardized structures, potentially automating this process in the future.

## 3. Proposed Features

### 3.1. Fuzzy Search Enhancements

*   **FS1: Advanced Scoring Algorithm:**
    *   Implement a more sophisticated scoring mechanism beyond simple `difflib.SequenceMatcher` on basenames.
    *   Considerations:
        *   Weighting for matches in filename vs. directory path.
        *   Bonus for contiguous matches.
        *   Penalty for gaps or transpositions.
        *   Normalization for path length.
        *   Option to use different algorithms (e.g., Levenshtein distance, Jaro-Winkler) if beneficial and stdlib-compatible or simple to implement.
*   **FS2: Performance Optimization:**
    *   Profile existing `difflib` usage and identify bottlenecks for large path lists.
    *   Explore pre-filtering or indexing strategies for very large datasets if feasible without heavy dependencies (e.g., simplified n-gram indexing for initial candidate selection).
*   **FS3: Configurable Search Parameters (CLI):**
    *   Allow users to set the similarity `cutoff` score via a CLI argument.
    *   Allow users to set the `limit` for the number of results via a CLI argument.
*   **FS4: Interactive Mode (Post-Search Filtering):**
    *   After an initial search, allow users to interactively refine results (e.g., filter by extension, or provide another sub-query on the current results).
*   **FS5: Contextual Snippets in Search:**
    *   For text-based files, optionally show a small snippet of the line where the query (if also a content query) matches. (This might be a v2 feature, depends on complexity).

### 3.2. Hierarchical Data Exploration & Visualization

*   **HD1: Text-Based Directory Tree View:**
    *   Implement a function to display the scanned directory structure as a text-based tree (similar to `tree` command).
    *   Allow users to specify the `max_depth` of the tree display.
    *   Option to include/exclude files in the tree view (default to show directories, option to show files).
    *   Indicate symlinks, and potentially their targets, in the tree.
*   **HD2: Metrics in Tree View:**
    *   Optionally, display metadata alongside entries in the tree view:
        *   For directories: number of files, total size.
        *   For files: size.
*   **HD3: "Navigate to" Functionality:**
    *   After a search or tree view, allow users to select a file/directory and output a command to `cd` to its directory or open the file (OS-dependent, provide guidance).

### 3.3. Directory Analysis & Metrics

*   **DA1: Comprehensive File Statistics:**
    *   Total number of files and directories scanned.
    *   Total size of all files.
    *   Distribution of file types (count and total size per extension), sortable.
*   **DA2: Top N Listings:**
    *   Top N largest files.
    *   Top N largest directories (based on contained file sizes).
*   **DA3: File Age Analysis:**
    *   Top N oldest files (by modification date).
    *   Top N most recently modified files.
*   **DA4: Folder Depth Analysis:**
    *   Distribution of folder depths (e.g., number of folders at depth 1, 2, 3...).
    *   Identify and list paths exceeding a certain depth threshold.
*   **DA5: Empty Directory Identification:**
    *   List all empty directories found during the scan.
*   **DA6: Duplicate File Detection (Optional & Advanced):**
    *   Implement an optional feature to detect duplicate files.
    *   Strategy:
        1.  Group files by size.
        2.  For files with identical sizes, compute and compare hashes (e.g., SHA256).
    *   Clearly indicate this is a potentially slow operation.

### 3.4. "Closeness" and Relationship Analysis

*   **CR1: Group by Directory in Search Results:**
    *   Option to group fuzzy search results by their parent directory to show locality.
*   **CR2: Suggest Structurally Similar Paths:**
    *   If a search yields a result like `/A/B/C/target_file.txt`, and `/X/Y/Z/target_file.txt` also exists, highlight such structural similarities or allow searching for files with similar names across different base paths. This is related to identifying patterns in hierarchical data.

### 3.5. Output & Reporting

*   **OR1: Enhanced Console Output:**
    *   Use formatted tables for displaying metrics and search results.
    *   Consider using colors for different types of information (e.g., file vs. directory, scores) if terminal supports it (e.g., using ANSI escape codes). This should be optional / auto-detected.
*   **OR2: Save Analysis Report:**
    *   Option to save the full analysis (metrics, tree structure, search results if applicable) to a file.
    *   Supported formats: JSON (structured), TXT (human-readable summary).
    *   Timestamped report filenames by default.

### 3.6. Filesystem Structure Analysis & Reorganization Suggestions

*   **SR1: Structure Audit & Problem Identification:**
    *   Analyze for common organizational anti-patterns:
        *   Overly deep nesting (configurable threshold).
        *   Overly flat directories (too many files/subdirs, configurable threshold).
        *   Inconsistent naming conventions (detect mixed case, spaces, special chars).
        *   Redundant or non-descriptive directory/file names (e.g., "New Folder", "Untitled", copies like `file (1).txt`).
        *   Fragmented project files (heuristics to identify related files scattered apart).
*   **SR2: Suggest Alternative Directory Structures:**
    *   Propose concrete alternative structures based on identified problems and configurable strategies. Examples:
        *   Date-based grouping (e.g., `YYYY/MM/` or `YYYY-MM-DD/`).
        *   Type-based grouping (e.g., `documents/`, `images/`, `source_code/`, `archives/`).
        *   Flattening shallow, sparse trees or creating intermediate directories for overly flat structures.
        *   Project-based grouping (suggest based on common parent folder names, file type clusters, or user-defined project markers).
    *   Suggestions should aim for a balance between computer-optimized (e.g., for faster traversal by scripts) and human-readable.
*   **SR3: Standardized File Naming Conventions:**
    *   Analyze existing filenames for inconsistencies.
    *   Suggest standardized naming rules based on user preference or detected patterns:
        *   Case convention (e.g., `snake_case`, `kebab-case`, `camelCase`, `lowercase`).
        *   Space handling (e.g., replace with `_` or `-`, or remove).
        *   Special character removal/replacement.
        *   Consistent date formatting in filenames (e.g., `YYYY-MM-DD_filename.ext`).
        *   Suggest adding/normalizing prefixes/suffixes based on type or inferred project.
*   **SR4: Reorganization Impact Preview & Reporting:**
    *   For each set of suggestions, provide a preview of potential changes (e.g., list of `mv /old/path /new/path` operations).
    *   Estimate metrics for the proposed new structure (e.g., change in average depth, number of name changes).
    *   Generate a dedicated report (TXT, structured JSON/YAML) detailing all identified issues and proposed structural/naming changes. This report should be designed to be potentially consumable by an external reorganization script.
*   **SR5: User Configuration for Reorganization Strategies:**
    *   Allow users to configure preferred organizational strategies (e.g., "target: /Photos -> date-based YYYY/MM", "global_naming: snake_case") via CLI or config file.
    *   Allow users to set thresholds for "overly deep," "overly flat," etc.

### 3.7. Usability & Configuration

*   **UC1: Improved CLI Arguments:**
    *   Comprehensive set of CLI flags to control features (e.g., `--enable-metrics`, `--tree-depth N`, `--report-format json`, `--show-duplicates`, `--analyze-structure`, `--suggest-naming`).
    *   Clear help messages for all arguments.
*   **UC2: Configuration File:**
    *   Support for a configuration file (e.g., `~/.maximized_py_config.json` or in project dir) to set default values for exclusion lists, report formats, common search parameters, etc.
*   **UC3: Path Collection Caching:**
    *   Implement a caching mechanism for the collected file paths.
    *   If a directory is scanned, store the path list (and perhaps basic metadata like mtime/size for cache invalidation).
    *   On subsequent runs for the same path, if the cache is deemed valid (e.g., root directory mtime hasn't changed significantly, or via a force refresh flag), load paths from cache to speed up startup.
    *   Cache should be stored in a user-cache directory.
*   **UC4: Progress Indication:**
    *   For long-running operations (initial scan of large directory, duplicate detection, structural analysis), provide a simple progress indicator (e.g., number of directories scanned, spinner).

## 4. Technical Considerations / Optimizations

*   **TC1: Efficient Filesystem Traversal:**
    *   While `os.walk` is robust, ensure `entry.stat()` from `os.scandir` is used if profiling shows significant benefits for metadata collection, especially if `maximized.py` moves towards more intensive per-file metadata analysis. For basic path collection, `os.walk` with minimal processing is often fine. The current `collect_file_paths` is good.
*   **TC2: Memory Management:**
    *   Be mindful of memory usage when storing lists of all file paths and their metadata, especially for very large filesystems. Consider iterative processing or generators where appropriate if full in-memory lists become problematic (though for fuzzy search, having the list in memory is often required).
*   **TC3: Modular Design:**
    *   Structure the code cambios into logical modules/functions (e.g., path collection, fuzzy matching, tree generation, metrics calculation, reporting) for better maintainability and testability.
*   **TC4: Cross-Platform Compatibility:**
    *   Ensure all path manipulations and system calls are cross-platform compatible (Windows, macOS, Linux). `os.path` and `pathlib` help here.
*   **NEW TC5: Complexity of Heuristics:** Recognizing that inferring user intent for optimal structure or project groupings can be complex. Start with clear, configurable rules and well-defined heuristics. The suggestions should be presented as *options* to the user.

## 5. Success Metrics

*   **SM1: Performance:**
    *   Time taken to scan a benchmark directory and collect paths.
    *   Time taken to perform a fuzzy search on a benchmark set of paths.
*   **SM2: Search Relevance:**
    *   User satisfaction with the ranking and accuracy of fuzzy search results.
*   **SM3: Feature Adoption:**
    *   Usage frequency of the new analytical features (tree view, metrics, structural analysis).
*   **SM4: Usability:**
    *   Ease of use of CLI options and understandability of output.
*   **NEW SM5: Actionability of Suggestions:** How often users find the structural and naming suggestions relevant and useful (potentially leading to manual or scripted reorganization).

## 6. Future Considerations (Out of Scope for this Iteration)

*   **FC1: Graphical User Interface (GUI):** A simple TUI (Text User Interface) or a web-based GUI.
*   **FC2: Plugin System:** Allow users to add custom analysis modules or reporters.
*   **FC3: Advanced Natural Language Queries:** "find text files modified last week related to 'project X'".
*   **FC4: Indexing Service:** For extremely large or frequently searched directories, an optional background indexing service.
*   **FC5: Content-based Fuzzy Search:** Extending fuzzy search to file contents, not just paths/names.
*   **NEW FC6: Direct Reorganization Engine:** An integrated (but separate and clearly delineated) module within `maximized.py` or a companion script to *apply* the suggested structural changes. This is a major undertaking beyond the analysis/suggestion scope of the current PRD.

---
This PRD outlines a significant expansion of `maximized.py`. It is recommended to implement these features iteratively. 