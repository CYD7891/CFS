from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def test_demo_generates_plot_asset(tmp_path: Path):
    out = tmp_path / "demo"
    cmd = [sys.executable, "-m", "cfs", "demo", "--out", str(out)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    assert r.returncode == 0, r.stderr

    plot_file = out / "assets" / "isentropic_area_ratio.png"
    assert plot_file.exists()
    assert plot_file.stat().st_size > 0

    html = (out / "report.html").read_text(encoding="utf-8")
    assert "Isentropic Area Ratio Curve" in html
    assert "assets/isentropic_area_ratio.png" in html