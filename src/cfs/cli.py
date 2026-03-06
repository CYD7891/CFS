from __future__ import annotations

from pathlib import Path
import csv
import math
import typer
from rich import print

from cfs.io.parse_cases import read_cases_csv
from cfs.report.render_html import render_report_html
from cfs.report.render_pdf import render_pdf_from_html
from cfs.models.isentropic import (
    temperature_ratio,
    pressure_ratio,
    density_ratio,
    area_ratio,
)
from cfs.models.normal_shock import (
    downstream_mach,
    static_pressure_ratio,
    static_density_ratio,
    static_temperature_ratio,
    total_pressure_ratio,
)
from cfs.models.oblique_shock import (
    shock_angle,
    normal_mach_upstream,
    normal_mach_downstream,
    downstream_mach_oblique,
    static_pressure_ratio_oblique,
    static_density_ratio_oblique,
    static_temperature_ratio_oblique,
    total_pressure_ratio_oblique,
)

app = typer.Typer(add_completion=False, no_args_is_help=True)


@app.callback()
def main():
    """
    Compressible Flow Studio CLI.
    """
    pass


def compute_result_row(r: dict[str, str]) -> dict[str, str]:
    model = r.get("model", "")
    case_id = r.get("case_id", "")

    result = {
        "case_id": case_id,
        "model": model,
        "status": "OK",
        "note": "",
        "branch": r.get("branch", ""),
        # isentropic outputs
        "T_T0": "",
        "P_P0": "",
        "rho_rho0": "",
        "A_Astar": "",
        # shared shock outputs
        "M2": "",
        "p2_p1": "",
        "rho2_rho1": "",
        "T2_T1": "",
        "p02_p01": "",
        # oblique-specific outputs
        "beta_deg": "",
        "Mn1": "",
        "Mn2": "",
    }

    try:
        if model == "isentropic":
            gamma = float(r["gamma"])
            M = float(r["M"])

            result["T_T0"] = f"{temperature_ratio(M, gamma):.12f}"
            result["P_P0"] = f"{pressure_ratio(M, gamma):.12f}"
            result["rho_rho0"] = f"{density_ratio(M, gamma):.12f}"
            result["A_Astar"] = f"{area_ratio(M, gamma):.12f}"
            result["note"] = "Real isentropic calculation"

        elif model == "normal_shock":
            gamma = float(r["gamma"])
            M1 = float(r["M1"])

            result["M2"] = f"{downstream_mach(M1, gamma):.12f}"
            result["p2_p1"] = f"{static_pressure_ratio(M1, gamma):.12f}"
            result["rho2_rho1"] = f"{static_density_ratio(M1, gamma):.12f}"
            result["T2_T1"] = f"{static_temperature_ratio(M1, gamma):.12f}"
            result["p02_p01"] = f"{total_pressure_ratio(M1, gamma):.12f}"
            result["note"] = "Real normal shock calculation"

        elif model == "oblique_shock":
            gamma = float(r["gamma"])
            M1 = float(r["M1"])
            theta_deg = float(r["theta_deg"])
            branch = r["branch"]
            theta_rad = math.radians(theta_deg)

            beta = shock_angle(M1, theta_rad, gamma, branch=branch)
            Mn1 = normal_mach_upstream(M1, beta)
            Mn2 = normal_mach_downstream(M1, beta, gamma)
            M2 = downstream_mach_oblique(M1, theta_rad, gamma, branch=branch)

            result["beta_deg"] = f"{math.degrees(beta):.12f}"
            result["Mn1"] = f"{Mn1:.12f}"
            result["Mn2"] = f"{Mn2:.12f}"
            result["M2"] = f"{M2:.12f}"
            result["p2_p1"] = f"{static_pressure_ratio_oblique(M1, theta_rad, gamma, branch=branch):.12f}"
            result["rho2_rho1"] = f"{static_density_ratio_oblique(M1, theta_rad, gamma, branch=branch):.12f}"
            result["T2_T1"] = f"{static_temperature_ratio_oblique(M1, theta_rad, gamma, branch=branch):.12f}"
            result["p02_p01"] = f"{total_pressure_ratio_oblique(M1, theta_rad, gamma, branch=branch):.12f}"
            result["note"] = "Real oblique shock calculation"

        else:
            result["status"] = "ERROR"
            result["note"] = f"Unknown model: {model}"

    except KeyError as exc:
        result["status"] = "ERROR"
        result["note"] = f"Missing required field: {exc.args[0]}"

    except ValueError as exc:
        result["status"] = "ERROR"
        result["note"] = f"Invalid numeric input: {exc}"

    except Exception as exc:
        result["status"] = "ERROR"
        result["note"] = str(exc)

    return result


