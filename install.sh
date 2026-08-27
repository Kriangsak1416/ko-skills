#!/usr/bin/env bash
# Installs the boss-mode crew (agents + skill) into this machine's user-level
# Claude Code config, so it is available in every project.
#
#   bash ./install.sh
#
# Per-project install instead: just copy the .claude folder into the project root.

set -euo pipefail

src="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/.claude"
dst="${HOME}/.claude"

[ -d "$src" ] || { echo "Cannot find $src - run this script from the repo it shipped in." >&2; exit 1; }

mkdir -p "$dst/agents" "$dst/skills" "$dst/rules"
cp -R "$src/agents/." "$dst/agents/"
cp -R "$src/skills/." "$dst/skills/"
# Only the rules that ship in this repo - leaves any other rules you already have untouched.
for f in "$src"/rules/*.md; do cp "$f" "$dst/rules/"; done

echo "Installed to $dst"
echo "  agents: coder, reviewer, scout, fixer  (model: sonnet)"
echo "  rules:"
for f in "$src"/rules/*.md; do echo "          $(basename "$f")"; done
echo "  skills:"
for d in "$src"/skills/*/; do echo "          /$(basename "$d")"; done

if ! command -v gh >/dev/null 2>&1; then
  echo
  echo "NOTE: GitHub CLI not found. /ship needs it to open the release PR:"
  echo "      see https://github.com/cli/cli#installation   then   gh auth login"
fi
echo

settings="$dst/settings.json"
if [ -f "$settings" ]; then
  if grep -q '"model"[[:space:]]*:[[:space:]]*"opus"' "$settings"; then
    echo "Lead model is already 'opus' in $settings - good."
  else
    echo "NOTE: $settings does not set model = opus."
    echo "      Boss mode expects the lead to be Opus. Set it with /model opus or edit that file."
  fi
else
  printf '{ "model": "opus" }\n' > "$settings"
  echo "Created $settings with model = opus"
fi

echo
echo "Restart Claude Code, then run:  /boss <your task>"
