# WebJin (dirweb.ir / webjin.ir) Development Roadmap

Persian web directory for discovering and submitting Iranian/Farsi websites.  
Stack: Django 6, Bootstrap 5 RTL, taggit, django-simple-captcha, django-csp,
Vazirmatn, Jalali via `farsi` app only (FarsiSaz removed).

See `.ai_files/technical-conventions.md` for locked decisions.  
See `feature_list.md` for the day-to-day checklist.  
See `AGENTS.md` for agent onboarding.

**Phase 0 closed:** 2026-08-03 (forms, settings, tags, commands, error URL names, tests green).  
**Current focus:** Phase 1 — MWS polish.

---

## Phase 0 — Foundation (DONE)

| Item | Result |
|------|--------|
| Env-driven settings (`SECRET_KEY`, `DEBUG`, `MYSQL_*`); no plaintext password on tip | Done |
| `WebsiteSubmitForm` full Meta + `QuickSubmitForm` `fields=['title','url']` + captcha | Done |
| `website_card.html` `{% load farsi_tags %}` | Done |
| Management commands: empty `__init__`, `directory.models` (not `websites` / `your_app`) | Done |
| Tag delete: `Website.objects.filter(tags=tag)` (taggit has no `tag.websites` manager) | Done |
| Error templates (401/403/404/500): real URL names (`index`, `contact_page`, …) | Done |
| Index: `select_related('category')`, limited featured, soft invalid category/tag filter | Done |
| Rating path + LocMem `CACHES` for django-ratelimit (`block=False` on rate) | Done |
| Directory test suite green | Done |
| `.env.example` / README env table | Done |

**Ops (not blocked on code):** rotate any MySQL password that appeared in old git history; secrets only in host env.

---

## Decision matrix — residual items (from 2026-08-02 audit)

| Priority | Item | Phase | Status |
|----------|------|-------|--------|
| P0 | Secrets / forms / card load / commands / tag delete / error URLs | 0 | **Done** |
| P1 | Broken legacy `farsi/templatetags/farsi.py` (`core.utils` import) | 1 hygiene | Open if file still present |
| P1 | Junk files (`concatenated_output.txt`, `.hermes-tmp.*`, `custome.css`) | 1 hygiene | Open — use `scripts/clean_junk.sh` |
| P1 | Duplicate WhiteNoise registration when `DEBUG=False` | 1 hygiene | Verify / dedupe |
| P1 | Admin modal ID mismatches | 1 dashboard | Open |
| P1 | CSRF consistency on staff AJAX | 1 dashboard | Open |
| P2 | Multiple submit templates → one public path | 1 submit | **Done** |
| P2 | `custom.css` vs `custome.css` | 1 hygiene | Open |
| P2 | `to_jalali` optional `fmt` argument | 2 / farsi polish | Open |
| P3 | Rename branch `Developement` → `development` | 1 hygiene | Optional |
| Keep | `main` ≡ development tip after merges | continuous | Ongoing |

---

## Phase 1 — MWS completion (current)

**Goal:** Moderated submission → public discovery loop is polished and safe for daily use.

### 1.1 Submission UX

- [x] Single public submit path (`submit.html` + `PublicWebsiteSubmitForm`, AJAX + POST fallback)
- [x] Consistent URL name + success redirect + messaging
- [x] Tag chips + suggestions on live submit (`/tags/suggestions/`)
- [ ] Categories reliably available on the active submit form
- [ ] Optional: email staff on new pending submission

### 1.2 Staff / admin dashboard

- [ ] Fix modal / ID mismatches (`editWebsiteModal` vs `editModal`, missing hidden fields for status/delete URLs)
- [x] Resolve-report AJAX wired via confirmStatusModal + hidden action fields
- [x] Counts in context: `pending_count`, report count, category/tag website counts (lists stay correct)
- [ ] CSRF on all staff AJAX endpoints verified
- [ ] More useful columns on site/category/tag tables (optional within Phase 1)
- [ ] Soft-delete **or** “rejected reason” field (product decision; defer hard-delete policy)

### 1.3 Permissions & lifecycle messaging

- [ ] Document and align **302 vs 403** for non-owner edit and non-staff AJAX
- [ ] Owner edit of approved site resets to `pending` with clear user-facing message
- [ ] Edit button visible for owner + staff on detail when allowed

### 1.4 Public discovery & UX

- [x] Navbar stays **solid** after scroll (no unwanted transparency)
- [ ] Empty states aligned with directory chrome
- [ ] Featured/random block only when no category/tag/search filters (confirm behavior)
- [x] Related sites prefer **shared tags** (not only same category / random)
- [ ] Pagination UX: more page numbers / clearer nav on large result sets
- [ ] Suggest policy beyond pure random (recent, higher rated — product pick)
- [ ] Handle missing owner name/email on detail without broken layout
- [ ] Report / rate / review UX polish (placement, accordion for comments if needed)

### 1.5 Hygiene & repo