def write_results_csv(results_path: Path, results_rows: list[dict[str, str]]) -> None:
    result_fieldnames = [
        "case_id",
        "model",
        "status",
        "note",
        "branch",
        "T_T0",
        "P_P0",
        "rho_rho0",
        "A_Astar",
        "M2",
        "p2_p1",
        "rho2_rho1",
        "T2_T1",
        "p02_p01",
        "beta_deg",
        "Mn1",
        "Mn2",
    ]

    with results_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=result_fieldnames)
        w.writeheader()
        w.writerows(results_rows)


def generate_outputs(
    *,
    input_rows: list[dict[str, str]],
    out: Path,
    title: str,
    pdf: bool,
    inputs_filename_for_report: str,
) -> None:
    out.mkdir(parents=True, exist_ok=True)

    results_path = out / "results.csv"
    report_path = out / "report.html"

    results_rows = [compute_result_row(r) for r in input_rows]
    write_results_csv(results_path, results_rows)

    html = render_report_html(
        title=title,
        inputs_csv=inputs_filename_for_report,
        results_csv=str(results_path.name),
        assumptions=[
            "Ideal gas, calorically perfect (constant gamma)",
            "Steady, inviscid, adiabatic",
            "Isentropic/normal shock: 1D relations; oblique shock: 2D attached shock model",
        ],
        failure_modes=[
            "No real-gas / variable-gamma / chemistry / high-temperature effects",
            "Normal shock requires upstream Mach number M1 > 1",
            "Oblique shock: if theta > theta_max(M1,gamma), no attached solution",
            "Near M≈1 can be ill-conditioned; numerical safeguards needed",
        ],
        input_rows=input_rows,
        result_rows=results_rows,
        output_dir=out,
    )
    report_path.write_text(html, encoding="utf-8")

    if pdf:
        pdf_path = out / "report.pdf"
        ok, message = render_pdf_from_html(report_path, pdf_path)
        if ok:
            print(f"[bold green]{message}[/bold green]")
        else:
            print(f"[bold yellow]{message}[/bold yellow]")

    print(f"[bold green]Run completed[/bold green]: {out}")
    print(f"- {results_path}")
    print(f"- {report_path}")


@app.command()
def demo(
    out: Path = typer.Option(Path("build/demo"), "--out", help="Output directory"),
    pdf: bool = typer.Option(False, "--pdf", help="Attempt to generate a PDF report"),
):
    """
    Generate demo inputs and run them.
    """
    out.mkdir(parents=True, exist_ok=True)

    demo_rows = [
        {"case_id": "iso_1", "model": "isentropic", "gamma": "1.4", "M": "2.0"},
        {"case_id": "ns_1", "model": "normal_shock", "gamma": "1.4", "M1": "2.0"},
        {
            "case_id": "os_1",
            "model": "oblique_shock",
            "gamma": "1.4",
            "M1": "3.0",
            "theta_deg": "15",
            "branch": "weak",
        },
    ]

    inputs_path = out / "inputs_demo.csv"
    fieldnames = sorted({k for r in demo_rows for k in r.keys()})
    with inputs_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(demo_rows)

    generate_outputs(
        input_rows=demo_rows,
        out=out,
        title="Compressible Flow Studio — Demo Report",
        pdf=pdf,
        inputs_filename_for_report=str(inputs_path.name),
    )


@app.command()
def run(
    input_csv: Path = typer.Argument(..., help="Input CSV containing batch cases"),
    out: Path = typer.Option(Path("build/run"), "--out", help="Output directory"),
    pdf: bool = typer.Option(False, "--pdf", help="Attempt to generate a PDF report"),
):
    """
    Run a batch of compressible-flow cases from a CSV file.
    """
    input_rows = read_cases_csv(input_csv)

    generate_outputs(
        input_rows=input_rows,
        out=out,
        title="Compressible Flow Studio — Batch Run Report",
        pdf=pdf,
        inputs_filename_for_report=str(input_csv.name),
    )