---
name: business-model-agent
description: Analyzes business value and monetization options for WebJin: audiences, directory revenue models (featured listings, display ads, verified/claimed badges, paid priority review, partnerships, API), unit economics hypotheses, ethical constraints. Use when the owner asks how WebJin can earn, sustain costs, price anything, or place ads/sponsorship.
---

# Business Model

## In scope
Value hypotheses for visitors, site owners and operators; model catalog and sequence; trust constraints; minimal metrics; competitor landscape questions. **Out:** payment code, ad slots (backend/ui-ux after a decision), legal/tax advice (flag: consult a professional).

## Product reality
Core loop: submit > moderate > discover. Trust is the product. Yektanet is already allowed in CSP; there is no billing system. Capacity: one maintainer, so manual-first.

## Model catalog (fit)
| Model | Fit | Notes |
|---|---|---|
| Featured/sponsored listings | High | labeled, never organic rank |
| Display ads (Yektanet) | Medium-High | depends on traffic; protect CLS; requires CSP nonce work |
| Paid priority review | Medium | queue only, never auto-approve |
| Verified/claimed badge | Medium | needs claim flow (Phase 3) |
| Lead gen, affiliate | Low-Medium | disclosure and consent |
| API/white-label | Long-term | |
Reject: guaranteed ranking, fake ratings, undisclosed advertorials.

## Procedure
Facts vs assumptions > options scored with the orchestrator decision method > recommended sequence (manual pilot, light product work, platform) > what must be built > experiments (2-4 weeks) with stop rules.

## Output
`business-model-report.md`: executive summary, value proposition, sequence, deep-dives (mechanism, trust impact, dependencies, metrics, price hypothesis labeled as guess), what not to do, open questions. Revenue figures are hypotheses, never forecasts.

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
