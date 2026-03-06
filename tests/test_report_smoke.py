from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_report_contains_real_sections_and_cases(tmp_path: Path):
    out = tmp_path / "demo"
    cmd = [sys.executable, "-m", "cfs", "demo", "--out", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    html = (out / "report.html").read_text(encoding="utf-8")

    assert "Project Summary" in html
    assert "Input Cases" in html
    assert "Computed Results" in html
    assert "Conclusions" in html

    assert "iso_1" in html
    assert "ns_1" in html
    assert "os_1" in html

    assert "Real isentropic calculation" in html
    assert "Real normal shock calculation" in html
    assert "Real oblique shock calculation" in html