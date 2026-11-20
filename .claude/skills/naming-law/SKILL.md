---
name: naming-law
description: NON-DISMISSABLE project law for naming everything in WebJin: Python variables, models, related_names, URL names and paths, template/block names, context keys, DOM ids, JS, CSS, static files, enums and the Persian/English glossary. Use whenever ANY code, template, migration, test, URL or skill is created, renamed, reviewed or audited, even for a one-line change, and before any other skill adds a name.
---

## Role & Scope
Own the mandatory project-wide naming standard and its owner-approved amendments.

# Naming Law

## In/Out
In: naming rules, glossary, legacy exceptions, and amendment procedure. Out:
implementation decisions, which remain with the relevant specialist; no
specialist may waive or narrow this law.

## Required Input
The proposed or existing name, its language/context, and the relevant code,
template, route, database or API surface.

**Status: NON-DISMISSABLE.** No agent, skill, task or chat instruction may waive it. Only the owner can amend it, and only through the Amendment procedure (section 9). If a task seems to need a name that breaks this law, stop and report it in the Handoff.

## 1. Language rule
- Every project identifier and symbol must be **English**, ASCII. This includes
  variables and all other code symbols, database fields, public/data/API names,
  keys, routes, templates and blocks, CSS, JavaScript, DOM ids, filenames, enum
  values, and glossary terms.
- Use casing appropriate to the language and artifact: Python variables and
  functions `snake_case`, Python classes `PascalCase`, JavaScript variables and
  functions `camelCase`, constants `UPPER_SNAKE`, CSS classes and URL paths
  `kebab-case`, templates `snake_case`. Follow the detailed rules below.
- User-visible text (templates, messages, `verbose_name`, help text): **Persian**. Never put Persian in identifiers or URL paths.
- Localized Persian prose or UI text never authorizes Persian code identifiers.
- Storage: Gregorian datetimes; Jalali and Hindi digits are display-only via `farsi_tags`.

## 2. Python
| Kind | Rule | Example |
|---|---|---|
| variable, function, module, field | `snake_case` | `website_count`, `update_rating` |
| class | `PascalCase` | `PublicWebsiteSubmitForm` |
| constant, enum value holder | `UPPER_SNAKE` | `STATUS_CHOICES` |
| form | `<Thing>Form` | `ReportForm` |
| boolean | `is_` / `has_` prefix | `is_resolved`, `is_approved` (legacy `hide_owner_info` stays until amended) |
| count | `<thing>_count`, int | `pending_count` |
| queryset / list | plural noun | `reviews`, `related_websites` |
| single object | singular noun | `website`, `selected_category` |
| selected filter | `selected_<thing>` (object) and `<thing>_slug` (raw GET value) | `selected_tag`, `tag_slug` |
- Status values are exactly `pending`, `approved`, `rejected`. New code reads them from one model-level constant, never retyped literals.
- `related_name`: plural snake_case noun (`websites`, `ratings`, `reviews`, `reports`). Never `*_set`.

## 3. Django surface
- **View functions:** pages `<noun>` or `<noun>_<page>` (`website_detail`, `user_dashboard`); actions `<verb>_<noun>` (`submit_website`, `rate_website`); AJAX views end in `_ajax` (`approve_website_ajax`).
- **URL names** equal the view function name. One view, one URL name (no aliases).
- **URL paths:** kebab-case; every AJAX endpoint lives under `/ajax/`; resources use `<slug:slug>` or `<int:pk>`.
- **Templates:** `snake_case.html`; partials start with `_` (`_website_card.html`); exactly **one** base template for the public site.
- **Block names:** `title`, `head`, `content`, `extra_css`, `extra_js` only. A child may not define a block its parent lacks.
- **Template tags/filters:** one implementation per behavior inside `farsi/templatetags/farsi_tags.py`; `to_*` converts, `persian_*` formats.
- **Static files:** lowercase kebab-case; one file per purpose (`custom.css` only).
- **JSON contract:** `{"status": "success"|"error", "message": "...", ...}`; extra keys are snake_case.

## 4. Front end
| Kind | Rule | Example |
|---|---|---|
| DOM id used by JS | `camelCase`, `<action><Entity><Element>` | `editWebsiteTitle`, `saveAddTagBtn` |
| modal id | `<action><Entity>Modal` | `confirmStatusModal` |
| hidden state input | `current<Entity><Action>Url` | `currentDeleteActionUrl` |
| CSS class (own) | kebab-case; Bootstrap classes untouched | `tag-chip` |
| `data-*` attribute | kebab-case, mirrors what JS reads | `data-action`, `data-status` |
| JS variable/function | `camelCase`, functions start with a verb | `renderChips()` |
| JS constant | `UPPER_SNAKE` | `MAX_TAGS` |
- Every id read by JS must exist in the same rendered page; every `data-*` read by JS must be set by the trigger. This pair is the top recurring bug source.
- No inline `onclick` built from user data.

