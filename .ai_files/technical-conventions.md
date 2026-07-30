# Technical Conventions — WebJin (dirweb.ir)

Single source of truth for cross-cutting technical decisions.

For day-to-day coding style, see `.ai_files/coding-conventions.md` when it exists.

## Stack

- **Python 3.11+**, **Django 6.x**
- Apps: `directory` (core), `contact`, `farsi` (Persian template tags), `config`
- Frontend: Bootstrap 5 **RTL**, Bootstrap Icons, Vazirmatn (bundled static)
- Tags: **django-taggit** (+ optional autosuggest)
- Captcha: django-simple-captcha
- Forms: django-crispy-forms + crispy-bootstrap5 where used
- Security: django-csp, Django security middleware, WhiteNoise for static
- DB: SQLite in DEBUG; MySQL (utf8mb4) in production
- Optional: Redis cache, django-ratelimit, django-jalali / jdatetime for display

## Language & locale

- Default `LANGUAGE_CODE = 'fa-ir'`, `TIME_ZONE = 'Asia/Tehran'`
- UI strings and templates are **Persian-first, RTL**
- Dates stored as timezone-aware Gregorian in DB; **Jalali display only** via
  `farsi` template tags (`to_jalali`, `to_hindi`, `truncate_persian`)
- Never store Jalali strings in the database

## Website lifecycle

- Status values: `pending` → `approved` | `rejected`
- Public index and detail only show `status='approved'`
- New submissions always start as `pending`
- Owner or staff edit of an approved site **should reset to pending** unless
  staff is editing from admin dashboard (document per-view behavior in specs)
- Tags via taggit `TaggableManager`; categories are a separate `Category` FK
  (tags replace subcategories — do not add nested Category trees)

## URLs & slugs

- Prefer slug-based public URLs: `/website/<slug>/`
- Auto-slugify from title; optional custom slug; uniqueness enforced in model
  `save()` and form `clean_custom_slug`
- Normalize user URLs: if missing scheme, prepend `https://`

## AJAX conventions

- Staff AJAX endpoints: `require_POST` + `staff_member_required`
- JSON shape: `{"status": "success"|"error", "message": "...", ...}`
- CSRF: cookie or `meta[name=csrf-token]`; send `X-CSRFToken` + form body token
- Prefer progressive enhancement: forms work without JS; AJAX is enhancement

## Security

- Secrets only in environment / `.env` (never commit real keys or DB passwords)
- CSP: allow only needed script origins (e.g. Yektanet CDN if ads enabled)
- Captcha on anonymous submit; rate-limit submit/rate/review/report
- Staff dashboard never exposed without `is_staff`
- XSS: escape user content in templates; be careful with `|safe` and favicon HTML

## Static & media

- `STATICFILES_DIRS` → project `static/`; collect to `staticfiles/`
- User uploads under `MEDIA_ROOT` (if added); django-cleanup for orphaned files

## Testing expectations

- Model/form unit tests for URL normalize, slug uniqueness, status transitions
- View tests for permission (anonymous vs staff) on AJAX moderation endpoints
- Template/integration tests for RTL critical paths when feasible

## Naming

- Apps and modules: English identifiers; verbose_name / UI: Persian
- Template package: `directory/templates/directory/`
- URL names: snake_case English (`website_detail`, `admin_dashboard`)
