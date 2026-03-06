from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def test_run_command_marks_bad_rows_as_error_but_continues(tmp_path: Path):
    input_csv = tmp_path / "bad_cases.csv"
    out = tmp_path / "run_out"

    input_csv.write_text(
        "case_id,model,gamma,M,M1,theta_deg,branch\n"
        "good_iso,isentropic,1.4,2.0,,,\n"
        "bad_ns,normal_shock,1.4,,0.8,,\n"
        "bad_os,oblique_shock,1.4,,2.0,40,weak\n"
        "bad_model,banana,1.4,2.0,,,\n",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "cfs", "run", str(input_csv), "--out", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    results_file = out / "results.csv"
    assert results_file.exists()

    with results_file.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 4

    rows_by_id = {row["case_id"]: row for row in rows}

    assert rows_by_id["good_iso"]["status"] == "OK"
    assert rows_by_id["good_iso"]["T_T0"] != ""

    assert rows_by_id["bad_ns"]["status"] == "ERROR"
    assert rows_by_id["bad_ns"]["note"] != ""

    assert rows_by_id["bad_os"]["status"] == "ERROR"
    assert rows_by_id["bad_os"]["note"] != ""

    assert rows_by_id["bad_model"]["status"] == "ERROR"
    assert "Unknown model" in rows_by_id["bad_model"]["note"]