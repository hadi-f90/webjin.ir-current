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
- [x] Categories reliably available on the active submit form
- [ ] Optional: email staff on new pending submission

### 1.2 Staff / admin dashboard

- [x] Fix modal / ID mismatches (`editWebsiteModal` vs `editModal`, missing hidden fields for status/delete URLs)
- [x] Resolve-report AJAX wired via confirmStatusModal + hidden action fields
- [x] Counts in context: `pending_count`, report count, category/tag website counts (lists stay correct)
- [x] CSRF on all staff AJAX endpoints verified
- [ ] More useful columns on site/category/tag tables (optional within Phase 1)
- [x] Soft-delete trash, optional reason, deleting actor, and role-based restore (keep moderation statuses unchanged)

### 1.3 Permissions & lifecycle messaging

- [x] Document and align **302 vs 403** for non-owner edit and non-staff AJAX
- [x] Owner edit of approved site resets to `pending` with clear user-facing message
- [x] Edit button visible for owner + staff on detail when allowed

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

### Recommended Phase 1 execution order

1. Verify CSRF enforcement and token delivery on every staff AJAX endpoint.
2. Resolve broken legacy modules, WhiteNoise/CSS duplication, stale URL copies, and confirmed junk.
3. Align owner-edit lifecycle and permission responses (`pending` reset, 302 vs 403, and edit visibility).
4. Finish essential dashboard and discovery UX (empty states, filter behavior, pagination, owner details, and rate/review/report flow).
5. Decide whether to add staff notification email, extra table columns, or a rejected reason before implementing those optional items.
6. Run CI smoke checks and verify production-MySQL/dev-SQLite documentation; close Phase 1 only when the success criteria above pass.

## TopAI.tools benchmark gap — 2026-11-21

Benchmark basis: public browsing, search, submit, update, category, and deals experiences on
TopAI.tools / TopAI.deals. This is a feature-gap roadmap, not a request to copy its visual design,
content, branding, or external ranking model. Relevance for WebJin must be decided by the
product, security, and Persian-RTL requirements before implementation.

### 1A — Core directory and trust foundation (Phase 1)
- [ ] Add a dedicated public category index and use-case landing pages with stable Persian and
  ASCII URL names, including search, sorting, pagination, and empty states.
- [ ] Add a public listing-update path for owners or submitters, with change review and
  pending-status behavior consistent with the locked website lifecycle.
- [ ] Add a public “update listing” notice/status and staff-confirmed owner claim workflow.
- [ ] Publish FAQ, terms, privacy, and submission-policy pages in Persian, without broken or
  fabricated contact claims.
- [ ] Add listing detail attributes for core data and contact links, with broken-media fallbacks.

### 2A — Discovery and trust expansion (Phase 2)
- [ ] Add a Persian-first assisted discovery search that translates a visitor's task into category,
  tag, and attribute filters; keep ordinary keyword search available and return an explainable
  result set rather than relying on an unaudited model-only answer.
- [ ] Expand directory filters from category/tag to purpose, input, output, audience, platform,
  pricing, verification, API, open-source status, mobile app, and browser extension where
  meaningful for a website/listing.
- [ ] Add sorting and discovery presets for recent, popular, highest rated, free, open source,
  verified, and top 100-style curated lists.
- [ ] Add editorial/listing badges with explicit, staff-visible rules: free, open source,
  mobile app, API, browser extension, and verified.
- [ ] Add a verified-listing review workflow: staff criteria, evidence, verification state,
  expiry/re-review, and clear public disclosure of what “verified” means.
- [ ] Add factual comparison views for 2–N listings when sufficient, normalized attributes exist;
  do not present unverified claims or scraped rankings as editorial fact.
- [ ] Add saved/favorite listings for logged-in users, with private default visibility and easy
  removal.
- [ ] Add listing-detail platforms, pricing-model, API, data/contact links, screenshots, and
  optional-media fields with SSRF-safe ingestion and broken-media fallbacks.
- [ ] Publish verification, deal, and advertising disclosure pages in Persian.

### 2B — Monetization and offers (Phase 2, gated by business/analytics specs)
- [ ] Add clearly disclosed paid submission tracks such as priority review or featured listing,
  after capacity, pricing, refund, and editorial-review policy are defined.
- [ ] Keep featured placement visibly labeled and enforce one or more standard slots by policy,
  avoiding ad-like rankings in ordinary relevance/order.
- [ ] Add homepage/category/search placement boosts with an auditable campaign, start/end time,
  budget/fee state, disclosure, and staff controls.
- [ ] Add a deal/offer module: official offer, expiration, discount code, disclosure, staff
  approval, alert subscription, and a user-requested-deal queue.
- [ ] Separate paid placement analytics from organic popularity metrics; never alter a site's
  rating, reviews, or organic relevance solely because it is paid.

### 3A — Personalization and content (Phase 3)
- [ ] Add “for you” recommendations only after consent/privacy and recommendation quality rules;
  first implement anonymous, explainable recommendations based on category/tag/attributes.
