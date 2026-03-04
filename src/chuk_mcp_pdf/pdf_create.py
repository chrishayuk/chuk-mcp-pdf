"""PDF creation helpers -- text, HTML, and images to PDF.

Uses fpdf2 for lightweight pure-Python PDF generation.
Uses markdown library for markdown-to-HTML conversion.

Phase 1.1 additions: custom fonts, page layout (orientation, margins,
headers/footers, multi-column), table of contents, improved markdown.
"""

from __future__ import annotations

import logging
import re
import tempfile
from pathlib import Path
from typing import Optional

from fpdf import FPDF

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# StyledPDF -- FPDF subclass with headers, footers, and font loading
# ---------------------------------------------------------------------------


class StyledPDF(FPDF):
    """FPDF subclass that renders configurable headers and footers."""

    def __init__(
        self,
        header_text: Optional[str] = None,
        footer_text: Optional[str] = None,
        show_page_numbers: bool = True,
        font_family: str = "Helvetica",
        **kwargs: object,
    ):
        super().__init__(**kwargs)
        self._header_text = header_text
        self._footer_text = footer_text
        self._show_page_numbers = show_page_numbers
        self._body_font_family = font_family

    def header(self) -> None:
        if not self._header_text:
            return
        self.set_font(self._body_font_family, "I", 9)
        self.set_text_color(128, 128, 128)
        self.cell(0, 8, self._header_text, new_x="LMARGIN", new_y="NEXT", align="C")
        self.set_draw_color(200, 200, 200)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)
        self.set_text_color(0, 0, 0)

    def footer(self) -> None:
        if not self._footer_text and not self._show_page_numbers:
            return
        self.set_y(-15)
        self.set_font(self._body_font_family, "I", 8)
        self.set_text_color(128, 128, 128)

        parts: list[str] = []
        if self._footer_text:
            parts.append(self._footer_text)
        if self._show_page_numbers:
            parts.append(f"Page {self.page_no()}/{{nb}}")

        self.cell(0, 10, "  |  ".join(parts), align="C")
        self.set_text_color(0, 0, 0)


def _make_pdf(
    page_size: str = "A4",
    orientation: str = "portrait",
    margin_top: float = 10,
    margin_bottom: float = 10,
    margin_left: float = 10,
    margin_right: float = 10,
    font_family: str = "Helvetica",
    font_path: Optional[str] = None,
    header_text: Optional[str] = None,
    footer_text: Optional[str] = None,
    show_page_numbers: bool = True,
) -> StyledPDF:
    """Create a configured StyledPDF instance with all layout options applied."""
    pdf = StyledPDF(
        header_text=header_text,
        footer_text=footer_text,
        show_page_numbers=show_page_numbers,
        font_family=font_family,
        orientation=orientation,
        format=page_size,
    )
    pdf.set_margins(margin_left, margin_top, margin_right)
    pdf.set_auto_page_break(auto=True, margin=margin_bottom + 5)
    pdf.alias_nb_pages()

    # Load custom font if provided
    if font_path:
        p = Path(font_path)
        if not p.exists():
            raise ValueError(f"Font file not found: {font_path}")
        pdf.add_font(font_family, "", font_path)
        # Try to load bold/italic variants by convention
        for style, suffixes in [
            ("B", ["-Bold", "_Bold", "Bold", "-bold"]),
            ("I", ["-Italic", "_Italic", "Italic", "-italic"]),
        ]:
            for suffix in suffixes:
                variant = p.parent / f"{p.stem}{suffix}{p.suffix}"
                if variant.exists():
                    pdf.add_font(font_family, style, str(variant))
                    break

    return pdf


# ---------------------------------------------------------------------------
# Text / Markdown -> PDF
# ---------------------------------------------------------------------------


