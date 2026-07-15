#!/usr/bin/env bash
# Scaffold a new mcp-stash plugin by copying plugins/_template to plugins/<slug>.
#
# Usage: scripts/new_plugin.sh <slug> ["Human readable description"]
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <slug> [\"description\"]" >&2
  exit 1
fi

SLUG="$1"
DESCRIPTION="${2:-TODO: describe this plugin}"

if [[ ! "$SLUG" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error: <slug> must be kebab-case, e.g. 'm365-toolkit'" >&2
  exit 1
fi

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$ROOT_DIR/plugins/_template"
DEST_DIR="$ROOT_DIR/plugins/$SLUG"

if [[ -e "$DEST_DIR" ]]; then
  echo "error: $DEST_DIR already exists" >&2
  exit 1
fi

SLUG_SNAKE="${SLUG//-/_}"
OLD_PKG="mcp_stash_template"
NEW_PKG="mcp_stash_${SLUG_SNAKE}"

echo "Copying $SRC_DIR -> $DEST_DIR"
cp -R "$SRC_DIR" "$DEST_DIR"

echo "Renaming package directory $OLD_PKG -> $NEW_PKG"
mv "$DEST_DIR/src/$OLD_PKG" "$DEST_DIR/src/$NEW_PKG"

echo "Renaming skill directory template-skill -> $SLUG"
mv "$DEST_DIR/skills/template-skill" "$DEST_DIR/skills/$SLUG"

echo "Rewriting package references"
grep -rl "$OLD_PKG" "$DEST_DIR" | while read -r f; do
  sed -i.bak "s/$OLD_PKG/$NEW_PKG/g" "$f" && rm -f "$f.bak"
done

echo "Rewriting plugin name (template -> $SLUG) and description"
sed -i.bak \
  -e "s/\"name\": \"template\"/\"name\": \"$SLUG\"/" \
  -e "s/TODO: describe this plugin/$DESCRIPTION/" \
  "$DEST_DIR/.claude-plugin/plugin.json" && rm -f "$DEST_DIR/.claude-plugin/plugin.json.bak"

sed -i.bak "s/template-skill/$SLUG/g; s/mcp-stash-template/mcp-stash-$SLUG/g" \
  "$DEST_DIR/skills/$SLUG/SKILL.md" && rm -f "$DEST_DIR/skills/$SLUG/SKILL.md.bak"

cat <<EOF

Done. Next steps:
  1. Add an entry for '$SLUG' to .claude-plugin/marketplace.json (plugins[]).
  2. Edit $DEST_DIR/src/$NEW_PKG/server.py with real tools.
  3. If this plugin needs packages/common helpers, vendor them the same
     way plugins/imessages does:
       ln -s ../../../packages/common/src/mcp_stash_common $DEST_DIR/src/mcp_stash_common
     and add "mcp_stash_common" to module-name in $DEST_DIR/pyproject.toml.
  4. From repo root: uv sync --all-packages --locked && uv run pytest $DEST_DIR/tests
  5. claude plugin validate $DEST_DIR
EOF
