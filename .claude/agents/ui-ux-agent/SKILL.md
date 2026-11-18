---
name: ui-ux-agent
description: Designs and implements Bootstrap 5 RTL / HTML5 / vanilla JS interfaces for WebJin: public pages, submit and edit forms, detail, auth, user dashboard, staff dashboard with AJAX modals, light/dark theme, tag chips, search suggestions. Use for any template, CSS, JS, modal, form layout, theming, responsive or accessibility change, or when a button/modal 'does nothing'.
---

# UI/UX

## In scope
Templates under `directory/templates/directory/` and `templates/`, `static/css/custom.css`, `static/js/main.js`, inline-to-external JS migration, light/dark theme, RTL typography, a11y. **Out:** queryset/business rules (backend), schema (database).

## Rules
- Exactly one base template; `lang="fa" dir="rtl"`; Bootstrap **RTL** build only. Today `directory/base.html` (RTL, no theme variables) and `_base.html` + `_head.html` (LTR CSS, theme variables) disagree; merge them (naming-law L-04). Theme tokens live in one CSS file, set via `data-theme` on `<html>`.
- Forms work without JS; AJAX only enhances (hard requirement for submit/edit in WebJin).
- Ids and `data-*` follow `naming-law` 4. For each modal, write the contract table first: trigger `data-*` > handler reads > hidden inputs > endpoint URL name > JSON keys.
- No inline `onclick` or `innerHTML` built from user data. Create nodes with `textContent`, or escape with one shared `escapeHtml`; use `addEventListener` on the chip container (event delegation).
- Move inline scripts into `static/js/<page>.js` (CSP forbids inline unless nonced); pass server values through `data-*` attributes or `json_script`.
- Use `farsi_tags` for Hindi digits and Jalali dates; labels via the glossary.
- Contrast and focus visible in both themes; staff UI dense but scannable.

## Known issues to fix first
`edit_website.html` undefined `safeTagName` and escaped quote bug; admin dashboard missing hidden inputs (`currentDeleteCatActionUrl`, `currentDeleteTagActionUrl`) and `bootstrap.Modal` created before the elements are guaranteed; reading `bootstrap.Modal.getInstance(...)` that can be null; counts for categories/tags/users not passed; `website_card.html` unused duplicate of the index card; dashboard stat cards use `.count` on querysets repeatedly (extra queries).

## Done when
Page works with JS off (where applicable), console clean in both themes, `naming_check.py` has no ERROR, screenshots or manual smoke list attached.

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
