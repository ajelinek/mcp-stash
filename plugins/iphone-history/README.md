# iphone-history (mcp-stash placeholder/test plugin)

Placeholder plugin proving the mcp-stash pattern end to end. It does
**not** read backup content — it only reports whether
`~/Library/Application Support/MobileSync/Backup` exists and basic
metadata.

## Prerequisites

The machine needs `uv` installed and on `PATH`.

## Install

In Claude Desktop: **Customize → Plugins → (+) → Add marketplace**,
enter `ajelinek/mcp-stash`, then install `iphone-history` from the list.
(Equivalent chat commands: `/plugin marketplace add ajelinek/mcp-stash`
then `/plugin install iphone-history@mcp-stash`.)

## What's inside

Same layout as `plugins/imessages` — see that plugin's README for the
file-by-file breakdown.
