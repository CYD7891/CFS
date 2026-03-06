from __future__ import annotations

from pathlib import Path


def _get_weasyprint_html():
    from weasyprint import HTML
    return HTML


def render_pdf_from_html(html_path: Path, pdf_path: Path) -> tuple[bool, str]:
    """
    Try to render a PDF from an existing HTML file.

    Returns:
        (success, message)
    """
    try:
        HTML = _get_weasyprint_html()
    except Exception as exc:
        return (
            False,
            f"PDF generation skipped: WeasyPrint is unavailable ({exc}). "
            "HTML report was still generated successfully.",
        )

    try:
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        HTML(filename=str(html_path), base_url=str(html_path.parent)).write_pdf(str(pdf_path))
        return True, f"PDF generated: {pdf_path}"
    except Exception as exc:
        return (
            False,
            f"PDF generation failed gracefully ({exc}). "
            "HTML report was still generated successfully.",
        )