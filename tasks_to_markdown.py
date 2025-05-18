#!/usr/bin/env python3

import json
import os
import argparse
from datetime import datetime


def read_tasks_json(file_path):
    """Read the tasks.json file and return the parsed JSON data."""
    with open(file_path, "r") as f:
        return json.load(f)


def format_dependencies(dependencies, tasks_dict):
    """Format the dependencies list with status indicators."""
    if not dependencies:
        return "None"

    formatted_deps = []
    for dep_id in dependencies:
        # Handle subtask dependencies (e.g., "1.2")
        if isinstance(dep_id, str) and "." in dep_id:
            parent_id, sub_id = dep_id.split(".")
            parent_id, sub_id = int(parent_id), int(sub_id)

            # Find the parent task and then the subtask
            parent_task = tasks_dict.get(parent_id)
            if parent_task and "subtasks" in parent_task:
                for subtask in parent_task["subtasks"]:
                    if subtask["id"] == sub_id:
                        status = subtask.get("status", "pending")
                        status_icon = "✅" if status == "done" else "⏱️"
                        formatted_deps.append(f"{status_icon} {dep_id}")
                        break
        else:
            # Handle main task dependencies
            dep_id = int(dep_id) if isinstance(dep_id, str) else dep_id
            dep_task = tasks_dict.get(dep_id)
            if dep_task:
                status = dep_task.get("status", "pending")
                status_icon = "✅" if status == "done" else "⏱️"
                formatted_deps.append(f"{status_icon} {dep_id}")

    return ", ".join(formatted_deps)


def create_tasks_dict(tasks):
    """Create a dictionary of tasks indexed by their ID for easy lookup."""
    return {task["id"]: task for task in tasks}


def format_task_as_markdown(task, level=0, tasks_dict=None, parent_id=None):
    """Format a single task as Markdown with appropriate indentation."""
    task_id = task["id"]

    # For subtasks, prepend the parent ID
    display_id = f"{parent_id}.{task_id}" if parent_id else str(task_id)

    # Create checkbox based on status
    checkbox = "[x]" if task["status"] == "done" else "[ ]"

    # Indentation based on level
    indent = "  " * level

    # Format the task title with checkbox
    md = f"{indent}- {checkbox} **Task {display_id}:** {task['title']}\n"

    # Add task description as a simple indented line
    if "description" in task:
        md += f"{indent}  - Description: {task['description']}\n"

    # Add minimal information (status and priority)
    md += f"{indent}  - Status: {task['status']}\n"

    if "priority" in task:
        md += f"{indent}  - Priority: {task['priority']}\n"

    # Add dependencies with status indicators
    if "dependencies" in task and tasks_dict:
        deps = format_dependencies(task["dependencies"], tasks_dict)
        md += f"{indent}  - Dependencies: {deps}\n"

    # Add details section if it exists (as simple indented text)
    if "details" in task and task["details"]:
        # Indent and format the details as plain text
        md += f"{indent}  - Details:\n"
        # Split by lines and add appropriate indentation
        details_lines = task["details"].split("\n")
        for line in details_lines:
            md += f"{indent}    {line}\n"

    # Add test strategy if it exists (as simple indented text)
    if "testStrategy" in task and task["testStrategy"]:
        md += f"{indent}  - Test Strategy:\n"
        test_lines = task["testStrategy"].split("\n")
        for line in test_lines:
            md += f"{indent}    {line}\n"

    # Add subtasks if they exist
    if "subtasks" in task and task["subtasks"]:
        md += f"{indent}  - Subtasks:\n"
        for subtask in task["subtasks"]:
            md += format_task_as_markdown(
                subtask, level + 2, tasks_dict, parent_id=task_id
            )

    return md


def count_subtasks(tasks):
    """Count total and completed subtasks across all main tasks."""
    total_subtasks = 0
    completed_subtasks = 0

    for task in tasks:
        if "subtasks" in task and task["subtasks"]:
            for subtask in task["subtasks"]:
                total_subtasks += 1
                if subtask.get("status") == "done":
                    completed_subtasks += 1

    return total_subtasks, completed_subtasks


