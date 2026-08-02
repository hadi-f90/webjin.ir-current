# WebJin (dirweb.ir / webjin.ir) Development Roadmap

Persian web directory for discovering and submitting Iranian/Farsi websites.  
Stack assumptions: Django 6, Bootstrap 5 RTL, taggit, django-simple-captcha,
django-csp, Vazirmatn, Jalali display helpers (`farsi` app only — FarsiSaz removed).

See `.ai_files/technical-conventions.md` for locked decisions this roadmap assumes.  
See `feature_list.md` for the living day-to-day checklist.  
See `AGENTS.md` for agent onboarding.

**Last decision-matrix merge:** 2026-08-02 (main ≡ Developement @ `11bd146`)

---

## Decision matrix (P0 → P3) — merged 2026-08-02

| Priority | Item | Owner agent | Status / action |
|----------|------|-------------|-----------------|
| **P0** | Hardcoded MySQL password + `DEBUG = True` in `config/settings.py` | security + django-backend | **Secrets must leave the repo.** Use env vars only. See settings section below. |
| **P0** | `QuickSubmitForm.Meta` broken (`exclude = ()`, labels on non-model `captcha`) | django-backend | Fix: explicit `fields = ['title', 'url']`; captcha stays as form field only |
| **P0** | `website_card.html` uses `to_hindi` / `truncate_persian` without `{% load farsi_tags %}` | ui-ux | Add load (latent until include is used) |
| **P1** | Broken legacy `farsi/templatetags/farsi.py` (imports non-existent `core.utils`) | django-backend | Delete or quarantine |
| **P1** | Junk files in tree (concatenated dumps, hermes tmp, `custome.css` typo) | documentation | Run `scripts/clean_junk.sh` |
| **P1** | Stale `AGENTS.md` still mentions FarsiSaz | documentation | Replaced by rewritten AGENTS.md |
| **P1** | Duplicate WhiteNoise middleware registration | django-backend | Keep one path only |
| **P2** | Multiple submit templates (`submit.html`, `submit_quick.html`, `submit_website.html`) | product + backend + ui-ux | Collapse to one public path |
| **P2** | `custom.css` vs `custome.css` | ui-ux | Keep `custom.css`, delete typo |
| **P2** | `to_jalali` lacks optional `fmt` argument | farsi | Optional API improvement |
| **P2** | Admin dashboard modal/ID mismatches (`editWebsiteModal` vs `editModal`) | ui-ux + backend | Fix JS + hidden fields |
| **P3** | Branch name `Developement` (typo) | ops | Rename → `development` when convenient |
| Keep | `main` ≡ `Developement` | — | Already identical; preserve until rename |

---

## Minimum Working State (MWS) — Phase 1

**Goal:** A public visitor can browse approved sites, filter by category/tag,
search, submit a site (with captcha), and an admin can approve/reject via the
custom admin dashboard. Authenticated users can rate, review, and report.

### 1. Foundation (shared)

- [x] Django project layout (`config`, `directory`, `contact`, `farsi`)
- [x] RTL Bootstrap + Vazirmatn + Bootstrap Icons
- [x] CSP middleware + basic security headers
- [x] Auth (register / login / logout) + staff flag for admin dashboard
- [x] `Category` + `Website` (status: pending/approved/rejected) + taggit tags
- [x] Media/static via WhiteNoise in production
- [ ] **Secrets out of repo** — `DJANGO_SECRET_KEY`, DB password, `DEBUG`, `ALLOWED_HOSTS` from env only
- [ ] Single source of truth for template names (`submit_website.html` vs
      `submit_quick.html` / `submit.html`) — pick one public submit path
- [ ] Consistent URL names and success redirect after submit
- [ ] Production MySQL + dev SQLite documented; no secrets in repo
- [ ] Remove junk files (concat dumps, hermes tmp, typo CSS)
- [ ] Fix / remove broken `farsi/templatetags/farsi.py`
- [ ] Deduplicate WhiteNoise middleware registration

### 2. Public discovery (MWS)

- [x] Index: list approved sites, category sidebar, popular tags, pagination
- [x] Search query + live suggestions endpoint
- [x] Website detail: description, tags, category, related sites, favicon helper
- [x] Rating (1–5, one per user) + reviews + report accordion
- [ ] Featured/random block only when no filters (already mostly done)
- [ ] Empty states and 404/403 pages aligned with `directory/base.html`
      (current error templates still reference other app URL names)
- [ ] `website_card.html` self-loads `farsi_tags` (defensive)

### 3. Submission flow (MWS)

