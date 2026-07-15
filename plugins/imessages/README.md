# imessages (mcp-stash placeholder/test plugin)

Placeholder plugin proving the mcp-stash pattern end to end: packaging,
GitHub marketplace install, stdio connection, and read-only local
filesystem access. It does **not** read iMessage content — it only
reports whether `~/Library/Messages/chat.db` exists and basic metadata.

## Prerequisites

The machine needs `uv` installed and on `PATH`
(https://docs.astral.sh/uv/getting-started/installation/).

## Install

In Claude Desktop: **Customize → Plugins → (+) → Add marketplace**,
enter `ajelinek/mcp-stash`, then install `imessages` from the list.
(Equivalent commands also work in a Desktop or Cowork chat window:
`/plugin marketplace add ajelinek/mcp-stash` then
`/plugin install imessages@mcp-stash`.)

Ask Claude to "ping the imessages plugin" or "check iMessage db access"
to exercise the two tools.

## What's inside

- `.claude-plugin/plugin.json` / `.mcp.json` - plugin + MCP server manifest.
- `fastmcp.json` - local dev only, not used by the installed plugin.
- `skills/imessages/SKILL.md` - usage guidance for Claude.
- `src/mcp_stash_imessages/` - the placeholder FastMCP server.
- `src/mcp_stash_common` - symlink to the repo's shared helpers.
- `tests/test_server.py` - in-memory tests (`uv run pytest` from repo root).
