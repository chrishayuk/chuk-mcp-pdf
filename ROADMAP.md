# chuk-mcp-pdf Roadmap

## Current State (v0.2.0)

**Working:** 8 tools for creating, editing, and viewing PDF documents — text/markdown to PDF, HTML to PDF, image compilation, merge, split, text extraction, watermarking, and interactive viewing.

**Phase 1.1 additions:** Custom fonts (TTF/OTF via path), page layout (orientation, margins, headers/footers, multi-column), table of contents generation from markdown headings.

**Test Stats:** 91 tests, all passing. All checks pass (ruff, mypy, bandit, pytest).

**Infrastructure:** pyproject.toml, Makefile, Dockerfile, examples/demo.py, CI-ready.

**Implemented:** `show_pdf` (display PDF by URL or base64 data URI), `create_pdf_from_text` (plain text or markdown with headings, bold, italic, lists, tables, TOC, multi-column, headers/footers), `create_pdf_from_html` (HTML with tables, lists, headings — full CSS via optional weasyprint, headers/footers), `create_pdf_from_images` (one image per page from URLs or data URIs, headers/footers), `merge_pdfs` (concatenate multiple PDFs), `split_pdf` (split by page ranges with selectable view part), `extract_text` (text extraction with page separators), `add_watermark` (diagonal text watermark with configurable opacity and page targeting). Dual delivery: base64 data URIs for small PDFs, HTTP file serving for large PDFs in HTTP mode. Pure Python core — fpdf2 + pypdf, no system dependencies required.

---

## Phase 1.0: Core PDF Tools (v0.1.0) -- COMPLETE

### 1.0.1 Project Infrastructure

- [x] Create `pyproject.toml` with dependencies (fpdf2, pypdf, httpx)
- [x] Create `Makefile` with full target set (test, lint, format, typecheck, security, check)
- [x] Add `Dockerfile` (multi-stage, python:3.14-slim)
- [x] Add `README.md` with tool reference
- [x] Add `ROADMAP.md` — this document
- [x] Add `examples/demo.py` — exercises all 8 tools via ToolRunner

### 1.0.2 Creation Tools (3 tools)

- [x] `create_pdf_from_text` — plain text or markdown to PDF (fpdf2 + optional markdown lib)
- [x] `create_pdf_from_html` — HTML to PDF (fpdf2 basic, weasyprint optional for full CSS)
- [x] `create_pdf_from_images` — combine images into multi-page PDF

### 1.0.3 Editing Tools (4 tools)

- [x] `merge_pdfs` — concatenate multiple PDFs in order
- [x] `split_pdf` — split by page ranges, select which part to view
- [x] `extract_text` — extract text with page separators (plain text return, not PDF view)
- [x] `add_watermark` — diagonal text watermark with opacity control

### 1.0.4 Viewing Tool

- [x] `show_pdf` — display PDF by URL or base64 data URI via PdfContent

### 1.0.5 Delivery System

- [x] Base64 data URI encoding for small/medium PDFs
- [x] HTTP file serving endpoint (`/pdf-files/{token}`) for large PDFs in HTTP mode
- [x] Size-based auto-selection (5 MB threshold)
- [x] JSON string/list duality for array parameters (LLM resilience)

### 1.0.6 Tests & Demo

- [x] 63 tests across 4 test files (helpers, create, edit, server integration)
- [x] `examples/demo.py` — full ToolRunner demo exercising all 8 tools

---

## Phase 1.1: Enhanced Text & Formatting (v0.2.0) -- COMPLETE

Improved PDF creation quality with more formatting control.

### 1.1.1 Custom Fonts

- [x] Support custom font files (TTF/OTF) via `font_family` + `font_path` parameters
- [x] Auto-detect bold/italic variants by naming convention
- [ ] Bundle 2-3 open-source fonts (e.g. Inter, JetBrains Mono, Noto Serif)
- [ ] CJK character support via Noto CJK font

### 1.1.2 Page Layout Options

- [x] Header/footer support (page numbers, custom text)
- [x] Configurable margins (top, bottom, left, right)
- [x] Landscape orientation option
- [x] Multi-column layout for plain text (2-3 columns)

### 1.1.3 Markdown Improvements

- [x] Code block rendering via fenced_code extension
- [x] Table rendering via tables extension
- [x] Table of contents generation from headings

### 1.1.4 Tests

- [x] Custom font path validation tests
- [x] Layout option tests (margins, orientation, columns)
- [x] Markdown rendering tests (TOC, code blocks, tables)
- [x] Header/footer tests across all creation tools
- [x] Server integration tests for all new parameters

---

## Phase 1.2: Form & Template Support (v0.3.0)

Enable generating PDFs from structured data using templates.

### 1.2.1 Template Engine

- [ ] `create_pdf_from_template` tool — fill a template with data
- [ ] Jinja2-style variable substitution in HTML templates
- [ ] Repeating sections (e.g. invoice line items, report rows)
- [ ] Conditional sections (show/hide based on data values)

### 1.2.2 Common Templates

