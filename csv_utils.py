import csv
import os
from agents import function_tool
from model import CSV_HEADERS, RepoFeatureRow


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
def append_rows_tool(file_path: str, rows: list[list[str]]) -> None:
    return append_rows(file_path, rows)


def append_rows(file_path: str, rows: list, headers: list[str] = None) -> None:
    """
    Append multiple rows to an existing CSV file.
    Each row can be:
      - a list of values (old behavior)
      - a RepoFeatureRow object or dict (new behavior)
    If headers are provided, align dict/model fields to header order.
    Ensures each row is written on its own line.
    """
    from model import RepoFeatureRow
    # Ensure the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    with open(file_path, "a", newline="") as csvfile:
        writer = csv.writer(csvfile, lineterminator="\n")
        for row in rows:
            # If row is a RepoFeatureRow or dict, convert to list in headers order if provided
            if hasattr(row, 'dict'):
                row_dict = row.dict()
            elif isinstance(row, dict):
                row_dict = row
            else:
                writer.writerow(row)
                continue
            if headers:
                row_out = [row_dict.get(self_key_from_header(header), '') for header in headers]
            else:
                row_out = list(row_dict.values())
            writer.writerow(row_out)

def self_key_from_header(header):
    # Map header to model key (simple normalization, can be extended)
    return header.lower().replace(' ', '_').replace('(s)', 's').replace('(', '').replace(')', '')
