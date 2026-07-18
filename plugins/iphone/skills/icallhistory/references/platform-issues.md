# Known platform issues

## Full Disk Access (TCC)

`CallHistory.storedata` is protected by macOS's TCC (Transparency, Consent, and
Control) system, the same bucket that gates the `imessage` skill's `chat.db` and the
AddressBook:

System Settings -> Privacy & Security -> Full Disk Access -> add the app running
Claude -> restart the app.

Without it, `sqlite3.connect(..., uri=True)` in read-only mode raises
`sqlite3.OperationalError` (typically `unable to open database file` or
`authorization denied`). `server.py`'s `open_calls_db()` catches this and raises a
clear error pointing at the fix; `calls_doctor` surfaces it as
`call_history_db_readable: false`. If Full Disk Access is already granted for the
`imessage` skill's tools, this skill is covered too — it's the same grant, not a
separate one. See the `imessage` skill's own `references/platform-issues.md` for a
Claude-Code-specific gotcha where an app update can silently revoke this grant.

## AddressBook access

Contact name resolution reads
`~/Library/Application Support/AddressBook/Sources/*/AddressBook-v22.abcddb` — also
a plain SQLite file, also covered by Full Disk Access. If it's unreadable or
missing, this skill degrades gracefully: handles are shown as raw phone
numbers/emails instead of names, and `calls_doctor` reports
`address_book_found: false` as a warning, not a failure.

## Continuity Calling ("Calls From iPhone")

This is the caveat that actually matters for this skill, more than the generic TCC
grant above.

A Mac only sees **real cellular phone calls** in `CallHistory.storedata` if
Continuity Calling is turned on and actively relaying: both the Mac and the iPhone
signed into the same Apple ID, both on the same Wi-Fi network (Bluetooth assists
discovery/handoff, but the call itself travels over Wi-Fi), and, on the Mac,
FaceTime -> Settings (or Preferences, depending on macOS version) -> "Calls From
iPhone" enabled.

Without that: `CallHistory.storedata` still exists and is still readable, but it
only contains FaceTime Audio/Video calls placed directly from the Mac itself
(`ZCALLTYPE` 8/16) — zero rows with `ZCALLTYPE = 1` (phone). `calls_doctor` detects
exactly this shape (`phone_call_count == 0` while `call_count > 0`) and warns about
it, because it's easy to misread as "this skill doesn't work" when actually it's
working correctly against a database that simply has no cellular calls synced to it.

Even with Continuity Calling on, this is **not** a continuously-synced iCloud
history the way iMessage is (see the `imessage` skill's own "iCloud multi-device
sync" caveat for that contrast) — a call only lands in this database if the Mac was
actually near the iPhone on the same network at the time. Treat a thin or gappy
result as expected behavior, not a bug, and don't assume this is a complete log of
every call the phone ever placed or received.

macOS 26 added a more fully-featured native Phone app with deeper Continuity
integration; the underlying `CallHistory.storedata`/`ZCALLRECORD` schema this skill
reads is still the mechanism observed in current forensics tooling, but if a future
macOS release changes this, `calls_doctor`'s readability/count checks will surface it
as an error or an unexpectedly-empty result rather than silently returning wrong data.

## Pre-Ventura encryption

Before macOS 13 (Ventura), `CallHistory.storedata` was encrypted with an AES-GCM key
stored in Keychain (labeled "Call History User Data Key"). This plugin assumes the
unencrypted Ventura+ format that current macOS releases use and does not attempt to
locate or use that key — on a pre-Ventura system, `open_calls_db()` will fail to
read the file the same way it would for any other unreadable database.

## Why no calling/write capability

Unlike the `imessage` skill's `imessage_send` (which shells out to `osascript`
telling Messages.app to deliver a message via AppleScript), there is no equivalent
scripting hook to originate a phone or FaceTime call from a script — Apple doesn't
expose one, and a Mac can't place a cellular call at all without an iPhone relaying
it regardless. This skill is deliberately read-only with no path to add a "call"
tool later without a fundamentally different mechanism (e.g. driving FaceTime.app's
UI directly, which is out of scope here).

## Why no daemon/scheduler

Same reasoning as the `imessage` skill: everything here is on-demand — open, query,
close, return data, done. No background watcher, no polling for inbound calls.
