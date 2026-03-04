"""Tests for chuk_mcp_pdf.pdf_edit."""

from __future__ import annotations

import io

import pytest
from pypdf import PdfReader

from chuk_mcp_pdf.pdf_edit import (
    add_watermark_to_pdf,
    extract_text_from_pdf,
    merge_pdfs,
    split_pdf,
)


# ---------------------------------------------------------------------------
# merge_pdfs
# ---------------------------------------------------------------------------


class TestMergePdfs:
    @pytest.mark.asyncio
    async def test_merge_two(self, two_pdf_data_uris: list[str]) -> None:
        result = await merge_pdfs(two_pdf_data_uris)
        assert result[:5] == b"%PDF-"
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) == 2

    @pytest.mark.asyncio
    async def test_merge_with_title(self, two_pdf_data_uris: list[str]) -> None:
        result = await merge_pdfs(two_pdf_data_uris, title="Merged")
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) == 2


# ---------------------------------------------------------------------------
# split_pdf
# ---------------------------------------------------------------------------


class TestSplitPdf:
    @pytest.mark.asyncio
    async def test_split_by_page(self, sample_pdf_data_uri: str) -> None:
        parts = await split_pdf(sample_pdf_data_uri, ["1", "2-3"])
        assert len(parts) == 2

        reader1 = PdfReader(io.BytesIO(parts[0]))
        assert len(reader1.pages) == 1

        reader2 = PdfReader(io.BytesIO(parts[1]))
        assert len(reader2.pages) == 2

    @pytest.mark.asyncio
    async def test_split_single_range(self, sample_pdf_data_uri: str) -> None:
        parts = await split_pdf(sample_pdf_data_uri, ["1-3"])
        assert len(parts) == 1
        reader = PdfReader(io.BytesIO(parts[0]))
        assert len(reader.pages) == 3


# ---------------------------------------------------------------------------
# extract_text_from_pdf
# ---------------------------------------------------------------------------


class TestExtractText:
    @pytest.mark.asyncio
    async def test_extract_all(self, sample_pdf_data_uri: str) -> None:
        text = await extract_text_from_pdf(sample_pdf_data_uri)
        assert "--- Page 1 ---" in text
        assert "--- Page 2 ---" in text
        assert "--- Page 3 ---" in text

    @pytest.mark.asyncio
    async def test_extract_range(self, sample_pdf_data_uri: str) -> None:
        text = await extract_text_from_pdf(sample_pdf_data_uri, page_range="1,3")
        assert "--- Page 1 ---" in text
        assert "--- Page 3 ---" in text
        assert "--- Page 2 ---" not in text

    @pytest.mark.asyncio
    async def test_extract_contains_content(self, sample_pdf_data_uri: str) -> None:
        text = await extract_text_from_pdf(sample_pdf_data_uri)
        # fpdf2-generated PDFs should contain the text we put in
        assert "Page" in text


# ---------------------------------------------------------------------------
# add_watermark_to_pdf
# ---------------------------------------------------------------------------


class TestAddWatermark:
    @pytest.mark.asyncio
    async def test_text_watermark(self, sample_pdf_data_uri: str) -> None:
        result = await add_watermark_to_pdf(sample_pdf_data_uri, watermark_text="DRAFT")
        assert result[:5] == b"%PDF-"
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) == 3

    @pytest.mark.asyncio
    async def test_watermark_specific_pages(self, sample_pdf_data_uri: str) -> None:
        result = await add_watermark_to_pdf(
            sample_pdf_data_uri, watermark_text="CONFIDENTIAL", page_range="1,3"
        )
        assert result[:5] == b"%PDF-"
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) == 3

    @pytest.mark.asyncio
    async def test_watermark_opacity(self, sample_pdf_data_uri: str) -> None:
        result = await add_watermark_to_pdf(sample_pdf_data_uri, watermark_text="TEST", opacity=0.5)
        assert result[:5] == b"%PDF-"
