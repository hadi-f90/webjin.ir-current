# Improvements and Bug Fixes - راهنمای وب ایران

**Current Branch**: `Debug-and-feature-add` (under feature-work)

**Status**: Solidification Phase (Bug Fixing First)

---

## Known Bugs & Issues (Updated Assessment)

### Home / Main Page
- [x] [BUG] Change the name of the website (partially done in templates)
- [ ] [FEATURE] [BUG] Fix pagination (add more page numbers, better navigation)
- [ ] [FEATURE] Change website suggesting policy (currently random → most visited, recently added, most viewed, advertised)

### Category Page
- [x] [FEATURE] Add category icon before title
- [x] [BUG] Replace slug with category name in page title/URL
- [x] [BUG] Fix pagination navigation (currently broken/limited)

### Website Cards
- [x] [Improvement] Make name/title shorter with proper truncation
- [] [Improvement] Add  favicon of homepage
- [ ] [Improvement] Add thumbnail / favicon / screenshot of homepage
- [x] [BUG] Make description longer (currently too short)
- [ ] [Improvement] Add advertisement slot in cards

### Website Detail Page
- [ ] [FEATURE] Edit button for owner + staff/admin
- [ ] [FEATURE] Share buttons (social + copy link)
- [ ] [FEATURE] View counts (visits)
- [x] [FEATURE] Icon + screenshot of website (icon done)
- [ ] [FEATURE] Flag/report button (exists but needs UX polish)
- [ ] [FEATURE] Ping / reachability check (from Iran)
- [ ] [FEATURE] Handle case when no owner name/email
- [ ] [FEATURE] Make similar sites suggestion use **tags** for better relevance
- [ ] [Improvement] Move "Go to website" button next to logo + make smaller
- [ ] [Improvement] Make comments accordion-style

### Navbar
- [ ] [BUG] Navbar becomes transparent after scrolling (should stay solid)
- [ ] [FEATURE] Light / Dark mode toggle

### Management Panel (Admin Dashboard)
- [ ] [BUG] Many modal buttons do not work (edit, delete, status change)
- [ ] [FEATURE] Add view count / statistics columns
- [ ] [Improvement] Add more columns to site/category/tag lists
- [ ] [BUG] Count of websites in category and tag lists doesn't update correctly
- [ ] [FEATURE] Bulk import from:
    - CSV files
    - Firefox HTML/JSON bookmark export
    - Chromium-based browsers HTML/JSON bookmark export

### Other Pages
- [ ] About page (basic version exists)
- [ ] FAQ page
- [ ] Policy / Terms page (basic exists)
- [ ] Contact page + response handling
- [ ] Footer (needs completion + ads)

### Backend / Quick Submit
- [ ] [BUG] Quick website submit doesn't work reliably (form submission fails)
- [x] [BUG] Categories do not load in submit form (fixed in some templates)
- [ ] [FEATURE] Management command to import list of websites via Django shell

### General / Cross-Cutting
- [ ] Hardcoded DB credentials in settings.py
- [ ] Duplicate urls.py files
- [ ] Inconsistent CSRF in admin AJAX
- [ ] Rate limiting not active
- [ ] SEO improvements (meta tags, sitemap)
- [ ] Ads integration (yektanet script present but placement needed)

---

## Roadmap (Merged & Prioritized)

### Phase 1: Solid State (Now - Critical)
- Fix all **Critical bugs** above (submit form, admin modals, pagination, CSRF)
- Unify submission forms (`WebsiteSubmitForm` + robust AJAX)
- Secure settings (`DJANGO_SECRET_KEY`, DB via `.env`)
- Make admin dashboard fully functional
- Test complete flow: submit → approve → detail page

### Phase 2: UX & Core Features
- Improved pagination + suggested websites logic
- View counters + smart suggestions using tags
- Dark mode + better navbar
- Edit buttons + ownership checks
- Bulk import commands

### Phase 3: Growth & Polish
- Full SEO + sitemap
- Ads placement
- Statistics dashboard
- Reachability ping
- Advanced search & filtering

---

**Next Actions I Propose**:
1. Fix **Quick Submit** bug (highest user impact)
2. Fix **Admin Dashboard modals** (JS issues)
3. Improve **Pagination** + **Suggested websites**
4. Secure settings + clean URLs

---

Would you like me to **start fixing** the top priority items now?

Reply with your order (e.g., "Fix quick submit first" or "Start with admin dashboard") and I will produce the exact code changes + push to the branch.

I'm ready. Let's make this rock solid.