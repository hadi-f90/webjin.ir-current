# WebJin (وب‌جین) — Persian Web Directory

**Live:** [webjin.ir](https://webjin.ir) / [dirweb.ir](https://dirweb.ir)  
**Stack:** Django 6 · Bootstrap 5 RTL · Vazirmatn · taggit · django-simple-captcha · django-csp

A Farsi-first directory for discovering and submitting Iranian/Persian websites. Visitors browse by category and tags, search, and submit new sites (captcha). Staff moderate submissions from a custom AJAX dashboard. Registered users can rate, review, and report.

---

## Status (2026-08-03)

| Phase | Status |
|-------|--------|
| **Phase 0** — foundation, secrets, forms, tags, error pages, test green | **Done** |
| **Phase 1** — MWS polish (admin modals, submit unify, navbar, permissions UX) | Next |
| **Phase 2+** — SEO, rate-limit productization, dark mode, engagement | Later |

See [`.ai_files/roadmap.md`](.ai_files/roadmap.md) and [`feature_list.md`](feature_list.md).

---

## Features

- **Public discovery:** approved listings, category sidebar, popular tags (top 10), search + live suggestions
- **Submit:** quick public form (title, URL, captcha) → `pending` until staff approves
- **Detail:** description, tags, related sites, ratings, reviews, reports
- **Staff dashboard:** AJAX approve / reject / edit / categories / tags / reports
- **Accounts:** register, login, user dashboard (my sites / reviews)
- **Persian UX:** RTL Bootstrap 5, Vazirmatn, Jalali display via `farsi` templatetags (`to_hindi`, `to_jalali`, `truncate_persian`)
- **Security:** env-based secrets, CSP, captcha on submit, staff-only moderation endpoints

---

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env               # if present; otherwise create .env
# Required:
#   DJANGO_SECRET_KEY=<long random string>
#   DEBUG=True
#   DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

python manage.py migrate
python manage.py createsuperuser   # optional
python manage.py runserver
```

Generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Tests

```bash
python manage.py test directory -v1
python manage.py check
```

### Import commands

```bash
python manage.py import_websites path/to/file.csv
python manage.py import_websites_json path/to/file.json [--default-status pending]
```

CSV columns: `name` (or `title`), `url`, optional `description`, `category`.

---

## Project layout

```
config/           # settings, urls, wsgi
directory/        # core app: models, views, forms, templates, management commands
contact/          # contact form
farsi/            # Persian templatetags (to_hindi, to_jalali, …)
templates/        # site-wide base, navbar, footer, 401/403/404/500
static/           # CSS/JS/fonts (source)
.ai_files/        # roadmap, technical-conventions
.claude/agents/   # optional multi-agent SKILL.md pipeline
```

### Core models (`directory`)

- **Category** — flat list (tags replace subcategories)
- **Website** — status: `pending` | `approved` | `rejected`; taggit tags
- **Rating** — one per user per site (1–5)
- **Review** / **Report**

---

## Configuration

| Variable | Dev | Production |
|----------|-----|------------|
| `DJANGO_SECRET_KEY` | required | required (unique, long) |
| `DEBUG` | `True` | `False` |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost` | `webjin.ir,www.webjin.ir,…` |
| `MYSQL_*` | ignored when DEBUG | required when `DEBUG=False` |

- **Dev DB:** SQLite (`db.sqlite3`)
- **Prod DB:** MySQL utf8mb4 via env vars
- **Never commit** `.env` or real passwords

If a database password ever appeared in git history, **rotate it on the server** and keep the new value only in the host environment.

---

## Production notes (Passenger / host)

1. Set env vars (`DEBUG=False`, secret, hosts, MySQL credentials).
2. `python manage.py migrate`
3. `python manage.py collectstatic --noinput`
4. `python manage.py check --deploy`
5. Restart the app process after env changes.

Entry points: `passenger_wsgi.py` or `config.wsgi:application`.

---

## Agent / contributor docs

| Doc | Purpose |
|-----|---------|
| [`AGENTS.md`](AGENTS.md) | Onboarding for AI/human agents |
| [`.ai_files/roadmap.md`](.ai_files/roadmap.md) | Phased plan + Phase 0 close-out |
| [`.ai_files/technical-conventions.md`](.ai_files/technical-conventions.md) | Stack, lifecycle, AJAX, security |
| [`feature_list.md`](feature_list.md) | Living bug/feature checklist |

---

## License

See [LICENSE](LICENSE).
