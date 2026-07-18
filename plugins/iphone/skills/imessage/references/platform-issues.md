# Known platform issues

## Full Disk Access (TCC)

`chat.db` is protected by macOS's TCC (Transparency, Consent, and Control) system.
The app actually running the MCP server — Claude Desktop, or the terminal/IDE
running Claude Code — needs **Full Disk Access**:

System Settings -> Privacy & Security -> Full Disk Access -> add that app -> restart
the app.

Without it, `sqlite3.connect(..., uri=True)` in read-only mode raises
`sqlite3.OperationalError` (typically `unable to open database file` or
`authorization denied`). `server.py`'s `open_chat_db()` catches this and raises a
clear error pointing at the fix; `imessage_doctor` surfaces it as
`chat_db_readable: false`.

**Claude Code specific gotcha**: granting Full Disk Access to `Claude.app` does
not necessarily cover its embedded CLI binary, and because that binary's path is
version-specific, a Claude Code update can silently invalidate a previously-working
Full Disk Access grant — `imessage_doctor` will suddenly start reporting
`chat_db_readable: false` again with no other change on the user's part. If reads
that used to work stop working right after an update, re-add the exact current
binary path under Full Disk Access rather than assuming the grant is gone for good.

## Transient "database is locked" errors

`chat.db` is under SQLite's WAL mode and Messages.app can be mid-checkpoint when a
read happens. `_open_readonly_db` retries briefly (two short backoff delays) on an
`OperationalError` whose message mentions "locked" or "busy" before giving up — this
is not a permissions problem and normally clears in well under a second.

## AddressBook access

Contact name resolution reads
`~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb` — also
a plain SQLite file, also covered by Full Disk Access. If it's unreadable or
missing, this plugin degrades gracefully: handles are shown as raw phone
numbers/emails instead of names, and `imessage_doctor` reports
`address_book_found: false` as a warning, not a failure — name resolution is a
nice-to-have, not a hard requirement to use these tools.

## Automation permission (TCC) for sending

`imessage_send` never touches chat.db — it shells out to `osascript`, which tells
Messages.app to deliver the text via AppleScript's `tell application "Messages" to
send`. macOS gates this separately from Full Disk Access: the first `imessage_send`
call in a session (or after an OS update) triggers an **Automation** permission
prompt for whatever app is running the MCP server ("Terminal wants to control
Messages.app" or similar). If the user dismissed or never saw that prompt,
`osascript` exits nonzero and `send_via_applescript()` raises with the fix pointer:

System Settings -> Privacy & Security -> Automation -> find the app running the MCP
server -> enable Messages.

A denied/missing grant here does not affect `imessage_doctor` or any read tool —
Full Disk Access and Automation are independent TCC checks.

## iCloud multi-device sync

`chat.db` only contains what has synced to **this** Mac. If "Messages in iCloud" is
off (or a different Mac was primary), a Mac that's new to your account, or one where
Messages.app hasn't been open continuously, may only have a partial — or very
shallow — local history. It does **not** inherit another Mac's full history just by
being signed into the same Apple ID; it accumulates going forward from whenever
Messages.app was running on this device. Relatedly, what's visible in Messages.app
itself isn't guaranteed to match chat.db exactly — older history can be offloaded to
iCloud-only storage even while it still displays in the app.

`imessage_doctor` heuristically flags this: if the earliest message in chat.db is
less than 90 days old, it emits a warning suggesting the user check whether
"Messages in iCloud" is enabled and fully synced (initial sync of a large history
can reportedly take 1-2 days). This is a heuristic, not a certainty — a genuinely
new iMessage user would also trip it harmlessly.

To fix: enable "Messages in iCloud" on all devices signed into the account
(Messages -> Settings -> iMessage on Mac; Settings -> [name] -> iCloud ->
"Messages in iCloud" on iPhone), and give it time to finish an initial sync before
re-running `imessage_doctor`.

## Watching for new messages

This plugin is deliberately on-demand only: open, query, close, return data, done —
no background watcher, no polling for inbound messages. If you need Claude to react
to new messages as they arrive rather than being asked to check, there are two real
options, neither built into this plugin:

1. **Claude Code's "Channels" feature** (research preview as of this writing) is the
   mechanism Anthropic's own official iMessage channel plugin
   ([anthropics/claude-plugins-official/external_plugins/imessage](https://github.com/anthropics/claude-plugins-official/tree/main/external_plugins/imessage))
   uses: an MCP server declares the `claude/channel` capability, polls chat.db
   internally (that plugin polls once a second for `ROWID > watermark`), and pushes
   a `notifications/claude/channel` event into the live Claude Code session when
   something new shows up — no separate cron/launchd job needed, but it requires
   the MCP server process itself to stay running, is gated behind Anthropic's
   channel allowlist or the `--dangerously-load-development-channels` flag, and is
   wired through the low-level MCP SDK rather than FastMCP's high-level tool API.
   See [the Channels reference](https://code.claude.com/docs/en/channels-reference)
   for the full contract.
2. **An external scheduler** (a local `/loop`-style recurring session, or a plain
   macOS `launchd` job) that wakes periodically, calls `imessage_recent` with a
   `since` watermark it persists itself, and only invokes Claude when there's
   something new. Simpler to build with what this plugin already exposes, at the
   cost of being coarser-grained than a live push.

## Why no calling/write capability beyond `imessage_send`

Everything here is on-demand: open, query, close, return data, exit (or, for
`imessage_send`, hand off to `osascript` once). A future scheduled job calling
`imessage_recent` on an interval is a natural next step for anyone wiring up option
2 above, but the watermark should live in whatever calling system consumes this
plugin's output, not be invented here.
