from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def test_run_command_from_csv(tmp_path: Path):
    input_csv = tmp_path / "cases.csv"
    out = tmp_path / "run_out"

    input_csv.write_text(
        "case_id,model,gamma,M,M1,theta_deg,branch\n"
        "iso_1,isentropic,1.4,2.0,,,\n"
        "ns_1,normal_shock,1.4,,2.0,,\n"
        "os_1,oblique_shock,1.4,,3.0,15,weak\n",
        encoding="utf-8",
    )

    cmd = [sys.executable, "-m", "cfs", "run", str(input_csv), "--out", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    results_file = out / "results.csv"
    report_file = out / "report.html"

    assert results_file.exists()
    assert report_file.exists()

    with results_file.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 3
    assert any(row["case_id"] == "iso_1" for row in rows)
    assert any(row["case_id"] == "ns_1" for row in rows)
    assert any(row["case_id"] == "os_1" for row in rows)