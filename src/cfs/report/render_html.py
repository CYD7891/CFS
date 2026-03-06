from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from cfs.report.plots import plot_isentropic_area_ratio


@dataclass(frozen=True)
class ReportContext:
    title: str
    inputs_csv: str
    results_csv: str
    assumptions: list[str]
    failure_modes: list[str]
    input_columns: list[str]
    result_columns: list[str]
    input_rows: list[dict[str, Any]]
    result_rows: list[dict[str, Any]]
    conclusions: list[str]
    figure_paths: dict[str, str]
    error_rows: list[dict[str, Any]]
    ok_count: int
    error_count: int


def ordered_union_keys(rows: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    columns: list[str] = []

    for row in rows:
        for key in row.keys():
            if key not in seen:
                seen.add(key)
                columns.append(key)

    return columns


def normalize_rows(rows: list[dict[str, Any]], columns: list[str]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for row in rows:
        normalized.append({col: row.get(col, "") for col in columns})
    return normalized


def build_conclusions(result_rows: list[dict[str, Any]]) -> list[str]:
    conclusions: list[str] = []

    for row in result_rows:
        if row.get("status") != "OK":
            continue

        case_id = row.get("case_id", "")
        model = row.get("model", "")

        if model == "isentropic" and row.get("T_T0"):
            conclusions.append(
                f"{case_id}: For the isentropic case, M = 2 produces "
                f"T/T0 = {row['T_T0']}, P/P0 = {row['P_P0']}, and A/A* = {row['A_Astar']}."
            )

        elif model == "normal_shock" and row.get("p02_p01"):
            conclusions.append(
                f"{case_id}: The normal shock drives the flow to M2 = {row['M2']} "
                f"and causes a total-pressure loss to p02/p01 = {row['p02_p01']}."
            )

        elif model == "oblique_shock" and row.get("beta_deg"):
            conclusions.append(
                f"{case_id}: The weak oblique shock solution gives beta = {row['beta_deg']} deg, "
                f"M2 = {row['M2']}, and p02/p01 = {row['p02_p01']}."
            )

    if not conclusions:
        conclusions.append("No successful computed conclusions were available.")

    return conclusions


def render_report_html(
    *,
    title: str,
    inputs_csv: str,
    results_csv: str,
    assumptions: list[str],
    failure_modes: list[str],
    input_rows: list[dict[str, Any]],
    result_rows: list[dict[str, Any]],
    output_dir: Path,
) -> str:
    template_dir = Path(__file__).parent / "templates"
    env = Environment(
        loader=FileSystemLoader(str(template_dir)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    tmpl = env.get_template("report.html.j2")

    input_columns = ordered_union_keys(input_rows)
    result_columns = ordered_union_keys(result_rows)

    normalized_input_rows = normalize_rows(input_rows, input_columns)
    normalized_result_rows = normalize_rows(result_rows, result_columns)

    error_rows = [row for row in normalized_result_rows if row.get("status") == "ERROR"]
    ok_count = sum(1 for row in normalized_result_rows if row.get("status") == "OK")
    error_count = len(error_rows)

    assets_dir = output_dir / "assets"
    area_plot_path = assets_dir / "isentropic_area_ratio.png"
    plot_isentropic_area_ratio(area_plot_path, gamma=1.4)

    figure_paths = {
        "isentropic_area_ratio": (Path("assets") / "isentropic_area_ratio.png").as_posix()
    }

    ctx = ReportContext(
        title=title,
        inputs_csv=inputs_csv,
        results_csv=results_csv,
        assumptions=assumptions,
        failure_modes=failure_modes,
        input_columns=input_columns,
        result_columns=result_columns,
        input_rows=normalized_input_rows,
        result_rows=normalized_result_rows,
        conclusions=build_conclusions(normalized_result_rows),
        figure_paths=figure_paths,
        error_rows=error_rows,
        ok_count=ok_count,
        error_count=error_count,
    )
    return tmpl.render(ctx=ctx)