- [ ] Invoice template (header, line items, totals, footer)
- [ ] Report template (title page, sections, charts placeholder)
- [ ] Letter template (letterhead, body, signature block)
- [ ] Certificate template (decorative border, name, date)

### 1.2.3 Tests

- [ ] Template variable substitution tests
- [ ] Repeating section tests with varying row counts
- [ ] Missing variable handling (graceful defaults)

---

## Phase 2.0: Advanced Editing (v0.4.0)

Expand editing capabilities for more complex PDF workflows.

### 2.0.1 Page Manipulation

- [ ] `rotate_pages` tool — rotate pages by 90/180/270 degrees
- [ ] `reorder_pages` tool — rearrange page order
- [ ] `delete_pages` tool — remove specific pages
- [ ] `insert_pages` tool — insert pages from one PDF into another at a position

### 2.0.2 Content Overlay

- [ ] Image watermark support (logo overlay, stamp)
- [ ] Header/footer injection on existing PDFs
- [ ] Page number stamping on unnumbered documents
- [ ] Bates numbering for legal documents

### 2.0.3 Metadata

- [ ] `get_pdf_info` tool — return page count, metadata, file size, encryption status
- [ ] `set_pdf_metadata` tool — update title, author, subject, keywords

### 2.0.4 Tests

- [ ] Page manipulation preserves content
- [ ] Overlay positioning tests
- [ ] Metadata round-trip tests

---

## Phase 2.1: Security & Protection (v0.5.0)

Add PDF security features for sensitive documents.

### 2.1.1 Encryption

- [ ] `encrypt_pdf` tool — password-protect a PDF (owner + user passwords)
- [ ] `decrypt_pdf` tool — remove password protection (given correct password)
- [ ] Permission control (print, copy, edit restrictions)

### 2.1.2 Digital Signatures

- [ ] `sign_pdf` tool — apply a digital signature
- [ ] `verify_signature` tool — check signature validity
- [ ] Certificate-based signing support

### 2.1.3 Redaction

- [ ] `redact_text` tool — permanently remove text from specified regions
- [ ] Pattern-based redaction (e.g. redact all email addresses, phone numbers)

### 2.1.4 Tests

- [ ] Encryption/decryption round-trip tests
- [ ] Permission enforcement tests
- [ ] Redaction completeness tests (text fully removed, not just hidden)

---

## Phase 3.0: Conversion & OCR (v0.6.0)

Expand input/output format support.

### 3.0.1 Format Conversion

- [ ] `pdf_to_images` tool — render PDF pages as PNG/JPEG images
- [ ] `pdf_to_html` tool — convert PDF to HTML (preserving layout)
- [ ] `pdf_to_markdown` tool — convert PDF to markdown text
- [ ] Support for DOCX/PPTX input (via python-docx, python-pptx)

### 3.0.2 OCR

- [ ] `ocr_pdf` tool — extract text from scanned/image PDFs
- [ ] Language detection and multi-language support
- [ ] Searchable PDF output (text layer over images)

### 3.0.3 Tests

- [ ] Format conversion fidelity tests
- [ ] OCR accuracy tests against known documents
- [ ] Round-trip: PDF → images → PDF preserves visual content

---

## Architecture: Composition with Sibling Servers

The PDF server has **no dependencies** on other MCP servers. It is designed to be composed at runtime by the LLM:

```
LLM (orchestrator)
 ├── chart server    →  show_chart(data=...)           →  chart image URL
 ├── weather server  →  get_weather_forecast("London") →  { temp, humidity, ... }
 ├── data server     →  query_database(sql=...)        →  { rows: [...] }
 └── pdf server      →  create_pdf_from_html(html=...) →  formatted report PDF
```

The LLM gathers data from any source, composes HTML or text, and calls the PDF server to generate the document. The PDF viewer in chuk-mcp-ui handles display automatically.

## Dependencies

| Install | Adds | What |
|---------|------|------|
| `chuk-mcp-pdf` | chuk-mcp-server, chuk-view-schemas, fpdf2, pypdf, httpx | All 8 tools |
| `chuk-mcp-pdf[markdown]` | + markdown | Markdown formatting in create_pdf_from_text |
| `chuk-mcp-pdf[html]` | + weasyprint | Full CSS support in create_pdf_from_html |
| `chuk-mcp-pdf[all]` | + markdown, weasyprint | Everything |

No system dependencies required for core functionality. weasyprint (optional) needs cairo and pango.

---

## Version Summary

| Version | Key Deliverables |
|---------|------------------|
| 0.1.0 | Initial release: 8 tools (3 creation, 4 editing, 1 viewing), dual delivery, demo. 63 tests. |
| 0.2.0 | Phase 1.1: Custom fonts, page layout options, markdown improvements. 91 tests. |
| 0.3.0 | Phase 1.2: Template engine, common document templates. |
| 0.4.0 | Phase 2.0: Page manipulation, content overlay, metadata tools. |
| 0.5.0 | Phase 2.1: Encryption, digital signatures, redaction. |
| 0.6.0 | Phase 3.0: Format conversion (PDF to images/HTML/markdown), OCR. |

---

*Last updated: 2026-03*
