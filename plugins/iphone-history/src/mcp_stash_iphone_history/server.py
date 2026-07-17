"""Placeholder FastMCP server for the mcp-stash 'iphone-history' plugin.

Deliberately does nothing beyond proving stdio connectivity and
read-only, metadata-only local filesystem access. Does not read any
backup content.
"""

from __future__ import annotations

from fastmcp import FastMCP
from mcp_stash_common import check_path, get_logger

logger = get_logger("mcp-stash-iphone-history")

IPHONE_BACKUP_PATH = "~/Library/Application Support/MobileSync/Backup"

mcp = FastMCP(
    name="mcp-stash-iphone-history",
    instructions=(
        "Placeholder/test MCP server for the 'iphone-history' plugin. "
        "Proves packaging, installation, and read-only local filesystem "
        "access. Does not read backup content."
    ),
)


@mcp.tool
def ping() -> str:
    """Trivial stdio connectivity smoke test."""
    logger.info("ping called")
    return "pong"


@mcp.tool
def check_iphone_backup_access() -> dict:
    """Report whether the local iPhone backup directory exists and its metadata.

    Never reads backup contents — existence/size/modified-time/
    readability only.
    """
    result = check_path(IPHONE_BACKUP_PATH)
    logger.info("check_iphone_backup_access -> %s", result)
    return result