- [ ] Add importable browser bookmarks and confirm matching/new submission records in a review
  step, preserving the existing pending lifecycle.
- [ ] Add Persian AI-tools/user guides and use-case hubs with sitemap and structured navigation.
- [ ] Add periodic availability and metadata checks with privacy, SSRF, timeout, and Iran
  reachability safeguards; expose only an accurate “last checked” status.
- [ ] Add alert preferences for new listings, category updates, deal updates, and claimed-owner
  changes, with unsubscribe and rate limiting.

### 4A — Advanced scale and optimization (Phase 4)
- [ ] Promote the benchmark features to Phase 4 only after measurable Phase 2–3 adoption:
  scale assisted discovery, optimize recommendation quality, add campaign reporting depth,
  and expand availability-monitoring capacity.
- [ ] Keep all advanced additions opt-in and reversible; do not change organic ranking,
  ratings, reviews, the moderation lifecycle, or public disclosure requirements.

### Benchmark acceptance gates
1. No TopAI.tools or TopAI.deals clone: names, URLs, copy, layout, ranking, badge claims, and
   monetization disclosures must be original and suitable for WebJin.
2. No feature may silently change the locked `pending → approved | rejected` lifecycle.
3. Assisted search may use model-assisted query expansion only as a retrieval aid; it must not
   invent listings, attributes, verification, ratings, or availability.
4. Verified, open source, free, API, mobile, and browser-extension labels require a source/evidence
   field or explicit staff-confirmed editorial status.
5. Any deal or paid submission remains optional, disclosed, reversible, and separated from organic
   ranking/relevance.
6. Before implementation, run product requirements, naming-law, security, testing, Persian QA,
   watchdog, final gate, and documentation in that feature's agreed chain.

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
- [ ] Prefill the contact form's name field for logged-in users
- [ ] Store and display a website's country with an accessible flag and country name; omit it when unknown
- [ ] Save and list favorite websites for logged-in users
- [ ] Add language-model-assisted tag/category suggestions on submission and staff tools for adding/editing tags and categories; staff must review and confirm changes
- [ ] Ad placement (Yektanet allowed in CSP; card/footer slots without harming CLS)
- [ ] About / FAQ / Terms / contact response handling / footer completion
- [ ] Admin view-count or simple statistics columns (if product wants)

Use **seo-agent**, **business-model-agent**, **growth-agent**, **analytics-metrics-agent**, and **conversion-monetization-agent** as listed in *Agent skills — profitability track*. Add **ad-ops** and **competitive-intel** skills when ads/competitors become active work.

---

## Phase 3 — Engagement & quality

- [ ] “Claim this website” ownership verification (DNS or email domain)
- [ ] View counts per site (privacy-respecting, no required third-party analytics)
- [ ] Periodic website availability checker and last-checked status on detail pages; keep checks server-side, SSRF-safe, and account for reachability from Iran
- [ ] Tag synonyms / merge UI for staff
- [ ] Public user profiles (optional, privacy-first)
- [ ] Import user-exported browser bookmarks (Firefox/Chromium); confirm entries before submitting them

---

## Phase 4 — Ops & hardening

### Release1.2 cPanel cutover — 2026-11-20 (deployed; post-deploy verification)

**Status:** The owner reports that Release1.2 is now running at `webjin.ir`. The initial root-domain under-construction page and cPanel “no app” message cleared after waiting for the slow host to complete the cutover. Keep the Phase 4 deployment items open until post-deploy checks and rollback readiness are confirmed.

**Actions completed / observed**

- Confirmed the host offers Python 3.13.5, meeting the project's Python >=3.12 requirement.
- Transferred Release1.2 manually through cPanel because Git commands were unavailable on the host.
- Verified the new app under `/beta`, then completed the production update at `webjin.ir`.
- Observed `migrate --plan` warning `django_check_seo.Page (models.W036)`: MariaDB will not create that package model's conditional unique constraint. This is a warning, not proof that the WebJin migrations failed.
- During troubleshooting, the app-root `.env` shown had `DEBUG=True` and loopback-only `DJANGO_ALLOWED_HOSTS`. `passenger_wsgi.py` loads `.env` with `override=True`; confirm production values were corrected. A Django secret was exposed during troubleshooting and must be rotated if that has not already been done. Do not record its value here.

**Remaining actions**

1. Verify the live app reports `DEBUG=False`, the correct production `ALLOWED_HOSTS`, and the intended MySQL backend/database; confirm `.env` and cPanel variables do not conflict.
2. Rotate the exposed Django secret if not already rotated, and keep it outside the upload archive and repository.
3. Confirm a fresh production MySQL backup exists and review the applied migration state. Decide whether the SEO package's unsupported conditional constraint is acceptable or needs follow-up.
4. Smoke-test the live root domain and any aliases, static assets, captcha submission, login/registration, contact form, and staff dashboard. Check Passenger logs after the host has had time to settle.
5. Preserve the Release1.1 files and rollback instructions until Release1.2 is stable. Record the final cPanel app/domain mapping and manual upload procedure; close Phase 4 deployment items only after the checks pass.

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
