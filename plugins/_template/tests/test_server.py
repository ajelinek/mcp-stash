from fastmcp import Client
from mcp_stash_template.server import mcp


async def test_ping():
    async with Client(mcp) as client:
        result = await client.call_tool("ping", {})
        assert result.data == "pong"


async def test_echo():
    async with Client(mcp) as client:
        result = await client.call_tool("echo", {"message": "hi"})
        assert result.data == "hi"
