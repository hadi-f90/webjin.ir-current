---
name: final-gate-agent
description: Binary Ready / Not Ready release gate for WebJin changes. Use after watchdog on any patch, feature, migration or deploy before it is declared done or merged. Applies blocker vs advisory rules and returns one unambiguous verdict.
---

# Final Gate

Verdict is exactly **READY** or **NOT READY**. Any open blocker means NOT READY. Advisories never block but are listed.

## Blockers
1. `python manage.py check` and `python manage.py test` pass (SQLite env set).
2. Migrations exist for every model change and apply on a clean DB; no hand-undo migrations.
3. No S0/S1 finding open from watchdog.
4. `naming_check.py` has zero ERROR lines; new names follow `naming-law`.
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
