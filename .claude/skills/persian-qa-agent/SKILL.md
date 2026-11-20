---
name: persian-qa-agent
description: Persian/RTL quality checker for WebJin templates, messages and the `farsi` app. Use whenever Persian text, digits, dates, punctuation, half-spaces, RTL layout, `farsi_tags` filters or form labels are written or changed, before any release, and when Persian output looks wrong (broken slugs, wrong letters, Latin digits).
---

## Role & Scope
Review Persian/RTL text, digits, dates, typography, and `farsi` app behavior; localization never permits Persian identifiers.

# Persian QA

## Checklist (blocker = B, advisory = A)
- B: UI strings are Persian only; identifiers English (naming-law 1).
- B: `<html lang="fa" dir="rtl">` on every page (the Bootstrap LTR build used by `_head.html` is wrong for Persian pages).
- B: Arabic letters ي ك and Arabic-Indic digits only via `persianize`; stored titles are normalized on save.
- B: no leftover placeholders in copy (`TODO`, `[PLACEHOLDER]`, lorem, test text).
- B: one vocabulary per glossary term (`naming-law` 5): دیدگاه, ایمیل, وب‌سایت.
- A: half-space (ZWNJ) in compounds (می‌شود, وب‌سایت, دسته‌بندی); no letter-spacing on Persian.
- A: punctuation « » ، ؟ ؛ and Persian ellipsis; digits shown with `to_hindi` where numbers are content.
- A: dates through `to_jalali*` only; DB stays Gregorian.
- A: long text uses line-height 1.8-2.0; Vazirmatn bundled, no external font CDN.

## Known defects in the `farsi` app (fix with tests)
1. `persianize` maps آ to ا and drops tashkeel; this corrupts words (آب becomes اب) and the current test enforces it. Keep آ, map only ي>ی, ك>ک, ة>ه, Arabic-Indic digits.
2. `to_hindi_with_comma` uses ASCII comma; Persian uses ٬ (thousands) and ٫ (decimal).
3. `persian_ordinal` above 10 appends «م» to the number word: 30 gives «سیم» (should be «سی‌ام») and 100+ falls back to digits; add rules or limit to 1-20.
4. `persian_list` is a `simple_tag`; filters cannot be piped. Decide one form and keep one implementation.
5. `farsi/templatetags/utils.py` duplicates helpers and sits where Django scans for tag libraries; move shared code to `farsi/utils.py`.
6. Django `slugify` drops Persian letters, so Persian titles get `website-<uuid>` slugs; use `slugify(value, allow_unicode=True)` in `Website.save` and forms (and check URL converter `<slug:slug>` accepts unicode: it does not; use `<str:slug>` or a custom converter). Coordinate with seo, database and django-backend.
7. `to_jalali_relative` compares naive `datetime.now()` with timezone-aware values; use `timezone.now()`.

## Tests to add
Round-trip for آ, ZWNJ preservation, digits, Jalali boundaries (Nowruz, leap years), empty and None inputs, long titles with slug fallback.

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
