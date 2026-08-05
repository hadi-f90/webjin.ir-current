# Feature list & bug tracker — WebJin (وب‌جین)

**Updated:** 2026-08-03  
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
- [ ] Categories always load on active submit form
- [ ] Optional staff email on pending

### Dashboard
- [ ] Modal/ID mismatches (edit/delete/status)
- [ ] Resolve-report AJAX in UI
- [ ] Correct pending/report/category/tag counts
- [ ] CSRF on all staff AJAX
- [ ] Rejected reason or soft-delete policy decision

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
