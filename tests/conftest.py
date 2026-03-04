"""Shared test fixtures for chuk-mcp-pdf."""

from __future__ import annotations

import base64
import io

import pytest
from fpdf import FPDF
from PIL import Image


@pytest.fixture
def sample_pdf_bytes() -> bytes:
    """Create a minimal 3-page PDF for testing."""
    pdf = FPDF()
    for i in range(3):
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"Page {i + 1} content")
    return pdf.output()


@pytest.fixture
def sample_pdf_data_uri(sample_pdf_bytes: bytes) -> str:
    """Return the sample PDF as a base64 data URI."""
    b64 = base64.b64encode(sample_pdf_bytes).decode()
    return f"data:application/pdf;base64,{b64}"


@pytest.fixture
def sample_image_data_uri() -> str:
    """Generate a valid 10x10 red PNG as base64 data URI using Pillow."""
    img = Image.new("RGB", (10, 10), color=(255, 0, 0))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode()
    return f"data:image/png;base64,{b64}"


@pytest.fixture
def two_pdf_data_uris(sample_pdf_bytes: bytes) -> list[str]:
    """Two PDF data URIs for merge testing."""
    pdf1 = FPDF()
    pdf1.add_page()
    pdf1.set_font("Helvetica", size=12)
    pdf1.cell(0, 10, "Document A")
    b1 = base64.b64encode(pdf1.output()).decode()

    pdf2 = FPDF()
    pdf2.add_page()
    pdf2.set_font("Helvetica", size=12)
    pdf2.cell(0, 10, "Document B")
    b2 = base64.b64encode(pdf2.output()).decode()

    return [
        f"data:application/pdf;base64,{b1}",
        f"data:application/pdf;base64,{b2}",
    ]
