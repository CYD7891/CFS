from __future__ import annotations

from pathlib import Path

import cfs.report.render_pdf as rp


def test_render_pdf_missing_dependency_is_graceful(monkeypatch, tmp_path: Path):
    html_path = tmp_path / "report.html"
    pdf_path = tmp_path / "report.pdf"
    html_path.write_text("<html><body><h1>Hello</h1></body></html>", encoding="utf-8")

    def fake_get_weasyprint_html():
        raise ImportError("No module named 'weasyprint'")

    monkeypatch.setattr(rp, "_get_weasyprint_html", fake_get_weasyprint_html)

    ok, message = rp.render_pdf_from_html(html_path, pdf_path)

    assert ok is False
    assert "WeasyPrint" in message or "weasyprint" in message.lower()
    assert not pdf_path.exists()


def test_render_pdf_success_path(monkeypatch, tmp_path: Path):
    html_path = tmp_path / "report.html"
    pdf_path = tmp_path / "report.pdf"
    html_path.write_text("<html><body><h1>Hello</h1></body></html>", encoding="utf-8")

    class FakeHTML:
        def __init__(self, filename: str, base_url: str | None = None):
            self.filename = filename
            self.base_url = base_url

        def write_pdf(self, output_path: str):
            Path(output_path).write_bytes(b"%PDF-FAKE%")

    monkeypatch.setattr(rp, "_get_weasyprint_html", lambda: FakeHTML)

    ok, message = rp.render_pdf_from_html(html_path, pdf_path)

    assert ok is True
    assert "PDF generated" in message
    assert pdf_path.exists()
    assert pdf_path.stat().st_size > 0