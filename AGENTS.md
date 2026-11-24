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

Under `.claude/skills/<skill-name>/SKILL.md`:

Read `naming-law` before creating or changing any name. Route project requests
through `orchestrator-agent`, which chooses the appropriate chain and decision
path. A typical feature chain is:

1. `product-requirements-agent` → testable `spec.md`
2. `ui-ux-agent`, `django-backend-agent`, and `database-agent` as needed
3. `security-agent` and `testing-qa-agent`
4. `persian-qa-agent` when Persian/RTL content or behavior is involved
5. `watchdog-agent` → cross-layer audit and findings
6. `final-gate-agent` → binary release verdict
7. `documentation-agent` → docs and skill registry

Other skills in the registry below retain their focused scopes. When custom
skills are unavailable, follow the corresponding skill files manually along
with the canonical sources of truth above.

Complete skill registry (all existing skills; no new skills):

| Skill | Canonical path |
|---|---|
| `analytics-metrics-agent` | `.claude/skills/analytics-metrics-agent/SKILL.md` |
| `business-model-agent` | `.claude/skills/business-model-agent/SKILL.md` |
| `conversion-monetization-agent` | `.claude/skills/conversion-monetization-agent/SKILL.md` |
| `database-agent` | `.claude/skills/database-agent/SKILL.md` |
| `deployment-agent` | `.claude/skills/deployment-agent/SKILL.md` |
| `django-backend-agent` | `.claude/skills/django-backend-agent/SKILL.md` |
| `documentation-agent` | `.claude/skills/documentation-agent/SKILL.md` |
| `facts-register-agent` | `.claude/skills/facts-register-agent/SKILL.md` |
| `final-gate-agent` | `.claude/skills/final-gate-agent/SKILL.md` |
| `growth-agent` | `.claude/skills/growth-agent/SKILL.md` |
| `naming-law` | `.claude/skills/naming-law/SKILL.md` |
| `orchestrator-agent` | `.claude/skills/orchestrator-agent/SKILL.md` |
| `persian-qa-agent` | `.claude/skills/persian-qa-agent/SKILL.md` |
| `product-requirements-agent` | `.claude/skills/product-requirements-agent/SKILL.md` |
| `security-agent` | `.claude/skills/security-agent/SKILL.md` |
| `seo-agent` | `.claude/skills/seo-agent/SKILL.md` |
| `testing-qa-agent` | `.claude/skills/testing-qa-agent/SKILL.md` |
| `ui-ux-agent` | `.claude/skills/ui-ux-agent/SKILL.md` |
| `watchdog-agent` | `.claude/skills/watchdog-agent/SKILL.md` |

`naming-law` is mandatory and non-dismissable across every skill. Task-level
instructions cannot override it; only an explicitly owner-approved amendment
may change it. It applies to every identifier, key, route, template, CSS class,
DOM id, script symbol, file name and project glossary term.

---

## 3. Stack (do not invent alternatives)

- **Python >=3.12**, **Django 6.0.3 pinned** in `requirements.txt`
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
.claude/skills/   # specialist SKILL.md files
scripts/          # maintenance scripts (e.g. clean_junk.sh)
```

---

## 6. Website lifecycle (do not change without a product decision)

- Status: `pending` → `approved` | `rejected`
- Public index/detail show only `status='approved'`
- New submissions always start `pending`
- Owner-facing edit of an approved site resets it to `pending`; staff dashboard edits preserve status
- Soft deletion uses a separate flag, hides a website from public discovery, and follows `.ai_files/specs/website-soft-delete.md` for owner/staff trash and restore access.
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

## 11. Known operational follow-up

- Rotate the previously committed MySQL password in the host environment if
  that operational action has not already been completed; never add it here.

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


## Profitability-related agents

| Agent | When to use | Output |
|-------|-------------|--------|
| `business-model-agent` | Strategy: what to sell | `business-model-report.md` |
| `growth-agent` | Traffic + listing supply | `growth-plan.md` |
| `analytics-metrics-agent` | KPIs + instrumentation map | `metrics-framework.md` |
| `conversion-monetization-agent` | Paid UX + disclosure | `conversion-spec.md` |
| `seo-agent` | Organic acquisition | `seo-report.md` |

**Later phases (skills not required yet):** partnerships-bd, ad-ops-publisher, competitive-intel, lifecycle-crm — scheduled in `.ai_files/roadmap.md`.

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. When the answer is under a Markdown heading, `graphify section "<heading>"` prints that section's text, so the .md need not be opened. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- Dirty graphify-out/ files are expected after hooks or incremental updates; dirty graph files are not a reason to skip graphify. Only skip graphify if the task is about stale or incorrect graph output, or the user explicitly says not to use it.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

# graphify
- **graphify** (`.claude/skills/graphify/SKILL.md`) - any input to knowledge graph. Trigger: `/graphify`
When the user types `/graphify`, use the installed graphify skill or instructions before doing anything else.
