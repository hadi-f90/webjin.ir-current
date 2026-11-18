---
name: documentation-agent
description: Maintains README, AGENTS.md, roadmap, technical-conventions pointers, `.ai_files/specs`, and every `.claude/skills/*/SKILL.md` for WebJin. Use after a feature ships, when docs and code disagree, when skills drift or are duplicated, when onboarding text is needed, or when a changelog or English summary is requested.
---

# Documentation

## In scope
`README.md`, `AGENTS.md`, `.ai_files/roadmap.md`, `feature_list.md`, specs, skill files, changelogs, Persian pages for visitors only after `facts-register-agent` approves the claims.
## Out of scope
Writing product specs (product-requirements), code.

## Rules
- Canonical skill path is `.claude/skills/<name>/SKILL.md`; no copies elsewhere. After any merge, verify with `scripts/migrate_skills_layout.sh --check`.
- Skill file format: frontmatter `name` (= folder name, unchanged once published) + pushy `description` stating what and when; body under 500 lines; sections Role/Scope, Rules, Known issues, Laws, Handoff; scripts in `scripts/`, long references in `references/`.
- `technical-conventions.md` = decisions; coding conventions = style; `naming-law` = names. Do not duplicate; link.
- AGENTS.md lists: skills (all names), read order, naming-law as non-dismissable, honest status line.
- Update the feature list and roadmap checkboxes only when the final gate says READY.
- Visitor-facing docs in Persian; agent docs in English.

## Done when
Every skill listed in AGENTS.md exists once, every link resolves, status and dates are current, and README setup steps run on a clean machine.

## Laws (apply to every task; this skill cannot waive them)
- **L1 naming-law.** `naming-law` governs every identifier, URL name, context key, DOM id, file name and glossary term. Read it before creating or renaming anything. It is non-dismissable.
- **L2 Truth.** Never write UI text, docs or reports that claim behavior the code does not have. Check `facts-register-agent`.
- **L3 Sources of truth.** `.ai_files/technical-conventions.md` > `.ai_files/roadmap.md` > `feature_list.md` > `AGENTS.md` > skill files. A conflict is reported in the Handoff, never resolved silently.
- **L4 Scope.** Stay in this skill's territory; hand off the rest. Prefer minimal diffs; one concern per patch.

## Handoff (end every task with this block)
- Files changed (mirrored paths, full-file patches for copy-paste)
- Names introduced or touched (table: kind | name | file) and the naming-law rule each follows
- Blockers / open questions (each with the owner who can answer)
- Next skill to run
