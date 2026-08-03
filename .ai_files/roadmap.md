# WebJin (dirweb.ir / webjin.ir) Development Roadmap

Persian web directory for discovering and submitting Iranian/Farsi websites.  
Stack: Django 6, Bootstrap 5 RTL, taggit, django-simple-captcha, django-csp,
Vazirmatn, Jalali via `farsi` app only.

**Tip audited:** `92b7895` (2026-08-03) — forms/settings/card Phase 0 merged;
management commands + tag delete + error templates still open.

---

## Phase 0 — Foundation / crashers (close-out)

### Done on tip

| Item | Notes |
|------|--------|
| Env-driven settings | No plaintext password on tip; `DEBUG` from env |
| `WebsiteSubmitForm` Meta | Full model fields restored |
| `QuickSubmitForm` Meta | `fields = ['title', 'url']` + captcha extra field |
| `website_card.html` | `{% load farsi_tags %}` present |
| `.env.example` | Present |

### Remaining (package: `phase0-remainder`)

| ID | Item | Severity |
|----|------|----------|
| T-E1 | `commands/__init__.py` is a command; imports `websites.models`; `import_websites.py` empty | **P0** — breaks test discovery / command load |
| T-E1b | `import_websites_json.py` imports `your_app.models.WebsiteResource` | **P0** |
| T-E2 | `delete_tag_ajax`: `tag.websites` → must be `tag.websites_tagged` | **P0** |
| T-E3 | `templates/500.html`, `404.html`, `403.html` use `websites:` / `pages:` / `accounts:` namespaces | **P0** — 500 page cannot render |

**Server (not git):** rotate MySQL password that appeared in old commits.

### Phase 0 success criteria

- `python manage.py check` passes  
- `from directory.management.commands import import_websites` works  
- Tag delete AJAX does not AttributeError  
- Raising a 500 in tests does not cause `NoReverseMatch: websites`  
- Public submit + edit form load without Meta/KeyError  

---

## Phase 1 — MWS completion

### Submission & tests

- Unify public submit templates / one success redirect  
- Captcha bypass or mock in tests so lifecycle/CSRF tests get 302  
- `test_slug_uniqueness`: assert distinct slugs (model auto-uniquifies; no IntegrityError)

### Permissions / HTTP

- Non-owner edit & staff AJAX: align **403** vs **302** with tests (or update tests)  
- Invalid pk → 404 when authenticated as staff  

### Admin dashboard

- Modal/ID mismatches (`editWebsiteModal` vs `editModal`)  
- Resolve-report AJAX wired  
- Counts (`pending_count`, category/tag website counts) in context  

### Performance & UX

- Index: `select_related('category')`; limit featured queryset (cuts N+1 / 17 queries)  
- Detail: optional `select_related` / relax query-count assertion  
- Navbar solid after scroll  
- Error pages already fixed in Phase 0 remainder — verify chrome matches site  

### Test hygiene

- SecuritySettingsTests: `@override_settings(DEBUG=False, …)` or skip if DEBUG  
- Long `SECRET_KEY` in test env  

---

## Phase 2 — Polish & trust

- SEO / sitemap / Open Graph  
- Rate limiting restored  
- Email on approve/reject / contact  
- Dark mode  
- Bulk import UX polish  

---

## Phase 3 — Engagement

- Bookmarks, claim site, broken-link checker, view counts, tag merge  

---

## Phase 4 — Ops

- CI: migrate + test + `check --deploy`  
- Staging, backups, document Passenger env  

---

## Branch note

Keep `main` and development branch tips aligned after each Phase 0/1 merge.  
Optional: rename `Developement` → `development`.
