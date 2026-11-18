#!/usr/bin/env bash
# Move WebJin skills to the canonical layout: .claude/skills/<name>/SKILL.md
# Usage: bash scripts/migrate_skills_layout.sh --check   (report only)
#        bash scripts/migrate_skills_layout.sh --apply   (git rm the old copies)
set -euo pipefail
mode="${1:---check}"
old=$(ls .claude/agents/*/SKILL.md 2>/dev/null || true)
if [ -z "$old" ]; then echo "OK: no legacy .claude/agents/*/SKILL.md copies"; exit 0; fi
echo "Legacy skill copies found:"; echo "$old"
if [ "$mode" = "--apply" ]; then
  for f in $old; do git rm -q "$f" && echo "removed $f"; done
  rmdir .claude/agents 2>/dev/null || true
  echo "Done. Commit: 'skills: canonical path .claude/skills'"
else
  echo "Run with --apply to remove them (new versions live in .claude/skills/)."; exit 1
fi
