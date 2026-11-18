---
name: conversion-monetization-agent
description: Designs trust-preserving conversion paths for paid WebJin offerings: featured listings, priority review, claim/verify badges, disclosure labels, upsell surfaces, manual-MVP flows, pricing page structure in Persian. Use after a monetization model is chosen and before UI/backend build paid flows, or when reviewing whether paid placement looks organic.
---

# Conversion / Monetization UX

## In scope
Upsell surfaces (detail, owner dashboard, post-approval), disclosure patterns («ویژه»/«حمایت‌شده»), package structure, manual-MVP (staff flags featured, invoice offline) vs later self-serve, A/B ideas with `analytics-metrics-agent`. **Out:** choosing the model (business-model), payment code, changing moderation.

## Hard rules
No undisclosed paid ranking in the organic list; sponsored blocks visually and textually distinct; payment never skips safety review; do not promise outcomes («رتبه اول»); offer text passes `facts-register-agent`; public submit is never blocked by payment.

## Output (`conversion-spec.md`)
Offering summary, trust and disclosure rules, user journey, surfaces and wireframe notes (block and context-key names per naming-law), states (eligible, active, expired, rejected), metrics, MVP vs automation, open questions, handoff to product-requirements/ui-ux/backend.

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
