# mcp-stash

A growing collection of Claude plugins ("solutions") for consulting
clients, each bundling its own local MCP server(s) (and, over time,
Skills/hooks) as a single one-command install. This repo is itself a
plugin marketplace.

## What this is

The consultant behind this repo builds automation tools and ships them
to consulting clients. Early tools were Python CLI scripts invoked
through Claude's Bash tool, which sometimes can't reach a client's real
machine because Bash-tool commands execute wherever that session's
code-execution sandbox happens to be hosted (for a default Cowork
session, that's a fully isolated, ephemeral VM on Anthropic's servers
with no path to the local machine or home network). MCP servers fix
this: an MCP tool call is dispatched to wherever the MCP server process
actually lives. Once a server is installed and spawned by **Claude
Desktop**, it runs as a real local subprocess on the user's own
machine — and both a plain chat session and a Cowork session in that
same Desktop app can reach that already-running local server, since its
lifecycle is owned by Desktop, not by whatever sandbox a particular
session's own reasoning/code-execution happens to use.

Each solution here is a **Claude plugin**: it bundles its own MCP
server (built with [FastMCP](https://gofastmcp.com)) plus a Skill that
tells Claude how to use it. This repo is the **marketplace** that lists
every solution, so a client can add it once and install whichever
solutions they need.

## Repo layout

```
mcp-stash/
  .claude-plugin/marketplace.json  # the marketplace manifest
  packages/common/                 # shared helpers, vendored (not installed) into plugins
  plugins/_template/                # copy-paste scaffold, never published
  plugins/imessages/                # placeholder/test solution #1
  plugins/iphone-history/           # placeholder/test solution #2
  scripts/new_plugin.sh             # scaffolds a new plugin from _template
```

## Installing a plugin (for clients)

In Claude Desktop: **Customize → Plugins → (+) → Add marketplace**,
enter `ajelinek/mcp-stash`, then install a plugin from the list (for
now: `imessages` or `iphone-history`).

The equivalent commands also work the same way in a Desktop or Cowork
chat window, since both reach the same locally-running MCP server once
it's registered through Desktop:

```
/plugin marketplace add ajelinek/mcp-stash
/plugin install imessages@mcp-stash
```

To update or remove a plugin later:

```
/plugin update imessages@mcp-stash
/plugin marketplace update mcp-stash
/plugin uninstall imessages@mcp-stash
```

**Prerequisite:** the machine running Claude Desktop needs
[`uv`](https://docs.astral.sh/uv/getting-started/installation/)
installed and on `PATH`. `uv` fetches the right Python version itself,
so no separate Python install is required.

Each plugin's own README (e.g. `plugins/imessages/README.md`) has
plugin-specific usage notes; this section covers the marketplace
mechanics, which are identical for every plugin here.

## Adding a new solution (for you)

1. Scaffold it from the template:

   ```
   ./scripts/new_plugin.sh my-solution "One-line description"
   ```

   This copies `plugins/_template` to `plugins/my-solution`, renaming
   the Python package, the skill directory, and the `plugin.json` name
   field.

2. Implement real tools in
   `plugins/my-solution/src/mcp_stash_my_solution/server.py`, and real
   guidance in `plugins/my-solution/skills/my-solution/SKILL.md`.

3. If the new plugin needs helpers from `packages/common` (logging,
   state paths, secrets, notifications, filesystem checks), vendor them
   via a symlink — required, not optional, because Claude Desktop
   copies each plugin's directory into an isolated cache at install
   time and does not follow paths outside the plugin. Copy the pattern
   from `plugins/imessages`:

   ```
   ln -s ../../../packages/common/src/mcp_stash_common \
     plugins/my-solution/src/mcp_stash_common
   ```

   and add `"mcp_stash_common"` to the `module-name` list in
   `plugins/my-solution/pyproject.toml`'s `[tool.uv.build-backend]`
   table.

4. Register it:
   - It's already picked up as a uv workspace member automatically
     (`plugins/*` glob in the root `pyproject.toml`).
   - Add an entry to `.claude-plugin/marketplace.json`'s `plugins` array
     only once it's ready for clients to install — `plugins/_template`
     is deliberately never added here.

5. Sync, lint, and test from the repo root:

   ```
   uv sync --all-packages --locked
   uv run ruff check .
   uv run pytest
   ```

6. Validate the plugin and the whole marketplace (maintainer-side tool
   only — clients never need this):

   ```
   claude plugin validate ./plugins/my-solution
   claude plugin validate .
   ```

7. Test the real install flow in Claude Desktop before publishing (a
   local path works for a marketplace under test).

8. Release it — see "Versioning and releases" below.

## Local development

```
uv sync --all-packages --locked   # one-time / after pulling changes
make lint                          # ruff check .
make test                          # uv run pytest
make check                         # lint + test + claude plugin validate
```

Run a single plugin's tests with `uv run pytest plugins/<name>/tests`.

## Versioning and releases

Each plugin is versioned independently — bump `version` in
`plugins/<name>/.claude-plugin/plugin.json`, add a dated entry to
`plugins/<name>/CHANGELOG.md`, then `claude plugin tag plugins/<name>`
(`--dry-run` to preview, `--push` to push) and push the commit. Clients
only receive the update when they explicitly update (via the Desktop
Plugins panel, or `/plugin update <name>@mcp-stash`) — nothing changes
on a client's machine on its own. Explicit semver (rather than letting
every commit auto-count as a new version) is deliberate here: these are
client deliverables that need controlled releases, not an
internal/rapidly-iterating tool.

## Roadmap

Next up: a real Microsoft 365/Graph-related solution, and turning
`imessages`/`iphone-history` into actual data-reading plugins once the
plumbing proven here (packaging, marketplace install, stdio connection,
local filesystem access) is trusted. Nothing in this structure blocks a
future plugin from also mixing in a third-party/remote MCP server
(e.g. an OAuth-authenticated Microsoft Graph endpoint) alongside its
own local FastMCP server, in the same `.mcp.json`.
