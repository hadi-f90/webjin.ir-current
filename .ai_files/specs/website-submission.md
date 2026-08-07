# Spec: Website Submission

## Problem Statement
Visitors and registered users need one reliable way to submit a website for moderation, with captcha, optional details, and progressive-enhancement AJAX — without multiple competing templates.

## User Stories
1. As a visitor, I want to submit a title and URL with captcha, so that staff can moderate my listing.
   - Acceptance criteria:
     - [ ] GET `/submit/` renders a single form (`directory/submit.html`)
     - [ ] Valid POST creates `Website` with `status=pending`
     - [ ] Invalid POST shows field errors (HTML or JSON for AJAX)
     - [ ] Captcha is required (django-simple-captcha)
2. As a visitor with JS enabled, I want AJAX submit so the page does not fully reload on validation errors.
   - Acceptance criteria:
     - [ ] `fetch` with `X-Requested-With: XMLHttpRequest` returns JSON `{status, message, redirect?|errors?}`
     - [ ] Success redirects to `success` URL
3. As a registered user, I want my account linked as `created_by` and owner fields prefilled when empty.

## In Scope
- Unified `PublicWebsiteSubmitForm` + `submit.html`
- Classic POST fallback
- Tags optional via `tags_input`

## Out of Scope
- Auto-approval, payment, email to staff (optional later)
- Changing captcha library

## Assumptions
- Moderation remains manual
- Only http/https URLs

## Open Questions
- None blocking after AJAX unification
