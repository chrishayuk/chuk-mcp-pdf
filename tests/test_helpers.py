"""Tests for chuk_mcp_pdf.helpers."""

from __future__ import annotations

import base64

import pytest

from chuk_mcp_pdf.helpers import (
    _decode_data_uri,
    deliver_pdf,
    get_served_file,
    pdf_to_data_uri,
    store_for_serving,
    validate_page_range,
)


# ---------------------------------------------------------------------------
# pdf_to_data_uri
# ---------------------------------------------------------------------------


class TestPdfToDataUri:
    def test_roundtrip(self) -> None:
        original = b"%PDF-1.4 test content"
        uri = pdf_to_data_uri(original)
        assert uri.startswith("data:application/pdf;base64,")
        decoded = base64.b64decode(uri.split(",", 1)[1])
        assert decoded == original

    def test_empty_bytes(self) -> None:
        uri = pdf_to_data_uri(b"")
        assert uri == "data:application/pdf;base64,"


# ---------------------------------------------------------------------------
# _decode_data_uri
# ---------------------------------------------------------------------------


class TestDecodeDataUri:
    def test_valid(self) -> None:
        content = b"hello world"
        b64 = base64.b64encode(content).decode()
        uri = f"data:application/pdf;base64,{b64}"
        assert _decode_data_uri(uri) == content

    def test_no_base64(self) -> None:
        with pytest.raises(ValueError, match="base64"):
            _decode_data_uri("data:application/pdf,notbase64")


# ---------------------------------------------------------------------------
# store_for_serving / get_served_file
# ---------------------------------------------------------------------------


class TestFileServing:
    def test_store_and_retrieve(self) -> None:
        content = b"%PDF-1.4 stored"
        token = store_for_serving(content)
        assert len(token) == 32  # uuid hex
        path = get_served_file(token)
        assert path is not None
        assert path.read_bytes() == content

    def test_unknown_token(self) -> None:
        assert get_served_file("nonexistent") is None


# ---------------------------------------------------------------------------
# deliver_pdf
# ---------------------------------------------------------------------------


class TestDeliverPdf:
    def test_base64_small(self) -> None:
        pdf_bytes = b"%PDF-1.4 small"
        result = deliver_pdf(pdf_bytes, title="Test")
        assert result.url.startswith("data:application/pdf;base64,")
        assert result.title == "Test"

    def test_base64_when_no_serve_url(self) -> None:
        # Even large PDFs should use base64 when no serve_base_url
        pdf_bytes = b"x" * (6 * 1024 * 1024)  # 6MB
        result = deliver_pdf(pdf_bytes)
        assert result.url.startswith("data:application/pdf;base64,")

    def test_file_serve_large(self) -> None:
        pdf_bytes = b"x" * (6 * 1024 * 1024)  # 6MB
        result = deliver_pdf(pdf_bytes, serve_base_url="http://localhost:8000")
        assert result.url.startswith("http://localhost:8000/pdf-files/")

    def test_initial_page(self) -> None:
        result = deliver_pdf(b"%PDF", initial_page=3)
        assert result.initial_page == 3


# ---------------------------------------------------------------------------
# validate_page_range
# ---------------------------------------------------------------------------


class TestValidatePageRange:
    def test_single_page(self) -> None:
        assert validate_page_range("1", 5) == [1]

    def test_range(self) -> None:
        assert validate_page_range("2-4", 5) == [2, 3, 4]

    def test_comma_separated(self) -> None:
        assert validate_page_range("1,3,5", 5) == [1, 3, 5]

    def test_mixed(self) -> None:
        assert validate_page_range("1-2, 4", 5) == [1, 2, 4]

    def test_dedup(self) -> None:
        assert validate_page_range("1,1,2", 3) == [1, 2]

    def test_out_of_range_high(self) -> None:
        with pytest.raises(ValueError):
            validate_page_range("6", 5)

    def test_out_of_range_low(self) -> None:
        with pytest.raises(ValueError):
            validate_page_range("0", 5)

    def test_invalid_range_reversed(self) -> None:
        with pytest.raises(ValueError):
            validate_page_range("5-2", 5)

    def test_all_pages(self) -> None:
        assert validate_page_range("1-5", 5) == [1, 2, 3, 4, 5]
