# Spec: Authenticated Submission Identity

## Problem Statement
On the public website submission page, logged-in users currently see the optional name and email inputs even though submission associates their account and only fills those values when omitted. This can leave submitter contact details blank or let submitted values differ from the authenticated account, while the separate choice to hide owner contact information must continue to work.

## User Stories
1. As a registered user, I want my account name and email used for my submission without seeing editable name/email fields, so that my submission identity is consistent with my authenticated account.
   - Acceptance criteria:
     - [ ] On GET `/submit/`, authenticated users do not see name or email inputs for submitter/owner contact details.
     - [ ] On a valid authenticated submission, `created_by` is the authenticated account and the stored name is that account's full name, falling back to its username when the full name is empty; the stored email is that account's email, or blank if the account has no email.
     - [ ] For an authenticated POST, omitted, forged, or otherwise altered submitted name/email values cannot replace the account-derived values or prevent an otherwise valid submission from succeeding.
     - [ ] The normal moderated-submission behavior remains unchanged: a new website is saved as pending, and both AJAX and classic POST submission remain supported.
2. As an anonymous visitor, I want to continue optionally providing contact details when submitting a website, so that I can submit without creating an account.
   - Acceptance criteria:
     - [ ] Anonymous visitors continue to see the optional name and email inputs within the optional-details section.
     - [ ] Submitted anonymous name/email values are preserved as before; if name is omitted or blank it defaults to “ناشناس”, and if email is omitted or blank it remains blank.
     - [ ] Anonymous submission continues to use the current captcha and moderation flow.
3. As a submitter, I want to control whether owner contact details are visible to other users, so that account-backed contact information does not become public without my choice.
   - Acceptance criteria:
     - [ ] The existing optional `hide_owner_info` control remains available and retains its current default and meaning for both authenticated and anonymous submissions.
     - [ ] Public detail-page contact visibility continues to be governed only by `hide_owner_info`; populating name/email from an account does not implicitly show or hide those details.

## In Scope
- Hide the existing name and email inputs from authenticated users on the public submission form.
- Bind authenticated submissions to the signed-in account on the server, ignoring client-supplied name/email values.
- Preserve the distinct `created_by` submitter-account association and the optional public owner-contact visibility choice.
- Preserve anonymous submission behavior, including the anonymous-name fallback and blank-email allowance.
- Add or update tests for authenticated rendering and server-side identity enforcement, as well as regression coverage for anonymous behavior and visibility preference.

## Out of Scope
- Changing sign-in, account profile, or account email/name management.
- Adding a separate owner/contact identity flow for submissions made on behalf of another website owner.
- Changing how owner contact details are rendered on website detail pages, or changing the default for `hide_owner_info`.
- Changes to the website moderation lifecycle, captcha, submission transport, or unrelated form fields.

## Assumptions
- The current `owner_name` and `owner_email` fields are the submission contact fields displayed as owner information; for authenticated submissions this feature populates them from the submitter's account, while `created_by` remains the distinct record of which account submitted the listing.
- Account name follows the existing fallback (`get_full_name()` then username); an account with no email produces a blank owner email rather than an invented value.
- Anonymous name/email remain optional despite the current visual asterisks; the current blank-name fallback and blank-email behavior are intentional compatibility requirements.
- Existing `hide_owner_info` behavior is intentional: it defaults to false and controls whether contact information appears on the public detail page.
- Existing `Website` fields (`owner_name`, `owner_email`, `hide_owner_info`, and `created_by`) are sufficient; no database schema change is needed.

## Open Questions
- None blocking. Whether a future feature should allow a submitter to provide contact details for a different website owner is outside this scope.
