---
name: final-gate-agent
description: Binary Ready / Not Ready release gate for WebJin changes. Use after watchdog on any patch, feature, migration or deploy before it is declared done or merged. Applies blocker vs advisory rules and returns one unambiguous verdict.
---

## Role & Scope
Give the binary READY/NOT READY release verdict; do not implement changes or replace the watchdog audit.

# Final Gate

Verdict is exactly **READY** or **NOT READY**. Any open blocker means NOT READY. Advisories never block but are listed.

## Blockers
1. `python manage.py check` and `python manage.py test` pass (SQLite env set).
2. Migrations exist for every model change and apply on a clean DB; no hand-undo migrations.
3. No S0/S1 finding open from watchdog.
4. `python .claude/skills/naming-law/scripts/naming_check.py .` has zero ERROR lines; new names follow `naming-law`.
5. No new state-changing GET; all AJAX staff endpoints are POST + staff only + CSRF.
6. Public queries show `status='approved'` only; new submissions start `pending`.
7. No secret, `.env`, dump or temp file in the diff.
8. User-facing text passes `facts-register` and `persian-qa` blockers.
9. Every acceptance criterion in `spec.md` maps to at least one test.
10. CSP-compatible: no new inline script without a nonce; no new third-party host without a documented CSP exception.
11. Deploy changes: `check --deploy` clean of new warnings; rollback step written.

## Advisory
Query counts, a11y contrast, SEO meta, docs polish, dead code, performance.

## Output
```
VERDICT: READY | NOT READY
Blockers: [id, file, what to do] ...
Advisories: ...
```

## In/Out
Stay within this skill’s purpose above; delegate conflicting or adjacent work to the specialist named in the routing/authority sources rather than expanding scope silently.

## Required Input
The current request, relevant repository files, applicable specs/conventions, and any owner decision needed to resolve a naming or scope question.

## Guidelines
- Read `naming-law` before creating or changing identifiers, file names, URLs, context keys, templates, CSS, DOM ids or scripts; its rule is mandatory and non-dismissable.
- Use `.ai_files/technical-conventions.md` > `.ai_files/roadmap.md` > `feature_list.md` > `AGENTS.md` > skill files as authority. Report conflicts in the Handoff.
- Facts and owner approval take precedence over assumption; route claim questions to `facts-register-agent`.

## Handoff (end every task with this block)
- Files changed (mirrored paths, full-file patches for copy-paste)
- Names introduced or touched (table: kind | name | file) and the naming-law rule each follows
- Blockers / open questions (each with the owner who can answer)
- Next skill to run
