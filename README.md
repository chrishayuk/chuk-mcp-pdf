# chuk-mcp-pdf

MCP server for creating, editing, and viewing PDF documents.

## Tools

### Creation
| Tool | Description |
|------|-------------|
| `create_pdf_from_text` | Convert plain text or markdown to a styled PDF |
| `create_pdf_from_html` | Render HTML content into a PDF |
| `create_pdf_from_images` | Combine one or more images into a PDF |

### Editing
| Tool | Description |
|------|-------------|
| `merge_pdfs` | Merge multiple PDFs into one document |
| `split_pdf` | Split a PDF into parts by page ranges |
| `extract_text` | Extract text content from PDF pages |
| `add_watermark` | Add text or image watermark to PDF pages |

### Viewing
| Tool | Description |
|------|-------------|
| `show_pdf` | Display a PDF in the interactive viewer |

## Quick Start

```bash
# Install
pip install chuk-mcp-pdf

# Run (STDIO mode for MCP clients)
chuk-mcp-pdf

# Run (HTTP mode)
chuk-mcp-pdf http
```

### Claude Desktop Configuration

```json
{
  "mcpServers": {
    "pdf": {
      "command": "uvx",
      "args": ["chuk-mcp-pdf"]
    }
  }
}
```

## Optional Dependencies

```bash
# Markdown support for create_pdf_from_text(markdown=True)
pip install chuk-mcp-pdf[markdown]

# Full CSS support for create_pdf_from_html (requires cairo/pango)
pip install chuk-mcp-pdf[html]

# All optional features
pip install chuk-mcp-pdf[all]
```

## Development

```bash
make dev-install   # Install with dev dependencies
make test          # Run tests
make check         # Run all checks (lint, typecheck, security, test)
make run           # Run the server
```
