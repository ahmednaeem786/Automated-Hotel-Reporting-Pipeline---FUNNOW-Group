import csv
import os
from pathlib import Path

import pandas as pd

REQUIRED_DATASET_COLUMNS = {"brandname", "revenue", "Order"}
IGNORED_DIRECTORIES = {".git", ".venv", "venv", "__pycache__", "node_modules"}


def find_dataset_file(search_root=None):
    """
    Find the hotel dataset without relying on a fixed directory or filename.

    HOTEL_DATA_FILE can be set when the dataset is outside the project or when
    more than one CSV has the expected columns.
    """
    configured_path = os.getenv("HOTEL_DATA_FILE")
    if configured_path:
        dataset_path = Path(configured_path).expanduser()
        if not dataset_path.is_file():
            raise FileNotFoundError(
                f"HOTEL_DATA_FILE does not point to a file: {dataset_path}"
            )
        return dataset_path

    root = Path(search_root or Path(__file__).resolve().parent).resolve()
    if not root.is_dir():
        raise NotADirectoryError(f"Dataset search root does not exist: {root}")

    matching_files = []
    for csv_path in root.rglob("*"):
        if not csv_path.is_file() or csv_path.suffix.lower() != ".csv":
            continue
        if any(part in IGNORED_DIRECTORIES for part in csv_path.parts):
            continue

        try:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as dataset:
                headers = {header.strip() for header in next(csv.reader(dataset), [])}
        except (OSError, UnicodeDecodeError, StopIteration):
            continue

        if REQUIRED_DATASET_COLUMNS.issubset(headers):
            matching_files.append(csv_path)

    if not matching_files:
        expected_columns = ", ".join(sorted(REQUIRED_DATASET_COLUMNS))
        raise FileNotFoundError(
            f"No CSV dataset containing these columns was found under {root}: "
            f"{expected_columns}"
        )

    if len(matching_files) > 1:
        matches = "\n".join(f"  - {path}" for path in matching_files)
        raise RuntimeError(
            "Multiple matching hotel datasets were found. Set HOTEL_DATA_FILE "
            f"to choose one:\n{matches}"
        )

    return matching_files[0]


def process_hotel_data(file_path=None, test_email="ahmednaeembhuri456@gmail.com"):
    """
    Reads hotel data, calculates performance thresholds,
    and tags each hotel's performance status.

    ``test_email`` is used as the recipient for all generated reports.
    """
    dataset_path = Path(file_path) if file_path else find_dataset_file()
    df = pd.read_csv(dataset_path)

    # Calculate thresholds (using median to avoid possible skew from massive outliers)
    median_revenue = df["revenue"].median()
    median_orders = df["Order"].median()

    # Function to determine status for each row
    def determine_status(row):
        if row["revenue"] >= median_revenue and row["Order"] >= median_orders:
            return "Performing Well"
        elif row["revenue"] < median_revenue and row["Order"] < median_orders:
            return "Needs Improvement"
        else:
            return "Mixed Results"

    # New column storing performance status based on thresholds
    df["performance_status"] = df.apply(determine_status, axis=1)

    # Using personal email for testing purposes; in production, this would be replaced with the actual boss's email
    df["Boss Gmail"] = test_email

    return df, median_revenue, median_orders


# Quick test block to ensure it works when run directly
if __name__ == "__main__":
    processed_df, revenue_threshold, order_thresh = process_hotel_data()

    print(f"Revenue Threshold (Median): ${revenue_threshold}")
    print(f"Order Threshold (Median): {order_thresh} bookings\n")
    print(processed_df[["brandname", "revenue", "Order", "performance_status"]])
