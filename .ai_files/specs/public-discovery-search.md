# Spec: Public Discovery / Search

## Problem Statement
Visitors need reliable, safe discovery of approved websites through filters,
recommendations, pagination, and detail-page actions.

## User Stories
1. As a visitor, I want to browse, search, and filter approved websites, so that
   I can find relevant listings.
   - Acceptance criteria:
     - [ ] Index results contain only approved, non-deleted websites.
     - [ ] Category, tag, and text-search filters can be combined; pagination
       preserves the active filter query.
     - [ ] Empty result, category, and tag states remain inside the directory
       page chrome and provide a clear way back to all websites.
     - [ ] The recommendation block is hidden whenever a non-empty category,
       tag, or search filter is active.
2. As a visitor, I want a balanced set of homepage recommendations, so that
   discovery is not based only on random selection.
   - Acceptance criteria:
     - [ ] With no active category, tag, or search filter, show at most six
       unique, approved, non-deleted websites.
     - [ ] Selection balances up to two random, two recent, and two
       highest-rated websites; duplicate entries are removed and available
       eligible sites fill any remaining slots.
     - [ ] Recent means most recently submitted (`created_at`); rating order is
       average rating, then rating count, then submission time.
     - [ ] No sponsored or paid placement is introduced by this change.
3. As a visitor, I want usable page navigation, so that I can move through
   larger result sets without losing filters.
   - Acceptance criteria:
     - [ ] Keep the existing 12-results-per-page limit.
     - [ ] Show first, previous, nearby page numbers, next, and last controls as
       applicable; use an elided range for large page counts.
     - [ ] The current page is identified accessibly and page numbers use the
       Persian display filter.
4. As a visitor, I want website details and related listings to remain useful
   when contact data is missing.
   - Acceptance criteria:
     - [ ] Do not render blank owner-name or email rows.
     - [ ] Respect `hide_owner_info`; if neither contact value is available and
       contact information is not hidden, show a concise empty state.
     - [ ] Prefer shared-tag related websites, then fill remaining slots by
       category; exclude the current, unapproved, and deleted website.
5. As a registered user, I want rating, review, and report actions to give clear
   feedback.
   - Acceptance criteria:
     - [ ] Rating, review, and report writes require POST and authentication.
     - [ ] Invalid ratings and invalid review/report submissions show a Persian
       error message instead of silently redirecting.
     - [ ] Existing duplicate rating/report state and empty review state remain
       clear; users can identify rating controls with assistive technology.
6. As a visitor, I want live search suggestions to display submitted text
   safely, so that suggestions work under the site's CSP.
   - Acceptance criteria:
     - [ ] The index inline script carries the per-response CSP nonce.
     - [ ] Suggestion titles and types are rendered as text; the script does not
       interpolate server data into `innerHTML`.

## In Scope / Out of Scope
- In scope: Phase 1.4 discovery, empty states, filters, pagination, contact
  fallbacks, rating/review/report feedback, and safe search suggestions.
- Out of scope: paid/sponsored placements, new ranking models, view counts,
  SEO metadata, and new database fields.

## Assumptions / Open Questions
- The owner approved a temporary balanced blend of random, recent, and
  highest-rated recommendations. Random selection remains bounded to a recent
  candidate pool to avoid shuffling the full website table.
- `created_at` is the available recency proxy; the model has no approval
  timestamp.
- Sponsored or advertised listings may replace this policy only after the
  Phase 2 monetization and disclosure decisions are approved.
- No open questions.

## Names introduced
| Kind | Name | Naming-law rule |
|---|---|---|
| Related name | `websites` | Plural `snake_case` reverse relation |
| Template context key | `page_range` | English `snake_case` |
| DOM id | `reportHeading` | English `camelCase` |
| Template partial | `_paginator.html` | English `snake_case.html`; partial starts with `_` |
| CI workflow file | `phase-one-smoke.yml` | English lowercase kebab-case |

## Revision Notes
- 2026-11-24: Owner selected a temporary blend of random, recent, and rated
  recommendations; future sponsored/advertised placements remain out of scope.
- 2026-11-24: Added measurable Phase 1.4 discovery and accessibility criteria.
