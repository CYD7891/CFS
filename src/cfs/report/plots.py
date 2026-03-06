from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

from cfs.models.isentropic import area_ratio


def plot_isentropic_area_ratio(output_path: Path, gamma: float = 1.4) -> None:
    """
    Plot A/A* vs M for isentropic flow and save as PNG.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    mach_values = []
    area_values = []

    # Build a smooth curve from M=0.2 to M=5.0
    n = 500
    for i in range(n):
        M = 0.2 + (5.0 - 0.2) * i / (n - 1)
        mach_values.append(M)
        area_values.append(area_ratio(M, gamma))

    # Demo point: M=2, gamma=1.4
    demo_M = 2.0
    demo_AA = area_ratio(demo_M, gamma)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(mach_values, area_values, label="A/A* curve")
    ax.plot([demo_M], [demo_AA], marker="o", linestyle="None", label="demo point (M=2)")
    ax.set_xlabel("Mach number, M")
    ax.set_ylabel("Area ratio, A/A*")
    ax.set_title("Isentropic Area Ratio Curve")
    ax.grid(True)
    ax.legend()

    fig.tight_layout()
    fig.savefig(output_path, dpi=160)
    plt.close(fig)