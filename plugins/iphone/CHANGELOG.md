# Changelog

## 0.1.0 - 2026-07-18

- Initial release, replacing the `imessages` and `iphone-history` placeholder
  plugins with one consolidated plugin.
- `imessage_*` tools: `doctor`, `chats`, `recent`, `messages`, `search`,
  `resolve_chat`, `send` (preview-then-confirm), `get_attachment`,
  `trusted_list`/`add`/`remove`/`suggest` — ported from the `imessage` skill's
  tested `imessage_cli.py` reference implementation.
- `calls_*` tools: `doctor`, `list` — ported from the `icallhistory` skill's
  tested `icallhistory_cli.py` reference implementation.
- Shared `contacts` tool (local AddressBook resolution) used by both.
- Trusted-contacts allow-list persisted under `~/.mcp-stash/iphone/`, not
  inside the plugin's own install directory.
