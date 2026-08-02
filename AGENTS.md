# AGENTS.md — WebJin (dirweb.ir / webjin.ir)

> **Purpose:** Single entry point for *any* AI coding agent (Claude, Copilot,
> Cursor, ChatGPT, Grok, Aider, Continue, etc.). Read this file first, then
> follow the links to deeper sources of truth.

---

## 1. Project in one paragraph

**WebJin** is a Persian (Farsi-first, RTL) web directory. Visitors browse approved
Iranian/Farsi websites by category and tags, search, and submit new sites (captcha).
Staff moderate submissions from a custom dashboard (AJAX approve/reject/edit).
Registered users can rate, review, and report. Tags replace subcategories; there is
no nested category tree.

Live domains: [webjin.ir](https://webjin.ir) / [dirweb.ir](https://dirweb.ir)

---

## 2. Canonical sources of truth (read order)

| Priority | File | What it contains |
|----------|------|------------------|
| 1 | `.ai_files/technical-conventions.md` | Locked stack, lifecycle, AJAX JSON shape, security, naming |
| 2 | `.ai_files/roadmap.md` | Phased plan (MWS → Phase 4) + decision matrix + success criteria |
| 3 | `feature_list.md` | Living bug/feature checklist (day-to-day open items) |
| 4 | This file (`AGENTS.md`) | Onboarding, commands, do/don't for every agent |

If any instruction conflicts, **technical-conventions.md wins**.

### Sequential specialist agents (Claude Code / compatible tools)

Under `.claude/agents/*/SKILL.md`:

1. `product-requirements-agent` → writes `spec.md`
2. `ui-ux-agent` → templates / Bootstrap RTL / progressive enhancement
3. `django-backend-agent` → views, forms, URLs, AJAX
4. `database-agent` → models, migrations, querysets
5. `security-agent` → CSP, CSRF, secrets, permissions
6. `testing-qa-agent` → tests and acceptance checks
7. `documentation-agent` → docs and changelog

Use them when the tool supports custom agents; otherwise stay inside this file +
the two `.ai_files` docs.

---

## 3. Stack (do not invent alternatives)

- **Python 3.11+**, **Django 6.x**
- Apps: `directory` (core), `contact`, `farsi` (Persian template tags **only** —
  `FarsiSaz` was merged/removed), `config`
- Frontend: Bootstrap 5 **RTL**, Bootstrap Icons, Vazirmatn (bundled under `static/`)
- Tags: **django-taggit**
- Captcha: django-simple-captcha
- Forms: django-crispy-forms + crispy-bootstrap5 where used
- Security: django-csp, Django security middleware, WhiteNoise for static
- DB: **SQLite when `DEBUG=True`**; **MySQL utf8mb4 when `DEBUG=False`**
- Display dates: Gregorian in DB; Jalali only via `farsi` filters
  (`to_jalali`, `to_hindi`, `truncate_persian`, …). Load with `{% load farsi_tags %}`
  (or compatibility `{% load jalali_filters %}`).

---

## 4. Quick start (local)

```bash
python -m venv .venv && source .venv/bin/activate   # or Windows equivalent
pip install -r requirements.txt
cp .env.example .env                                 # then edit values
python manage.py migrate
python manage.py createsuperuser                     # optional
python manage.py runserver
```

**Required env vars** (see `.env.example`):

| Variable | Dev example | Prod |
|----------|-------------|------|
| `DJANGO_SECRET_KEY` | long random string | **unique** long random string |
| `DEBUG` | `True` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | `webjin.ir,www.webjin.ir,dirweb.ir,www.dirweb.ir` |
| `MYSQL_DATABASE` / `MYSQL_USER` / `MYSQL_PASSWORD` / `MYSQL_HOST` | (ignored in DEBUG) | real production values |

Never commit `.env` or real secrets. `settings.py` must raise if
`DJANGO_SECRET_KEY` is missing.

---

## 5. Project layout (what lives where)

```
config/           # settings, urls, wsgi/asgi
directory/        # models, views, forms, templates, templatetags, management
contact/          # contact form
farsi/            # Persian templatetags + widgets (single app)
templates/        # site-wide base, navbar, footer, error pages
static/           # source CSS/JS/fonts/img (committed)
staticfiles/      # collectstatic output (do not hand-edit)
.ai_files/        # roadmap + technical-conventions
.claude/agents/   # specialist SKILL.md files
scripts/          # maintenance scripts (e.g. clean_junk.sh)
```

---

## 6. Website lifecycle (do not change without a product decision)

- Status: `pending` → `approved` | `rejected`
- Public index/detail show only `status='approved'`
- New submissions always start `pending`
- Owner edit of an approved site should reset to `pending` (confirm per-view)
- Tags via taggit; categories are a flat FK (no nested trees)

---

## 7. AJAX contract (staff endpoints)

- Decorator: `require_POST` + `staff_member_required` (or equivalent)
- Response shape: `{"status": "success"|"error", "message": "...", ...}`
- CSRF: send `X-CSRFToken` from cookie or meta tag + form body token
- Progressive enhancement: forms work without JS

---

## 8. Common commands

```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py makemigrations
python manage.py test
python manage.py runserver
python manage.py collectstatic --noinput   # production
python manage.py check --deploy            # production readiness
bash scripts/clean_junk.sh                 # remove dump/tmp junk
```

---

## 9. Do / Don't for agents

**Do**

- Keep changes minimal and scoped to the requested task
- Run or update tests for the area you touch
- Prefer existing patterns in `directory/views.py` and forms
- Load `farsi_tags` in any template that uses Persian filters
- Put secrets only in environment variables
- After model changes, include a migration

**Don't**

- Reintroduce `FarsiSaz` or a second Persian app
- Commit `.env`, DB dumps, `concatenated_output.txt`, or editor temp files
- Hardcode `SECRET_KEY`, DB passwords, or `DEBUG = True` for production
- Invent nested categories or change the status lifecycle without a product note
- Edit minified CSS/JS under `static/` unless explicitly asked
- Large cross-cutting refactors without tests and an agreed plan

---

## 10. Files agents edit most often

- `config/settings.py` — env-driven config only
- `directory/models.py` — Category, Website, Rating, Review, Report
- `directory/forms.py` — WebsiteSubmitForm, QuickSubmitForm, Rating/Review/Report
- `directory/views.py` + `directory/urls.py`
- `directory/templates/directory/*`
- `farsi/templatetags/farsi_tags.py` (+ `jalali_filters.py` shim)
- `templates/_base.html`, `_navbar.html`, `_footer.html`

---

## 11. Known P0/P1 items (see roadmap for full matrix)

1. Move all secrets to env; rotate the previously committed MySQL password
2. Fix `QuickSubmitForm.Meta`
3. Add `{% load farsi_tags %}` to `website_card.html`
4. Remove broken `farsi/templatetags/farsi.py` and junk files
5. Deduplicate WhiteNoise middleware registration

---

## 12. Deployment notes (Passenger / host)

- Entry: `passenger_wsgi.py` or `config.wsgi:application`
- Set env vars in the host panel / systemd / Passenger config — **not** in code
- `DEBUG=False`, HTTPS redirect, HSTS, secure cookies only when not DEBUG
- Run `collectstatic` and `migrate` on deploy
- After rotating any leaked password, update the host env and restart the app

---

## 13. Questions to ask the user if unclear

- Prefer direct commit vs patch/PR?
- Is there a staging host or only production + local?
- Should Quick submit and full submit stay as two UX paths or one?

---

*Generated for multi-agent use. Keep this file short, accurate, and free of secrets.*
