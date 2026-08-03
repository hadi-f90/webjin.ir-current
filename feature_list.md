# Feature list & bug tracker — WebJin (وب‌جین)

**Updated:** 2026-08-03  
**Phase 0:** complete (foundation + directory tests green)  
**Current focus:** Phase 1 — MWS polish  

See also: `.ai_files/roadmap.md`, `AGENTS.md`.

---

## Phase 0 — closed (reference)

- [x] Env-based secrets / no plaintext DB password on tip
- [x] `WebsiteSubmitForm` + `QuickSubmitForm` Meta
- [x] `website_card` loads `farsi_tags`
- [x] Management commands (`directory.models`, empty commands `__init__`)
- [x] Tag delete via `Website.objects.filter(tags=tag)`
- [x] Error pages use real URL names (`index`, `contact_page`, …)
- [x] Index query optimization (`select_related`, limited featured)
- [x] Soft invalid category/tag filter (empty results, not 404)
- [x] Rating endpoint reliable with cache + ratelimit `block=False`
- [x] Directory test suite green

---

## Phase 1 — open

### Submission

- [ ] Unify public submit templates (one path, one success redirect)
- [ ] Tag chips + live suggestions on the active submit template
- [ ] Staff email on new pending (optional)

### Home / discovery

- [ ] Pagination UX (more page links / clearer nav on large sets)
- [ ] Featured / suggest policy: not only random (e.g. recent, higher rated)
- [ ] Related sites on detail: prefer shared **tags**

### Cards / detail

- [ ] Favicon or thumbnail on cards (best-effort)
- [ ] Share buttons (copy link + social)
- [ ] View counts (optional, privacy-aware)
- [ ] Report / rate / review UX polish (accordion, placement)
- [ ] Owner/staff edit control visible when allowed

### Navbar / chrome

- [ ] Navbar remains solid after scroll
- [ ] Dark mode toggle (can slip to Phase 2 if large)

### Admin dashboard

- [ ] Modal / button ID mismatches (edit / delete / status)
- [ ] Resolve-report AJAX end-to-end in UI
- [ ] Accurate pending / report / per-category counts
- [ ] CSRF on all staff AJAX calls verified

### Permissions

- [ ] Non-owner edit: consistent UX (message + redirect or 403)
- [ ] Owner edit of approved site → back to `pending` + clear message

---

## Phase 2+ (backlog)

### SEO & trust

- [ ] Meta / Open Graph / sitemap / structured data
- [ ] django-check-seo staff workflow
- [ ] Rate limits enforced product-wide on write endpoints

### Content & growth

- [ ] Bulk import UX (CSV / browser bookmarks) documented in UI
- [ ] Broken-link checker command
- [ ] Claim ownership
- [ ] Bookmarks / favorites

### Site pages

- [ ] About / FAQ / Terms polish
- [ ] Contact response handling
- [ ] Footer + ads placement (Yektanet already allowed in CSP)

---

## Display limits (by design)

| Surface | Limit |
|---------|-------|
| Popular tags (sidebar) | 10 |
| Search suggestion sites | 5 |
| Search suggestion tags | 5 |
| Combined suggestions | 10 |
| Featured block | 6 |
| Reviews on detail | 10 |

Tag **count per website** is not limited by the app.

---

## Won’t do / deferred decisions

- Nested category trees (tags replace subcategories)
- Storing Jalali strings in the database
- Reintroducing a second Persian app (`FarsiSaz`)
