# WebJin (dirweb.ir / webjin.ir) Development Roadmap

Persian web directory — Django 6, Bootstrap 5 RTL, taggit, captcha, CSP, Vazirmatn, Jalali via `farsi` app only.

**Phase 0 closed:** 2026-08-03 (forms, settings, tags, commands, error pages, directory tests green).

Canonical companions: `feature_list.md`, `AGENTS.md`, `.ai_files/technical-conventions.md`.

---

## Phase 0 — Foundation (DONE)

| Item | Result |
|------|--------|
| Env-driven settings (`SECRET_KEY`, `DEBUG`, `MYSQL_*`) | Done — no plaintext password on tip |
| `WebsiteSubmitForm` / `QuickSubmitForm` Meta | Done |
| `website_card` `{% load farsi_tags %}` | Done |
| Management commands use `directory.models` | Done |
| Tag delete uses `Website.objects.filter(tags=tag)` | Done |
| Error templates use real URL names (`index`, …) | Done |
| Index `select_related` / soft category filter | Done |
| Rating path + LocMem cache for ratelimit | Done |
| Directory test suite green | Done |

**Still ops (not code):** rotate any MySQL password that lived in old git history; keep secrets only in host env.

---

## Phase 1 — MWS completion (current)

**Goal:** Moderated submission → public discovery loop is polished and trustworthy for daily use.

### 1.1 Submission UX

- [ ] Single public submit path (collapse `submit.html` / `submit_quick.html` / `submit_website.html`)
- [ ] Consistent success redirect and messaging
- [ ] Tag chips + suggestions fully wired on the live submit template
- [ ] Optional: email staff on new pending

### 1.2 Staff dashboard

- [ ] Fix modal / ID mismatches (`editWebsiteModal` vs `editModal`, hidden fields)
- [ ] Resolve-report AJAX fully wired in UI
- [ ] Counts in context (`pending_count`, report count, category/tag website counts)
- [ ] CSRF consistency on all staff AJAX endpoints

### 1.3 Permissions & HTTP semantics

- [ ] Document and align 302 (redirect) vs 403 for non-owner edit and non-staff AJAX
- [ ] Owner edit of approved site resets to `pending` with clear message

### 1.4 Public UX

- [ ] Navbar stays solid after scroll (no unwanted transparency)
- [ ] Empty states consistent with directory chrome
- [ ] Related sites prefer **shared tags** over random/category-only
- [ ] Pagination UX (more page numbers / clearer nav) if still weak on large result sets

### 1.5 Hygiene

- [ ] Align `main` ↔ development branch tips after each merge
- [ ] Optional: rename branch `Developement` → `development`
- [ ] CI smoke: `migrate` + `test directory` + `check` on PR

**Phase 1 success criteria:**  
Anonymous submit → pending → staff approve from dashboard (modals work) → site on index with category/tags → user rates/reviews/reports → staff sees report. Navbar and submit path feel finished.

---

## Phase 2 — Polish & trust

- SEO: per-page meta, Open Graph, sitemap, structured data
- django-check-seo for staff previews
- Product rate limiting on submit / rate / review / report (cache already available)
- Email: approval/rejection to `owner_email`; contact → admin
- Admin: filters, search, bulk approve/reject
- Review moderation queue if `is_approved` is used strictly
- Accessibility pass (RTL forms, focus, contrast)
- Dark mode toggle
- Favicon / thumbnail improvements on cards

---

## Phase 3 — Engagement & quality

- Bookmarks / favorites
- “Claim this website” (DNS or email domain)
- Broken-link checker management command
- Tag synonyms / merge UI for staff
- View counts (privacy-respecting)
- Public profiles (optional, privacy-first)

---

## Phase 4 — Ops & hardening

- CI: migrate + test + `check --deploy`
- Staging with production-like env
- Error reporting (e.g. Sentry)
- MySQL backup / restore drill
- Document Passenger / WSGI deploy path used on host

---

## Website lifecycle (locked)

```
submit → pending → approved | rejected
```

- Public index/detail: `status='approved'` only  
- Tags via taggit; categories are flat (no nested trees)  
- Dates: Gregorian in DB; Jalali only in templates  

## AJAX contract (locked)

- Staff: `require_POST` + `staff_member_required`
- JSON: `{"status": "success"|"error", "message": "...", ...}`
- CSRF: cookie / meta + `X-CSRFToken`
