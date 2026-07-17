# mcp-stash — instructions for Claude

This repo is both a **uv workspace** (for building/testing Python code)
and a **Claude plugin marketplace** (`.claude-plugin/marketplace.json`
at the repo root) that consulting clients install from directly in
Claude Desktop: Customize → Plugins → (+) → Add marketplace →
`ajelinek/mcp-stash`. Each installable unit is a "solution" — a
self-contained Claude plugin bundling one or more local FastMCP
servers, built so it still runs correctly after Claude Desktop copies
it out of this repo into its own isolated plugin cache.

There is no scaffolding script and no template directory — when asked
to add a new plugin, generate the files directly from the pattern
below (copy the shape of `plugins/imessages`, which is a complete,
tested, working reference implementation).

## Repo layout

```
mcp-stash/
  .claude-plugin/marketplace.json   # lists every installable plugin
  packages/common/                  # shared helpers, vendored (not installed) into plugins
  plugins/<name>/                   # one directory per solution
```

## Anatomy of one plugin (`plugins/<name>/`)

```
plugins/<name>/
  .claude-plugin/plugin.json   # name (kebab-case), version, description, author, etc.
  .mcp.json                    # declares the bundled MCP server(s) — see below
  fastmcp.json                 # local dev only (`fastmcp run fastmcp.json`); NOT used by the installed plugin
  skills/<name>/SKILL.md        # tells Claude when/how to use this plugin's tools
  pyproject.toml
  src/mcp_stash_<name>/
    __init__.py                # `from .server import mcp`
    __main__.py                # `from mcp_stash_<name>.server import mcp` + `mcp.run()` under `if __name__ == "__main__"`
    server.py                  # FastMCP instance + @mcp.tool functions
  tests/test_server.py          # in-memory fastmcp.Client tests
  README.md
  CHANGELOG.md
```

Naming: directory and marketplace `name` are kebab-case
(`iphone-history`); the Python package is the same string with
underscores (`mcp_stash_iphone_history`).

### `.claude-plugin/plugin.json`

Required: `name` only. Always also set `version` (semver — see
Versioning below), `description`, `author`, `homepage`/`repository`
(this repo's URL), `license`. Do **not** add an `mcpServers` field here
— `.mcp.json` at the plugin root is already the default discovery
location, and declaring both risks the two sources being merged
ambiguously.

### `.mcp.json`

```json
{
  "mcpServers": {
    "<name>": {
      "command": "uv",
      "args": ["run", "--project", "${CLAUDE_PLUGIN_ROOT}", "python", "-m", "mcp_stash_<name>"]
    }
  }
}
```

Invoke the module directly (`uv run --project ... python -m <pkg>`),
not `fastmcp run <fastmcp.json>` — once installed, the plugin directory
is a fully self-sufficient uv project, and going through FastMCP's own
CLI would add a second, redundant environment-management layer with its
own path assumptions.

A single plugin can bundle **multiple** MCP servers: add more entries
to this same `mcpServers` object (each its own `command`/`args`,
typically one more `src/mcp_stash_<name>/<thing>_server.py` module and
one more `__main__`-style entry point). Use this when a solution is one
coherent product with several tool surfaces (e.g. Outlook + Teams +
SharePoint under one client-facing install), rather than splitting into
several separately-installed plugins.

### `fastmcp.json` (dev-only)

```json
{
  "source": {
    "type": "filesystem",
    "path": "src/mcp_stash_<name>/server.py",
    "entrypoint": "mcp"
  },
  "environment": { "type": "uv", "python": ">=3.12", "project": "." },
  "deployment": { "transport": "stdio", "log_level": "INFO" }
}
```

### `pyproject.toml`

```toml
[project]
name = "mcp-stash-<name>"
version = "0.1.0"
description = "..."
requires-python = ">=3.12"
dependencies = ["fastmcp>=3.4"]

[build-system]
requires = ["uv_build>=0.8.17,<0.9"]
build-backend = "uv_build"
```

If this plugin vendors `packages/common` (see next section), add
`"keyring>=25.5.0"` to `dependencies` (a transitive import of
`mcp_stash_common`) and the `[tool.uv.build-backend]` table shown below.

## Sharing code via `packages/common`

Claude Desktop copies an installed plugin's directory into an isolated
cache and does **not** follow references outside that directory — a
plain `../../../packages/common` import, or a `{workspace = true}`
uv-source dependency, breaks the moment a client installs the plugin,
even though it works fine when testing in-place from a git checkout.

The fix, already proven in `plugins/imessages` and
`plugins/iphone-history`: a **same-repo symlink** dereferenced by Claude
Desktop at install time into a real copy, packaged into the plugin's
own distribution via `uv_build`'s multi-directory `module-name`:

```bash
ln -s ../../../packages/common/src/mcp_stash_common plugins/<name>/src/mcp_stash_common
```

```toml
[tool.uv.build-backend]
module-name = ["mcp_stash_<name>", "mcp_stash_common"]
```

`packages/common` itself is a **virtual** workspace member
(`package = false`, no `[build-system]`) — it is never installed as its
own distribution, only ever consumed this way. Only vendor it if the
new plugin actually needs its helpers (logging, `~/.mcp-stash/<name>/`
state paths, keychain secrets, desktop notifications, read-only
filesystem checks); it's fine for a plugin to skip this entirely.

## Skills

`skills/<name>/SKILL.md` needs YAML frontmatter with `name` and
`description` (the description drives when Claude decides to use it —
be specific about trigger conditions), then guidance on which tools to
call and how to interpret their results.

## Registering a new plugin

Add an entry to `.claude-plugin/marketplace.json`'s `plugins` array
once it's ready for clients to install:

```json
{ "name": "<name>", "source": "./plugins/<name>", "description": "..." }
```

(Use a full `./plugins/<name>` path, not a bare `<name>` shorthand —
the latter isn't accepted by the currently-installed `claude` CLI even
with `metadata.pluginRoot` set.)

## Verifying a new plugin

```bash
uv sync --all-packages --locked
uv run ruff check .
uv run pytest plugins/<name>/tests
claude plugin validate ./plugins/<name>
claude plugin validate .            # whole marketplace, run before every push
```

`claude plugin validate` and `claude` generally are maintainer-side dev
tools only — clients never run them; they use Claude Desktop's GUI.

For a stronger check that the vendored dependency truly survives
Desktop's cache-copy (not just the in-memory `fastmcp.Client` tests),
spawn the plugin's actual `.mcp.json` command against a copy with the
symlink dereferenced (`cp -RL plugins/<name> /tmp/check`) and confirm
`uv run --project /tmp/check python -m mcp_stash_<name>` still resolves
and runs with no sibling `packages/` directory present.

## Versioning and releases

Each plugin versions independently. To release a change: bump
`version` in `plugins/<name>/.claude-plugin/plugin.json`, add a dated
entry to `plugins/<name>/CHANGELOG.md`, then
`claude plugin tag plugins/<name> --push` (or omit `--push` and push
manually), then push the commit. Clients only receive it when they
explicitly update (Desktop's Plugins panel, or
`/plugin update <name>@mcp-stash`) — never automatically. Use explicit
semver here, not commit-SHA auto-versioning — these are client
deliverables that need controlled releases.

## CI

`.github/workflows/ci.yml` runs `uv sync --all-packages --locked` +
`ruff check` + `pytest`, and separately `claude plugin validate . --strict`
(installing `@anthropic-ai/claude-code` via npm — confirmed to need no
auth for this check). Keep both green before merging.
