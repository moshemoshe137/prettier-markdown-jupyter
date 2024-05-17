# https://chat.openai.com/share/8ed67729-3531-4da2-b6f3-8fcd0c1ec250
"""Format the markdown cells in a Jupyter notebook with `prettier`."""

import argparse
from pathlib import Path
import subprocess

import nbformat


def format_markdown_cells(notebook_path: str | Path) -> bool:
    """Format the markdown cells in a Jupyter notebook with `prettier`."""
    modified = False  # Flag to keep track of modification
    notebook_path = Path(notebook_path)

    with notebook_path.open("r", encoding="utf8") as f:
        notebook = nbformat.read(f, as_version=4)

    temp_md_path = notebook_path.with_suffix(".temp.md")
    with open(temp_md_path, "w", encoding="utf-8") as temp_md_file:
        markdown_cells = [
            cell.source for cell in notebook.cells if cell.cell_type == "markdown"
        ]
        temp_md_file.write("\n\n<!--cell-->\n\n".join(markdown_cells))

    # Read the original file content for comparison later
    original_content = temp_md_path.read_text(encoding="utf8")
    # with open("original.txt", "w", encoding="utf8") as f:
    #     f.write(original_content)

    # Run pre-commit prettier
    subprocess.run(
        f"pre-commit run prettier --files {temp_md_path}".split(" "),
        capture_output=True,
    )

    # Read the potentially modified content
    formatted_content = temp_md_path.read_text(encoding="utf8").rstrip()

    # with open("formatted.txt", "w", encoding="utf8") as f:
    #     f.write(formatted_content)

    # Check if the content was modified
    if original_content != formatted_content:
        modified = True

        # Split the formatted content back into cells
        formatted_cells = formatted_content.split("<!--cell-->\n\n")

        # Replace the source of each markdown cell with formatted content
        assert len(formatted_cells) == sum(
            1 for cell in notebook.cells if cell.cell_type == "markdown"
        )
        cell_index = 0
        for cell in notebook.cells:
            if cell.cell_type == "markdown":
                cell.source = formatted_cells[cell_index].strip()
                cell_index += 1

        # Save the notebook
        with notebook_path.open("w", encoding="utf-8") as f:
            nbformat.write(notebook, f)

    # Remove the temporary file using pathlib
    temp_md_path.unlink(missing_ok=True)

    return modified


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Format Markdown cells in a Jupyter Notebook using prettier."
    )
    parser.add_argument(
        "notebook_paths",
        nargs="+",
        type=str,
        help="Paths to the Jupyter Notebook files.",
    )

    args = parser.parse_args()

    exit_code = 0
    for notebook_path in args.notebook_paths:
        modified = format_markdown_cells(notebook_path)
        if modified:
            exit_code = 1
    exit(exit_code)