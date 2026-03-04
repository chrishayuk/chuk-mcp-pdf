"""Tests for chuk_mcp_pdf.pdf_create."""

from __future__ import annotations

import io

import pytest
from pypdf import PdfReader

from chuk_mcp_pdf.pdf_create import (
    create_pdf_from_html,
    create_pdf_from_images,
    create_pdf_from_text,
)


# ---------------------------------------------------------------------------
# create_pdf_from_text
# ---------------------------------------------------------------------------


class TestCreatePdfFromText:
    def test_basic_text(self) -> None:
        result = create_pdf_from_text("Hello, World!")
        assert result[:5] == b"%PDF-"

    def test_with_title(self) -> None:
        result = create_pdf_from_text("Body text", title="My Title")
        assert result[:5] == b"%PDF-"
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) >= 1

    def test_markdown_mode(self) -> None:
        md = "# Heading\n\nSome **bold** text and *italic* text."
        result = create_pdf_from_text(md, is_markdown=True)
        assert result[:5] == b"%PDF-"

    def test_letter_page_size(self) -> None:
        result = create_pdf_from_text("Test", page_size="Letter")
        assert result[:5] == b"%PDF-"

    def test_custom_font_size(self) -> None:
        result = create_pdf_from_text("Test", font_size=16)
        assert result[:5] == b"%PDF-"

    def test_empty_content(self) -> None:
        result = create_pdf_from_text("")
        assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# create_pdf_from_html
# ---------------------------------------------------------------------------


class TestCreatePdfFromHtml:
    def test_basic_html(self) -> None:
        html = "<h1>Hello</h1><p>World</p>"
        result = create_pdf_from_html(html)
        assert result[:5] == b"%PDF-"

    def test_with_title(self) -> None:
        html = "<p>Content</p>"
        result = create_pdf_from_html(html, title="HTML Doc")
        assert result[:5] == b"%PDF-"

    def test_table_html(self) -> None:
        html = "<table><tr><th>Name</th><th>Value</th></tr><tr><td>A</td><td>1</td></tr></table>"
        result = create_pdf_from_html(html)
        assert result[:5] == b"%PDF-"

    def test_list_html(self) -> None:
        html = "<ul><li>Item 1</li><li>Item 2</li></ul>"
        result = create_pdf_from_html(html)
        assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# create_pdf_from_images
# ---------------------------------------------------------------------------


