#!/usr/bin/env python3
"""
Demo: chuk-mcp-pdf -- PDF Creation, Editing, and Viewing

Exercises all 8 tools through the ToolRunner harness (no transport needed).
Run directly:  python examples/demo.py
"""

import asyncio
import io
import json

from chuk_mcp_server.testing import ToolRunner
from pypdf import PdfReader

# Import the server so tools get registered
from chuk_mcp_pdf.server import mcp  # noqa: F401


def banner(title: str) -> None:
    print(f"\n{'=' * 60}")
    print(f"  {title}")
    print(f"{'=' * 60}")


def pdf_info(b64_url: str) -> dict:
    """Extract basic info from a base64 data URI PDF."""
    import base64

    _, b64 = b64_url.split(";base64,", 1)
    pdf_bytes = base64.b64decode(b64)
    reader = PdfReader(io.BytesIO(pdf_bytes))
    return {"pages": len(reader.pages), "size_kb": round(len(pdf_bytes) / 1024, 1)}


async def main() -> None:
    runner = ToolRunner(server=mcp)

    # ----------------------------------------------------------------
    # 0. List available tools
    # ----------------------------------------------------------------
    banner("Available Tools")
    tools = await runner.list_tools()
    for t in tools:
        print(f"  {t['name']:30s}  {t.get('description', '')[:60]}")

    # ----------------------------------------------------------------
    # 1. show_pdf -- display an existing PDF by URL
    # ----------------------------------------------------------------
    banner("1. show_pdf")
    result = await runner.call_tool(
        "show_pdf",
        {
            "url": "https://www.w3.org/WAI/ER/tests/xhtml/testfiles/resources/pdf/dummy.pdf",
            "title": "W3C Test PDF",
            "initial_page": 1,
        },
    )
    sc = result["result"]["structuredContent"]
    print(f"  type={sc['type']}  version={sc['version']}")
    print(f"  url={sc['url'][:70]}...")
    print(f"  title={sc.get('title')}")

    # ----------------------------------------------------------------
    # 2. create_pdf_from_text -- plain text
    # ----------------------------------------------------------------
    banner("2. create_pdf_from_text (plain)")
    result = await runner.call_tool(
        "create_pdf_from_text",
        {
            "content": (
                "The quick brown fox jumps over the lazy dog.\n\n"
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. "
                "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris."
            ),
            "title": "Plain Text Demo",
            "font_size": 14,
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Generated PDF: {info['pages']} page(s), {info['size_kb']} KB")

    # ----------------------------------------------------------------
    # 3. create_pdf_from_text -- markdown
    # ----------------------------------------------------------------
    banner("3. create_pdf_from_text (markdown)")
    result = await runner.call_tool(
        "create_pdf_from_text",
        {
            "content": "\n".join(
                [
                    "# Project Status Report",
                    "",
                    "## Summary",
                    "",
                    "The project is **on track** for the Q2 release.",
                    "",
                    "### Key Metrics",
                    "",
                    "- Tests passing: *63/63*",
                    "- Code coverage: **99%**",
                    "- Open issues: 0",
                    "",
                    "## Next Steps",
                    "",
                    "1. Deploy to staging",
                    "2. Run integration tests",
                    "3. Release candidate build",
                ]
            ),
            "title": "Status Report",
            "markdown": True,
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Generated PDF: {info['pages']} page(s), {info['size_kb']} KB")

    # ----------------------------------------------------------------
    # 4. create_pdf_from_html
    # ----------------------------------------------------------------
    banner("4. create_pdf_from_html")
    result = await runner.call_tool(
        "create_pdf_from_html",
        {
            "html": """
        <h1>Invoice #2024-001</h1>
        <p>Date: March 3, 2026</p>
        <table border="1" cellpadding="5">
          <tr><th>Item</th><th>Qty</th><th>Price</th></tr>
          <tr><td>Widget A</td><td>10</td><td>$25.00</td></tr>
          <tr><td>Widget B</td><td>5</td><td>$40.00</td></tr>
          <tr><td>Shipping</td><td>1</td><td>$15.00</td></tr>
        </table>
        <p><b>Total: $465.00</b></p>
        """,
            "title": "Invoice",
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Generated PDF: {info['pages']} page(s), {info['size_kb']} KB")

    # ----------------------------------------------------------------
    # 5. create_pdf_from_images
    # ----------------------------------------------------------------
    banner("5. create_pdf_from_images")
    # Create two small test images as base64 data URIs
    from PIL import Image
    import base64

    images = []
    for color, label in [((70, 130, 180), "blue"), ((220, 80, 60), "red")]:
        img = Image.new("RGB", (200, 200), color=color)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        b64 = base64.b64encode(buf.getvalue()).decode()
        images.append(f"data:image/png;base64,{b64}")

    result = await runner.call_tool(
        "create_pdf_from_images",
        {
            "images": json.dumps(images),
            "title": "Color Swatches",
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Generated PDF: {info['pages']} page(s), {info['size_kb']} KB")

    # ----------------------------------------------------------------
    # 6. merge_pdfs
    # ----------------------------------------------------------------
    banner("6. merge_pdfs")

    # Create two small PDFs to merge
    from fpdf import FPDF

    pdfs_b64 = []
    for label in ["Document A", "Document B"]:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", size=24)
        pdf.cell(0, 40, label, align="C")
        pdf.add_page()
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"Content of {label}")
        b64 = base64.b64encode(pdf.output()).decode()
        pdfs_b64.append(f"data:application/pdf;base64,{b64}")

    result = await runner.call_tool(
        "merge_pdfs",
        {
            "sources": json.dumps(pdfs_b64),
            "title": "Merged Document",
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Merged PDF: {info['pages']} page(s), {info['size_kb']} KB")
    print(f"  (2 docs x 2 pages = {info['pages']} pages)")

    # ----------------------------------------------------------------
    # 7. split_pdf -- split the merged doc back apart
    # ----------------------------------------------------------------
    banner("7. split_pdf")
    result = await runner.call_tool(
        "split_pdf",
        {
            "source": url,
            "page_ranges": json.dumps(["1-2", "3-4"]),
            "view_part": 1,
        },
    )
    sc = result["result"]["structuredContent"]
    split_info = pdf_info(sc["url"])
    print(f"  Split part 1: {split_info['pages']} page(s)")
    print(f"  title: {sc.get('title')}")

    result = await runner.call_tool(
        "split_pdf",
        {
            "source": url,
            "page_ranges": json.dumps(["1-2", "3-4"]),
            "view_part": 2,
        },
    )
    split_info = pdf_info(result["result"]["structuredContent"]["url"])
    print(f"  Split part 2: {split_info['pages']} page(s)")

    # ----------------------------------------------------------------
    # 8. extract_text
    # ----------------------------------------------------------------
    banner("8. extract_text")
    result = await runner.call_tool(
        "extract_text",
        {
            "source": url,
            "page_range": "1,3",
        },
    )
    text = result["result"]["content"][0]["text"]
    # Show first 200 chars
    preview = text[:200].replace("\n", "\n  ")
    print(f"  {preview}...")

    # ----------------------------------------------------------------
    # 9. add_watermark
    # ----------------------------------------------------------------
    banner("9. add_watermark")
    result = await runner.call_tool(
        "add_watermark",
        {
            "source": url,
            "watermark_text": "CONFIDENTIAL",
            "opacity": 0.2,
            "page_range": "1,3",
        },
    )
    wm_url = result["result"]["structuredContent"]["url"]
    wm_info = pdf_info(wm_url)
    print(f"  Watermarked PDF: {wm_info['pages']} page(s), {wm_info['size_kb']} KB")
    print("  Watermark 'CONFIDENTIAL' applied to pages 1 and 3")

    # ================================================================
    # Phase 1.1 demos: Layout, headers/footers, columns, TOC
    # ================================================================

    # ----------------------------------------------------------------
    # 10. Landscape with headers/footers
    # ----------------------------------------------------------------
    banner("10. Landscape + Headers/Footers")
    result = await runner.call_tool(
        "create_pdf_from_text",
        {
            "content": (
                "This document demonstrates landscape orientation with custom "
                "headers and footers. The header shows the document title and "
                "the footer shows page numbers.\n\n"
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
                "Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. " * 5
            ),
            "title": "Landscape Demo",
            "orientation": "landscape",
            "header_text": "Quarterly Report - Q1 2026",
            "footer_text": "Confidential",
            "show_page_numbers": True,
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Generated PDF: {info['pages']} page(s), {info['size_kb']} KB")
    print("  orientation=landscape, header='Quarterly Report', footer='Confidential'")

    # ----------------------------------------------------------------
    # 11. Multi-column text
    # ----------------------------------------------------------------
    banner("11. Multi-Column Text")
    result = await runner.call_tool(
        "create_pdf_from_text",
        {
            "content": ("This text is rendered in two columns, like a newspaper. " * 40),
            "title": "Two-Column Layout",
            "columns": 2,
            "margin_left": 15,
            "margin_right": 15,
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Generated PDF: {info['pages']} page(s), {info['size_kb']} KB")
    print("  columns=2, custom margins")

    # ----------------------------------------------------------------
    # 12. Markdown with Table of Contents
    # ----------------------------------------------------------------
    banner("12. Markdown with TOC")
    result = await runner.call_tool(
        "create_pdf_from_text",
        {
            "content": "\n".join(
                [
                    "# Chapter 1: Introduction",
                    "",
                    "Welcome to this document with a table of contents.",
                    "",
                    "## 1.1 Background",
                    "",
                    "Some background information here.",
                    "",
                    "## 1.2 Objectives",
                    "",
                    "- Objective A",
                    "- Objective B",
                    "- Objective C",
                    "",
                    "# Chapter 2: Implementation",
                    "",
                    "The implementation details follow.",
                    "",
                    "## 2.1 Architecture",
                    "",
                    "The system uses a **modular** design.",
                    "",
                    "## 2.2 Testing",
                    "",
                    "All 91 tests pass with full coverage.",
                    "",
                    "# Chapter 3: Conclusion",
                    "",
                    "The project is *complete* and ready for deployment.",
                ]
            ),
            "title": "Document with TOC",
            "markdown": True,
            "table_of_contents": True,
            "header_text": "Technical Specification",
            "footer_text": "Draft v0.2",
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Generated PDF: {info['pages']} page(s), {info['size_kb']} KB")
    print("  markdown=True, table_of_contents=True, headers/footers")

    # ----------------------------------------------------------------
    # 13. HTML with layout options
    # ----------------------------------------------------------------
    banner("13. HTML with Layout Options")
    result = await runner.call_tool(
        "create_pdf_from_html",
        {
            "html": """
        <h1>Sales Report</h1>
        <p>Period: January - March 2026</p>
        <table border="1" cellpadding="5">
          <tr><th>Region</th><th>Q1 Sales</th><th>Growth</th></tr>
          <tr><td>North</td><td>$1,250,000</td><td>+12%</td></tr>
          <tr><td>South</td><td>$980,000</td><td>+8%</td></tr>
          <tr><td>East</td><td>$1,100,000</td><td>+15%</td></tr>
          <tr><td>West</td><td>$870,000</td><td>+5%</td></tr>
        </table>
        <p><b>Total: $4,200,000</b> (overall growth: +10%)</p>
        """,
            "title": "Sales Report",
            "orientation": "landscape",
            "header_text": "ACME Corp - Internal Use Only",
            "footer_text": "Finance Department",
            "margin_top": 20,
            "margin_bottom": 20,
        },
    )
    url = result["result"]["structuredContent"]["url"]
    info = pdf_info(url)
    print(f"  Generated PDF: {info['pages']} page(s), {info['size_kb']} KB")
    print("  landscape HTML with headers/footers and custom margins")

    # ----------------------------------------------------------------
    # Done
    # ----------------------------------------------------------------
    banner("Demo Complete")
    print("  All tools exercised successfully (8 core + 4 Phase 1.1 demos).")
    print("  Run as MCP server:  chuk-mcp-pdf")
    print("  Run HTTP mode:      chuk-mcp-pdf http")
    print()


if __name__ == "__main__":
    asyncio.run(main())
