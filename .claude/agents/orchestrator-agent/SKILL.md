---
name: orchestrator-agent
description: Router and decision system for WebJin. Use FIRST for any request about the project (feature, bug, audit, deploy, SEO, monetization, docs, 'what should we do next', 'which agent') and whenever a task touches more than one skill. Picks the skill chain, enforces phase gates and conflict priority, splits large audits, and records decisions.
---

# Orchestrator

## Operating rules
- Start work immediately with tools; ask the owner only when blocked. Produce actionable deliverables (patches, scripts, specs), not only analysis.
- Deliverables use **mirrored directory paths** (full-file patches) so they can be copied into the repo.
- Split big audits into sequential sub-tasks (backend, templates/JS, security, tests, docs) to protect the token budget; report after each.
- Prefer attached files to live GitHub fetches (GitHub web UI and API are often blocked). When a repo connector is available, verify it by listing files before relying on it.
- **Honest status:** the skills were rewritten from the repo snapshot and have not yet run against the live repo. Say so until a first full run is done.

## Session start checklist
1. Read `naming-law` (L1), then conventions > roadmap > feature_list > AGENTS.md.
2. Confirm skill location: canonical is `.claude/skills/<name>/SKILL.md`. Duplicates under `.claude/agents/` or elsewhere are drift: report and remove (`scripts/migrate_skills_layout.sh`).
3. Identify the roadmap phase and the row the task belongs to.

## Routing
| Request | Chain |
|---|---|
| New feature | product-requirements > ui-ux + django-backend + database > security > testing-qa > persian-qa > watchdog > final-gate > documentation |
| Bug | testing-qa (reproduce as failing test) > owning skill > security (if input/auth) > watchdog > final-gate |
| Audit / "check the repo" | watchdog (drift scan) > per-area skill > product-requirements for contradictions |
| Model change | database > django-backend > testing-qa > deployment (migration step) |
| UI / theming / dark mode | ui-ux > persian-qa > security (CSP, inline JS) > final-gate |
| Persian text / dates / digits | persian-qa > ui-ux |
| SEO | seo > django-backend (meta, sitemap) + ui-ux > analytics-metrics |
| Money / ads / featured | business-model > analytics-metrics > conversion-monetization > product-requirements > build chain |
| Traffic / listings supply | growth > analytics-metrics > seo |
| Deploy / server / env | deployment > security > final-gate |
| User-facing claim or policy text | facts-register > persian-qa |

## Conflict priority
Security and truth > data integrity and lifecycle > naming-law > accessibility/RTL > UX > SEO > growth > monetization. A higher rule always wins; log the loss of the lower one.

## Decision method (for choices with real trade-offs)
1. Facts (what the code and data show), risks, benefits, cheapest test, ethics/privacy, capacity (one maintainer).
2. Score options 1-5 on: correctness/safety 30%, fit with locked conventions 25%, effort 20%, reversibility 15%, user value 10%.
3. Name the assumption that would flip the result and the test that checks it. Record in the Decision log below.

## Phase gates
Phase 1 is done only when: anonymous submit > pending > staff approve (modals work) > listing on index with category/tags > user rates/reviews/reports > staff sees report; no known P0. Do not start Phase 2 monetization or ads placement before that.

## Known drift register (seed; update on every audit)
| ID | Drift | Owner skill |
|---|---|---|
| D-01 | `admin_dashboard` view omits `pending_count`, `report_count`, `users`, `recent_reviews`; template reads them | django-backend |
| D-02 | CSP `script-src 'self'` with many inline `<script>` blocks (theme toggle, submit AJAX, dashboard, Yektanet): verify in a browser for CSP violations; fix with nonces | security |
| D-03 | Two base templates and two theme systems (`directory/base.html` lacks theme variables) | ui-ux |
| D-04 | `edit_website.html` uses undefined `safeTagName`; inline `onclick` with raw tag names | ui-ux + security |
| D-05 | Edit-resets-to-pending rule: conventions say reset, view resets only on major change, messages differ | product-requirements |
| D-06 | `.claude/agents/*` vs `.claude/skills/*` duplicates | documentation |
| D-07 | Success page and about page promise emails/addresses that do not exist | facts-register |
| D-08 | Duplicate Persian utilities (`farsi/templatetags/utils.py` vs `farsi_tags.py`) | persian-qa |

## Decision log
| Date | Decision | Reason |
|---|---|---|
| 2026-11-18 | Canonical skill path `.claude/skills/<name>/SKILL.md`; original skill names kept | Claude Code reads that layout; renames would break references |
| 2026-11-18 | `naming-law` is non-dismissable | Name drift caused repeated modal/ID/context bugs |

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
