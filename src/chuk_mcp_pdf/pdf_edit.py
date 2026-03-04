"""PDF editing helpers -- merge, split, extract text, watermark.

Uses pypdf for all PDF manipulation operations.
"""

from __future__ import annotations

import io
import logging
from typing import Optional

from pypdf import PdfReader, PdfWriter

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Merge
# ---------------------------------------------------------------------------


async def merge_pdfs(
    sources: list[str],
    title: Optional[str] = None,
) -> bytes:
    """Merge multiple PDFs into one.

    Args:
        sources: List of PDF URLs or base64 data URIs.
        title: Optional title metadata for the merged PDF.

    Returns:
        Raw PDF bytes of the merged document.
    """
    from .helpers import fetch_pdf_bytes

    writer = PdfWriter()

    for source in sources:
        pdf_bytes = await fetch_pdf_bytes(source)
        reader = PdfReader(io.BytesIO(pdf_bytes))
        for page in reader.pages:
            writer.add_page(page)

    if title:
        writer.add_metadata({"/Title": title})

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


# ---------------------------------------------------------------------------
# Split
# ---------------------------------------------------------------------------


async def split_pdf(
    source: str,
    page_ranges: list[str],
) -> list[bytes]:
    """Split a PDF into multiple PDFs by page ranges.

    Args:
        source: PDF URL or base64 data URI.
        page_ranges: List of page range strings, e.g. ["1-3", "4-6", "7"].
            Each range produces one output PDF.

    Returns:
        List of raw PDF bytes, one per page range.
    """
    from .helpers import fetch_pdf_bytes, validate_page_range

    pdf_bytes = await fetch_pdf_bytes(source)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)

    results: list[bytes] = []
    for range_str in page_ranges:
        pages = validate_page_range(range_str, total_pages)
        writer = PdfWriter()
        for page_num in pages:
            writer.add_page(reader.pages[page_num - 1])  # 0-indexed

        output = io.BytesIO()
        writer.write(output)
        results.append(output.getvalue())

    return results


# ---------------------------------------------------------------------------
# Extract text
# ---------------------------------------------------------------------------


async def extract_text_from_pdf(
    source: str,
    page_range: Optional[str] = None,
) -> str:
    """Extract text content from a PDF.

    Args:
        source: PDF URL or base64 data URI.
        page_range: Optional page range string (e.g. "1-3,5").
            If None, extracts from all pages.

    Returns:
        Extracted text content, with page separators.
    """
    from .helpers import fetch_pdf_bytes, validate_page_range

    pdf_bytes = await fetch_pdf_bytes(source)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)

    if page_range:
        pages = validate_page_range(page_range, total_pages)
    else:
        pages = list(range(1, total_pages + 1))

    text_parts: list[str] = []
    for page_num in pages:
        page = reader.pages[page_num - 1]
        text = page.extract_text() or ""
        text_parts.append(f"--- Page {page_num} ---\n{text}")

    return "\n\n".join(text_parts)


# ---------------------------------------------------------------------------
# Watermark
# ---------------------------------------------------------------------------


async def add_watermark_to_pdf(
    source: str,
    watermark_text: Optional[str] = None,
    watermark_image_url: Optional[str] = None,
    opacity: float = 0.3,
    page_range: Optional[str] = None,
) -> bytes:
    """Add a text or image watermark to PDF pages.

    Args:
        source: PDF URL or base64 data URI.
        watermark_text: Text to use as watermark (e.g. "CONFIDENTIAL").
        watermark_image_url: URL or data URI of watermark image.
        opacity: Watermark opacity 0.0-1.0.
        page_range: Pages to watermark. If None, watermarks all pages.

    Returns:
        Raw PDF bytes with watermarks applied.
    """
    from .helpers import fetch_pdf_bytes, validate_page_range

    pdf_bytes = await fetch_pdf_bytes(source)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    total_pages = len(reader.pages)

    if page_range:
        target_pages = set(validate_page_range(page_range, total_pages))
    else:
        target_pages = set(range(1, total_pages + 1))

    # Create the watermark PDF overlay
    watermark_pdf = _create_watermark_overlay(
        watermark_text=watermark_text,
        opacity=opacity,
        page_width=float(reader.pages[0].mediabox.width),
        page_height=float(reader.pages[0].mediabox.height),
    )
    watermark_reader = PdfReader(io.BytesIO(watermark_pdf))
    watermark_page = watermark_reader.pages[0]

    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if (i + 1) in target_pages:
            page.merge_page(watermark_page)
        writer.add_page(page)

    output = io.BytesIO()
    writer.write(output)
    return output.getvalue()


def _create_watermark_overlay(
    watermark_text: Optional[str],
    opacity: float,
    page_width: float,
    page_height: float,
) -> bytes:
    """Create a single-page PDF to use as a watermark overlay.

    Uses fpdf2 to generate the overlay page with diagonal text.
    """
    from fpdf import FPDF

    # Convert PDF units (points) to mm for fpdf2
    width_mm = page_width * 25.4 / 72
    height_mm = page_height * 25.4 / 72

    pdf = FPDF(unit="mm", format=(width_mm, height_mm))
    pdf.add_page()
    pdf.set_auto_page_break(auto=False)

    if watermark_text:
        pdf.set_font("Helvetica", "B", size=60)
        # Set text color with opacity via gray level
        gray = int(255 * (1 - opacity))
        pdf.set_text_color(gray, gray, gray)

        # Rotate and center the text
        with pdf.rotation(angle=45, x=width_mm / 2, y=height_mm / 2):
            pdf.set_xy(0, height_mm / 2 - 15)
            pdf.cell(width_mm, 30, watermark_text, align="C")

    return pdf.output()
