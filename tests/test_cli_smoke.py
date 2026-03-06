from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path


def test_demo_command_creates_artifacts(tmp_path: Path):
    out = tmp_path / "demo"
    cmd = [sys.executable, "-m", "cfs", "demo", "--out", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    inputs_file = out / "inputs_demo.csv"
    results_file = out / "results.csv"
    report_file = out / "report.html"

    assert inputs_file.exists()
    assert results_file.exists()
    assert report_file.exists()

    with results_file.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    iso_row = next(row for row in rows if row["case_id"] == "iso_1")
    ns_row = next(row for row in rows if row["case_id"] == "ns_1")
    os_row = next(row for row in rows if row["case_id"] == "os_1")

    assert iso_row["model"] == "isentropic"
    assert iso_row["status"] == "OK"
    assert iso_row["note"] == "Real isentropic calculation"
    assert abs(float(iso_row["T_T0"]) - 0.5555555555555556) < 1e-10
    assert abs(float(iso_row["P_P0"]) - 0.12780452546295096) < 1e-10
    assert abs(float(iso_row["rho_rho0"]) - 0.23004814583331168) < 1e-10
    assert abs(float(iso_row["A_Astar"]) - 1.6875) < 1e-10

    assert ns_row["model"] == "normal_shock"
    assert ns_row["status"] == "OK"
    assert ns_row["note"] == "Real normal shock calculation"
    assert abs(float(ns_row["M2"]) - 0.5773502691896257) < 1e-10
    assert abs(float(ns_row["p2_p1"]) - 4.5) < 1e-10
    assert abs(float(ns_row["rho2_rho1"]) - 2.666666666666667) < 1e-10
    assert abs(float(ns_row["T2_T1"]) - 1.6875) < 1e-10
    assert abs(float(ns_row["p02_p01"]) - 0.7208738614847454) < 1e-10

    assert os_row["model"] == "oblique_shock"
    assert os_row["status"] == "OK"
    assert os_row["branch"] == "weak"
    assert os_row["note"] == "Real oblique shock calculation"
    assert abs(float(os_row["beta_deg"]) - 32.24040018274467) < 1e-9
    assert abs(float(os_row["Mn1"]) - 1.600418424201603) < 1e-9
    assert abs(float(os_row["Mn2"]) - 0.668311462098548) < 1e-9
    assert abs(float(os_row["M2"]) - 2.254902312264938) < 1e-9
    assert abs(float(os_row["p2_p1"]) - 2.821562321277495) < 1e-9
    assert abs(float(os_row["rho2_rho1"]) - 2.0324488190583185) < 1e-9
    assert abs(
    float(os_row["T2_T1"]) - float(os_row["p2_p1"]) / float(os_row["rho2_rho1"])
) < 1e-9
    assert abs(float(os_row["p02_p01"]) - 0.895044329829952) < 1e-9