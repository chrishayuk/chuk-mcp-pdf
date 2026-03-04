"""Integration tests for chuk_mcp_pdf.server tool functions."""

from __future__ import annotations

import json

import pytest

from chuk_mcp_pdf.server import (
    add_watermark,
    create_pdf_from_html,
    create_pdf_from_images,
    create_pdf_from_text,
    extract_text,
    merge_pdfs,
    show_pdf,
    split_pdf,
)


# ---------------------------------------------------------------------------
# show_pdf
# ---------------------------------------------------------------------------


class TestShowPdf:
    @pytest.mark.asyncio
    async def test_url(self) -> None:
        result = await show_pdf(url="https://example.com/doc.pdf")
        assert result.url == "https://example.com/doc.pdf"
        assert result.type == "pdf"
        assert result.version == "1.0"

    @pytest.mark.asyncio
    async def test_with_title_and_page(self) -> None:
        result = await show_pdf(
            url="https://example.com/doc.pdf",
            title="My Doc",
            initial_page=5,
        )
        assert result.title == "My Doc"
        assert result.initial_page == 5

    @pytest.mark.asyncio
    async def test_data_uri(self) -> None:
        uri = "data:application/pdf;base64,JVBERi0xLjQ="
        result = await show_pdf(url=uri)
        assert result.url == uri


# ---------------------------------------------------------------------------
# create_pdf_from_text
# ---------------------------------------------------------------------------


class TestCreatePdfFromTextTool:
    @pytest.mark.asyncio
    async def test_returns_pdf_content(self) -> None:
        result = await create_pdf_from_text(content="Hello world")
        assert result.type == "pdf"
        assert result.url.startswith("data:application/pdf;base64,")

    @pytest.mark.asyncio
    async def test_with_title(self) -> None:
        result = await create_pdf_from_text(content="Hello", title="Test")
        assert result.title == "Test"

    @pytest.mark.asyncio
    async def test_markdown(self) -> None:
        result = await create_pdf_from_text(content="# Hello\n\n**Bold**", markdown=True)
        assert result.url.startswith("data:application/pdf;base64,")


# ---------------------------------------------------------------------------
# create_pdf_from_html
# ---------------------------------------------------------------------------


class TestCreatePdfFromHtmlTool:
    @pytest.mark.asyncio
    async def test_basic(self) -> None:
        result = await create_pdf_from_html(html="<h1>Hello</h1>")
        assert result.type == "pdf"
        assert result.url.startswith("data:application/pdf;base64,")


# ---------------------------------------------------------------------------
# create_pdf_from_images
# ---------------------------------------------------------------------------