class TestCreatePdfFromImages:
    @pytest.mark.asyncio
    async def test_single_image(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images([sample_image_data_uri])
        assert result[:5] == b"%PDF-"
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) >= 1

    @pytest.mark.asyncio
    async def test_multiple_images(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images([sample_image_data_uri, sample_image_data_uri])
        assert result[:5] == b"%PDF-"
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) >= 2

    @pytest.mark.asyncio
    async def test_with_title(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images([sample_image_data_uri], title="Image Doc")
        assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# Phase 1.1: Layout options
# ---------------------------------------------------------------------------


class TestLayoutOptions:
    def test_landscape_orientation(self) -> None:
        result = create_pdf_from_text("Landscape test", orientation="landscape")
        assert result[:5] == b"%PDF-"

    def test_custom_margins(self) -> None:
        result = create_pdf_from_text(
            "Margins test",
            margin_top=25,
            margin_bottom=25,
            margin_left=30,
            margin_right=30,
        )
        assert result[:5] == b"%PDF-"

    def test_multi_column(self) -> None:
        long_text = "Lorem ipsum dolor sit amet. " * 100
        result = create_pdf_from_text(long_text, columns=2)
        assert result[:5] == b"%PDF-"

    def test_three_columns(self) -> None:
        long_text = "Column text. " * 200
        result = create_pdf_from_text(long_text, columns=3)
        assert result[:5] == b"%PDF-"

    def test_columns_clamped_to_three(self) -> None:
        result = create_pdf_from_text("Test", columns=5)
        assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# Phase 1.1: Headers and footers
# ---------------------------------------------------------------------------


class TestHeadersFooters:
    def test_header_text(self) -> None:
        result = create_pdf_from_text("Body", header_text="My Header")
        assert result[:5] == b"%PDF-"

    def test_footer_text(self) -> None:
        result = create_pdf_from_text("Body", footer_text="My Footer")
        assert result[:5] == b"%PDF-"

    def test_header_and_footer(self) -> None:
        result = create_pdf_from_text(
            "Body",
            header_text="Report Header",
            footer_text="Confidential",
            show_page_numbers=True,
        )
        assert result[:5] == b"%PDF-"
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) >= 1

    def test_no_page_numbers(self) -> None:
        result = create_pdf_from_text("Body", show_page_numbers=False)
        assert result[:5] == b"%PDF-"

    def test_html_with_headers(self) -> None:
        result = create_pdf_from_html(
            "<p>Hello</p>",
            header_text="HTML Header",
            footer_text="HTML Footer",
        )
        assert result[:5] == b"%PDF-"

    @pytest.mark.asyncio
    async def test_images_with_headers(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images(
            [sample_image_data_uri],
            header_text="Image Header",
            footer_text="Image Footer",
        )
        assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# Phase 1.1: Custom font path (invalid path raises)
# ---------------------------------------------------------------------------


class TestCustomFonts:
    def test_invalid_font_path_raises(self) -> None:
        with pytest.raises(ValueError, match="Font file not found"):
            create_pdf_from_text("Test", font_path="/nonexistent/font.ttf")

    def test_html_invalid_font_path_raises(self) -> None:
        with pytest.raises(ValueError, match="Font file not found"):
            create_pdf_from_html("<p>Test</p>", font_path="/nonexistent/font.ttf")


# ---------------------------------------------------------------------------
# Phase 1.1: Markdown improvements
# ---------------------------------------------------------------------------


class TestMarkdownImprovements:
    def test_markdown_with_columns(self) -> None:
        md = "# Title\n\nSome **bold** text.\n\n- item 1\n- item 2"
        result = create_pdf_from_text(md, is_markdown=True, columns=2)
        assert result[:5] == b"%PDF-"

    def test_markdown_with_toc(self) -> None:
        md = "# Chapter 1\n\nContent.\n\n## Section 1.1\n\nMore content.\n\n# Chapter 2\n\nFinal."
        result = create_pdf_from_text(md, is_markdown=True, table_of_contents=True)
        assert result[:5] == b"%PDF-"
        reader = PdfReader(io.BytesIO(result))
        assert len(reader.pages) >= 1

    def test_markdown_code_block(self) -> None:
        md = "# Code Example\n\n```python\ndef hello():\n    print('hi')\n```"
        result = create_pdf_from_text(md, is_markdown=True)
        assert result[:5] == b"%PDF-"

    def test_markdown_table(self) -> None:
        md = "| Name | Value |\n|------|-------|\n| A    | 1     |\n| B    | 2     |"
        result = create_pdf_from_text(md, is_markdown=True)
        assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# Phase 1.1: HTML layout options
# ---------------------------------------------------------------------------


class TestHtmlLayoutOptions:
    def test_html_landscape(self) -> None:
        result = create_pdf_from_html("<p>Landscape</p>", orientation="landscape")
        assert result[:5] == b"%PDF-"

    def test_html_custom_margins(self) -> None:
        result = create_pdf_from_html(
            "<p>Margins</p>",
            margin_top=20,
            margin_bottom=20,
            margin_left=25,
            margin_right=25,
        )
        assert result[:5] == b"%PDF-"


# ---------------------------------------------------------------------------
# Phase 1.1: Images layout options
# ---------------------------------------------------------------------------


class TestImagesLayoutOptions:
    @pytest.mark.asyncio
    async def test_images_landscape(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images([sample_image_data_uri], orientation="landscape")
        assert result[:5] == b"%PDF-"

    @pytest.mark.asyncio
    async def test_images_custom_margins(self, sample_image_data_uri: str) -> None:
        result = await create_pdf_from_images(
            [sample_image_data_uri],
            margin_top=20,
            margin_bottom=20,
            margin_left=25,
            margin_right=25,
        )
        assert result[:5] == b"%PDF-"
