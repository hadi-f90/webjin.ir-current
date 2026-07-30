# WebJin (dirweb.ir) Development Roadmap

Persian web directory for discovering and submitting Iranian/Farsi websites.
Stack assumptions: Django 6, Bootstrap 5 RTL, taggit, django-simple-captcha,
django-csp, Vazirmatn, Jalali display helpers (`farsi` app).

See `.ai_files/technical-conventions.md` for locked decisions this roadmap assumes.

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
- [ ] Single source of truth for template names (`submit_website.html` vs
      `submit_quick.html` / `submit.html`) — pick one public submit path
- [ ] Consistent URL names and success redirect after submit
- [ ] Production MySQL + dev SQLite documented; no secrets in repo

### 2. Public discovery (MWS)

- [x] Index: list approved sites, category sidebar, popular tags, pagination
- [x] Search query + live suggestions endpoint
- [x] Website detail: description, tags, category, related sites, favicon helper
- [x] Rating (1–5, one per user) + reviews + report accordion
- [ ] Featured/random block only when no filters (already mostly done)
- [ ] Empty states and 404/403 pages aligned with `directory/base.html`
      (current error templates still reference other app URL names)

### 3. Submission flow (MWS)

- [x] Submit form (title, URL normalize to https, optional category/tags/desc,
      owner name/email, captcha)
- [x] AJAX-capable submit returning JSON errors/success
- [x] Pending status by default; staff must approve
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

---

## Phase 2 — Polish & trust

- SEO: per-page meta, Open Graph, sitemap (django-sitemaps already in deps),
  structured data for website listings
- django-check-seo integration for staff previews
- Image/favicon cache or proxy (avoid broken external favicon.ico)
- Rate limiting restored (`django-ratelimit`) on submit, rate, review, report
- Email: approval/rejection mail to `owner_email`; contact form → admin inbox
- Admin dashboard: filters, search, bulk approve/reject
- Review moderation queue (is_approved workflow used consistently)
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
- Multi-language switch (fa primary, en secondary) using existing LANGUAGES

---

## Phase 4 — Scale & integrations

- API (DRF) for partners / mobile client — only after auth + throttling design
- Elasticsearch / Postgres full-text if MySQL search becomes a bottleneck
- CDN for static; object storage for uploads if logos added
- Yektanet / ad slots documented under CSP allowlist only
- Backup & restore runbooks; monitoring (uptime + error rate)

---

## Explicitly out of scope until specified

- Payment / premium listing marketplace
- Full CMS / blog (separate product)
- User-generated subcategories (tags already replace subcategories)
- Mobile native apps

Update this roadmap as features ship; mark checkboxes and move items between phases only via a Product/Requirements `spec.md`.