def create_pdf_from_text(
    content: str,
    title: Optional[str] = None,
    font_size: int = 12,
    page_size: str = "A4",
    is_markdown: bool = False,
    orientation: str = "portrait",
    margin_top: float = 10,
    margin_bottom: float = 10,
    margin_left: float = 10,
    margin_right: float = 10,
    font_family: str = "Helvetica",
    font_path: Optional[str] = None,
    columns: int = 1,
    header_text: Optional[str] = None,
    footer_text: Optional[str] = None,
    show_page_numbers: bool = True,
    table_of_contents: bool = False,
) -> bytes:
    """Create a PDF from plain text or markdown content.

    Args:
        content: Text or markdown string to render.
        title: Optional document title (rendered as a heading).
        font_size: Body text font size in points.
        page_size: Page size -- "A4", "Letter", etc.
        is_markdown: If True, parse content as markdown.
        orientation: "portrait" or "landscape".
        margin_top: Top margin in mm.
        margin_bottom: Bottom margin in mm.
        margin_left: Left margin in mm.
        margin_right: Right margin in mm.
        font_family: Font family name (built-in or matches font_path).
        font_path: Path to a TTF/OTF font file.
        columns: Number of text columns (1-3).
        header_text: Text for page header.
        footer_text: Text for page footer.
        show_page_numbers: Show page numbers in footer.
        table_of_contents: Generate TOC from markdown headings.

    Returns:
        Raw PDF bytes.
    """
    pdf = _make_pdf(
        page_size=page_size,
        orientation=orientation,
        margin_top=margin_top,
        margin_bottom=margin_bottom,
        margin_left=margin_left,
        margin_right=margin_right,
        font_family=font_family,
        font_path=font_path,
        header_text=header_text,
        footer_text=footer_text,
        show_page_numbers=show_page_numbers,
    )
    pdf.add_page()

    if title:
        pdf.set_font(font_family, "B", size=font_size + 6)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

    if is_markdown:
        _render_markdown(
            pdf,
            content,
            font_size,
            font_family=font_family,
            columns=columns,
            table_of_contents=table_of_contents,
        )
    elif columns > 1:
        pdf.set_font(font_family, size=font_size)
        cols = pdf.text_columns(ncols=min(columns, 3), gutter=5)
        with cols:
            cols.write(text=content)
    else:
        pdf.set_font(font_family, size=font_size)
        pdf.multi_cell(0, font_size * 0.5, content)

    return pdf.output()


def _render_markdown(
    pdf: StyledPDF,
    md_text: str,
    base_font_size: int,
    font_family: str = "Helvetica",
    columns: int = 1,
    table_of_contents: bool = False,
) -> None:
    """Render markdown to PDF using fpdf2's write_html method."""
    try:
        import markdown

        html = markdown.markdown(md_text, extensions=["tables", "fenced_code"])
    except ImportError:
        logger.warning("markdown package not installed; rendering as plain text")
        pdf.set_font(font_family, size=base_font_size)
        pdf.multi_cell(0, base_font_size * 0.5, md_text)
        return

    # Table of contents: parse headings and insert TOC + sections
    if table_of_contents:
        _render_markdown_with_toc(pdf, md_text, html, base_font_size, font_family, columns)
        return

    pdf.set_font(font_family, size=base_font_size)
    # Note: write_html uses its own internal text_columns, so multi-column
    # layout is not supported for markdown/HTML content.
    pdf.write_html(html)


def _render_markdown_with_toc(
    pdf: StyledPDF,
    md_text: str,
    html: str,
    base_font_size: int,
    font_family: str,
    columns: int,
) -> None:
    """Render markdown with a table of contents generated from headings."""
    from fpdf.outline import TableOfContents

    toc = TableOfContents()
    pdf.insert_toc_placeholder(toc.render_toc, allow_extra_pages=True)
    pdf.add_page()

    # Split markdown by headings and render each section
    heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    last_end = 0
    sections: list[tuple[int, str, str]] = []

    for match in heading_pattern.finditer(md_text):
        level = len(match.group(1)) - 1  # 0-based
        heading_text = match.group(2).strip()
        pre_content = md_text[last_end : match.start()]
        sections.append((level, heading_text, pre_content))
        last_end = match.end()

    # Remaining content after last heading
    trailing = md_text[last_end:]

    try:
        import markdown
    except ImportError:
        pdf.set_font(font_family, size=base_font_size)
        pdf.multi_cell(0, base_font_size * 0.5, md_text)
        return

    pdf.set_font(font_family, size=base_font_size)
    for level, heading_text, pre_content in sections:
        # Render any content before this heading
        if pre_content.strip():
            section_html = markdown.markdown(pre_content, extensions=["tables", "fenced_code"])
            pdf.write_html(section_html)

        # Start a new section for the TOC
        pdf.start_section(heading_text, level=level)

        # Render the heading itself
        heading_html = markdown.markdown(
            f"{'#' * (level + 1)} {heading_text}",
            extensions=["tables", "fenced_code"],
        )
        pdf.write_html(heading_html)

    # Render trailing content
    if trailing.strip():
        trailing_html = markdown.markdown(trailing, extensions=["tables", "fenced_code"])
        pdf.write_html(trailing_html)


# ---------------------------------------------------------------------------
# HTML -> PDF
# ---------------------------------------------------------------------------


