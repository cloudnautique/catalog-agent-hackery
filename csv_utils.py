import csv
import os
from agents import function_tool


@function_tool
def initialize_csv_tool(file_path: str, headers: list[str]) -> None:
    return initialize_csv(file_path, headers)


def initialize_csv(file_path: str, headers: list[str]) -> None:
    """
    Create or overwrite a CSV file at file_path with the provided headers.
    Assumes file_path is relative to the current working directory.
    """
    # Convert to absolute path relative to current directory
    abs_path = os.path.abspath(os.path.join(".", file_path))
    # Ensure the directory exists
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    with open(abs_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)


@function_tool
def append_rows(file_path: str, rows: list[list[str]]) -> None:
    """
    Append multiple rows to an existing CSV file.
    Each row should be an iterable of values.
    Ensures each row is written on its own line.
    """
    # Ensure the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile, lineterminator="\n")
        for row in rows:
            writer.writerow(row)
