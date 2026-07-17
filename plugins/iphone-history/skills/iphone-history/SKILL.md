---
name: iphone-history
description: Use to sanity-check that the mcp-stash iphone-history plugin's MCP server is installed and reachable, and to report whether the local iPhone backup directory is visible on this machine. This is a placeholder/test plugin — it does not read backup content.
---

# iPhone History Plugin Skill (placeholder)

This skill pairs with the `iphone-history` plugin's bundled MCP server
(`plugin:iphone-history:iphone-history`), which exposes two tools:

- `ping()` - trivial stdio connectivity smoke test, returns `"pong"`.
- `check_iphone_backup_access()` - reports whether
  `~/Library/Application Support/MobileSync/Backup` exists on this
  machine, plus basic metadata. It never reads any backup content.

## When to use this skill

Use it when asked to verify the `iphone-history` plugin is installed
and working, or to check whether this machine has local iPhone backups
at all (useful groundwork before any real history-reading feature is
built). Report the `exists` field plainly; do not imply any backup
content has been read, because none has.
