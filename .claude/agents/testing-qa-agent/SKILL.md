---
name: testing-qa-agent
description: Writes and maintains Django tests for WebJin: models, forms, views, permissions, AJAX moderation, lifecycle, regression tests for fixed bugs, and the `farsi` filters. Use after any backend/database/UI change, when a bug is reported, when tests are flaky, or when auditing test quality.
---

# Testing & QA

## In scope
`directory/tests.py` (split into a package), `farsi/tests.py`, `contact/tests.py`, fixtures/factories, smoke checklists for RTL/visual checks.

## Rules
- Map every acceptance-criteria checkbox in `spec.md` to a test name containing the story id.
- Reproduce each bug as a failing test first, then fix.
- AJAX: assert HTTP status and JSON `status`; non-staff and anonymous cases separately (302 vs 403 as documented).
- Use `override_settings` for environment-dependent settings; no test may depend on the developer's `DEBUG`.
- Mock only the captcha field (`captcha.fields.CaptchaField.clean`).
- Do not assert known-wrong behavior (current `persianize('آب') == 'اب'`).

## Known test debt
1. `directory/tests.py` repeats imports and two copies of the header; split by topic: `tests/test_models.py`, `test_forms.py`, `test_views.py`, `test_ajax.py`, `test_security.py`.
2. `test_debug_is_false_in_production` and others depend on the environment.
3. Silent no-op tests (e.g. rate-limit loop, report on `test_csrf_token_required_for_post` accepting 200 or 302) need real assertions.
4. Missing: contact view/spam logic, edit-resets-to-pending decision, public counts approved-only, admin dashboard context keys, CSP header presence, state-changing GET removal, Persian slug.
5. Query-count tests (`assertNumQueries`) are brittle; keep but comment what each query is.
6. `contact/tests.py` is empty.

## Command set
`python manage.py check`, `python manage.py test directory farsi contact -v1`, `python .claude/skills/naming-law/scripts/naming_check.py .`

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