def generate_markdown(data, output_file):
    """Generate a Markdown file from the tasks data."""
    tasks = data["tasks"]
    metadata = data.get("metadata", {})
    tasks_dict = create_tasks_dict(tasks)

    # Start with a header
    md = f"# {metadata.get('projectName', 'Project')} Tasks\n\n"

    # Add generation information
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    md += f"*Generated on: {current_time}*\n\n"

    if "generatedAt" in metadata:
        md += f"*Original tasks created: {metadata['generatedAt']}*\n\n"

    # Add project statistics
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task["status"] == "done")
    total_subtasks, completed_subtasks = count_subtasks(tasks)

    # Project progress section with both main task and subtask statistics
    md += f"**Project Progress:** {completed_tasks}/{total_tasks} main tasks completed ({completed_subtasks}/{total_subtasks} subtasks completed)\n\n"

    # Add a note about updating the Markdown
    md += "> Note: This Markdown file is generated from the tasks.json file. To mark tasks as complete, \n"
    md += "> edit the checkboxes in this file and run the conversion script with the `--update` flag to update tasks.json.\n\n"

    # Format each main task
    md += "## Tasks\n\n"
    for task in tasks:
        md += format_task_as_markdown(task, tasks_dict=tasks_dict)
        md += "\n"

    # Create the output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # Write to the output file
    with open(output_file, "w") as f:
        f.write(md)

    print(f"Markdown successfully written to {output_file}")


def update_tasks_json_from_markdown(markdown_file, tasks_json_file):
    """Update the tasks.json file based on the checkboxes in the Markdown file."""
    # Read the Markdown file
    with open(markdown_file, "r") as f:
        md_content = f.read()

    # Read the current tasks.json
    with open(tasks_json_file, "r") as f:
        tasks_data = json.load(f)

    # Parse each line that has a checkbox
    changes_made = False
    lines = md_content.split("\n")

    for line in lines:
        if "- [x]" in line or "- [ ]" in line:
            # Extract task ID
            task_match = (
                line.strip().split("**Task ")[1].split(":")[0].strip()
                if "**Task " in line
                else None
            )

            if task_match:
                is_checked = "[x]" in line

                # Handle main tasks vs subtasks
                if "." in task_match:
                    # This is a subtask
                    parent_id, subtask_id = map(int, task_match.split("."))

                    # Find the parent task
                    for task in tasks_data["tasks"]:
                        if task["id"] == parent_id and "subtasks" in task:
                            # Find the specific subtask
                            for subtask in task["subtasks"]:
                                if subtask["id"] == subtask_id:
                                    current_status = subtask.get("status", "pending")
                                    new_status = "done" if is_checked else "pending"

                                    if current_status != new_status:
                                        subtask["status"] = new_status
                                        changes_made = True
                                    break
                else:
                    # This is a main task
                    try:
                        task_id = int(task_match)

                        # Find the task
                        for task in tasks_data["tasks"]:
                            if task["id"] == task_id:
                                current_status = task.get("status", "pending")
                                new_status = "done" if is_checked else "pending"

                                if current_status != new_status:
                                    task["status"] = new_status
                                    changes_made = True
                                break
                    except ValueError:
                        # Not a valid task ID
                        continue

    # Write the updated tasks.json if changes were made
    if changes_made:
        with open(tasks_json_file, "w") as f:
            json.dump(tasks_data, f, indent=2)
        print(f"Updated {tasks_json_file} based on checkboxes in {markdown_file}")
    else:
        print("No changes detected in checkbox statuses")


def main():
    parser = argparse.ArgumentParser(
        description="Convert TaskMaster tasks.json to Markdown format"
    )
    parser.add_argument(
        "--input", "-i", default="tasks/tasks.json", help="Path to the tasks.json file"
    )
    parser.add_argument(
        "--output",
        "-o",
        default="docs/tasks.md",
        help="Path for the output Markdown file",
    )
    parser.add_argument(
        "--update",
        "-u",
        action="store_true",
        help="Update tasks.json based on checkbox status in Markdown",
    )

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file {args.input} does not exist")
        return

    if args.update and os.path.exists(args.output):
        # Update tasks.json based on Markdown checkboxes
        update_tasks_json_from_markdown(args.output, args.input)
    else:
        # Generate Markdown from tasks.json
        data = read_tasks_json(args.input)
        generate_markdown(data, args.output)


if __name__ == "__main__":
    main()
