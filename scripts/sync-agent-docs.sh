#!/usr/bin/env bash
set -euo pipefail

# Keep Codex/OpenAI-style AGENTS.md files and Claude-style CLAUDE.md files
# mirrored. Each AGENTS.md is a symlink to the CLAUDE.md beside it, so edits
# through either filename update the same underlying document.
root="${1:-.}"
find "$root" \
  -path '*/.git' -prune -o \
  -name CLAUDE.md -type f -print | while IFS= read -r claude; do
    dir="$(dirname "$claude")"
    agents="$dir/AGENTS.md"
    if [ -e "$agents" ] && [ ! -L "$agents" ]; then
        echo "Refusing to replace non-symlink $agents" >&2
        exit 1
    fi
    ln -sfn CLAUDE.md "$agents"
done
