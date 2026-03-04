"""Helper utilities for chuk-mcp-pdf.

Covers PDF delivery (base64 data URI vs HTTP file serving),
remote URL fetching, and input validation.
"""

from __future__ import annotations

import base64
import logging
import tempfile
import uuid
from pathlib import Path
from typing import Optional

import httpx

from chuk_view_schemas.pdf import PdfContent

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# PDFs smaller than this go as base64 data URIs; larger ones get served via HTTP
SIZE_THRESHOLD_BYTES: int = 5 * 1024 * 1024  # 5 MB

# Temp directory for served PDFs (HTTP mode only)
_SERVE_DIR: Path | None = None
_served_files: dict[str, Path] = {}  # token -> file path


# ---------------------------------------------------------------------------
# PDF delivery
# ---------------------------------------------------------------------------


def pdf_to_data_uri(pdf_bytes: bytes) -> str:
    """Encode raw PDF bytes as a base64 data URI."""
    b64 = base64.b64encode(pdf_bytes).decode("ascii")
    return f"data:application/pdf;base64,{b64}"


def store_for_serving(pdf_bytes: bytes) -> str:
    """Write PDF to a temp file and return a token for retrieval.

    Returns a token string. The caller must combine this with the
    server's base URL to form the full serving URL.
    """
    global _SERVE_DIR
    if _SERVE_DIR is None:
        _SERVE_DIR = Path(tempfile.mkdtemp(prefix="chuk-pdf-"))

    token = uuid.uuid4().hex
    file_path = _SERVE_DIR / f"{token}.pdf"
    file_path.write_bytes(pdf_bytes)
    _served_files[token] = file_path
    return token


def get_served_file(token: str) -> Path | None:
    """Retrieve a previously stored PDF file path by token."""
    return _served_files.get(token)


def deliver_pdf(
    pdf_bytes: bytes,
    title: Optional[str] = None,
    initial_page: Optional[int] = None,
    serve_base_url: Optional[str] = None,
) -> PdfContent:
    """Create a PdfContent, choosing base64 or file-serving based on size.

    Args:
        pdf_bytes: Raw PDF content.
        title: Optional display title.
        initial_page: Optional page to open to (1-based).
        serve_base_url: If provided and the PDF exceeds SIZE_THRESHOLD_BYTES,
            store the PDF and return an HTTP URL. If None, always use base64.
    """
    if serve_base_url and len(pdf_bytes) > SIZE_THRESHOLD_BYTES:
        token = store_for_serving(pdf_bytes)
        url = f"{serve_base_url}/pdf-files/{token}"
    else:
        url = pdf_to_data_uri(pdf_bytes)

    return PdfContent(
        url=url,
        title=title,
        initial_page=initial_page,
    )


# ---------------------------------------------------------------------------
# URL / data fetching
# ---------------------------------------------------------------------------


async def fetch_pdf_bytes(source: str) -> bytes:
    """Fetch PDF bytes from a URL or decode from a base64 data URI.

    Args:
        source: An HTTPS URL or a base64 data URI (data:application/pdf;base64,...).

    Returns:
        Raw PDF bytes.

    Raises:
        ValueError: If the source is not a valid URL or data URI.
        httpx.HTTPStatusError: If the URL returns a non-2xx status.
    """
    if source.startswith("data:"):
        return _decode_data_uri(source)

    if source.startswith(("http://", "https://")):
        return await _fetch_url(source)

    raise ValueError(f"Invalid PDF source: must be an HTTP(S) URL or data URI, got: {source[:80]}")


async def fetch_image_bytes(source: str) -> tuple[bytes, str]:
    """Fetch image bytes from a URL or decode from a base64 data URI.

    Returns:
        (image_bytes, mime_type) tuple. mime_type is e.g. "image/png".
    """
    if source.startswith("data:"):
        # data:image/png;base64,iVBOR...
        header, b64_data = source.split(",", 1)
        mime = header.split(":")[1].split(";")[0]
        return base64.b64decode(b64_data), mime

    if source.startswith(("http://", "https://")):
        async with httpx.AsyncClient(follow_redirects=True, timeout=30.0) as client:
            resp = await client.get(source)
            resp.raise_for_status()
            ct = resp.headers.get("content-type", "image/png").split(";")[0]
            return resp.content, ct

    raise ValueError(f"Invalid image source: {source[:80]}")


def _decode_data_uri(data_uri: str) -> bytes:
    """Decode a base64 data URI to raw bytes."""
    if ";base64," not in data_uri:
        raise ValueError("Data URI must use base64 encoding.")
    _, b64_data = data_uri.split(";base64,", 1)
    return base64.b64decode(b64_data)


async def _fetch_url(url: str) -> bytes:
    """Fetch bytes from an HTTP(S) URL."""
    async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


def validate_page_range(page_range: str, total_pages: int) -> list[int]:
    """Parse a page range string into a list of 1-based page numbers.

    Supports: "1", "1-5", "1,3,5", "1-3,7,10-12"

    Args:
        page_range: Human-readable page range string.
        total_pages: Total number of pages in the PDF.

    Returns:
        Sorted list of 1-based page numbers.

    Raises:
        ValueError: If the range is invalid or out of bounds.
    """
    pages: set[int] = set()
    for part in page_range.split(","):
        part = part.strip()
        if "-" in part:
            start_s, end_s = part.split("-", 1)
            start, end = int(start_s.strip()), int(end_s.strip())
            if start < 1 or end > total_pages or start > end:
                raise ValueError(f"Invalid page range '{part}': must be within 1-{total_pages}")
            pages.update(range(start, end + 1))
        else:
            p = int(part)
            if p < 1 or p > total_pages:
                raise ValueError(f"Page {p} is out of range (1-{total_pages})")
            pages.add(p)
    return sorted(pages)
