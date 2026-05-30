# AGENTS: Developer/AI Agent Instructions

Purpose: concise, actionable guidance to help an AI coding agent be immediately productive in this Django repository.

Summary

- Type: Django web project (apps: `directory`, `contact`, `farsi`, `FarsiSaz`, ...)
- DB: default SQLite at `db.sqlite3` (development)

Quick start (for agents)

- Create and activate a virtualenv: `python -m venv .venv && source .venv/bin/activate`
- Install deps: `pip install -r requirements.txt`
- Apply migrations: `python manage.py migrate`
- Run tests: `python manage.py test`
- Run dev server: `python manage.py runserver`

Where to look first

- Project entry: `manage.py` (Django CLI). See `config/settings.py` for settings and installed apps.
- Main apps: `directory/`, `contact/`, `farsi/`, `FarsiSaz/` — each follows Django app layout. Look in their `models.py`, `views.py`, `urls.py`, and `templates/` for behavior.
- Templates: top-level `templates/` and app-level `templates/` directories contain site layout fragments (`_base.html`, `_navbar.html`).
- Static assets: `static/` and `staticfiles/` contain CSS/JS/fonts.

Conventions & notes for agents

- Keep changes minimal and focused to the user-requested task. Preserve existing code style and naming.
- Tests exist in app `tests.py` files; run the test suite locally before proposing changes.
- Database migrations are tracked under `*/migrations/`. If a model change is required, add a migration with `python manage.py makemigrations` and include it in the patch.
- This repo contains Persian-language helpers and widgets (see `farsi/` and `FarsiSaz/`). Be conservative modifying localization logic; ask before wide refactors.
- Static assets are prebuilt in `static/` — avoid wholesale changes to compiled/minified files unless requested.

Common tasks and commands (copyable)

- Install deps: `pip install -r requirements.txt`
- Migrate DB: `python manage.py migrate`
- Run tests: `python manage.py test`
- Create migrations: `python manage.py makemigrations`
- Run server: `python manage.py runserver`

Files an agent will often edit

- [manage.py](manage.py) — entrypoint for Django commands
- [config/settings.py](config/settings.py) — settings, installed apps
- [directory/models.py](directory/models.py) — core models for listings
- [templates/\_base.html](templates/_base.html) — base site layout

What to avoid unless asked

- Editing minified CSS/JS in `static/` (prefer changing source and rebuilding).
- Large cross-cutting refactors without tests and an explicit plan.

Links to repo docs

- Read project README: [README.md](README.md)
- Requirements: [requirements.txt](requirements.txt)

If you need more granular agent behaviors

- Suggestion: split agent instructions by area (backend, templates, static build). Use `/create-skill` or request an additional AGENTS.md section.

Questions for the user

- Do you prefer changes committed directly or presented as a patch/PR?
- Is there a CI workflow or branch policy I should follow (not present in repo)?

--
Generated/updated by AI agent to help coding assistants quickly understand and act on small, focused tasks.
