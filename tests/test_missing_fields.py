from __future__ import annotations

from cfs.cli import compute_result_row


def test_missing_required_field_marks_error():
    row = {
        "case_id": "missing_m1",
        "model": "normal_shock",
        "gamma": "1.4",
        # intentionally missing M1
    }

    result = compute_result_row(row)

    assert result["status"] == "ERROR"
    assert "Missing required field" in result["note"]