- [x] Submit form (title, URL normalize to https, optional category/tags/desc,
      owner name/email, captcha)
- [x] AJAX-capable submit returning JSON errors/success
- [x] Pending status by default; staff must approve
- [x] `WebsiteSubmitForm.Meta.model = Website` present
- [ ] **Fix QuickSubmitForm.Meta** (broken exclude/labels)
- [ ] Unify Quick vs full form; one template + one form class for public path
- [ ] Tag chips + suggestions fully wired on the live template
- [ ] Email notification to staff on new pending (optional MWS stretch)

### 4. Moderation / custom admin dashboard (MWS)

- [x] Staff-only `admin_dashboard` with tabs: overview, sites, reports, users,
      content, categories, tags
- [x] AJAX approve / reject / delete / status update / edit website
- [x] Category & tag CRUD via AJAX
- [ ] Fix modal/ID mismatches in `admin_dashboard.html` JS
      (`editWebsiteModal` vs `editModal`, missing hidden fields for status/delete URLs)
- [ ] Resolve report AJAX fully wired in UI
- [ ] Counts (`pending_count`, `report_count`, user `website_count`) passed in
      context and annotated correctly
- [ ] Soft-delete or “rejected reason” field (defer hard delete policy decision)

### 5. User account area (MWS)

- [x] User dashboard: my websites + my reviews
- [x] Delete own website / own review
- [ ] Edit own pending/approved site returns to pending after save (already
      intended) — confirm messaging and status reset rule

**Success criteria (MWS):**  
Anonymous user submits a site → appears in pending → staff approves from
custom dashboard → site shows on index with category/tag → logged-in user rates
and reviews → report appears for staff.  
**Plus:** no secrets in git history of active settings; `DEBUG=False` + HTTPS
headers active on host; junk files gone.

---

## Known bugs / debt (from feature_list + 2026-08-02 audit)

### Critical
- [ ] Hardcoded DB credentials in `settings.py` (must rotate password after move to env)
- [ ] `DEBUG = True` hardcoded (must be env-driven)
- [ ] QuickSubmitForm Meta invalid
- [ ] Admin dashboard modal ID mismatches / incomplete hidden fields

### High
- [ ] Latent `website_card.html` missing `{% load farsi_tags %}`
- [ ] Broken `farsi.py` templatetag module
- [ ] Multiple public submit templates / form classes
- [ ] Rate limiting present in requirements but commented out in settings
- [ ] Inconsistent CSRF handling in some admin AJAX paths

### Medium
- [ ] Empty / error pages not fully aligned with directory base
- [ ] Pagination + suggested-sites edge cases
- [ ] Duplicate CSS (`custom.css` / `custome.css`)
- [ ] WhiteNoise registered twice when `DEBUG=False`

### Cleanup
- [ ] `directory/concatenated_output.txt`, `farsi/concatenated_output.txt`
- [ ] `.hermes-tmp.*`
- [ ] `tmp/restart.txt`
- [ ] Stale FarsiSaz references in docs

---

## Phase 2 — Polish & trust

- SEO: per-page meta, Open Graph, sitemap (django-sitemaps already in deps),
  structured data for website listings
- django-check-seo integration for staff previews
- Image/favicon cache or proxy (avoid broken external favicon.ico)
- Rate limiting restored (`django-ratelimit`) on submit, rate, review, report
- Email: approval/rejection mail to `owner_email`; contact form → admin inbox
- Admin dashboard: filters, search, bulk approve/reject
- Review moderation queue (`is_approved` workflow used consistently)
- Accessibility pass (RTL forms, focus, contrast)
- Error pages (401/403/404/500) rewritten to extend `directory/base.html`
- Caching for index category counts / popular tags (Redis optional)

---

## Phase 3 — Engagement & quality

- Bookmarks / favorites for logged-in users
- “Claim this website” ownership verification (DNS or email domain)
- Broken-link checker management command (periodic)
- Tag synonyms / merge UI for staff
- Public user profiles (optional, privacy-first)
- Analytics: views per site (privacy-respecting, no third-party required)

---

## Phase 4 — Ops & hardening

- CI: migrate + test + `check --deploy` on every PR
- Staging environment with production-like env vars
- Log aggregation / error reporting (Sentry or equivalent)
- Backup + restore drill for MySQL
- Document Passenger / WSGI deployment path used on host

---

## Branch policy (current)

- `main` and `Developement` point to the **same commit** — keep them identical
  until the typo rename is done.
- Feature work: short-lived branches → PR into `main`.
- Do not commit secrets, concatenated dumps, or editor temp files.
