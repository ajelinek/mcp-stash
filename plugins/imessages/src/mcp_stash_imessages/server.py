"""Placeholder FastMCP server for the mcp-stash 'imessages' plugin.

Deliberately does nothing beyond proving stdio connectivity and
read-only, metadata-only local filesystem access. Does not open or
parse the iMessage database.
"""

from __future__ import annotations

from fastmcp import FastMCP
from mcp_stash_common import check_path, get_logger

logger = get_logger("mcp-stash-imessages")

IMESSAGE_DB_PATH = "~/Library/Messages/chat.db"

mcp = FastMCP(
    name="mcp-stash-imessages",
    instructions=(
        "Placeholder/test MCP server for the 'imessages' plugin. Proves "
        "packaging, installation, and read-only local filesystem access. "
        "Does not read message content."
    ),
)


@mcp.tool
def ping() -> str:
    """Trivial stdio connectivity smoke test."""
    logger.info("ping called")
    return "pong"


@mcp.tool
def check_imessage_db_access() -> dict:
    """Report whether the local iMessage database exists and its metadata.

    Never opens or reads the database — existence/size/modified-time/
    readability only.
    """
    result = check_path(IMESSAGE_DB_PATH)
    logger.info("check_imessage_db_access -> %s", result)
    return result
