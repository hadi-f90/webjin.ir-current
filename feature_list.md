# Feature list & bug tracker — WebJin (وب‌جین)

**Updated:** 2026-11-24
**Phase 0:** complete  
**Current focus:** Phase 1 — MWS polish  

Full phased detail: `.ai_files/roadmap.md` (restored open items from pre–Phase-0 roadmap).

---

## Phase 0 — closed

- [x] Env secrets / forms Meta / farsi_tags on card
- [x] Management commands + tag delete + error URL names
- [x] Index select_related / soft filters / rating+cache
- [x] Directory tests green

---

## Phase 1 — open (from roadmap + legacy feature list)

### Submit
- [x] Unify submit templates + AJAX progressive enhancement (`submit.html`)
- [x] Tag chips + suggestions on live submit form (endpoint `/tags/suggestions/`)
- [x] Categories always load on active submit form
- [ ] Optional staff email on pending

### Dashboard
- [x] Modal/ID mismatches (edit/delete/status)
- [x] Resolve-report AJAX in UI
- [x] Correct pending/report/category/tag counts
- [x] CSRF on all staff AJAX
- [x] Soft-delete trash, optional reason, deleting actor, and role-based restore

### Permissions / lifecycle
- [x] Document page redirects (302) and forbidden staff AJAX (403 JSON)
- [x] Owner/staff edits of approved websites return them to pending with a clear message
- [x] Show the detail-page edit action to owners and staff when permitted

### Discovery / UX
- [ ] Navbar solid after scroll
- [ ] Featured only when no filters (confirm)
- [ ] Related sites by **tags**
- [ ] Pagination UX on large sets
- [ ] Suggest policy beyond random
- [ ] Missing owner name/email safe on detail
- [ ] Rate/review/report UX polish; comments accordion if needed
- [ ] Owner/staff edit control on detail

### Hygiene
- [ ] Remove broken `farsi/templatetags/farsi.py` if present
- [ ] Junk files + `custome.css` typo
- [ ] WhiteNoise single registration
- [ ] Branch tip alignment / optional rename Developement

---

## Phase 2+ (summary — see roadmap)
- SEO, sitemap, OG, structured data, check-seo
- Favicon/thumbnail proxy; share buttons; dark mode
- Product rate limits; approval emails; bulk admin tools
- Ads placement (Yektanet); About/FAQ/Terms/footer
- Claim site; bookmarks; view counts; link checker; tag merge
- CI, staging, Sentry, backups, Passenger docs
 - TopAI benchmark gaps: Persian assisted discovery, richer listing filters/attributes,
  category/use-case indexes, sorting and curated lists, verified-listing workflow,
  listing-update flow, listing comparisons, saved listings, disclosed paid placement,
  and optional deal/offer alerts

---

## Display limits

Popular tags 10 · search suggestions 5+5 · featured 6 · detail reviews 10.  
No app-level max tags per website.

---

## Agent skills (profitability)

**Now:** business-model, growth, analytics-metrics, conversion-monetization, seo  
**Phase 2:** ad-ops-publisher, competitive-intel  
**Phase 3:** partnerships-bd, lifecycle-crm  

See `.ai_files/roadmap.md` § Agent skills — profitability track.
## TopAI.tools benchmark gap phase mapping

### Phase 1
- [ ] Dedicated public category index and use-case landing pages
- [ ] Public listing-update path for owners or submitters
- [ ] Public update-listing notice and staff-confirmed owner claim workflow
- [ ] Persian FAQ, terms, privacy, and submission-policy pages
- [ ] Core listing-detail attributes and contact links

### Phase 2
- [ ] Persian-first assisted discovery search
- [ ] Extended directory filters and sorting presets
- [ ] Editorial and verified-listing badges
- [ ] Verified-listing review workflow
- [ ] Listing comparison view
- [ ] Saved/favorite listings
- [ ] Listing screenshots and SSRF-safe optional media
- [ ] Verification, deal, and advertising disclosure pages
- [ ] Paid submission tracks
- [ ] Visibly labeled featured placement
- [ ] Auditable placement campaigns
- [ ] Deal/offer module
- [ ] Separation of paid-placement and organic analytics

### Phase 3
- [ ] Consent-based personalized recommendations
- [ ] Browser-bookmark import review
- [ ] Persian AI-tools and use-case guides
- [ ] Safe periodic availability and metadata checks
- [ ] Category, listing, deal, and owner-change alerts

### Phase 4
- [ ] Scale assisted discovery after Phase 2–3 evidence
- [ ] Optimize recommendation quality and reporting depth
- [ ] Expand availability-monitoring capacity