class TestCreatePdfFromImagesTool:
    @pytest.mark.asyncio
    async def test_with_data_uri(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images(images=[sample_image_data_uri])
        assert result.type == "pdf"
        assert result.url.startswith("data:application/pdf;base64,")

    @pytest.mark.asyncio
    async def test_json_string_input(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images(images=json.dumps([sample_image_data_uri]))
        assert result.url.startswith("data:application/pdf;base64,")

    @pytest.mark.asyncio
    async def test_empty_list_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one"):
            await create_pdf_from_images(images=[])


# ---------------------------------------------------------------------------
# merge_pdfs
# ---------------------------------------------------------------------------


class TestMergePdfsTool:
    @pytest.mark.asyncio
    async def test_merge(self, two_pdf_data_uris: list[str]) -> None:
        result = await merge_pdfs(sources=two_pdf_data_uris)
        assert result.type == "pdf"
        assert result.url.startswith("data:application/pdf;base64,")

    @pytest.mark.asyncio
    async def test_json_string(self, two_pdf_data_uris: list[str]) -> None:
        result = await merge_pdfs(sources=json.dumps(two_pdf_data_uris))
        assert result.url.startswith("data:application/pdf;base64,")

    @pytest.mark.asyncio
    async def test_single_source_raises(self, sample_pdf_data_uri: str) -> None:
        with pytest.raises(ValueError, match="at least 2"):
            await merge_pdfs(sources=[sample_pdf_data_uri])


# ---------------------------------------------------------------------------
# split_pdf
# ---------------------------------------------------------------------------


class TestSplitPdfTool:
    @pytest.mark.asyncio
    async def test_split(self, sample_pdf_data_uri: str) -> None:
        result = await split_pdf(source=sample_pdf_data_uri, page_ranges=["1", "2-3"])
        assert result.type == "pdf"
        assert result.title == "Split Part 1 of 2"

    @pytest.mark.asyncio
    async def test_view_part(self, sample_pdf_data_uri: str) -> None:
        result = await split_pdf(
            source=sample_pdf_data_uri,
            page_ranges=["1", "2-3"],
            view_part=2,
        )
        assert result.title == "Split Part 2 of 2"

    @pytest.mark.asyncio
    async def test_invalid_view_part(self, sample_pdf_data_uri: str) -> None:
        with pytest.raises(ValueError, match="view_part"):
            await split_pdf(
                source=sample_pdf_data_uri,
                page_ranges=["1"],
                view_part=5,
            )

    @pytest.mark.asyncio
    async def test_empty_ranges(self, sample_pdf_data_uri: str) -> None:
        with pytest.raises(ValueError, match="at least one"):
            await split_pdf(source=sample_pdf_data_uri, page_ranges=[])


# ---------------------------------------------------------------------------
# extract_text
# ---------------------------------------------------------------------------


class TestExtractTextTool:
    @pytest.mark.asyncio
    async def test_extract(self, sample_pdf_data_uri: str) -> None:
        result = await extract_text(source=sample_pdf_data_uri)
        assert isinstance(result, str)
        assert "--- Page 1 ---" in result

    @pytest.mark.asyncio
    async def test_extract_with_range(self, sample_pdf_data_uri: str) -> None:
        result = await extract_text(source=sample_pdf_data_uri, page_range="1")
        assert "--- Page 1 ---" in result
        assert "--- Page 2 ---" not in result


# ---------------------------------------------------------------------------
# add_watermark
# ---------------------------------------------------------------------------


class TestAddWatermarkTool:
    @pytest.mark.asyncio
    async def test_text_watermark(self, sample_pdf_data_uri: str) -> None:
        result = await add_watermark(source=sample_pdf_data_uri, watermark_text="DRAFT")
        assert result.type == "pdf"
        assert result.url.startswith("data:application/pdf;base64,")

    @pytest.mark.asyncio
    async def test_no_watermark_raises(self, sample_pdf_data_uri: str) -> None:
        with pytest.raises(ValueError, match="watermark_text or watermark_image_url"):
            await add_watermark(source=sample_pdf_data_uri)


# ---------------------------------------------------------------------------
# Phase 1.1: Layout params via server tools
# ---------------------------------------------------------------------------


class TestPhase11TextTool:
    @pytest.mark.asyncio
    async def test_landscape(self) -> None:
        result = await create_pdf_from_text(content="Test", orientation="landscape")
        assert result.type == "pdf"
        assert result.url.startswith("data:application/pdf;base64,")

    @pytest.mark.asyncio
    async def test_with_headers_footers(self) -> None:
        result = await create_pdf_from_text(
            content="Body text",
            header_text="Report",
            footer_text="Confidential",
            show_page_numbers=True,
        )
        assert result.type == "pdf"

    @pytest.mark.asyncio
    async def test_multi_column(self) -> None:
        result = await create_pdf_from_text(content="Text " * 200, columns=2)
        assert result.type == "pdf"

    @pytest.mark.asyncio
    async def test_custom_margins(self) -> None:
        result = await create_pdf_from_text(
            content="Test",
            margin_top=25,
            margin_bottom=25,
            margin_left=30,
            margin_right=30,
        )
        assert result.type == "pdf"

    @pytest.mark.asyncio
    async def test_markdown_with_toc(self) -> None:
        md = "# Ch1\n\nText.\n\n## Sec 1.1\n\nMore.\n\n# Ch2\n\nEnd."
        result = await create_pdf_from_text(content=md, markdown=True, table_of_contents=True)
        assert result.type == "pdf"


class TestPhase11HtmlTool:
    @pytest.mark.asyncio
    async def test_html_landscape_headers(self) -> None:
        result = await create_pdf_from_html(
            html="<p>Content</p>",
            orientation="landscape",
            header_text="HTML Header",
            footer_text="HTML Footer",
        )
        assert result.type == "pdf"


class TestPhase11ImagesTool:
    @pytest.mark.asyncio
    async def test_images_landscape_headers(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images(
            images=[sample_image_data_uri],
            orientation="landscape",
            header_text="Image Header",
        )
        assert result.type == "pdf"