- [ ] Remove or quarantine broken `farsi/templatetags/farsi.py` if still present
- [ ] Run junk cleanup (`concatenated_output.txt`, hermes temps, `custome.css` typo)
- [ ] Dedupe WhiteNoise middleware registration
- [ ] Resolve `custom.css` vs `custome.css` (keep one)
- [ ] Audit duplicate / stale `urls.py` copies if any remain outside `config` + apps
- [ ] Align `main` ↔ development tips after each merge
- [ ] Optional: rename `Developement` → `development`
- [ ] CI smoke on PR: `migrate` + `test directory` + `check`
- [ ] Production MySQL + dev SQLite documented in README (keep current)

**Instrumentation (optional in Phase 1):** baseline metrics with `analytics-metrics-agent` so Phase 2 growth is not blind.

**Phase 1 success criteria:**  
Anonymous submit → pending → staff approve from dashboard (modals work) → site on index with category/tags → user rates/reviews/reports → staff sees report. Navbar and submit path feel finished; no known P0 crashers.

---

## Phase 2 — Polish & trust

- [ ] SEO: per-page meta, Open Graph, sitemap (`django-sitemaps` in deps), structured data for listings
- [ ] django-check-seo integration for staff previews
- [ ] Image/favicon cache or proxy (avoid broken external favicon.ico on cards)
- [ ] Favicon / thumbnail / optional screenshot on cards
- [ ] Share buttons (copy link + social)
- [ ] Rate limiting restored product-wide on submit, rate, review, report
- [ ] Email: approval/rejection to `owner_email`; contact form → admin inbox
- [ ] Admin dashboard: filters, search, bulk approve/reject
- [ ] Review moderation queue (`is_approved` used consistently)
- [ ] Accessibility pass (RTL forms, focus, contrast)
- [ ] Dark mode toggle
- [ ] Error pages fully extend shared directory/base chrome (beyond URL-name fix)
- [ ] Caching for index category counts / popular tags (LocMem done; Redis optional)
- [ ] `to_jalali` optional format argument (farsi API polish)
- [ ] Ad placement (Yektanet allowed in CSP; card/footer slots without harming CLS)
- [ ] About / FAQ / Terms / contact response handling / footer completion
- [ ] Admin view-count or simple statistics columns (if product wants)

Use **seo-agent**, **business-model-agent**, **growth-agent**, **analytics-metrics-agent**, and **conversion-monetization-agent** as listed in *Agent skills — profitability track*. Add **ad-ops** and **competitive-intel** skills when ads/competitors become active work.

---

## Phase 3 — Engagement & quality

- [ ] Bookmarks / favorites for logged-in users
- [ ] “Claim this website” ownership verification (DNS or email domain)
- [ ] View counts per site (privacy-respecting, no required third-party analytics)
- [ ] Broken-link / reachability checker management command (periodic; “from Iran” is an ops constraint)
- [ ] Tag synonyms / merge UI for staff
- [ ] Public user profiles (optional, privacy-first)
- [ ] Bulk import UX documented (CSV + optional Firefox/Chromium bookmark export)
- [ ] Ping / reachability status surfaced on detail (if checker exists)

---

## Phase 4 — Ops & hardening

- [ ] CI: migrate + test + `check --deploy` on every PR
- [ ] Staging environment with production-like env vars
- [ ] Log aggregation / error reporting (Sentry or equivalent)
- [ ] Backup + restore drill for MySQL
- [ ] Document Passenger / WSGI deployment path used on host
- [ ] History hygiene: old secret-tipped branches deleted or rewritten after password rotation

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
- Progressive enhancement preferred  

## Display limits (by design)

| Surface | Limit |
|---------|-------|
| Popular tags sidebar | 10 |
| Search suggestion sites / tags | 5 each |
| Combined suggestions | 10 |
| Featured block | 6 |
| Reviews on detail | 10 |

Tag count per website is unlimited.


## Agent skills — profitability track

### Available now (essential)

| Skill | Use for |
|-------|---------|
| `business-model-agent` | Revenue model choice and sequencing |
| `growth-agent` | Visitor + listing acquisition plans |
| `analytics-metrics-agent` | KPIs, funnels, event dictionary |
| `conversion-monetization-agent` | Featured/priority/claim UX + disclosure |
| `seo-agent` | Organic traffic research and specs |

Typical order when money is in scope:

```
business-model → analytics-metrics + growth
        → conversion-monetization → product-requirements
        → ui-ux + django-backend → security + testing-qa
        → seo (ongoing) → documentation
```

### Scheduled for later phases (do not create until needed)

| Phase | Planned skill | Purpose |
|-------|---------------|---------|
| **Phase 2** | `ad-ops-publisher-agent` | Ad slot map, density, CLS, network policy (e.g. Yektanet) |
| **Phase 2** | `competitive-intel-agent` | Periodic landscape of other directories / pricing |
| **Phase 3** | `partnerships-bd-agent` | Co-branded niches, hoster/agency packages, outreach kits |
| **Phase 3** | `lifecycle-crm-agent` | Owner emails: approved, featured offer, claim reminders |

Phase 4 remains ops (CI, staging, Sentry, backups) — no new revenue agent required by default.


## Branch policy

- Keep `main` and development branch tips aligned after merges  
- Feature work: short-lived branches → PR into `main`  
- Do not commit secrets, concatenated dumps, or editor temp files  
