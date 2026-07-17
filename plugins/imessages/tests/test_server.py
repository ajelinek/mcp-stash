"""In-memory tests for the mcp-stash-imessages FastMCP server."""

from fastmcp import Client
from mcp_stash_imessages.server import mcp


async def test_ping():
    async with Client(mcp) as client:
        result = await client.call_tool("ping", {})
        assert result.data == "pong"


async def test_check_imessage_db_access_shape():
    async with Client(mcp) as client:
        result = await client.call_tool("check_imessage_db_access", {})
        assert "path" in result.data
        assert "exists" in result.data