def create_pdf_from_html(
    html_content: str,
    title: Optional[str] = None,
    page_size: str = "A4",
    orientation: str = "portrait",
    margin_top: float = 10,
    margin_bottom: float = 10,
    margin_left: float = 10,
    margin_right: float = 10,
    font_family: str = "Helvetica",
    font_path: Optional[str] = None,
    header_text: Optional[str] = None,
    footer_text: Optional[str] = None,
    show_page_numbers: bool = True,
) -> bytes:
    """Create a PDF from HTML content.

    Uses fpdf2's write_html for basic HTML support. For full CSS rendering
    (if weasyprint is installed), uses that instead.

    Args:
        html_content: HTML string to render.
        title: Optional document title.
        page_size: Page size -- "A4", "Letter", etc.
        orientation: "portrait" or "landscape".
        margin_top: Top margin in mm.
        margin_bottom: Bottom margin in mm.
        margin_left: Left margin in mm.
        margin_right: Right margin in mm.
        font_family: Font family name (built-in or matches font_path).
        font_path: Path to a TTF/OTF font file.
        header_text: Text for page header.
        footer_text: Text for page footer.
        show_page_numbers: Show page numbers in footer.

    Returns:
        Raw PDF bytes.
    """
    # Try weasyprint first for full CSS support
    try:
        import weasyprint

        html_doc = html_content
        if title:
            html_doc = (
                f"<html><head><title>{title}</title></head><body>{html_content}</body></html>"
            )
        doc = weasyprint.HTML(string=html_doc)
        return doc.write_pdf()
    except ImportError:
        pass

    # Fallback: fpdf2 write_html (supports basic HTML tags)
    pdf = _make_pdf(
        page_size=page_size,
        orientation=orientation,
        margin_top=margin_top,
        margin_bottom=margin_bottom,
        margin_left=margin_left,
        margin_right=margin_right,
        font_family=font_family,
        font_path=font_path,
        header_text=header_text,
        footer_text=footer_text,
        show_page_numbers=show_page_numbers,
    )
    pdf.add_page()

    if title:
        pdf.set_font(font_family, "B", size=18)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

    pdf.set_font(font_family, size=12)
    pdf.write_html(html_content)

    return pdf.output()


# ---------------------------------------------------------------------------
# Images -> PDF
# ---------------------------------------------------------------------------


async def create_pdf_from_images(
    image_sources: list[str],
    title: Optional[str] = None,
    page_size: str = "A4",
    one_per_page: bool = True,
    orientation: str = "portrait",
    margin_top: float = 10,
    margin_bottom: float = 10,
    margin_left: float = 10,
    margin_right: float = 10,
    header_text: Optional[str] = None,
    footer_text: Optional[str] = None,
    show_page_numbers: bool = True,
) -> bytes:
    """Combine one or more images into a PDF.

    Args:
        image_sources: List of image URLs or base64 data URIs.
        title: Optional document title.
        page_size: Page size -- "A4", "Letter", etc.
        one_per_page: If True, each image gets its own page.
        orientation: "portrait" or "landscape".
        margin_top: Top margin in mm.
        margin_bottom: Bottom margin in mm.
        margin_left: Left margin in mm.
        margin_right: Right margin in mm.
        header_text: Text for page header.
        footer_text: Text for page footer.
        show_page_numbers: Show page numbers in footer.

    Returns:
        Raw PDF bytes.
    """
    from .helpers import fetch_image_bytes

    pdf = _make_pdf(
        page_size=page_size,
        orientation=orientation,
        margin_top=margin_top,
        margin_bottom=margin_bottom,
        margin_left=margin_left,
        margin_right=margin_right,
        header_text=header_text,
        footer_text=footer_text,
        show_page_numbers=show_page_numbers,
    )

    if title:
        pdf.add_page()
        pdf.set_font(pdf._body_font_family, "B", size=18)
        pdf.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT", align="C")
        pdf.ln(5)

    ext_map = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/jpg": "jpg",
        "image/gif": "gif",
        "image/webp": "webp",
        "image/bmp": "bmp",
    }

    for i, source in enumerate(image_sources):
        img_bytes, mime_type = await fetch_image_bytes(source)
        ext = ext_map.get(mime_type, "png")

        # Write to temp file for fpdf2
        with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as tmp:
            tmp.write(img_bytes)
            tmp_path = tmp.name

        try:
            if one_per_page or i == 0:
                if not (title and i == 0):
                    pdf.add_page()

            # Calculate width to fit within page margins
            page_w = pdf.w - pdf.l_margin - pdf.r_margin
            pdf.image(tmp_path, x=pdf.l_margin, w=page_w)
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    return pdf.output()
