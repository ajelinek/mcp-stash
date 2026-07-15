"""Minimal starting point for a new mcp-stash plugin's FastMCP server."""

from __future__ import annotations

from fastmcp import FastMCP

mcp = FastMCP(
    name="mcp-stash-template",
    instructions="Minimal starting point for a new mcp-stash plugin. Replace these tools.",
)


@mcp.tool
def ping() -> str:
    """Health-check tool: always returns 'pong'."""
    return "pong"


@mcp.tool
def echo(message: str) -> str:
    """Echo back whatever message is passed in."""
    return message
