"""PDF MCP Server -- create, edit, and view PDF documents.

Provides eight tools:

Creation:
- create_pdf_from_text   -- Convert text/markdown to PDF
- create_pdf_from_html   -- Render HTML to PDF
- create_pdf_from_images -- Combine images into a PDF

Editing:
- merge_pdfs             -- Merge multiple PDFs into one
- split_pdf              -- Split a PDF by page ranges
- extract_text           -- Extract text from PDF pages
- add_watermark          -- Add text/image watermark to pages

Viewing:
- show_pdf               -- Display a PDF in the viewer

Built with chuk-mcp-server; renders via chuk-view-schemas PdfContent.
"""

import json
import logging
import sys
from typing import Optional, Union

from chuk_mcp_server import ChukMCPServer
from chuk_view_schemas.chuk_mcp import pdf_tool
from chuk_view_schemas.pdf import PdfContent

from . import __version__
from .helpers import deliver_pdf
from .pdf_create import create_pdf_from_html as _create_html
from .pdf_create import create_pdf_from_images as _create_images
from .pdf_create import create_pdf_from_text as _create_text
from .pdf_edit import add_watermark_to_pdf as _watermark
from .pdf_edit import extract_text_from_pdf as _extract
from .pdf_edit import merge_pdfs as _merge
from .pdf_edit import split_pdf as _split

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s:%(name)s:%(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP server instance
# ---------------------------------------------------------------------------
mcp = ChukMCPServer(
    name="chuk-mcp-pdf",
    version=__version__,
    title="PDF Server",
    description=(
        "Create, edit, and view PDF documents -- text/markdown to PDF, "
        "HTML to PDF, image compilation, merge, split, text extraction, "
        "watermarking, and interactive viewing."
    ),
)


# ---------------------------------------------------------------------------
# Tool: show_pdf  (view only -- uses pdf_tool decorator)
# ---------------------------------------------------------------------------


@pdf_tool(
    mcp,
    "show_pdf",
    description=(
        "Display a PDF in the interactive viewer. "
        "Pass an HTTPS URL to a PDF file, or a base64 data URI. "
        "Optionally specify an initial page and title."
    ),
    read_only_hint=True,
)
async def show_pdf(
    url: str,
    title: Optional[str] = None,
    initial_page: Optional[int] = None,
) -> PdfContent:
    """Display a PDF document in the viewer."""
    return PdfContent(url=url, title=title, initial_page=initial_page)


# ---------------------------------------------------------------------------
# Tool: create_pdf_from_text
# ---------------------------------------------------------------------------


@pdf_tool(
    mcp,
    "create_pdf_from_text",
    description=(
        "Create a PDF from plain text or markdown. "
        "Pass text content and it will be rendered into a styled PDF. "
        "Set markdown=true for headings, bold, italic, lists, and tables. "
        "Supports custom fonts, page layout, multi-column, headers/footers, "
        "and table of contents generation."
    ),
)
async def create_pdf_from_text(
    content: str,
    title: Optional[str] = None,
    markdown: bool = False,
    font_size: int = 12,
    page_size: str = "A4",
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
) -> PdfContent:
    """Create a PDF from text or markdown content."""
    pdf_bytes = _create_text(
        content=content,
        title=title,
        font_size=font_size,
        page_size=page_size,
        is_markdown=markdown,
        orientation=orientation,
        margin_top=margin_top,
        margin_bottom=margin_bottom,
        margin_left=margin_left,
        margin_right=margin_right,
        font_family=font_family,
        font_path=font_path,
        columns=columns,
        header_text=header_text,
        footer_text=footer_text,
        show_page_numbers=show_page_numbers,
        table_of_contents=table_of_contents,
    )
    return deliver_pdf(pdf_bytes, title=title)


# ---------------------------------------------------------------------------
# Tool: create_pdf_from_html
# ---------------------------------------------------------------------------


@pdf_tool(
    mcp,
    "create_pdf_from_html",
    description=(
        "Create a PDF from HTML content. "
        "Supports headings, paragraphs, tables, lists, images, and basic CSS "
        "(full CSS requires weasyprint). "
        "Pass raw HTML and receive a viewable PDF. "
        "Supports custom fonts, page layout, and headers/footers."
    ),
)
async def create_pdf_from_html(
    html: str,
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
) -> PdfContent:
    """Create a PDF from HTML content."""
    pdf_bytes = _create_html(
        html_content=html,
        title=title,
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
    return deliver_pdf(pdf_bytes, title=title)


# ---------------------------------------------------------------------------
# Tool: create_pdf_from_images
# ---------------------------------------------------------------------------


@pdf_tool(
    mcp,
    "create_pdf_from_images",
    description=(
        "Create a PDF from one or more images. "
        "Pass a JSON array of image URLs or base64 data URIs. "
        "Each image becomes a page in the PDF. "
        "Supports page layout and headers/footers."
    ),
)
async def create_pdf_from_images(
    images: Union[str, list[str]],
    title: Optional[str] = None,
    page_size: str = "A4",
    orientation: str = "portrait",
    margin_top: float = 10,
    margin_bottom: float = 10,
    margin_left: float = 10,
    margin_right: float = 10,
    header_text: Optional[str] = None,
    footer_text: Optional[str] = None,
    show_page_numbers: bool = True,
) -> PdfContent:
    """Create a PDF from images."""
    if isinstance(images, str):
        image_list = json.loads(images)
    else:
        image_list = images

    if not image_list:
        raise ValueError("images must contain at least one image URL or data URI.")

    pdf_bytes = await _create_images(
        image_sources=image_list,
        title=title,
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
    return deliver_pdf(pdf_bytes, title=title)


# ---------------------------------------------------------------------------
# Tool: merge_pdfs
# ---------------------------------------------------------------------------


@pdf_tool(
    mcp,
    "merge_pdfs",
    description=(
        "Merge multiple PDF documents into one. "
        "Pass a JSON array of PDF URLs or base64 data URIs. "
        "Documents are concatenated in order."
    ),
)
async def merge_pdfs(
    sources: Union[str, list[str]],
    title: Optional[str] = None,
) -> PdfContent:
    """Merge multiple PDFs into one document."""
    if isinstance(sources, str):
        source_list = json.loads(sources)
    else:
        source_list = sources

    if len(source_list) < 2:
        raise ValueError("merge_pdfs requires at least 2 PDF sources.")

    pdf_bytes = await _merge(sources=source_list, title=title)
    return deliver_pdf(pdf_bytes, title=title or "Merged Document")


# ---------------------------------------------------------------------------
# Tool: split_pdf
# ---------------------------------------------------------------------------


@pdf_tool(
    mcp,
    "split_pdf",
    description=(
        "Split a PDF into multiple PDFs by page ranges. "
        "Returns the first split part as a viewable PDF. "
        'page_ranges: JSON array of range strings, e.g. ["1-3", "4-6", "7"].'
    ),
)
async def split_pdf(
    source: str,
    page_ranges: Union[str, list[str]],
    view_part: int = 1,
) -> PdfContent:
    """Split a PDF into parts by page ranges."""
    if isinstance(page_ranges, str):
        ranges = json.loads(page_ranges)
    else:
        ranges = page_ranges

    if not ranges:
        raise ValueError("page_ranges must contain at least one range.")

    parts = await _split(source=source, page_ranges=ranges)

    idx = view_part - 1
    if idx < 0 or idx >= len(parts):
        raise ValueError(f"view_part must be 1-{len(parts)}, got {view_part}")

    return deliver_pdf(
        parts[idx],
        title=f"Split Part {view_part} of {len(parts)}",
    )


# ---------------------------------------------------------------------------
# Tool: extract_text  (returns plain text, NOT a pdf_tool)
# ---------------------------------------------------------------------------


@mcp.tool(
    name="extract_text",
    description=(
        "Extract text content from a PDF. "
        "Returns plain text, not a PDF view. "
        "Optionally specify pages to extract from (e.g. '1-3,5')."
    ),
    read_only_hint=True,
)
async def extract_text(
    source: str,
    page_range: Optional[str] = None,
) -> str:
    """Extract text from a PDF document."""
    return await _extract(source=source, page_range=page_range)


# ---------------------------------------------------------------------------
# Tool: add_watermark
# ---------------------------------------------------------------------------


@pdf_tool(
    mcp,
    "add_watermark",
    description=(
        "Add a text or image watermark to PDF pages. "
        "Pass the PDF source and either watermark_text (e.g. 'CONFIDENTIAL') "
        "or watermark_image_url. Optionally limit to specific pages."
    ),
)
async def add_watermark(
    source: str,
    watermark_text: Optional[str] = None,
    watermark_image_url: Optional[str] = None,
    opacity: float = 0.3,
    page_range: Optional[str] = None,
) -> PdfContent:
    """Add a watermark to PDF pages."""
    if not watermark_text and not watermark_image_url:
        raise ValueError("Provide either watermark_text or watermark_image_url.")

    pdf_bytes = await _watermark(
        source=source,
        watermark_text=watermark_text,
        watermark_image_url=watermark_image_url,
        opacity=opacity,
        page_range=page_range,
    )
    return deliver_pdf(
        pdf_bytes,
        title="Watermarked Document",
    )


# ---------------------------------------------------------------------------
# File serving endpoint (HTTP mode only)
# ---------------------------------------------------------------------------


def _register_file_serving() -> None:
    """Register the /pdf-files/{token} endpoint for serving large PDFs."""
    from starlette.requests import Request
    from starlette.responses import Response

    from chuk_mcp_server.endpoint_registry import http_endpoint_registry

    from .helpers import get_served_file

    async def serve_pdf(request: Request) -> Response:
        token = request.path_params.get("token", "")
        file_path = get_served_file(token)
        if file_path is None or not file_path.exists():
            return Response("Not Found", status_code=404)

        pdf_bytes = file_path.read_bytes()
        return Response(
            pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'inline; filename="{token}.pdf"',
                "Access-Control-Allow-Origin": "*",
            },
        )

    http_endpoint_registry.register_endpoint(
        "/pdf-files/{token}",
        serve_pdf,
        methods=["GET"],
        name="serve_pdf_file",
        description="Serve generated PDF files for large documents",
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """Run the PDF MCP server."""
    use_stdio = True

    if len(sys.argv) > 1 and sys.argv[1] in ("http", "--http"):
        use_stdio = False
        _register_file_serving()
        logger.warning("Starting Chuk MCP PDF Server in HTTP mode")

    if use_stdio:
        logging.getLogger("chuk_mcp_server").setLevel(logging.ERROR)
        logging.getLogger("chuk_mcp_server.core").setLevel(logging.ERROR)
        logging.getLogger("chuk_mcp_server.stdio_transport").setLevel(logging.ERROR)

    mcp.run(stdio=use_stdio)


if __name__ == "__main__":
    main()
