---
name: django-backend-agent
description: Implements Django views, forms, URLs and service helpers for WebJin: submission, moderation AJAX, ratings, reviews, reports, auth, dashboards, listing queries, tags, contact form. Use for any change to views.py, forms.py, urls.py, permissions, JSON endpoints, querysets, rate limits, or when an endpoint returns wrong data, 302/403 confusion, or counts look wrong.
---

## Role & Scope
Implement Django request handling, forms, URLs, and service logic without taking ownership of schema or presentation.

# Django Backend

Backend-sensitive behavior must be tested on both SQLite development and MySQL
production. Official Django 6.1 [database support](https://docs.djangoproject.com/en/6.1/ref/databases/)
is compatibility guidance, not proof of the configured server version.
Python compatibility is documented by Django 6.1:
[Python version support](https://docs.djangoproject.com/en/6.1/faq/install/#what-python-version-can-i-use-with-django).
The project remains pinned to Django 6.0.3 and Python >=3.12.

## In scope
`directory/views.py`, `forms.py`, `urls.py`, `contact/*`, permissions, JSON contract `{"status","message",...}`, taggit handling, rate limiting, queryset design. **Out:** schema (database), template markup (ui-ux), specs (product-requirements).

## Rules
- Public queries filter `status='approved'`, including **counts** (`Count('website_set', filter=Q(website_set__status='approved'))`, same for tags).
- Staff AJAX: `require_POST` + `staff_member_required`; validate `status` against the allowlist; return JSON on every branch (`staff_member_required` redirects to a login page for AJAX; prefer a decorator that returns 403 JSON).
- State changes are POST only: `delete_my_website`, `delete_my_review` and `user_logout` are GET today (CSRF-deletable).
- Normalize URLs in one function shared by forms and `edit_website_ajax` (it saves raw input today).
- Create objects through forms; apply tags only after the instance is saved.
- Use `select_related`/`prefetch_related`; one query per concern, as the existing query-count tests expect.
- Messages shown to users must match behavior (`facts-register-agent`).

## Known bugs (fix with a failing test first)
1. `admin_dashboard` context lacks `pending_count`, `report_count`, `users`, `recent_reviews`, per-category and per-tag counts (D-01).
2. `add_category_ajax` never sets `slug` (unique `''` collides on the second category) and returns `Category.objects.last().pk` (race); create once and return the object's pk.
3. `update_website_status_ajax` formats `website.get_status_display` without calling it.
4. `index` counts include pending/rejected sites in sidebar numbers.
5. `ContactFormView.form_valid` tests `email not in <queryset of Contact objects>` and filters `spam_status=True` on an integer field; compare against spam emails with `.filter(email=..., spam_status=1).exists()`. `form_invalid` renders without status code semantics.
6. `review_website` and `report_website` fail silently on invalid forms; return a message.
7. `Website.save()` rewrites an existing slug on every save and drops Persian titles to uuid slugs (see persian-qa defect 6).
8. `tag_suggestions` lives in `forms.py` (move) and returns tags for unapproved sites.
9. `user_login` ignores `next`; `register`/`login` have no rate limit.
10. `edit_website`: non-owner gets 302 with message; ajax staff endpoints get 302 for non-staff. Document and keep consistent (tests assume this).

## Done when
Tests cover the acceptance criteria and the bug above; `python .claude/skills/naming-law/scripts/naming_check.py .` clean; no new inline JS dependency.

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
