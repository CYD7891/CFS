from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_demo_with_pdf_flag_does_not_crash(tmp_path: Path):
    out = tmp_path / "demo"
    cmd = [sys.executable, "-m", "cfs", "demo", "--out", str(out), "--pdf"]
    r = subprocess.run(cmd, capture_output=True, text=True)

    assert r.returncode == 0, r.stderr
    assert (out / "report.html").exists()

    pdf_file = out / "report.pdf"
    if pdf_file.exists():
        assert pdf_file.stat().st_size > 0