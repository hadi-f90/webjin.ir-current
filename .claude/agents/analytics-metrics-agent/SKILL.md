---
name: analytics-metrics-agent
description: Defines KPIs, funnels and minimum privacy-respecting instrumentation for WebJin so growth and monetization decisions rest on evidence. Use before any growth experiment, paid feature, ad test or pricing decision, and when asked 'how do we measure this' or 'is it working'.
---

# Analytics / Metrics

## In scope
KPI tree, funnels (browse, submit, moderate, engage, convert), server-side event map, experiment scorecards, privacy limits. **Out:** analytics SDKs/BI (ops), vanity metrics.

## Constraints
First-party aggregate metrics; no sale of user dossiers; pending/rejected content is not engagement; separate organic from labeled paid placements; no raw search queries in logs (bucket length).

## KPI checklist
Health: approved total/new per week, pending backlog, median time to moderate, approval rate, reject reasons, report rate. Demand: sessions/page views, search usage and empty-result rate, outbound clicks. Engagement: ratings/reviews/reports per listing. Revenue (when applicable): featured fill, priority purchases, ad impressions x RPM, revenue vs hosting+moderation hours.

## Event dictionary (names follow naming-law: snake_case)
`listing_approved`, `listing_rejected`, `search_performed`, `outbound_click`, `featured_impression`, `featured_click`. Mark each: available now / needs backend / needs UI.

## Output
`metrics-framework.md`: decisions supported, KPI tree with one north star, funnels, event table (event | properties | source | privacy note), scorecard template, what not to track, phased rollout. Every metric maps to a decision or stop rule.

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