## 5. Domain glossary (baseline; the owner may amend once, see section 9)
| Code | Persian UI | Notes |
|---|---|---|
| Website | وب‌سایت | never `Site`/`Listing` in code |
| Category | دسته‌بندی | flat, no tree |
| Tag | برچسب | taggit |
| Rating | امتیاز | 1-5 |
| Review | دیدگاه | UI currently mixes «نظر» (legacy) |
| Report | گزارش | abuse/broken-link report |
| `created_by` | ثبت‌کننده | the submitting account |
| `owner_name`, `owner_email` | نام/ایمیل صاحب وب‌سایت | contact data of the site's owner, not the account |
| Staff dashboard / User dashboard | پنل مدیریت / پنل کاربری | |
| ایمیل | not «رایانامه» | contact app uses «رایانامه» (legacy) |

## 6. Legacy exceptions register (finite; never copy these into new code)
| ID | Where | Violation | Target |
|---|---|---|---|
| L-01 | `Category.website_set` related_name | `_set` | `websites` (migration + templates + tests) |
| L-02 | url name `approve_website`; paths `approve/<pk>/`, `resolve-report/<pk>/`, `add-tag/` | missing `_ajax`, missing `/ajax/`, alias `add_tag` | `approve_website_ajax`, `/ajax/approve/<pk>/` etc., drop alias |
| L-03 | `website_card.html`, `paginator.html` | partial without `_` | `_website_card.html`, `_paginator.html`; index inlines the card, so `website_card.html` is dead or must be adopted |
| L-04 | `directory/base.html` and `templates/_base.html` | two base templates with different theme systems | one base (owner picks) |
| L-05 | `contact.html` block `extrajs`; error pages `meta_title`/`meta_description` | block not defined by parent | `extra_js`; add or drop blocks |
| L-06 | admin_dashboard context `pending/approved/rejected/reports/tags` | counts and `users`, `recent_reviews`, `pending_count`, `report_count` used by template but not passed | `pending_websites`, ... plus the missing keys |
| L-07 | `farsi/templatetags/utils.py` | duplicates `truncate_persian`, `to_persian_num` of `farsi_tags`; not a tag library | single implementation |
| L-08 | `tag_suggestions` in `forms.py` | view outside `views.py` | move |
| L-09 | ids `tagInput` (form widget and manual input), `confirmModal` unused, missing `currentDeleteCatActionUrl`, `currentDeleteTagActionUrl` | id collisions / dangling | unique, defined ids |
| L-10 | «نظر» vs «دیدگاه», «ایمیل» vs «رایانامه», «سایت» vs «وب‌سایت» | mixed vocabulary | glossary terms |
| L-11 | `custome.css` (if present) | typo duplicate | delete |

Retiring an entry needs a patch that changes the name everywhere (code, templates, tests, docs) in one change.

## 7. Pre-flight (run before handing off)
```bash
python .claude/skills/naming-law/scripts/naming_check.py .
grep -rn "related_name='[a-z_]*_set'" directory
grep -rn "{% block " templates directory/templates | sort | uniq -c
```
The script reports undefined URL names, blocks not defined by the parent, JS ids that do not exist in the page, partials without `_`, and `*_set` related names.

## 8. Review checklist
- [ ] Every new name appears in the Handoff table with its rule
- [ ] No Persian in identifiers; no English in user-visible strings
- [ ] No new legacy-pattern name; legacy entries touched are retired or untouched
- [ ] URL name = view name; AJAX under `/ajax/`
- [ ] JS ids and `data-*` match the HTML

## 9. Amendment procedure
1. Agent writes a proposal (rule, reason, files affected, migration plan).
2. Owner approves in writing in the chat.
3. Add a row below and update affected skills in the same patch.

| Date | Change | Approved by |
|---|---|---|
| 2026-11-18 | Law and mandatory scope approved for this maintenance direction | Owner (approved in task) |

## Guidelines
- Treat the rules above as mandatory and non-dismissable across every skill.
- Preserve established names. Do not rename public, data, or API names without
  an explicit owner-approved migration decision.
- Only an explicit owner-approved amendment can change this law; task-level
  instructions cannot override it.

## Handoff (end every task with this block)
- Files changed (mirrored paths, full-file patches for copy-paste)
- Names introduced or touched (table: kind | name | file) and the naming-law rule each follows
- Blockers / open questions (each with the owner who can answer)
- Next skill to run
