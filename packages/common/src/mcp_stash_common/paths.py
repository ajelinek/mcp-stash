"""Per-solution state directories, shared across every mcp-stash plugin."""

from __future__ import annotations

from pathlib import Path


def state_dir(name: str) -> Path:
    """Return (creating if needed) `~/.mcp-stash/<name>/`."""
    d = Path.home() / ".mcp-stash" / name
    d.mkdir(parents=True, exist_ok=True)
    return d
