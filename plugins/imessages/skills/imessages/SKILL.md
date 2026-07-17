---
name: imessages
description: Use to sanity-check that the mcp-stash imessages plugin's MCP server is installed and reachable, and to report whether the local iMessage database is visible on this machine. This is a placeholder/test plugin — it does not read message content.
---

# iMessages Plugin Skill (placeholder)

This skill pairs with the `imessages` plugin's bundled MCP server
(`plugin:imessages:imessages`), which exposes two tools:

- `ping()` - trivial stdio connectivity smoke test, returns `"pong"`.
- `check_imessage_db_access()` - reports whether
  `~/Library/Messages/chat.db` exists on this machine, plus basic
  metadata (size, last-modified time, readable). It never opens or
  reads the database itself.

## When to use this skill

Use it when asked to verify the `imessages` plugin is installed and
working, or to check whether this machine has a local iMessage database
at all (useful groundwork before any real message-reading feature is
built). Report the `exists`/`readable` fields plainly; do not imply any
message content has been read, because none has.
