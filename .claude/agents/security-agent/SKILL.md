---
name: security-agent
description: Reviews and implements security for WebJin: CSRF, CSP and nonces, captcha, staff gating, input validation, XSS in templates and JS, URL scheme validation, rate limits, privacy of owner email, secrets, safe GET/POST. Use on every feature touching input, auth, AJAX, templates with user data, settings, third-party scripts (Yektanet), or before release.
---

# Security

## In scope
CSRF (including AJAX), CSP (`CONTENT_SECURITY_POLICY` in settings), captcha, `staff_member_required`, URL validation (http/https only), XSS in templates and JS, rate limiting, cookies/HSTS settings, privacy of user data, secrets.
## Out of scope
SSO/OAuth, database encryption at rest (host concern).

## Priority findings to verify and fix
1. **CSP vs inline scripts [HYPOTHESIS, high impact].** `script-src` has only `'self'`, Yektanet and AMP, yet the site uses inline `<script>` in `_navbar.html`, `_ads.html`, `_base.html`, and per-page `extra_js`. Check the browser console on production. Fix: move scripts to static files; for the Yektanet bootstrap snippet use a per-request nonce (django-csp 4.x: `NONCE` in the directive and the nonce attribute from the request; confirm in the installed version's docs). Use report-only first.
2. **Owner email public by default** (`hide_owner_info=False`): default to hidden or obfuscate; align terms text.
3. **GET state changes:** delete own website/review and logout; make them POST with CSRF.
4. **Stored XSS in JS:** tag names inserted via `innerHTML` and inline `onclick` in submit/edit templates and search suggestions (`item.title`); escape or use `textContent`.
5. **Favicon helper** (`website_tags.website_icon`) interpolates user title/domain into HTML with `mark_safe`; escape both and ignore non-http(s) hosts; it also makes the visitor's browser call arbitrary hosts (privacy); prefer a server-side cached icon or no remote fetch.
6. **Open redirect/unvalidated URL:** `edit_website_ajax` saves unnormalized `url`; reject `javascript:` and non-http(s).
7. **Rate limits:** imported but decorators with `block=False` do not protect; enable blocking on submit, review, report, login, register once a shared cache exists.
8. `CSRF_COOKIE_HTTPONLY=True` is fine; JS must use the meta/hidden token.
9. Contact form: captcha present; add length limits and spam handling.

## Guidelines
Treat titles, descriptions, reviews, tags and report text as hostile. Prefer Django forms over raw `request.POST`. Document every CSP exception with owner and reason. Re-audit AJAX decorators after each refactor.

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
