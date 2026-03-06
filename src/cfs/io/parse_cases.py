from __future__ import annotations

import csv
from pathlib import Path


def read_cases_csv(path: Path) -> list[dict[str, str]]:
    """
    Read batch input cases from a CSV file.

    Empty cells are preserved as empty strings.
    """
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return [dict(row) for row in reader]