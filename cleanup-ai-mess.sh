#!/usr/bin/env bash
# cleanup-ai-mess.sh
# Safe cleanup of redundant AI skill/agent files on webjin.ir-current main
# Run from the repository root.

set -euo pipefail

echo "=== WebJin AI cleanup ==="
echo

# 1. Empty Claude template
if [ -f ".claude/agents/claude.agent.md" ]; then
  git rm -f ".claude/agents/claude.agent.md"
  echo "Removed: .claude/agents/claude.agent.md (empty template)"
fi

# 2. Generic mentor (not part of the sequential pipeline)
if [ -f ".claude/agents/claude Agent.agent.md" ]; then
  git rm -f ".claude/agents/claude Agent.agent.md"
  echo "Removed: .claude/agents/claude Agent.agent.md (generic mentor)"
fi

# 3. Entire Copilot skills tree (Celery + DRF + generic duplicates)
if [ -d ".copilot" ]; then
  git rm -rf .copilot
  echo "Removed: .copilot/ (entire tree)"
fi

# 4. Generic GitHub / VS Code agent
if [ -d ".github/agents" ]; then
  git rm -rf .github/agents
  echo "Removed: .github/agents/"
fi

# Optional: remove empty .github if nothing else is left inside
if [ -d ".github" ] && [ -z "$(find .github -type f 2>/dev/null)" ]; then
  git rm -rf .github 2>/dev/null || rm -rf .github
  echo "Removed empty: .github/"
fi

echo
echo "=== Kept (do not touch) ==="
echo "  .ai_files/roadmap.md"
echo "  .ai_files/technical-conventions.md"
echo "  .claude/agents/*/SKILL.md   (7 sequential agents)"
echo "  AGENTS.md"
echo "  feature_list.md"
echo
echo "Done. Review with:  git status"
echo "Then commit:        git commit -m 'chore: remove redundant AI skill/agent placeholders'"