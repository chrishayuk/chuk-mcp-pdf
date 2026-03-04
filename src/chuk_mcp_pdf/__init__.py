"""chuk-mcp-pdf — PDF creation, editing, and viewing MCP server."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("chuk-mcp-pdf")
except PackageNotFoundError:
    __version__ = "0.0.0"
