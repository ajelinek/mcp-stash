# chat.db schema reference

`~/Library/Messages/chat.db` is a plain SQLite database. The `imessage_*` tools
open it read-only (`file:...?mode=ro`) and never write to it. Only the columns
these tools actually query are documented here — see the sources below for the
rest.

Sources: [Atomic Object's chat.db walkthrough](https://spin.atomicobject.com/search-imessage-sql/),
cross-checked against the `db.ts` in both
[daveremy/imessage-mcp](https://github.com/daveremy/imessage-mcp) and
[anipotts/imessage-mcp](https://github.com/anipotts/imessage-mcp), and against
Anthropic's own official channel plugin at
[anthropics/claude-plugins-official/external_plugins/imessage](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage).

## Tables

| Table | Purpose |
|---|---|
| `message` | One row per message (sent or received). |
| `chat` | One row per conversation (1:1 or group). |
| `handle` | One row per contact address (phone number or Apple ID email) ever seen. |
| `chat_message_join` | `(chat_id, message_id)` — many-to-many, but a message is practically always in exactly one chat. |
| `chat_handle_join` | `(chat_id, handle_id)` — which handles participate in which chat. A chat with exactly one row here is a 1:1 DM; more than one is a group. |
| `attachment` | One row per attachment; `filename` is an absolute filesystem path. |
| `message_attachment_join` | `(message_id, attachment_id)`. |

## Key columns

**`message`**
- `ROWID` — internal integer PK, used for joins and pagination cursors.
- `guid` — stable string identifier, exposed as `message_guid`.
- `text` — plain-text body, or `NULL` on macOS 14+ if the text lives in `attributedBody` instead (see `attributed-body.md`).
- `attributedBody` — `BLOB`, NSArchiver-encoded `NSAttributedString`.
- `handle_id` — FK to `handle.ROWID`. `0`/absent when `is_from_me = 1`.
- `is_from_me` — `0` or `1`.
- `date` — Apple-epoch nanoseconds (see below). Also `date_read`, `date_delivered`,
  `date_edited`, `date_retracted` (unused by this plugin — see SKILL.md's
  "Known limitations").
- `cache_has_attachments` — `0`/`1`, cheap pre-check before joining `attachment`.
- `associated_message_type` — `0` for a normal message; non-zero marks tapback
  reactions and other synthetic associated messages. `imessage_*` tools filter
  `!= 0` out by default (`include_reactions=True` opts back in) and decode the
  known codes into a `reaction_type` field — see `server.py`'s
  `REACTION_TYPE_NAMES`.

**`chat`**
- `ROWID`, `guid` — `guid` is what `imessage_send`'s `chat_guid` (and
  AppleScript's `chat id`) expect. Format observed: `iMessage;-;+15551234567` for a
  1:1 DM, `iMessage;+;chat<hash>` for a group (matching the official Anthropic
  imessage plugin's own chat.db guid format for its sends).
- `display_name` — set for named group chats, `NULL` for DMs and unnamed groups.

**`handle`**
- `ROWID`, `id` — the handle address itself (`+15551234567` or `someone@icloud.com`).

## Apple epoch date conversion

`message.date` (and the other date columns) are nanoseconds since
`2001-01-01T00:00:00Z`, not the Unix epoch:

```python
APPLE_EPOCH_OFFSET = 978307200  # 2001-01-01 00:00:00 UTC in Unix seconds
unix_seconds = apple_ns / 1_000_000_000 + APPLE_EPOCH_OFFSET
```

`server.py`'s `apple_ns_to_dt`/`dt_to_apple_ns` implement this both ways (the
reverse direction is needed to turn a parsed `since`/`until` argument into a
value usable in a `WHERE date >= ?` clause). Note this is **not** the same unit
CallHistory.storedata uses for calls — see the `icallhistory` skill's own
`references/schema.md`.

## Example join (chats + messages + handles)

```sql
SELECT m.text, c.guid, h.id, m.is_from_me
FROM message m
JOIN chat_message_join cmj ON cmj.message_id = m.ROWID
JOIN chat c ON c.ROWID = cmj.chat_id
LEFT JOIN handle h ON h.ROWID = m.handle_id
WHERE m.associated_message_type = 0
ORDER BY m.date DESC;
```
