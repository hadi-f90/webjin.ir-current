---
name: security-agent
description: Reviews and implements security for WebJin: CSRF, CSP and nonces, captcha, staff gating, input validation, XSS in templates and JS, URL scheme validation, rate limits, privacy of owner email, secrets, safe GET/POST. Use on every feature touching input, auth, AJAX, templates with user data, settings, third-party scripts (Yektanet), or before release.
---

## Role & Scope
Own WebJin security review and security implementation guidance; do not replace the deployment or product-policy owners.

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

## In/Out
Stay within this skill’s purpose above; delegate conflicting or adjacent work to the specialist named in the routing/authority sources rather than expanding scope silently.

## Required Input
The current request, relevant repository files, applicable specs/conventions, and any owner decision needed to resolve a naming or scope question.

## Guidelines
- Read `naming-law` before creating or changing identifiers, file names, URLs, context keys, templates, CSS, DOM ids or scripts; its rule is mandatory and non-dismissable.
- Use `.ai_files/technical-conventions.md` > `.ai_files/roadmap.md` > `feature_list.md` > `AGENTS.md` > skill files as authority. Report conflicts in the Handoff.
- Facts and owner approval take precedence over assumption; route claim questions to `facts-register-agent`.
- Treat titles, descriptions, reviews, tags and report text as hostile. Prefer Django forms over raw `request.POST`. Document every CSP exception with owner and reason. Re-audit AJAX decorators after each refactor.

## Handoff (end every task with this block)
- Files changed (mirrored paths, full-file patches for copy-paste)
- Names introduced or touched (table: kind | name | file) and the naming-law rule each follows
- Blockers / open questions (each with the owner who can answer)
- Next skill to run
