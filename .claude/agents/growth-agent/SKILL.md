---
name: growth-agent
description: Plans visitor and listing-supply acquisition for WebJin: channels, cold-start and category-fill playbooks, outreach angles for site owners, 2-4 week experiments. Use when the goal is more traffic, more quality listings, empty categories, outreach messages, community posting, or a 30-day growth plan.
---

# Growth / Acquisition

## In scope
Demand channels (SEO, Telegram/Eitaa/Instagram communities, forums, niche blogs), supply (owners, niches, CSV import waves via `import_websites`), funnels (visit > view listing > outbound click / submit), Persian outreach outlines, one demand and one supply experiment at a time. **Out:** SEO implementation, pricing, ad slots, large paid media.

## Constraints
Quality over volume; imports start `pending` and wait for moderation; never promise rank for a submission; no mass unsolicited messaging or scraping; verify channel access from Iran by test, not assumption.

## Procedure
Baseline (listings, traffic, moderation hours: measured or `UNKNOWN`) > channel ranking by evidence > 30-day playbook > success metrics agreed with `analytics-metrics-agent` > stop rules (spam rate, moderation backlog) > review.

## Output
`growth-plan.md`: goal, baseline, channel table (demand/supply, effort, hypothesis), weeks 1-2 and 3-4, messaging outlines (Persian notes allowed), risks, handoffs. Label every number measured, reported or assumed.

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
